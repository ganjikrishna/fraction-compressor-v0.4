"""Plain-assert tests for src/factored.py. Run: python3 tests/test_factored.py"""
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from factored import (  # noqa: E402
    apply_dense,
    apply_factored,
    pack_signs,
    quantize_delta,
    storage_bytes,
    unpack_signs,
)


def test_apply_factored_matches_dense_factor():
    rng = np.random.default_rng(0)
    X = rng.standard_normal((4, 16))
    U = rng.standard_normal((16, 5))
    V = rng.standard_normal((12, 5))
    got = apply_factored(X, U, V)
    want = X @ (U @ V.T)
    err = np.max(np.abs(got - want))
    assert err < 1e-10, f"apply_factored mismatch: {err}"
    print(f"  apply_factored vs X @ (U @ V.T): max err {err:.3e}")


def test_sign_pack_roundtrip():
    rng = np.random.default_rng(1)
    U = rng.standard_normal((7, 5))
    back = unpack_signs(pack_signs(U), U.shape)
    assert np.array_equal(back, np.where(U >= 0, 1.0, -1.0))
    print("  sign pack/unpack roundtrip: exact")


def test_full_rank_reconstruction():
    # Honest scoping: exactness is tested on the unpacked float factors.
    # The stored format (1-bit signs + fp16 V) is lossy by design; its cost
    # is what storage_bytes prices. At full rank on a square delta the
    # least-squares refit of V against the signed U recovers D exactly,
    # because U is square and invertible: U @ pinv(U) = I.
    rng = np.random.default_rng(2)
    D = rng.standard_normal((64, 64))
    q = quantize_delta(D, rank=64)
    X = rng.standard_normal((8, 64))
    got = apply_factored(X, q["U"], q["V"])
    want = apply_dense(X, D)
    rel = np.linalg.norm(got - want) / np.linalg.norm(want)
    assert rel < 1e-6, f"full-rank reconstruction rel err {rel}"
    print(f"  full-rank reconstruction: rel err {rel:.3e}")


def test_low_rank_is_approximation():
    rng = np.random.default_rng(3)
    D = rng.standard_normal((64, 64))
    q = quantize_delta(D, rank=4)
    approx = q["U"] @ q["V"].T
    rel = np.linalg.norm(approx - D) / np.linalg.norm(D)
    assert 0.0 < rel < 1.0, f"low-rank rel err should be in (0,1), got {rel}"
    print(f"  rank-4 approximation: rel err {rel:.3f} (expected in (0,1))")


def test_storage_budget():
    total = storage_bytes(32, (2048, 2048))
    bpw = total * 8 / (2048 * 2048)
    assert bpw < 0.6, f"storage {bpw:.3f} bpw not under 0.6"
    print(f"  storage_bytes(32, 2048x2048) = {total} bytes = {bpw:.4f} bits/weight")


def main():
    tests = [
        test_apply_factored_matches_dense_factor,
        test_sign_pack_roundtrip,
        test_full_rank_reconstruction,
        test_low_rank_is_approximation,
        test_storage_budget,
    ]
    for t in tests:
        print(t.__name__)
        t()
    print("PASS")


if __name__ == "__main__":
    main()
