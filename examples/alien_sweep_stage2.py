"""Alien Sweep Stage 2: real-model task benchmark for all sweep recipes.

    # on Flash, with the qwen-test venv (numpy + tokenizers):
    python3 examples/alien_sweep_stage2.py build \
        --base ~/qwen-test/data/qwen2.5-0.5b.safetensors \
        --instruct ~/qwen-test/data/qwen2.5-0.5b-instruct.safetensors \
        --recipes results/alien_sweep_check1.json \
        --workdir ~/fc-v04-sweep/stage2
    python3 examples/alien_sweep_stage2.py eval --config base \
        --base ... --instruct ... --workdir ~/fc-v04-sweep/stage2
    python3 examples/alien_sweep_stage2.py eval --config embed_guardian ...
    python3 examples/alien_sweep_stage2.py assemble \
        --workdir ~/fc-v04-sweep/stage2 --check1 results/alien_sweep_check1.json \
        --reference ~/qwen-test/qwen_signet_results.json \
        --out results/alien_sweep_stage2.json

Stage 2 of the Alien Sweep protocol in BUILD_PLAN.md: the recipes that
passed the Stage 1 filter run the end-to-end task benchmark against the
real model pair (Qwen2.5-0.5B base / Instruct). Per the plan, Stage 1 is
only a filter: no winner is declared from matrix error. Stage 2 task
scores decide, and the human uniform rank-32 recipe runs alongside as
the baseline every alien recipe has to beat.

Two design inputs from the Day-2 Gemini cross-validation
(results/gemini_validation_day2.md) are mandatory here:

1. Every recipe is re-priced on the REAL model shapes before any
   comparison. The check-1 budget was priced on generic single-block
   shapes; the real model has an embedding plus 24 blocks whose shapes
   differ, so the generic totals do not carry over. Both pricings are
   reported. Real-shape pricing uses factored.storage_bytes per matrix,
   exactly the check-1 convention (a rank-0 layer still prices its
   per-row scale term, 4 * rows, as in check 1).
2. Stage 1's ranking is treated as a filter only. The ranking published
   here is by Stage 2 task score.

What is applied, exactly:
- Rank maps name 8 layer types (embed, attn.q/k/v/o_proj, mlp.gate/up/
  down). A recipe's rank for a layer type applies to that matrix in
  every one of the 24 blocks (embed: the single embedding matrix).
  169 matrices in total.
- The factored config for a recipe is base weights + factored delta on
  those 169 matrices only, factors from factored.quantize_delta's
  construction (truncated SVD, U forced onto its sign pattern with
  per-row scales, V refit by least squares). Rank 0 means the matrix's
  delta is dropped entirely (the matrix keeps its base value).
- All other tensors (RMSNorm weights, attention biases; 121 tensors)
  keep their BASE values in the factored configs. Nothing outside the
  169 recipe matrices is grafted in.
- The full-delta config is the Instruct weights themselves; the prior
  Signet run verified base + full delta == Instruct to float precision
  (build re-verifies this on sample tensors), so it is the same config.
- Scoring mirrors src/bench.py's metric definitions (argmax accuracy,
  mean target logprob, per-bucket breakdown, gap closed) with the
  Signet convention for logprob: the summed log-probability of the
  probe's answer tokens under the chat-formatted prompt. Accuracy here
  is first-token accuracy: the fraction of items whose first answer
  token is the model's argmax next token. Probes are the 24
  hand-written Signet items (8 knowledge, 8 instruction, 8 math),
  imported at run time from the prior work's data file on Flash and
  labeled in the output as pre-existing evaluation data.
- The forward pass is a fresh NumPy implementation of the Qwen2.5
  architecture (config.json: 24 layers, hidden 896, 14 Q heads, 2 KV
  heads, head_dim 64, inter 4864, tied embeddings), written for this
  stage. The assemble step validates it against the prior Signet run's
  published base / Instruct bucket means.

Memory discipline (Flash lesson): build computes one matrix at a time
streamed from the safetensors byte ranges; eval runs one config per
process invocation and holds one fp32 weight dict (~2 GB). Two extra
ablation configs isolate the rank-0 question Gemini flagged: the
Stage 1 filter's top recipe with k_proj also dropped, and
sparse_extremes with its embedding delta restored at rank 80.
"""

import argparse
import gc
import json
import resource
import struct
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
for cand in (HERE, HERE.parent / "src", HERE / "src"):
    if (cand / "factored.py").exists() and str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

import factored  # noqa: E402

# Recipe layer name -> safetensors key template ({i} = block index).
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
N_BLOCKS = 24

# Qwen2.5-0.5B architecture (data/config.json).
VOCAB = 151936
HIDDEN = 896
LAYERS = 24
HEADS = 14
KV_HEADS = 2
HEAD_DIM = HIDDEN // HEADS  # 64
EPS = 1e-6
ROPE_THETA = 1000000.0

SYSTEM_DEFAULT = "You are Qwen, created by Alibaba Cloud. You are a helpful assistant."
BUCKET_LABELS = {"math": "math", "knowledge": "knowledge", "instruct": "instruction"}


def matrix_keys():
    """Yield (store_key, hf_key, layer_name) for all 169 recipe matrices."""
    yield "embed", KEY_TEMPLATES["embed"], "embed"
    for i in range(N_BLOCKS):
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


# ---------------------------------------------------------------------------
# Rank maps: the 5 Spark recipes + human uniform + 2 rank-0 ablations.
# ---------------------------------------------------------------------------

def all_rank_maps(recipes):
    maps = {r["name"]: {k: int(v) for k, v in r["ranks"].items()} for r in recipes}
    maps["uniform_rank32"] = {name: 32 for name in KEY_TEMPLATES}
    top = maps["embed_guardian"]
    maps["ablation_k0_embed_guardian"] = {**top, "attn.k_proj": 0}
    se = maps["sparse_extremes"]
    maps["ablation_embed80_sparse_extremes"] = {**se, "embed": 80}
    return maps


RECIPE_NAMES = ["embed_guardian", "attn_output_focus", "mlp_behemoth",
                "sparse_extremes", "balanced_uneven", "uniform_rank32"]
ABLATION_NAMES = ["ablation_k0_embed_guardian", "ablation_embed80_sparse_extremes"]


# ---------------------------------------------------------------------------
# Factored construction. quantize_from_svd replicates factored.quantize_delta
# step for step, but takes a precomputed full SVD of the delta so each matrix
# is decomposed once for all rank maps instead of once per (matrix, rank).
# The build validates the two against each other on sample matrices.
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


def cmd_build(args):
    recipes = json.loads(Path(args.recipes).read_text())["recipes"]
    generic_shapes = json.loads(Path(args.recipes).read_text())["layers"]
    maps = all_rank_maps(recipes)
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    base_hdr, base_off = load_header(args.base)
    ins_hdr, ins_off = load_header(args.instruct)

    # Re-verify the full-delta == Instruct equivalence on sample tensors.
    graft_check = {}
    for key in ("model.embed_tokens.weight",
                "model.layers.12.mlp.gate_proj.weight",
                "model.layers.23.self_attn.o_proj.weight"):
        Wb = read_tensor_fp32(args.base, base_hdr, base_off, key)
        Wi = read_tensor_fp32(args.instruct, ins_hdr, ins_off, key)
        graft_check[key] = float(np.abs((Wb + (Wi - Wb)) - Wi).max())
        del Wb, Wi

    pricing = {name: {"real_shape_bytes": 0, "generic_shape_bytes": 0} for name in maps}
    full_fp16 = 0
    factors = {name: {} for name in maps}  # map -> store_key -> (U32, V32)
    validation = []
    t_all = time.perf_counter()

    for store_key, hf_key, name in matrix_keys():
        Wb = read_tensor_fp32(args.base, base_hdr, base_off, hf_key)
        Wi = read_tensor_fp32(args.instruct, ins_hdr, ins_off, hf_key)
        D32 = Wi - Wb
        shape = D32.shape
        del Wb, Wi
        full_fp16 += 2 * D32.size

        for map_name, ranks in maps.items():
            r = ranks[name]
            pricing[map_name]["real_shape_bytes"] += factored.storage_bytes(r, shape)
            pricing[map_name]["generic_shape_bytes"] += factored.storage_bytes(
                r, tuple(generic_shapes[name]))
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
# Fresh NumPy forward pass for Qwen2.5 (written for this stage from
# data/config.json) + Signet-style probe scoring.
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
        o = np.einsum("hts,shd->thd", att, v).reshape(T, HIDDEN)
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
    tok = Tokenizer.from_file(str(Path(args.data) / "tokenizer.json"))
    sys.path.insert(0, str(Path(args.qwen_test)))
    from qwen_signet import ITEMS  # pre-existing probe data, imported not copied

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
            applied = (f"base + factored delta ({args.config}) on the 169 recipe "
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
# Assemble the deliverable.
# ---------------------------------------------------------------------------

def cmd_assemble(args):
    workdir = Path(args.workdir)
    build = json.loads((workdir / "build_summary.json").read_text())
    check1 = json.loads(Path(args.check1).read_text())
    generic_check1 = {v["name"]: v["total_bytes"] for v in check1["validation"]}
    reference = json.loads(Path(args.reference).read_text())["part_a_summary"]

    evals = {}
    for name in ["base", "full_delta"] + RECIPE_NAMES + ABLATION_NAMES:
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

    generic_layers = check1["layers"]

    def generic_single_block_bytes(ranks):
        # Check-1 convention: one block set (embed + one of each block
        # layer type) at the generic shapes. Reproduces check 1's
        # recorded validation totals exactly for the 5 Spark recipes.
        return sum(
            factored.storage_bytes(r, tuple(generic_layers[layer]))
            for layer, r in ranks.items()
        )

    def entry(name, kind):
        ev = evals[name]
        ranks = build["rank_maps"][name]
        return {
            "name": name,
            "kind": kind,
            "ranks": ranks,
            "rank0_layer_names": [n for n, r in ranks.items() if r == 0],
            "real_shape_bytes": build["pricing"][name]["real_shape_bytes"],
            "generic_shape_bytes": generic_single_block_bytes(ranks),
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

    recipes = [entry(n, "spark_recipe") for n in RECIPE_NAMES[:5]]
    human = entry("uniform_rank32", "human_baseline")
    ablations = [entry(n, "ablation") for n in ABLATION_NAMES]

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

    def lp(ev):
        return ev["scores"]["overall"]["mean_target_logprob"]

    def delta_block(parent_name, ablated_name, change):
        p, a = evals[parent_name], evals[ablated_name]
        return {
            "parent_recipe": parent_name,
            "ablation": ablated_name,
            "change": change,
            "parent_factored_mean_target_logprob": lp(p),
            "ablation_factored_mean_target_logprob": lp(a),
            "delta_mean_target_logprob": lp(a) - lp(p),
            "parent_factored_accuracy": p["scores"]["overall"]["accuracy"],
            "ablation_factored_accuracy": a["scores"]["overall"]["accuracy"],
            "per_bucket_delta_mean_target_logprob": {
                b: a["scores"]["per_bucket"][b]["mean_target_logprob"]
                - p["scores"]["per_bucket"][b]["mean_target_logprob"]
                for b in ("knowledge", "instruction", "math")
            },
        }

    rank0_analysis = {
        "question": "Gemini Day-2 flag: recipes that assign rank 0 to a layer type drop that matrix's delta entirely; does that materially change task outcomes?",
        "k_proj_drop_isolated": delta_block(
            "embed_guardian", "ablation_k0_embed_guardian",
            "attn.k_proj rank 5 -> 0 in all 24 blocks, all other ranks unchanged"),
        "embed_drop_isolated": delta_block(
            "sparse_extremes", "ablation_embed80_sparse_extremes",
            "embed rank 0 -> 80 (delta restored), all other ranks unchanged; "
            "read in reverse: the ablation minus the parent is what restoring "
            "the embedding delta buys, so the parent's rank-0 embed costs the "
            "negative of that delta"),
        "recipes_with_rank0_layers": {
            e["name"]: e["rank0_layer_names"] for e in recipes if e["rank0_layer_names"]
        },
    }

    result = {
        "stage": "alien_sweep_stage2_real_model_task_benchmark",
        "date": "2026-10-27",
        "machine": "Flash (Vinay's Ubuntu box, ssh flash, 12 threads, qwen-test venv: python 3.14 + numpy 2.5.4 + tokenizers 0.23.3)",
        "model_pair": {
            "base": "~/qwen-test/data/qwen2.5-0.5b.safetensors (Qwen2.5-0.5B, BF16)",
            "instruct": "~/qwen-test/data/qwen2.5-0.5b-instruct.safetensors (Qwen2.5-0.5B-Instruct, BF16)",
            "matrices": "embedding + 24 blocks x (attn.q/k/v/o_proj, mlp.gate/up/down_proj) = 169 delta matrices",
        },
        "probe_set": {
            "source": "Signet probe items (ITEMS) imported at run time from ~/qwen-test/qwen_signet.py on Flash",
            "label": "pre-existing evaluation data: 24 hand-written probe items from the prior Fraction Compressor work (v0.1-v0.3 / Signet), not created during this event",
            "n_items": 24,
            "buckets": {"knowledge": 8, "instruction": 8, "math": 8},
            "note": "the source data labels the instruction bucket 'instruct'; renamed here for consistency with src/bench.py",
        },
        "method": {
            "configs_per_recipe": "base (no delta), full_delta (Instruct weights == base + full delta on every tensor), factored_delta (base + factored delta per the recipe's rank map)",
            "factored_application": "rank map applies per layer type across all 24 blocks plus the embedding (169 matrices); factors built with factored.quantize_delta's construction via one exact SVD per matrix sliced per rank (validated against quantize_delta itself, see build_validation); rank 0 drops the matrix's delta; RMSNorm weights and attention biases (121 tensors) stay at base values in factored configs",
            "scoring": "chat-formatted prompt (Qwen default system line); target logprob = summed log-probability of the answer tokens (Signet convention); accuracy = first-token accuracy (first answer token is the argmax next token); gap_closed = (factored - base) / (full - base) on mean target logprob, per src/bench.py's metric definitions",
            "forward_pass": "fresh NumPy Qwen2.5 forward written for this stage from data/config.json; validated against the prior Signet run's published bucket means (see forward_validation)",
            "stage1_role": "filter only (Gemini Day-2 finding 2): no winner is declared from Stage 1 matrix error; the ranking below is by Stage 2 task score",
            "repricing": "every recipe re-priced on real shapes with factored.storage_bytes before comparison (Gemini Day-2 finding 1); generic-shape totals from check 1 reported alongside",
        },
        "build_validation": {
            "graft_check_max_abs_diff": build["graft_check_max_abs_diff"],
            "quantize_from_svd_vs_quantize_delta": build["quantize_from_svd_validation"],
            "build_wall_s": build["wall_s"],
            "build_peak_rss_mb": build["peak_rss_mb"],
        },
        "forward_validation": forward_validation,
        "full_delta_fp16_bytes_real_shapes": build["full_delta_fp16_bytes"],
        "shared_configs": {
            "base": cfg_block(evals["base"]),
            "full_delta": cfg_block(evals["full_delta"]),
            "base_wall_s": evals["base"]["wall_s"],
            "full_delta_wall_s": evals["full_delta"]["wall_s"],
        },
        "recipes": recipes,
        "human_baseline": human,
        "ablations": ablations,
        "rank0_analysis": rank0_analysis,
        "ranking_by_task_score": ranking,
        "api_calls": "none (compute only); results/api_usage_log.jsonl unchanged",
        "scripts": ["examples/alien_sweep_stage2.py"],
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
    e.add_argument("--qwen-test", default=str(Path.home() / "qwen-test"))
    e.add_argument("--workdir", required=True)
    e.set_defaults(fn=cmd_eval)

    a = sub.add_parser("assemble")
    a.add_argument("--workdir", required=True)
    a.add_argument("--check1", required=True)
    a.add_argument("--reference", required=True)
    a.add_argument("--out", required=True)
    a.set_defaults(fn=cmd_assemble)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
