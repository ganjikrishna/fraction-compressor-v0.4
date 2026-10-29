"""Recovery tuning: a short training pass on the shipped factored patch.

Design: results/recovery_tuning_design.md (frozen before training).

Question: the matched-byte LoRA baseline beat the factored patch but cost
1,014 steps per seed. Does a 101-step tune-up of the lite patch's own
factors recover much of the gap, and does any of it survive re-quantizing
the trained delta back into the exact 1-bit factored format at the exact
same byte count?

Subcommands:
  train    (voice-clone venv, torch): U/V trainable factors in the lite
           parameterization, base frozen, soft forward KL
           (teacher||student, T=1) at teacher-answer positions on the
           existing in-style distillation set, teacher online, 101 steps
           at batch 8, AdamW lr 2e-5 OneCycle (panel-set), seed
           20261028, final state taken (no checkpoint selection).
           Two inits (--init): "patch" starts from the shipped
           mlp_behemoth_lite factors (the headline run); "control" is
           the panel-mandated matched control, U drawn N(0, 0.02) and
           V zero (initial delta exactly zero, the LoRA baseline's
           starting point), identical in every other way. Val KL is
           logged on the full 150-item split at steps 0 and 101 and on
           a fixed 30-item subset every 10 steps, for transparency
           only. Before training, the factored torch forward is
           validated against the stored NumPy scores of the matching
           config (lite for patch init, base for control init) on 12
           eval items.
  requant  (qwen-test venv, numpy): form each trained delta
           D' = U @ V.T and re-quantize with factored.quantize_delta at
           the shipped ranks; verify the priced total equals the lite
           patch's 19,358,176 bytes exactly. Also emits the fp16
           diagnostic factor file (trained factors rounded through
           fp16, priced honestly).
  eval     (qwen-test venv, numpy): score one factors file on the
           combined 96 held-out probes with the house NumPy machinery
           (dense apply, same as every factored row), with extended
           per-item fields for the first-token vs continuation split.

The script lives next to alien_sweep_stage2.py and lora_baseline.py both
in the repo (examples/) and on Flash (~/fc-v04-sweep/); it imports those
modules unchanged for the forward ports, the KL objective, the weight
loader, and the metrics.
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
import factored  # noqa: E402  (resolved via s2's sys.path setup)
import lora_baseline as lb  # noqa: E402

SEED = 20261028
STEPS = 101
BATCH = 8
LR = 2e-5
LITE_BYTES = 19358176

KEY_OF = {sk: hk for sk, hk, _ in s2.matrix_keys()}  # store_key -> hf_key
NAME_OF = {sk: nm for sk, _hk, nm in s2.matrix_keys()}  # store_key -> layer name


def rank_map_by_name(fac):
    """Lite rank map by layer name, read off the shipped factors file."""
    out = {}
    for sk in KEY_OF:
        ukey = f"{sk}_U"
        out[NAME_OF[sk]] = int(fac[ukey].shape[1]) if ukey in fac else 0
    return out


# ---------------------------------------------------------------------------
# PyTorch forward with factored hooks. Same op order as
# lora_baseline.forward_torch; the patch contributes (X @ V) @ U.T at each
# factored linear (the dense apply's x @ (U @ V.T).T), and at the tied
# embedding in both places (lookup rows U[ids] @ V.T added to the
# embedding, (X @ V) @ U.T added to the logits), which is exactly what
# the dense numpy apply computes.
# ---------------------------------------------------------------------------

def forward_factored(ids, sd, facs):
    import torch
    device = sd["model.embed_tokens.weight"].device
    T = len(ids)
    cos, sin = lb._rope_tables_t(torch, T, device)
    E = sd["model.embed_tokens.weight"]
    ids_t = torch.tensor(ids, dtype=torch.long, device=device)
    x = E[ids_t]
    if "embed" in facs:
        Ue, Ve = facs["embed"]
        x = x + Ue[ids_t] @ Ve.T

    def linear(x_, key, store_key):
        y = x_ @ sd[key].T
        bkey = key.replace(".weight", ".bias")
        if bkey in sd:
            y = y + sd[bkey]
        if store_key in facs:
            U, V = facs[store_key]
            # The delta is D = U @ V.T added to W, and the layer computes
            # x @ W.T, so the contribution is x @ D.T = (x @ V) @ U.T.
            # (factored.apply_factored's (X @ U) @ V.T is x @ D, the
            # untransposed convention; the eval pipeline's dense apply is
            # the semantics every published row uses, so we match that.)
            y = y + (x_ @ V) @ U.T
        return y

    for i in range(s2.LAYERS):
        p = f"model.layers.{i}"
        sk = lambda nm: f"b{i:02d}_{nm.replace('.', '_')}"  # noqa: E731
        h = lb._rmsnorm_t(x, sd[f"{p}.input_layernorm.weight"])
        q = linear(h, f"{p}.self_attn.q_proj.weight", sk("attn.q_proj")).reshape(
            T, s2.HEADS, s2.HEAD_DIM)
        k = linear(h, f"{p}.self_attn.k_proj.weight", sk("attn.k_proj")).reshape(
            T, s2.KV_HEADS, s2.HEAD_DIM)
        v = linear(h, f"{p}.self_attn.v_proj.weight", sk("attn.v_proj")).reshape(
            T, s2.KV_HEADS, s2.HEAD_DIM)
        q, k = lb._apply_rope_t(q, cos, sin), lb._apply_rope_t(k, cos, sin)
        k = k.repeat_interleave(s2.HEADS // s2.KV_HEADS, dim=1)
        v = v.repeat_interleave(s2.HEADS // s2.KV_HEADS, dim=1)
        att = torch.einsum("thd,shd->hts", q, k) / math.sqrt(s2.HEAD_DIM)
        mask = torch.triu(torch.ones((T, T), dtype=torch.bool, device=device), 1)
        att = att.masked_fill(mask, -1e9)
        att = lb._softmax_t(att)
        o = torch.einsum("hts,shd->thd", att, v).reshape(T, s2.HIDDEN)
        x = x + linear(o, f"{p}.self_attn.o_proj.weight", sk("attn.o_proj"))
        h2 = lb._rmsnorm_t(x, sd[f"{p}.post_attention_layernorm.weight"])
        gate = torch.nn.functional.silu(
            linear(h2, f"{p}.mlp.gate_proj.weight", sk("mlp.gate")))
        up = linear(h2, f"{p}.mlp.up_proj.weight", sk("mlp.up"))
        x = x + linear(gate * up, f"{p}.mlp.down_proj.weight", sk("mlp.down"))
    x = lb._rmsnorm_t(x, sd["model.norm.weight"])
    logits = x @ E.T
    if "embed" in facs:
        Ue, Ve = facs["embed"]
        logits = logits + (x @ Ve) @ Ue.T
    return logits


def torch_factored_item_logprobs(tok, sd_t, facs, items):
    """lb.torch_item_logprobs with forward_factored swapped in."""
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
            logits = forward_factored(ids_p + ids_a, sd_t, facs)
            off = len(ids_p)
            lp = 0.0
            for j, tok_id in enumerate(ids_a):
                row = torch.log_softmax(logits[off + j - 1].double(), dim=-1)
                lp += float(row[tok_id])
            rows.append({"bucket": s2.BUCKET_LABELS[bucket], "logprob": lp})
    return rows


# ---------------------------------------------------------------------------
# train
# ---------------------------------------------------------------------------

def cmd_train(args):
    import torch
    from tokenizers import Tokenizer

    torch.set_num_threads(args.threads)
    torch.manual_seed(SEED)
    rng = np.random.default_rng(SEED)
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    tag = args.tag

    dataset = json.loads(Path(args.dataset).read_text())
    train_items = [it for it in dataset if it["split"] == "train"]
    val_items = [it for it in dataset if it["split"] == "val"]
    val_subset = val_items[:30]  # fixed trajectory subset (amendment)
    print(f"train {len(train_items)} val {len(val_items)}", flush=True)

    fac0 = np.load(args.factors)
    shapes = {}
    for sk in KEY_OF:
        ukey = f"{sk}_U"
        if ukey in fac0:
            shapes[sk] = (fac0[ukey].shape, fac0[f"{sk}_V"].shape)
    print(f"factored matrices: {len(shapes)}", flush=True)

    sd_base_t = lb.to_torch(s2.load_all_fp32(args.base))

    facs = {}
    params = []
    init = {}
    for sk, (ushape, vshape) in shapes.items():
        if args.init == "patch":
            U0 = fac0[f"{sk}_U"].astype(np.float32)
            V0 = fac0[f"{sk}_V"].astype(np.float32)
            U = torch.from_numpy(np.ascontiguousarray(U0)).clone()
            V = torch.from_numpy(np.ascontiguousarray(V0)).clone()
        elif args.init == "control":
            # Panel-mandated matched control: U random N(0, 0.02) (the
            # LoRA baseline's A init), V zero, so the initial delta is
            # exactly zero everywhere.
            U = torch.empty(ushape, dtype=torch.float32)
            torch.nn.init.normal_(U, std=0.02)
            V = torch.zeros(vshape, dtype=torch.float32)
            U0, V0 = U.numpy().copy(), V.numpy().copy()
        else:
            raise ValueError(args.init)
        U.requires_grad_(True)
        V.requires_grad_(True)
        init[sk] = (U0, V0)
        facs[sk] = (U, V)
        params.extend([U, V])

    # --- Forward validation: factored torch forward vs stored NumPy
    # scores of the matching config on 12 eval items (same pick as the
    # LoRA prep validation). Patch init must reproduce lite; the control
    # init has a zero delta, so it must reproduce base. ---
    ref_name = "eval_mlp_behemoth_lite.json" if args.init == "patch" else "eval_base.json"
    tok = Tokenizer.from_file(str(Path(args.data) / "tokenizer.json"))
    probes = json.loads(Path(args.probes).read_text())
    stored = json.loads((Path(args.heldout96_workdir) / ref_name).read_text())
    ordered = ([it for it in probes if it["subset"] == "heldout24"]
               + [it for it in probes if it["subset"] == "heldout72_new"])
    stored_rows = stored["per_item"]
    assert len(stored_rows) == len(ordered) == 96
    pick = [i for i in range(96) if i % 8 == 0]
    items = [(ordered[i]["bucket"], ordered[i]["prompt"], ordered[i]["answer"])
             for i in pick]
    mine = torch_factored_item_logprobs(tok, sd_base_t, facs, items)
    diffs = []
    for row_idx, i in enumerate(pick):
        ref = stored_rows[i]
        assert ref["bucket"] == mine[row_idx]["bucket"], (i, ref, mine[row_idx])
        diffs.append(abs(mine[row_idx]["logprob"] - ref["logprob"]))
    fwd_val = {"reference": ref_name, "n_items": len(pick),
               "max_abs_logprob_diff_vs_numpy": max(diffs),
               "mean_abs_logprob_diff_vs_numpy": float(np.mean(diffs))}
    print("forward validation:", json.dumps(fwd_val, indent=2), flush=True)
    assert max(diffs) < 5e-3, f"factored torch forward mismatch: {max(diffs)}"

    sd_ins_t = lb.to_torch(s2.load_all_fp32(args.instruct))

    opt = torch.optim.AdamW(params, lr=LR, betas=(0.9, 0.999), weight_decay=0.0)
    sched = torch.optim.lr_scheduler.OneCycleLR(
        opt, max_lr=LR, total_steps=STEPS, pct_start=10 / STEPS,
        anneal_strategy="cos")

    def run_kl(batch_items, train_mode):
        tot, cnt = 0.0, 0
        for it in batch_items:
            ids = it["prompt_ids"] + it["answer_ids"]
            with torch.no_grad():
                tl = forward_factored(ids, sd_ins_t, {})
            if train_mode:
                sl = forward_factored(ids, sd_base_t, facs)
                loss = lb.kl_on_answers(sl, tl, len(it["prompt_ids"]))
                loss.backward()
                tot += float(loss)
            else:
                with torch.no_grad():
                    sl = forward_factored(ids, sd_base_t, facs)
                    tot += float(lb.kl_on_answers(sl, tl, len(it["prompt_ids"])))
            cnt += 1
        return tot / max(cnt, 1)

    log = {"stage": "recovery_tuning_train", "tag": tag, "init": args.init,
           "seed": SEED, "lr": LR, "batch": BATCH, "steps_budget": STEPS,
           "init_factors": str(args.factors) if args.init == "patch" else
           "random/zero control (U ~ N(0, 0.02), V = 0), shapes from shipped lite factors",
           "forward_validation": fwd_val, "val_checks": [], "val_curve": []}
    t0 = time.perf_counter()
    step = 0
    order = rng.permutation(len(train_items))

    def log_val(step_now):
        vk = run_kl(val_items, train_mode=False)
        log["val_checks"].append({"step": step_now, "val_kl": vk,
                                  "wall_s": round(time.perf_counter() - t0, 1)})
        print("val check:", json.dumps(log["val_checks"][-1]), flush=True)
        vc = run_kl(val_subset, train_mode=False)
        log["val_curve"].append({"step": step_now, "val_kl_subset30": vc,
                                 "wall_s": round(time.perf_counter() - t0, 1)})
        print("val curve:", json.dumps(log["val_curve"][-1]), flush=True)

    log_val(0)
    done = False
    for bstart in range(0, len(order), BATCH):
        if done:
            break
        batch = [train_items[i] for i in order[bstart:bstart + BATCH]]
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
            print(f"step {step}/{STEPS} ({time.perf_counter() - t0:.0f}s)", flush=True)
        if step % 10 == 0 and step < STEPS:
            vc = run_kl(val_subset, train_mode=False)
            log["val_curve"].append({"step": step, "val_kl_subset30": vc,
                                     "wall_s": round(time.perf_counter() - t0, 1)})
            print("val curve:", json.dumps(log["val_curve"][-1]), flush=True)
        if step >= STEPS:
            done = True
    log_val(STEPS)
    log["steps_run"] = step
    log["wall_s"] = round(time.perf_counter() - t0, 1)
    log["peak_rss_mb"] = round(s2.peak_rss_mb(), 1)

    flat = {}
    drift = {}
    for sk, (U, V) in facs.items():
        U0, V0 = init[sk]
        Un, Vn = U.detach().numpy(), V.detach().numpy()
        flat[f"{sk}_U"], flat[f"{sk}_V"] = Un, Vn
        drift[sk] = {"U_max_abs_change": float(np.abs(Un - U0).max()),
                     "V_max_abs_change": float(np.abs(Vn - V0).max())}
    log["drift_max_U"] = max(d["U_max_abs_change"] for d in drift.values())
    log["drift_max_V"] = max(d["V_max_abs_change"] for d in drift.values())
    np.savez(workdir / f"factors_{tag}_trained.npz", **flat)
    (workdir / f"train_log_{tag}.json").write_text(json.dumps(log, indent=2) + "\n")
    print(f"train done ({tag}, init={args.init}): {step} steps, {log['wall_s']}s, "
          f"peak RSS {log['peak_rss_mb']} MB, "
          f"val KL {log['val_checks'][0]['val_kl']:.4f} -> "
          f"{log['val_checks'][-1]['val_kl']:.4f}")


# ---------------------------------------------------------------------------
# requant
# ---------------------------------------------------------------------------

def cmd_requant(args):
    workdir = Path(args.workdir)
    tag = args.tag
    trained = np.load(workdir / f"factors_{tag}_trained.npz")
    ranks = rank_map_by_name(trained)

    header, _off = s2.load_header(args.base)
    shapes = {sk: tuple(header[hk]["shape"]) for sk, hk in KEY_OF.items()}
    pricing_table = []
    for sk in KEY_OF:
        r = ranks[NAME_OF[sk]]
        pricing_table.append({
            "store_key": sk, "hf_key": KEY_OF[sk], "name": NAME_OF[sk],
            "rank": int(r), "shape": list(shapes[sk]),
            "bytes": int(factored.storage_bytes(r, shapes[sk])),
            "stored": f"{sk}_U" in trained,
        })
    total = sum(row["bytes"] for row in pricing_table)
    print(f"priced total at lite rank map: {total} (target {LITE_BYTES})")
    assert total == LITE_BYTES, total

    out_q, out_16 = {}, {}
    rel_errs = {}
    t0 = time.perf_counter()
    for sk in KEY_OF:
        ukey = f"{sk}_U"
        if ukey not in trained:
            continue
        U = trained[ukey].astype(np.float64)
        V = trained[f"{sk}_V"].astype(np.float64)
        D = U @ V.T
        q = factored.quantize_delta(D, ranks[NAME_OF[sk]])
        out_q[ukey] = q["U"].astype(np.float32)
        out_q[f"{sk}_V"] = q["V"].astype(np.float32)
        rel_errs[sk] = float(np.linalg.norm(q["U"] @ q["V"].T - D)
                             / max(np.linalg.norm(D), 1e-12))
        out_16[ukey] = trained[ukey].astype(np.float16).astype(np.float32)
        out_16[f"{sk}_V"] = trained[f"{sk}_V"].astype(np.float16).astype(np.float32)
        print(f"requant {sk} rank {ranks[NAME_OF[sk]]} "
              f"rel_frobenius_err {rel_errs[sk]:.4f}", flush=True)
    fp16_price = int(sum(2 * trained[k].size for k in trained.files))
    np.savez(workdir / f"factors_{tag}_requant.npz", **out_q)
    np.savez(workdir / f"factors_{tag}_fp16.npz", **out_16)
    rec = {"stage": "recovery_tuning_requant", "tag": tag,
           "pricing_table": pricing_table,
           "bytes_requantized": int(total),
           "bytes_target": LITE_BYTES,
           "bytes_match": int(total) == LITE_BYTES,
           "fp16_diagnostic_bytes": fp16_price,
           "rel_frobenius_err_mean": float(np.mean(list(rel_errs.values()))),
           "rel_frobenius_err_max": float(np.max(list(rel_errs.values()))),
           "rel_frobenius_err_by_matrix": rel_errs,
           "wall_s": round(time.perf_counter() - t0, 1),
           "peak_rss_mb": round(s2.peak_rss_mb(), 1)}
    (workdir / f"requant_record_{tag}.json").write_text(json.dumps(rec, indent=2) + "\n")
    print(json.dumps({k: rec[k] for k in
                      ("bytes_requantized", "bytes_match", "fp16_diagnostic_bytes",
                       "rel_frobenius_err_mean", "rel_frobenius_err_max", "wall_s")},
                     indent=2))


# ---------------------------------------------------------------------------
# eval: house NumPy scoring with extended per-item fields.
# ---------------------------------------------------------------------------

def score_items_ext(tok, sd, items):
    """s2.score_items plus first-token logprob and answer length per item."""
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
        logits = s2.forward(ids_p + ids_a, sd)
        off = len(ids_p)
        lp = 0.0
        first_lp = None
        for j, tok_id in enumerate(ids_a):
            row = logits[off + j - 1].astype(np.float64)
            row = row - row.max()
            e = np.exp(row)
            tok_lp = float(np.log(e[tok_id] / e.sum()))
            if j == 0:
                first_lp = tok_lp
            lp += tok_lp
        first_hit = int(np.argmax(logits[off - 1]) == ids_a[0])
        rows.append({"bucket": s2.BUCKET_LABELS[bucket], "logprob": lp,
                     "first_token_correct": first_hit,
                     "first_token_logprob": first_lp,
                     "n_answer_tokens": len(ids_a)})
    return rows


def aggregate_ext(rows):
    def agg(rs):
        base = s2.aggregate(rs)["overall"]
        cont_num = sum(r["logprob"] - r["first_token_logprob"]
                       for r in rs if r["n_answer_tokens"] >= 2)
        cont_den = sum(r["n_answer_tokens"] - 1
                       for r in rs if r["n_answer_tokens"] >= 2)
        base["first_token_mean_logprob"] = (
            sum(r["first_token_logprob"] for r in rs) / len(rs) if rs else 0.0)
        base["continuation_mean_logprob_per_token"] = (
            cont_num / cont_den if cont_den else 0.0)
        base["n_continuation_tokens"] = int(cont_den)
        return base
    per_bucket = {}
    for b in ("knowledge", "instruction", "math"):
        per_bucket[b] = agg([r for r in rows if r["bucket"] == b])
    return {"overall": agg(rows), "per_bucket": per_bucket}


def cmd_eval(args):
    from tokenizers import Tokenizer

    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(str(Path(args.data) / "tokenizer.json"))
    probes = json.loads(Path(args.probes).read_text())
    subsets = ("heldout24", "heldout72_new")

    t0 = time.perf_counter()
    sd = s2.load_all_fp32(args.base)
    fac = np.load(args.factors)
    for store_key, hf_key in KEY_OF.items():
        ukey = f"{store_key}_U"
        if ukey not in fac:
            continue
        U, V = fac[ukey], fac[f"{store_key}_V"]
        sd[hf_key] = sd[hf_key] + (U @ V.T)
    applied = f"base + factored delta from {args.factors} (dense apply)"
    load_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    rows = []
    for subset in subsets:
        sub_items = [(it["bucket"], it["prompt"], it["answer"])
                     for it in probes if it["subset"] == subset]
        sub_rows = score_items_ext(tok, sd, sub_items)
        for r in sub_rows:
            r["subset"] = subset
        rows.extend(sub_rows)
    eval_s = time.perf_counter() - t1
    del sd
    gc.collect()

    out = {"config": args.label,
           "probe_set": "heldout96_spark",
           "applied": applied,
           "n_items": len(rows),
           "scores": aggregate_ext(rows),
           "scores_by_subset": {
               s: aggregate_ext([r for r in rows if r["subset"] == s])
               for s in subsets},
           "per_item": rows,
           "load_wall_s": round(load_s, 2),
           "eval_wall_s": round(eval_s, 2),
           "wall_s": round(time.perf_counter() - t0, 2),
           "peak_rss_mb": round(s2.peak_rss_mb(), 1)}
    (workdir / f"eval_{args.label}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("config", "n_items", "wall_s", "peak_rss_mb")},
                     indent=2))
    print("combined:", json.dumps(out["scores"]["overall"], indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    t = sub.add_parser("train")
    t.add_argument("--base", required=True)
    t.add_argument("--instruct", required=True)
    t.add_argument("--factors", required=True)
    t.add_argument("--dataset", required=True)
    t.add_argument("--probes", required=True)
    t.add_argument("--data", default=str(Path.home() / "qwen-test" / "data"))
    t.add_argument("--heldout96-workdir", required=True)
    t.add_argument("--workdir", required=True)
    t.add_argument("--init", choices=("patch", "control"), required=True)
    t.add_argument("--tag", required=True)
    t.add_argument("--threads", type=int, default=10)
    t.set_defaults(fn=cmd_train)

    r = sub.add_parser("requant")
    r.add_argument("--base", required=True)
    r.add_argument("--workdir", required=True)
    r.add_argument("--tag", required=True)
    r.set_defaults(fn=cmd_requant)

    e = sub.add_parser("eval")
    e.add_argument("--label", required=True)
    e.add_argument("--factors", required=True)
    e.add_argument("--base", required=True)
    e.add_argument("--probes", required=True)
    e.add_argument("--data", default=str(Path.home() / "qwen-test" / "data"))
    e.add_argument("--workdir", required=True)
    e.set_defaults(fn=cmd_eval)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
