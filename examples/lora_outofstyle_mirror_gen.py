"""Out-of-style LoRA control: Gemini generation of the mirrored eval set.

Design: results/lora_outofstyle_design.md (Spark consult: the mirrored
2x2). Gemini authors 96 NEW eval probes WITH reference answers, 32 per
bucket, in the same Gemini conventions as the control distillation
prompts (varied formats, no bare fragments, no bare commands, never
the Spark math suffix phrase). Subset labels mirror the Spark 96:
first 8 accepted per bucket -> "heldout24", remaining 24 ->
"heldout72_new". Eval-only: these probes are never trained on.

Hygiene: exact normalized match or token-set Jaccard >= 0.7 against
the Spark 96, the 1,500 in-style Spark prompts, AND the 1,500 Gemini
control prompts is rejected; within-set >= 0.6. Reference answers are
checked for the math bucket (must parse as a number) and kept short.
One logged regeneration retry per failed batch.

Output: data/mirror96_probes_gemini.json, items
{"bucket", "prompt", "answer", "subset"}. All Gemini calls logged to
results/api_usage_log.jsonl.

Run from the repo root on the Muse VM, AFTER lora_outofstyle_gen.py:

    python3 examples/lora_outofstyle_mirror_gen.py
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
PER_BUCKET = 32
BATCH = 32
BANNED_PHRASE = "answer with just the number"
SEED = 20261028


def now_z():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_usage(purpose, usage):
    with open(REPO / "results/api_usage_log.jsonl", "a") as f:
        f.write(json.dumps({
            "provider": PROVIDER, "model": MODEL, "time": now_z(), "purpose": purpose,
            "prompt_tokens": (usage or {}).get("promptTokenCount"),
            "completion_tokens": (usage or {}).get("candidatesTokenCount"),
            "total_tokens": (usage or {}).get("totalTokenCount")}) + "\n")


def chat(prompt, purpose):
    scratch = REPO / "data/.oos_tmp"
    scratch.mkdir(parents=True, exist_ok=True)
    pf = scratch / f"oos_mirror_{purpose}.txt"
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
    obj, _ = json.JSONDecoder().raw_decode(text[min(starts):])
    return obj


def norm(s):
    return re.sub(r"\s+", " ", s.strip().lower())


def tokens(s):
    return set(re.findall(r"[a-z0-9]+", norm(s)))


def jaccard(a, b):
    return len(a & b) / len(a | b) if a and b else 0.0


SHAPE = ('Reply with ONLY a JSON array, no markdown fences, no commentary, of exactly '
         '%d objects in this shape:\n{"bucket": "%s", "prompt": "...", "answer": "..."}')

BUCKET_INTRO = {
    "knowledge": (
        'You are writing EVALUATION probes for a language-model benchmark. Write %d NEW '
        'items for the bucket "knowledge": questions and quiz items that ask for a '
        'single fact, each WITH its short correct answer. Use VARIED formats: full '
        'questions ("What is the capital of France?", answer "Paris"), exam-style '
        'items, fill-in-the-blank with ___ (answer = the missing words), true-or-false '
        'items (answer "True" or "False"), and casual conversational asks. NEVER a bare '
        'sentence fragment trailing off for completion. Every prompt must be a '
        'complete, self-contained ask ending in "?" or ".". Answers are 1-6 words: '
        'the fact itself, nothing else. Span geography, science, history, literature, '
        'sport, everyday facts.'
    ),
    "instruct": (
        'You are writing EVALUATION probes for a language-model benchmark. Write %d NEW '
        'items for the bucket "instruct": conversational or scenario-framed requests, '
        'each WITH the minimal correct response as its answer. Mix polite requests '
        '("Could you list three fruits for me, please?", answer e.g. "Apple, banana, '
        'orange"), scenario framing ("I am packing for a beach trip. Name four things '
        'I should bring.", answer = four suitable items), prose constraints, and '
        'short multi-part asks. AVOID bare one-line commands. Answers must be the '
        'exact short response satisfying the request (a list, a formatted word, a '
        'spelling, a translation, a count), under 12 words. Vary tasks: naming, '
        'listing, formatting, translating a common word, counting, spelling, '
        'opposites, ordering, one-line definitions.'
    ),
    "math": (
        'You are writing EVALUATION probes for a language-model benchmark. Write %d NEW '
        'items for the bucket "math": arithmetic word problems (money, distance, '
        'time, groups of objects, ages, measurements, percentages, simple fractions) '
        'in VARIED formats (plain questions, exam style "Q7. ...", conversational), '
        'each WITH its answer as a plain number (no units, no commas, decimals only '
        'when the true answer is not whole). NEVER use the exact phrase "Answer with '
        'just the number" or any fixed closing instruction. The arithmetic must be '
        'checkable from the text alone, and the answer must be exactly right: '
        'compute carefully.'
    ),
}

RULES = """Rules:
- Every probe must be NEW. Do not reuse or lightly reword any prompt in the EXCLUDED list below, and do not repeat a topic or template inside this set.
- One probe per object; prompts under 45 words.
- The answer must be correct and minimal.

EXCLUDED prompts (never reuse or lightly reword):
"""


def validate_batch(items, bucket, excluded):
    problems, accepted = [], []
    if not isinstance(items, list):
        return [], [f"expected a list, got {type(items).__name__}"]
    seen_norm, batch_toks = set(), []
    for i, it in enumerate(items):
        if not isinstance(it, dict) or not isinstance(it.get("prompt"), str) \
                or not isinstance(it.get("answer"), str):
            problems.append(f"item {i} is not an object with prompt and answer strings")
            continue
        p, a = it["prompt"].strip(), it["answer"].strip()
        if it.get("bucket") != bucket:
            problems.append(f"item {i} bucket is {it.get('bucket')!r}, expected {bucket!r}")
            continue
        if len(p.split()) > 48:
            problems.append(f"item {i} prompt too long: {p!r}")
            continue
        if not a or len(a.split()) > 14:
            problems.append(f"item {i} answer missing or too long: {a!r}")
            continue
        if BANNED_PHRASE in norm(p):
            problems.append(f"item {i} uses the banned suffix phrase: {p!r}")
            continue
        if bucket == "knowledge" and p[-1:].isalnum():
            problems.append(f"item {i} knowledge prompt looks like a bare fragment: {p!r}")
            continue
        if bucket == "math":
            try:
                float(a.replace(",", ""))
            except ValueError:
                problems.append(f"item {i} math answer is not a plain number: {a!r}")
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
            thr = 0.6 if e_src == "mirror" else 0.7
            if jaccard(toks, e_toks) >= thr:
                bad = f"too close to a {e_src} prompt: {p!r}"
                break
        if bad is None:
            for b_toks in batch_toks:
                if jaccard(toks, b_toks) >= 0.6:
                    bad = f"too close to another probe in this batch: {p!r}"
                    break
        if bad:
            problems.append(bad)
            continue
        seen_norm.add(np_)
        batch_toks.append(toks)
        accepted.append({"bucket": bucket, "prompt": p, "answer": a})
    return accepted, problems


def gen_bucket(bucket, record, excluded):
    purpose = f"lora_outofstyle_mirror_generation_{bucket}"
    excluded_prompts = [e[3] for e in excluded if e[2] in ("eval",)]
    prompt_text = (BUCKET_INTRO[bucket] % BATCH) + "\n\n" + RULES \
        + json.dumps(excluded_prompts, indent=1) + "\n\n" + (SHAPE % (BATCH, bucket))
    content, usage, elapsed = chat(prompt_text, purpose)
    entry = {"bucket": bucket, "attempts": [{"usage": usage, "elapsed_s": elapsed,
                                             "content_chars": len(content)}]}
    record["batches"].append(entry)
    try:
        accepted, problems = validate_batch(extract_json(content), bucket, excluded)
    except Exception as e:
        accepted, problems = [], [f"unparseable reply: {e}"]
    entry["validation_problems"] = problems
    entry["accepted_first_try"] = len(accepted)
    tries = 0
    while len(accepted) < PER_BUCKET and tries < 3:
        tries += 1
        need = PER_BUCKET - len(accepted)
        fix = (
            "Your previous batch for the bucket \"" + bucket + "\" had these problems:\n- "
            + "\n- ".join((problems or ["not enough valid items"])[:40])
            + f"\n\nWrite {need} MORE new probes for this bucket, fixing every problem, "
              "same style rules and JSON shape as before (objects with bucket, prompt, "
              "answer), none reusing the excluded prompts or each other."
        )
        content2, usage2, elapsed2 = chat(fix, f"{purpose}_topup{tries}")
        entry["attempts"].append({"usage": usage2, "elapsed_s": elapsed2,
                                  "content_chars": len(content2)})
        for it in accepted:
            excluded.append((norm(it["prompt"]), tokens(it["prompt"]), "mirror",
                             it["prompt"]))
        try:
            acc2, prob2 = validate_batch(extract_json(content2), bucket, excluded)
        except Exception as e:
            acc2, prob2 = [], [f"unparseable topup reply: {e}"]
        accepted.extend(acc2)
        problems = prob2
        entry[f"accepted_after_topup{tries}"] = len(accepted)
    entry["accepted_final"] = len(accepted)
    return accepted[:PER_BUCKET]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--eval-probes", default="data/heldout96_probes_spark.json")
    ap.add_argument("--instyle", default="data/distill_prompts.json")
    ap.add_argument("--oos", default="data/distill_prompts_gemini_oos.json")
    ap.add_argument("--record", default="data/lora_oos_mirror_record.json")
    ap.add_argument("--out", default="data/mirror96_probes_gemini.json")
    args = ap.parse_args()

    excluded = []
    for src, path in (("eval", args.eval_probes), ("instyle", args.instyle),
                      ("oos", args.oos)):
        for it in json.loads((REPO / path).read_text()):
            excluded.append((norm(it["prompt"]), tokens(it["prompt"]), src,
                             it["prompt"]))

    record = {"model": MODEL, "provider": PROVIDER, "started": now_z(),
              "purpose": "lora_outofstyle_mirror_probes",
              "excluded_total": len(excluded), "batches": []}

    all_items = []
    for bucket in BUCKETS:
        items = gen_bucket(bucket, record, excluded)
        if len(items) < PER_BUCKET:
            raise RuntimeError(f"{bucket}: only {len(items)} probes")
        for i, it in enumerate(items):
            it["subset"] = "heldout24" if i < 8 else "heldout72_new"
        all_items.extend(items)
        print(f"{bucket}: {PER_BUCKET} probes", flush=True)
        for it in items:
            excluded.append((norm(it["prompt"]), tokens(it["prompt"]), "mirror",
                             it["prompt"]))

    out = REPO / args.out
    out.write_text(json.dumps(all_items, indent=2) + "\n")
    print(f"wrote {len(all_items)} probes to {out}")
    audit = random.Random(SEED).sample(all_items, k=24)
    (REPO / "data/lora_oos_mirror_audit.txt").write_text(
        "\n".join(f"[{it['bucket']}/{it['subset']}] {it['prompt']} -> {it['answer']}"
                  for it in audit) + "\n")
    record["finished"] = now_z()
    record["total_prompts"] = len(all_items)
    Path(args.record).write_text(json.dumps(record, indent=2) + "\n")
    print(f"record written to {args.record}")


if __name__ == "__main__":
    main()
