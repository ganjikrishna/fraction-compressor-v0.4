"""Alien Sweep go/no-go check 3: Stage 1 scores the recipe set by slicing.

    python3 examples/alien_sweep_stage1.py \
        --npz ~/fc-v04-sweep/precompute.npz \
        --recipes results/alien_sweep_check1.json \
        --out ~/fc-v04-sweep/stage1.json

Day-2 check 3 from BUILD_PLAN.md: Stage 1 must score the full recipe
set in minutes via slicing the precomputed factors. For each matrix,
the rank-r truncated-SVD reconstruction error comes straight from the
stored singular values: err^2(r) = ||D||_F^2 - sum_{i<r} s_i^2. A
recipe's score is its total relative Frobenius error across every
matrix the rank map addresses (embedding + all 24 blocks):

    score = sqrt( sum err^2 ) / sqrt( sum ||D||_F^2 )

Lower is better. The human uniform rank-32 recipe is scored on the
same footing for context. Prints and optionally writes a JSON ranking.
"""

import argparse
import json
import time
from pathlib import Path

import numpy as np

BLOCK_NAMES = [
    "attn.q_proj",
    "attn.k_proj",
    "attn.v_proj",
    "attn.o_proj",
    "mlp.gate",
    "mlp.up",
    "mlp.down",
]
N_BLOCKS = 24


def store_keys():
    yield "embed", "embed"
    for i in range(N_BLOCKS):
        for name in BLOCK_NAMES:
            yield f"b{i:02d}_{name.replace('.', '_')}", name


def score_recipe(ranks, data):
    err_sq = 0.0
    tot_sq = 0.0
    for store_key, name in store_keys():
        s = data[f"{store_key}_s"]
        fro = float(data[f"{store_key}_fro"][0])
        r = min(int(ranks[name]), len(s))
        kept = float(np.dot(s[:r], s[:r])) if r else 0.0
        err_sq += max(fro - kept, 0.0)
        tot_sq += fro
    return float(np.sqrt(err_sq / tot_sq)) if tot_sq else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--npz", required=True)
    ap.add_argument("--recipes", required=True, help="alien_sweep_check1.json")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    data = np.load(args.npz)
    check1 = json.loads(Path(args.recipes).read_text())
    recipes = [(r["name"], r["ranks"]) for r in check1["recipes"]]
    human = {name: 32 for name in ["embed"] + BLOCK_NAMES}

    t0 = time.perf_counter()
    scored = [(name, score_recipe(ranks, data)) for name, ranks in recipes]
    human_score = score_recipe(human, data)
    elapsed = time.perf_counter() - t0

    ranking = sorted(
        ({"name": name, "relative_frobenius_error": round(score, 6)} for name, score in scored),
        key=lambda d: d["relative_frobenius_error"],
    )
    result = {
        "check": "alien_sweep_day2_check3_stage1_slicing",
        "n_recipes_scored": len(recipes),
        "scoring_s": round(elapsed, 4),
        "budget": "minutes",
        "verdict": "PASS" if elapsed < 60 else "FAIL",
        "ranking": ranking,
        "human_uniform_rank32": round(human_score, 6),
        "winner": ranking[0]["name"] if ranking else None,
    }
    print(json.dumps(result, indent=2))
    if args.out:
        Path(args.out).write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
