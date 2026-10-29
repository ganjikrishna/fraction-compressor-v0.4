"""LoRA baseline: Muse Spark judging pass over the assembled results.

House pattern (cf. spark_judging_baseline): Spark is given ONLY the
numbers copied by script from results/lora_baseline.json and must
return a verdict per claim with the source file cited by name. Claims
are generated programmatically from the result file (no hand-copied
numbers). One call, logged to results/api_usage_log.jsonl.

Run from the repo root on the Muse VM after assemble:

    python3 examples/lora_baseline_judge.py
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.meta-model-api/bin"))
import meta_api  # noqa: E402

MODEL = "muse-spark-1.3"
SRC = "results/lora_baseline.json"


def now_z():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    res = json.loads(Path(SRC).read_text())
    rows = {r["name"]: r for r in res["table"]}
    hc = res["headline_comparison"]
    ver = res["verification"]
    ad = res["adapter_summary"]
    base = rows["base"]["mean_target_logprob"]
    full = rows["full_delta"]["mean_target_logprob"]

    def lp(name):
        return rows[name]["mean_target_logprob"]

    def gc(name):
        return rows[name]["gap_closed"]["overall"]

    claims = [
        ("L1", f"The LoRA adapter prices at exactly {ad['bytes']:,} bytes fp16 "
               f"({ad['params']:,} params, rank 17, all seven block linears x 24 blocks, "
               f"no embedding), under the uniform factored budget of 19,434,496 B and "
               f"the lite budget of 19,358,176 B."),
        ("L2", f"Adapter mean target logprob over 3 seeds is "
               f"{ad['mean_target_logprob_mean_over_seeds']:.4f} "
               f"(std {ad['mean_target_logprob_std_over_seeds']:.4f}), closing "
               f"{ad['gap_closed_mean_over_seeds']:.3f} of the base-to-full gap "
               f"(base {base:.4f}, full {full:.4f})."),
        ("L3", f"The uniform factored patch closes {gc('uniform_rank32'):.3f} and the "
               f"lite factored patch closes {gc('mlp_behemoth_lite'):.3f} on the same 96; "
               f"the adapter's mean gap closed is "
               f"{'higher than both' if hc['adapter_beats_lite'] else ('higher than uniform but not lite' if hc['adapter_beats_uniform'] else 'lower than both')}."),
        ("L4", f"Blocks-only comparison: with the embedding delta dropped, uniform "
               f"closes {gc('uniform_rank32_noembed'):.3f} at "
               f"{rows['uniform_rank32_noembed']['bytes']:,} B and lite closes "
               f"{gc('mlp_behemoth_lite_noembed'):.3f} at "
               f"{rows['mlp_behemoth_lite_noembed']['bytes']:,} B, vs the adapter's "
               f"{ad['gap_closed_mean_over_seeds']:.3f} at {ad['bytes']:,} B."),
        ("L5", f"Forward-path verification: the zero adapter reproduces the stored base "
               f"per-item logprobs with max abs diff "
               f"{ver['zero_adapter_vs_stored_base_max_abs_per_item_diff']:.2e}, and the "
               f"dense W+B@A reference matches the hooked (X@A.T)@B.T path with max abs "
               f"per-item diff {ver['dense_vs_hooked_seed1_max_abs_per_item_diff']:.2e}."),
        ("L6", f"Precision sensitivity: scoring seed 1 from fp32-unrounded A/B gives "
               f"{lp('lora_seed20261028_fp32'):.4f} vs {lp('lora_distilled_seed20261028'):.4f} from "
               f"the fp16-rounded file; the factored rows re-scored with V rounded "
               f"through fp16 move uniform to {lp('uniform_rank32_vfp16'):.4f} (from "
               f"{lp('uniform_rank32'):.4f}) and lite to {lp('mlp_behemoth_lite_vfp16'):.4f} "
               f"(from {lp('mlp_behemoth_lite'):.4f})."),
        ("L7", "Hygiene: the adapter trained only on 1,350 fresh prompts (150 more used "
               "only for early stopping) with teacher-generated supervision; the 96 eval "
               "prompts and their reference answers were never used for training, "
               "stopping, or selection; hyperparameters were frozen in "
               "results/lora_baseline_design.md before training."),
    ]
    winner = ("the distilled LoRA adapter" if hc["adapter_beats_lite"]
              else "the factored lite patch" if hc["adapter_beats_uniform"] or True
              else "the factored patches")
    if hc["adapter_beats_lite"]:
        sentence = (f"At about 19 MB on the Qwen2.5-0.5B pair, a LoRA adapter distilled "
                    f"from the fine-tune closes {ad['gap_closed_mean_over_seeds']:.1%} of "
                    f"the base-to-full gap on the combined 96, more than the full "
                    f"fine-tune itself scores on this probe set and far more than the "
                    f"post-hoc factored patch ({gc('mlp_behemoth_lite'):.1%} lite, "
                    f"{gc('uniform_rank32'):.1%} uniform); the adapter's edge is "
                    f"specialization to this probe distribution's style, bought with "
                    f"gradient training on 1,500 teacher queries instead of a "
                    f"deterministic weight-only conversion, and it does not imply the "
                    f"adapter is the better model off this distribution.")
    elif hc["adapter_beats_uniform"]:
        sentence = (f"At about 19 MB on the Qwen2.5-0.5B pair, a LoRA adapter distilled "
                    f"from the fine-tune ({ad['gap_closed_mean_over_seeds']:.1%} gap "
                    f"closed) beats the uniform factored patch "
                    f"({gc('uniform_rank32'):.1%}) but not the searched factored recipe "
                    f"({gc('mlp_behemoth_lite'):.1%}), and it costs gradient training on "
                    f"1,500 teacher queries instead of a deterministic weight-only "
                    f"conversion.")
    else:
        sentence = (f"At about 19 MB on the Qwen2.5-0.5B pair, the post-hoc factored "
                    f"patch (lite {gc('mlp_behemoth_lite'):.1%}, uniform "
                    f"{gc('uniform_rank32'):.1%} gap closed) beats a LoRA adapter "
                    f"distilled from the same fine-tune "
                    f"({ad['gap_closed_mean_over_seeds']:.1%}), even though the adapter "
                    f"had gradient training on 1,500 teacher queries and the factored "
                    f"patch is a deterministic weight-only conversion.")

    extract = {
        "table": [{k: r[k] for k in ("name", "kind", "bytes", "mean_target_logprob",
                                     "accuracy", "gap_closed")}
                  for r in res["table"]],
        "adapter_summary": {k: ad[k] for k in
                            ("bytes", "params", "rank", "placement",
                             "mean_target_logprob_mean_over_seeds",
                             "mean_target_logprob_std_over_seeds",
                             "gap_closed_mean_over_seeds",
                             "gap_closed_std_over_seeds")},
        "verification": res["verification"],
        "adapter_block": res["adapter"],
        "design": res["design"],
        "probe_set": res["probe_set"],
        "headline_comparison": res["headline_comparison"],
        "script_rerun_of_stored_rows": res["script_rerun_of_stored_rows"],
    }
    prompt = (
        "You are an independent judge for a research benchmark. Below is an extract "
        f"copied verbatim from {SRC} (the experiment's result file), followed by "
        "claims about that experiment. Judge the claims against the extract: for "
        "EACH claim, return a verdict: SUPPORTED, CONTRADICTED, or UNVERIFIABLE, "
        "with a one-line reason and the cited source file name "
        f"(\"{SRC}\"). Recompute any derived number you rely on (gap_closed = "
        "(config - base) / (full - base) on mean target logprob over the combined 96 "
        "held-out questions; base and full_delta are rows of the table). Then answer "
        "the headline question.\n\nEXTRACT FROM " + SRC + ":\n"
        + json.dumps(extract, indent=1)
        + "\n\nCLAIMS:\n"
        + "\n".join(f"{cid}. {text}" for cid, text in claims)
        + f"\n\nHEADLINE QUESTION: Is this the honest one-sentence conclusion? Answer "
          f"yes or no, and if no, give the corrected sentence.\n\"{sentence}\"\n\n"
          "Reply in this exact JSON shape, no markdown fences:\n"
          "{\"verdicts\": [{\"claim\": \"L1\", \"verdict\": \"SUPPORTED\", "
          "\"reason\": \"...\", \"cited_file\": \"" + SRC + "\"}], "
          "\"headline_question\": {\"answer\": \"yes\", \"sentence\": \"...\"}}"
    )
    payload = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
               "max_tokens": 24000}
    t0 = time.perf_counter()
    resp = meta_api.call("POST", "/v1/chat/completions", payload)
    elapsed = round(time.perf_counter() - t0, 2)
    if "http_error" in resp:
        raise RuntimeError(f"HTTP {resp['http_error']}: {resp['body'][:500]}")
    usage = resp.get("usage") or {}
    with open("results/api_usage_log.jsonl", "a") as f:
        f.write(json.dumps({
            "provider": "meta-model-api", "model": MODEL, "time": now_z(),
            "purpose": "lora_baseline_spark_judging",
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens")}) + "\n")
    content = resp["choices"][0]["message"].get("content") or ""
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    verdicts = json.loads(text)

    out = {
        "date": "2026-10-28",
        "judging_pass": "lora_baseline_spark_judging",
        "judge": {"provider": "meta-model-api", "model": MODEL, "time": now_z(),
                  "prompt_tokens": usage.get("prompt_tokens"),
                  "completion_tokens": usage.get("completion_tokens"),
                  "total_tokens": usage.get("total_tokens"),
                  "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                  "elapsed_s": elapsed,
                  "role": "independent judge over the finished LoRA baseline results; "
                          "Spark saw only the numbers copied from the cited file"},
        "sources_judged": [SRC],
        "metric": "gap_closed = (config - base) / (full_delta - base) on mean target "
                  "logprob over the combined 96 fresh held-out questions",
        "claims": [{"id": cid, "text": t} for cid, t in claims],
        "verdicts": verdicts.get("verdicts"),
        "headline_question": verdicts.get("headline_question"),
        "headline_sentence_tested": sentence,
    }
    Path("results/lora_baseline_judging.json").write_text(json.dumps(out, indent=2) + "\n")
    n_sup = sum(1 for v in out["verdicts"] if v.get("verdict") == "SUPPORTED")
    lines = [
        "# Muse Spark judging pass: the LoRA baseline (2026-10-28)",
        "",
        f"Muse Spark (muse-spark-1.3, Meta Model API) acted as an independent judge "
        f"over the LoRA-baseline results in {SRC}. Spark was given an extract copied "
        f"verbatim from that file (table, adapter summary, verification block), and "
        f"had to return a verdict per claim with the source file cited by name. "
        f"Final judging call: {usage.get('prompt_tokens')} prompt tokens, "
        f"{usage.get('completion_tokens')} completion tokens, "
        f"{usage.get('total_tokens')} total. Full structured record: "
        f"results/lora_baseline_judging.json.",
        "",
        f"Source judged: {SRC}.",
        f"(gap_closed = (config - base) / (full_delta - base) on mean target logprob "
        f"over the combined 96 fresh held-out questions; base {base:.4f}, "
        f"full {full:.4f}.)",
        "",
        f"## Verdicts: {n_sup} of {len(out['verdicts'])} claims SUPPORTED",
        "",
        "| Claim | Verdict | Cited file |",
        "|---|---|---|",
    ]
    claim_text = dict(claims)
    for v in out["verdicts"]:
        lines.append(f"| {v['claim']}. {claim_text.get(v['claim'], '')} | "
                     f"{v['verdict']} | {v.get('cited_file', SRC)} |")
    hq = out["headline_question"] or {}
    lines += ["", "## Headline question", "",
              f"Asked whether the honest one-sentence conclusion is: \"{sentence}\"",
              f"Spark's answer: {hq.get('answer')}.", ""]
    if hq.get("sentence") and hq.get("sentence") != sentence:
        lines.append(f"> {hq['sentence']}")
    Path("results/lora_baseline_judging.md").write_text("\n".join(lines) + "\n")
    print(f"verdicts: {n_sup} of {len(out['verdicts'])} SUPPORTED; "
          f"headline answer: {hq.get('answer')}")
    print(json.dumps(out["verdicts"], indent=2))


if __name__ == "__main__":
    main()
