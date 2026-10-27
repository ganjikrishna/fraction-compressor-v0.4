#!/usr/bin/env python3
"""Make a patch file: the do-it-yourself entry point for Fraction Compressor.

In plain words, this is the whole tool in one script:

  1. Take two models: a base model and a fine-tuned version of it
     (same architecture, same shapes; safetensors format).
  2. Subtract, layer by layer: fine-tuned minus base. That difference
     is the patch (the delta). On its own it is almost as big as the
     model itself.
  3. Squeeze each layer's difference into the factored format: the
     layer's change is approximated by two thin factors, U and V, where
     U is stored as 1-bit signs (plus one scale per row) and V is
     stored in fp16. You choose how much room each layer gets: one
     --rank for every layer, or a --recipe that gives each layer type
     its own rank.
  4. Write ONE patch file (.npz) holding every layer's packed signs,
     scales, and V factor, plus a header that says where the patch came
     from and what it costs in bytes.
  5. To use the patch, load the base model and add the patch through
     the factored path, (X @ U) @ V.T, which never rebuilds the full
     weight matrix. examples/hotswap_demo.py shows patches being
     swapped live exactly this way. Check a patch file any time with
     --verify: it rebuilds a few layers from the file and proves the
     factored path and the dense path agree.

Which matrices get patched: the same set the Alien Sweep used, the
embedding plus, in every block, attn.q/k/v/o_proj and mlp.gate/up/down
(169 matrices on Qwen2.5-0.5B). Everything else (norm weights, biases)
is not part of the delta and stays at its base value; the LM head is
tied to the embedding on these models, so it is covered by the
embedding patch and is never stored twice.

Pricing is the documented format price from src/factored.py:
storage_bytes, summed over every patched matrix, exactly as the Alien
Sweep priced its recipes (a layer dropped at rank 0 still contributes
its per-row scale term, 4 * rows, the check-1 convention). The .npz
container adds a little overhead on top; both numbers are printed.

Examples:

  # one rank for every layer
  python3 examples/make_patch.py \\
      --base ~/models/qwen2.5-0.5b \\
      --finetuned ~/models/qwen2.5-0.5b-instruct \\
      --out patch_rank32.npz --rank 32

  # a per-layer recipe (JSON: layer name -> rank; the Alien Sweep
  # results files work too, pick one with --recipe-name)
  python3 examples/make_patch.py --base ... --finetuned ... \\
      --out patch_recipe.npz --recipe results/alien_sweep_check1.json \\
      --recipe-name mlp_behemoth

  # check a patch file round-trips through the factored path
  python3 examples/make_patch.py --base ... --finetuned ... \\
      --patch patch_rank32.npz --verify

--base and --finetuned each accept either a model directory (every
*.safetensors file in it is indexed, sharded models included) or a
single .safetensors file. Needs only numpy plus src/factored.py.
"""

import argparse
import gc
import json
import re
import resource
import struct
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
for cand in (HERE, HERE.parent / "src", HERE / "src"):
    if (cand / "factored.py").exists() and str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

import factored  # noqa: E402

# The patched matrices, same handling as examples/alien_sweep_stage2.py:
# the embedding plus 7 matrices per block. The LM head is tied to the
# embedding, so it is deliberately not in this list.
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
LAYER_NAMES = list(KEY_TEMPLATES)
BLOCK_NAMES = [n for n in KEY_TEMPLATES if n != "embed"]


def enumerate_matrices(available_keys):
    """Yield (store_key, hf_key, layer_name) for the patch matrices.

    Same enumeration and store-key naming as the Alien Sweep's
    matrix_keys(): embed first, then block by block. The block count is
    read from the model's own tensor names, not hard-coded. Matrices
    absent from the model are skipped by the caller.
    """
    blocks = set()
    for key in available_keys:
        m = re.match(r"model\.layers\.(\d+)\.", key)
        if m:
            blocks.add(int(m.group(1)))
    yield "embed", KEY_TEMPLATES["embed"], "embed"
    for i in sorted(blocks):
        for name in BLOCK_NAMES:
            yield f"b{i:02d}_{name.replace('.', '_')}", KEY_TEMPLATES[name].format(i=i), name


# ---------------------------------------------------------------------------
# safetensors reading: one tensor at a time, straight from the byte
# ranges, so a whole model never has to sit in memory. Accepts a single
# .safetensors file or a directory of them (sharded models included).
# ---------------------------------------------------------------------------

class ModelSource:
    def __init__(self, path):
        self.path = Path(path).expanduser()
        if self.path.is_file():
            files = [self.path]
        elif self.path.is_dir():
            files = sorted(self.path.glob("*.safetensors"))
            if not files:
                raise SystemExit(f"no .safetensors files in {self.path}")
        else:
            raise SystemExit(f"model path not found: {self.path}")
        self.index = {}  # tensor key -> (file, dtype, shape, lo, hi, data_start)
        for f in files:
            with open(f, "rb") as fh:
                (hlen,) = struct.unpack("<Q", fh.read(8))
                header = json.loads(fh.read(hlen))
            data_start = 8 + hlen
            for key, info in header.items():
                if key == "__metadata__":
                    continue
                if key in self.index:
                    raise SystemExit(f"tensor {key} appears in two files of {self.path}")
                lo, hi = info["data_offsets"]
                self.index[key] = (f, info["dtype"], tuple(info["shape"]), lo, hi, data_start)

    def keys(self):
        return self.index.keys()

    def __contains__(self, key):
        return key in self.index

    def shape(self, key):
        return self.index[key][2]

    def read_fp32(self, key):
        """Read one tensor as a fresh fp32 array."""
        f, dtype, shape, lo, hi, data_start = self.index[key]
        with open(f, "rb") as fh:
            fh.seek(data_start + lo)
            raw = fh.read(hi - lo)
        if dtype == "F32":
            return np.frombuffer(raw, dtype=np.float32).reshape(shape).copy()
        if dtype == "F64":
            return np.frombuffer(raw, dtype=np.float64).reshape(shape).astype(np.float32)
        if dtype == "F16":
            return np.frombuffer(raw, dtype=np.float16).reshape(shape).astype(np.float32)
        if dtype == "BF16":
            u16 = np.frombuffer(raw, dtype=np.uint16)
            return (u16.astype(np.uint32) << 16).view(np.float32).reshape(shape).copy()
        raise SystemExit(f"{key}: unsupported dtype {dtype}")


def peak_rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0


# ---------------------------------------------------------------------------
# Rank choice: one rank for all layers, or a recipe file.
# ---------------------------------------------------------------------------

def load_recipe(path, recipe_name):
    """Load a layer-name -> rank map from a recipe JSON file.

    Accepts a plain {"embed": 32, "attn.q_proj": 32, ...} object, a
    single {"name": ..., "ranks": {...}} object, or an Alien Sweep
    results file with a "recipes" list (then --recipe-name picks one).
    Layer types missing from the map get rank 0 (their delta is
    dropped), with a warning, matching the sweep's rank-0 semantics.
    """
    data = json.loads(Path(path).read_text())
    name = recipe_name
    if isinstance(data, dict) and "recipes" in data:
        recipes = data["recipes"]
        if name is None:
            if len(recipes) != 1:
                names = [r.get("name") for r in recipes]
                raise SystemExit(
                    f"{path} holds {len(recipes)} recipes {names}; "
                    "pick one with --recipe-name")
            chosen = recipes[0]
            name = chosen.get("name")
        else:
            matches = [r for r in recipes if r.get("name") == name]
            if not matches:
                raise SystemExit(f"no recipe named {name!r} in {path}")
            chosen = matches[0]
        ranks = chosen["ranks"]
    elif isinstance(data, dict) and "ranks" in data:
        ranks = data["ranks"]
        name = name or data.get("name")
    elif isinstance(data, dict):
        ranks = data
    else:
        raise SystemExit(f"{path}: unrecognized recipe format")
    unknown = set(ranks) - set(LAYER_NAMES)
    if unknown:
        raise SystemExit(
            f"recipe names unknown layers {sorted(unknown)}; "
            f"known layer names: {LAYER_NAMES}")
    out = {}
    for layer in LAYER_NAMES:
        if layer not in ranks:
            print(f"warning: recipe has no rank for {layer!r}; using rank 0 "
                  "(that layer's delta is dropped)", file=sys.stderr)
        out[layer] = int(ranks.get(layer, 0))
        if out[layer] < 0:
            raise SystemExit(f"recipe rank for {layer!r} is negative")
    return out, name


def resolve_ranks(args):
    """Return (ranks_by_layer, mode_description, recipe_meta)."""
    if args.rank is not None:
        if args.rank < 0:
            raise SystemExit("--rank must be 0 or more")
        return ({layer: int(args.rank) for layer in LAYER_NAMES},
                f"uniform rank {args.rank}", None)
    ranks, name = load_recipe(args.recipe, args.recipe_name)
    return ranks, f"recipe {name or args.recipe}", {"file": str(args.recipe), "name": name}


# ---------------------------------------------------------------------------
# Build a patch.
# ---------------------------------------------------------------------------

def cmd_build(args):
    ranks_by_layer, mode_desc, recipe_meta = resolve_ranks(args)
    base = ModelSource(args.base)
    finetuned = ModelSource(args.finetuned)

    arrays = {}
    per_matrix = []
    total_price = 0
    full_fp16 = 0
    n_dropped = 0
    n_skipped = 0

    for store_key, hf_key, layer in enumerate_matrices(base.keys()):
        if hf_key not in base or hf_key not in finetuned:
            n_skipped += 1
            continue
        shape = base.shape(hf_key)
        if finetuned.shape(hf_key) != shape:
            raise SystemExit(
                f"{hf_key}: shape differs between the two models "
                f"({shape} vs {finetuned.shape(hf_key)}); a patch only "
                "makes sense between a base model and its own fine-tune")
        if len(shape) != 2:
            n_skipped += 1
            continue
        requested = ranks_by_layer[layer]
        rank = min(requested, min(shape))
        price = factored.storage_bytes(rank, shape)
        total_price += price

        Wb = base.read_fp32(hf_key)
        Wi = finetuned.read_fp32(hf_key)
        delta32 = Wi - Wb
        del Wb, Wi
        full_fp16 += 2 * delta32.size

        entry = {
            "store_key": store_key, "hf_key": hf_key, "layer": layer,
            "shape": list(shape), "rank_requested": requested,
            "rank": rank, "storage_bytes": price,
        }
        if rank == 0:
            n_dropped += 1
            entry["note"] = "rank 0: delta dropped, matrix keeps its base value"
            del delta32
        else:
            q = factored.quantize_delta(delta32, rank)
            del delta32
            arrays[f"{store_key}_signs"] = q["U_signs_packed"]
            arrays[f"{store_key}_scales"] = q["row_scales_u"]
            arrays[f"{store_key}_V"] = q["V"].astype(np.float16)
            arrays[f"{store_key}_shape"] = np.array(shape, dtype=np.int64)
            del q
        per_matrix.append(entry)
        gc.collect()

    header = {
        "format": "fraction-compressor-patch",
        "format_version": 1,
        "created_by": "examples/make_patch.py (Fraction Compressor v0.4)",
        "base_model": {"path": str(args.base), "name": Path(args.base).name},
        "finetuned_model": {"path": str(args.finetuned),
                             "name": Path(args.finetuned).name},
        "rank_mode": mode_desc,
        "recipe": recipe_meta,
        "ranks_by_layer": ranks_by_layer,
        "n_matrices_patched": len(per_matrix) - n_dropped,
        "n_matrices_dropped_rank0": n_dropped,
        "n_matrices_skipped_absent": n_skipped,
        "matrices": per_matrix,
        "storage_bytes_total": total_price,
        "full_delta_fp16_bytes": int(full_fp16),
        "compression_ratio": (full_fp16 / total_price) if total_price else None,
        "pricing": ("documented format price: factored.storage_bytes summed "
                    "over every enumerated matrix, the Alien Sweep convention "
                    "(rank 0 contributes its 4 * rows scale term)"),
        "array_layout": ("per matrix with rank > 0: '<store_key>_signs' "
                         "(uint8, packed 1-bit signs of U), '<store_key>_scales' "
                         "(fp32, one scale per row of U), '<store_key>_V' "
                         "(fp16 V factor, shape (cols, rank)), '<store_key>_shape' "
                         "(int64 [rows, cols]). Rebuild U = unpack_signs(signs, "
                         "(rows, rank)) * scales[:, None]; the delta is U @ V.T."),
    }
    arrays["header_json"] = np.array(json.dumps(header, indent=2))

    out_path = Path(args.out)
    np.savez(out_path, **arrays)
    disk_bytes = out_path.stat().st_size

    print("PATCH SUMMARY")
    print(f"  base model:         {args.base}")
    print(f"  fine-tuned model:   {args.finetuned}")
    print(f"  ranks:              {mode_desc} "
          f"({', '.join(f'{k}={v}' for k, v in ranks_by_layer.items())})")
    print(f"  matrices patched:   {len(per_matrix) - n_dropped}"
          f" ({n_dropped} dropped at rank 0, {n_skipped} skipped: not a "
          "patched matrix or absent from one model)")
    print(f"  patch byte price (factored format): {total_price:,} B")
    print(f"  patch file on disk (.npz):          {disk_bytes:,} B "
          "(container overhead included)")
    print(f"  full delta at fp16:                 {int(full_fp16):,} B")
    print(f"  compression: {full_fp16 / total_price:.1f}x smaller "
          "than the full delta")
    print(f"  peak RSS: {peak_rss_mb():.0f} MB")
    print(f"  wrote {out_path}")
    return header


# ---------------------------------------------------------------------------
# Verify a patch: rebuild a few layers from the file alone and check the
# factored path against the dense path, plus against a fresh quantize of
# the real delta (so the check covers the file, not just the math).
# ---------------------------------------------------------------------------

VERIFY_TOL_ROUNDTRIP = 1e-6   # factored vs dense on identical factors
VERIFY_TOL_FIDELITY = 1e-2    # relative: file factors vs fresh quantize


def cmd_verify(args):
    patch_path = Path(args.patch)
    z = np.load(patch_path)
    header = json.loads(z["header_json"].item())
    by_store = {m["store_key"]: m for m in header["matrices"]}
    patched = [m for m in header["matrices"] if m["rank"] > 0]
    if not patched:
        raise SystemExit("patch file contains no matrices with rank > 0")

    # A spread of layers: the first patched, the embedding, a middle
    # attention and MLP matrix, and the last patched.
    picks = []

    def add(cand):
        if cand["rank"] > 0 and cand["store_key"] not in picks:
            picks.append(cand["store_key"])

    add(patched[0])
    add(header["matrices"][0])
    for layer in ("attn.q_proj", "mlp.gate"):
        same = [m for m in patched if m["layer"] == layer]
        if same:
            add(same[len(same) // 2])
    add(patched[-1])

    base = ModelSource(args.base)
    finetuned = ModelSource(args.finetuned)
    rng = np.random.default_rng(20261027)

    print(f"VERIFY {patch_path}")
    print(f"  patch header: base={header['base_model']['name']}, "
          f"fine-tuned={header['finetuned_model']['name']}, "
          f"ranks: {header['rank_mode']}, "
          f"byte price {header['storage_bytes_total']:,} B")
    worst_roundtrip = 0.0
    worst_fidelity = 0.0
    for store_key in picks:
        meta = by_store[store_key]
        m, n = meta["shape"]
        rank = meta["rank"]
        signs = z[f"{store_key}_signs"]
        scales = z[f"{store_key}_scales"].astype(np.float64)
        V = z[f"{store_key}_V"].astype(np.float64)
        U = factored.unpack_signs(signs, (m, rank)) * scales[:, None]

        # factored.py's convention: the delta maps X (batch, rows) to
        # (batch, cols) as X @ D, factored as (X @ U) @ V.T.
        X = rng.standard_normal((4, m))
        y_factored = factored.apply_factored(X, U, V)
        y_dense = factored.apply_dense(X, U @ V.T)
        roundtrip = float(np.abs(y_factored - y_dense).max())
        worst_roundtrip = max(worst_roundtrip, roundtrip)

        Wb = base.read_fp32(meta["hf_key"])
        Wi = finetuned.read_fp32(meta["hf_key"])
        delta32 = Wi - Wb
        del Wb, Wi
        q = factored.quantize_delta(delta32, rank)
        del delta32
        D_fresh = q["U"] @ q["V"].T
        del q
        D_file = U @ V.T
        scale = float(np.abs(D_fresh).max()) or 1.0
        fidelity = float(np.abs(D_file - D_fresh).max()) / scale
        worst_fidelity = max(worst_fidelity, fidelity)
        print(f"  {store_key} ({meta['hf_key']}, rank {rank}): "
              f"factored-vs-dense max diff {roundtrip:.3e}; "
              f"file-vs-fresh-quantize rel diff {fidelity:.3e}")
        del U, V, D_fresh, D_file
        gc.collect()
    z.close()

    ok = worst_roundtrip < VERIFY_TOL_ROUNDTRIP and worst_fidelity < VERIFY_TOL_FIDELITY
    print(f"  worst factored-vs-dense max diff: {worst_roundtrip:.3e} "
          f"(tolerance {VERIFY_TOL_ROUNDTRIP:.0e})")
    print(f"  worst file-vs-fresh rel diff:     {worst_fidelity:.3e} "
          f"(tolerance {VERIFY_TOL_FIDELITY:.0e}; the gap is the fp16 "
          "storage rounding of V, by design)")
    print(f"  peak RSS: {peak_rss_mb():.0f} MB")
    print(f"VERIFY: {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    ap = argparse.ArgumentParser(
        description="Make a Fraction Compressor patch file from a base "
                    "model and its fine-tuned version (see the module "
                    "docstring for the plain-words version).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  make a patch, one rank for every layer:\n"
            "    python3 examples/make_patch.py --base MODEL_DIR \\\n"
            "        --finetuned FINETUNED_DIR --out patch.npz --rank 32\n"
            "  make a patch from a per-layer recipe:\n"
            "    python3 examples/make_patch.py --base MODEL_DIR \\\n"
            "        --finetuned FINETUNED_DIR --out patch.npz \\\n"
            "        --recipe recipe.json [--recipe-name NAME]\n"
            "  verify a patch file:\n"
            "    python3 examples/make_patch.py --base MODEL_DIR \\\n"
            "        --finetuned FINETUNED_DIR --patch patch.npz --verify\n"))
    ap.add_argument("--base", required=True,
                    help="base model: a directory of .safetensors files, "
                         "or one .safetensors file")
    ap.add_argument("--finetuned", required=True,
                    help="the fine-tuned version of the base model "
                         "(same format as --base)")
    ap.add_argument("--out",
                    help="where to write the patch file (.npz); "
                         "required unless --verify is given")
    ap.add_argument("--rank", type=int, default=None,
                    help="use this rank for every layer (simplest choice; "
                         "32 is a good start)")
    ap.add_argument("--recipe", default=None,
                    help="JSON file mapping layer names to ranks, e.g. "
                         '{"embed": 80, "attn.q_proj": 32, ...}; Alien '
                         "Sweep results files work too (see --recipe-name)")
    ap.add_argument("--recipe-name", default=None,
                    help="which recipe to use when --recipe holds several")
    ap.add_argument("--patch", default=None,
                    help="an existing patch file, for --verify")
    ap.add_argument("--verify", action="store_true",
                    help="check a patch file instead of building one: "
                         "rebuild a few layers from the file and confirm "
                         "the factored path matches the dense path")
    args = ap.parse_args()

    if args.verify:
        if not args.patch:
            ap.error("--verify needs --patch <patch file>")
        ok = cmd_verify(args)
        sys.exit(0 if ok else 1)
    if args.patch:
        ap.error("--patch is only for --verify; to build a patch use --out")
    if not args.out:
        ap.error("--out is required when building a patch")
    if (args.rank is None) == (args.recipe is None):
        ap.error("choose exactly one of --rank N or --recipe FILE")
    cmd_build(args)


if __name__ == "__main__":
    main()
