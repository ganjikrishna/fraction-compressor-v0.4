"""Alien Sweep held-out expansion: Spark generation step (24 -> 96 items).

One strengthening test approved by Vinay on Oct 27: expand the fresh
held-out probe set from 24 items to 96 so the byte-fairness verdict
(mlp_behemoth_lite vs uniform_rank32) rests on more evidence. This
script makes three Muse Spark calls (Meta Model API, muse-spark-1.3),
one per bucket, 24 NEW items each (24 knowledge, 24 instruct, 24
math), in the same format as data/heldout_probes_spark.json. All calls
are logged to results/api_usage_log.jsonl.

Novelty is checked against BOTH pre-existing sets:
- the 24 Signet prompts (passed via --exclude, a JSON list of prompt
  strings kept OUTSIDE the repo), and
- the first 24 held-out prompts (--also-exclude, the probes file
  data/heldout_probes_spark.json itself).
No exact normalized prompt match, and token-set Jaccard >= 0.7 against
any prompt in either set is flagged; a flagged bucket is regenerated
once with the problems fed back (logged retry), exactly as the
original held-out guard did.

Output: data/heldout72_probes_spark.json (gitignored, local only),
ordered knowledge, instruct, math, in the Signet scorer shape
(bucket / prompt / answer / wrong).

Run from the repo root on the Muse VM (needs the Meta connector):

    python3 examples/alien_sweep_heldout96_gen.py \
        --exclude /tmp/signet_prompts.json \
        --also-exclude data/heldout_probes_spark.json \
        --record /tmp/heldout96_gen_record.json
"""

import argparse
import json
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
PER_BUCKET = 24


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


def jaccard(a, b):
    ta = set(re.findall(r"[a-z0-9]+", norm(a)))
    tb = set(re.findall(r"[a-z0-9]+", norm(b)))
    return len(ta & tb) / len(ta | tb) if ta and tb else 0.0


# ---------------------------------------------------------------------------
# Per-bucket prompts. The "do not reuse" list covers the Signet 24 and
# the first held-out 24 topics, verbatim from the earlier guard plus the
# held-out set's topics.
# ---------------------------------------------------------------------------

COMMON_RULES = """Rules:
- Every item must be NEW: do not reuse or lightly reword any of these existing items: capitals of Japan, France, or Canada; boiling point of water; chemical formula for water; chemical symbol for gold; the element with symbol O; largest planet; planet closest to the Sun; author of Romeo and Juliet or of '1984'; currency of the United Kingdom or Japan; photosynthesis location; the year the Berlin Wall fell; largest ocean on Earth; first person to walk on the Moon; a train at 60 mph for 2.5 hours; 15 percent of 200; a rectangle of 8 by 5; 3 dozen eggs minus 14; 7 squared plus 8 squared; 7 squared; a 40 dollar shirt at 25 percent off; minutes in 3.5 hours; the prime after 17; naming three colors; what bees make; counting one to five; hello in Spanish; two animals that can fly; the opposite of hot; repeating "the sky is blue"; the first month of the year; repeating the word 'blue' two times; 'cat' in uppercase; reversing 'abc'; listing numbers 1 to 3 with commas and no spaces; spelling out the number 5; repeating '!' four times; 'Monday' and 'Tuesday' in order; 'hello world' in uppercase; and the bare drills 12+15, 9*6, 100-37, 48/4, 15+23-10, 8*7+6, 200/5.
- Keep answers short: knowledge and instruct answers at most 6 words; math answers a single number.
- For each item also give exactly 2 plausible but WRONG answers in the same surface form as the correct answer (same leading-space convention, similar length): plausible confusions, not jokes.
- Vary the topics widely.
- The correct answer must actually be correct. Double-check every math result."""

SHAPE = ('Reply with ONLY a JSON array, no markdown fences, no commentary, of exactly 24 objects '
         'in this shape:\n{"bucket": "%s", "prompt": "...", "answer": "...", "wrong": ["...", "..."]}')

BUCKET_PROMPTS = {
    "knowledge": """You are writing evaluation probe items for a small language model benchmark. Write 24 NEW items for the bucket "knowledge": a short factual sentence fragment as the prompt; the answer is the natural continuation of that fragment, beginning with a space. Example shape: prompt "The capital of France is", answer " Paris".

""" + COMMON_RULES + "\n\n" + (SHAPE % "knowledge"),
    "instruct": """You are writing evaluation probe items for a small language model benchmark. Write 24 NEW items for the bucket "instruct": a short direct command or format-constrained request as the prompt; the answer is a short compliant reply beginning with a space, often ending with a period. Example shape: prompt "Name three fruits.", answer " Apple, banana, orange."

""" + COMMON_RULES + "\n\n" + (SHAPE % "instruct"),
    "math": """You are writing evaluation probe items for a small language model benchmark. Write 24 NEW items for the bucket "math": a short arithmetic word problem ending with "Answer with just the number."; the answer is the bare number with no space and no units, e.g. "42". The arithmetic must be correct and checkable. Use varied word-problem settings (money, distance, time, groups of objects, ages, measurements), not bare drills like "What is 12 + 15?".

""" + COMMON_RULES + "\n\n" + (SHAPE % "math"),
}


def validate_bucket(items, bucket, excluded_norm, excluded_raw):
    problems = []
    if not isinstance(items, list) or len(items) != PER_BUCKET:
        return [f"expected a list of {PER_BUCKET} items, got {type(items).__name__} "
                f"len={len(items) if isinstance(items, list) else '?'}"]
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            problems.append(f"item {i} is not an object")
            continue
        for k in ("bucket", "prompt", "answer", "wrong"):
            if k not in it:
                problems.append(f"item {i} missing key {k}")
        if it.get("bucket") != bucket:
            problems.append(f"item {i} bucket is {it.get('bucket')!r}, expected {bucket!r}")
        if not isinstance(it.get("wrong"), list) or len(it.get("wrong", [])) != 2:
            problems.append(f"item {i} wrong must be a list of 2")
        if bucket == "math" and not re.fullmatch(r"-?\d+(\.\d+)?", str(it.get("answer", "")).strip()):
            problems.append(f"item {i} math answer is not a bare number: {it.get('answer')!r}")
    prompts = [it.get("prompt", "") for it in items if isinstance(it, dict)]
    if len({norm(p) for p in prompts}) != len(prompts):
        problems.append("duplicate prompts inside the new bucket set")
    for p in prompts:
        if norm(p) in excluded_norm:
            problems.append(f"prompt duplicates an existing item: {p!r}")
        else:
            worst = max((jaccard(p, e) for e in excluded_raw), default=0.0)
            if worst >= 0.7:
                problems.append(f"prompt too close to an existing item (jaccard {worst:.2f}): {p!r}")
    return problems


def gen_bucket(bucket, args, record, excluded_norm, excluded_raw):
    purpose = f"alien_sweep_heldout96_probe_generation_{bucket}"
    content, usage, elapsed, finish = chat(BUCKET_PROMPTS[bucket], 24000, purpose, args.usage_log)
    items = extract_json(content)
    problems = validate_bucket(items, bucket, excluded_norm, excluded_raw)
    entry = {"attempts": [{"usage": usage, "elapsed_s": elapsed, "finish_reason": finish,
                           "content_chars": len(content)}],
             "raw_content": content, "validation_problems": problems}
    record["buckets"][bucket] = entry
    if problems:
        fix_prompt = (
            "Your previous probe set for the bucket \"" + bucket + "\" had these problems:\n- "
            + "\n- ".join(problems)
            + "\n\nRewrite the FULL set of 24 items for this bucket fixing every problem. "
              "Same rules and same JSON shape as before: ONLY a JSON array of 24 objects "
              "{\"bucket\": \"" + bucket + "\", \"prompt\", \"answer\", \"wrong\": [2 items]}, "
              "all new, all answers correct, math answers bare numbers."
        )
        content2, usage2, elapsed2, finish2 = chat(
            fix_prompt, 24000, purpose + "_retry", args.usage_log)
        items = extract_json(content2)
        problems = validate_bucket(items, bucket, excluded_norm, excluded_raw)
        entry["attempts"].append({"usage": usage2, "elapsed_s": elapsed2,
                                  "finish_reason": finish2, "content_chars": len(content2)})
        entry["raw_content_retry"] = content2
        entry["validation_problems_after_retry"] = problems
    if problems:
        raise RuntimeError(f"{bucket} validation still failing: {problems}")
    return items


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exclude", default="/tmp/signet_prompts.json",
                    help="JSON list of Signet prompt strings (kept outside the repo)")
    ap.add_argument("--also-exclude", default="data/heldout_probes_spark.json",
                    help="probes file whose prompts are also excluded (first held-out 24)")
    ap.add_argument("--record", default="/tmp/heldout96_gen_record.json")
    ap.add_argument("--probes-out", default="data/heldout72_probes_spark.json")
    ap.add_argument("--usage-log", default="results/api_usage_log.jsonl")
    args = ap.parse_args()

    signet_prompts = json.loads(Path(args.exclude).read_text())
    heldout24 = json.loads(Path(args.also_exclude).read_text())
    heldout24_prompts = [it["prompt"] for it in heldout24]
    excluded_raw = list(signet_prompts) + heldout24_prompts
    excluded_norm = {norm(p) for p in excluded_raw}

    record = {"model": MODEL, "provider": PROVIDER, "started": now_z(),
              "excluded_prompt_count": len(excluded_raw),
              "excluded_signet": len(signet_prompts),
              "excluded_heldout24": len(heldout24_prompts),
              "buckets": {}}
    all_items = []
    for bucket in BUCKETS:
        items = gen_bucket(bucket, args, record, excluded_norm, excluded_raw)
        # Prompts accepted for one bucket also exclude later buckets.
        for it in items:
            excluded_raw.append(it["prompt"])
            excluded_norm.add(norm(it["prompt"]))
        all_items.extend(items)
        print(f"{bucket}: 24 items OK")

    if len(all_items) != 72:
        raise RuntimeError(f"expected 72 items, got {len(all_items)}")
    out = Path(args.probes_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(all_items, indent=2) + "\n")
    print(f"probes: 72 items written to {out}")
    record["finished"] = now_z()
    Path(args.record).write_text(json.dumps(record, indent=2) + "\n")
    print(f"record written to {args.record}")


if __name__ == "__main__":
    main()
