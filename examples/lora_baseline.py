"""LoRA baseline: Flash-side pipeline (prep / train / eval).

Design: results/lora_baseline_design.md. The matched-byte LoRA baseline
for the Qwen2.5-0.5B pair, distilled from the full Instruct model on
Spark-written prompts (examples/lora_baseline_gen.py), scored with the
house NumPy machinery on the same combined 96 held-out probes as every
other row.

Subcommands:
  prep   (voice-clone venv, torch): validate the PyTorch forward port
         against the NumPy scorer's stored base scores, then greedy-
         generate teacher answers for all distillation prompts with a
         KV-cache decoder (itself validated against full-forward
         decoding). Writes the distillation dataset JSON.
  train  (voice-clone venv, torch): one seed of LoRA distillation.
         Soft KL (forward KL teacher||student, T=1) at teacher-answer
         positions, teacher online. Rank 17 on all seven block linears,
         alpha 32, AdamW lr 2e-4 cosine, batch 8, up to 6 epochs, early
         stop on validation-split KL. Exports fp32 and fp16-rounded
         adapter files (scale folded into B).
  eval   (qwen-test venv, numpy): score one config on the combined 96
         with alien_sweep_stage2's forward/metrics. Configs:
         lora_seed{N}        hooked (X@A.T)@B.T apply, fp16 adapter
         lora_seed{N}_fp32   hooked apply, fp32 adapter (sensitivity)
         lora_seed1_dense    dense W + B@A through the unmodified
                             forward (reference for the hooked path)
         lora_zero           hooked path with zero adapter (must
                             reproduce the stored base scores)
         uniform_noembed / lite_noembed
                             factored rows with the embedding delta
                             dropped (blocks-only comparison)
         uniform_vfp16 / lite_vfp16
                             factored rows with V rounded through
                             fp16 (precision sensitivity)

The script lives next to alien_sweep_stage2.py both in the repo
(examples/) and on Flash (~/fc-v04-sweep/); it imports that module for
the weight loader, the NumPy forward, and the metrics, unchanged.
"""

import argparse
import gc
import json
import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import alien_sweep_stage2 as s2  # noqa: E402

RANK = 17
ALPHA = 32.0
TARGET_NAMES = ["attn.q_proj", "attn.k_proj", "attn.v_proj", "attn.o_proj",
                "mlp.gate", "mlp.up", "mlp.down"]
IM_END = 151645


def price_adapter(shapes):
    """fp16 byte price of the rank-17 all-block-linears adapter.

    shapes: {hf_key: (out, in)} for the 168 targeted matrices.
    Returns (total_bytes, total_params)."""
    params = 0
    for _sk, hk, name in s2.matrix_keys():
        if name == "embed":
            continue
        out, inn = shapes[hk]
        params += RANK * (out + inn)
    return 2 * params, params


def lora_keys():
    """Yield (store_key, hf_key) for the 168 adapter-targeted matrices."""
    for sk, hk, name in s2.matrix_keys():
        if name != "embed":
            yield sk, hk


# ---------------------------------------------------------------------------
# PyTorch port of the stage-2 Qwen2.5 forward (fp32). Mirrors
# alien_sweep_stage2.forward op for op: same RMSNorm, RoPE tables,
# GQA repeat, -1e9 causal mask, manual softmax, tied head. Validated
# numerically against the NumPy scorer in prep before any training.
# ---------------------------------------------------------------------------

def to_torch(sd_np):
    import torch
    return {k: torch.from_numpy(np.ascontiguousarray(v)) for k, v in sd_np.items()}


def _rope_tables_t(torch, T, device):
    inv = 1.0 / (s2.ROPE_THETA ** (torch.arange(0, s2.HEAD_DIM, 2, dtype=torch.float32,
                                                device=device) / s2.HEAD_DIM))
    f = torch.outer(torch.arange(T, dtype=torch.float32, device=device), inv)
    e = torch.cat([f, f], dim=-1)
    return torch.cos(e), torch.sin(e)


def _apply_rope_t(x, cos, sin):
    import torch
    x1, x2 = x[..., : s2.HEAD_DIM // 2], x[..., s2.HEAD_DIM // 2:]
    xr = torch.cat([-x2, x1], dim=-1)
    return x * cos[:, None, :] + xr * sin[:, None, :]


def _rmsnorm_t(x, w):
    import torch
    return x / torch.sqrt((x ** 2).mean(-1, keepdim=True) + s2.EPS) * w


def _softmax_t(x):
    import torch
    x = x - x.max(-1, keepdim=True).values
    e = torch.exp(x)
    return e / e.sum(-1, keepdim=True)


def forward_torch(ids, sd, loras=None, scale=1.0):
    """Full forward. ids: list[int]. loras: {hf_key: (A, B)} or None.
    Returns logits (T, vocab) fp32. Differentiable w.r.t. A/B."""
    import torch
    device = sd["model.embed_tokens.weight"].device
    T = len(ids)
    cos, sin = _rope_tables_t(torch, T, device)

    def linear(x, key):
        y = x @ sd[key].T
        bkey = key.replace(".weight", ".bias")
        if bkey in sd:
            y = y + sd[bkey]
        if loras is not None and key in loras:
            A, B = loras[key]
            y = y + scale * ((x @ A.T) @ B.T)
        return y

    x = sd["model.embed_tokens.weight"][torch.tensor(ids, dtype=torch.long, device=device)]
    for i in range(s2.LAYERS):
        p = f"model.layers.{i}"
        h = _rmsnorm_t(x, sd[f"{p}.input_layernorm.weight"])
        q = linear(h, f"{p}.self_attn.q_proj.weight").reshape(T, s2.HEADS, s2.HEAD_DIM)
        k = linear(h, f"{p}.self_attn.k_proj.weight").reshape(T, s2.KV_HEADS, s2.HEAD_DIM)
        v = linear(h, f"{p}.self_attn.v_proj.weight").reshape(T, s2.KV_HEADS, s2.HEAD_DIM)
        q, k = _apply_rope_t(q, cos, sin), _apply_rope_t(k, cos, sin)
        k = k.repeat_interleave(s2.HEADS // s2.KV_HEADS, dim=1)
        v = v.repeat_interleave(s2.HEADS // s2.KV_HEADS, dim=1)
        att = torch.einsum("thd,shd->hts", q, k) / math.sqrt(s2.HEAD_DIM)
        mask = torch.triu(torch.ones((T, T), dtype=torch.bool, device=device), 1)
        att = att.masked_fill(mask, -1e9)
        att = _softmax_t(att)
        o = torch.einsum("hts,shd->thd", att, v).reshape(T, s2.HIDDEN)
        x = x + linear(o, f"{p}.self_attn.o_proj.weight")
        h2 = _rmsnorm_t(x, sd[f"{p}.post_attention_layernorm.weight"])
        gate = torch.nn.functional.silu(linear(h2, f"{p}.mlp.gate_proj.weight"))
        up = linear(h2, f"{p}.mlp.up_proj.weight")
        x = x + linear(gate * up, f"{p}.mlp.down_proj.weight")
    x = _rmsnorm_t(x, sd["model.norm.weight"])
    return x @ sd["model.embed_tokens.weight"].T


class KVDecoder:
    """Greedy decoding with a KV cache, same math as forward_torch.

    Processes a whole chunk per call (the prompt as one prefill chunk,
    then one token per decode step) with an explicit causal mask over
    cache + chunk. The prep KV check compares its greedy output
    token-for-token against full-forward greedy decoding."""

    def __init__(self, sd):
        import torch
        self.sd = sd
        self.torch = torch
        self.device = sd["model.embed_tokens.weight"].device
        self.kcache = [None] * s2.LAYERS
        self.vcache = [None] * s2.LAYERS
        self.pos = 0

    def _chunk(self, token_ids):
        torch = self.torch
        sd = self.sd
        m = len(token_ids)
        start = self.pos
        cos, sin = _rope_tables_t(torch, start + m, self.device)
        cos_c, sin_c = cos[start:start + m], sin[start:start + m]

        def linear(v_, key):
            y = v_ @ sd[key].T
            bkey = key.replace(".weight", ".bias")
            if bkey in sd:
                y = y + sd[bkey]
            return y

        x = sd["model.embed_tokens.weight"][torch.tensor(
            token_ids, dtype=torch.long, device=self.device)]
        for i in range(s2.LAYERS):
            p = f"model.layers.{i}"
            h = _rmsnorm_t(x, sd[f"{p}.input_layernorm.weight"])
            q = linear(h, f"{p}.self_attn.q_proj.weight").reshape(m, s2.HEADS, s2.HEAD_DIM)
            k = linear(h, f"{p}.self_attn.k_proj.weight").reshape(m, s2.KV_HEADS, s2.HEAD_DIM)
            v = linear(h, f"{p}.self_attn.v_proj.weight").reshape(m, s2.KV_HEADS, s2.HEAD_DIM)
            q = _apply_rope_t(q, cos_c, sin_c)
            k = _apply_rope_t(k, cos_c, sin_c)
            if self.kcache[i] is None:
                kall, vall = k, v
            else:
                kall = torch.cat([self.kcache[i], k], dim=0)
                vall = torch.cat([self.vcache[i], v], dim=0)
            self.kcache[i], self.vcache[i] = kall, vall
            kk = kall.repeat_interleave(s2.HEADS // s2.KV_HEADS, dim=1)
            vv = vall.repeat_interleave(s2.HEADS // s2.KV_HEADS, dim=1)
            att = torch.einsum("thd,shd->hts", q, kk) / math.sqrt(s2.HEAD_DIM)
            s_total = kall.shape[0]
            key_pos = torch.arange(s_total, device=self.device)
            q_pos = start + torch.arange(m, device=self.device)
            mask = key_pos[None, :] > q_pos[:, None]
            if bool(mask.any()):
                att = att.masked_fill(mask[None, :, :], -1e9)
            att = _softmax_t(att)
            o = torch.einsum("hts,shd->thd", att, vv).reshape(m, s2.HIDDEN)
            x = x + linear(o, f"{p}.self_attn.o_proj.weight")
            h2 = _rmsnorm_t(x, sd[f"{p}.post_attention_layernorm.weight"])
            gate = torch.nn.functional.silu(linear(h2, f"{p}.mlp.gate_proj.weight"))
            up = linear(h2, f"{p}.mlp.up_proj.weight")
            x = x + linear(gate * up, f"{p}.mlp.down_proj.weight")
        x = _rmsnorm_t(x, sd["model.norm.weight"])
        self.pos += m
        return x @ sd["model.embed_tokens.weight"].T

    def generate(self, prompt_ids, max_new=48):
        import torch
        with torch.no_grad():
            logits = self._chunk(list(prompt_ids))
            out = []
            nxt = int(torch.argmax(logits[-1]).item())
            for _ in range(max_new):
                out.append(nxt)
                if nxt == IM_END:
                    break
                logits = self._chunk([nxt])
                nxt = int(torch.argmax(logits[-1]).item())
            return out


# ---------------------------------------------------------------------------
# prep: forward-port validation + teacher answer generation.
# ---------------------------------------------------------------------------

def torch_item_logprobs(tok, sd_t, items):
    """Mirror s2.score_items' logprob computation with the torch port."""
    import torch
    rows = []
    with torch.no_grad():
        for bucket, prompt, answer in items:
            ids_p = tok.encode(s2.format_chat(prompt)).ids
            ids_f = tok.encode(s2.format_chat(prompt) + answer).ids
            if len(ids_f) > len(ids_p) and ids_f[: len(ids_p)] == ids_p:
                ids_a = ids_f[len(ids_p):]
            else:
                ids_a = tok.encode(answer).ids
            if not ids_a:
                continue
            logits = forward_torch(ids_p + ids_a, sd_t)
            off = len(ids_p)
            lp = 0.0
            for j, tok_id in enumerate(ids_a):
                row = torch.log_softmax(logits[off + j - 1].double(), dim=-1)
                lp += float(row[tok_id])
            rows.append({"bucket": s2.BUCKET_LABELS[bucket], "logprob": lp})
    return rows


def cmd_prep(args):
    import torch
    from tokenizers import Tokenizer

    torch.set_num_threads(args.threads)
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(str(Path(args.data) / "tokenizer.json"))
    summary = {"stage": "lora_baseline_prep", "threads": args.threads}

    # --- 1. Forward-port validation vs the stored NumPy base scores. ---
    probes = json.loads(Path(args.probes).read_text())
    stored = json.loads((Path(args.heldout96_workdir) / "eval_base.json").read_text())
    # Rebuild the stored per-item order: heldout24 rows first (file
    # order), then heldout72_new rows (file order), as the eval wrote.
    ordered = ([it for it in probes if it["subset"] == "heldout24"]
               + [it for it in probes if it["subset"] == "heldout72_new"])
    stored_rows = stored["per_item"]
    assert len(stored_rows) == len(ordered) == 96
    pick = [i for i in range(96) if i % 8 == 0]  # 12 items across subsets/buckets
    items = [(ordered[i]["bucket"], ordered[i]["prompt"], ordered[i]["answer"])
             for i in pick]

    t0 = time.perf_counter()
    sd_base_np = s2.load_all_fp32(args.base)
    shapes = {k: tuple(v.shape) for k, v in sd_base_np.items()}
    price_bytes, price_params = price_adapter(shapes)
    sd_base_t = to_torch(sd_base_np)
    del sd_base_np
    gc.collect()
    mine = torch_item_logprobs(tok, sd_base_t, items)
    diffs = []
    for row_idx, i in enumerate(pick):
        ref = stored_rows[i]
        assert ref["bucket"] == mine[row_idx]["bucket"], (i, ref, mine[row_idx])
        diffs.append(abs(mine[row_idx]["logprob"] - ref["logprob"]))
    summary["forward_validation"] = {
        "n_items": len(pick),
        "max_abs_logprob_diff_vs_numpy_base": max(diffs),
        "mean_abs_logprob_diff_vs_numpy_base": float(np.mean(diffs)),
        "wall_s": round(time.perf_counter() - t0, 1),
    }
    print("forward validation:", json.dumps(summary["forward_validation"], indent=2),
          flush=True)
    del sd_base_t
    gc.collect()

    summary["adapter_price"] = {"bytes_fp16": price_bytes, "params": price_params,
                                "rank": RANK,
                                "uniform_budget_bytes": 19434496,
                                "lite_budget_bytes": 19358176,
                                "under_uniform_by": 19434496 - price_bytes}
    assert price_bytes == 18696192, price_bytes

    # --- 2. KV-cache vs full-forward greedy check on 20 distill prompts. ---
    distill = json.loads(Path(args.distill).read_text())
    sd_ins_t = to_torch(s2.load_all_fp32(args.instruct))
    check_prompts = distill[:20]
    mismatches = 0
    for it in check_prompts:
        ids_p = tok.encode(s2.format_chat(it["prompt"])).ids
        dec = KVDecoder(sd_ins_t)
        fast = dec.generate(ids_p, max_new=24)
        with torch.no_grad():
            ids = list(ids_p)
            slow = []
            for _ in range(24):
                logits = forward_torch(ids, sd_ins_t)
                nxt = int(torch.argmax(logits[-1]).item())
                slow.append(nxt)
                ids.append(nxt)
                if nxt == IM_END:
                    break
        if fast != slow:
            mismatches += 1
    summary["kv_cache_check"] = {"n_prompts": len(check_prompts),
                                 "sequence_mismatches": mismatches}
    print("kv cache check:", json.dumps(summary["kv_cache_check"]), flush=True)

    # --- 3. Teacher generations for the full distillation set. ---
    t1 = time.perf_counter()
    out_items = []
    for n, it in enumerate(distill):
        ids_p = tok.encode(s2.format_chat(it["prompt"])).ids
        dec = KVDecoder(sd_ins_t)
        ans_ids = dec.generate(ids_p, max_new=48)
        out_items.append({
            "bucket": it["bucket"], "prompt": it["prompt"], "split": it["split"],
            "prompt_ids": ids_p, "answer_ids": ans_ids,
            "answer_text": tok.decode(ans_ids),
        })
        if (n + 1) % 250 == 0:
            print(f"teacher gen {n + 1}/{len(distill)} "
                  f"({time.perf_counter() - t1:.0f}s)", flush=True)
    del sd_ins_t
    gc.collect()
    lens = [len(it["answer_ids"]) for it in out_items]
    summary["teacher_generation"] = {
        "n": len(out_items),
        "answer_tokens_mean": float(np.mean(lens)),
        "answer_tokens_min": int(np.min(lens)),
        "answer_tokens_max": int(np.max(lens)),
        "ended_with_im_end": int(sum(1 for it in out_items
                                     if it["answer_ids"] and it["answer_ids"][-1] == IM_END)),
        "wall_s": round(time.perf_counter() - t1, 1),
    }
    print("teacher generation:", json.dumps(summary["teacher_generation"], indent=2),
          flush=True)
    (workdir / "distill_dataset.json").write_text(json.dumps(out_items, indent=2) + "\n")
    (workdir / "prep_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote {workdir / 'distill_dataset.json'} and prep_summary.json")


# ---------------------------------------------------------------------------
# train: one seed of LoRA distillation (soft KL, online teacher).
# ---------------------------------------------------------------------------

def kl_on_answers(student_logits, teacher_logits, prompt_len):
    """Mean per-token forward KL (teacher||student) at answer positions.

    Sequences are prompt_ids + answer_ids; logits at position t predict
    token t+1, so answer tokens (positions prompt_len..end in the token
    stream) are predicted from logits rows prompt_len-1..end-1."""
    import torch
    sl = torch.log_softmax(student_logits[prompt_len - 1:-1].double(), dim=-1)
    tp = torch.softmax(teacher_logits[prompt_len - 1:-1].double(), dim=-1)
    tl = torch.log_softmax(teacher_logits[prompt_len - 1:-1].double(), dim=-1)
    kl = (tp * (tl - sl)).sum(-1)
    return kl.mean()


def cmd_train(args):
    import torch

    torch.set_num_threads(args.threads)
    seed = args.seed
    torch.manual_seed(seed)
    rng = np.random.default_rng(seed)
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    scale = ALPHA / RANK

    dataset = json.loads((workdir / "distill_dataset.json").read_text())
    train_items = [it for it in dataset if it["split"] == "train"]
    val_items = [it for it in dataset if it["split"] == "val"]
    print(f"train {len(train_items)} val {len(val_items)}", flush=True)

    sd_base_t = to_torch(s2.load_all_fp32(args.base))
    sd_ins_t = to_torch(s2.load_all_fp32(args.instruct))

    loras = {}
    params = []
    for _sk, hk in lora_keys():
        W = sd_base_t[hk]
        out, inn = W.shape
        A = torch.empty((RANK, inn), dtype=torch.float32)
        torch.nn.init.normal_(A, std=0.02)
        B = torch.zeros((out, RANK), dtype=torch.float32)
        A.requires_grad_(True)
        B.requires_grad_(True)
        loras[hk] = (A, B)
        params.extend([A, B])
    opt = torch.optim.AdamW(params, lr=args.lr, betas=(0.9, 0.999), weight_decay=0.0)

    steps_per_epoch = math.ceil(len(train_items) / args.batch)
    total_steps = steps_per_epoch * args.epochs
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=args.lr, total_steps=total_steps, pct_start=10 / total_steps,
        anneal_strategy="cos")

    def run_kl(items, train_mode, limit=None):
        """Mean answer-position KL over items (optionally a subset)."""
        tot, cnt = 0.0, 0
        for it in items[:limit]:
            ids = it["prompt_ids"] + it["answer_ids"]
            with torch.no_grad():
                tl = forward_torch(ids, sd_ins_t)
            if train_mode:
                sl = forward_torch(ids, sd_base_t, loras=loras, scale=scale)
                loss = kl_on_answers(sl, tl, len(it["prompt_ids"]))
                loss.backward()
                tot += float(loss)
            else:
                with torch.no_grad():
                    sl = forward_torch(ids, sd_base_t, loras=loras, scale=scale)
                    tot += float(kl_on_answers(sl, tl, len(it["prompt_ids"])))
            cnt += 1
        return tot / max(cnt, 1)

    log = {"seed": seed, "lr": args.lr, "batch": args.batch, "epochs_max": args.epochs,
           "alpha": ALPHA, "rank": RANK, "scale": scale, "checks": []}
    best_val, best_state, bad_checks = float("inf"), None, 0
    step = 0
    t0 = time.perf_counter()
    stop = False
    for epoch in range(args.epochs):
        order = rng.permutation(len(train_items))
        for bstart in range(0, len(order), args.batch):
            if stop:
                break
            batch = [train_items[i] for i in order[bstart:bstart + args.batch]]
            opt.zero_grad(set_to_none=True)
            run_kl(batch, train_mode=True)
            for p_ in params:
                if p_.grad is not None:
                    p_.grad /= len(batch)
            torch.nn.utils.clip_grad_norm_(params, 1.0)
            opt.step()
            sched.step()
            step += 1
            if step % 25 == 0:
                print(f"seed {seed} step {step}/{total_steps} "
                      f"({time.perf_counter() - t0:.0f}s)", flush=True)
            if step % args.val_every == 0 or step == total_steps:
                val_kl = run_kl(val_items, train_mode=False)
                entry = {"step": step, "epoch": epoch, "val_kl": val_kl,
                         "wall_s": round(time.perf_counter() - t0, 1)}
                log["checks"].append(entry)
                print("val check:", json.dumps(entry), flush=True)
                if val_kl < best_val - 1e-4:
                    best_val = val_kl
                    best_state = {hk: (A.detach().clone(), B.detach().clone())
                                  for hk, (A, B) in loras.items()}
                    bad_checks = 0
                else:
                    bad_checks += 1
                    if bad_checks >= 2:
                        print(f"early stop at step {step}: val KL plateaued", flush=True)
                        stop = True
                        break
        if stop:
            break

    assert best_state is not None
    log["best_val_kl"] = best_val
    log["steps_run"] = step
    log["wall_s"] = round(time.perf_counter() - t0, 1)
    log["peak_rss_mb"] = round(s2.peak_rss_mb(), 1)

    key_of = {hk: sk for sk, hk in lora_keys()}
    flat32, flat16 = {}, {}
    for hk, (A, B) in best_state.items():
        sk = key_of[hk]
        Bf = (B * scale).numpy().astype(np.float32)  # fold alpha/r into B
        Af = A.numpy().astype(np.float32)
        flat32[f"{sk}_A"], flat32[f"{sk}_B"] = Af, Bf
        flat16[f"{sk}_A"] = Af.astype(np.float16).astype(np.float32)
        flat16[f"{sk}_B"] = Bf.astype(np.float16).astype(np.float32)
    np.savez(workdir / f"adapter_seed{seed}.npz", **flat32)
    np.savez(workdir / f"adapter_seed{seed}_fp16.npz", **flat16)
    (workdir / f"train_log_seed{seed}.json").write_text(json.dumps(log, indent=2) + "\n")
    print(f"seed {seed} done: best val KL {best_val:.4f} at step {step}, "
          f"{log['wall_s']}s, peak RSS {log['peak_rss_mb']} MB")


# ---------------------------------------------------------------------------
# eval: score one config on the combined 96 (house NumPy machinery).
# ---------------------------------------------------------------------------

def forward_adapted(ids, sd, adapters):
    """Copy of s2.forward with (X@A.T)@B.T added at adapted linears.

    adapters: {hf_key: (A, B)} fp32 numpy. Validated against the
    unmodified s2.forward via the lora_zero and lora_seed1_dense
    configs."""
    T = len(ids)
    cos, sin = s2.rope_tables(T)
    x = sd["model.embed_tokens.weight"][np.array(ids, dtype=np.int64)]

    def linear(x_, key):
        y = x_ @ sd[key].T
        bkey = key.replace(".weight", ".bias")
        if bkey in sd:
            y = y + sd[bkey]
        if key in adapters:
            A, B = adapters[key]
            y = y + (x_ @ A.T) @ B.T
        return y

    for i in range(s2.LAYERS):
        p = f"model.layers.{i}"
        h = s2.rmsnorm(x, sd[f"{p}.input_layernorm.weight"])
        q = linear(h, f"{p}.self_attn.q_proj.weight").reshape(T, s2.HEADS, s2.HEAD_DIM)
        k = linear(h, f"{p}.self_attn.k_proj.weight").reshape(T, s2.KV_HEADS, s2.HEAD_DIM)
        v = linear(h, f"{p}.self_attn.v_proj.weight").reshape(T, s2.KV_HEADS, s2.HEAD_DIM)
        q, k = s2.apply_rope(q, cos, sin), s2.apply_rope(k, cos, sin)
        k = np.repeat(k, s2.HEADS // s2.KV_HEADS, axis=1)
        v = np.repeat(v, s2.HEADS // s2.KV_HEADS, axis=1)
        att = np.einsum("thd,shd->hts", q, k) / np.sqrt(s2.HEAD_DIM)
        mask = np.triu(np.ones((T, T), dtype=bool), 1)
        att[:, mask] = -1e9
        att = s2.softmax(att)
        o = np.einsum("hts,shd->thd", att, v).reshape(T, s2.HIDDEN)
        x = x + linear(o, f"{p}.self_attn.o_proj.weight")
        h2 = s2.rmsnorm(x, sd[f"{p}.post_attention_layernorm.weight"])
        gate = s2.silu(linear(h2, f"{p}.mlp.gate_proj.weight"))
        up = linear(h2, f"{p}.mlp.up_proj.weight")
        x = x + linear(gate * up, f"{p}.mlp.down_proj.weight")
    x = s2.rmsnorm(x, sd["model.norm.weight"])
    return x @ sd["model.embed_tokens.weight"].T


def score_items_adapted(tok, sd, items, adapters):
    """s2.score_items with forward_adapted swapped in."""
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
        logits = forward_adapted(ids_p + ids_a, sd, adapters)
        off = len(ids_p)
        lp = 0.0
        for j, tok_id in enumerate(ids_a):
            row = logits[off + j - 1].astype(np.float64)
            row = row - row.max()
            e = np.exp(row)
            lp += float(np.log(e[tok_id] / e.sum()))
        first_hit = int(np.argmax(logits[off - 1]) == ids_a[0])
        rows.append({"bucket": s2.BUCKET_LABELS[bucket], "logprob": lp,
                     "first_token_correct": first_hit})
    return rows


def load_adapters(workdir, fname):
    fac = np.load(Path(workdir) / fname)
    key_of = {sk: hk for sk, hk in lora_keys()}
    adapters = {}
    for sk, hk in key_of.items():
        adapters[hk] = (fac[f"{sk}_A"], fac[f"{sk}_B"])
    return adapters


def cmd_eval(args):
    from tokenizers import Tokenizer

    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(str(Path(args.data) / "tokenizer.json"))
    probes = json.loads(Path(args.probes).read_text())
    subsets = ("heldout24", "heldout72_new")

    t0 = time.perf_counter()
    sd = s2.load_all_fp32(args.base)
    adapters = None
    mode = "plain"
    cfg = args.config

    if cfg.startswith("lora_seed"):
        seed = cfg.split("_")[1].replace("seed", "")
        if cfg.endswith("_dense"):
            mode = "dense"
            adapters = load_adapters(workdir, f"adapter_seed{seed}_fp16.npz")
            for hk, (A, B) in adapters.items():
                sd[hk] = sd[hk] + B @ A
            applied = f"base + dense LoRA (seed {seed}, fp16-rounded B@A merged)"
        else:
            fp32 = cfg.endswith("_fp32")
            adapters = load_adapters(
                workdir, f"adapter_seed{seed}.npz" if fp32
                else f"adapter_seed{seed}_fp16.npz")
            mode = "adapted"
            applied = (f"base + LoRA adapter (seed {seed}, "
                       f"{'fp32' if fp32 else 'fp16-rounded'}, hooked (X@A.T)@B.T)")
    elif cfg == "lora_zero":
        adapters = {}
        for _sk, hk in lora_keys():
            W = sd[hk]
            adapters[hk] = (np.zeros((RANK, W.shape[1]), dtype=np.float32),
                            np.zeros((W.shape[0], RANK), dtype=np.float32))
        mode = "adapted"
        applied = "base + zero LoRA adapter through the hooked forward (sanity)"
    elif cfg in ("uniform_noembed", "lite_noembed", "uniform_vfp16", "lite_vfp16"):
        name = "uniform_rank32" if cfg.startswith("uniform") else "mlp_behemoth_lite"
        fac_path = Path(args.heldout_workdir) / f"factors_{name}.npz"
        if not fac_path.exists():
            fac_path = Path(args.stage2_workdir) / f"factors_{name}.npz"
        fac = np.load(fac_path)
        key_of = {sk: hk for sk, hk, _ in s2.matrix_keys()}
        drop_embed = cfg.endswith("_noembed")
        round_v = cfg.endswith("_vfp16")
        for store_key, hf_key in key_of.items():
            ukey = f"{store_key}_U"
            if ukey not in fac:
                continue
            if drop_embed and store_key == "embed":
                continue
            U, V = fac[ukey], fac[f"{store_key}_V"]
            if round_v:
                V = V.astype(np.float16).astype(np.float32)
            sd[hf_key] = sd[hf_key] + (U @ V.T)
        applied = (f"base + factored delta ({name})"
                   + (" with embedding delta dropped (blocks-only)" if drop_embed else "")
                   + (" with V rounded through fp16" if round_v else ""))
    else:
        raise ValueError(f"unknown config {cfg}")
    load_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    rows = []
    for subset in subsets:
        sub_items = [(it["bucket"], it["prompt"], it["answer"])
                     for it in probes if it["subset"] == subset]
        if mode == "adapted":
            sub_rows = score_items_adapted(tok, sd, sub_items, adapters)
        else:
            sub_rows = s2.score_items(tok, sd, sub_items)
        for r in sub_rows:
            r["subset"] = subset
        rows.extend(sub_rows)
    eval_s = time.perf_counter() - t1
    del sd
    gc.collect()

    out = {
        "config": cfg,
        "probe_set": "heldout96_spark",
        "applied": applied,
        "n_items": len(rows),
        "scores": s2.aggregate(rows),
        "scores_by_subset": {s: s2.aggregate([r for r in rows if r["subset"] == s])
                             for s in subsets},
        "per_item": rows,
        "load_wall_s": round(load_s, 2),
        "eval_wall_s": round(eval_s, 2),
        "wall_s": round(time.perf_counter() - t0, 2),
        "peak_rss_mb": round(s2.peak_rss_mb(), 1),
    }
    (workdir / f"eval_{cfg}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("config", "n_items", "wall_s", "peak_rss_mb")},
                     indent=2))
    print("combined:", json.dumps(out["scores"]["overall"], indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("prep")
    p.add_argument("--base", required=True)
    p.add_argument("--instruct", required=True)
    p.add_argument("--probes", required=True)
    p.add_argument("--distill", required=True)
    p.add_argument("--data", default=str(Path.home() / "qwen-test" / "data"))
    p.add_argument("--heldout96-workdir", required=True)
    p.add_argument("--workdir", required=True)
    p.add_argument("--threads", type=int, default=10)
    p.set_defaults(fn=cmd_prep)

    t = sub.add_parser("train")
    t.add_argument("--base", required=True)
    t.add_argument("--instruct", required=True)
    t.add_argument("--workdir", required=True)
    t.add_argument("--seed", type=int, required=True)
    t.add_argument("--lr", type=float, default=2e-4)
    t.add_argument("--batch", type=int, default=8)
    t.add_argument("--epochs", type=int, default=6)
    t.add_argument("--val-every", type=int, default=100)
    t.add_argument("--threads", type=int, default=10)
    t.set_defaults(fn=cmd_train)

    e = sub.add_parser("eval")
    e.add_argument("--config", required=True)
    e.add_argument("--base", required=True)
    e.add_argument("--probes", required=True)
    e.add_argument("--data", default=str(Path.home() / "qwen-test" / "data"))
    e.add_argument("--stage2-workdir", required=True)
    e.add_argument("--heldout-workdir", required=True)
    e.add_argument("--workdir", required=True)
    e.set_defaults(fn=cmd_eval)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
