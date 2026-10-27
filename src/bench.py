"""End-to-end task benchmark for factored 1-bit deltas.

    python3 src/bench.py --smoke --out results/smoke_bench.json

Needs only numpy. The benchmark scores three configurations of the same
model on the same probe tasks, so the compressed path is judged on task
answers, not only on weight error:

- ``base``           the base model, no delta applied
- ``full_delta``     base + the full fine-tune delta, applied densely
- ``factored_delta`` base + the delta in factored 1-bit form (per-layer
  ranks from a rank map), applied as ``(X @ U) @ V.T`` per layer and
  never materialized

A model here is a stack of named linear layers with a tanh nonlinearity
between layers. A probe task is one input vector plus the index of the
correct output logit; scoring is argmax accuracy plus the mean
log-probability of the correct logit (the logprob view matches how the
pre-existing Signet probes were scored). Results are reported overall
and per bucket (knowledge / instruction / math / ...), together with a
Signet-style "gap closed" number: how much of the base-to-full logprob
gap the factored delta recovers.

Probe files are JSON: a list of {"id", "bucket", "x", "target"} items.
Real runs load model weights and Spark-generated probes through the same
:func:`run_benchmark` entry point this file's smoke test exercises.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from factored import apply_factored, quantize_delta, storage_bytes  # noqa: E402

CONFIGS = ("base", "full_delta", "factored_delta")


def _log_softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - np.max(logits)
    return z - np.log(np.sum(np.exp(z)))


def _forward_stack(layers_W, x, extra=None):
    """Forward pass for one input vector.

    ``extra`` optionally maps layer index -> callable(h_in) -> contribution
    added to that layer's output before the nonlinearity. Used by the
    factored config so the delta contribution is computed as
    ``(h_in @ U) @ V.T`` without ever forming the full delta matrix.
    """
    h = np.asarray(x, dtype=np.float64)
    last = len(layers_W) - 1
    for i, W in enumerate(layers_W):
        h_in = h
        h = h_in @ W
        if extra is not None and i in extra:
            h = h + extra[i](h_in)
        if i < last:
            h = np.tanh(h)
    return h


def _score(logits_fn, probes):
    """Score a logits function over probes: accuracy + mean target logprob."""
    per_bucket = {}
    correct = 0
    lp_sum = 0.0
    for p in probes:
        logits = logits_fn(np.asarray(p["x"], dtype=np.float64))
        target = int(p["target"])
        hit = int(np.argmax(logits) == target)
        lp = float(_log_softmax(logits)[target])
        correct += hit
        lp_sum += lp
        b = per_bucket.setdefault(p.get("bucket", "unknown"), {"n": 0, "correct": 0, "logprob": 0.0})
        b["n"] += 1
        b["correct"] += hit
        b["logprob"] += lp
    n = len(probes)
    return {
        "accuracy": correct / n if n else 0.0,
        "mean_target_logprob": lp_sum / n if n else 0.0,
        "per_bucket": {
            name: {
                "n": b["n"],
                "accuracy": b["correct"] / b["n"],
                "mean_target_logprob": b["logprob"] / b["n"],
            }
            for name, b in sorted(per_bucket.items())
        },
    }


def run_benchmark(layers, deltas, rank_map, probes):
    """Score base vs full delta vs factored delta on the same probes.

    layers:   list of (name, W) with W of shape (in, out)
    deltas:   dict name -> full delta matrix (missing layers mean no delta)
    rank_map: dict name -> rank for the factored config (default 32)
    probes:   list of {"id", "bucket", "x", "target"}
    """
    names = [name for name, _ in layers]
    base_W = [np.asarray(W, dtype=np.float64) for _, W in layers]
    full_W = [
        base_W[i] + np.asarray(deltas[name], dtype=np.float64)
        if name in deltas else base_W[i]
        for i, name in enumerate(names)
    ]

    factored_extra = {}
    factored_bytes = 0
    effective_ranks = {}
    for i, name in enumerate(names):
        if name not in deltas:
            continue
        D = np.asarray(deltas[name], dtype=np.float64)
        # A rank cannot exceed the smaller dimension; clamp and record
        # the effective rank so small layers are reported honestly.
        rank = min(int(rank_map.get(name, 32)), min(D.shape))
        effective_ranks[name] = rank
        q = quantize_delta(D, rank)
        U, V = q["U"], q["V"]
        factored_extra[i] = (lambda U, V: lambda h: apply_factored(h, U, V))(U, V)
        factored_bytes += storage_bytes(rank, D.shape)

    full_bytes = sum(
        2 * np.asarray(deltas[name]).size for name in names if name in deltas
    )

    results = {
        "n_probes": len(probes),
        "layers": names,
        "rank_map": effective_ranks,
        "sizes": {
            "full_delta_fp16_bytes": int(full_bytes),
            "factored_bytes": int(factored_bytes),
            "compression_ratio": (full_bytes / factored_bytes) if factored_bytes else None,
        },
        "configs": {
            "base": _score(lambda x: _forward_stack(base_W, x), probes),
            "full_delta": _score(lambda x: _forward_stack(full_W, x), probes),
            "factored_delta": _score(
                lambda x: _forward_stack(base_W, x, extra=factored_extra), probes
            ),
        },
    }

    base_lp = results["configs"]["base"]["mean_target_logprob"]
    full_lp = results["configs"]["full_delta"]["mean_target_logprob"]
    fact_lp = results["configs"]["factored_delta"]["mean_target_logprob"]
    gap = full_lp - base_lp
    results["gap_closed"] = (fact_lp - base_lp) / gap if gap > 1e-12 else None
    return results


def load_probes(path):
    """Load probe tasks from a JSON file (list of id/bucket/x/target)."""
    with open(path) as f:
        probes = json.load(f)
    for p in probes:
        if "x" not in p or "target" not in p:
            raise ValueError(f"probe missing x/target: {p.get('id', '?')}")
    return probes


def synthetic_smoke(seed=0, n_probes=120):
    """A self-contained end-to-end check with synthetic matrices.

    A teacher matrix defines the probe answers. The full delta turns the
    base model's output layer into the teacher (so full_delta must score
    perfectly by construction), the base model starts from a random
    output layer, and the factored delta has to recover as much of the
    teacher as its rank allows. No downloads, no API calls.
    """
    rng = np.random.default_rng(seed)
    d_in, d_hidden, d_out = 24, 32, 10

    W0 = rng.standard_normal((d_in, d_hidden)) * 0.3
    D0 = (rng.standard_normal((d_in, 4)) @ rng.standard_normal((4, d_hidden))) * 0.05
    teacher = rng.standard_normal((d_hidden, d_out)) * 0.8
    W1_base = rng.standard_normal((d_hidden, d_out)) * 0.3
    D1 = teacher - W1_base

    layers = [("layer0", W0), ("layer1", W1_base)]
    deltas = {"layer0": D0, "layer1": D1}
    rank_map = {"layer0": 8, "layer1": 8}

    buckets = ["knowledge", "instruction", "math"]
    probes = []
    for i in range(n_probes):
        x = rng.standard_normal(d_in)
        hidden = np.tanh(x @ (W0 + D0))
        target = int(np.argmax(hidden @ teacher))
        probes.append(
            {"id": f"smoke-{i:03d}", "bucket": buckets[i % 3], "x": x.tolist(), "target": target}
        )

    return run_benchmark(layers, deltas, rank_map, probes)


def _print_table(results):
    print(f"probes: {results['n_probes']}   layers: {', '.join(results['layers'])}")
    print(f"{'config':<16} {'accuracy':>9} {'mean logprob':>13}")
    for name in CONFIGS:
        c = results["configs"][name]
        print(f"{name:<16} {c['accuracy']:>9.3f} {c['mean_target_logprob']:>13.3f}")
    s = results["sizes"]
    print(
        f"sizes: full fp16 {s['full_delta_fp16_bytes']:,} B vs factored "
        f"{s['factored_bytes']:,} B ({s['compression_ratio']:.1f}x smaller)"
    )
    gc = results["gap_closed"]
    print(f"gap closed by factored delta: {gc:.3f}" if gc is not None else "gap closed: n/a")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--smoke", action="store_true", help="run the synthetic smoke benchmark")
    ap.add_argument("--out", default=None, help="write the results JSON to this path")
    args = ap.parse_args()

    if not args.smoke:
        ap.error("only --smoke mode is wired up so far; real runs call run_benchmark()")

    results = synthetic_smoke()
    _print_table(results)
    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(results, indent=2) + "\n")
        print(f"wrote {out}")
    # Smoke invariants: the harness only passes if the full delta (which
    # encodes the teacher by construction) scores perfectly and the
    # factored delta lands strictly between base and full on accuracy.
    acc = {k: v["accuracy"] for k, v in results["configs"].items()}
    assert acc["full_delta"] == 1.0, f"smoke: full delta accuracy {acc['full_delta']} != 1.0"
    assert acc["base"] < acc["factored_delta"] <= acc["full_delta"], (
        f"smoke: expected base < factored <= full, got {acc}"
    )
    print("SMOKE OK")


if __name__ == "__main__":
    main()
