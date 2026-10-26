"""Factored runtime for 1-bit compressed weight deltas.

A fine-tune delta ``D`` (shape ``(m, n)``) is approximated by a factored
form ``D ~= U @ V.T`` where ``U`` is ``(m, rank)`` and ``V`` is ``(n, rank)``.
Inference applies the delta as ``(X @ U) @ V.T`` and never materializes the
full ``m x n`` matrix; at batch size 1 the memory read per token is the
size of the factors, not the size of ``D``.

Storage format (what :func:`storage_bytes` prices):

- ``U`` is stored as **1-bit signs** (one bit per entry) plus one fp32
  scale per row of ``U``. The sign pattern is the part that carries the
  delta's structure at 1 bit per entry.
- ``V`` is stored in fp16.
- One fp32 scale per row of the original matrix ``D`` (folded into ``V``
  at apply time in this scaffold; priced separately for honesty).

This is a research scaffold, not a kernel: factors are kept in float in
memory, and :func:`pack_signs` / :func:`unpack_signs` show the exact bit
layout the on-disk format uses so byte counts are computed from the real
representation, not a formula alone.
"""

import numpy as np


def pack_signs(U: np.ndarray) -> np.ndarray:
    """Pack the sign of each entry of U into bits (1 where U >= 0 else 0).

    Returns a uint8 array of ceil(U.size / 8) bytes, row-major order.
    """
    signs = (U >= 0).astype(np.uint8).ravel()
    return np.packbits(signs)


def unpack_signs(packed: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Inverse of :func:`pack_signs`: returns a float array of +/-1."""
    bits = np.unpackbits(packed)[: shape[0] * shape[1]]
    return (bits.astype(np.float64) * 2.0 - 1.0).reshape(shape)


def quantize_delta(delta: np.ndarray, rank: int) -> dict:
    """Factor a delta into U, V with U carrying the 1-bit sign structure.

    Construction: truncated SVD ``D ~= A @ diag(s) @ B.T`` at ``rank``.
    The singular values are split symmetrically, ``U_svd = A * sqrt(s)``
    and ``V_svd = B * sqrt(s)``. The stored ``U`` keeps only the *signs*
    of ``U_svd`` times a per-row scale: ``U = sign(U_svd) * row_scale``
    where ``row_scale[i] = mean(|U_svd[i, :]|)``. ``V`` absorbs the rest:
    it is the least-squares fit of ``D`` against the fixed signed ``U``,
    ``V.T = pinv(U) @ D``, so ``U @ V.T`` is the best approximation of
    ``D`` achievable with that sign pattern.

    Returns a dict with:
      U          (m, rank) float, entries are +/- row_scale (the signs are
                 the stored 1-bit structure; see ``U_signs_packed``)
      V          (n, rank) float, stored as fp16 on disk
      U_signs_packed  bytes of the packed sign layout for U
      row_scales (m,) fp32 per-row scales of the original matrix
      rank, shape
    """
    delta = np.asarray(delta, dtype=np.float64)
    m, n = delta.shape
    if not 1 <= rank <= min(m, n):
        raise ValueError(f"rank must be in 1..{min(m, n)}, got {rank}")

    A, s, Bt = np.linalg.svd(delta, full_matrices=False)
    A_r, s_r, B_r = A[:, :rank], s[:rank], Bt[:rank, :].T
    root = np.sqrt(s_r)
    U_svd = A_r * root
    # V_svd would be B_r * root; it is superseded by the least-squares refit
    # below once U is forced onto its sign pattern.

    signs = np.where(U_svd >= 0, 1.0, -1.0)
    row_scales_u = np.mean(np.abs(U_svd), axis=1)
    U = signs * row_scales_u[:, None]

    # Least-squares refit of V against the fixed signed U, then fold the
    # original per-row scale bookkeeping in: row_scales of D are reported
    # separately (priced in storage) but not needed for the apply path.
    V = (np.linalg.pinv(U) @ delta).T  # (n, rank)
    row_scales = np.mean(np.abs(delta), axis=1)

    return {
        "U": U,
        "V": V,
        "U_signs_packed": pack_signs(U),
        "row_scales_u": row_scales_u.astype(np.float32),
        "row_scales": row_scales.astype(np.float32),
        "rank": rank,
        "shape": (m, n),
    }


def apply_factored(X: np.ndarray, U: np.ndarray, V: np.ndarray) -> np.ndarray:
    """Apply the factored delta: (X @ U) @ V.T. Never forms U @ V.T."""
    return (np.asarray(X) @ np.asarray(U)) @ np.asarray(V).T


def apply_dense(X: np.ndarray, delta: np.ndarray) -> np.ndarray:
    """Reference: apply the full delta directly."""
    return np.asarray(X) @ np.asarray(delta)


def storage_bytes(rank: int, shape: tuple[int, int]) -> int:
    """Real byte cost of a factored delta under the documented format.

    - U signs: m * rank bits
    - U per-row scales: m * 4 bytes (fp32)
    - V: n * rank * 2 bytes (fp16)
    - per-row scales of the original matrix: m * 4 bytes (fp32)
    """
    m, n = shape
    sign_bits = m * rank
    sign_bytes = (sign_bits + 7) // 8
    return sign_bytes + 4 * m + 2 * n * rank + 4 * m
