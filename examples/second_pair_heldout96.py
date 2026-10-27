"""Second pair (SmolLM2-360M): byte-matched lite + 96-item confirmation.

    # variant generation, on the Muse VM (Baseten connector):
    python3 examples/second_pair_heldout96.py variant-gen \
        --stage2-results results/second_pair_stage2.json \
        --record /tmp/second_pair_variant_record.json \
        --variant-out /tmp/second_pair_variant.json
    # on Flash, with the qwen-test venv:
    python3 second_pair_heldout96.py build-variant \
        --base ~/qwen-test/data/smollm2-360m.safetensors \
        --instruct ~/qwen-test/data/smollm2-360m-instruct.safetensors \
        --variant /tmp/second_pair_variant.json \
        --stage2-workdir ~/fc-v04-sweep2/stage2 \
        --workdir ~/fc-v04-sweep2/heldout96
    python3 second_pair_heldout96.py eval --config base \
        --base ... --instruct ... --probes heldout96_probes_spark.json \
        --stage2-workdir ~/fc-v04-sweep2/stage2 \
        --workdir ~/fc-v04-sweep2/heldout96
    # ... eval full_delta, uniform_rank32, the winner, and the variant
    python3 second_pair_heldout96.py assemble \
        --variant /tmp/second_pair_variant.json \
        --gen-record /tmp/second_pair_variant_record.json \
        --stage2-results /tmp/second_pair_stage2.json \
        --stage2-workdir ~/fc-v04-sweep2/stage2 \
        --workdir ~/fc-v04-sweep2/heldout96 \
        --out ~/fc-v04-sweep2/second_pair_heldout96.json

Phase 2, final step: the Stage 2 winner on the SmolLM2 pair is only
the headline if a byte-fair version of it beats the human uniform
rank-32 recipe on fresh items. Exactly as in Phase 1's guard:

- variant-gen asks Muse Spark Open (Baseten, the same model that
  proposed the recipes) for a byte-matched variant of the winner:
  same style, re-priced on the REAL SmolLM2 shapes, total <= the
  uniform recipe's real byte budget. Over-budget or style-breaking
  attempts are fed back with the computed overage (max 3 attempts);
  every attempt is recorded and every call is logged to
  results/api_usage_log.jsonl. If the winner already fits the
  budget, no variant is needed and the winner itself is the
  byte-fair contender (recorded as such).
- build-variant constructs the variant's factors on Flash with one
  exact SVD per matrix (second_pair_stage2.quantize_from_svd) and
  validates its real-shape price the Stage 2 way.
- eval scores base, full_delta, uniform_rank32, the winner and the
  variant on the combined 96 fresh probe items from Phase 1
  (data/heldout96_probes_spark.json), with the same SmolLM2 forward,
  chat format and metrics as second_pair_stage2. The winner is
  labeled byte-unfair wherever its real price exceeds the budget.
"""

import argparse
import gc
import importlib.util
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
for cand in (HERE, ROOT / "src", HERE / "src"):
    if (cand / "factored.py").exists() and str(cand) not in sys.path:
        sys.path.insert(0, str(cand))

import factored  # noqa: E402
import second_pair_stage2 as sp  # noqa: E402

BASETEN_MODEL = "meta-models/muse-spark-open-1026"
BASETEN_PROVIDER = "baseten"
SUBSETS = ("heldout24", "heldout72_new")


def now_z():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# variant-gen (Baseten, Muse VM)
# ---------------------------------------------------------------------------

def _load_baseten_helper():
    helper = Path.home() / "workspace/custom-connectors/custom.baseten/bin/baseten_api.py"
    spec = importlib.util.spec_from_file_location("baseten_api", helper)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def log_usage(usage, purpose):
    entry = {
        "provider": BASETEN_PROVIDER,
        "model": BASETEN_MODEL,
        "time": now_z(),
        "purpose": purpose,
        "prompt_tokens": (usage or {}).get("prompt_tokens"),
        "completion_tokens": (usage or {}).get("completion_tokens"),
        "total_tokens": (usage or {}).get("total_tokens"),
    }
    log = ROOT / "results" / "api_usage_log.jsonl"
    log.parent.mkdir(parents=True, exist_ok=True)
    with open(log, "a") as f:
        f.write(json.dumps(entry) + "\n")
    return entry


def extract_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    starts = [i for i in (text.find("{"), text.find("[")) if i >= 0]
    if not starts:
        raise ValueError("no JSON found in reply")
    start = min(starts)
    obj, _ = json.JSONDecoder().raw_decode(text[start:])
    return obj


def style_rules(winner_ranks):
    zeros = [n for n, r in winner_ranks.items() if r == 0]
    top3 = sorted(winner_ranks, key=lambda n: -winner_ranks[n])[:3]
    return zeros, top3


def variant_prompt(winner_name, winner_ranks, winner_bytes, budget, feedback=None):
    zeros, top3 = style_rules(winner_ranks)
    lines = [
        "You are rebalancing a compression recipe for a factored 1-bit weight-delta format. "
        "A recipe assigns an integer rank to each of 8 layer types of the SmolLM2-360M model. "
        "The rank for a layer type applies to that matrix in every transformer block, so the "
        "recipe's true stored size is the sum over all 225 real matrices, priced per matrix as:",
        "",
        "  bytes(matrix, r) = ceil(rows * r / 8) + 4 * rows + 2 * cols * r   (the 4 * rows term is paid even at r = 0)",
        "",
        "Real shapes (rows x cols), and how many matrices of each type exist:",
    ]
    for name, (rows, cols) in sp.SHAPES.items():
        cnt = sp.COUNTS[name]
        base_cost = cnt * 4 * rows
        per_rank = cnt * (rows // 8 + 2 * cols)
        lines.append(f"  {name}: {rows} x {cols}, x{cnt} (total cost at rank r: {base_cost:,} + {per_rank:,}*r)")
    lines += [
        "",
        f"The current winning recipe, {winner_name}, is:",
        json.dumps(winner_ranks),
        f"It prices at {winner_bytes:,} bytes on the real shapes. The budget is {budget:,} bytes "
        f"(that is what the human uniform rank-32 recipe costs on the same real shapes), so "
        f"the variant must shed at least {winner_bytes - budget:,} bytes of rank cost.",
        "",
        "Propose ONE rebalanced variant that keeps the winner's style:",
    ]
    if zeros:
        lines.append(f"- These layer types stay at rank 0: {', '.join(zeros)}.")
    lines.append(f"- The highest-ranked layer types stay the same three, in some order: {', '.join(top3)}.")
    lines.append("- No rank may exceed the winner's rank for that layer type.")
    lines.append("- Every rank is an integer >= 0.")
    lines.append(f"- The total priced size on the real shapes must be <= {budget:,} bytes. Check "
                 "your arithmetic with the per-type costs above before answering.")
    lines += [
        "",
        "Reply with ONLY a JSON object, no markdown fences, no commentary, in exactly this shape:",
        '{"name": "<short name>", "reason": "<one sentence>", "ranks": {"embed": 0, '
        '"attn.q_proj": 0, "attn.k_proj": 0, "attn.v_proj": 0, "attn.o_proj": 0, '
        '"mlp.gate": 0, "mlp.up": 0, "mlp.down": 0}}',
        "Replace the zeros with your ranks.",
    ]
    if feedback:
        lines += ["", feedback]
    return "\n".join(lines)


def cmd_variant_gen(args):
    stage2 = json.loads(Path(args.stage2_results).read_text())
    winner_name = stage2["winner"]["name"]
    if winner_name == "uniform_rank32":
        raise RuntimeError("Stage 2 winner is the human uniform recipe itself; "
                           "there is no alien winner to byte-match (honest outcome rule)")
    entries = {e["name"]: e for e in stage2["recipes"] + [stage2["human_baseline"]]}
    winner_ranks = entries[winner_name]["ranks"]
    winner_bytes = entries[winner_name]["real_shape_bytes"]
    budget = entries["uniform_rank32"]["real_shape_bytes"]

    record = {"winner": winner_name, "winner_ranks": winner_ranks,
              "winner_real_shape_bytes": winner_bytes, "budget_bytes": budget,
              "started": now_z(), "attempts": []}

    if winner_bytes <= budget:
        record["variant"] = {"name": winner_name, "ranks": winner_ranks,
                             "real_shape_bytes": winner_bytes,
                             "note": "winner already fits the uniform budget; "
                                     "no byte-matched variant needed"}
        Path(args.record).write_text(json.dumps(record, indent=2) + "\n")
        Path(args.variant_out).write_text(json.dumps(record["variant"], indent=2) + "\n")
        print(f"winner {winner_name} already within budget ({winner_bytes:,} <= {budget:,}); "
              "no variant call needed")
        return

    helper = _load_baseten_helper()
    zeros, top3 = style_rules(winner_ranks)
    feedback = None
    for attempt in range(1, 4):
        prompt = variant_prompt(winner_name, winner_ranks, winner_bytes, budget, feedback)
        payload = {"model": BASETEN_MODEL,
                   "messages": [{"role": "user", "content": prompt}],
                   "max_tokens": 12000}
        t0 = time.perf_counter()
        resp = helper.call("POST", "/v1/chat/completions", payload)
        elapsed = round(time.perf_counter() - t0, 2)
        if "http_error" in resp:
            raise RuntimeError(f"baseten HTTP {resp['http_error']}: {resp.get('body', '')[:500]}")
        usage = resp.get("usage") or {}
        log_usage(usage, f"second_pair_bytematched_variant_attempt{attempt}")
        content = resp["choices"][0]["message"].get("content") or ""
        entry = {"attempt": attempt, "usage": usage, "elapsed_s": elapsed,
                 "raw_content": content}
        record["attempts"].append(entry)
        try:
            obj = extract_json(content)
            ranks = {k: int(v) for k, v in obj["ranks"].items()}
            if set(ranks) != set(sp.SHAPES):
                raise ValueError(f"rank keys mismatch: {sorted(ranks)}")
            if any(v < 0 for v in ranks.values()):
                raise ValueError("negative rank")
            for n in zeros:
                if ranks[n] != 0:
                    raise ValueError(f"style break: {n} must stay rank 0, got {ranks[n]}")
            for n, r in ranks.items():
                if r > winner_ranks[n]:
                    raise ValueError(f"style break: {n} rank {r} exceeds winner's {winner_ranks[n]}")
            new_top3 = sorted(ranks, key=lambda n: -ranks[n])[:3]
            if set(new_top3) != set(top3):
                raise ValueError(f"style break: top-3 layer types changed {new_top3} != {top3}")
            total = sp.price_real(ranks)
            entry["parsed_name"] = obj.get("name")
            entry["ranks"] = ranks
            entry["real_shape_bytes"] = total
            entry["within_budget"] = total <= budget
            if total <= budget:
                record["variant"] = {"name": obj.get("name"), "reason": obj.get("reason"),
                                     "ranks": ranks, "real_shape_bytes": total,
                                     "budget_bytes": budget}
                Path(args.record).write_text(json.dumps(record, indent=2) + "\n")
                Path(args.variant_out).write_text(json.dumps(record["variant"], indent=2) + "\n")
                print(f"variant: {obj.get('name')} ranks={ranks} real_bytes={total:,} budget={budget:,}")
                return
            feedback = (f"Your attempt {attempt} priced at {total:,} bytes on the real shapes, "
                        f"which is {total - budget:,} bytes OVER the {budget:,} budget. Shed at "
                        f"least that much more rank cost using the per-type costs above. Keep "
                        f"the style rules and reply with the same JSON shape only.")
        except Exception as exc:
            entry["error"] = str(exc)
            feedback = (f"Your attempt {attempt} could not be used ({exc}). Reply with ONLY the "
                        f"JSON object in the exact shape requested, integer ranks for exactly "
                        f"the 8 layer names, total real-shape price <= {budget:,} bytes.")
        entry["feedback_sent"] = feedback
    Path(args.record).write_text(json.dumps(record, indent=2) + "\n")
    raise RuntimeError("Spark variant stayed over budget or style-invalid after 3 attempts")


# ---------------------------------------------------------------------------
# build-variant (Flash)
# ---------------------------------------------------------------------------

def cmd_build_variant(args):
    variant = json.loads(Path(args.variant).read_text())
    ranks = {k: int(v) for k, v in variant["ranks"].items()}
    name = variant["name"]
    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)

    base_hdr, base_off = sp.load_header(args.base)
    ins_hdr, ins_off = sp.load_header(args.instruct)

    pricing = 0
    full_fp16 = 0
    flat = {}
    t_all = time.perf_counter()
    for store_key, hf_key, layer_name in sp.matrix_keys():
        Wb = sp.read_tensor_fp32(args.base, base_hdr, base_off, hf_key)
        Wi = sp.read_tensor_fp32(args.instruct, ins_hdr, ins_off, hf_key)
        D32 = Wi - Wb
        shape = D32.shape
        del Wb, Wi
        full_fp16 += 2 * D32.size
        r = ranks[layer_name]
        pricing += factored.storage_bytes(r, shape)
        if r == 0:
            del D32
            continue
        D = D32.astype(np.float64)
        del D32
        svd = np.linalg.svd(D, full_matrices=False)
        U, V = sp.quantize_from_svd(D, svd, r)
        del D, svd
        flat[f"{store_key}_U"] = U.astype(np.float32)
        flat[f"{store_key}_V"] = V.astype(np.float32)
        del U, V
        print(f"built {store_key} rank={r}", file=sys.stderr)

    np.savez(workdir / f"factors_{name}.npz", **flat)
    stage2_build = json.loads((Path(args.stage2_workdir) / "build_summary.json").read_text())
    record = {
        "phase": "build_variant",
        "variant_name": name,
        "ranks": ranks,
        "real_shape_bytes_computed": int(pricing),
        "real_shape_bytes_claimed_by_generation": variant.get("real_shape_bytes"),
        "price_matches_generation_claim": int(pricing) == variant.get("real_shape_bytes"),
        "budget_bytes_uniform_rank32_real": stage2_build["pricing"]["uniform_rank32"]["real_shape_bytes"],
        "within_budget": int(pricing) <= stage2_build["pricing"]["uniform_rank32"]["real_shape_bytes"],
        "full_delta_fp16_bytes": int(full_fp16),
        "wall_s": round(time.perf_counter() - t_all, 2),
        "peak_rss_mb": round(sp.peak_rss_mb(), 1),
    }
    (workdir / "build_variant.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


# ---------------------------------------------------------------------------
# eval (Flash): one config on the combined 96 probes.
# ---------------------------------------------------------------------------

def load_probes(path):
    items = json.loads(Path(path).read_text())
    return [(it["bucket"], it["prompt"], it["answer"], it["subset"]) for it in items]


def cmd_eval(args):
    from tokenizers import Tokenizer

    workdir = Path(args.workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    tok = Tokenizer.from_file(str(Path(args.data) / args.tokenizer))
    items = load_probes(args.probes)

    t0 = time.perf_counter()
    if args.config == "full_delta":
        sd = sp.load_all_fp32(args.instruct)
        applied = "Instruct weights (== base + full delta on every tensor)"
    else:
        sd = sp.load_all_fp32(args.base)
        if args.config == "base":
            applied = "base weights, no delta"
        else:
            fac_path = workdir / f"factors_{args.config}.npz"
            if not fac_path.exists():
                fac_path = Path(args.stage2_workdir) / f"factors_{args.config}.npz"
            fac = np.load(fac_path)
            key_of = {sk: hk for sk, hk, _ in sp.matrix_keys()}
            for store_key, hf_key in key_of.items():
                ukey = f"{store_key}_U"
                if ukey not in fac:
                    continue  # rank 0: delta dropped, matrix keeps base value
                U, V = fac[ukey], fac[f"{store_key}_V"]
                sd[hf_key] = sd[hf_key] + (U @ V.T)
            applied = (f"base + factored delta ({args.config}) on the 225 recipe "
                       "matrices; all other tensors at base values")
    load_s = time.perf_counter() - t0

    t1 = time.perf_counter()
    rows = []
    for subset in SUBSETS:
        sub_items = [(b, p, a) for (b, p, a, s) in items if s == subset]
        sub_rows = sp.score_items(tok, sd, sub_items)
        for r in sub_rows:
            r["subset"] = subset
        rows.extend(sub_rows)
    eval_s = time.perf_counter() - t1
    del sd
    gc.collect()

    out = {
        "config": args.config,
        "probe_set": "heldout96_spark",
        "applied": applied,
        "n_items": len(rows),
        "scores": sp.aggregate(rows),
        "scores_by_subset": {s: sp.aggregate([r for r in rows if r["subset"] == s])
                             for s in SUBSETS},
        "per_item": rows,
        "load_wall_s": round(load_s, 2),
        "eval_wall_s": round(eval_s, 2),
        "wall_s": round(time.perf_counter() - t0, 2),
        "peak_rss_mb": round(sp.peak_rss_mb(), 1),
    }
    (workdir / f"eval_{args.config}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("config", "n_items", "wall_s", "peak_rss_mb")}, indent=2))
    print("combined:", json.dumps(out["scores"]["overall"], indent=2))


# ---------------------------------------------------------------------------
# assemble (Flash or VM; pure file work)
# ---------------------------------------------------------------------------

def gap_closed(factored, base, full):
    out = {}
    for b in ("knowledge", "instruction", "math"):
        gap = (full["per_bucket"][b]["mean_target_logprob"]
               - base["per_bucket"][b]["mean_target_logprob"])
        out[b] = ((factored["per_bucket"][b]["mean_target_logprob"]
                   - base["per_bucket"][b]["mean_target_logprob"]) / gap
                  if gap and gap > 1e-9 else None)
    gap_all = (full["overall"]["mean_target_logprob"] - base["overall"]["mean_target_logprob"])
    out["overall"] = ((factored["overall"]["mean_target_logprob"]
                       - base["overall"]["mean_target_logprob"]) / gap_all
                      if gap_all and gap_all > 1e-9 else None)
    return out


def cmd_assemble(args):
    workdir = Path(args.workdir)
    stage2 = json.loads(Path(args.stage2_results).read_text())
    variant = json.loads(Path(args.variant).read_text())
    gen_record = json.loads(Path(args.gen_record).read_text())
    build_v = json.loads((workdir / "build_variant.json").read_text())
    vname = variant["name"]
    winner_name = stage2["winner"]["name"]

    s2_entries = {e["name"]: e for e in stage2["recipes"] + [stage2["human_baseline"]]}
    rank_maps = {n: e["ranks"] for n, e in s2_entries.items()}
    rank_maps[vname] = {k: int(v) for k, v in variant["ranks"].items()}
    uniform_b = s2_entries["uniform_rank32"]["real_shape_bytes"]
    real_bytes = {
        "uniform_rank32": uniform_b,
        winner_name: s2_entries[winner_name]["real_shape_bytes"],
        vname: build_v["real_shape_bytes_computed"],
    }
    configs = list(dict.fromkeys(["uniform_rank32", winner_name, vname]))
    kinds = {"uniform_rank32": "human_baseline",
             winner_name: "spark_recipe_stage2_winner" + ("_BYTE_UNFAIR" if real_bytes[winner_name] > uniform_b else ""),
             vname: "spark_bytematched_variant"}

    all_configs = ["base", "full_delta"] + configs
    evals = {c: json.loads((workdir / f"eval_{c}.json").read_text()) for c in all_configs}

    def view(ev, which):
        return ev["scores"] if which == "combined96" else ev["scores_by_subset"][which]

    entries = {}
    for c in configs:
        ev = evals[c]
        entries[c] = {
            "name": c,
            "kind": kinds[c],
            "byte_unfair": real_bytes[c] > uniform_b,
            "ranks": rank_maps[c],
            "rank0_layer_names": [n for n, r in rank_maps[c].items() if r == 0],
            "real_shape_bytes": real_bytes[c],
            "combined96": {
                "configs": {"base": view(evals["base"], "combined96"),
                            "full_delta": view(evals["full_delta"], "combined96"),
                            "factored_delta": view(ev, "combined96")},
                "gap_closed": gap_closed(view(ev, "combined96"), view(evals["base"], "combined96"),
                                         view(evals["full_delta"], "combined96")),
            },
            "heldout24_subset": {
                "configs": {"base": view(evals["base"], "heldout24"),
                            "full_delta": view(evals["full_delta"], "heldout24"),
                            "factored_delta": view(ev, "heldout24")},
                "gap_closed": gap_closed(view(ev, "heldout24"), view(evals["base"], "heldout24"),
                                         view(evals["full_delta"], "heldout24")),
            },
            "heldout72_new_subset": {
                "configs": {"base": view(evals["base"], "heldout72_new"),
                            "full_delta": view(evals["full_delta"], "heldout72_new"),
                            "factored_delta": view(ev, "heldout72_new")},
                "gap_closed": gap_closed(view(ev, "heldout72_new"),
                                         view(evals["base"], "heldout72_new"),
                                         view(evals["full_delta"], "heldout72_new")),
            },
            "per_item": ev["per_item"],
            "wall_s": ev["wall_s"],
            "eval_wall_s": ev["eval_wall_s"],
            "peak_rss_mb": ev["peak_rss_mb"],
        }

    def lp96(c):
        return evals[c]["scores"]["overall"]["mean_target_logprob"]

    def gc96(c):
        return entries[c]["combined96"]["gap_closed"]["overall"]

    verdict = {
        "stage2_winner": winner_name,
        "byte_fair_contender": vname,
        "byte_fair_headline_question": f"does {vname} beat uniform_rank32 on the combined 96 fresh items?",
        "contender_beats_uniform_on_combined96": lp96(vname) > lp96("uniform_rank32"),
        "contender_gap_closed_combined96": gc96(vname),
        "uniform_gap_closed_combined96": gc96("uniform_rank32"),
        "contender_within_uniform_budget": real_bytes[vname] <= uniform_b,
        "winner_byte_status": {
            "winner_real_shape_bytes": real_bytes[winner_name],
            "uniform_real_shape_bytes": uniform_b,
            "winner_byte_unfair": real_bytes[winner_name] > uniform_b,
            "winner_combined96_gap_closed": gc96(winner_name),
        },
        "subset_consistency": {
            s: {
                "contender_gap_closed": entries[vname][
                    "heldout24_subset" if s == "heldout24" else "heldout72_new_subset"]["gap_closed"]["overall"],
                "uniform_gap_closed": entries["uniform_rank32"][
                    "heldout24_subset" if s == "heldout24" else "heldout72_new_subset"]["gap_closed"]["overall"],
                "contender_beats_uniform": (
                    evals[vname]["scores_by_subset"][s]["overall"]["mean_target_logprob"]
                    > evals["uniform_rank32"]["scores_by_subset"][s]["overall"]["mean_target_logprob"]),
            } for s in SUBSETS
        },
    }

    result = {
        "stage": "second_pair_heldout96_confirmation",
        "date": "2026-10-27",
        "machine": "Flash (Vinay's Ubuntu box, ssh flash, 12 threads, qwen-test venv: python 3.14 + numpy 2.5.4 + tokenizers 0.23.3)",
        "model_pair": stage2["model_pair"],
        "probe_set": {
            "source": "the combined 96 fresh Spark probe items from Phase 1 (original 24 held-out + 72 expansion items); neither the Qwen sweep nor this pair's sweep saw them during search, Stage 1, or Stage 2",
            "file": "data/heldout96_probes_spark.json (local only, data/ is gitignored)",
            "n_items": 96,
            "buckets": {"knowledge": 32, "instruction": 32, "math": 32},
            "subsets": {"heldout24": 24, "heldout72_new": 72},
        },
        "byte_matched_variant": {
            "name": vname,
            "reason": variant.get("reason"),
            "ranks": rank_maps[vname],
            "generation": {
                "provider": "baseten", "model": BASETEN_MODEL,
                "winner": gen_record.get("winner"),
                "attempts": [
                    {"attempt": a["attempt"], "real_shape_bytes": a.get("real_shape_bytes"),
                     "within_budget": a.get("within_budget"), "error": a.get("error")}
                    for a in gen_record.get("attempts", [])
                ],
                "note": gen_record.get("variant", {}).get("note"),
            },
            "price_validation": {
                "method": "factored.storage_bytes summed over the 225 real matrices read from the model files, computed in the Flash build pass (same code path as Stage 2 pricing)",
                "real_shape_bytes_computed_on_flash": build_v["real_shape_bytes_computed"],
                "matches_generation_claim": build_v["price_matches_generation_claim"],
                "budget_bytes_uniform_rank32_real": build_v["budget_bytes_uniform_rank32_real"],
                "within_budget": build_v["within_budget"],
                "build_wall_s": build_v["wall_s"],
                "build_peak_rss_mb": build_v["peak_rss_mb"],
            },
        },
        "method": {
            "configs": "base (no delta), full_delta (Instruct weights), and factored_delta per recipe: uniform_rank32, the Stage 2 winner, and the byte-matched variant",
            "scoring": "identical to second_pair Stage 2: ChatML prompt (system line 'You are a helpful assistant.'); target logprob = summed log-probability of the answer tokens; accuracy = first-token accuracy; gap_closed = (factored - base) / (full - base) on mean target logprob, per subset with that subset's own base/full references",
            "forward_pass": "the second_pair_stage2 NumPy SmolLM2 forward, validated in Stage 2 against the prior Signet run's published bucket means",
            "full_delta_fp16_bytes": stage2["full_delta_fp16_bytes_real_shapes"],
        },
        "shared_configs": {
            "base": evals["base"]["scores"],
            "full_delta": evals["full_delta"]["scores"],
            "base_by_subset": evals["base"]["scores_by_subset"],
            "full_delta_by_subset": evals["full_delta"]["scores_by_subset"],
        },
        "configs": entries,
        "ranking_by_combined96_task_score": sorted(
            ({"name": c, "kind": kinds[c], "byte_unfair": real_bytes[c] > uniform_b,
              "factored_mean_target_logprob": lp96(c),
              "factored_accuracy": evals[c]["scores"]["overall"]["accuracy"],
              "overall_gap_closed": gc96(c), "real_shape_bytes": real_bytes[c]}
             for c in configs),
            key=lambda e: e["factored_mean_target_logprob"], reverse=True),
        "verdict": verdict,
        "scripts": ["examples/second_pair_stage2.py", "examples/second_pair_heldout96.py"],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {out}")
    print(json.dumps(result["ranking_by_combined96_task_score"], indent=2))
    print(json.dumps(verdict, indent=2))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("variant-gen")
    g.add_argument("--stage2-results", required=True)
    g.add_argument("--record", default="/tmp/second_pair_variant_record.json")
    g.add_argument("--variant-out", default="/tmp/second_pair_variant.json")
    g.set_defaults(fn=cmd_variant_gen)

    b = sub.add_parser("build-variant")
    b.add_argument("--base", required=True)
    b.add_argument("--instruct", required=True)
    b.add_argument("--variant", required=True)
    b.add_argument("--stage2-workdir", required=True)
    b.add_argument("--workdir", required=True)
    b.set_defaults(fn=cmd_build_variant)

    e = sub.add_parser("eval")
    e.add_argument("--config", required=True)
    e.add_argument("--base", required=True)
    e.add_argument("--instruct", required=True)
    e.add_argument("--probes", required=True)
    e.add_argument("--data", default=str(Path.home() / "qwen-test" / "data"))
    e.add_argument("--tokenizer", default="smollm2-360m-tokenizer.json")
    e.add_argument("--stage2-workdir", required=True)
    e.add_argument("--workdir", required=True)
    e.set_defaults(fn=cmd_eval)

    a = sub.add_parser("assemble")
    a.add_argument("--variant", required=True)
    a.add_argument("--gen-record", required=True)
    a.add_argument("--stage2-results", required=True)
    a.add_argument("--stage2-workdir", required=True)
    a.add_argument("--workdir", required=True)
    a.add_argument("--out", required=True)
    a.set_defaults(fn=cmd_assemble)

    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
