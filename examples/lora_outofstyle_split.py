"""Out-of-style LoRA control: first-token vs continuation split scorer.

Design: results/lora_outofstyle_design.md (Glimmer's KL-shape check).
Scores a probes file with the house machinery, but records per item
the logprob of the FIRST answer token separately from the continuation
(all remaining answer tokens), so a distribution-shape / confidence
explanation stays visible next to the style explanation.

Configs: base, full (Instruct weights), uniform, lite (factored deltas
applied to base exactly as alien_sweep_heldout96.py does), lora_instyle
(adapter_seed20261028_fp16 from the in-style workdir), lora_oos
(adapter_seed20261028_fp16 from the out-of-style workdir, hooked
(X@A.T)@B.T forward from lora_baseline.py).

Trust rule (design doc): this scorer's per-item TOTAL logprobs must
reproduce the canonical eval totals for the same config and probes
before its splits are used; the validation step checks that.

Runs on Flash next to alien_sweep_stage2.py and lora_baseline.py:

    python3 lora_outofstyle_split.py --config lora_oos \
        --base ~/qwen-test/data/qwen2.5-0.5b.safetensors \
        --instruct ~/qwen-test/data/qwen2.5-0.5b-instruct.safetensors \
        --probes <probes.json> \
        --stage2-workdir ~/fc-v04-sweep/stage2 \
        --heldout-workdir ~/fc-v04-sweep/heldout \
        --instyle-workdir ~/fc-v04-sweep/lora_baseline \
        --oos-workdir ~/fc-v04-sweep/lora_outofstyle \
        --out <out.json>
"""

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import alien_sweep_stage2 as s2  # noqa: E402
import lora_baseline as lb  # noqa: E402


def score_items_split(tok, sd, items, adapters=None):
    """Mirror s2.score_items / lb.score_items_adapted, recording the
    first-answer-token logprob separately from the continuation."""
    rows = []
    for bucket, prompt, answer in items:
        ids_p = tok.encode(s2.format_chat(prompt)).ids
        ids_f = tok.encode(s2.format_chat(prompt) + answer).ids
        if len(ids_f) > len(ids_p) and ids_f[: len(ids_p)] == ids_p:
            ids_a = ids_f[len(ids_p):]
        else:
            ids_a = tok.encode(answer).ids
        if not ids_a:
            continue
        if adapters is None:
            logits = s2.forward(ids_p + ids_a, sd)
        else:
            logits = lb.forward_adapted(ids_p + ids_a, sd, adapters)
        off = len(ids_p)
        per_tok = []
        for j, tok_id in enumerate(ids_a):
            row = logits[off + j - 1].astype(np.float64)
            row = row - row.max()
            e = np.exp(row)
            per_tok.append(float(np.log(e[tok_id] / e.sum())))
        first_hit = int(np.argmax(logits[off - 1]) == ids_a[0])
        rows.append({
            "bucket": s2.BUCKET_LABELS[bucket],
            "logprob": float(sum(per_tok)),
            "first_token_logprob": per_tok[0],
            "continuation_logprob": float(sum(per_tok[1:])),
            "n_answer_tokens": len(ids_a),
            "first_token_correct": first_hit,
        })
    return rows


def agg(rows):
    if not rows:
        return None
    total = float(np.mean([r["logprob"] for r in rows]))
    first = float(np.mean([r["first_token_logprob"] for r in rows]))
    cont = float(np.mean([r["continuation_logprob"] for r in rows]))
    return {
        "n": len(rows),
        "mean_target_logprob": total,
        "mean_first_token_logprob": first,
        "mean_continuation_logprob": cont,
        "first_token_share_of_total": (first / total) if total else None,
        "first_token_accuracy": float(np.mean([r["first_token_correct"] for r in rows])),
        "mean_answer_tokens": float(np.mean([r["n_answer_tokens"] for r in rows])),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True,
                    choices=["base", "full", "uniform", "lite",
                             "lora_instyle", "lora_oos"])
    ap.add_argument("--base", required=True)
    ap.add_argument("--instruct", required=True)
    ap.add_argument("--probes", required=True)
    ap.add_argument("--data", default=str(Path.home() / "qwen-test" / "data"))
    ap.add_argument("--stage2-workdir", required=True)
    ap.add_argument("--heldout-workdir", required=True)
    ap.add_argument("--instyle-workdir", required=True)
    ap.add_argument("--oos-workdir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    from tokenizers import Tokenizer

    tok = Tokenizer.from_file(str(Path(args.data) / "tokenizer.json"))
    probes = json.loads(Path(args.probes).read_text())
    subsets = ("heldout24", "heldout72_new")

    t0 = time.perf_counter()
    adapters = None
    if args.config == "full":
        sd = s2.load_all_fp32(args.instruct)
        applied = "Instruct weights (== base + full delta)"
    else:
        sd = s2.load_all_fp32(args.base)
        if args.config in ("uniform", "lite"):
            name = "uniform_rank32" if args.config == "uniform" else "mlp_behemoth_lite"
            fac_path = Path(args.heldout_workdir) / f"factors_{name}.npz"
            if not fac_path.exists():
                fac_path = Path(args.stage2_workdir) / f"factors_{name}.npz"
            fac = np.load(fac_path)
            key_of = {sk: hk for sk, hk, _ in s2.matrix_keys()}
            for store_key, hf_key in key_of.items():
                ukey = f"{store_key}_U"
                if ukey not in fac:
                    continue
                U, V = fac[ukey], fac[f"{store_key}_V"]
                sd[hf_key] = sd[hf_key] + (U @ V.T)
            applied = f"base + factored delta ({name})"
        elif args.config == "lora_instyle":
            adapters = lb.load_adapters(args.instyle_workdir,
                                        "adapter_seed20261028_fp16.npz")
            applied = "base + in-style LoRA adapter (seed 20261028, fp16, hooked)"
        elif args.config == "lora_oos":
            adapters = lb.load_adapters(args.oos_workdir,
                                        "adapter_seed20261028_fp16.npz")
            applied = "base + out-of-style LoRA adapter (seed 20261028, fp16, hooked)"
        else:
            applied = "base weights, no delta"
    load_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    rows = []
    for subset in subsets:
        sub_items = [(it["bucket"], it["prompt"], it["answer"])
                     for it in probes if it["subset"] == subset]
        sub_rows = score_items_split(tok, sd, sub_items, adapters)
        for r in sub_rows:
            r["subset"] = subset
        rows.extend(sub_rows)
    eval_s = time.perf_counter() - t1
    del sd
    gc.collect()

    by_bucket = {}
    for b in sorted({r["bucket"] for r in rows}):
        by_bucket[b] = agg([r for r in rows if r["bucket"] == b])
    out = {
        "config": args.config,
        "probes": str(args.probes),
        "applied": applied,
        "n_items": len(rows),
        "overall": agg(rows),
        "by_bucket": by_bucket,
        "by_subset": {s: agg([r for r in rows if r["subset"] == s]) for s in subsets},
        "per_item": rows,
        "load_wall_s": round(load_s, 2),
        "eval_wall_s": round(eval_s, 2),
        "peak_rss_mb": round(s2.peak_rss_mb(), 1),
    }
    Path(args.out).write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"config": args.config, "overall": out["overall"],
                      "eval_wall_s": out["eval_wall_s"],
                      "peak_rss_mb": out["peak_rss_mb"]}, indent=2))


if __name__ == "__main__":
    main()
