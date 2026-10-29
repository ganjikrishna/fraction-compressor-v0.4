"""LoRA baseline: Spark generation of the distillation prompt set.

Design: results/lora_baseline_design.md. The matched-byte LoRA baseline is
trained by distillation from the full Qwen2.5-0.5B-Instruct model (the
teacher) on fresh prompts written by Muse Spark (Meta Model API,
muse-spark-1.3). This script writes ONLY prompts (500 per bucket:
knowledge, instruct, math), in the same shapes as the held-out eval
probes. All supervision answers come from the teacher itself on Flash;
this script never asks for answers.

Hygiene (design doc): every prompt is novelty-checked against all 96
eval prompts (data/heldout96_probes_spark.json) and the 24 Signet
prompts (--exclude): exact normalized match or token-set Jaccard >= 0.7
is rejected. Accepted prompts also exclude each other at a stricter
within-set threshold (Jaccard >= 0.6, math suffix stripped) so the set
does not repeat itself. A failed batch gets one logged regeneration
retry with the problems fed back (house pattern); items still offending
after the retry are dropped and the bucket is topped up with extra
batches. Generation is 5 batches of 100 per bucket. All calls are
logged to results/api_usage_log.jsonl.

Output: data/distill_prompts.json (gitignored), each item
{"bucket", "prompt", "split"} with a fixed-seed per-bucket shuffle:
450 train + 50 validation per bucket (validation is for early stopping
on distillation KL only; the eval probes are never touched). A random
10% audit sample is written next to the record for manual inspection.

Run from the repo root on the Muse VM (needs the Meta connector):

    python3 examples/lora_baseline_gen.py \
        --exclude /tmp/signet_prompts.json \
        --eval-probes data/heldout96_probes_spark.json \
        --record /tmp/lora_distill_gen_record.json
"""

import argparse
import json
import random
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.meta-model-api/bin"))
import meta_api  # noqa: E402

MODEL = "muse-spark-1.3"
PROVIDER = "meta-model-api"
BUCKETS = ("knowledge", "instruct", "math")
PER_BUCKET = 500
BATCH = 100
TRAIN_PER_BUCKET = 450
MATH_SUFFIX = "Answer with just the number."
SEED = 20261028


def now_z():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_usage(path, purpose, usage):
    row = {
        "provider": PROVIDER,
        "model": MODEL,
        "time": now_z(),
        "purpose": purpose,
        "prompt_tokens": (usage or {}).get("prompt_tokens"),
        "completion_tokens": (usage or {}).get("completion_tokens"),
        "total_tokens": (usage or {}).get("total_tokens"),
    }
    with open(path, "a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def chat(prompt, max_tokens, purpose, usage_log):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
    }
    t0 = time.perf_counter()
    resp = meta_api.call("POST", "/v1/chat/completions", payload)
    elapsed = round(time.perf_counter() - t0, 2)
    if "http_error" in resp:
        raise RuntimeError(f"{purpose}: HTTP {resp['http_error']}: {resp['body'][:500]}")
    usage = resp.get("usage") or {}
    log_usage(usage_log, purpose, usage)
    msg = resp["choices"][0]["message"]
    content = msg.get("content") or ""
    return content, usage, elapsed, resp.get("choices", [{}])[0].get("finish_reason")


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    starts = [i for i in (text.find("{"), text.find("[")) if i >= 0]
    if not starts:
        raise ValueError("no JSON found in reply")
    start = min(starts)
    dec = json.JSONDecoder()
    obj, _ = dec.raw_decode(text[start:])
    return obj


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def tokens(s):
    s = norm(s)
    if s.endswith(MATH_SUFFIX.lower()):
        s = s[: -len(MATH_SUFFIX)].strip()
    return set(re.findall(r"[a-z0-9]+", s))


def jaccard(a_toks, b_toks):
    return len(a_toks & b_toks) / len(a_toks | b_toks) if a_toks and b_toks else 0.0


SHAPE = ('Reply with ONLY a JSON array, no markdown fences, no commentary, of exactly '
         '%d objects in this shape:\n{"bucket": "%s", "prompt": "..."}')

BUCKET_INTRO = {
    "knowledge": (
        'You are writing prompts for a language-model distillation set. Write %d NEW items '
        'for the bucket "knowledge": each prompt is a short factual sentence FRAGMENT that '
        'a respondent would naturally continue with the fact (for example: "The capital of '
        'France is", "Water is made of hydrogen and"). No question marks; the fragment '
        'itself sets up the completion. Span world geography, science, history, literature, '
        'sport, everyday facts; vary the phrasing widely (definitions, "X is", "X was", '
        '"The largest Y is", completions of famous facts).'
    ),
    "instruct": (
        'You are writing prompts for a language-model distillation set. Write %d NEW items '
        'for the bucket "instruct": each prompt is a short direct command or '
        'format-constrained request a respondent can satisfy in a few words (for example: '
        '"Name three fruits.", "Write the word \'hello\' in uppercase.", "List the days of '
        'the week in order."). Vary the task types widely: naming, listing, formatting, '
        'translating a common word, counting, spelling, opposites, ordering, one-line '
        'definitions, yes/no with a reason word.'
    ),
    "math": (
        'You are writing prompts for a language-model distillation set. Write %d NEW items '
        'for the bucket "math": each prompt is a short arithmetic word problem (money, '
        'distance, time, groups of objects, ages, measurements, percentages, simple '
        'fractions) and MUST end with the exact suffix "Answer with just the number." '
        'Use varied numbers and settings; no bare drills like "What is 12 + 15?"; the '
        'arithmetic must be checkable from the text alone.'
    ),
}

RULES = """Rules:
- Every prompt must be NEW. Do not reuse or lightly reword any prompt in the EXCLUDED list below (those are benchmark items), and do not repeat a topic or template you have already used in this set.
- One prompt per object; prompts are short (under 25 words).
- Do not include answers; prompts only.

EXCLUDED prompts (never reuse or lightly reword):
"""


def validate_batch(items, bucket, excluded):
    """Return (accepted_items, problems). excluded: list of (norm, toks, source)
    covering eval + signet + already-accepted distill prompts. Within-set
    threshold 0.6, eval/signet threshold 0.7."""
    problems = []
    accepted = []
    if not isinstance(items, list):
        return [], [f"expected a list, got {type(items).__name__}"]
    seen_norm = set()
    batch_toks = []
    for i, it in enumerate(items):
        if not isinstance(it, dict) or not isinstance(it.get("prompt"), str):
            problems.append(f"item {i} is not an object with a prompt string")
            continue
        p = it["prompt"].strip()
        if it.get("bucket") != bucket:
            problems.append(f"item {i} bucket is {it.get('bucket')!r}, expected {bucket!r}")
            continue
        if len(p.split()) > 30:
            problems.append(f"item {i} prompt too long: {p!r}")
            continue
        if bucket == "math" and not p.endswith(MATH_SUFFIX):
            problems.append(f"item {i} math prompt lacks the required suffix: {p!r}")
            continue
        if bucket == "knowledge" and p.endswith("?"):
            problems.append(f"item {i} knowledge prompt must be a fragment, not a question: {p!r}")
            continue
        np_ = norm(p)
        if np_ in seen_norm:
            problems.append(f"duplicate inside batch: {p!r}")
            continue
        toks = tokens(p)
        bad = None
        for e_norm, e_toks, e_src, _e_raw in excluded:
            if np_ == e_norm:
                bad = f"duplicates a {e_src} prompt: {p!r}"
                break
            thr = 0.6 if e_src == "distill" else 0.7
            j = jaccard(toks, e_toks)
            if j >= thr:
                bad = f"too close to a {e_src} prompt (jaccard {j:.2f} >= {thr}): {p!r}"
                break
        if bad is None:
            for b_toks in batch_toks:
                if jaccard(toks, b_toks) >= 0.6:
                    bad = f"too close to another prompt in this batch: {p!r}"
                    break
        if bad:
            problems.append(bad)
            continue
        seen_norm.add(np_)
        batch_toks.append(toks)
        accepted.append({"bucket": bucket, "prompt": p})
    return accepted, problems


def gen_batch(bucket, args, record, excluded, batch_idx):
    purpose = f"lora_baseline_distill_prompt_generation_{bucket}_{batch_idx}"
    excluded_prompts = [e[3] for e in excluded if e[2] in ("eval", "signet")]
    prompt_text = (BUCKET_INTRO[bucket] % BATCH) + "\n\n" + RULES \
        + json.dumps(excluded_prompts, indent=1) + "\n\n" + (SHAPE % (BATCH, bucket))
    content, usage, elapsed, finish = chat(prompt_text, 48000, purpose, args.usage_log)
    entry = {"attempts": [{"usage": usage, "elapsed_s": elapsed, "finish_reason": finish,
                           "content_chars": len(content)}]}
    record["batches"].append({"bucket": bucket, "batch": batch_idx, **entry})
    try:
        items = extract_json(content)
        accepted, problems = validate_batch(items, bucket, excluded)
    except Exception as e:  # truncated or malformed JSON: treat as a failed batch
        accepted, problems = [], [f"unparseable reply: {e}"]
    entry["validation_problems"] = problems
    entry["accepted_first_try"] = len(accepted)
    if problems:
        fix_prompt = (
            "Your previous batch of prompts for the bucket \"" + bucket + "\" had these "
            "problems:\n- " + "\n- ".join(problems[:40])
            + "\n\nRewrite the FULL batch of " + str(BATCH) + " prompts for this bucket "
              "fixing every problem. Same rules and same JSON shape as before: ONLY a JSON "
              "array of " + str(BATCH) + " objects {\"bucket\": \"" + bucket + "\", "
              "\"prompt\": \"...\"}, all new, none reusing or lightly rewording the "
              "excluded benchmark prompts, none repeating each other."
        )
        content2, usage2, elapsed2, finish2 = chat(
            fix_prompt, 48000, purpose + "_retry", args.usage_log)
        entry["attempts"].append({"usage": usage2, "elapsed_s": elapsed2,
                                  "finish_reason": finish2, "content_chars": len(content2)})
        try:
            items2 = extract_json(content2)
            accepted2, problems2 = validate_batch(items2, bucket, excluded)
        except Exception as e:
            accepted2, problems2 = [], [f"unparseable retry reply: {e}"]
        entry["validation_problems_after_retry"] = problems2
        entry["accepted_after_retry"] = len(accepted2)
        # Keep whichever attempt accepted more clean items.
        if len(accepted2) > len(accepted):
            accepted = accepted2
    entry["accepted_final"] = len(accepted)
    return accepted


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exclude", default="/tmp/signet_prompts.json")
    ap.add_argument("--eval-probes", default="data/heldout96_probes_spark.json")
    ap.add_argument("--record", default="/tmp/lora_distill_gen_record.json")
    ap.add_argument("--out", default="data/distill_prompts.json")
    ap.add_argument("--audit-out", default="/tmp/lora_distill_audit_sample.txt")
    ap.add_argument("--usage-log", default="results/api_usage_log.jsonl")
    args = ap.parse_args()

    signet_prompts = json.loads(Path(args.exclude).read_text())
    eval_items = json.loads(Path(args.eval_probes).read_text())
    eval_prompts = [it["prompt"] for it in eval_items]

    # excluded entries: (norm, tokens, source, raw_prompt)
    excluded = []
    for p in eval_prompts:
        excluded.append((norm(p), tokens(p), "eval", p))
    for p in signet_prompts:
        excluded.append((norm(p), tokens(p), "signet", p))

    record = {"model": MODEL, "provider": PROVIDER, "started": now_z(),
              "purpose": "lora_baseline_distillation_prompts",
              "excluded_eval": len(eval_prompts), "excluded_signet": len(signet_prompts),
              "batches": []}

    by_bucket = {b: [] for b in BUCKETS}
    for bucket in BUCKETS:
        batch_idx = 0
        while len(by_bucket[bucket]) < PER_BUCKET and batch_idx < 9:
            accepted = gen_batch(bucket, args, record, excluded, batch_idx)
            for it in accepted:
                excluded.append((norm(it["prompt"]), tokens(it["prompt"]), "distill",
                                 it["prompt"]))
            by_bucket[bucket].extend(accepted)
            print(f"{bucket} batch {batch_idx}: +{len(accepted)} "
                  f"(total {len(by_bucket[bucket])}/{PER_BUCKET})", flush=True)
            batch_idx += 1
        if len(by_bucket[bucket]) < PER_BUCKET:
            raise RuntimeError(f"{bucket}: only {len(by_bucket[bucket])} prompts after "
                               f"{batch_idx} batches")

    rng = random.Random(SEED)
    all_items = []
    for bucket in BUCKETS:
        items = by_bucket[bucket][:PER_BUCKET]
        rng.shuffle(items)
        for i, it in enumerate(items):
            it["split"] = "train" if i < TRAIN_PER_BUCKET else "val"
        all_items.extend(items)
        print(f"{bucket}: {PER_BUCKET} prompts "
              f"({TRAIN_PER_BUCKET} train / {PER_BUCKET - TRAIN_PER_BUCKET} val)")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(all_items, indent=2) + "\n")
    print(f"wrote {len(all_items)} prompts to {out}")

    audit = rng.sample(all_items, k=len(all_items) // 10)
    Path(args.audit_out).write_text(
        "\n".join(f"[{it['bucket']}/{it['split']}] {it['prompt']}" for it in audit) + "\n")
    print(f"audit sample: {len(audit)} prompts to {args.audit_out}")
    record["finished"] = now_z()
    record["total_prompts"] = len(all_items)
    Path(args.record).write_text(json.dumps(record, indent=2) + "\n")
    print(f"record written to {args.record}")


if __name__ == "__main__":
    main()
