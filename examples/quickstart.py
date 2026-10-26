"""Quickstart: run the factored 1-bit delta runtime on a dummy delta.

    python3 examples/quickstart.py

Needs only numpy. Builds a random low-rank-ish delta, compresses it with
the factored runtime, and prints the storage cost, the bits per weight,
and how close the factored application is to the full delta.
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from factored import apply_dense, apply_factored, quantize_delta, storage_bytes

rng = np.random.default_rng(0)
m = n = 512
rank = 32

# A dummy fine-tune delta with strong low-rank structure, like a real one
# (real deltas are dominated by a few directions; pure noise is not
# compressible and is not what this format is for).
delta = (rng.normal(size=(m, 8)) @ rng.normal(size=(8, n))) * 0.02
delta += rng.normal(size=(m, n)) * 0.0005

packed = quantize_delta(delta, rank)
X = rng.normal(size=(4, m))

factored_out = apply_factored(X, packed["U"], packed["V"])
dense_out = apply_dense(X, delta)

stored = storage_bytes(rank, (m, n))
full_fp16 = m * n * 2
bpw = stored * 8 / (m * n)
apply_err = np.linalg.norm(factored_out - dense_out) / np.linalg.norm(dense_out)
recon_err = np.linalg.norm(packed["U"] @ packed["V"].T - delta) / np.linalg.norm(delta)

# The floor any rank-`rank` factored form can reach (plain truncated SVD,
# full precision factors, much bigger on disk). The sign constraint on U
# is what we pay for the 1-bit storage; how much task accuracy that costs
# is what the benchmark in this repo measures.
s = np.linalg.svd(delta, compute_uv=False)
svd_floor = float(np.sqrt(np.sum(s[rank:] ** 2)) / np.linalg.norm(delta))

print(f"delta shape        : {m} x {n}")
print(f"rank               : {rank}")
print(f"full delta (fp16)  : {full_fp16:,} bytes")
print(f"factored file      : {stored:,} bytes ({full_fp16 / stored:.1f}x smaller)")
print(f"bits per weight    : {bpw:.3f}")
print(f"reconstruction err : {recon_err:.3f} (relative, sign-factored vs full delta)")
print(f"best possible      : {svd_floor:.3f} (relative, plain SVD at same rank, full precision)")
print(f"apply rel err      : {apply_err:.3f} (factored apply vs dense apply)")
big = storage_bytes(rank, (2048, 2048))
print(f"larger layer price : 2048 x 2048 at rank {rank} costs {big:,} bytes "
      f"({big * 8 / (2048 * 2048):.3f} bits per weight); bits per weight falls as layers grow")
print("OK: the factored path runs and never builds the full matrix at apply time.")
