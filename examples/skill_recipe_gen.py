#!/usr/bin/env python3
"""Step 4 (allocation test): ask Muse Spark Open for NuExtract-pair recipes.

Same bytes, smarter placement. The size axis was tested with uniform
rank 64 / 128 (results/skill_demo_ranks.json). This asks Muse Spark
Open (Baseten) for per-layer-type rank recipes for the NuExtract pair
(Qwen2.5-0.5B shapes) under the ORIGINAL rank-32 real budget of
19,434,496 bytes, telling it the gate finding: the extraction skill is
decided by the first generated token, uniform rank 32 flips only 1 of
10 gates, so allocation should weigh protecting the embedding and the
output-side layers.

One Baseten call (one retry only if the reply cannot be parsed at
all), max_tokens 16000: Spark Open spends most of its budget on
reasoning before answering (the 8k-cap failures in
results/second_pair_check1.json are the lesson). The call is logged to
results/api_usage_log.jsonl. Validation is strict: exact layer keys,
integer ranks within caps, and the total priced on the REAL model
shapes with factored.storage_bytes (embed once + 24 blocks) must be
<= BUDGET. The chosen recipe is the first schema-valid one in Spark's
own best-first order; it is written to /tmp/skill_recipe.json in the
{"name": ..., "ranks": {...}} shape examples/make_patch.py --recipe
accepts, and the full exchange to /tmp/skill_recipe_exchange.json.
"""

import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from factored import storage_bytes  # noqa: E402

HELPER = Path.home() / "workspace/custom-connectors/custom.baseten/bin/baseten_api.py"
MODEL = "meta-models/muse-spark-open-1026"
PROVIDER = "baseten"
MAX_TOKENS = 16000
BLOCKS = 24
BUDGET = 19_434_496  # uniform rank 32 on the real shapes, exact

# Real Qwen2.5-0.5B delta shapes (rows x cols) per layer type.
LAYERS = {
    "embed": (151936, 896),
    "attn.q_proj": (896, 896),
    "attn.k_proj": (128, 896),
    "attn.v_proj": (128, 896),
    "attn.o_proj": (896, 896),
    "mlp.gate": (4864, 896),
    "mlp.up": (4864, 896),
    "mlp.down": (896, 4864),
}


def recipe_total_bytes(ranks):
    total = storage_bytes(ranks["embed"], LAYERS["embed"])
    for name, shape in LAYERS.items():
        if name == "embed":
            continue
        total += BLOCKS * storage_bytes(ranks[name], shape)
    return total


def build_prompt():
    table = "\n".join(
        f"  {name}: delta matrix {m} x {n}, rank may be 0..{min(m, n)}"
        for name, (m, n) in LAYERS.items()
    )
    return f"""You are proposing compression recipes for a factored 1-bit weight-delta format. A recipe assigns one integer rank to each layer TYPE; that rank is used for that layer type in all {BLOCKS} transformer blocks (the embedding is a single matrix). The stored size of one matrix at rank r is priced exactly as:

  bytes(matrix, r) = ceil(rows * r / 8) + 4 * rows + 2 * cols * r

Layers (rows x cols of the delta matrix):
{table}

The total size of a recipe is bytes(embed) + {BLOCKS} * (sum of bytes over the other 7 layer types), and it must be <= {BUDGET} bytes. That is exactly the cost of the uniform rank-32 recipe on this model; you have the same bytes, spend them differently.

The model pair is Qwen2.5-0.5B base and NuExtract-1.5-tiny, a fine-tune for structured JSON extraction (read a text and a JSON template, answer with the filled template). The finding you are designing against: this skill is gated by the FIRST generated token. The fine-tune starts the JSON; the plain base emits end-of-text immediately and answers nothing (0 of 10 test prompts). Our uniform rank-32 patch flips that gate on only 1 of 10 prompts (on the 9 others the patched model still stops immediately), even though the one extraction it does start is fully correct. Bigger uniform patches barely help (rank 64 and rank 128 each flip 2 of 10). So placement, not size, is the open question. Weigh protecting the embedding (it feeds every token position and, with tied weights, the output head) and the output-side layers (attn.o_proj, mlp.down) that shape the final logits, if you judge that is where the start-vs-stop decision lives.

Propose exactly 5 recipes, ordered best-first: put the recipe you recommend most first. Make them genuinely different from each other and from uniform: uneven allocations are the point. Every recipe must include every layer name exactly once in its "ranks" object, with an integer rank (0 is allowed and means that layer type's delta is dropped).

Reply with ONLY a JSON object, no markdown fences, no commentary, in exactly this shape:
{{"recipes": [{{"name": "<short name>", "reason": "<one sentence>", "ranks": {{"embed": 0, "attn.q_proj": 0, "attn.k_proj": 0, "attn.v_proj": 0, "attn.o_proj": 0, "mlp.gate": 0, "mlp.up": 0, "mlp.down": 0}}}}]}}
Replace the zeros with your ranks. Check your arithmetic: each recipe's total (embed once + {BLOCKS} blocks) must be <= {BUDGET} bytes."""


def _load_helper():
    spec = importlib.util.spec_from_file_location("baseten_api", HELPER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def call_spark(prompt):
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": MAX_TOKENS,
    }
    helper = _load_helper()
    started = time.time()
    result = helper.call("POST", "/v1/chat/completions", payload)
    elapsed = time.time() - started
    if "http_error" in result:
        raise RuntimeError(f"baseten HTTP {result['http_error']}: {result.get('body', '')[:500]}")
    return result, elapsed


def log_usage(usage, purpose, when):
    entry = {
        "provider": PROVIDER,
        "model": MODEL,
        "time": when,
        "purpose": purpose,
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }
    log = ROOT / "results" / "api_usage_log.jsonl"
    with open(log, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def extract_json(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return json.loads(text[start:end + 1])
    raise ValueError("no JSON object found in reply")


def validate_recipe(recipe, idx):
    errors = []
    name = recipe.get("name") if isinstance(recipe, dict) else None
    if not isinstance(recipe, dict):
        return {"index": idx, "name": None, "valid": False,
                "errors": ["recipe is not a JSON object"], "total_bytes": None}
    ranks = recipe.get("ranks")
    if not isinstance(ranks, dict):
        return {"index": idx, "name": name, "valid": False,
                "errors": ["missing or non-object 'ranks'"], "total_bytes": None}
    keys = set(ranks)
    if keys != set(LAYERS):
        if set(LAYERS) - keys:
            errors.append(f"missing layers: {sorted(set(LAYERS) - keys)}")
        if keys - set(LAYERS):
            errors.append(f"unknown layers: {sorted(keys - set(LAYERS))}")
    for layer, rank in ranks.items():
        if layer not in LAYERS:
            continue
        if type(rank) is not int:
            errors.append(f"{layer}: rank {rank!r} is not an integer")
        elif rank < 0:
            errors.append(f"{layer}: rank {rank} is negative")
        elif rank > min(LAYERS[layer]):
            errors.append(f"{layer}: rank {rank} exceeds max {min(LAYERS[layer])}")
    total = None
    if not errors:
        total = recipe_total_bytes(ranks)
        if total > BUDGET:
            errors.append(f"total {total} bytes exceeds budget {BUDGET}")
    return {"index": idx, "name": name, "valid": not errors,
            "errors": errors, "total_bytes": total}


def main():
    # Sanity: the stated budget must be the true uniform rank-32 price.
    uniform = {name: 32 for name in LAYERS}
    assert recipe_total_bytes(uniform) == BUDGET, recipe_total_bytes(uniform)

    prompt = build_prompt()
    attempts = []
    parsed = None
    content = None
    for attempt in (1, 2):
        when = datetime.now(timezone.utc).isoformat()
        resp, elapsed = call_spark(prompt)
        usage = resp.get("usage", {})
        log_usage(usage, "skill_recipe_gen_allocation_test", when)
        msg = resp["choices"][0]["message"]
        content = msg.get("content") or ""
        attempts.append({
            "attempt": attempt, "time": when, "elapsed_s": round(elapsed, 2),
            "usage": usage,
            "reasoning_chars": len(msg.get("reasoning_content") or ""),
            "content_chars": len(content),
        })
        try:
            parsed = extract_json(content)
            break
        except (json.JSONDecodeError, ValueError) as e:
            attempts[-1]["parse_error"] = str(e)
            if attempt == 2:
                parsed = None

    recipes = []
    validation = []
    if isinstance(parsed, dict) and isinstance(parsed.get("recipes"), list):
        recipes = parsed["recipes"]
        validation = [validate_recipe(r, i) for i, r in enumerate(recipes)]
    chosen = None
    for v in validation:
        if v["valid"]:
            chosen = recipes[v["index"]]
            break

    exchange = {
        "call": {"provider": PROVIDER, "model": MODEL, "max_tokens": MAX_TOKENS,
                 "budget_bytes": BUDGET, "blocks": BLOCKS,
                 "layers": {k: list(v) for k, v in LAYERS.items()}},
        "prompt": prompt,
        "attempts": attempts,
        "raw_content": content,
        "recipes": recipes,
        "validation": validation,
        "chosen_recipe": chosen,
    }
    Path("/tmp/skill_recipe_exchange.json").write_text(json.dumps(exchange, indent=2) + "\n")
    if chosen is not None:
        Path("/tmp/skill_recipe.json").write_text(
            json.dumps({"name": chosen["name"], "ranks": chosen["ranks"]}, indent=2) + "\n")
    print(f"attempts: {len(attempts)}; recipes returned: {len(recipes)}")
    for v in validation:
        status = "valid" if v["valid"] else "INVALID: " + "; ".join(v["errors"])
        size = f"{v['total_bytes']:,} B" if v["total_bytes"] is not None else "n/a"
        print(f"  [{v['index']}] {v['name']}: {status} (total {size})")
    if chosen is not None:
        cv = validation[[r['name'] for r in recipes].index(chosen['name'])]
        print(f"CHOSEN (Spark's best-first order): {chosen['name']} at {cv['total_bytes']:,} B")
        print(f"ranks: {chosen['ranks']}")
    else:
        print("NO VALID RECIPE")


if __name__ == "__main__":
    main()
