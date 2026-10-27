"""Alien Sweep held-out guard: Spark generation step.

Two Muse Spark calls (Meta Model API, muse-spark-1.3), both logged to
results/api_usage_log.jsonl:

1. Fresh held-out probe set: 24 NEW items in the Signet style and
   buckets (8 knowledge, 8 instruct, 8 math), each with a prompt, the
   correct answer, and two plausible wrong answers. Saved as a plain
   JSON list (the shape the Signet scorer consumes: bucket / prompt /
   answer, plus a "wrong" list the task asks for) at
   data/heldout_probes_spark.json. Novelty is checked against the
   pre-existing Signet prompts (passed via --exclude, a JSON list of
   prompt strings kept OUTSIDE the repo): no exact normalized match,
   and token-set Jaccard >= 0.7 against any Signet prompt is flagged.

2. Byte-matched variant of the Stage 2 winner mlp_behemoth: same
   style (MLP front-loaded, attn.k_proj rank 0, attention and embed
   low), rebalanced to fit the human uniform rank-32 recipe's real
   byte budget (19,434,496 bytes on the real Qwen2.5-0.5B shapes).
   The variant is priced exactly as Stage 2 priced recipes:
   factored.storage_bytes summed over all 169 real matrices
   (embedding + 24 blocks). If Spark's map prices over budget, the
   computed overage is fed back and Spark is asked again (max 3
   attempts); every attempt is recorded.

Run from the repo root on the Muse VM (needs the Meta connector):

    python3 examples/alien_sweep_heldout_gen.py \
        --exclude /tmp/signet_prompts.json \
        --record /tmp/heldout_gen_record.json
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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import factored  # noqa: E402

MODEL = "muse-spark-1.3"
PROVIDER = "meta-model-api"

# Real Qwen2.5-0.5B shapes (rows, cols) per layer type and how many
# matrices of that type the rank map covers (embed x1, blocks x24).
REAL_SHAPES = {
    "embed": (151936, 896),
    "attn.q_proj": (896, 896),
    "attn.k_proj": (128, 896),
    "attn.v_proj": (128, 896),
    "attn.o_proj": (896, 896),
    "mlp.gate": (4864, 896),
    "mlp.up": (4864, 896),
    "mlp.down": (896, 4864),
}
COUNTS = {name: (1 if name == "embed" else 24) for name in REAL_SHAPES}
BUDGET = 19_434_496  # uniform rank-32, real shapes (Stage 2)

MLP_BEHEMOTH = {
    "embed": 10, "attn.q_proj": 20, "attn.k_proj": 0, "attn.v_proj": 20,
    "attn.o_proj": 20, "mlp.gate": 45, "mlp.up": 45, "mlp.down": 50,
}


def price_real(ranks):
    return sum(
        COUNTS[name] * factored.storage_bytes(int(ranks[name]), REAL_SHAPES[name])
        for name in REAL_SHAPES
    )


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
    """Pull the first JSON value (object or array) out of a reply."""
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
# Call 1: held-out probes
# ---------------------------------------------------------------------------

PROBE_PROMPT = """You are writing evaluation probe items for a small language model benchmark. Write 24 NEW items in exactly this style, 8 per bucket:

- bucket "knowledge": a short factual sentence fragment as the prompt; the answer is the natural continuation of that fragment, beginning with a space. Example shape: prompt "The capital of France is", answer " Paris".
- bucket "instruct": a short direct command or format-constrained request as the prompt; the answer is a short compliant reply beginning with a space, often ending with a period. Example shape: prompt "Name three fruits.", answer " Apple, banana, orange."
- bucket "math": a short arithmetic word problem ending with "Answer with just the number."; the answer is the bare number with no space and no units, e.g. "42". The arithmetic must be correct and checkable.

Rules:
- Every item must be NEW: do not reuse or lightly reword common textbook examples such as capitals of Japan or France, the boiling point of water, the chemical symbol for gold, the largest planet, the author of Romeo and Juliet, a train at 60 mph for 2.5 hours, 15 percent of 200, a rectangle of 8 by 5, 3 dozen eggs minus 14, 7 squared plus 8 squared, a 40 dollar shirt at 25 percent off, minutes in 3.5 hours, the prime after 17, naming three colors, what bees make, counting one to five, hello in Spanish, two animals that can fly, the opposite of hot, repeating "the sky is blue", or the first month of the year.
- Keep answers short: knowledge and instruct answers at most 6 words; math answers a single number.
- For each item also give exactly 2 plausible but WRONG answers in the same surface form as the correct answer (same leading-space convention, similar length): plausible confusions, not jokes.
- Vary the topics widely within each bucket.
- The correct answer must actually be correct. Double-check every math result.

Reply with ONLY a JSON array, no markdown fences, no commentary, of exactly 24 objects in this shape:
{"bucket": "knowledge" | "instruct" | "math", "prompt": "...", "answer": "...", "wrong": ["...", "..."]}
Order: the 8 knowledge items first, then the 8 instruct items, then the 8 math items."""


def validate_probes(items, exclude_path):
    problems = []
    if not isinstance(items, list) or len(items) != 24:
        return [f"expected a list of 24 items, got {type(items).__name__} "
                f"len={len(items) if isinstance(items, list) else '?'}"]
    counts = {}
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            problems.append(f"item {i} is not an object")
            continue
        for k in ("bucket", "prompt", "answer", "wrong"):
            if k not in it:
                problems.append(f"item {i} missing key {k}")
        b = it.get("bucket")
        counts[b] = counts.get(b, 0) + 1
        if not isinstance(it.get("wrong"), list) or len(it.get("wrong", [])) != 2:
            problems.append(f"item {i} ({b}) wrong must be a list of 2")
        if b == "math" and not re.fullmatch(r"-?\d+(\.\d+)?", str(it.get("answer", "")).strip()):
            problems.append(f"item {i} math answer is not a bare number: {it.get('answer')!r}")
    if counts != {"knowledge": 8, "instruct": 8, "math": 8}:
        problems.append(f"bucket counts wrong: {counts}")
    prompts = [it.get("prompt", "") for it in items if isinstance(it, dict)]
    if len({norm(p) for p in prompts}) != len(prompts):
        problems.append("duplicate prompts inside the new set")
    if exclude_path:
        excluded = [norm(p) for p in json.loads(Path(exclude_path).read_text())]
        for p in prompts:
            if norm(p) in excluded:
                problems.append(f"prompt duplicates a Signet item: {p!r}")
            else:
                worst = max((jaccard(p, e) for e in excluded), default=0.0)
                if worst >= 0.7:
                    problems.append(f"prompt too close to a Signet item (jaccard {worst:.2f}): {p!r}")
    return problems


def gen_probes(args, record):
    content, usage, elapsed, finish = chat(
        PROBE_PROMPT, 24000, "alien_sweep_heldout_probe_generation", args.usage_log)
    items = extract_json(content)
    problems = validate_probes(items, args.exclude)
    record["probes"] = {
        "attempts": [{"usage": usage, "elapsed_s": elapsed, "finish_reason": finish,
                      "content_chars": len(content)}],
        "raw_content": content,
        "validation_problems": problems,
    }
    if problems:
        fix_prompt = (
            "Your previous probe set had these problems:\n- " + "\n- ".join(problems)
            + "\n\nRewrite the FULL set of 24 items fixing every problem. Same rules and "
              "same JSON shape as before: ONLY a JSON array of 24 objects "
              "{\"bucket\", \"prompt\", \"answer\", \"wrong\": [2 items]}, 8 knowledge, "
              "8 instruct, 8 math, all new, all answers correct, math answers bare numbers."
        )
        content2, usage2, elapsed2, finish2 = chat(
            fix_prompt, 24000, "alien_sweep_heldout_probe_generation_retry", args.usage_log)
        items = extract_json(content2)
        problems = validate_probes(items, args.exclude)
        record["probes"]["attempts"].append(
            {"usage": usage2, "elapsed_s": elapsed2, "finish_reason": finish2,
             "content_chars": len(content2)})
        record["probes"]["raw_content_retry"] = content2
        record["probes"]["validation_problems_after_retry"] = problems
    if problems:
        raise RuntimeError(f"probe validation still failing: {problems}")
    return items


# ---------------------------------------------------------------------------
# Call 2: byte-matched mlp_behemoth variant
# ---------------------------------------------------------------------------

def variant_prompt(feedback=None):
    lines = [
        "You are rebalancing a compression recipe for a factored 1-bit weight-delta format. "
        "A recipe assigns an integer rank to each of 8 layer types of the Qwen2.5-0.5B model. "
        "The rank for a layer type applies to that matrix in every transformer block, so the "
        "recipe's true stored size is the sum over all 169 real matrices, priced per matrix as:",
        "",
        "  bytes(matrix, r) = ceil(rows * r / 8) + 4 * rows + 2 * cols * r   (the 4 * rows term is paid even at r = 0)",
        "",
        "Real shapes (rows x cols), and how many matrices of each type exist:",
        "  embed:       151936 x 896,  x1  (cost at rank r: 607744 + 20784*r)",
        "  attn.q_proj: 896 x 896,     x24 (cost at rank r: 3584 + 1904*r each)",
        "  attn.k_proj: 128 x 896,     x24 (cost at rank r: 512 + 1808*r each)",
        "  attn.v_proj: 128 x 896,     x24 (cost at rank r: 512 + 1808*r each)",
        "  attn.o_proj: 896 x 896,     x24 (cost at rank r: 3584 + 1904*r each)",
        "  mlp.gate:    4864 x 896,    x24 (cost at rank r: 19456 + 2400*r each)",
        "  mlp.up:      4864 x 896,    x24 (cost at rank r: 19456 + 2400*r each)",
        "  mlp.down:    896 x 4864,    x24 (cost at rank r: 3584 + 9840*r each)",
        "",
        "Handy totals: +1 rank on a layer type across all its matrices costs: embed 20784, "
        "attn.q_proj 45696, attn.k_proj 43392, attn.v_proj 43392, attn.o_proj 45696, "
        "mlp.gate 57600, mlp.up 57600, mlp.down 236160 bytes. mlp.down is by far the most "
        "expensive rank in the model.",
        "",
        "The current winning recipe, mlp_behemoth, is:",
        json.dumps(MLP_BEHEMOTH),
        "It prices at 21,719,776 bytes on the real shapes. The budget is 19,434,496 bytes "
        "(that is what the human uniform rank-32 recipe costs on the same real shapes), so "
        "the variant must shed at least 2,285,280 bytes of rank cost.",
        "",
        "Propose ONE rebalanced variant that keeps the mlp_behemoth style:",
        "- attn.k_proj stays at rank 0.",
        "- The MLP types (mlp.gate, mlp.up, mlp.down) keep the highest ranks in the map; "
        "the recipe stays MLP front-loaded.",
        "- Attention (q/v/o) and embed stay at or below their mlp_behemoth values.",
        "- Every rank is an integer >= 0; mlp ranks must stay >= 30 so the recipe keeps "
        "its character.",
        "- The total priced size on the real shapes must be <= 19,434,496 bytes. Check "
        "your arithmetic with the per-type costs above before answering.",
        "",
        "Reply with ONLY a JSON object, no markdown fences, no commentary, in exactly this shape:",
        '{"name": "<short name>", "reason": "<one sentence>", "ranks": {"embed": 0, '
        '"attn.q_proj": 0, "attn.k_proj": 0, "attn.v_proj": 0, "attn.o_proj": 0, '
        '"mlp.gate": 0, "mlp.up": 0, "mlp.down": 0}}',
        "Replace the zeros with your ranks.",
    ]
    if feedback:
        lines += ["", feedback]
    return "\n".join(lines)


def gen_variant(args, record):
    feedback = None
    attempts = []
    for attempt in range(1, 4):
        content, usage, elapsed, finish = chat(
            variant_prompt(feedback), 12000,
            f"alien_sweep_heldout_bytematched_variant_attempt{attempt}", args.usage_log)
        entry = {"attempt": attempt, "usage": usage, "elapsed_s": elapsed,
                 "finish_reason": finish, "raw_content": content}
        attempts.append(entry)
        try:
            obj = extract_json(content)
            ranks = {k: int(v) for k, v in obj["ranks"].items()}
            if set(ranks) != set(REAL_SHAPES):
                raise ValueError(f"rank keys mismatch: {sorted(ranks)}")
            if any(v < 0 for v in ranks.values()):
                raise ValueError("negative rank")
            total = price_real(ranks)
            entry["parsed_name"] = obj.get("name")
            entry["ranks"] = ranks
            entry["real_shape_bytes"] = total
            entry["within_budget"] = total <= BUDGET
            if total <= BUDGET:
                record["variant"] = {"attempts": attempts, "name": obj.get("name"),
                                     "reason": obj.get("reason"), "ranks": ranks,
                                     "real_shape_bytes": total, "budget_bytes": BUDGET}
                return record["variant"]
            feedback = (
                f"Your attempt {attempt} priced at {total:,} bytes on the real shapes, "
                f"which is {total - BUDGET:,} bytes OVER the 19,434,496 budget. Shed at "
                f"least that much more rank cost (remember mlp.down costs 236,160 bytes "
                f"per rank across the model, mlp.gate and mlp.up 57,600 each). Keep the "
                f"style rules and reply with the same JSON shape only."
            )
        except Exception as exc:  # parse or schema problem: feed it back
            entry["error"] = str(exc)
            feedback = (
                f"Your attempt {attempt} could not be used ({exc}). Reply with ONLY the "
                f"JSON object in the exact shape requested, integer ranks for exactly "
                f"the 8 layer names, total real-shape price <= 19,434,496 bytes."
            )
        entry["feedback_sent"] = feedback
    record["variant"] = {"attempts": attempts, "name": None}
    raise RuntimeError("Spark variant stayed over budget after 3 attempts")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exclude", default="/tmp/signet_prompts.json")
    ap.add_argument("--record", default="/tmp/heldout_gen_record.json")
    ap.add_argument("--probes-out", default="data/heldout_probes_spark.json")
    ap.add_argument("--usage-log", default="results/api_usage_log.jsonl")
    args = ap.parse_args()

    record = {"model": MODEL, "provider": PROVIDER, "started": now_z()}
    items = gen_probes(args, record)
    out = Path(args.probes_out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(items, indent=2) + "\n")
    print(f"probes: 24 items written to {out}")

    variant = gen_variant(args, record)
    print(f"variant: {variant['name']} ranks={variant['ranks']} "
          f"real_bytes={variant['real_shape_bytes']} budget={BUDGET}")
    record["finished"] = now_z()
    Path(args.record).write_text(json.dumps(record, indent=2) + "\n")
    print(f"record written to {args.record}")


if __name__ == "__main__":
    main()
