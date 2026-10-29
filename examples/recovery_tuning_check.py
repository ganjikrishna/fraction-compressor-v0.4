"""Independent recomputation for the recovery tuning result.

Deliberately shares no scoring code with the eval pipeline: it reads only
stored per-item rows (logprob, first_token_correct) from the eval JSON
files and recomputes every aggregate, gap-closed value, and comparison
that results/recovery_tuning.json reports. It also re-prices the
re-quantized factors file from its array shapes with the storage formula
written out here, and checks the eval machinery by comparing a fresh
re-score of the untouched lite factors against the originally stored
lite eval, item by item.

Inputs (Flash paths in the run; assembled JSON is written locally):
  --heldout96-workdir  stored eval_base / eval_full_delta /
                       eval_uniform_rank32 / eval_mlp_behemoth_lite JSONs
  --workdir            recovery tuning workdir (eval_*.json for both
                       tags lite_rt and ctrl_rt, requant_record_<tag>.json,
                       train_log_<tag>.json, factors npz files)
  --lora-json          results/lora_baseline.json (context row)
  --out                where to write results/recovery_tuning.json
"""

import argparse
import json
from pathlib import Path

import numpy as np

LITE_BYTES = 19358176


def mean_lp(rows):
    return sum(r["logprob"] for r in rows) / len(rows)


def acc(rows):
    return sum(r["first_token_correct"] for r in rows) / len(rows)


def bucket_block(rows):
    out = {}
    for b in ("knowledge", "instruction", "math"):
        rs = [r for r in rows if r["bucket"] == b]
        if rs:
            out[b] = {"n": len(rs), "mean_target_logprob": mean_lp(rs),
                      "accuracy": acc(rs)}
    return out


def split_block(rows):
    """First-token vs continuation split from extended per-item fields."""
    if not rows or "first_token_logprob" not in rows[0]:
        return None
    cont_num = sum(r["logprob"] - r["first_token_logprob"]
                   for r in rows if r["n_answer_tokens"] >= 2)
    cont_den = sum(r["n_answer_tokens"] - 1
                   for r in rows if r["n_answer_tokens"] >= 2)
    return {
        "first_token_mean_logprob": sum(r["first_token_logprob"] for r in rows) / len(rows),
        "continuation_mean_logprob_per_token": cont_num / cont_den if cont_den else 0.0,
        "n_continuation_tokens": int(cont_den),
    }


def row_from_eval(ev, base_lp, full_lp, extra_fields_from=None):
    rows = ev["per_item"]
    lp = mean_lp(rows)
    row = {
        "n": len(rows),
        "mean_target_logprob": lp,
        "gap_closed": (lp - base_lp) / (full_lp - base_lp),
        "first_token_accuracy": acc(rows),
        "per_bucket": bucket_block(rows),
    }
    sp = split_block(rows)
    if sp:
        row["first_token_vs_continuation"] = sp
    return row


def price_from_npz(path):
    """Storage price from array shapes only, formula written out here:
    per matrix, ceil(m * rank / 8) sign bytes + 4 * m scale bytes
    + 2 * n * rank fp16 V bytes; rank-0 matrices (absent from the file)
    are priced by the caller through the rank map, not here."""
    fac = np.load(path)
    total = 0
    mats = 0
    for k in fac.files:
        if k.endswith("_U"):
            sk = k[:-2]
            U, V = fac[k], fac[f"{sk}_V"]
            m, rank = U.shape
            n = V.shape[0]
            total += (m * rank + 7) // 8 + 4 * m + 2 * n * rank
            mats += 1
    return total, mats


def byte_check(wd, header, tag):
    """Cross-verify one tag's re-quantized byte count three ways: stored
    matrices repriced from npz shapes; the requant pricing table sums to
    the target with shapes matching the base header, ranks matching the
    npz, stored flags matching the npz; stored price + rank-0 table rows
    equals the target."""
    stored_price, n_mats = price_from_npz(wd / f"factors_{tag}_requant.npz")
    rec = json.loads((wd / f"requant_record_{tag}.json").read_text())
    fac_q = np.load(wd / f"factors_{tag}_requant.npz")
    table = rec["pricing_table"]
    table_sum = sum(r["bytes"] for r in table)
    shape_ok = all(tuple(header[r["hf_key"]]["shape"]) == tuple(r["shape"])
                   for r in table)
    rank_ok = True
    stored_ok = True
    for r in table:
        present = f"{r['store_key']}_U" in fac_q.files
        if present != r["stored"]:
            stored_ok = False
        if present and fac_q[f"{r['store_key']}_U"].shape[1] != r["rank"]:
            rank_ok = False
        if not present and r["rank"] != 0:
            rank_ok = False
    rank0_bytes = sum(r["bytes"] for r in table if not r["stored"])
    return rec, {
        "stored_matrices_priced_from_shapes": int(stored_price),
        "n_stored_matrices": int(n_mats),
        "rank0_bytes_from_table": int(rank0_bytes),
        "pricing_table_sum": int(table_sum),
        "table_shapes_match_header": bool(shape_ok),
        "table_ranks_match_npz": bool(rank_ok),
        "table_stored_flags_match_npz": bool(stored_ok),
        "target": LITE_BYTES,
        "pass": bool(table_sum == LITE_BYTES
                     and stored_price + rank0_bytes == LITE_BYTES
                     and shape_ok and rank_ok and stored_ok
                     and rec["bytes_match"]),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--heldout96-workdir", required=True)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--lora-json", required=True)
    ap.add_argument("--base-header", required=True,
                    help="base safetensors path, for rank-0 matrix shapes")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    h96 = Path(args.heldout96_workdir)
    wd = Path(args.workdir)
    ev = {name: json.loads((h96 / f"eval_{name}.json").read_text())
          for name in ("base", "full_delta", "uniform_rank32", "mlp_behemoth_lite")}
    base_lp = mean_lp(ev["base"]["per_item"])
    full_lp = mean_lp(ev["full_delta"]["per_item"])

    checks = {}

    # Machinery check: fresh re-score of untouched lite vs stored lite.
    fresh_lite = json.loads((wd / "eval_lite_check.json").read_text())
    stored_rows = ev["mlp_behemoth_lite"]["per_item"]
    fresh_rows = fresh_lite["per_item"]
    assert len(stored_rows) == len(fresh_rows) == 96
    diffs = [abs(a["logprob"] - b["logprob"])
             for a, b in zip(stored_rows, fresh_rows)]
    ft_same = all(a["first_token_correct"] == b["first_token_correct"]
                  for a, b in zip(stored_rows, fresh_rows))
    checks["eval_machinery_lite_rescore"] = {
        "max_abs_per_item_logprob_diff": max(diffs),
        "first_token_flags_identical": bool(ft_same),
        "pass": bool(max(diffs) < 1e-6 and ft_same),
    }

    # Byte checks for both re-quantized files (headline and control).
    import struct
    with open(args.base_header, "rb") as f:
        (hlen,) = struct.unpack("<Q", f.read(8))
        header = json.loads(f.read(hlen))
    recs = {}
    for tag in ("lite_rt", "ctrl_rt"):
        recs[tag], checks[f"byte_count_{tag}"] = byte_check(wd, header, tag)

    rows = {
        "base": row_from_eval(ev["base"], base_lp, full_lp),
        "full_fine_tune": row_from_eval(ev["full_delta"], base_lp, full_lp),
        "uniform_rank32": row_from_eval(ev["uniform_rank32"], base_lp, full_lp),
        "lite_untouched": row_from_eval(ev["mlp_behemoth_lite"], base_lp, full_lp),
    }
    rq = json.loads((wd / "eval_lite_rt_requant.json").read_text())
    rows["lite_recovery_tuned_requantized"] = row_from_eval(rq, base_lp, full_lp)
    fp = json.loads((wd / "eval_lite_rt_fp16.json").read_text())
    rows["lite_recovery_tuned_fp16_diagnostic"] = row_from_eval(fp, base_lp, full_lp)
    cq = json.loads((wd / "eval_ctrl_rt_requant.json").read_text())
    rows["control_recovery_tuned_requantized"] = row_from_eval(cq, base_lp, full_lp)
    cf = json.loads((wd / "eval_ctrl_rt_fp16.json").read_text())
    rows["control_recovery_tuned_fp16_diagnostic"] = row_from_eval(cf, base_lp, full_lp)

    lora = json.loads(Path(args.lora_json).read_text())
    train_logs = {tag: json.loads((wd / f"train_log_{tag}.json").read_text())
                  for tag in ("lite_rt", "ctrl_rt")}

    lite_gc = rows["lite_untouched"]["gap_closed"]
    rq_gc = rows["lite_recovery_tuned_requantized"]["gap_closed"]
    fp_gc = rows["lite_recovery_tuned_fp16_diagnostic"]["gap_closed"]
    cq_gc = rows["control_recovery_tuned_requantized"]["gap_closed"]
    cf_gc = rows["control_recovery_tuned_fp16_diagnostic"]["gap_closed"]
    out = {
        "stage": "recovery_tuning_pilot",
        "date": "2026-10-29",
        "pilot": "one seed (20261028); no training-cost claim is drawn "
                 "from this pilot alone (panel amendment, "
                 "results/lora_result_discussion.md)",
        "design": "results/recovery_tuning_design.md (frozen before "
                  "training, panel amendment included)",
        "question": "does a 101-step training pass initialized from the "
                    "shipped lite factored patch beat the same 101-step "
                    "pass from a random/zero start, after both are "
                    "re-quantized into the same 1-bit factored format at "
                    "the same byte count?",
        "model_pair": "Qwen2.5-0.5B base / Qwen2.5-0.5B-Instruct",
        "probe_set": "combined 96 held-out Spark probes, identical file and "
                     "scoring to results/alien_sweep_heldout96.json",
        "reference_gap": {"base_mean_logprob": base_lp,
                          "full_mean_logprob": full_lp,
                          "gap_nats": full_lp - base_lp},
        "training": {
            tag: {
                "init": train_logs[tag]["init"],
                "steps": train_logs[tag]["steps_run"],
                "lr": train_logs[tag]["lr"],
                "batch": train_logs[tag]["batch"],
                "seed": train_logs[tag]["seed"],
                "wall_s": train_logs[tag]["wall_s"],
                "peak_rss_mb": train_logs[tag]["peak_rss_mb"],
                "val_kl_checks": train_logs[tag]["val_checks"],
                "val_kl_curve_subset30": train_logs[tag]["val_curve"],
                "forward_validation": train_logs[tag]["forward_validation"],
            } for tag in ("lite_rt", "ctrl_rt")
        },
        "requant": {tag: {k: recs[tag][k] for k in
                          ("bytes_requantized", "bytes_match",
                           "fp16_diagnostic_bytes",
                           "rel_frobenius_err_mean", "rel_frobenius_err_max",
                           "wall_s")}
                    for tag in ("lite_rt", "ctrl_rt")},
        "rows": rows,
        "lora_context": {
            "adapter_mean_gap_closed": lora["adapter_summary"]["gap_closed_mean_over_seeds"],
            "adapter_mean_logprob": lora["adapter_summary"]["mean_target_logprob_mean_over_seeds"],
            "adapter_bytes": lora["adapter_summary"]["bytes"],
            "note": "context only, not like-for-like: the adapter used a "
                    "different parameterization, 1,014 steps per seed, and "
                    "an 18.7 MB fp16 price against the tuned factors' "
                    "43.4 MB fp16 diagnostic price",
        },
        "headline": {
            "comparison": "patch-init re-quantized vs control-init "
                          "re-quantized, identical bytes (19,358,176 B)",
            "lite_untouched_gap_closed": lite_gc,
            "patch_init_requantized_gap_closed": rq_gc,
            "control_init_requantized_gap_closed": cq_gc,
            "patch_init_advantage_over_control": rq_gc - cq_gc,
            "patch_init_gain_over_lite": rq_gc - lite_gc,
            "control_init_gain_over_lite": cq_gc - lite_gc,
            "patch_init_fp16_diagnostic_gap_closed": fp_gc,
            "control_init_fp16_diagnostic_gap_closed": cf_gc,
            "share_of_patch_fp16_gain_surviving_requantization": (
                (rq_gc - lite_gc) / (fp_gc - lite_gc) if fp_gc > lite_gc else None),
        },
        "checks": checks,
        "scripts": ["examples/recovery_tuning.py",
                    "examples/recovery_tuning_check.py"],
    }
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"checks": checks, "headline": out["headline"]}, indent=2))


if __name__ == "__main__":
    main()
