"""Alien Sweep go/no-go check 1: can Muse Spark Open propose recipes?

    python3 examples/alien_sweep_check1.py

Day-2 check 1 from BUILD_PLAN.md: Spark must produce 5 schema-valid
recipe JSONs quickly, layer-to-rank maps only, under a fixed total size
budget. This script makes ONE Baseten chat call to Muse Spark Open
(two only if the first response cannot be parsed as JSON at all), then
validates every recipe against a strict schema:

- the reply parses as JSON with a "recipes" list of exactly 5 objects
- each recipe's "ranks" object has exactly the known layer names as keys
- every rank is a non-negative integer no larger than the layer's
  smaller dimension (bools, floats and strings are rejected)
- the total size, priced with src/factored.py's storage_bytes (the real
  on-disk format), stays within the budget

The budget is the price of the human recipe (uniform rank 32 on every
layer) under the same pricing, so an alien recipe wins room only by
spending the same bytes differently.

Every Baseten call is appended to results/api_usage_log.jsonl with
provider, model, time, purpose and token counts, and the full outcome
(prompt, raw reply, parsed recipes, per-recipe verdicts) is written to
results/alien_sweep_check1.json. Verdict GO means all 5 recipes were
schema-valid on the first parseable reply; anything else is NO-GO for
check 1 and, per the plan, points at the human rank sweep fallback.

Implementation note: the connector helper's CLI prints its result
truncated to 6000 characters, which cuts long Spark replies (the
reasoning alone can exceed that) mid-JSON and hides the usage block.
This script therefore imports the helper as a module and calls its
``call()`` function, which is the same registered-credential request
path; only the lossy print step is bypassed.
"""

import importlib.util
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np  # noqa: F401  (keeps the numpy-only dependency explicit)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from factored import storage_bytes  # noqa: E402

HELPER = Path.home() / "workspace/custom-connectors/custom.baseten/bin/baseten_api.py"
MODEL = "meta-models/muse-spark-open-1026"
PROVIDER = "baseten"
MAX_TOKENS = 8000

# The layer table the recipes allocate ranks over: name -> (rows, cols)
# of the delta matrix for that layer, in the format storage_bytes
# prices: signs for the (rows x rank) factor U, fp16 for (cols x rank) V.
LAYERS = {
    "embed": (1024, 512),
    "attn.q_proj": (512, 512),
    "attn.k_proj": (512, 512),
    "attn.v_proj": (512, 512),
    "attn.o_proj": (512, 512),
    "mlp.gate": (512, 1408),
    "mlp.up": (512, 1408),
    "mlp.down": (1408, 512),
}
HUMAN_RANK = 32
BUDGET_BYTES = sum(storage_bytes(HUMAN_RANK, shape) for shape in LAYERS.values())


def recipe_total_bytes(ranks):
    return sum(storage_bytes(ranks[name], LAYERS[name]) for name in LAYERS)


def build_prompt():
    table = "\n".join(
        f"  {name}: delta matrix {m} x {n}, rank may be 0..{min(m, n)}"
        for name, (m, n) in LAYERS.items()
    )
    return f"""You are proposing compression recipes for a factored 1-bit weight-delta format. A recipe assigns an integer rank to each layer of one transformer block set. The stored size of one layer at rank r is priced exactly as:

  bytes(layer, r) = ceil(rows * r / 8) + 4 * rows + 2 * cols * r

Layers (rows x cols of the delta matrix):
{table}

The total size of a recipe is the sum of bytes(layer, rank) over all layers and must be <= {BUDGET_BYTES} bytes (that is the cost of the uniform rank-{HUMAN_RANK} recipe; you have the same bytes, spend them differently).

Propose exactly 5 recipes. Make them genuinely different from each other and from the uniform recipe: uneven allocations are the point. Ideas you may use or ignore: starve some layers to rank 0 and feed others, front-load early layers, front-load the MLP, protect attention output, protect the embedding. Every recipe must include every layer name exactly once in its "ranks" object, with an integer rank (0 is allowed and means the layer's delta is dropped).

Reply with ONLY a JSON object, no markdown fences, no commentary, in exactly this shape:
{{"recipes": [{{"name": "<short name>", "reason": "<one sentence>", "ranks": {{"embed": 0, "attn.q_proj": 0, "attn.k_proj": 0, "attn.v_proj": 0, "attn.o_proj": 0, "mlp.gate": 0, "mlp.up": 0, "mlp.down": 0}}}}]}}
Replace the zeros with your ranks. Check your arithmetic: each recipe's total must be <= {BUDGET_BYTES} bytes."""


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
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def extract_json(text):
    """Parse the reply as JSON; tolerate code fences or stray prose."""
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
        missing = sorted(set(LAYERS) - keys)
        extra = sorted(keys - set(LAYERS))
        if missing:
            errors.append(f"missing layers: {missing}")
        if extra:
            errors.append(f"unknown layers: {extra}")
    for layer, rank in ranks.items():
        if layer not in LAYERS:
            continue
        if type(rank) is not int:  # rejects bool, float, str
            errors.append(f"{layer}: rank {rank!r} is not an integer")
        elif rank < 0:
            errors.append(f"{layer}: rank {rank} is negative")
        elif rank > min(LAYERS[layer]):
            errors.append(f"{layer}: rank {rank} exceeds max {min(LAYERS[layer])}")
    total = None
    if not errors:
        total = recipe_total_bytes(ranks)
        if total > BUDGET_BYTES:
            errors.append(f"total {total} bytes exceeds budget {BUDGET_BYTES}")
    return {"index": idx, "name": name, "valid": not errors,
            "errors": errors, "total_bytes": total}


# Calls made while diagnosing the helper's 6000-char print truncation,
# before this script switched to the module import. The probe call's
# usage survived (its reply was short); the two full-prompt calls were
# cut mid-JSON by the print cap, so their token counts are lost. They
# are recorded here and in the usage log so the spend accounting stays
# honest even where the counts cannot be recovered.
PRIOR_CALLS = [
    {
        "provider": PROVIDER, "model": MODEL,
        "time": "2026-10-27T14:20:57Z (approx)",
        "purpose": "alien_sweep_check1_recipe_generation (exploratory, output truncated by helper print cap)",
        "prompt_tokens": None, "completion_tokens": None, "total_tokens": None,
    },
    {
        "provider": PROVIDER, "model": MODEL,
        "time": "2026-10-27T14:21:22Z",
        "purpose": "baseten_helper_format_probe (tiny call to inspect helper output)",
        "prompt_tokens": 152, "completion_tokens": 84, "total_tokens": 236,
    },
    {
        "provider": PROVIDER, "model": MODEL,
        "time": "2026-10-27T14:21:55Z",
        "purpose": "alien_sweep_check1_recipe_generation (exploratory, output truncated by helper print cap)",
        "prompt_tokens": None, "completion_tokens": None, "total_tokens": None,
    },
]


def main():
    log_path = ROOT / "results" / "api_usage_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with open(log_path, "a") as f:
        for entry in PRIOR_CALLS:
            f.write(json.dumps(entry) + "\n")

    prompt = build_prompt()
    attempts = []
    parsed = None
    content = None
    total_elapsed = 0.0
    # One retry, only if the first reply cannot be parsed as JSON at all.
    for attempt in (1, 2):
        when = datetime.now(timezone.utc).isoformat()
        resp, elapsed = call_spark(prompt)
        total_elapsed += elapsed
        usage = resp.get("usage", {})
        log_usage(usage, "alien_sweep_check1_recipe_generation", when)
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

    validation = []
    recipes = []
    if isinstance(parsed, dict) and isinstance(parsed.get("recipes"), list):
        recipes = parsed["recipes"]
        validation = [validate_recipe(r, i) for i, r in enumerate(recipes)]
    valid_count = sum(1 for v in validation if v["valid"])
    go = (
        parsed is not None
        and len(recipes) == 5
        and valid_count == 5
    )
    verdict = "GO" if go else "NO-GO"

    out = {
        "check": "alien_sweep_day2_check1_spark_recipes_schema_valid",
        "provider": PROVIDER,
        "model": MODEL,
        "layers": {k: list(v) for k, v in LAYERS.items()},
        "budget_bytes": BUDGET_BYTES,
        "budget_basis": f"uniform rank {HUMAN_RANK} on every layer, priced by factored.storage_bytes",
        "prompt": prompt,
        "attempts": attempts,
        "elapsed_s_total": round(total_elapsed, 2),
        "raw_content": content,
        "recipes": recipes,
        "validation": validation,
        "valid_count": valid_count,
        "recipes_returned": len(recipes),
        "verdict": verdict,
        "prior_exploratory_calls": PRIOR_CALLS,
    }
    out_path = ROOT / "results" / "alien_sweep_check1.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n")

    print(f"budget: {BUDGET_BYTES:,} bytes (uniform rank {HUMAN_RANK})")
    print(f"recipes returned: {len(recipes)}, schema-valid: {valid_count}")
    for v in validation:
        status = "valid" if v["valid"] else "INVALID: " + "; ".join(v["errors"])
        size = f"{v['total_bytes']:,} B" if v["total_bytes"] is not None else "n/a"
        print(f"  [{v['index']}] {v['name']}: {status} (total {size})")
    print(f"elapsed: {total_elapsed:.1f}s over {len(attempts)} call(s)")
    print(f"verdict: {verdict}")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
