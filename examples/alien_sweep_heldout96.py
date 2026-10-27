"""Alien Sweep held-out expansion: score the byte-fair contest on 96 items.

    # build the combined probe file (VM or Flash):
    python3 alien_sweep_heldout96.py build-probes \
        --old data/heldout_probes_spark.json \
        --new data/heldout72_probes_spark.json \
        --out data/heldout96_probes_spark.json
    # on Flash, with the qwen-test venv, next to alien_sweep_stage2.py:
    python3 alien_sweep_heldout96.py eval --config base \
        --base ~/qwen-test/data/qwen2.5-0.5b.safetensors \
        --instruct ~/qwen-test/data/qwen2.5-0.5b-instruct.safetensors \
        --probes data/heldout96_probes_spark.json \
        --stage2-workdir ~/fc-v04-sweep/stage2 \
        --heldout-workdir ~/fc-v04-sweep/heldout \
        --workdir ~/fc-v04-sweep/heldout96
    # ... eval full_delta, uniform_rank32, mlp_behemoth, mlp_behemoth_lite
    python3 alien_sweep_heldout96.py assemble \
        --gen-record /tmp/heldout96_gen_record.json \
        --stage2-workdir ~/fc-v04-sweep/stage2 \
        --heldout-workdir ~/fc-v04-sweep/heldout \
        --workdir ~/fc-v04-sweep/heldout96 \
        --out results/alien_sweep_heldout96.json

Strengthening test (Vinay, Oct 27): the original held-out guard scored
the byte-fair contest (mlp_behemoth_lite vs the human uniform rank-32
recipe) on 24 fresh Spark items. This expansion scores the same five
configs on the COMBINED 96 fresh items (the original 24 plus 72 new
ones from alien_sweep_heldout96_gen.py, novelty-checked against both
the Signet 24 and the first held-out 24). Scores are reported for the
combined 96 and, separately, for the old-24 and new-72 subsets, so
old-vs-new consistency is visible rather than assumed.

Machinery is identical to the original guard: the Stage 2 NumPy
Qwen2.5 forward, chat formatting, metrics, factor files and real-shape
byte prices are reused unchanged (alien_sweep_stage2 as a module).
mlp_behemoth runs as a reference only and is labeled byte-unfair
everywhere it appears (21,719,776 real-shape bytes vs the uniform
budget of 19,434,496; ruling in BUILD_PLAN.md).
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

CONFIGS = ["uniform_rank32", "mlp_behemoth", "mlp_behemoth_lite"]
SUBSETS = ("heldout24", "heldout72_new")


def load_probes(path):
    items = json.loads(Path(path).read_text())
    out = []
    for it in items:
        out.append((it["bucket"], it["prompt"], it["answer"], it["subset"]))
    return out


def cmd_build_probes(args):
    old = json.loads(Path(args.old).read_text())
    new = json.loads(Path(args.new).read_text())
    combined = ([{**it, "subset": "heldout24"} for it in old]
                + [{**it, "subset": "heldout72_new"} for it in new])
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(combined, indent=2) + "\n")
    print(f"combined probes: {len(old)} old + {len(new)} new = {len(combined)} -> {out}")


# ---------------------------------------------------------------------------
# Eval one config on the combined 96 probes (one process per config).
# ---------------------------------------------------------------------------

def cmd_eval(args):
    from tokenizers import Tokenizer

    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
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
            fac_path = Path(args.heldout_workdir) / f"factors_{args.config}.npz"
            if not fac_path.exists():
                fac_path = Path(args.stage2_workdir) / f"factors_{args.config}.npz"
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

    def agg(rs):
        return s2.aggregate(rs)

    out = {
        "config": args.config,
        "probe_set": "heldout96_spark",
        "applied": applied,
        "n_items": len(rows),
        "scores": agg(rows),
        "scores_by_subset": {s: agg([r for r in rows if r["subset"] == s]) for s in SUBSETS},
        "per_item": rows,
        "load_wall_s": round(load_s, 2),
        "eval_wall_s": round(eval_s, 2),
        "wall_s": round(time.perf_counter() - t0, 2),
        "peak_rss_mb": round(s2.peak_rss_mb(), 1),
    }
    (workdir / f"eval_{args.config}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("config", "n_items", "wall_s", "peak_rss_mb")}, indent=2))
    print("combined:", json.dumps(out["scores"]["overall"], indent=2))
    for s in SUBSETS:
        print(s, json.dumps(out["scores_by_subset"][s]["overall"], indent=2))


# ---------------------------------------------------------------------------
# Assemble the deliverable.
# ---------------------------------------------------------------------------

def gap_closed(factored, base, full):
    out = {}
    for b in ("knowledge", "instruction", "math"):
        gap = (full["per_bucket"][b]["mean_target_logprob"]
               - base["per_bucket"][b]["mean_target_logprob"])
        out[b] = ((factored["per_bucket"][b]["mean_target_logprob"]
                   - base["per_bucket"][b]["mean_target_logprob"]) / gap
                  if gap and gap > 1e-9 else None)
    gap_all = (full["overall"]["mean_target_logprob"] - base["overall"]["mean_target_logprob"])
    out["overall"] = ((factored["overall"]["mean_target_logprob"]
                       - base["overall"]["mean_target_logprob"]) / gap_all
                      if gap_all and gap_all > 1e-9 else None)
    return out


def cmd_assemble(args):
    workdir = Path(args.workdir)
    stage2_build = json.loads((Path(args.stage2_workdir) / "build_summary.json").read_text())
    build_v = json.loads((Path(args.heldout_workdir) / "build_variant.json").read_text())
    gen_record = json.loads(Path(args.gen_record).read_text())
    heldout_result = json.loads(Path(args.heldout_results).read_text())

    all_configs = ["base", "full_delta"] + CONFIGS
    evals = {c: json.loads((workdir / f"eval_{c}.json").read_text()) for c in all_configs}

    rank_maps = dict(stage2_build["rank_maps"])
    rank_maps["mlp_behemoth_lite"] = heldout_result["byte_matched_variant"]["ranks"]
    real_bytes = {
        "uniform_rank32": stage2_build["pricing"]["uniform_rank32"]["real_shape_bytes"],
        "mlp_behemoth": stage2_build["pricing"]["mlp_behemoth"]["real_shape_bytes"],
        "mlp_behemoth_lite": build_v["real_shape_bytes_computed"],
    }
    kinds = {"uniform_rank32": "human_baseline",
             "mlp_behemoth": "spark_recipe_stage2_winner_BYTE_UNFAIR_reference_only",
             "mlp_behemoth_lite": "spark_bytematched_variant"}

    def view(ev, which):
        return ev["scores"] if which == "combined96" else ev["scores_by_subset"][which]

    entries = {}
    for c in CONFIGS:
        ev = evals[c]
        entries[c] = {
            "name": c,
            "kind": kinds[c],
            "byte_unfair": c == "mlp_behemoth",
            "ranks": rank_maps[c],
            "rank0_layer_names": [n for n, r in rank_maps[c].items() if r == 0],
            "real_shape_bytes": real_bytes[c],
            "combined96": {
                "configs": {"base": view(evals["base"], "combined96"),
                            "full_delta": view(evals["full_delta"], "combined96"),
                            "factored_delta": view(ev, "combined96")},
                "gap_closed": gap_closed(view(ev, "combined96"), view(evals["base"], "combined96"),
                                         view(evals["full_delta"], "combined96")),
            },
            "heldout24_subset": {
                "configs": {"base": view(evals["base"], "heldout24"),
                            "full_delta": view(evals["full_delta"], "heldout24"),
                            "factored_delta": view(ev, "heldout24")},
                "gap_closed": gap_closed(view(ev, "heldout24"), view(evals["base"], "heldout24"),
                                         view(evals["full_delta"], "heldout24")),
            },
            "heldout72_new_subset": {
                "configs": {"base": view(evals["base"], "heldout72_new"),
                            "full_delta": view(evals["full_delta"], "heldout72_new"),
                            "factored_delta": view(ev, "heldout72_new")},
                "gap_closed": gap_closed(view(ev, "heldout72_new"),
                                         view(evals["base"], "heldout72_new"),
                                         view(evals["full_delta"], "heldout72_new")),
            },
            "per_item": ev["per_item"],
            "wall_s": ev["wall_s"],
            "eval_wall_s": ev["eval_wall_s"],
            "peak_rss_mb": ev["peak_rss_mb"],
        }

    def lp96(c):
        return evals[c]["scores"]["overall"]["mean_target_logprob"]

    def gc96(c):
        return entries[c]["combined96"]["gap_closed"]["overall"]

    uniform_b = real_bytes["uniform_rank32"]
    verdict = {
        "byte_fair_headline_question": "does mlp_behemoth_lite still beat uniform_rank32 on the combined 96 fresh items?",
        "lite_beats_uniform_on_combined96": lp96("mlp_behemoth_lite") > lp96("uniform_rank32"),
        "lite_gap_closed_combined96": gc96("mlp_behemoth_lite"),
        "uniform_gap_closed_combined96": gc96("uniform_rank32"),
        "lite_within_uniform_budget": real_bytes["mlp_behemoth_lite"] <= uniform_b,
        "subset_consistency": {
            "heldout24": {
                "lite_gap_closed": entries["mlp_behemoth_lite"]["heldout24_subset"]["gap_closed"]["overall"],
                "uniform_gap_closed": entries["uniform_rank32"]["heldout24_subset"]["gap_closed"]["overall"],
                "lite_beats_uniform": (
                    evals["mlp_behemoth_lite"]["scores_by_subset"]["heldout24"]["overall"]["mean_target_logprob"]
                    > evals["uniform_rank32"]["scores_by_subset"]["heldout24"]["overall"]["mean_target_logprob"]),
            },
            "heldout72_new": {
                "lite_gap_closed": entries["mlp_behemoth_lite"]["heldout72_new_subset"]["gap_closed"]["overall"],
                "uniform_gap_closed": entries["uniform_rank32"]["heldout72_new_subset"]["gap_closed"]["overall"],
                "lite_beats_uniform": (
                    evals["mlp_behemoth_lite"]["scores_by_subset"]["heldout72_new"]["overall"]["mean_target_logprob"]
                    > evals["uniform_rank32"]["scores_by_subset"]["heldout72_new"]["overall"]["mean_target_logprob"]),
            },
        },
        "mlp_behemoth_reference_only": {
            "note": "mlp_behemoth is BYTE-UNFAIR (over the uniform budget) and is "
                    "reported as a reference only, never as the headline.",
            "real_shape_bytes": real_bytes["mlp_behemoth"],
            "uniform_real_shape_bytes": uniform_b,
            "over_bytes": real_bytes["mlp_behemoth"] - uniform_b,
            "over_pct": round(100.0 * (real_bytes["mlp_behemoth"] - uniform_b) / uniform_b, 1),
            "combined96_gap_closed": gc96("mlp_behemoth"),
            "combined96_factored_mean_target_logprob": lp96("mlp_behemoth"),
        },
    }

    gen_calls = []
    for bucket, entry in gen_record.get("buckets", {}).items():
        for i, a in enumerate(entry["attempts"]):
            gen_calls.append({
                "purpose": f"alien_sweep_heldout96_probe_generation_{bucket}" + ("_retry" if i else ""),
                "usage": a.get("usage"), "elapsed_s": a.get("elapsed_s"),
                "validation_problems_first_attempt": entry["validation_problems"] if i == 0 else None,
            })

    result = {
        "stage": "alien_sweep_heldout96_expansion",
        "date": "2026-10-27",
        "machine": "Flash (Vinay's Ubuntu box, ssh flash, 12 threads, qwen-test venv: python 3.14 + numpy 2.5.4 + tokenizers 0.23.3)",
        "model_pair": heldout_result["model_pair"],
        "probe_set": {
            "source": "combined fresh probe items generated by Muse Spark (Meta Model API, muse-spark-1.3): the original 24 held-out items plus 72 new items from alien_sweep_heldout96_gen.py; the sweep never saw any of them during search, Stage 1, or Stage 2",
            "file": "data/heldout96_probes_spark.json (local only, data/ is gitignored)",
            "n_items": 96,
            "buckets": {"knowledge": 32, "instruction": 32, "math": 32},
            "subsets": {"heldout24": 24, "heldout72_new": 72},
            "novelty_check_new72": "no exact normalized prompt match and no token-set Jaccard >= 0.7 against the 24 Signet prompts OR the first 24 held-out prompts; the knowledge bucket's first draft had one prompt flagged (Jaccard 0.71, a Switzerland currency item), regenerated via the logged retry",
            "generation": {"provider": "meta-model-api", "model": "muse-spark-1.3", "calls": gen_calls},
        },
        "method": {
            "configs": "base (no delta), full_delta (Instruct weights), and factored_delta per recipe: uniform_rank32, mlp_behemoth_lite (byte-matched), mlp_behemoth (BYTE-UNFAIR reference only)",
            "scoring": "identical to Stage 2 and the original guard: chat-formatted prompt (Qwen default system line); target logprob = summed log-probability of the answer tokens; accuracy = first-token accuracy; gap_closed = (factored - base) / (full - base) on mean target logprob, computed separately for the combined 96 and each subset with that subset's own base/full references",
            "forward_pass": "the Stage 2 NumPy Qwen2.5 forward (alien_sweep_stage2.py), unchanged",
            "full_delta_fp16_bytes": stage2_build["full_delta_fp16_bytes"],
        },
        "shared_configs": {
            "base": evals["base"]["scores"],
            "full_delta": evals["full_delta"]["scores"],
            "base_by_subset": evals["base"]["scores_by_subset"],
            "full_delta_by_subset": evals["full_delta"]["scores_by_subset"],
        },
        "configs": entries,
        "ranking_by_combined96_task_score": sorted(
            ({"name": c, "kind": kinds[c], "byte_unfair": c == "mlp_behemoth",
              "factored_mean_target_logprob": lp96(c),
              "factored_accuracy": evals[c]["scores"]["overall"]["accuracy"],
              "overall_gap_closed": gc96(c), "real_shape_bytes": real_bytes[c]}
             for c in CONFIGS),
            key=lambda e: e["factored_mean_target_logprob"], reverse=True),
        "verdict": verdict,
        "scripts": ["examples/alien_sweep_heldout96_gen.py", "examples/alien_sweep_heldout96.py"],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {out}")
    print(json.dumps(result["ranking_by_combined96_task_score"], indent=2))
    print(json.dumps(verdict, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    bp = sub.add_parser("build-probes")
    bp.add_argument("--old", required=True)
    bp.add_argument("--new", required=True)
    bp.add_argument("--out", required=True)
    bp.set_defaults(fn=cmd_build_probes)

    e = sub.add_parser("eval")
    e.add_argument("--config", required=True)
    e.add_argument("--base", required=True)
    e.add_argument("--instruct", required=True)
    e.add_argument("--probes", required=True)
    e.add_argument("--data", default=str(Path.home() / "qwen-test" / "data"))
    e.add_argument("--stage2-workdir", required=True)
    e.add_argument("--heldout-workdir", required=True)
    e.add_argument("--workdir", required=True)
    e.set_defaults(fn=cmd_eval)

    a = sub.add_parser("assemble")
    a.add_argument("--gen-record", required=True)
    a.add_argument("--heldout-results", default="alien_sweep_heldout.json")
    a.add_argument("--stage2-workdir", required=True)
    a.add_argument("--heldout-workdir", required=True)
    a.add_argument("--workdir", required=True)
    a.add_argument("--out", required=True)
    a.set_defaults(fn=cmd_assemble)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
