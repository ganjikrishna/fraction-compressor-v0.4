"""Out-of-style LoRA control: Gemini generation of the distillation prompts.

Design: results/lora_outofstyle_design.md. Same matched-byte LoRA
control as examples/lora_baseline_gen.py, except the 1,500 distillation
prompts are authored by GEMINI (gemini-3.5-flash-lite) in a deliberately
different surface style from the Spark eval probes: the eval style is
knowledge = bare sentence fragments, instruct = short bare commands,
math = short word problems ending "Answer with just the number."; the
Gemini style here is full questions / exam items / fill-in-the-blank /
conversational and scenario-framed requests, varied length, and math
with NO fixed suffix (the Spark suffix phrase is banned outright).

Hygiene (same as the in-style run): every prompt novelty-checked
against all 96 eval prompts, the 24 Signet prompts (reconstructed as
the heldout24 subset; the original /tmp list did not survive), AND the
1,500 in-style Spark distill prompts: exact normalized match or
token-set Jaccard >= 0.7 rejected. Accepted prompts also exclude each
other at Jaccard >= 0.6. One logged regeneration retry per failed
batch; buckets topped up with extra batches.

Output: data/distill_prompts_gemini_oos.json (gitignored), each item
{"bucket", "prompt", "split"} with the same fixed-seed per-bucket
shuffle as the in-style run: 450 train + 50 validation per bucket.
A random 10% audit sample is written next to the record. All Gemini
calls are logged to results/api_usage_log.jsonl.

Run from the repo root on the Muse VM:

    python3 examples/lora_outofstyle_gen.py
"""

import argparse
import json
import random
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GEMINI = Path.home() / "workspace/custom-connectors/custom.google-gemini/bin/gemini_api.py"
MODEL = "gemini-3.5-flash-lite"
PROVIDER = "google-gemini"
BUCKETS = ("knowledge", "instruct", "math")
PER_BUCKET = 500
BATCH = 100
TRAIN_PER_BUCKET = 450
BANNED_PHRASE = "answer with just the number"
SEED = 20261028


def now_z():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_usage(purpose, usage):
    row = {
        "provider": PROVIDER, "model": MODEL, "time": now_z(), "purpose": purpose,
        "prompt_tokens": (usage or {}).get("promptTokenCount"),
        "completion_tokens": (usage or {}).get("candidatesTokenCount"),
        "total_tokens": (usage or {}).get("totalTokenCount"),
    }
    with open(REPO / "results/api_usage_log.jsonl", "a") as f:
        f.write(json.dumps(row) + "\n")
    return row


def chat(prompt, purpose):
    scratch = REPO / "data/.oos_tmp"
    scratch.mkdir(parents=True, exist_ok=True)
    pf = scratch / f"oos_gen_{purpose}.txt"
    pf.write_text(prompt)
    t0 = time.perf_counter()
    r = None
    for attempt, wait in enumerate((0, 20, 45, 90)):
        if wait:
            time.sleep(wait)
        r = subprocess.run(
            [str(GEMINI), "ask", "--prompt-file", str(pf), "--model", MODEL,
             "--max-tokens", "32768"],
            capture_output=True, text=True, timeout=900)
        if r.returncode == 0:
            break
        print(f"{purpose}: attempt {attempt + 1} failed rc={r.returncode}: "
              f"{(r.stderr or '')[-200:]}", flush=True)
    elapsed = round(time.perf_counter() - t0, 2)
    if r is None or r.returncode != 0:
        raise RuntimeError(f"{purpose}: gemini failed after retries: "
                           f"{(r.stderr if r else '')[:400]}")
    g = json.loads(r.stdout)
    usage = g.get("usage") or {}
    log_usage(purpose, usage)
    return g.get("text") or "", usage, elapsed


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    starts = [i for i in (text.find("{"), text.find("[")) if i >= 0]
    if not starts:
        raise ValueError("no JSON found in reply")
    start = min(starts)
    obj, _ = json.JSONDecoder().raw_decode(text[start:])
    return obj


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def tokens(s):
    return set(re.findall(r"[a-z0-9]+", norm(s)))


def jaccard(a_toks, b_toks):
    return len(a_toks & b_toks) / len(a_toks | b_toks) if a_toks and b_toks else 0.0


SHAPE = ('Reply with ONLY a JSON array, no markdown fences, no commentary, of exactly '
         '%d objects in this shape:\n{"bucket": "%s", "prompt": "..."}')

BUCKET_INTRO = {
    "knowledge": (
        'You are writing prompts for a language-model distillation set. Write %d NEW items '
        'for the bucket "knowledge": questions and quiz items that ask for a single fact. '
        'Use VARIED formats, mixing all of these: full questions ("What is the capital of '
        'France?"), exam-style items ("Q12. Which planet is known as the Red Planet?"), '
        'fill-in-the-blank with ___ ("___ is the chemical symbol for gold."), true-or-false '
        'items ("True or false: penguins can fly."), and casual conversational asks '
        '("Hey, quick one: how many legs does a spider have?"). NEVER write a bare '
        'sentence fragment that trails off for completion (NOT "The capital of France '
        'is"). Every item must be a complete, self-contained ask ending in "?", "." '
        'Span geography, science, history, literature, sport, everyday facts. Vary '
        'length: some one line, some with a sentence of setup.'
    ),
    "instruct": (
        'You are writing prompts for a language-model distillation set. Write %d NEW items '
        'for the bucket "instruct": requests a respondent can satisfy briefly, but framed '
        'CONVERSATIONALLY or as small scenarios, NOT as bare one-line commands. Mix '
        'formats: polite requests ("Could you list three fruits for me, please?"), '
        'scenario framing ("I am packing for a beach trip. Name four things I should '
        'bring."), requests with the constraint inside prose ("For my quiz night I need '
        'the days of the week in order."), asking a friend ("Quick favour: spell the '
        'word \'necessary\' for me."), and short multi-part asks. AVOID the bare '
        'imperative style ("Name three fruits.", "List the days of the week."). Vary '
        'the tasks (naming, listing, formatting, translating a common word, counting, '
        'spelling, opposites, ordering, one-line definitions, yes/no with a reason) and '
        'vary the length from about 8 to 40 words.'
    ),
    "math": (
        'You are writing prompts for a language-model distillation set. Write %d NEW items '
        'for the bucket "math": arithmetic word problems (money, distance, time, groups '
        'of objects, ages, measurements, percentages, simple fractions) asked in VARIED '
        'formats: plain questions ("How many apples are left?"), exam style ("Q7. A '
        'train travels..."), conversational asks ("So if I buy 3 notebooks at $4 '
        'each..."), and problems embedded in a sentence or two of story. NEVER use the '
        'exact phrase "Answer with just the number" or any fixed closing instruction; '
        'let the question itself carry the ask. Use varied numbers and settings; no '
        'bare drills like "What is 12 + 15?"; the arithmetic must be checkable from '
        'the text alone.'
    ),
}

RULES = """Rules:
- Every prompt must be NEW. Do not reuse or lightly reword any prompt in the EXCLUDED list below (benchmark items and an earlier prompt set), and do not repeat a topic or template you have already used in this set.
- One prompt per object; prompts are under 45 words.
- Do not include answers; prompts only.

EXCLUDED prompts (never reuse or lightly reword):
"""


def validate_batch(items, bucket, excluded):
    """excluded: list of (norm, toks, source). Eval/signet/instyle
    threshold 0.7, within-set (source 'distill') threshold 0.6."""
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
        if len(p.split()) > 48:
            problems.append(f"item {i} prompt too long: {p!r}")
            continue
        if BANNED_PHRASE in norm(p):
            problems.append(f"item {i} uses the banned Spark-style suffix phrase: {p!r}")
            continue
        if bucket == "knowledge" and p[-1:].isalnum():
            problems.append(f"item {i} knowledge prompt looks like a bare fragment "
                            f"(must end in '?', '.', or contain ___): {p!r}")
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


def gen_batch(bucket, record, excluded, batch_idx):
    purpose = f"lora_outofstyle_prompt_generation_{bucket}_{batch_idx}"
    excluded_prompts = [e[3] for e in excluded if e[2] in ("eval", "signet")]
    prompt_text = (BUCKET_INTRO[bucket] % BATCH) + "\n\n" + RULES \
        + json.dumps(excluded_prompts, indent=1) + "\n\n" + (SHAPE % (BATCH, bucket))
    content, usage, elapsed = chat(prompt_text, purpose)
    entry = {"bucket": bucket, "batch": batch_idx,
             "attempts": [{"usage": usage, "elapsed_s": elapsed,
                           "content_chars": len(content)}]}
    record["batches"].append(entry)
    try:
        items = extract_json(content)
        accepted, problems = validate_batch(items, bucket, excluded)
    except Exception as e:
        accepted, problems = [], [f"unparseable reply: {e}"]
    entry["validation_problems"] = problems
    entry["accepted_first_try"] = len(accepted)
    if problems:
        fix_prompt = (
            "Your previous batch of prompts for the bucket \"" + bucket + "\" had these "
            "problems:\n- " + "\n- ".join(problems[:40])
            + "\n\nRewrite the FULL batch of " + str(BATCH) + " prompts for this bucket "
              "fixing every problem, keeping the same style rules as before (varied "
              "formats, no bare fragments, no bare commands, never the phrase \"Answer "
              "with just the number\"). Same JSON shape: ONLY a JSON array of "
            + str(BATCH) + " objects {\"bucket\": \"" + bucket + "\", \"prompt\": "
              "\"...\"}, all new, none reusing or lightly rewording the excluded "
              "benchmark prompts, none repeating each other."
        )
        content2, usage2, elapsed2 = chat(fix_prompt, purpose + "_retry")
        entry["attempts"].append({"usage": usage2, "elapsed_s": elapsed2,
                                  "content_chars": len(content2)})
        try:
            items2 = extract_json(content2)
            accepted2, problems2 = validate_batch(items2, bucket, excluded)
        except Exception as e:
            accepted2, problems2 = [], [f"unparseable retry reply: {e}"]
        entry["validation_problems_after_retry"] = problems2
        entry["accepted_after_retry"] = len(accepted2)
        if len(accepted2) > len(accepted):
            accepted = accepted2
    entry["accepted_final"] = len(accepted)
    return accepted


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--eval-probes", default="data/heldout96_probes_spark.json")
    ap.add_argument("--signet-probes", default="data/heldout_probes_spark.json")
    ap.add_argument("--instyle", default="data/distill_prompts.json")
    ap.add_argument("--record", default="data/lora_oos_gen_record.json")
    ap.add_argument("--out", default="data/distill_prompts_gemini_oos.json")
    ap.add_argument("--audit-out", default="data/lora_oos_audit_sample.txt")
    ap.add_argument("--checkpoint", default="data/.oos_gen_checkpoint.json")
    args = ap.parse_args()

    eval_items = json.loads((REPO / args.eval_probes).read_text())
    signet_items = json.loads((REPO / args.signet_probes).read_text())
    instyle_items = json.loads((REPO / args.instyle).read_text())

    # excluded entries: (norm, tokens, source, raw_prompt)
    excluded = []
    for it in eval_items:
        excluded.append((norm(it["prompt"]), tokens(it["prompt"]), "eval", it["prompt"]))
    seen = {e[0] for e in excluded}
    for it in signet_items:
        if norm(it["prompt"]) not in seen:
            excluded.append((norm(it["prompt"]), tokens(it["prompt"]), "signet",
                             it["prompt"]))
            seen.add(norm(it["prompt"]))
    for it in instyle_items:
        excluded.append((norm(it["prompt"]), tokens(it["prompt"]), "instyle",
                         it["prompt"]))

    record = {"model": MODEL, "provider": PROVIDER, "started": now_z(),
              "purpose": "lora_outofstyle_distillation_prompts",
              "excluded_eval": len(eval_items), "excluded_signet": 24,
              "excluded_instyle": len(instyle_items), "batches": []}

    # Checkpoint resume: a prior interrupted run may have completed some
    # buckets (the first attempt died when the VM /tmp was wiped mid-run;
    # accepted items live only in memory, so completed buckets are saved
    # to data/ as they finish).
    ckpt_path = REPO / args.checkpoint
    by_bucket = {b: [] for b in BUCKETS}
    if ckpt_path.exists():
        saved = json.loads(ckpt_path.read_text())
        for b in BUCKETS:
            by_bucket[b] = saved.get(b, [])
        for b in BUCKETS:
            for it in by_bucket[b]:
                excluded.append((norm(it["prompt"]), tokens(it["prompt"]), "distill",
                                 it["prompt"]))
        print(f"resumed from checkpoint: "
              f"{ {b: len(by_bucket[b]) for b in BUCKETS} }", flush=True)
        record["resumed_from_checkpoint"] = True

    for bucket in BUCKETS:
        batch_idx = 0
        while len(by_bucket[bucket]) < PER_BUCKET and batch_idx < 12:
            accepted = gen_batch(bucket, record, excluded, batch_idx)
            for it in accepted:
                excluded.append((norm(it["prompt"]), tokens(it["prompt"]), "distill",
                                 it["prompt"]))
            by_bucket[bucket].extend(accepted)
            print(f"{bucket} batch {batch_idx}: +{len(accepted)} "
                  f"(total {len(by_bucket[bucket])}/{PER_BUCKET})", flush=True)
            ckpt_path.write_text(json.dumps(by_bucket, indent=1) + "\n")
            batch_idx += 1
        if len(by_bucket[bucket]) < PER_BUCKET:
            raise RuntimeError(f"{bucket}: only {len(by_bucket[bucket])} prompts after "
                               f"{batch_idx} batches")
        ckpt_path.write_text(json.dumps(
            {b: by_bucket[b][:PER_BUCKET] for b in BUCKETS}, indent=1) + "\n")
        print(f"checkpoint saved after {bucket}", flush=True)

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

    out = REPO / args.out
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
