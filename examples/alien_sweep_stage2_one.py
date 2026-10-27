"""Alien Sweep go/no-go check 4: one Stage 2 config through src/bench.py.

    python3 examples/alien_sweep_stage2_one.py \
        --base ~/qwen-test/data/qwen2.5-0.5b.safetensors \
        --instruct ~/qwen-test/data/qwen2.5-0.5b-instruct.safetensors \
        --recipes alien_sweep_check1.json --recipe <stage1 winner>

Day-2 check 4 from BUILD_PLAN.md: one Stage 2 config must complete
the end-to-end task benchmark inside the agreed time budget without
memory thrash on Flash. Applied thresholds: under 10 minutes wall and
under 6 GB peak RSS (the standing Flash memory lesson).

What runs here is the benchmark harness (src/bench.py) fed with REAL
delta matrices: one transformer block (block 12, the middle block) of
Qwen2.5-0.5B base/Instruct, chained in the harness's (in, out)
orientation as attn.q_proj -> attn.o_proj -> mlp.gate -> mlp.down,
with the winning recipe's ranks for those four layer names. Probes are
synthetic harness probes (fixed seed): inputs are standard normal
vectors and each target is the argmax logit of the full-delta config,
the same teacher construction as bench.py's own smoke test; bucket
labels cycle knowledge/instruction/math. This gates feasibility of a
Stage 2 config (real matrices, real ranks, real quantization cost) —
the full Stage 2 runs the actual probe sets against the model later.
Prints a JSON summary including wall time and peak RSS.
"""

import argparse
import json
import resource
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
for cand in (HERE, HERE.parent / "src", HERE.parent / "examples"):
    if (cand / "factored.py").exists() and str(cand) not in sys.path:
        sys.path.insert(0, str(cand))
    if (cand / "alien_sweep_precompute.py").exists() and str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

import bench  # noqa: E402
from alien_sweep_precompute import load_header, read_tensor_fp32  # noqa: E402

CHAIN = [  # (recipe name, hf key infix) in harness stack order
    ("attn.q_proj", "self_attn.q_proj.weight"),
    ("attn.o_proj", "self_attn.o_proj.weight"),
    ("mlp.gate", "mlp.gate_proj.weight"),
    ("mlp.down", "mlp.down_proj.weight"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True)
    ap.add_argument("--instruct", required=True)
    ap.add_argument("--recipes", required=True)
    ap.add_argument("--recipe", required=True, help="winning recipe name from Stage 1")
    ap.add_argument("--block", type=int, default=12)
    ap.add_argument("--n-probes", type=int, default=120)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    recipes = {r["name"]: r["ranks"] for r in json.loads(Path(args.recipes).read_text())["recipes"]}
    ranks = recipes[args.recipe]

    base_hdr, base_off = load_header(args.base)
    ins_hdr, ins_off = load_header(args.instruct)

    layers, deltas, rank_map = [], {}, {}
    for name, infix in CHAIN:
        key = f"model.layers.{args.block}.{infix}"
        Wb = read_tensor_fp32(args.base, base_hdr, base_off, key)
        Wi = read_tensor_fp32(args.instruct, ins_hdr, ins_off, key)
        layers.append((name, np.ascontiguousarray(Wb.T)))  # HF (out,in) -> harness (in,out)
        deltas[name] = np.ascontiguousarray((Wi - Wb).T)
        rank_map[name] = int(ranks[name])
        del Wb, Wi

    base_W = [W for _, W in layers]
    full_W = [base_W[i] + deltas[name] for i, (name, _) in enumerate(layers)]

    rng = np.random.default_rng(7)
    buckets = ["knowledge", "instruction", "math"]
    d_in = layers[0][1].shape[0]
    probes = []
    for i in range(args.n_probes):
        x = rng.standard_normal(d_in)
        target = int(np.argmax(bench._forward_stack(full_W, x)))
        probes.append(
            {"id": f"stage2-{i:03d}", "bucket": buckets[i % 3], "x": x.tolist(), "target": target}
        )

    t0 = time.perf_counter()
    results = bench.run_benchmark(layers, deltas, rank_map, probes)
    wall_s = time.perf_counter() - t0
    peak_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

    summary = {
        "check": "alien_sweep_day2_check4_stage2_one_config",
        "recipe": args.recipe,
        "block": args.block,
        "chain": [name for name, _ in CHAIN],
        "rank_map": results["rank_map"],
        "n_probes": results["n_probes"],
        "wall_s": round(wall_s, 2),
        "peak_rss_mb": round(peak_mb, 1),
        "budget": {"wall_s_max": 600, "peak_rss_mb_max": 6144},
        "verdict": "PASS" if wall_s < 600 and peak_mb < 6144 else "FAIL",
        "configs": {
            k: {
                "accuracy": round(v["accuracy"], 4),
                "mean_target_logprob": round(v["mean_target_logprob"], 4),
            }
            for k, v in results["configs"].items()
        },
        "gap_closed": results["gap_closed"],
        "sizes": results["sizes"],
    }
    print(json.dumps(summary, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
