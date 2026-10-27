#!/usr/bin/env python3
"""Live hot-swap demo for Fraction Compressor v0.4.

Loads the real Qwen2.5-0.5B BASE model ONCE, answers three archetype
prompts with no patch, then swaps factored patches in and out live and
re-runs the same prompts:

  1. base model, no patch
  2. base + uniform rank-32 factored patch
  3. base + mlp_behemoth_lite factored patch (the byte-fair Alien Sweep
     leader from results/alien_sweep_heldout.json)

The factored path NEVER materializes the dense delta. For a weight
matrix W of shape (out, in) with factored delta D = U @ V.T, the
per-token contribution is computed as U @ (V.T @ h) and added to
W @ h. The embedding delta is applied the same way at lookup time
(U[token] @ V.T) and at the tied LM head (U @ (V.T @ h)).

Patch sizes are the documented-format prices from
src/factored.py:storage_bytes, summed over all 169 delta matrices
(rank-0 matrices priced at rank 0, exactly as Stage 2 and the held-out
run priced them). The .npz working files used here store the factors
as fp32 arrays and are larger on disk; the printed sizes are the
shipped-format prices, not the .npz file sizes.

Decoding is greedy. Generation uses a KV-cached NumPy forward built on
the verified Stage 2 machinery in examples/alien_sweep_stage2.py (same
chat template, same RoPE/RMSNorm math, activations kept in fp32).

Run on Flash:
  ~/qwen-test/.venv/bin/python examples/hotswap_demo.py \
      --out-json results/hotswap_demo.json
"""

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "src"))

import alien_sweep_stage2 as s2  # noqa: E402  (verified Stage 2 forward machinery)
from factored import storage_bytes  # noqa: E402
from tokenizers import Tokenizer  # noqa: E402

EOS = {151643, 151645}  # <|endoftext|>, <|im_end|>
EMB_KEY = "model.embed_tokens.weight"
HF2STORE = {hk: sk for sk, hk, _ in s2.matrix_keys()}
COS, SIN = [a.astype(np.float32) for a in s2.rope_tables(1024)]

PROMPTS = [
    {
        "id": "json_transform",
        "kind": "strict JSON instruction",
        "prompt": (
            'Return ONLY a JSON object with exactly these keys: "title", '
            '"year", and "director". Set title to "Arrival", year to 2016, '
            'and director to "Denis Villeneuve". Do not include markdown, '
            "comments, explanations, or any other text."
        ),
        "expected_json": {
            "title": "Arrival",
            "year": 2016,
            "director": "Denis Villeneuve",
        },
    },
    {
        "id": "knowledge_capital",
        "kind": "knowledge",
        "prompt": "Question: What is the capital of Japan? Answer with just the name.",
        "expected_substring": "Tokyo",
    },
    {
        "id": "math_percent",
        "kind": "math",
        "prompt": "What is 15 percent of 200? Answer with just the number.",
        "expected_substring": "30",
    },
]
MAX_NEW_TOKENS = 48


def rmsnorm32(x, w):
    var = np.mean((x.astype(np.float64) ** 2), axis=-1, keepdims=True)
    scale = (1.0 / np.sqrt(var + s2.EPS)).astype(np.float32)
    return (x * scale * w).astype(np.float32, copy=False)


def linear(h, sd, hf_key, adapters):
    """W @ h plus, when a patch is live, the factored delta contribution.

    The dense delta D = U @ V.T is never formed: the contribution is
    U @ (V.T @ h), two thin multiplies.
    """
    y = sd[hf_key] @ h
    if adapters is not None:
        fac = adapters.get(HF2STORE[hf_key])
        if fac is not None:
            U, V = fac
            y = y + U @ (V.T @ h)
    bkey = hf_key.replace(".weight", ".bias")
    if bkey in sd:
        y = y + sd[bkey]
    return y


def step(sd, token, pos, caches, adapters):
    """One KV-cached forward step; returns logits for the next token."""
    x = sd[EMB_KEY][token].astype(np.float32, copy=True)
    if adapters is not None and "embed" in adapters:
        U, V = adapters["embed"]
        x = x + U[token] @ V.T
    for i in range(s2.LAYERS):
        p = f"model.layers.{i}"
        h = rmsnorm32(x, sd[f"{p}.input_layernorm.weight"])
        q = linear(h, sd, f"{p}.self_attn.q_proj.weight", adapters).reshape(
            s2.HEADS, s2.HEAD_DIM
        )
        k = linear(h, sd, f"{p}.self_attn.k_proj.weight", adapters).reshape(
            s2.KV_HEADS, s2.HEAD_DIM
        )
        v = linear(h, sd, f"{p}.self_attn.v_proj.weight", adapters).reshape(
            s2.KV_HEADS, s2.HEAD_DIM
        )
        q = s2.apply_rope(q[None, :, :], COS[pos : pos + 1], SIN[pos : pos + 1])[0]
        k = s2.apply_rope(k[None, :, :], COS[pos : pos + 1], SIN[pos : pos + 1])[0]
        caches[i][0].append(k)
        caches[i][1].append(v)
        K = np.repeat(
            np.stack(caches[i][0]), s2.HEADS // s2.KV_HEADS, axis=1
        )
        V = np.repeat(
            np.stack(caches[i][1]), s2.HEADS // s2.KV_HEADS, axis=1
        )
        scores = np.einsum("hd,thd->ht", q, K) / np.float32(np.sqrt(s2.HEAD_DIM))
        probs = s2.softmax(scores)
        o = np.einsum("ht,thd->hd", probs, V).reshape(s2.HIDDEN)
        x = x + linear(o, sd, f"{p}.self_attn.o_proj.weight", adapters)
        h2 = rmsnorm32(x, sd[f"{p}.post_attention_layernorm.weight"])
        gate = s2.silu(linear(h2, sd, f"{p}.mlp.gate_proj.weight", adapters))
        up = linear(h2, sd, f"{p}.mlp.up_proj.weight", adapters)
        x = x + linear(gate * up, sd, f"{p}.mlp.down_proj.weight", adapters)
    x = rmsnorm32(x, sd["model.norm.weight"])
    logits = sd[EMB_KEY] @ x
    if adapters is not None and "embed" in adapters:
        U, V = adapters["embed"]
        logits = logits + U @ (V.T @ x)
    return logits


def generate(sd, tok, prompt, adapters):
    ids = tok.encode(s2.format_chat(prompt)).ids
    caches = [[[], []] for _ in range(s2.LAYERS)]
    logits = None
    t0 = time.perf_counter()
    for pos, token in enumerate(ids):
        logits = step(sd, token, pos, caches, adapters)
    out = []
    pos = len(ids)
    for _ in range(MAX_NEW_TOKENS):
        nxt = int(np.argmax(logits))
        if nxt in EOS:
            break
        out.append(nxt)
        if len(out) == MAX_NEW_TOKENS:
            break
        logits = step(sd, nxt, pos, caches, adapters)
        pos += 1
    return tok.decode(out, skip_special_tokens=True), len(out), time.perf_counter() - t0


def score_json(answer, expected):
    """Score by raw json.loads parseability and exact key/value match."""
    try:
        obj = json.loads(answer.strip())
    except Exception:
        return {"parseable": False, "exact_keys": False, "exact_values": False}
    if not isinstance(obj, dict):
        return {"parseable": True, "exact_keys": False, "exact_values": False}
    return {
        "parseable": True,
        "exact_keys": set(obj.keys()) == set(expected.keys()),
        "exact_values": obj == expected,
    }


def priced_size(npz_path, shapes):
    """Documented-format price of a factor file, Stage 2 method.

    Reads only the U array headers (ranks) from the .npz; every one of
    the 169 matrices is priced, absent ones at rank 0.
    """
    fac = np.load(npz_path)
    total = 0
    for store_key, shape in shapes.items():
        ukey = f"{store_key}_U"
        rank = int(fac[ukey].shape[1]) if ukey in fac else 0
        total += storage_bytes(rank, shape)
    fac.close()
    return total


def load_adapters(npz_path):
    """Load a factored patch into memory (the live swap)."""
    t0 = time.perf_counter()
    fac = np.load(npz_path)
    adapters = {}
    for key in list(fac.keys()):
        if key.endswith("_U"):
            store_key = key[:-2]
            adapters[store_key] = (
                fac[key].astype(np.float32),
                fac[f"{store_key}_V"].astype(np.float32),
            )
    fac.close()
    return adapters, time.perf_counter() - t0


def one_line(text):
    return text.replace("\n", "\\n")


def run_config(label, sd, tok, adapters, results):
    print(f"\n{'=' * 72}\nCONFIG: {label}\n{'=' * 72}")
    per_prompt = {}
    for spec in PROMPTS:
        answer, ntok, secs = generate(sd, tok, spec["prompt"], adapters)
        entry = {
            "answer": answer,
            "generated_tokens": ntok,
            "seconds": round(secs, 3),
        }
        if "expected_json" in spec:
            entry["json"] = score_json(answer, spec["expected_json"])
        if "expected_substring" in spec:
            entry["contains_expected"] = spec["expected_substring"] in answer
        per_prompt[spec["id"]] = entry
        print(f"\n[{spec['kind']}] PROMPT: {spec['prompt']}")
        print(f"ANSWER ({ntok} tokens, {secs:.1f}s):")
        print(answer)
        if "json" in entry:
            j = entry["json"]
            print(
                f"JSON SCORE: parseable={j['parseable']} "
                f"exact_keys={j['exact_keys']} exact_values={j['exact_values']}"
            )
        if "contains_expected" in entry:
            print(f"CONTAINS EXPECTED ANSWER: {entry['contains_expected']}")
    results[label] = per_prompt
    return per_prompt


def main():
    ap = argparse.ArgumentParser()
    home = Path.home()
    ap.add_argument("--base", default=str(home / "qwen-test/data/qwen2.5-0.5b.safetensors"))
    ap.add_argument("--tokenizer", default=str(home / "qwen-test/data/tokenizer.json"))
    ap.add_argument(
        "--uniform-factors",
        default=str(home / "fc-v04-sweep/stage2/factors_uniform_rank32.npz"),
    )
    ap.add_argument(
        "--lite-factors",
        default=str(home / "fc-v04-sweep/heldout/factors_mlp_behemoth_lite.npz"),
    )
    ap.add_argument("--out-json", default="hotswap_demo.json")
    args = ap.parse_args()

    print("FRACTION COMPRESSOR v0.4 - LIVE HOT-SWAP DEMO")
    print("Model: Qwen2.5-0.5B base, loaded ONCE. Patches swap live in memory.")
    print("Decoding: greedy, max 48 new tokens per prompt. No API calls.")
    t0 = time.perf_counter()
    sd = s2.load_all_fp32(args.base)
    print(f"Base model loaded in {time.perf_counter() - t0:.1f}s "
          f"(RSS {s2.peak_rss_mb():.0f} MB)")
    tok = Tokenizer.from_file(args.tokenizer)
    shapes = {sk: tuple(sd[hk].shape) for sk, hk, _ in s2.matrix_keys()}
    full_bytes = sum(int(np.prod(sd[hk].shape)) for _, hk, _ in s2.matrix_keys()) * 2
    uniform_bytes = priced_size(args.uniform_factors, shapes)
    lite_bytes = priced_size(args.lite_factors, shapes)

    results = {}
    swaps = []

    # 1. Base model, no patch.
    run_config("base (no patch)", sd, tok, None, results)

    # 2. Patch sizes.
    print(f"\n{'=' * 72}\nPATCH SIZES (documented factored format, src/factored.py)\n{'=' * 72}")
    print(f"full delta, fp16:        {full_bytes:>13,} B  (1.00x)")
    print(f"uniform rank-32 patch:   {uniform_bytes:>13,} B  "
          f"({full_bytes / uniform_bytes:.1f}x smaller)")
    print(f"mlp_behemoth_lite patch: {lite_bytes:>13,} B  "
          f"({full_bytes / lite_bytes:.1f}x smaller)")

    # 3. Swap in the uniform factored patch, live.
    adapters, swap_secs = load_adapters(args.uniform_factors)
    swaps.append({"to": "uniform_rank32", "seconds": round(swap_secs, 3),
                  "priced_bytes": uniform_bytes})
    print(f"\n>>> SWAP: uniform rank-32 factored patch loaded live in "
          f"{swap_secs:.2f}s ({len(adapters)} matrices, dense delta never formed)")
    run_config("base + uniform rank-32 factored patch", sd, tok, adapters, results)

    # 4. Swap to mlp_behemoth_lite, live.
    del adapters
    gc.collect()
    adapters, swap_secs = load_adapters(args.lite_factors)
    swaps.append({"to": "mlp_behemoth_lite", "seconds": round(swap_secs, 3),
                  "priced_bytes": lite_bytes})
    print(f"\n>>> SWAP: mlp_behemoth_lite factored patch loaded live in "
          f"{swap_secs:.2f}s ({len(adapters)} matrices, dense delta never formed)")
    run_config("base + mlp_behemoth_lite factored patch", sd, tok, adapters, results)

    # 5. Scoreboard.
    print(f"\n{'=' * 72}\nSCOREBOARD\n{'=' * 72}")
    for label, per_prompt in results.items():
        j = per_prompt["json_transform"]["json"]
        print(f"\n{label}")
        print(f"  JSON parseable: {'YES' if j['parseable'] else 'NO'}"
              f" (exact keys: {'YES' if j['exact_keys'] else 'NO'},"
              f" exact values: {'YES' if j['exact_values'] else 'NO'})")
        for spec in PROMPTS:
            print(f"  [{spec['id']}] {one_line(per_prompt[spec['id']]['answer'])}")

    peak = s2.peak_rss_mb()
    print(f"\nPeak RSS for the whole run: {peak:.0f} MB")
    out = {
        "model": "Qwen2.5-0.5B base (loaded once); patches applied live in factored form",
        "decoding": "greedy, max 48 new tokens",
        "prompts": [{k: v for k, v in s.items() if k != "expected_json"} |
                    ({"expected_json": s["expected_json"]} if "expected_json" in s else {})
                    for s in PROMPTS],
        "patch_sizes_bytes": {
            "full_delta_fp16": full_bytes,
            "uniform_rank32": uniform_bytes,
            "mlp_behemoth_lite": lite_bytes,
        },
        "swaps": swaps,
        "configs": results,
        "peak_rss_mb": round(peak, 1),
        "api_calls": [],
    }
    Path(args.out_json).write_text(json.dumps(out, indent=2))
    print(f"Wrote {args.out_json}")


if __name__ == "__main__":
    main()
