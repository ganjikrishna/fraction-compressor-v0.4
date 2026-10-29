"""Out-of-style LoRA control: prep validation only (no generation).

Design: results/lora_outofstyle_design.md. The in-style run's
lora_baseline.py prep is monolithic (validation + single-stream teacher
generation); the dataset for both runs actually comes from the batched
generator (lora_gen_batch.py). This script runs ONLY the validation
half, on Flash, before the batched generation:

1. Torch forward port vs the stored NumPy base scores (12 held-out
   items, identical picks to lora_baseline.py prep).
2. Adapter price assert (18,696,192 B fp16).
3. KV-cache decoder vs full-forward greedy on 6 prompts from the NEW
   Gemini prompt set.
4. Batched decoder (lora_gen_batch.BatchDecoder) vs single-stream
   KVDecoder greedy on 20 prompts from the NEW set.

Writes prepval_summary.json into the out-of-style workdir. Run with
the voice-clone venv (torch), from ~/fc-v04-sweep:

    ~/voice-clone/.venv/bin/python lora_outofstyle_prepval.py \
        --workdir ~/fc-v04-sweep/lora_outofstyle
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
import lora_gen_batch as lgb  # noqa: E402

BASE = "/home/vinay/qwen-test/data/qwen2.5-0.5b.safetensors"
INSTRUCT = "/home/vinay/qwen-test/data/qwen2.5-0.5b-instruct.safetensors"
DATA = "/home/vinay/qwen-test/data"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workdir", required=True)
    ap.add_argument("--probes", default="/home/vinay/fc-v04-sweep/heldout96_probes_spark.json")
    ap.add_argument("--heldout96-workdir", default="/home/vinay/fc-v04-sweep/heldout96")
    ap.add_argument("--threads", type=int, default=10)
    args = ap.parse_args()

    import torch
    from tokenizers import Tokenizer

    torch.set_num_threads(args.threads)
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(str(Path(DATA) / "tokenizer.json"))
    summary = {"stage": "lora_outofstyle_prepval", "threads": args.threads}

    # --- 1+2. Forward-port validation + adapter price (as cmd_prep). ---
    probes = json.loads(Path(args.probes).read_text())
    stored = json.loads((Path(args.heldout96_workdir) / "eval_base.json").read_text())
    ordered = ([it for it in probes if it["subset"] == "heldout24"]
               + [it for it in probes if it["subset"] == "heldout72_new"])
    stored_rows = stored["per_item"]
    assert len(stored_rows) == len(ordered) == 96
    pick = [i for i in range(96) if i % 8 == 0]
    items = [(ordered[i]["bucket"], ordered[i]["prompt"], ordered[i]["answer"])
             for i in pick]
    t0 = time.perf_counter()
    sd_base_np = s2.load_all_fp32(BASE)
    shapes = {k: tuple(v.shape) for k, v in sd_base_np.items()}
    price_bytes, price_params = lb.price_adapter(shapes)
    sd_base_t = lb.to_torch(sd_base_np)
    del sd_base_np
    gc.collect()
    mine = lb.torch_item_logprobs(tok, sd_base_t, items)
    diffs = []
    for row_idx, i in enumerate(pick):
        ref = stored_rows[i]
        assert ref["bucket"] == mine[row_idx]["bucket"]
        diffs.append(abs(mine[row_idx]["logprob"] - ref["logprob"]))
    summary["forward_validation"] = {
        "n_items": len(pick),
        "max_abs_logprob_diff_vs_numpy_base": max(diffs),
        "mean_abs_logprob_diff_vs_numpy_base": float(np.mean(diffs)),
        "wall_s": round(time.perf_counter() - t0, 1),
    }
    print("forward validation:", json.dumps(summary["forward_validation"]), flush=True)
    del sd_base_t
    gc.collect()
    summary["adapter_price"] = {"bytes_fp16": price_bytes, "params": price_params,
                                "rank": lb.RANK}
    assert price_bytes == 18696192, price_bytes

    # --- 3+4. Decoder checks on the NEW Gemini prompts. ---
    distill = json.loads((workdir / "distill_prompts.json").read_text())
    sd_ins_t = lb.to_torch(s2.load_all_fp32(INSTRUCT))

    mism = 0
    for it in distill[:6]:
        ids_p = tok.encode(s2.format_chat(it["prompt"])).ids
        fast = lb.KVDecoder(sd_ins_t).generate(ids_p, max_new=24)
        with torch.no_grad():
            ids = list(ids_p)
            slow = []
            for _ in range(24):
                logits = lb.forward_torch(ids, sd_ins_t)
                nxt = int(torch.argmax(logits[-1]).item())
                slow.append(nxt)
                ids.append(nxt)
                if nxt == lb.IM_END:
                    break
        if fast != slow:
            mism += 1
    summary["kv_cache_check"] = {"n_prompts": 6, "sequence_mismatches": mism,
                                 "set": "new Gemini distill prompts"}
    print("kv cache check:", json.dumps(summary["kv_cache_check"]), flush=True)

    items20 = distill[:20]
    idss = [tok.encode(s2.format_chat(it["prompt"])).ids for it in items20]
    t0 = time.perf_counter()
    batched = lgb.BatchDecoder(sd_ins_t, idss).generate(max_new=48)
    t_batch = time.perf_counter() - t0
    mism = 0
    t0 = time.perf_counter()
    for ids, bout in zip(idss, batched):
        slow = lb.KVDecoder(sd_ins_t).generate(ids, max_new=48)
        if slow != bout:
            mism += 1
    summary["batched_decoder_check"] = {
        "n_prompts": 20, "sequence_mismatches": mism,
        "batched_wall_s": round(t_batch, 1),
        "single_stream_wall_s": round(time.perf_counter() - t0, 1),
        "set": "new Gemini distill prompts"}
    print("batched decoder check:", json.dumps(summary["batched_decoder_check"]),
          flush=True)
    del sd_ins_t
    gc.collect()

    (workdir / "prepval_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote {workdir / 'prepval_summary.json'}")


if __name__ == "__main__":
    main()
