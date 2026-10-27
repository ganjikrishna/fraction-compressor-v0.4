"""Alien Sweep go/no-go check 2: one-time SVD precompute for the target model.

    python3 examples/alien_sweep_precompute.py \
        --base ~/qwen-test/data/qwen2.5-0.5b.safetensors \
        --instruct ~/qwen-test/data/qwen2.5-0.5b-instruct.safetensors \
        --out ~/fc-v04-sweep/precompute.npz

Day-2 check 2 from BUILD_PLAN.md: the one-time SVD precompute for the
target model must finish in under 10 minutes. Technique (adopted from
the Gemini debate): compute the SVD of each base-to-instruct delta
matrix ONCE, up to the max rank any recipe uses for that layer name,
then Stage 1 scores recipes by slicing these stored singular values
instead of re-running an SVD per recipe.

Scope: every matrix the sweep's rank maps address, for the real target
model (Qwen2.5-0.5B base + Instruct safetensors): the embedding plus,
for each of the 24 blocks, attn.q/k/v/o_proj and mlp.gate/up/down_proj.
Per matrix this stores only the top singular values and the squared
Frobenius norm of the full delta, which is all Stage 1 slicing needs:
err^2(rank r) = ||D||_F^2 - sum_{i<r} s_i^2.

The truncated SVD is randomized (fixed seed, oversampling 12, 2 power
iterations), which makes the stored singular values approximate, not
exact; with this oversampling the top values are accurate far beyond
what a Stage 1 filter needs. Deltas are computed one matrix at a time
straight from the safetensors byte ranges, so peak memory stays at
roughly one fp32 matrix (the embedding dominates) plus workspace.

Prints a JSON summary (per-matrix timings, totals) on stdout and saves
the precompute to an .npz: for matrix key K, "<K>_s" holds the singular
values (descending) and "<K>_fro" the squared Frobenius norm.
"""

import argparse
import json
import struct
import sys
import time
from pathlib import Path

import numpy as np

# Recipe layer name -> safetensors key template ({i} = block index).
KEY_TEMPLATES = {
    "embed": "model.embed_tokens.weight",
    "attn.q_proj": "model.layers.{i}.self_attn.q_proj.weight",
    "attn.k_proj": "model.layers.{i}.self_attn.k_proj.weight",
    "attn.v_proj": "model.layers.{i}.self_attn.v_proj.weight",
    "attn.o_proj": "model.layers.{i}.self_attn.o_proj.weight",
    "mlp.gate": "model.layers.{i}.mlp.gate_proj.weight",
    "mlp.up": "model.layers.{i}.mlp.up_proj.weight",
    "mlp.down": "model.layers.{i}.mlp.down_proj.weight",
}
BLOCK_NAMES = [n for n in KEY_TEMPLATES if n != "embed"]
N_BLOCKS = 24

# Singular values stored per layer name: the max rank any check-1
# recipe uses for that name, raised to 32 where the human uniform
# rank-32 baseline needs more (k_proj: recipe max 30, baseline 32).
RANK_STORE = {
    "embed": 80,
    "attn.q_proj": 80,
    "attn.k_proj": 32,
    "attn.v_proj": 40,
    "attn.o_proj": 120,
    "mlp.gate": 45,
    "mlp.up": 45,
    "mlp.down": 50,
}

SEED = 20261027


def load_header(path):
    with open(path, "rb") as f:
        (hlen,) = struct.unpack("<Q", f.read(8))
        header = json.loads(f.read(hlen))
    return header, 8 + hlen


def read_tensor_fp32(path, header, data_start, key):
    """Read one BF16 tensor from a safetensors file as an fp32 array."""
    info = header[key]
    assert info["dtype"] == "BF16", f"{key}: unexpected dtype {info['dtype']}"
    lo, hi = info["data_offsets"]
    with open(path, "rb") as f:
        f.seek(data_start + lo)
        raw = f.read(hi - lo)
    u16 = np.frombuffer(raw, dtype=np.uint16)
    fp32 = (u16.astype(np.uint32) << 16).view(np.float32)
    return fp32.reshape(info["shape"]).copy()


def frobenius_sq(D):
    acc = 0.0
    for chunk in np.array_split(D, 8, axis=0):
        acc += float((chunk * chunk).sum(dtype=np.float64))
    return acc


def rsvd_singular_values(D, r, seed, oversample=12, power=2):
    """Top-r singular values of D via randomized SVD (fixed seed)."""
    m, n = D.shape
    r = min(r, min(m, n))
    rng = np.random.default_rng(seed)
    omega = rng.standard_normal((n, r + oversample), dtype=np.float32)
    Y = D @ omega
    for _ in range(power):
        Y, _ = np.linalg.qr(Y)
        Y = D @ (D.T @ Y)
    Q, _ = np.linalg.qr(Y)
    B = Q.T @ D
    s = np.linalg.svd(B, compute_uv=False)
    return s[:r].astype(np.float64)


def matrix_keys():
    yield "embed", KEY_TEMPLATES["embed"], "embed"
    for i in range(N_BLOCKS):
        for name in BLOCK_NAMES:
            yield f"b{i:02d}_{name.replace('.', '_')}", KEY_TEMPLATES[name].format(i=i), name


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True)
    ap.add_argument("--instruct", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    base_hdr, base_off = load_header(args.base)
    ins_hdr, ins_off = load_header(args.instruct)

    store = {}
    per_matrix = []
    t_all = time.perf_counter()
    for idx, (store_key, hf_key, name) in enumerate(matrix_keys()):
        t0 = time.perf_counter()
        W_base = read_tensor_fp32(args.base, base_hdr, base_off, hf_key)
        W_ins = read_tensor_fp32(args.instruct, ins_hdr, ins_off, hf_key)
        D = W_ins - W_base
        del W_base, W_ins
        fro = frobenius_sq(D)
        t_delta = time.perf_counter()
        s = rsvd_singular_values(D, RANK_STORE[name], seed=SEED + idx)
        shape = list(D.shape)
        del D
        t_done = time.perf_counter()
        store[f"{store_key}_s"] = s
        store[f"{store_key}_fro"] = np.array([fro])
        per_matrix.append(
            {
                "key": store_key,
                "layer_name": name,
                "hf_key": hf_key,
                "shape": shape,
                "rank_stored": int(len(s)),
                "delta_s": round(t_delta - t0, 3),
                "svd_s": round(t_done - t_delta, 3),
                "total_s": round(t_done - t0, 3),
            }
        )
        print(f"{store_key}: shape={shape} r={len(s)} {t_done - t0:.2f}s", file=sys.stderr)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, **store)
    total_s = time.perf_counter() - t_all
    summary = {
        "check": "alien_sweep_day2_check2_svd_precompute",
        "n_matrices": len(per_matrix),
        "total_s": round(total_s, 2),
        "budget_s": 600,
        "verdict": "PASS" if total_s < 600 else "FAIL",
        "method": "randomized SVD, fp32, oversampling 12, 2 power iterations, seed 20261027",
        "per_matrix": per_matrix,
        "npz": str(out),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
