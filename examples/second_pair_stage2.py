"""Second pair (SmolLM2-360M): Alien Sweep Stage 1 + Stage 2.

    # recipe generation, on the Muse VM (Baseten connector):
    python3 examples/second_pair_stage2.py recipes
    # on Flash, with the qwen-test venv:
    python3 second_pair_stage2.py stage1 \
        --npz ~/fc-v04-sweep2/precompute.npz \
        --recipes /tmp/second_pair_check1.json \
        --out ~/fc-v04-sweep2/stage1.json
    python3 second_pair_stage2.py build \
        --base ~/qwen-test/data/smollm2-360m.safetensors \
        --instruct ~/qwen-test/data/smollm2-360m-instruct.safetensors \
        --recipes /tmp/second_pair_check1.json \
        --workdir ~/fc-v04-sweep2/stage2
    python3 second_pair_stage2.py eval --config base \
        --base ... --instruct ... --workdir ~/fc-v04-sweep2/stage2
    # ... eval full_delta, each recipe, uniform_rank32
    python3 second_pair_stage2.py assemble \
        --workdir ~/fc-v04-sweep2/stage2 --check1 /tmp/second_pair_check1.json \
        --stage1 ~/fc-v04-sweep2/stage1.json \
        --reference ~/qwen-test/smollm2_360_signet_results.json \
        --out ~/fc-v04-sweep2/second_pair_stage2.json

Phase 2 of the strengthening tests (Vinay, Oct 27): the full Alien
Sweep protocol on a second model pair, HuggingFaceTB/SmolLM2-360M
base / Instruct (Apache 2.0), already on Flash from the pre-hackathon
Signet work (no download needed). The protocol mirrors Phase 1
exactly (see alien_sweep_check1.py, alien_sweep_stage1.py,
alien_sweep_stage2.py):

- Recipe generation: ONE Baseten call to Muse Spark Open, 5 recipes
  as per-layer rank maps under a fixed budget = the uniform rank-32
  price on THIS model's shapes (generic block-set shapes below,
  priced by factored.storage_bytes). Strict schema validation.
- Stage 1: filter by slicing the precomputed singular values
  (second_pair_precompute.py). Filter only, never a winner.
- Stage 2: every recipe re-priced on the REAL shapes (embed x1 +
  32 blocks), factors built from one exact SVD per matrix
  (quantize_from_svd, validated against factored.quantize_delta),
  and scored end to end on the 24 Signet items with a NumPy SmolLM2
  forward adapted from the pre-hackathon signet_battery.py on Flash
  (same ChatML format, system line, RoPE theta 100000, eps 1e-5).
- The assemble step VALIDATES the adapted forward against the prior
  Signet run's published base / Instruct bucket means
  (~/qwen-test/smollm2_360_signet_results.json) before any factored
  ranking is reported; the diffs are recorded in the output.

Architecture constants are SmolLM2-360M's published config values
(hidden 960, 32 layers, 15 Q heads, 5 KV heads, head_dim 64, inter
2560, vocab 49152, tied embeddings), asserted against the tensor
shapes actually read from the model files.
"""

import argparse
import gc
import importlib.util
import json
import resource
import struct
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for cand in (HERE, ROOT / "src", HERE / "src"):
    if (cand / "factored.py").exists() and str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

import factored  # noqa: E402

# ---------------------------------------------------------------------------
# Model constants (SmolLM2-360M, from its config; asserted at load).
# ---------------------------------------------------------------------------

KEY_TEMPLATES = {
    "embed": "model.embed_tokens.weight",
    "attn.q_proj": "model.layers.{i}.self_attn.q_proj.weight",
    "attn.k_proj": "model.layers.{i}.self_attn.k_proj.weight",
    "attn.v_proj": "model.layers.{i}.self_attn.v_proj.weight",
    "attn.o_proj": "model.layers.{i}.self_attn.o_proj.weight",
    "mlp.gate": "model.layers.{i}.mlp.gate_proj.weight",
    "mlp.up": "model.layers.{i}.mlp.up_proj.weight",
    "mlp.down": "model.layers.{i}.mlp.down_proj.weight",
}
BLOCK_NAMES = [n for n in KEY_TEMPLATES if n != "embed"]

# Per-layer-type shapes (rows, cols) read from the model files.
SHAPES = {
    "embed": (49152, 960),
    "attn.q_proj": (960, 960),
    "attn.k_proj": (320, 960),
    "attn.v_proj": (320, 960),
    "attn.o_proj": (960, 960),
    "mlp.gate": (2560, 960),
    "mlp.up": (2560, 960),
    "mlp.down": (960, 2560),
}
COUNTS = {name: (1 if name == "embed" else 32) for name in SHAPES}

VOCAB = 49152
HIDDEN = 960
LAYERS = 32
HEADS = 15
KV_HEADS = 5
HEAD_DIM = 64
EPS = 1e-5
ROPE_THETA = 100000.0

SYSTEM_DEFAULT = "You are a helpful assistant."
BUCKET_LABELS = {"math": "math", "knowledge": "knowledge", "instruct": "instruction"}


def matrix_keys():
    """Yield (store_key, hf_key, layer_name) for all 225 recipe matrices."""
    yield "embed", KEY_TEMPLATES["embed"], "embed"
    for i in range(LAYERS):
        for name in BLOCK_NAMES:
            yield f"b{i:02d}_{name.replace('.', '_')}", KEY_TEMPLATES[name].format(i=i), name


def load_header(path):
    with open(path, "rb") as f:
        (hlen,) = struct.unpack("<Q", f.read(8))
        header = json.loads(f.read(hlen))
    return header, 8 + hlen


def read_tensor_fp32(path, header, data_start, key):
    """Read one BF16 tensor from a safetensors file as an fp32 array."""
    info = header[key]
    assert info["dtype"] == "BF16", f"{key}: unexpected dtype {info['dtype']}"
    lo, hi = info["data_offsets"]
    with open(path, "rb") as f:
        f.seek(data_start + lo)
        raw = f.read(hi - lo)
    u16 = np.frombuffer(raw, dtype=np.uint16)
    fp32 = (u16.astype(np.uint32) << 16).view(np.float32)
    return fp32.reshape(info["shape"]).copy()


def load_all_fp32(path):
    header, off = load_header(path)
    return {
        k: read_tensor_fp32(path, header, off, k)
        for k in header
        if k != "__metadata__"
    }


def peak_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


def price_generic(ranks):
    return sum(factored.storage_bytes(int(ranks[name]), SHAPES[name]) for name in SHAPES)


def price_real(ranks):
    return sum(COUNTS[name] * factored.storage_bytes(int(ranks[name]), SHAPES[name])
               for name in SHAPES)


# ---------------------------------------------------------------------------
# Subcommand: recipes (Baseten Spark Open, run on the Muse VM).
# Mirrors alien_sweep_check1.py: helper imported as a module because
# its CLI truncates printed output at 6000 chars.
# ---------------------------------------------------------------------------

BASETEN_MODEL = "meta-models/muse-spark-open-1026"
BASETEN_PROVIDER = "baseten"
BASETEN_MAX_TOKENS = 16000
HUMAN_RANK = 32
BUDGET_BYTES = price_generic({name: HUMAN_RANK for name in SHAPES})


def build_recipe_prompt():
    table = "\n".join(
        f"  {name}: delta matrix {m} x {n}, rank may be 0..{min(m, n)}"
        for name, (m, n) in SHAPES.items()
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


def _load_baseten_helper():
    helper = Path.home() / "workspace/custom-connectors/custom.baseten/bin/baseten_api.py"
    spec = importlib.util.spec_from_file_location("baseten_api", helper)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def log_usage(usage, purpose, when):
    entry = {
        "provider": BASETEN_PROVIDER,
        "model": BASETEN_MODEL,
        "time": when,
        "purpose": purpose,
        "prompt_tokens": (usage or {}).get("prompt_tokens"),
        "completion_tokens": (usage or {}).get("completion_tokens"),
        "total_tokens": (usage or {}).get("total_tokens"),
    }
    log = ROOT / "results" / "api_usage_log.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
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
    if keys != set(SHAPES):
        missing = sorted(set(SHAPES) - keys)
        extra = sorted(keys - set(SHAPES))
        if missing:
            errors.append(f"missing layers: {missing}")
        if extra:
            errors.append(f"unknown layers: {extra}")
    for layer, rank in ranks.items():
        if layer not in SHAPES:
            continue
        if type(rank) is not int:
            errors.append(f"{layer}: rank {rank!r} is not an integer")
        elif rank < 0:
            errors.append(f"{layer}: rank {rank} is negative")
        elif rank > min(SHAPES[layer]):
            errors.append(f"{layer}: rank {rank} exceeds max {min(SHAPES[layer])}")
    total = None
    if not errors:
        total = price_generic(ranks)
        if total > BUDGET_BYTES:
            errors.append(f"total {total} bytes exceeds budget {BUDGET_BYTES}")
    return {"index": idx, "name": name, "valid": not errors,
            "errors": errors, "total_bytes": total}


def cmd_recipes(args):
    helper = _load_baseten_helper()
    prompt = build_recipe_prompt()
    attempts = []
    parsed = None
    content = None
    total_elapsed = 0.0
    for attempt in (1, 2):  # one retry only if the reply cannot be parsed at all
        when = datetime.now(timezone.utc).isoformat()
        payload = {"model": BASETEN_MODEL,
                   "messages": [{"role": "user", "content": prompt}],
                   "max_tokens": BASETEN_MAX_TOKENS}
        started = time.time()
        resp = helper.call("POST", "/v1/chat/completions", payload)
        elapsed = time.time() - started
        total_elapsed += elapsed
        if "http_error" in resp:
            raise RuntimeError(f"baseten HTTP {resp['http_error']}: {resp.get('body', '')[:500]}")
        usage = resp.get("usage", {})
        log_usage(usage, "second_pair_recipe_generation", when)
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
    go = parsed is not None and len(recipes) == 5 and valid_count == 5

    out = {
        "check": "second_pair_spark_recipes_schema_valid",
        "pair": "smollm2-360m",
        "provider": BASETEN_PROVIDER,
        "model": BASETEN_MODEL,
        "layers": {k: list(v) for k, v in SHAPES.items()},
        "budget_bytes": BUDGET_BYTES,
        "budget_basis": "uniform rank 32 on every layer of the SmolLM2 block set, priced by factored.storage_bytes",
        "prompt": prompt,
        "attempts": attempts,
        "elapsed_s_total": round(total_elapsed, 2),
        "raw_content": content,
        "recipes": recipes,
        "validation": validation,
        "valid_count": valid_count,
        "recipes_returned": len(recipes),
        "verdict": "GO" if go else "NO-GO",
    }
    out_path = ROOT / "results" / "second_pair_check1.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, indent=2) + "\n")
    print(f"budget: {BUDGET_BYTES:,} bytes (uniform rank {HUMAN_RANK})")
    print(f"recipes returned: {len(recipes)}, schema-valid: {valid_count}")
    for v in validation:
        status = "valid" if v["valid"] else "INVALID: " + "; ".join(v["errors"])
        size = f"{v['total_bytes']:,} B" if v["total_bytes"] is not None else "n/a"
        print(f"  [{v['index']}] {v['name']}: {status} (total {size})")
    print(f"verdict: {out['verdict']}")
    print(f"wrote {out_path}")


# ---------------------------------------------------------------------------
# Subcommand: stage1 (slicing filter over the precompute).
# ---------------------------------------------------------------------------

def cmd_stage1(args):
    data = np.load(args.npz)
    check1 = json.loads(Path(args.recipes).read_text())
    recipes = [(r["name"], r["ranks"]) for r in check1["recipes"]]
    human = {name: HUMAN_RANK for name in SHAPES}

    def score_recipe(ranks):
        err_sq = 0.0
        tot_sq = 0.0
        clamped = []
        for store_key, _hf, name in matrix_keys():
            s = data[f"{store_key}_s"]
            fro = float(data[f"{store_key}_fro"][0])
            r = int(ranks[name])
            if r > len(s):
                clamped.append({"matrix": store_key, "rank": r, "stored": int(len(s))})
                r = len(s)
            kept = float(np.dot(s[:r], s[:r])) if r else 0.0
            err_sq += max(fro - kept, 0.0)
            tot_sq += fro
        return (float(np.sqrt(err_sq / tot_sq)) if tot_sq else 0.0), clamped

    t0 = time.perf_counter()
    scored = []
    all_clamped = {}
    for name, ranks in recipes:
        sc, cl = score_recipe(ranks)
        scored.append((name, sc))
        if cl:
            all_clamped[name] = cl
    human_score, _ = score_recipe(human)
    elapsed = time.perf_counter() - t0

    ranking = sorted(
        ({"name": name, "relative_frobenius_error": round(score, 6)} for name, score in scored),
        key=lambda d: d["relative_frobenius_error"],
    )
    result = {
        "check": "second_pair_stage1_slicing",
        "n_recipes_scored": len(recipes),
        "scoring_s": round(elapsed, 4),
        "budget": "minutes",
        "verdict": "PASS" if elapsed < 60 else "FAIL",
        "ranking": ranking,
        "human_uniform_rank32": round(human_score, 6),
        "winner_filter_only": ranking[0]["name"] if ranking else None,
        "rank_clamping": all_clamped,
    }
    print(json.dumps(result, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2) + "\n")


# ---------------------------------------------------------------------------
# Factored construction (same as Stage 2 on the Qwen pair).
# ---------------------------------------------------------------------------

def quantize_from_svd(delta_f64, svd, rank):
    A, s, _Bt = svd
    A_r, s_r = A[:, :rank], s[:rank]
    root = np.sqrt(s_r)
    U_svd = A_r * root
    signs = np.where(U_svd >= 0, 1.0, -1.0)
    row_scales_u = np.mean(np.abs(U_svd), axis=1)
    U = signs * row_scales_u[:, None]
    V = (np.linalg.pinv(U) @ delta_f64).T
    return U, V


def all_rank_maps(recipes):
    maps = {r["name"]: {k: int(v) for k, v in r["ranks"].items()} for r in recipes}
    maps["uniform_rank32"] = {name: HUMAN_RANK for name in SHAPES}
    return maps


def cmd_build(args):
    recipes = json.loads(Path(args.recipes).read_text())["recipes"]
    maps = all_rank_maps(recipes)
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    base_hdr, base_off = load_header(args.base)
    ins_hdr, ins_off = load_header(args.instruct)

    graft_check = {}
    for key in ("model.embed_tokens.weight",
                "model.layers.12.mlp.gate_proj.weight",
                "model.layers.31.self_attn.o_proj.weight"):
        Wb = read_tensor_fp32(args.base, base_hdr, base_off, key)
        Wi = read_tensor_fp32(args.instruct, ins_hdr, ins_off, key)
        graft_check[key] = float(np.abs((Wb + (Wi - Wb)) - Wi).max())
        del Wb, Wi

    pricing = {name: {"real_shape_bytes": 0, "generic_shape_bytes": 0} for name in maps}
    full_fp16 = 0
    factors = {name: {} for name in maps}
    validation = []
    t_all = time.perf_counter()

    for store_key, hf_key, name in matrix_keys():
        Wb = read_tensor_fp32(args.base, base_hdr, base_off, hf_key)
        Wi = read_tensor_fp32(args.instruct, ins_hdr, ins_off, hf_key)
        D32 = Wi - Wb
        shape = D32.shape
        del Wb, Wi
        assert tuple(shape) == SHAPES[name], f"{hf_key}: shape {shape} != {SHAPES[name]}"
        full_fp16 += 2 * D32.size

        for map_name, ranks in maps.items():
            r = ranks[name]
            pricing[map_name]["real_shape_bytes"] += factored.storage_bytes(r, shape)
            pricing[map_name]["generic_shape_bytes"] += factored.storage_bytes(
                r, SHAPES[name])
        if all(ranks[name] == 0 for ranks in maps.values()):
            del D32
            continue

        D = D32.astype(np.float64)
        del D32
        svd = np.linalg.svd(D, full_matrices=False)
        distinct = sorted({ranks[name] for ranks in maps.values() if ranks[name] > 0})
        built = {}
        for r in distinct:
            U, V = quantize_from_svd(D, svd, r)
            built[r] = (U.astype(np.float32), V.astype(np.float32))
            if len(validation) < 6 and name != "embed":
                q = factored.quantize_delta(D, r)
                validation.append({
                    "matrix": hf_key, "rank": r,
                    "max_abs_diff_U": float(np.abs(q["U"] - U).max()),
                    "max_abs_diff_V": float(np.abs(q["V"] - V).max()),
                })
                del q
            del U, V
        del D, svd
        for map_name, ranks in maps.items():
            r = ranks[name]
            if r > 0:
                factors[map_name][store_key] = built[r]
        del built
        print(f"built {store_key} shape={list(shape)}", file=sys.stderr)

    for map_name, fac in factors.items():
        flat = {}
        for store_key, (U, V) in fac.items():
            flat[f"{store_key}_U"] = U
            flat[f"{store_key}_V"] = V
        np.savez(workdir / f"factors_{map_name}.npz", **flat)

    summary = {
        "phase": "build",
        "rank_maps": maps,
        "pricing": pricing,
        "full_delta_fp16_bytes": int(full_fp16),
        "graft_check_max_abs_diff": graft_check,
        "quantize_from_svd_validation": validation,
        "wall_s": round(time.perf_counter() - t_all, 2),
        "peak_rss_mb": round(peak_rss_mb(), 1),
    }
    (workdir / "build_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


# ---------------------------------------------------------------------------
# NumPy SmolLM2 forward, adapted from the pre-hackathon signet_battery.py
# on Flash (same operations, same ChatML format and system line, RoPE
# theta 100000, RMSNorm eps 1e-5, tied head). Validated in assemble
# against that run's published bucket means.
# ---------------------------------------------------------------------------

def format_chat(prompt):
    return (
        "<|im_start|>system\n" + SYSTEM_DEFAULT + "<|im_end|>\n"
        "<|im_start|>user\n" + prompt + "<|im_end|>\n"
        "<|im_start|>assistant\n"
    )


def rmsnorm(x, w):
    return x / np.sqrt((x ** 2).mean(-1, keepdims=True) + EPS) * w


def rope_tables(T):
    inv = 1.0 / (ROPE_THETA ** (np.arange(0, HEAD_DIM, 2, dtype=np.float32) / HEAD_DIM))
    f = np.outer(np.arange(T, dtype=np.float32), inv)
    e = np.concatenate([f, f], axis=-1)
    return np.cos(e).astype(np.float32), np.sin(e).astype(np.float32)


def apply_rope(x, cos, sin):
    x1, x2 = x[..., : HEAD_DIM // 2], x[..., HEAD_DIM // 2:]
    xr = np.concatenate([-x2, x1], axis=-1)
    return x * cos[:, None, :] + xr * sin[:, None, :]


def softmax(x):
    x = x - x.max(-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(-1, keepdims=True)


def silu(x):
    return x / (1.0 + np.exp(-x))


def linear(x, sd, key):
    y = x @ sd[key].T
    bkey = key.replace(".weight", ".bias")
    if bkey in sd:
        y = y + sd[bkey]
    return y


def forward(ids, sd):
    T = len(ids)
    cos, sin = rope_tables(T)
    x = sd["model.embed_tokens.weight"][np.array(ids, dtype=np.int64)]
    for i in range(LAYERS):
        p = f"model.layers.{i}"
        h = rmsnorm(x, sd[f"{p}.input_layernorm.weight"])
        q = linear(h, sd, f"{p}.self_attn.q_proj.weight").reshape(T, HEADS, HEAD_DIM)
        k = linear(h, sd, f"{p}.self_attn.k_proj.weight").reshape(T, KV_HEADS, HEAD_DIM)
        v = linear(h, sd, f"{p}.self_attn.v_proj.weight").reshape(T, KV_HEADS, HEAD_DIM)
        q, k = apply_rope(q, cos, sin), apply_rope(k, cos, sin)
        k = np.repeat(k, HEADS // KV_HEADS, axis=1)
        v = np.repeat(v, HEADS // KV_HEADS, axis=1)
        att = np.einsum("thd,shd->hts", q, k) / np.sqrt(HEAD_DIM)
        mask = np.triu(np.ones((T, T), dtype=bool), 1)
        att[:, mask] = -1e9
        att = softmax(att)
        o = np.einsum("hts,shd->thd", att, v).reshape(T, HEADS * HEAD_DIM)
        x = x + linear(o, sd, f"{p}.self_attn.o_proj.weight")
        h2 = rmsnorm(x, sd[f"{p}.post_attention_layernorm.weight"])
        gate = silu(linear(h2, sd, f"{p}.mlp.gate_proj.weight"))
        up = linear(h2, sd, f"{p}.mlp.up_proj.weight")
        x = x + linear(gate * up, sd, f"{p}.mlp.down_proj.weight")
    x = rmsnorm(x, sd["model.norm.weight"])
    return x @ sd["model.embed_tokens.weight"].T  # tied head


def score_items(tok, sd, items):
    """Per-item: summed answer logprob (Signet metric) + first-token argmax hit."""
    rows = []
    for bucket, prompt, answer in items:
        ids_p = tok.encode(format_chat(prompt)).ids
        ids_f = tok.encode(format_chat(prompt) + answer).ids
        if len(ids_f) > len(ids_p) and ids_f[: len(ids_p)] == ids_p:
            ids_a = ids_f[len(ids_p):]
        else:
            ids_a = tok.encode(answer).ids
        if not ids_a:
            continue
        logits = forward(ids_p + ids_a, sd)
        off = len(ids_p)
        lp = 0.0
        for j, tok_id in enumerate(ids_a):
            row = logits[off + j - 1].astype(np.float64)
            row = row - row.max()
            e = np.exp(row)
            lp += float(np.log(e[tok_id] / e.sum()))
        first_hit = int(np.argmax(logits[off - 1]) == ids_a[0])
        rows.append({"bucket": BUCKET_LABELS[bucket], "logprob": lp,
                     "first_token_correct": first_hit})
    return rows


def aggregate(rows):
    def agg(rs):
        n = len(rs)
        return {
            "n": n,
            "accuracy": sum(r["first_token_correct"] for r in rs) / n if n else 0.0,
            "mean_target_logprob": sum(r["logprob"] for r in rs) / n if n else 0.0,
        }
    per_bucket = {}
    for b in ("knowledge", "instruction", "math"):
        per_bucket[b] = agg([r for r in rows if r["bucket"] == b])
    return {"overall": agg(rows), "per_bucket": per_bucket}


def cmd_eval(args):
    from tokenizers import Tokenizer

    workdir = Path(args.workdir)
    tok = Tokenizer.from_file(str(Path(args.data) / args.tokenizer))
    sys.path.insert(0, str(Path(args.qwen_test)))
    from signet_battery import ITEMS  # pre-existing probe data, imported not copied

    t0 = time.perf_counter()
    if args.config == "full_delta":
        sd = load_all_fp32(args.instruct)
        applied = "Instruct weights (== base + full delta on every tensor)"
    else:
        sd = load_all_fp32(args.base)
        if args.config == "base":
            applied = "base weights, no delta"
        else:
            fac = np.load(workdir / f"factors_{args.config}.npz")
            key_of = {sk: hk for sk, hk, _ in matrix_keys()}
            for store_key, hf_key in key_of.items():
                ukey = f"{store_key}_U"
                if ukey not in fac:
                    continue  # rank 0: delta dropped, matrix keeps base value
                U, V = fac[ukey], fac[f"{store_key}_V"]
                sd[hf_key] = sd[hf_key] + (U @ V.T)
            applied = (f"base + factored delta ({args.config}) on the 225 recipe "
                       "matrices; all other tensors at base values")
    load_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    rows = score_items(tok, sd, ITEMS)
    eval_s = time.perf_counter() - t1
    del sd
    gc.collect()

    out = {
        "config": args.config,
        "applied": applied,
        "n_items": len(rows),
        "scores": aggregate(rows),
        "per_item": rows,
        "load_wall_s": round(load_s, 2),
        "eval_wall_s": round(eval_s, 2),
        "wall_s": round(time.perf_counter() - t0, 2),
        "peak_rss_mb": round(peak_rss_mb(), 1),
    }
    (workdir / f"eval_{args.config}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("config", "n_items", "wall_s", "peak_rss_mb")}, indent=2))
    print(json.dumps(out["scores"], indent=2))


# ---------------------------------------------------------------------------
# Assemble the deliverable (validates the forward first).
# ---------------------------------------------------------------------------

def cmd_assemble(args):
    workdir = Path(args.workdir)
    build = json.loads((workdir / "build_summary.json").read_text())
    check1 = json.loads(Path(args.check1).read_text())
    stage1 = json.loads(Path(args.stage1).read_text())
    reference = json.loads(Path(args.reference).read_text())["part_a_summary"]
    recipe_names = [r["name"] for r in check1["recipes"]]

    evals = {}
    for name in ["base", "full_delta"] + recipe_names + ["uniform_rank32"]:
        evals[name] = json.loads((workdir / f"eval_{name}.json").read_text())

    def cfg_block(ev):
        return {"overall": ev["scores"]["overall"], "per_bucket": ev["scores"]["per_bucket"]}

    base_scores = evals["base"]["scores"]
    full_scores = evals["full_delta"]["scores"]

    # Validate this stage's forward pass against the prior Signet run.
    forward_validation = {}
    for src_bucket, ref in reference.items():
        b = BUCKET_LABELS[src_bucket]
        mine_base = base_scores["per_bucket"][b]["mean_target_logprob"]
        mine_full = full_scores["per_bucket"][b]["mean_target_logprob"]
        forward_validation[b] = {
            "base_mine": mine_base, "base_reference": ref["base"],
            "base_abs_diff": abs(mine_base - ref["base"]),
            "full_mine": mine_full, "full_reference": ref["instruct"],
            "full_abs_diff": abs(mine_full - ref["instruct"]),
        }
    max_fwd_diff = max(max(v["base_abs_diff"], v["full_abs_diff"])
                       for v in forward_validation.values())

    def gap_closed(factored_scores):
        out = {}
        for b in ("knowledge", "instruction", "math"):
            gap = (full_scores["per_bucket"][b]["mean_target_logprob"]
                   - base_scores["per_bucket"][b]["mean_target_logprob"])
            out[b] = ((factored_scores["per_bucket"][b]["mean_target_logprob"]
                       - base_scores["per_bucket"][b]["mean_target_logprob"]) / gap
                      if gap > 1e-9 else None)
        gap_all = (full_scores["overall"]["mean_target_logprob"]
                    - base_scores["overall"]["mean_target_logprob"])
        out["overall"] = ((factored_scores["overall"]["mean_target_logprob"]
                           - base_scores["overall"]["mean_target_logprob"]) / gap_all
                          if gap_all > 1e-9 else None)
        return out

    def entry(name, kind):
        ev = evals[name]
        ranks = build["rank_maps"][name]
        return {
            "name": name,
            "kind": kind,
            "ranks": ranks,
            "rank0_layer_names": [n for n, r in ranks.items() if r == 0],
            "real_shape_bytes": build["pricing"][name]["real_shape_bytes"],
            "generic_shape_bytes": build["pricing"][name]["generic_shape_bytes"],
            "configs": {
                "base": cfg_block(evals["base"]),
                "full_delta": cfg_block(evals["full_delta"]),
                "factored_delta": cfg_block(ev),
            },
            "gap_closed": gap_closed(ev["scores"]),
            "wall_s": ev["wall_s"],
            "eval_wall_s": ev["eval_wall_s"],
            "peak_rss_mb": ev["peak_rss_mb"],
        }

    recipes = [entry(n, "spark_recipe") for n in recipe_names]
    human = entry("uniform_rank32", "human_baseline")

    ranked = sorted(
        recipes + [human],
        key=lambda e: e["configs"]["factored_delta"]["overall"]["mean_target_logprob"],
        reverse=True,
    )
    ranking = [
        {
            "position": i + 1,
            "name": e["name"],
            "kind": e["kind"],
            "factored_mean_target_logprob": e["configs"]["factored_delta"]["overall"]["mean_target_logprob"],
            "factored_accuracy": e["configs"]["factored_delta"]["overall"]["accuracy"],
            "overall_gap_closed": e["gap_closed"]["overall"],
            "real_shape_bytes": e["real_shape_bytes"],
        }
        for i, e in enumerate(ranked)
    ]
    winner = ranking[0]

    result = {
        "stage": "second_pair_stage2_real_model_task_benchmark",
        "date": "2026-10-27",
        "machine": "Flash (Vinay's Ubuntu box, ssh flash, 12 threads, qwen-test venv: python 3.14 + numpy 2.5.4 + tokenizers 0.23.3)",
        "model_pair": {
            "base": "~/qwen-test/data/smollm2-360m.safetensors (HuggingFaceTB/SmolLM2-360M, BF16, Apache 2.0)",
            "instruct": "~/qwen-test/data/smollm2-360m-instruct.safetensors (HuggingFaceTB/SmolLM2-360M-Instruct, BF16, Apache 2.0)",
            "local_note": "pair already present on Flash from the pre-hackathon Signet work; no download was needed",
            "matrices": "embedding + 32 blocks x (attn.q/k/v/o_proj, mlp.gate/up/down_proj) = 225 delta matrices",
        },
        "probe_set": {
            "source": "Signet probe items (ITEMS) imported at run time from ~/qwen-test/signet_battery.py on Flash",
            "label": "pre-existing evaluation data: 24 hand-written probe items from the prior Fraction Compressor work (v0.1-v0.3 / Signet), not created during this event",
            "n_items": 24,
            "buckets": {"knowledge": 8, "instruction": 8, "math": 8},
        },
        "method": {
            "configs_per_recipe": "base (no delta), full_delta (Instruct weights == base + full delta on every tensor), factored_delta (base + factored delta per the recipe's rank map)",
            "factored_application": "rank map applies per layer type across all 32 blocks plus the embedding (225 matrices); factors built with factored.quantize_delta's construction via one exact SVD per matrix sliced per rank (validated against quantize_delta itself, see build_validation); rank 0 drops the matrix's delta; RMSNorm weights (no biases exist in this architecture) stay at base values in factored configs",
            "scoring": "chat-formatted prompt (ChatML, system line 'You are a helpful assistant.', as in the prior Signet battery); target logprob = summed log-probability of the answer tokens (Signet convention); accuracy = first-token accuracy; gap_closed = (factored - base) / (full - base) on mean target logprob",
            "forward_pass": "NumPy SmolLM2 forward adapted from the pre-hackathon signet_battery.py (RoPE theta 100000, RMSNorm eps 1e-5, GQA 15 Q / 5 KV heads, tied embeddings); validated against the prior Signet run's published bucket means (see forward_validation)",
            "stage1_role": "filter only: no winner is declared from Stage 1 matrix error; the ranking below is by Stage 2 task score",
            "repricing": "every recipe re-priced on real shapes with factored.storage_bytes before comparison; generic block-set totals from the recipe generation reported alongside",
            "recipe_generation": {
                "provider": "baseten", "model": BASETEN_MODEL,
                "budget_bytes_generic": BUDGET_BYTES,
                "recipes_file": "results/second_pair_check1.json",
                "stage1_file": "~/fc-v04-sweep2/stage1.json (Flash workdir)",
                "stage1_ranking": stage1["ranking"],
                "stage1_human_uniform_rank32": stage1["human_uniform_rank32"],
            },
        },
        "build_validation": {
            "graft_check_max_abs_diff": build["graft_check_max_abs_diff"],
            "quantize_from_svd_vs_quantize_delta": build["quantize_from_svd_validation"],
            "build_wall_s": build["wall_s"],
            "build_peak_rss_mb": build["peak_rss_mb"],
        },
        "forward_validation": forward_validation,
        "forward_validation_max_abs_diff": max_fwd_diff,
        "full_delta_fp16_bytes_real_shapes": build["full_delta_fp16_bytes"],
        "shared_configs": {
            "base": cfg_block(evals["base"]),
            "full_delta": cfg_block(evals["full_delta"]),
            "base_wall_s": evals["base"]["wall_s"],
            "full_delta_wall_s": evals["full_delta"]["wall_s"],
        },
        "recipes": recipes,
        "human_baseline": human,
        "ranking_by_task_score": ranking,
        "winner": {
            "name": winner["name"],
            "kind": winner["kind"],
            "note": ("the human uniform recipe won Stage 2; reported as-is per the "
                     "honest outcome rule" if winner["kind"] == "human_baseline" else
                     "top recipe by Stage 2 task score; byte-fairness is judged on "
                     "real_shape_bytes vs the uniform recipe and the byte-matched "
                     "confirmation runs in second_pair_heldout96"),
        },
        "api_calls": "recipe generation only (Baseten, logged in results/api_usage_log.jsonl); the rest is compute",
        "scripts": ["examples/second_pair_precompute.py", "examples/second_pair_stage2.py"],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {out}")
    print(json.dumps(ranking, indent=2))
    print(json.dumps(forward_validation, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("recipes")
    r.set_defaults(fn=cmd_recipes)

    s1 = sub.add_parser("stage1")
    s1.add_argument("--npz", required=True)
    s1.add_argument("--recipes", required=True)
    s1.add_argument("--out", default=None)
    s1.set_defaults(fn=cmd_stage1)

    b = sub.add_parser("build")
    b.add_argument("--base", required=True)
    b.add_argument("--instruct", required=True)
    b.add_argument("--recipes", required=True)
    b.add_argument("--workdir", required=True)
    b.set_defaults(fn=cmd_build)

    e = sub.add_parser("eval")
    e.add_argument("--config", required=True)
    e.add_argument("--base", required=True)
    e.add_argument("--instruct", required=True)
    e.add_argument("--data", default=str(Path.home() / "qwen-test" / "data"))
    e.add_argument("--tokenizer", default="smollm2-360m-tokenizer.json")
    e.add_argument("--qwen-test", default=str(Path.home() / "qwen-test"))
    e.add_argument("--workdir", required=True)
    e.set_defaults(fn=cmd_eval)

    a = sub.add_parser("assemble")
    a.add_argument("--workdir", required=True)
    a.add_argument("--check1", required=True)
    a.add_argument("--stage1", required=True)
    a.add_argument("--reference", required=True)
    a.add_argument("--out", required=True)
    a.set_defaults(fn=cmd_assemble)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
