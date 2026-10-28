"""The missing baseline: a plain 1-bit delta at its own price, and our
factored format at that same price (GPT-OSS's judge question, Oct 28).

    # on Flash, with the qwen-test venv, next to alien_sweep_stage2.py:
    python3 bitdelta_baseline.py price \
        --base ~/qwen-test/data/qwen2.5-0.5b.safetensors \
        --workdir ~/fc-v04-sweep/bitdelta
    python3 bitdelta_baseline.py build-factors --rank 108 \
        --base ~/qwen-test/data/qwen2.5-0.5b.safetensors \
        --instruct ~/qwen-test/data/qwen2.5-0.5b-instruct.safetensors \
        --workdir ~/fc-v04-sweep/bitdelta
    python3 bitdelta_baseline.py eval --config bitdelta_init \
        --base ~/qwen-test/data/qwen2.5-0.5b.safetensors \
        --instruct ~/qwen-test/data/qwen2.5-0.5b-instruct.safetensors \
        --probes ~/fc-v04-sweep/heldout96_probes_spark.json \
        --workdir ~/fc-v04-sweep/bitdelta
    python3 bitdelta_baseline.py eval --config factored_rank108 \
        --base ~/qwen-test/data/qwen2.5-0.5b.safetensors \
        --instruct ~/qwen-test/data/qwen2.5-0.5b-instruct.safetensors \
        --probes ~/fc-v04-sweep/heldout96_probes_spark.json \
        --workdir ~/fc-v04-sweep/bitdelta
    # assemble anywhere (small files only):
    python3 bitdelta_baseline.py assemble \
        --workdir ~/fc-v04-sweep/bitdelta \
        --heldout96 results/alien_sweep_heldout96.json \
        --out results/bitdelta_baseline.json

Why this exists: the fresh-eyes review (results/fresh_perspective.md)
asked the judge's first question: why not a plain 1-bit delta at the
same bytes? The honest answer has a wrinkle: a plain 1-bit delta
cannot go below its own floor, 1 bit per weight over the 169 recipe
matrices plus one scale per matrix (about 61.7 MB here). At our
19.4 MB headline budget no plain 1-bit delta exists. So the fair
comparison is a two-budget curve:

- 19.4 MB budget: factored only (uniform rank 32: 2.1% gap closed;
  Spark's mlp_behemoth_lite: 23.2%, both already measured on the
  combined 96 in results/alien_sweep_heldout96.json).
- ~61.7 MB budget: the plain 1-bit delta at its floor price vs the
  factored format at a uniform rank priced just under the same total.

Configs measured here, same combined 96 questions, same scoring
(mean target logprob, Signet convention) and the same NumPy forward
as Stage 2 / the held-out guard (alien_sweep_stage2 as a module):

- bitdelta_init: the published BitDelta initialization, exactly:
  per matrix, delta_hat = sign(delta) * mean(|delta|), one fp32 scale
  per matrix. NO scale distillation, NO training of any kind. This is
  the initialization from Liu et al., arXiv:2402.10193, not the full
  BitDelta method (which then distills the scales on data).
- factored_rank<R>: our factored format (factored.quantize_delta)
  at the largest uniform rank whose factored.storage_bytes total
  over the 169 matrices is <= the plain 1-bit price.
"""

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import alien_sweep_stage2 as s2  # noqa: E402
import factored  # noqa: E402  (alien_sweep_stage2 puts src/ or HERE on sys.path)

SUBSETS = ("heldout24", "heldout72_new")


def matrix_shapes(base_path):
    """(store_key, hf_key, layer_name, shape) for the 169 recipe matrices."""
    header, _ = s2.load_header(base_path)
    out = []
    for store_key, hf_key, name in s2.matrix_keys():
        out.append((store_key, hf_key, name, tuple(header[hf_key]["shape"])))
    return out


def bitdelta_price(shapes):
    """1 bit per weight + one fp32 scale per matrix."""
    bits = sum(m * n for _, _, _, (m, n) in shapes)
    return (bits + 7) // 8 + 4 * len(shapes), bits


def factored_total(rank, shapes):
    return sum(factored.storage_bytes(rank, shape) for _, _, _, shape in shapes)


def best_uniform_rank(price_cap, shapes):
    max_rank = min(min(shape) for _, _, _, shape in shapes)
    r = 1
    while r < max_rank and factored_total(r + 1, shapes) <= price_cap:
        r += 1
    return r, factored_total(r, shapes)


# ---------------------------------------------------------------------------
# Price: plain 1-bit floor and the factored rank that fits under it.
# ---------------------------------------------------------------------------

def cmd_price(args):
    shapes = matrix_shapes(args.base)
    price, n_weights = bitdelta_price(shapes)
    rank, fac_bytes = best_uniform_rank(price, shapes)
    out = {
        "n_matrices": len(shapes),
        "n_weights_169_matrices": n_weights,
        "bitdelta_init_price_bytes": price,
        "bitdelta_price_formula": "ceil(total_weights / 8) + 4 bytes x n_matrices (one fp32 scale per matrix)",
        "factored_matched_rank": rank,
        "factored_matched_price_bytes": fac_bytes,
        "factored_rank_plus_one_price_bytes": factored_total(rank + 1, shapes),
        "factored_under_by_bytes": price - fac_bytes,
    }
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    (workdir / "pricing.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


# ---------------------------------------------------------------------------
# Build factored factors at one uniform rank (factored.quantize_delta).
# ---------------------------------------------------------------------------

def cmd_build_factors(args):
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    base_hdr, base_off = s2.load_header(args.base)
    ins_hdr, ins_off = s2.load_header(args.instruct)
    flat = {}
    t0 = time.perf_counter()
    for store_key, hf_key, _name in s2.matrix_keys():
        Wb = s2.read_tensor_fp32(args.base, base_hdr, base_off, hf_key)
        Wi = s2.read_tensor_fp32(args.instruct, ins_hdr, ins_off, hf_key)
        D = (Wi - Wb).astype(np.float64)
        del Wb, Wi
        q = factored.quantize_delta(D, args.rank)
        del D
        flat[f"{store_key}_U"] = q["U"].astype(np.float32)
        flat[f"{store_key}_V"] = q["V"].astype(np.float32)
        del q
        print(f"built {store_key}", file=sys.stderr)
    out_path = workdir / f"factors_uniform_rank{args.rank}.npz"
    np.savez(out_path, **flat)
    print(json.dumps({
        "factors": str(out_path), "rank": args.rank,
        "wall_s": round(time.perf_counter() - t0, 2),
        "peak_rss_mb": round(s2.peak_rss_mb(), 1),
    }, indent=2))


# ---------------------------------------------------------------------------
# Eval one config on the combined 96 (one process per config).
# ---------------------------------------------------------------------------

def load_probes(path):
    items = json.loads(Path(path).read_text())
    return [(it["bucket"], it["prompt"], it["answer"], it["subset"]) for it in items]


def cmd_eval(args):
    from tokenizers import Tokenizer

    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(str(Path(args.data) / "tokenizer.json"))
    items = load_probes(args.probes)

    t0 = time.perf_counter()
    sd = s2.load_all_fp32(args.base)
    if args.config == "bitdelta_init":
        base_hdr, base_off = s2.load_header(args.base)
        ins_hdr, ins_off = s2.load_header(args.instruct)
        scales = {}
        for store_key, hf_key, _name in s2.matrix_keys():
            Wi = s2.read_tensor_fp32(args.instruct, ins_hdr, ins_off, hf_key)
            D = Wi - sd[hf_key]
            del Wi
            alpha = float(np.mean(np.abs(D)))
            scales[store_key] = alpha
            sd[hf_key] = sd[hf_key] + alpha * np.sign(D)
            del D
        (workdir / "bitdelta_scales.json").write_text(json.dumps(scales, indent=2) + "\n")
        applied = ("base + BitDelta-initialization delta (sign(delta) * per-matrix "
                   "mean|delta|, no distillation, no training) on the 169 recipe "
                   "matrices; all other tensors at base values")
    elif args.config.startswith("factored_rank"):
        rank = int(args.config.removeprefix("factored_rank"))
        fac = np.load(workdir / f"factors_uniform_rank{rank}.npz")
        key_of = {sk: hk for sk, hk, _ in s2.matrix_keys()}
        for store_key, hf_key in key_of.items():
            U, V = fac[f"{store_key}_U"], fac[f"{store_key}_V"]
            sd[hf_key] = sd[hf_key] + (U @ V.T)
        applied = (f"base + factored delta (uniform rank {rank}) on the 169 recipe "
                   "matrices; all other tensors at base values")
    else:
        raise SystemExit(f"unknown config {args.config}")
    load_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    rows = []
    for subset in SUBSETS:
        sub_items = [(b, p, a) for (b, p, a, s) in items if s == subset]
        sub_rows = s2.score_items(tok, sd, sub_items)
        for r in sub_rows:
            r["subset"] = subset
        rows.extend(sub_rows)
    eval_s = time.perf_counter() - t1
    del sd
    gc.collect()

    out = {
        "config": args.config,
        "probe_set": "heldout96_spark",
        "applied": applied,
        "n_items": len(rows),
        "scores": s2.aggregate(rows),
        "scores_by_subset": {s: s2.aggregate([r for r in rows if r["subset"] == s])
                             for s in SUBSETS},
        "per_item": rows,
        "load_wall_s": round(load_s, 2),
        "eval_wall_s": round(eval_s, 2),
        "wall_s": round(time.perf_counter() - t0, 2),
        "peak_rss_mb": round(s2.peak_rss_mb(), 1),
    }
    (workdir / f"eval_{args.config}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("config", "n_items", "wall_s", "peak_rss_mb")}, indent=2))
    print("combined:", json.dumps(out["scores"]["overall"], indent=2))


# ---------------------------------------------------------------------------
# Assemble the deliverable.
# ---------------------------------------------------------------------------

def gap_closed(factored_scores, base_scores, full_scores):
    out = {}
    for b in ("knowledge", "instruction", "math"):
        gap = (full_scores["per_bucket"][b]["mean_target_logprob"]
               - base_scores["per_bucket"][b]["mean_target_logprob"])
        out[b] = ((factored_scores["per_bucket"][b]["mean_target_logprob"]
                   - base_scores["per_bucket"][b]["mean_target_logprob"]) / gap
                  if gap and gap > 1e-9 else None)
    gap_all = (full_scores["overall"]["mean_target_logprob"]
               - base_scores["overall"]["mean_target_logprob"])
    out["overall"] = ((factored_scores["overall"]["mean_target_logprob"]
                       - base_scores["overall"]["mean_target_logprob"]) / gap_all
                      if gap_all and gap_all > 1e-9 else None)
    return out


def cmd_assemble(args):
    workdir = Path(args.workdir)
    pricing = json.loads((workdir / "pricing.json").read_text())
    h96 = json.loads(Path(args.heldout96).read_text())
    base_scores = h96["shared_configs"]["base"]
    full_scores = h96["shared_configs"]["full_delta"]
    rank = pricing["factored_matched_rank"]

    ev_bd = json.loads((workdir / "eval_bitdelta_init.json").read_text())
    ev_fac = json.loads((workdir / f"eval_factored_rank{rank}.json").read_text())

    def block(ev, price_bytes):
        return {
            "mean_target_logprob": ev["scores"]["overall"]["mean_target_logprob"],
            "accuracy_first_token": ev["scores"]["overall"]["accuracy"],
            "per_bucket_mean_target_logprob": {
                b: ev["scores"]["per_bucket"][b]["mean_target_logprob"]
                for b in ("knowledge", "instruction", "math")},
            "gap_closed": gap_closed(ev["scores"], base_scores, full_scores),
            "price_bytes": price_bytes,
            "wall_s": ev["wall_s"],
            "peak_rss_mb": ev["peak_rss_mb"],
        }

    lite = h96["configs"]["mlp_behemoth_lite"]
    uniform = h96["configs"]["uniform_rank32"]
    result = {
        "stage": "bitdelta_baseline_missing_baseline",
        "date": "2026-10-28",
        "machine": "Flash (Vinay's Ubuntu box, ssh flash, 12 threads, qwen-test venv: python 3.14 + numpy 2.5.4 + tokenizers 0.23.3)",
        "question": ("GPT-OSS 120B, fresh-eyes review (results/fresh_perspective.md): "
                     "why not a plain 1-bit delta at the same bytes, i.e. a baseline "
                     "against an existing delta codec?"),
        "model_pair": h96["model_pair"],
        "probe_set": "the same combined 96 fresh held-out questions and the same scoring (mean target logprob, Signet convention, Stage 2 NumPy forward) as results/alien_sweep_heldout96.json",
        "references_from_heldout96": {
            "base_mean_target_logprob": base_scores["overall"]["mean_target_logprob"],
            "full_delta_mean_target_logprob": full_scores["overall"]["mean_target_logprob"],
            "full_delta_fp16_bytes": h96["method"]["full_delta_fp16_bytes"],
        },
        "pricing": pricing,
        "configs": {
            "bitdelta_init": {
                "kind": "published_baseline_initialization",
                "definition": ("BitDelta initialization (Liu et al., arXiv:2402.10193): "
                               "per matrix, delta_hat = sign(delta) * mean(|delta|); one "
                               "fp32 scale per matrix; NO scale distillation and NO "
                               "training. The full BitDelta method distills the scales "
                               "on data afterwards; that step is deliberately not run, "
                               "and this config must be cited as the initialization, "
                               "not as BitDelta's final reported quality."),
                **block(ev_bd, pricing["bitdelta_init_price_bytes"]),
            },
            f"factored_uniform_rank{rank}": {
                "kind": "ours_factored_matched_budget",
                "definition": (f"factored.quantize_delta at uniform rank {rank} on all "
                               "169 matrices: the largest uniform rank whose "
                               "factored.storage_bytes total fits under the plain "
                               "1-bit price."),
                **block(ev_fac, pricing["factored_matched_price_bytes"]),
            },
        },
        "two_budget_curve": {
            "framing": ("A plain 1-bit delta has a floor price: 1 bit per weight over "
                        "the 169 matrices plus one scale per matrix. At the 19.4 MB "
                        "headline budget no plain 1-bit delta fits, so the honest "
                        "comparison is a curve with two budgets, not one."),
            "budget_19mb_factored_only": {
                "uniform_rank32": {
                    "price_bytes": uniform["real_shape_bytes"],
                    "gap_closed_overall": uniform["combined96"]["gap_closed"]["overall"],
                    "source": "results/alien_sweep_heldout96.json",
                },
                "mlp_behemoth_lite_spark_recipe": {
                    "price_bytes": lite["real_shape_bytes"],
                    "gap_closed_overall": lite["combined96"]["gap_closed"]["overall"],
                    "source": "results/alien_sweep_heldout96.json",
                },
                "plain_1bit_delta": "does not fit: floor price is "
                                    f"{pricing['bitdelta_init_price_bytes']} bytes",
            },
            "budget_at_plain_1bit_floor": {
                "bitdelta_init": {
                    "price_bytes": pricing["bitdelta_init_price_bytes"],
                    "gap_closed_overall": gap_closed(ev_bd["scores"], base_scores, full_scores)["overall"],
                },
                f"factored_uniform_rank{rank}": {
                    "price_bytes": pricing["factored_matched_price_bytes"],
                    "gap_closed_overall": gap_closed(ev_fac["scores"], base_scores, full_scores)["overall"],
                },
            },
        },
        "scripts": ["examples/bitdelta_baseline.py"],
        "api_calls": "none for the measurements (compute only); the Spark judging pass over this file is logged in results/api_usage_log.jsonl",
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {out}")
    print(json.dumps(result["two_budget_curve"], indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("price")
    p.add_argument("--base", required=True)
    p.add_argument("--workdir", required=True)
    p.set_defaults(fn=cmd_price)

    b = sub.add_parser("build-factors")
    b.add_argument("--rank", type=int, required=True)
    b.add_argument("--base", required=True)
    b.add_argument("--instruct", required=True)
    b.add_argument("--workdir", required=True)
    b.set_defaults(fn=cmd_build_factors)

    e = sub.add_parser("eval")
    e.add_argument("--config", required=True)
    e.add_argument("--base", required=True)
    e.add_argument("--instruct", required=True)
    e.add_argument("--probes", required=True)
    e.add_argument("--data", default=str(Path.home() / "qwen-test" / "data"))
    e.add_argument("--workdir", required=True)
    e.set_defaults(fn=cmd_eval)

    a = sub.add_parser("assemble")
    a.add_argument("--workdir", required=True)
    a.add_argument("--heldout96", required=True)
    a.add_argument("--out", required=True)
    a.set_defaults(fn=cmd_assemble)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
