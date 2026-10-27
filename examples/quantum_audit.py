"""Quantum-audited verification pass over the held-out benchmark results.

    python3 examples/quantum_audit.py

What this is
------------
The benchmark's verification pass (BUILD_PLAN: "Quantum component, honest
and bounded") audits a subset of the recorded results instead of trusting
the whole file on sight. The subset is NOT picked by a person or by a
seeded PRNG: it is selected by true quantum random numbers generated on
IBM Quantum hardware and frozen in ``fixtures/qrng_fixture.json`` (see
that file for backend, job id, and how the bytes were produced). No live
quantum call happens here; the fixture is read, never regenerated.

Selection method (deterministic given the fixture)
--------------------------------------------------
The fixture carries 8,192 random bytes (2,048 shots x 32 qubits, 4 bytes
per shot). The held-out file records 24 items (indices 0..23, in file
order: 8 knowledge, 8 instruction, 8 math). Walk the fixture bytes in
order; each byte proposes a candidate index ``byte % 24``; accept it if
it has not been selected already, skip duplicates; stop once 8 distinct
indices are selected. The script records how many bytes were consumed,
so anyone can reproduce the same subset from the fixture by hand.

What is checked
---------------
For each of the three factored configs in ``results/alien_sweep_heldout.json``
(uniform_rank32, mlp_behemoth, mlp_behemoth_lite), recomputed from the
file's own per-item records only:

- the full-set overall and per-bucket mean target logprobs, and the
  first-token accuracies, against the aggregates the file reports;
- for the quantum-selected subset: each item's recorded logprob and
  first-token flag (its contribution), the subset bucket means, and a
  consistency check that subset sum + complement sum reproduces the
  reported full-set mean (this is what ties the selected items to the
  file's headline numbers);
- the reported gap_closed values (overall and per bucket), recomputed
  as (factored - base) / (full - base) from the reported means.

Subset gap_closed is not applicable: the held-out file records per-item
logprobs only for the factored configs, not for base / full_delta, so a
subset-only gap has no reported or recomputable counterpart. That is
stated in the output rather than worked around.

Outputs: ``results/quantum_audit.json`` (full record) and
``results/quantum_audit.log`` (the human-readable run log, identical to
stdout). Pure standard library; no API calls; no quantum jobs.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIXTURE_PATH = ROOT / "fixtures" / "qrng_fixture.json"
HELDOUT_PATH = ROOT / "results" / "alien_sweep_heldout.json"
OUT_PATH = ROOT / "results" / "quantum_audit.json"
LOG_PATH = ROOT / "results" / "quantum_audit.log"
PROBES_PATH = ROOT / "data" / "heldout_probes_spark.json"  # local only, optional

SUBSET_SIZE = 8
TOL = 1e-6  # pass if abs diff <= TOL * max(1, |reported|)

CONFIG_NAMES = ("uniform_rank32", "mlp_behemoth", "mlp_behemoth_lite")
BUCKETS = ("knowledge", "instruction", "math")


def select_indices(random_bytes, n_items, k):
    """Byte-walk selection: byte % n_items, skip duplicates, stop at k."""
    chosen, seen = [], set()
    for consumed, byte in enumerate(random_bytes, start=1):
        idx = byte % n_items
        if idx not in seen:
            seen.add(idx)
            chosen.append(idx)
            if len(chosen) == k:
                return chosen, consumed
    raise ValueError("fixture bytes exhausted before the subset was complete")


def close(a, b):
    return abs(a - b) <= TOL * max(1.0, abs(b))


def main():
    log_lines = []

    def log(msg=""):
        log_lines.append(msg)
        print(msg)

    fixture = json.loads(FIXTURE_PATH.read_text())
    heldout = json.loads(HELDOUT_PATH.read_text())

    random_bytes = bytes.fromhex(fixture["random_bytes_hex"])
    configs = heldout["configs"]
    # Per-item records exist per factored config; all three share the
    # same item order (bucket sequence is asserted identical below).
    ref_items = configs[CONFIG_NAMES[0]]["per_item"]
    n_items = len(ref_items)

    selected, bytes_consumed = select_indices(random_bytes, n_items, SUBSET_SIZE)
    selected_set = set(selected)

    # Optional human-readable labels from the local probe file (gitignored;
    # the audit does not depend on it).
    prompts = None
    if PROBES_PATH.exists():
        probes = json.loads(PROBES_PATH.read_text())
        if isinstance(probes, list) and len(probes) == n_items:
            prompts = [p.get("prompt") for p in probes]

    # Item identities: index, bucket, position within bucket.
    bucket_counts = {}
    items_meta = []
    for i, rec in enumerate(ref_items):
        b = rec["bucket"]
        pos = bucket_counts.get(b, 0)
        bucket_counts[b] = pos + 1
        items_meta.append(
            {
                "index": i,
                "item_id": f"heldout-{i:02d}",
                "bucket": b,
                "position_in_bucket": pos,
            }
        )
    for name in CONFIG_NAMES:
        seq = [r["bucket"] for r in configs[name]["per_item"]]
        assert seq == [m["bucket"] for m in items_meta], f"bucket order differs in {name}"

    checks = []

    def check(name, recomputed, reported):
        ok = close(recomputed, reported)
        checks.append(
            {
                "name": name,
                "recomputed": recomputed,
                "reported": reported,
                "abs_diff": abs(recomputed - reported),
                "pass": ok,
            }
        )
        return ok

    check(
        "fixture_byte_count == shots * qubits / 8",
        float(len(random_bytes)),
        float(fixture["shots"] * fixture["qubits"] // 8),
    )

    shared = heldout["shared_configs"]
    base_means = {
        "overall": shared["base"]["overall"]["mean_target_logprob"],
        **{b: shared["base"]["per_bucket"][b]["mean_target_logprob"] for b in BUCKETS},
    }
    full_means = {
        "overall": shared["full_delta"]["overall"]["mean_target_logprob"],
        **{b: shared["full_delta"]["per_bucket"][b]["mean_target_logprob"] for b in BUCKETS},
    }

    per_config = {}
    for name in CONFIG_NAMES:
        cfg = configs[name]
        items = cfg["per_item"]
        reported_fact = cfg["configs"]["factored_delta"]

        # Full-set recomputation from per-item records.
        for scope, subset in (("overall", items),) + tuple(
            (b, [r for r in items if r["bucket"] == b]) for b in BUCKETS
        ):
            mean_lp = sum(r["logprob"] for r in subset) / len(subset)
            rep = (
                reported_fact["overall"]["mean_target_logprob"]
                if scope == "overall"
                else reported_fact["per_bucket"][scope]["mean_target_logprob"]
            )
            check(f"{name}: full-set {scope} factored mean_target_logprob", mean_lp, rep)
            acc = sum(r["first_token_correct"] for r in subset) / len(subset)
            rep_acc = (
                reported_fact["overall"]["accuracy"]
                if scope == "overall"
                else reported_fact["per_bucket"][scope]["accuracy"]
            )
            check(f"{name}: full-set {scope} factored accuracy", acc, rep_acc)

        # gap_closed recomputed from the reported means vs the file's values.
        for scope in ("overall",) + BUCKETS:
            fact_mean = (
                reported_fact["overall"]["mean_target_logprob"]
                if scope == "overall"
                else reported_fact["per_bucket"][scope]["mean_target_logprob"]
            )
            recomputed_gc = (fact_mean - base_means[scope]) / (full_means[scope] - base_means[scope])
            check(f"{name}: gap_closed {scope}", recomputed_gc, cfg["gap_closed"][scope])

        # Subset records and bucket means (factored logprobs only; the
        # held-out file has no per-item base / full records).
        sel_records = []
        for i in selected:
            rec = items[i]
            sel_records.append(
                {
                    **items_meta[i],
                    "logprob": rec["logprob"],
                    "first_token_correct": rec["first_token_correct"],
                    "contribution_to_full_mean": rec["logprob"] / n_items,
                }
            )
        subset_bucket_means = {}
        for b in BUCKETS:
            vals = [items[i]["logprob"] for i in selected if items[i]["bucket"] == b]
            subset_bucket_means[b] = (sum(vals) / len(vals)) if vals else None
        subset_mean = sum(items[i]["logprob"] for i in selected) / len(selected)

        # Consistency: subset sum + complement sum == reported full-set total.
        subset_sum = sum(items[i]["logprob"] for i in selected)
        complement_sum = sum(
            items[i]["logprob"] for i in range(n_items) if i not in selected_set
        )
        check(
            f"{name}: subset+complement mean reproduces reported overall factored mean",
            (subset_sum + complement_sum) / n_items,
            reported_fact["overall"]["mean_target_logprob"],
        )

        per_config[name] = {
            "selected_items": sel_records,
            "subset_overall_mean_target_logprob": subset_mean,
            "subset_bucket_mean_target_logprob": subset_bucket_means,
            "subset_first_token_accuracy": sum(
                items[i]["first_token_correct"] for i in selected
            )
            / len(selected),
            "subset_gap_closed": None,
            "subset_gap_closed_note": (
                "not applicable: the held-out file records per-item logprobs "
                "only for the factored configs, so there is no per-item base "
                "or full_delta counterpart to form a subset gap from"
            ),
        }

    # Ranking order must match the recomputed full-set factored means.
    recomputed_means = {
        name: sum(r["logprob"] for r in configs[name]["per_item"]) / n_items
        for name in CONFIG_NAMES
    }
    recomputed_order = sorted(CONFIG_NAMES, key=lambda n: -recomputed_means[n])
    reported_order = [r["name"] for r in heldout["ranking_by_heldout_task_score"]]
    ranking_ok = recomputed_order == reported_order
    checks.append(
        {
            "name": "ranking_by_heldout_task_score order matches recomputed factored means",
            "recomputed": recomputed_order,
            "reported": reported_order,
            "abs_diff": None,
            "pass": ranking_ok,
        }
    )

    n_pass = sum(1 for c in checks if c["pass"])
    all_pass = n_pass == len(checks)

    if prompts:
        for cfg_block in per_config.values():
            for rec in cfg_block["selected_items"]:
                rec["prompt"] = prompts[rec["index"]]

    result = {
        "audit": "quantum-audited verification pass over results/alien_sweep_heldout.json",
        "script": "examples/quantum_audit.py",
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "quantum_source": {
            "fixture_file": "fixtures/qrng_fixture.json",
            "backend": fixture["backend"],
            "job_id": fixture["job_id"],
            "qubits": fixture["qubits"],
            "shots": fixture["shots"],
            "qpu_seconds": fixture.get("qpu_seconds"),
            "fixture_generated_at": fixture.get("generated_at"),
            "purpose": fixture.get("purpose"),
            "n_random_bytes": len(random_bytes),
            "note": "frozen fixture from one IBM Quantum job run earlier; no new job was submitted for this audit",
        },
        "selection": {
            "method": (
                "walk the fixture bytes in order; candidate index = byte % 24 "
                "(24 held-out items); accept if not already selected, skip "
                "duplicates; stop at 8 distinct indices"
            ),
            "subset_size": SUBSET_SIZE,
            "total_items": n_items,
            "bytes_consumed": bytes_consumed,
            "selected_indices": selected,
            "selected_items": [
                {
                    **items_meta[i],
                    **({"prompt": prompts[i]} if prompts else {}),
                }
                for i in selected
            ],
        },
        "per_config": per_config,
        "checks": checks,
        "summary": {
            "n_checks": len(checks),
            "n_passed": n_pass,
            "all_pass": all_pass,
            "tolerance": "abs diff <= 1e-6 * max(1, |reported|)",
        },
    }

    OUT_PATH.write_text(json.dumps(result, indent=2) + "\n")

    log("Quantum audit of results/alien_sweep_heldout.json")
    log(
        f"Quantum source: backend {fixture['backend']}, job {fixture['job_id']}, "
        f"{fixture['qubits']} qubits, {fixture['shots']} shots, "
        f"{len(random_bytes)} random bytes (frozen fixture, no new job)"
    )
    log(
        f"Selection: byte % {n_items}, skip duplicates, first {SUBSET_SIZE} distinct "
        f"indices from {bytes_consumed} bytes: {selected}"
    )
    for i in selected:
        m = items_meta[i]
        log(f"  item {m['item_id']}: index {i}, bucket {m['bucket']} (#{m['position_in_bucket']} in bucket)")
    for c in checks:
        status = "PASS" if c["pass"] else "FAIL"
        if isinstance(c["recomputed"], list):
            log(f"[{status}] {c['name']}: recomputed {c['recomputed']} vs reported {c['reported']}")
        else:
            log(
                f"[{status}] {c['name']}: recomputed {c['recomputed']:.12g} "
                f"vs reported {c['reported']:.12g} (abs diff {c['abs_diff']:.3g})"
            )
    log(f"Result: {n_pass}/{len(checks)} checks passed, all_pass={all_pass}")
    log(f"Wrote {OUT_PATH.relative_to(ROOT)} and {LOG_PATH.relative_to(ROOT)}")

    LOG_PATH.write_text("\n".join(log_lines) + "\n")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
