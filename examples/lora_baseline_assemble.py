"""LoRA baseline: assemble the deliverable from all eval JSONs.

Reads the stored held-out-96 eval files (Flash workdir mirror) and the
LoRA baseline eval files, RE-COMPUTES every aggregate from per-item
rows (the script-rerun validation: published aggregates must match the
recompute), verifies the hooked forward against the dense reference
and the zero-adapter against the stored base scores, and writes
results/lora_baseline.json with the side-by-side table.

Run on the Muse VM from the repo root:

    python3 examples/lora_baseline_assemble.py \
        --heldout96-dir /tmp/lora_workdir/heldout96 \
        --lora-dir /tmp/lora_workdir/lora_baseline \
        --stage2-dir /tmp/lora_workdir/stage2 \
        --heldout-dir /tmp/lora_workdir/heldout \
        --gen-record /tmp/lora_distill_gen_record.json \
        --out results/lora_baseline.json
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "src"))
import factored  # noqa: E402

BUCKETS = ("knowledge", "instruction", "math")
SEEDS = (20261028, 20261029, 20261030)


def agg_from_rows(rows):
    def agg(rs):
        n = len(rs)
        return {"n": n,
                "accuracy": sum(r["first_token_correct"] for r in rs) / n if n else 0.0,
                "mean_target_logprob": sum(r["logprob"] for r in rs) / n if n else 0.0}
    out = {"overall": agg(rows)}
    out["per_bucket"] = {b: agg([r for r in rows if r["bucket"] == b]) for b in BUCKETS}
    return out


def gap_closed(scores, base, full):
    out = {}
    for b in BUCKETS:
        gap = (full["per_bucket"][b]["mean_target_logprob"]
               - base["per_bucket"][b]["mean_target_logprob"])
        out[b] = ((scores["per_bucket"][b]["mean_target_logprob"]
                   - base["per_bucket"][b]["mean_target_logprob"]) / gap
                  if gap and gap > 1e-9 else None)
    gap_all = (full["overall"]["mean_target_logprob"]
               - base["overall"]["mean_target_logprob"])
    out["overall"] = ((scores["overall"]["mean_target_logprob"]
                       - base["overall"]["mean_target_logprob"]) / gap_all
                      if gap_all and gap_all > 1e-9 else None)
    return out


def load(d, name):
    return json.loads((Path(d) / name).read_text())


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--heldout96-dir", required=True)
    ap.add_argument("--lora-dir", required=True)
    ap.add_argument("--stage2-dir", required=True)
    ap.add_argument("--heldout-dir", required=True)
    ap.add_argument("--gen-record", required=True)
    ap.add_argument("--published", default="results/alien_sweep_heldout96.json")
    ap.add_argument("--out", default="results/lora_baseline.json")
    args = ap.parse_args()

    published = json.loads(Path(args.published).read_text())
    stored = {c: load(args.heldout96_dir, f"eval_{c}.json")
              for c in ("base", "full_delta", "uniform_rank32", "mlp_behemoth_lite")}

    # --- Script-rerun validation: recompute stored aggregates from
    # per-item rows and compare against the published result file. ---
    rerun = {}
    base_scores = agg_from_rows(stored["base"]["per_item"])
    full_scores = agg_from_rows(stored["full_delta"]["per_item"])
    for c in ("uniform_rank32", "mlp_behemoth_lite"):
        rec = agg_from_rows(stored[c]["per_item"])
        pub = published["configs"][c]["combined96"]["configs"]["factored_delta"]
        rerun[c] = {
            "recomputed_mean_target_logprob": rec["overall"]["mean_target_logprob"],
            "published_mean_target_logprob": pub["overall"]["mean_target_logprob"],
            "abs_diff": abs(rec["overall"]["mean_target_logprob"]
                            - pub["overall"]["mean_target_logprob"]),
            "recomputed_gap_closed": gap_closed(rec, base_scores, full_scores)["overall"],
            "published_gap_closed": published["configs"][c]["combined96"]["gap_closed"]["overall"],
        }
    for c in ("base", "full_delta"):
        rec = agg_from_rows(stored[c]["per_item"])
        pub = published["shared_configs"][c]
        rerun[c] = {
            "recomputed_mean_target_logprob": rec["overall"]["mean_target_logprob"],
            "published_mean_target_logprob": pub["overall"]["mean_target_logprob"],
            "abs_diff": abs(rec["overall"]["mean_target_logprob"]
                            - pub["overall"]["mean_target_logprob"]),
        }

    # --- My eval files + forward-path verification. ---
    lora_dir = Path(args.lora_dir)
    evals = {}
    for name in ("lora_zero", "lora_seed20261028", "lora_seed20261029",
                 "lora_seed20261030", "lora_seed20261028_dense",
                 "lora_seed20261028_fp32", "uniform_noembed", "lite_noembed",
                 "uniform_vfp16", "lite_vfp16"):
        p = lora_dir / f"eval_{name}.json"
        if p.exists():
            evals[name] = json.loads(p.read_text())

    def per_item_diffs(a_rows, b_rows):
        assert len(a_rows) == len(b_rows)
        return max(abs(a["logprob"] - b["logprob"]) for a, b in zip(a_rows, b_rows))

    verification = {
        "zero_adapter_vs_stored_base_max_abs_per_item_diff":
            per_item_diffs(evals["lora_zero"]["per_item"], stored["base"]["per_item"]),
        "dense_vs_hooked_seed1_max_abs_per_item_diff":
            per_item_diffs(evals["lora_seed20261028_dense"]["per_item"],
                           evals["lora_seed20261028"]["per_item"]),
    }
    prep = load(lora_dir, "prep_summary.json")
    verification["torch_port_vs_numpy_base"] = prep["forward_validation"]
    verification["kv_cache_check"] = prep["kv_cache_check"]

    # --- Byte prices. ---
    embed_shape = (151936, 896)
    uniform_bytes = 19434496
    lite_bytes = 19358176
    build_v = load(args.heldout_dir, "build_variant.json")
    lite_ranks = build_v["byte_matched_variant"]["ranks"] \
        if "byte_matched_variant" in build_v else build_v["ranks"]
    lite_embed_price = factored.storage_bytes(int(lite_ranks["embed"]), embed_shape)
    uniform_embed_price = factored.storage_bytes(32, embed_shape)
    adapter_bytes = prep["adapter_price"]["bytes_fp16"]

    def row(name, kind, nbytes, ev, note=None):
        scores = agg_from_rows(ev["per_item"]) if "per_item" in ev else ev["scores"]
        r = {"name": name, "kind": kind, "bytes": nbytes,
             "mean_target_logprob": scores["overall"]["mean_target_logprob"],
             "accuracy": scores["overall"]["accuracy"],
             "gap_closed": gap_closed(scores, base_scores, full_scores),
             "per_bucket_mean_target_logprob":
                 {b: scores["per_bucket"][b]["mean_target_logprob"] for b in BUCKETS},
             "wall_s": ev.get("wall_s"), "peak_rss_mb": ev.get("peak_rss_mb")}
        if note:
            r["note"] = note
        return r

    rows = [
        row("base", "reference", 0, stored["base"]),
        row("full_delta", "reference", published["method"]["full_delta_fp16_bytes"],
            stored["full_delta"]),
        row("uniform_rank32", "factored_patch", uniform_bytes, stored["uniform_rank32"]),
        row("mlp_behemoth_lite", "factored_patch_headline", lite_bytes,
            stored["mlp_behemoth_lite"]),
    ]
    seed_rows = []
    for s in SEEDS:
        ev = evals[f"lora_seed{s}"]
        seed_rows.append(row(f"lora_distilled_seed{s}", "lora_adapter_distilled",
                             adapter_bytes, ev))
    rows.extend(seed_rows)
    lps = [r["mean_target_logprob"] for r in seed_rows]
    gcs = [r["gap_closed"]["overall"] for r in seed_rows]
    adapter_summary = {
        "bytes": adapter_bytes,
        "params": prep["adapter_price"]["params"],
        "rank": 17,
        "placement": "all seven block linears x 24 blocks, no embedding",
        "mean_target_logprob_mean_over_seeds": float(np.mean(lps)),
        "mean_target_logprob_std_over_seeds": float(np.std(lps)),
        "gap_closed_mean_over_seeds": float(np.mean(gcs)),
        "gap_closed_std_over_seeds": float(np.std(gcs)),
        "per_seed": seed_rows,
    }
    rows.append(row("uniform_rank32_noembed", "factored_blocks_only",
                    uniform_bytes - uniform_embed_price, evals["uniform_noembed"],
                    note="embedding delta dropped; priced blocks-only"))
    rows.append(row("mlp_behemoth_lite_noembed", "factored_blocks_only",
                    lite_bytes - lite_embed_price, evals["lite_noembed"],
                    note="embedding delta dropped; priced blocks-only"))
    rows.append(row("lora_seed20261028_fp32", "sensitivity", adapter_bytes,
                    evals["lora_seed20261028_fp32"],
                    note="same adapter scored from fp32-unrounded A/B"))
    rows.append(row("uniform_rank32_vfp16", "sensitivity", uniform_bytes,
                    evals["uniform_vfp16"],
                    note="factored row re-scored with V rounded through fp16"))
    rows.append(row("mlp_behemoth_lite_vfp16", "sensitivity", lite_bytes,
                    evals["lite_vfp16"],
                    note="factored row re-scored with V rounded through fp16"))

    gen_record = json.loads(Path(args.gen_record).read_text())
    train_logs = {s: load(lora_dir, f"train_log_seed{s}.json") for s in SEEDS}

    result = {
        "stage": "lora_baseline_matched_byte_distillation",
        "date": "2026-10-28",
        "design": "results/lora_baseline_design.md (frozen before training; "
                  "pressure-tested by Gemini + Muse Spark, calls logged)",
        "question": "at the factored patches' byte budget on the Qwen2.5-0.5B pair, "
                    "how much of the base-to-full gap does a LoRA adapter distilled "
                    "from the full fine-tune close on the same combined 96?",
        "model_pair": published["model_pair"],
        "probe_set": "combined 96 held-out Spark probes, identical file and scoring "
                     "to results/alien_sweep_heldout96.json",
        "adapter": {
            "form": "LoRA delta_W = B@A, rank 17, all seven block linears x 24 blocks, "
                    "no embedding adapter, alpha 32 folded into B at export",
            "training": "soft KL (forward KL teacher||student, T=1) at teacher-answer "
                        "positions, teacher = full Instruct weights run online; "
                        "1,350 train prompts (450/bucket), 150 val prompts for early "
                        "stopping only; AdamW lr 2e-4 cosine, batch 8, up to 6 epochs",
            "distillation_prompts": "1,500 fresh Muse Spark prompts (500/bucket), "
                                    "novelty-checked vs the 96 eval prompts and the 24 "
                                    "Signet prompts (exact match / Jaccard >= 0.7 rejected), "
                                    "teacher answers are the teacher's own greedy "
                                    "generations; eval prompts/answers never used",
            "price": prep["adapter_price"],
        },
        "verification": verification,
        "script_rerun_of_stored_rows": rerun,
        "table": rows,
        "adapter_summary": adapter_summary,
        "generation_record_summary": {
            "batches": len(gen_record["batches"]),
            "total_prompts": gen_record.get("total_prompts"),
        },
        "prep": prep,
        "training_logs": train_logs,
        "headline_comparison": {
            "adapter_gap_closed_mean": adapter_summary["gap_closed_mean_over_seeds"],
            "adapter_gap_closed_std": adapter_summary["gap_closed_std_over_seeds"],
            "uniform_gap_closed": rerun["uniform_rank32"]["recomputed_gap_closed"],
            "lite_gap_closed": rerun["mlp_behemoth_lite"]["recomputed_gap_closed"],
            "adapter_beats_uniform": bool(np.mean(gcs) > rerun["uniform_rank32"]["recomputed_gap_closed"]),
            "adapter_beats_lite": bool(np.mean(gcs) > rerun["mlp_behemoth_lite"]["recomputed_gap_closed"]),
        },
        "scripts": ["examples/lora_baseline_gen.py", "examples/lora_baseline.py",
                    "examples/lora_baseline_assemble.py"],
    }
    out = Path(args.out)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {out}")
    for r in rows:
        print(f"{r['name']:28s} bytes={r['bytes']:>12,} lp={r['mean_target_logprob']:.4f} "
              f"gap_closed={r['gap_closed']['overall'] if r['gap_closed']['overall'] is not None else float('nan'):.4f}")
    print("verification:", json.dumps(verification, indent=2))
    print("headline:", json.dumps(result["headline_comparison"], indent=2))


if __name__ == "__main__":
    main()
