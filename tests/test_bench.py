"""Plain-assert tests for src/bench.py. Run: python3 tests/test_bench.py"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from bench import run_benchmark, synthetic_smoke  # noqa: E402


def test_smoke_ordering():
    r = synthetic_smoke(seed=0)
    acc = {k: v["accuracy"] for k, v in r["configs"].items()}
    assert acc["full_delta"] == 1.0, f"teacher construction must be exact, got {acc}"
    assert acc["base"] < acc["factored_delta"] <= acc["full_delta"], acc
    print(f"  smoke ordering: base {acc['base']:.3f} < factored "
          f"{acc['factored_delta']:.3f} <= full {acc['full_delta']:.3f}")


def test_scores_bounded_and_buckets():
    r = synthetic_smoke(seed=1, n_probes=30)
    assert r["n_probes"] == 30
    for name, c in r["configs"].items():
        assert 0.0 <= c["accuracy"] <= 1.0, (name, c["accuracy"])
        assert c["mean_target_logprob"] <= 0.0, (name, c["mean_target_logprob"])
        assert sum(b["n"] for b in c["per_bucket"].values()) == 30
    print("  accuracies in [0,1], logprobs <= 0, bucket counts sum to n_probes")


def test_zero_rank_map_defaults_and_sizes():
    rng = np.random.default_rng(7)
    W = rng.standard_normal((16, 12)) * 0.3
    D = rng.standard_normal((16, 12)) * 0.1
    probes = [
        {"id": "p0", "bucket": "knowledge",
         "x": rng.standard_normal(16).tolist(), "target": 0}
    ]
    r = run_benchmark([("only", W)], {"only": D}, {}, probes)
    s = r["sizes"]
    assert s["full_delta_fp16_bytes"] == 2 * 16 * 12
    assert 0 < s["factored_bytes"] < s["full_delta_fp16_bytes"], s
    # Default rank 32 exceeds min(16, 12); the harness clamps to the
    # layer's max rank and records the effective rank.
    assert r["rank_map"] == {"only": 12}, r["rank_map"]
    print(f"  sizes: factored {s['factored_bytes']} B < full {s['full_delta_fp16_bytes']} B, "
          f"rank clamped to effective 12 and recorded")


def test_gap_closed_definition():
    r = synthetic_smoke(seed=2)
    base = r["configs"]["base"]["mean_target_logprob"]
    full = r["configs"]["full_delta"]["mean_target_logprob"]
    fact = r["configs"]["factored_delta"]["mean_target_logprob"]
    expect = (fact - base) / (full - base)
    assert abs(r["gap_closed"] - expect) < 1e-12
    assert 0.0 < r["gap_closed"] < 1.0, r["gap_closed"]
    print(f"  gap_closed {r['gap_closed']:.3f} matches its definition and is in (0,1)")


def test_no_delta_layers_match_base():
    rng = np.random.default_rng(11)
    W = rng.standard_normal((8, 6)) * 0.3
    probes = [
        {"id": "p0", "bucket": "math",
         "x": rng.standard_normal(8).tolist(), "target": 1}
    ]
    r = run_benchmark([("a", W)], {}, {}, probes)
    assert r["configs"]["base"] == r["configs"]["full_delta"] == r["configs"]["factored_delta"]
    assert r["gap_closed"] is None
    print("  with no deltas all three configs agree and gap_closed is None")


def main():
    tests = [
        test_smoke_ordering,
        test_scores_bounded_and_buckets,
        test_zero_rank_map_defaults_and_sizes,
        test_gap_closed_definition,
        test_no_delta_layers_match_base,
    ]
    for t in tests:
        print(t.__name__)
        t()
    print("PASS")


if __name__ == "__main__":
    main()
