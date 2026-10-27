"""Alien Sweep held-out guard: score Stage 2 configs on fresh probes.

    # on Flash, with the qwen-test venv (numpy + tokenizers), next to
    # alien_sweep_stage2.py and factored.py:
    python3 alien_sweep_heldout.py build-variant \
        --base ~/qwen-test/data/qwen2.5-0.5b.safetensors \
        --instruct ~/qwen-test/data/qwen2.5-0.5b-instruct.safetensors \
        --variant /tmp/variant.json \
        --stage2-workdir ~/fc-v04-sweep/stage2 \
        --workdir ~/fc-v04-sweep/heldout
    python3 alien_sweep_heldout.py eval --config base \
        --base ... --instruct ... --probes data/heldout_probes_spark.json \
        --stage2-workdir ~/fc-v04-sweep/stage2 --workdir ~/fc-v04-sweep/heldout
    # ... eval full_delta, uniform_rank32, mlp_behemoth, and the variant
    python3 alien_sweep_heldout.py assemble \
        --probes data/heldout_probes_spark.json --variant /tmp/variant.json \
        --stage2-workdir ~/fc-v04-sweep/stage2 --workdir ~/fc-v04-sweep/heldout \
        --out results/alien_sweep_heldout.json

The held-out guard from the Alien Sweep protocol in BUILD_PLAN.md:
Spark generated 24 fresh probe items the sweep never saw (see
examples/alien_sweep_heldout_gen.py). The Stage 2 winner is only
confirmed if it still beats the human uniform rank-32 recipe on these
items. This script scores, with the exact Stage 2 machinery (same
forward pass, same chat formatting, same metrics):

- base and full_delta (shared references),
- uniform_rank32 (human baseline),
- mlp_behemoth (Stage 2 winner by task score),
- the Spark byte-matched variant of mlp_behemoth (same style, priced
  to fit the uniform recipe's real byte budget).

The variant's factors are built here, one exact SVD per matrix sliced
at the variant's rank, using alien_sweep_stage2.quantize_from_svd
(the construction Stage 2 validated against factored.quantize_delta).
Its price is validated in the same pass the Stage 2 way:
factored.storage_bytes summed over the 169 real matrices read from
the model files. The other configs reuse Stage 2's factor files and
Stage 2's recorded real-shape prices.

Probe items keep the Signet scorer's shape (bucket / prompt / answer,
plus a "wrong" list that the scorer does not use). Buckets use the
source labels ("instruct"), renamed to "instruction" in aggregates by
alien_sweep_stage2.BUCKET_LABELS, exactly as in Stage 2.
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

import factored  # noqa: E402
import alien_sweep_stage2 as s2  # noqa: E402

CONFIGS_SHARED = ["base", "full_delta", "uniform_rank32", "mlp_behemoth"]


def load_probes(path):
    items = json.loads(Path(path).read_text())
    out = []
    for it in items:
        out.append((it["bucket"], it["prompt"], it["answer"]))
    return out


# ---------------------------------------------------------------------------
# Build the byte-matched variant's factors + validate its real price.
# ---------------------------------------------------------------------------

def cmd_build_variant(args):
    variant = json.loads(Path(args.variant).read_text())
    ranks = {k: int(v) for k, v in variant["ranks"].items()}
    name = variant["name"]
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    base_hdr, base_off = s2.load_header(args.base)
    ins_hdr, ins_off = s2.load_header(args.instruct)

    pricing = 0
    full_fp16 = 0
    flat = {}
    t_all = time.perf_counter()
    for store_key, hf_key, layer_name in s2.matrix_keys():
        Wb = s2.read_tensor_fp32(args.base, base_hdr, base_off, hf_key)
        Wi = s2.read_tensor_fp32(args.instruct, ins_hdr, ins_off, hf_key)
        D32 = Wi - Wb
        shape = D32.shape
        del Wb, Wi
        full_fp16 += 2 * D32.size
        r = ranks[layer_name]
        # Stage 2 pricing, exactly: storage_bytes per real matrix.
        pricing += factored.storage_bytes(r, shape)
        if r == 0:
            del D32
            continue
        D = D32.astype(np.float64)
        del D32
        svd = np.linalg.svd(D, full_matrices=False)
        U, V = s2.quantize_from_svd(D, svd, r)
        del D, svd
        flat[f"{store_key}_U"] = U.astype(np.float32)
        flat[f"{store_key}_V"] = V.astype(np.float32)
        del U, V
        print(f"built {store_key} rank={r}", file=sys.stderr)

    np.savez(workdir / f"factors_{name}.npz", **flat)
    stage2_build = json.loads((Path(args.stage2_workdir) / "build_summary.json").read_text())
    record = {
        "phase": "build_variant",
        "variant_name": name,
        "ranks": ranks,
        "real_shape_bytes_computed": int(pricing),
        "real_shape_bytes_claimed_by_generation": variant.get("real_shape_bytes"),
        "price_matches_generation_claim": int(pricing) == variant.get("real_shape_bytes"),
        "budget_bytes_uniform_rank32_real": stage2_build["pricing"]["uniform_rank32"]["real_shape_bytes"],
        "within_budget": int(pricing) <= stage2_build["pricing"]["uniform_rank32"]["real_shape_bytes"],
        "full_delta_fp16_bytes": int(full_fp16),
        "wall_s": round(time.perf_counter() - t_all, 2),
        "peak_rss_mb": round(s2.peak_rss_mb(), 1),
    }
    (workdir / "build_variant.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


# ---------------------------------------------------------------------------
# Eval one config on the held-out probes (one process per config).
# ---------------------------------------------------------------------------

def cmd_eval(args):
    from tokenizers import Tokenizer

    workdir = Path(args.workdir)
    stage2_workdir = Path(args.stage2_workdir)
    tok = Tokenizer.from_file(str(Path(args.data) / "tokenizer.json"))
    items = load_probes(args.probes)

    t0 = time.perf_counter()
    if args.config == "full_delta":
        sd = s2.load_all_fp32(args.instruct)
        applied = "Instruct weights (== base + full delta on every tensor)"
    else:
        sd = s2.load_all_fp32(args.base)
        if args.config == "base":
            applied = "base weights, no delta"
        else:
            fac_path = workdir / f"factors_{args.config}.npz"
            if not fac_path.exists():
                fac_path = stage2_workdir / f"factors_{args.config}.npz"
            fac = np.load(fac_path)
            key_of = {sk: hk for sk, hk, _ in s2.matrix_keys()}
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
    rows = s2.score_items(tok, sd, items)
    eval_s = time.perf_counter() - t1
    del sd
    gc.collect()

    out = {
        "config": args.config,
        "probe_set": "heldout_spark",
        "applied": applied,
        "n_items": len(rows),
        "scores": s2.aggregate(rows),
        "per_item": rows,
        "load_wall_s": round(load_s, 2),
        "eval_wall_s": round(eval_s, 2),
        "wall_s": round(time.perf_counter() - t0, 2),
        "peak_rss_mb": round(s2.peak_rss_mb(), 1),
    }
    (workdir / f"eval_{args.config}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("config", "n_items", "wall_s", "peak_rss_mb")}, indent=2))
    print(json.dumps(out["scores"], indent=2))


# ---------------------------------------------------------------------------
# Assemble the deliverable.
# ---------------------------------------------------------------------------

def cmd_assemble(args):
    workdir = Path(args.workdir)
    stage2_workdir = Path(args.stage2_workdir)
    variant = json.loads(Path(args.variant).read_text())
    vname = variant["name"]
    build_v = json.loads((workdir / "build_variant.json").read_text())
    stage2_build = json.loads((stage2_workdir / "build_summary.json").read_text())
    stage2_result = json.loads(Path(args.stage2_results).read_text())
    gen_record = json.loads(Path(args.gen_record).read_text())
    probes = json.loads(Path(args.probes).read_text())

    configs = CONFIGS_SHARED + [vname]
    evals = {c: json.loads((workdir / f"eval_{c}.json").read_text()) for c in configs}
    base_scores = evals["base"]["scores"]
    full_scores = evals["full_delta"]["scores"]

    def gap_closed(factored_scores):
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

    def cfg_block(ev):
        return {"overall": ev["scores"]["overall"], "per_bucket": ev["scores"]["per_bucket"]}

    rank_maps = dict(stage2_build["rank_maps"])
    rank_maps[vname] = {k: int(v) for k, v in variant["ranks"].items()}
    real_bytes = {c: stage2_build["pricing"][c]["real_shape_bytes"]
                  for c in ("uniform_rank32", "mlp_behemoth")}
    real_bytes[vname] = build_v["real_shape_bytes_computed"]
    kinds = {"uniform_rank32": "human_baseline", "mlp_behemoth": "spark_recipe_stage2_winner",
             vname: "spark_bytematched_variant"}

    entries = {}
    for c in ("uniform_rank32", "mlp_behemoth", vname):
        ev = evals[c]
        entries[c] = {
            "name": c,
            "kind": kinds[c],
            "ranks": rank_maps[c],
            "rank0_layer_names": [n for n, r in rank_maps[c].items() if r == 0],
            "real_shape_bytes": real_bytes[c],
            "configs": {
                "base": cfg_block(evals["base"]),
                "full_delta": cfg_block(evals["full_delta"]),
                "factored_delta": cfg_block(ev),
            },
            "gap_closed": gap_closed(ev["scores"]),
            "per_item": ev["per_item"],
            "wall_s": ev["wall_s"],
            "eval_wall_s": ev["eval_wall_s"],
            "peak_rss_mb": ev["peak_rss_mb"],
        }

    def lp(c):
        return evals[c]["scores"]["overall"]["mean_target_logprob"]

    def acc(c):
        return evals[c]["scores"]["overall"]["accuracy"]

    uniform_b = real_bytes["uniform_rank32"]
    verdict = {
        "stage2_winner": "mlp_behemoth",
        "heldout_task_score_metric": "overall mean target logprob of the factored config (Stage 2 convention)",
        "mlp_behemoth_beats_uniform_on_heldout": lp("mlp_behemoth") > lp("uniform_rank32"),
        "mlp_behemoth_confirmed_sweep_winner": lp("mlp_behemoth") > lp("uniform_rank32"),
        "byte_fair_comparison": {
            "variant": vname,
            "variant_real_shape_bytes": real_bytes[vname],
            "uniform_real_shape_bytes": uniform_b,
            "variant_within_uniform_budget": real_bytes[vname] <= uniform_b,
            "variant_beats_uniform_on_heldout": lp(vname) > lp("uniform_rank32"),
            "variant_gap_closed_overall": entries[vname]["gap_closed"]["overall"],
            "uniform_gap_closed_overall": entries["uniform_rank32"]["gap_closed"]["overall"],
        },
        "mlp_behemoth_byte_caveat": {
            "mlp_behemoth_real_shape_bytes": real_bytes["mlp_behemoth"],
            "uniform_real_shape_bytes": uniform_b,
            "over_bytes": real_bytes["mlp_behemoth"] - uniform_b,
            "over_pct": round(100.0 * (real_bytes["mlp_behemoth"] - uniform_b) / uniform_b, 1),
            "note": "mlp_behemoth's Stage 2 win was not byte-fair; the byte-fair comparison is the variant's row.",
        },
    }

    result = {
        "stage": "alien_sweep_heldout_guard",
        "date": "2026-10-27",
        "machine": "Flash (Vinay's Ubuntu box, ssh flash, 12 threads, qwen-test venv: python 3.14 + numpy 2.5.4 + tokenizers 0.23.3)",
        "model_pair": stage2_result["model_pair"],
        "probe_set": {
            "source": "fresh probe items generated by Muse Spark (Meta Model API, muse-spark-1.3) for this guard; the sweep never saw them during search, Stage 1, or Stage 2",
            "file": "data/heldout_probes_spark.json (local only, data/ is gitignored)",
            "n_items": len(probes),
            "buckets": {"knowledge": 8, "instruction": 8, "math": 8},
            "shape": "Signet scorer shape: bucket / prompt / answer per item, plus 2 plausible wrong answers per item (recorded, not used by the scorer)",
            "bucket_label_note": "items carry the Signet source label 'instruct'; reported as 'instruction' via the same rename Stage 2 used",
            "novelty_check": "no exact normalized prompt match and no token-set Jaccard >= 0.7 against the 24 pre-existing Signet prompts; Spark's first draft reproduced one Signet item ('The year the Berlin Wall fell was'), which the check caught and the logged retry replaced",
            "generation": {
                "provider": "meta-model-api",
                "model": "muse-spark-1.3",
                "calls": [
                    {"purpose": a.get("purpose"), "time": a.get("time"),
                     "prompt_tokens": a.get("prompt_tokens"),
                     "completion_tokens": a.get("completion_tokens"),
                     "total_tokens": a.get("total_tokens")}
                    for a in gen_record.get("usage_rows", [])
                ],
            },
            "style_deviations_noted": "Spark dropped the leading-space convention on most answers and the math items do not carry the 'Answer with just the number.' suffix; items are scored identically for every config, so within-set comparisons are unaffected",
        },
        "byte_matched_variant": {
            "name": vname,
            "reason": variant.get("reason"),
            "ranks": rank_maps[vname],
            "generation_attempts": [
                {"attempt": a["attempt"], "real_shape_bytes": a.get("real_shape_bytes"),
                 "within_budget": a.get("within_budget")}
                for a in gen_record.get("variant", {}).get("attempts", [])
            ],
            "price_validation": {
                "method": "factored.storage_bytes summed over the 169 real matrices read from the model files, computed in the Flash build pass (same code path as Stage 2 pricing)",
                "real_shape_bytes_computed_on_flash": build_v["real_shape_bytes_computed"],
                "matches_generation_claim": build_v["price_matches_generation_claim"],
                "budget_bytes_uniform_rank32_real": build_v["budget_bytes_uniform_rank32_real"],
                "within_budget": build_v["within_budget"],
                "build_wall_s": build_v["wall_s"],
                "build_peak_rss_mb": build_v["peak_rss_mb"],
            },
        },
        "method": {
            "configs": "base (no delta), full_delta (Instruct weights), and factored_delta per recipe: uniform_rank32, mlp_behemoth, and the byte-matched variant",
            "scoring": "identical to Stage 2: chat-formatted prompt (Qwen default system line); target logprob = summed log-probability of the answer tokens; accuracy = first-token accuracy; gap_closed = (factored - base) / (full - base) on mean target logprob",
            "forward_pass": "the Stage 2 NumPy Qwen2.5 forward (alien_sweep_stage2.py), validated in Stage 2 against the prior Signet run's published bucket means",
            "heldout_only": "every score in this file is on the 24 held-out items only; no Signet item was scored here",
        },
        "shared_configs": {
            "base": cfg_block(evals["base"]),
            "full_delta": cfg_block(evals["full_delta"]),
            "base_wall_s": evals["base"]["wall_s"],
            "full_delta_wall_s": evals["full_delta"]["wall_s"],
        },
        "configs": entries,
        "ranking_by_heldout_task_score": sorted(
            ({"name": c, "kind": kinds[c],
              "factored_mean_target_logprob": lp(c), "factored_accuracy": acc(c),
              "overall_gap_closed": entries[c]["gap_closed"]["overall"],
              "real_shape_bytes": real_bytes[c]}
             for c in ("uniform_rank32", "mlp_behemoth", vname)),
            key=lambda e: e["factored_mean_target_logprob"], reverse=True),
        "verdict": verdict,
        "scripts": ["examples/alien_sweep_heldout_gen.py", "examples/alien_sweep_heldout.py"],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {out}")
    print(json.dumps(result["ranking_by_heldout_task_score"], indent=2))
    print(json.dumps(verdict, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build-variant")
    b.add_argument("--base", required=True)
    b.add_argument("--instruct", required=True)
    b.add_argument("--variant", required=True)
    b.add_argument("--stage2-workdir", required=True)
    b.add_argument("--workdir", required=True)
    b.set_defaults(fn=cmd_build_variant)

    e = sub.add_parser("eval")
    e.add_argument("--config", required=True)
    e.add_argument("--base", required=True)
    e.add_argument("--instruct", required=True)
    e.add_argument("--probes", required=True)
    e.add_argument("--data", default=str(Path.home() / "qwen-test" / "data"))
    e.add_argument("--stage2-workdir", required=True)
    e.add_argument("--workdir", required=True)
    e.set_defaults(fn=cmd_eval)

    a = sub.add_parser("assemble")
    a.add_argument("--probes", required=True)
    a.add_argument("--variant", required=True)
    a.add_argument("--gen-record", required=True)
    a.add_argument("--stage2-results", default="alien_sweep_stage2.json")
    a.add_argument("--stage2-workdir", required=True)
    a.add_argument("--workdir", required=True)
    a.add_argument("--out", required=True)
    a.set_defaults(fn=cmd_assemble)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
