"""Fourth pair (Qwen2.5-1.5B): one-time SVD precompute for the sweep.

    python3 examples/fourth_pair_precompute.py \
        --base ~/qwen15-test/data/base/model.safetensors \
        --instruct ~/qwen15-test/data/instruct/model.safetensors \
        --out ~/fc-v04-sweep4/precompute.npz

Scale test (Vinay, Oct 28): the Alien Sweep protocol rerun on a
fourth, larger model pair, Qwen/Qwen2.5-1.5B base / Instruct
(Apache 2.0, non-gated), to answer the fresh-eyes review question
"does any of this survive above 1B parameters?" (see
results/fresh_perspective.md). This is third_pair_precompute.py
adapted to the pair: the block count and matrix shapes are read from
the model files' own tensor names (28 blocks; embed 151936x1536; attn q/o 1536x1536, k/v 256x1536;
mlp gate/up 8960x1536, down 1536x8960), not assumed from the other
pairs. 197 delta matrices in total (embed + 7 per block;
Qwen2.5-1.5B ties its embeddings per its config.json, and the
safetensors files carry no lm_head.weight tensor, so the embedding
doubles as the LM head exactly as on the Llama pair).

Method is unchanged: randomized SVD (fixed seed, oversampling 12, 2
power iterations) of each base-to-instruct delta, one matrix at a
time; per matrix only the top singular values and the squared
Frobenius norm are stored, which is all Stage 1 slicing needs:
err^2(rank r) = ||D||_F^2 - sum_{i<r} s_i^2. Singular values are
stored up to --rank-store per matrix (default 192, clamped to the
matrix's smaller dimension); if a generated recipe ever asks for
more, Stage 1 reports the clamp and the precompute is rerun with a
larger store before Stage 2 (Stage 2 itself uses exact SVDs and is
unaffected).

RAM note: the embedding delta is 151936x1536 (0.93 GB in fp32).
The randomized SVD only ever multiplies it by thin matrices
(1536 x ~204), so peak memory stays at the two weight tensors plus
the delta themselves (~2.8 GB while that delta is formed, ~1.2 GB
during its SVD), inside the ~6 GB cap. No chunking was needed.
"""

import argparse
import json
import struct
import sys
import time
from pathlib import Path

import numpy as np

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

SEED = 20261028


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


def n_blocks(header):
    idx = set()
    for k in header:
        parts = k.split(".")
        if len(parts) > 2 and parts[0] == "model" and parts[1] == "layers":
            idx.add(int(parts[2]))
    return max(idx) + 1 if idx else 0


def matrix_keys(nblocks):
    yield "embed", KEY_TEMPLATES["embed"], "embed"
    for i in range(nblocks):
        for name in BLOCK_NAMES:
            yield f"b{i:02d}_{name.replace('.', '_')}", KEY_TEMPLATES[name].format(i=i), name


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


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--base", required=True)
    ap.add_argument("--instruct", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rank-store", type=int, default=192)
    args = ap.parse_args()

    base_hdr, base_off = load_header(args.base)
    ins_hdr, ins_off = load_header(args.instruct)
    nb = n_blocks(base_hdr)
    assert nb == n_blocks(ins_hdr) and nb > 0, "block count mismatch between pair"
    print(f"blocks: {nb}", file=sys.stderr)

    store = {}
    per_matrix = []
    t_all = time.perf_counter()
    for idx, (store_key, hf_key, name) in enumerate(matrix_keys(nb)):
        t0 = time.perf_counter()
        W_base = read_tensor_fp32(args.base, base_hdr, base_off, hf_key)
        W_ins = read_tensor_fp32(args.instruct, ins_hdr, ins_off, hf_key)
        D = W_ins - W_base
        del W_base, W_ins
        fro = frobenius_sq(D)
        t_delta = time.perf_counter()
        s = rsvd_singular_values(D, args.rank_store, seed=SEED + idx)
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
        "check": "fourth_pair_svd_precompute",
        "model_pair": "Qwen/Qwen2.5-1.5B base / Instruct (Apache 2.0), local files on Flash",
        "n_blocks": nb,
        "n_matrices": len(per_matrix),
        "rank_store_requested": args.rank_store,
        "total_s": round(total_s, 2),
        "budget_s": 600,
        "verdict": "PASS" if total_s < 600 else "FAIL",
        "method": "randomized SVD, fp32, oversampling 12, 2 power iterations, seed 20261028",
        "per_matrix": per_matrix,
        "npz": str(out),
    }
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
