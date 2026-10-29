"""Out-of-style LoRA control: Muse Spark judging pass.

House pattern: Spark is given ONLY numbers copied by script from
results/lora_outofstyle.json and must return a verdict per claim with
the source file cited by name. Claims are generated programmatically
from the result file. One call, logged to results/api_usage_log.jsonl
with purpose "lora out-of-style".

Run from the repo root on the Muse VM after assemble:

    python3 examples/lora_outofstyle_judge.py
"""

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path.home() / "workspace/custom-connectors/custom.meta-model-api/bin"))
import meta_api  # noqa: E402

MODEL = "muse-spark-1.3"
SRC = "results/lora_outofstyle.json"


def now_z():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    res = json.loads(Path(SRC).read_text())
    rows = {r["name"]: r for r in res["spark96_table"]}
    rule = res["preregistered_rule"]
    ver = res["verification"]
    mir = res["mirror96_table"]
    ctl = res["control_adapter"]

    def gc(name):
        return rows[name]["gap_closed"]["overall"]

    def lp(name):
        return rows[name]["mean_target_logprob"]

    def mgc(name):
        return mir[name]["gap_closed"]["overall"]

    in_split = rows["lora_instyle_seed20261028"]["split"]
    oos_split = rows["lora_oos_seed20261028"]["split"]
    claims = [
        ("O1", f"The out-of-style adapter is the identical artifact shape to the "
               f"in-style adapter (rank 17, all seven block linears x 24 blocks, "
               f"no embedding, 18,696,192 B fp16) and was trained with the "
               f"identical recipe and seed 20261028; only the distillation "
               f"prompt set changed (1,500 Gemini-authored prompts, varied "
               f"surface style, vs 1,500 Spark-authored prompts in the Spark "
               f"eval style)."),
        ("O2", f"On the untouched Spark 96: base {lp('base'):.4f}, full delta "
               f"{lp('full_delta'):.4f}, uniform {lp('uniform_rank32'):.4f} "
               f"(gap closed {gc('uniform_rank32'):.3f}), lite "
               f"{lp('mlp_behemoth_lite'):.4f} (gap closed "
               f"{gc('mlp_behemoth_lite'):.3f}), in-style adapter "
               f"{lp('lora_instyle_seed20261028'):.4f} (gap closed "
               f"{gc('lora_instyle_seed20261028'):.3f}), out-of-style adapter "
               f"{lp('lora_oos_seed20261028'):.4f} (gap closed "
               f"{gc('lora_oos_seed20261028'):.3f})."),
        ("O3", f"Under the interpretation rule frozen in "
               f"results/lora_outofstyle_design.md before training "
               f"(>= 0.60 the win is not only style; 0.40-0.60 partly; "
               f"< 0.40 mostly style), the out-of-style gap closed of "
               f"{gc('lora_oos_seed20261028'):.3f} gives the verdict: "
               f"{rule['verdict']}."),
        ("O4", f"Mirrored eval on the Gemini-authored 96: the full fine-tune "
               f"scores BELOW the base there (base "
               f"{mir['base']['mean_target_logprob']:.4f}, full "
               f"{mir['full_delta']['mean_target_logprob']:.4f}), so mirror "
               f"gap closed is recorded as null (negative denominator) and "
               f"the read is on raw mean logprob: in-style adapter "
               f"{mir['lora_instyle_seed20261028']['mean_target_logprob']:.4f} "
               f"beats the out-of-style adapter "
               f"{mir['lora_oos_seed20261028']['mean_target_logprob']:.4f} on "
               f"the Gemini set too, so crossover (each adapter wins on its "
               f"own author's set) is {rule['crossover']}."),
        ("O5", f"First-token vs continuation split on the Spark 96: in-style "
               f"adapter mean first-token logprob "
               f"{in_split['mean_first_token_logprob']:.4f} and continuation "
               f"{in_split['mean_continuation_logprob']:.4f} (first-token "
               f"accuracy {in_split['first_token_accuracy']:.3f}); "
               f"out-of-style adapter first-token "
               f"{oos_split['mean_first_token_logprob']:.4f} and continuation "
               f"{oos_split['mean_continuation_logprob']:.4f} (first-token "
               f"accuracy {oos_split['first_token_accuracy']:.3f})."),
        ("O6", f"Verification: the zero adapter in the new workdir reproduces "
               f"the stored base per-item logprobs with max abs diff "
               f"{ver['oos_zero_adapter_vs_stored_base_max_abs_per_item_diff']:.2e}; "
               f"the dense W+B@A reference matches the hooked path at "
               f"{ver['oos_dense_vs_hooked_max_abs_per_item_diff']:.2e}; every "
               f"published aggregate was recomputed from per-item rows by an "
               f"independent script (worst stored-vs-recomputed diff "
               f"{max(v['abs_diff'] for v in res['recompute_report'].values()):.2e})."),
        ("O7", f"Hygiene: the control adapter trained only on the 1,350 "
               f"Gemini train prompts (150 more used only for early stopping) "
               f"with teacher-generated supervision; the Spark 96 and the "
               f"Gemini mirror-96 were never used for training, stopping, or "
               f"selection; the design, thresholds, and interpretation rule "
               f"were frozen in results/lora_outofstyle_design.md before any "
               f"training, after consults with Spark, Gemini, Nemotron, and "
               f"Glimmer."),
    ]
    verdict_word = rule["verdict"]
    if verdict_word == "survives":
        sentence = (f"Distilled on Gemini-authored prompts in a deliberately "
                    f"different style, the same 18.7 MB LoRA adapter still "
                    f"closes {gc('lora_oos_seed20261028'):.1%} of the base-to-full "
                    f"gap on the Spark-written 96 (vs {gc('lora_instyle_seed20261028'):.1%} "
                    f"in-style and {gc('mlp_behemoth_lite'):.1%} for the factored "
                    f"patch), so the adapter's matched-byte win is not only a "
                    f"style-match artifact, though training-style match still "
                    f"adds a large share on top.")
    elif verdict_word == "partly":
        sentence = (f"Distilled on Gemini-authored prompts in a deliberately "
                    f"different style, the same 18.7 MB LoRA adapter closes "
                    f"{gc('lora_oos_seed20261028'):.1%} of the base-to-full gap on "
                    f"the Spark-written 96: still clearly above the factored "
                    f"patch ({gc('mlp_behemoth_lite'):.1%}) but far below the "
                    f"in-style adapter ({gc('lora_instyle_seed20261028'):.1%}), so "
                    f"the shared style explains a large share of the in-style "
                    f"win, not all of it.")
    else:
        sentence = (f"Distilled on Gemini-authored prompts in a deliberately "
                    f"different style, the same 18.7 MB LoRA adapter closes only "
                    f"{gc('lora_oos_seed20261028'):.1%} of the base-to-full gap on "
                    f"the Spark-written 96, against "
                    f"{gc('lora_instyle_seed20261028'):.1%} for the in-style "
                    f"adapter and {gc('mlp_behemoth_lite'):.1%} for the factored "
                    f"patch, so the in-style adapter win was mostly the shared "
                    f"Spark style between its training prompts and the eval.")

    extract = {
        "spark96_table": [{k: r[k] for k in ("name", "bytes", "mean_target_logprob",
                                             "accuracy", "gap_closed", "split")}
                          for r in res["spark96_table"]],
        "mirror96_table": {k: {"mean_target_logprob": v["mean_target_logprob"],
                               "accuracy": v["accuracy"],
                               "gap_closed": v["gap_closed"]}
                           for k, v in mir.items()},
        "preregistered_rule": rule,
        "verification": {k: ver[k] for k in
                         ("oos_zero_adapter_vs_stored_base_max_abs_per_item_diff",
                          "oos_dense_vs_hooked_max_abs_per_item_diff")},
        "control_adapter": {k: ctl[k] for k in ("form", "seed", "training")},
        "recompute_worst_abs_diff": max(
            v["abs_diff"] for v in res["recompute_report"].values()),
    }
    prompt = (
        "You are an independent judge for a research benchmark. Below is an extract "
        f"copied verbatim from {SRC} (the experiment's result file), followed by "
        "claims about that experiment. Judge the claims against the extract: for "
        "EACH claim, return a verdict: SUPPORTED, CONTRADICTED, or UNVERIFIABLE, "
        "with a one-line reason and the cited source file name "
        f"(\"{SRC}\"). Recompute any derived number you rely on (gap_closed = "
        "(config - base) / (full - base) on mean target logprob; base and "
        "full_delta are rows of the table). Then answer the headline question.\n\n"
        "EXTRACT FROM " + SRC + ":\n"
        + json.dumps(extract, indent=1)
        + "\n\nCLAIMS:\n"
        + "\n".join(f"{cid}. {text}" for cid, text in claims)
        + f"\n\nHEADLINE QUESTION: Is this the honest one-sentence conclusion? "
          f"Answer yes or no, and if no, give the corrected sentence.\n"
          f"\"{sentence}\"\n\n"
          "Reply in this exact JSON shape, no markdown fences:\n"
          "{\"verdicts\": [{\"claim\": \"O1\", \"verdict\": \"SUPPORTED\", "
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
            "purpose": "lora out-of-style",
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "total_tokens": usage.get("total_tokens")}) + "\n")
    content = resp["choices"][0]["message"].get("content") or ""
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1].rsplit("```", 1)[0]
    verdicts = json.loads(text)

    out = {
        "date": "2026-10-29",
        "judging_pass": "lora_outofstyle_spark_judging",
        "judge": {"provider": "meta-model-api", "model": MODEL, "time": now_z(),
                  "prompt_tokens": usage.get("prompt_tokens"),
                  "completion_tokens": usage.get("completion_tokens"),
                  "total_tokens": usage.get("total_tokens"),
                  "reasoning_tokens": (usage.get("completion_tokens_details") or {}).get("reasoning_tokens"),
                  "elapsed_s": elapsed,
                  "role": "independent judge over the finished out-of-style control "
                          "results; Spark saw only the numbers copied from the cited file"},
        "sources_judged": [SRC],
        "metric": "gap_closed = (config - base) / (full_delta - base) on mean target "
                  "logprob over the combined 96 held-out questions",
        "claims": [{"id": cid, "text": t} for cid, t in claims],
        "verdicts": verdicts.get("verdicts"),
        "headline_question": verdicts.get("headline_question"),
        "headline_sentence_tested": sentence,
    }
    Path("results/lora_outofstyle_judging.json").write_text(json.dumps(out, indent=2) + "\n")
    n_sup = sum(1 for v in out["verdicts"] if v.get("verdict") == "SUPPORTED")
    lines = [
        "# Muse Spark judging pass: the out-of-style LoRA control (2026-10-29)",
        "",
        f"Muse Spark (muse-spark-1.3, Meta Model API) acted as an independent judge "
        f"over the out-of-style control results in {SRC}. Spark was given an extract "
        f"copied verbatim from that file and had to return a verdict per claim with "
        f"the source file cited by name. Judging call: {usage.get('prompt_tokens')} "
        f"prompt tokens, {usage.get('completion_tokens')} completion tokens, "
        f"{usage.get('total_tokens')} total. Full structured record: "
        f"results/lora_outofstyle_judging.json.",
        "",
        f"Source judged: {SRC}.",
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
    Path("results/lora_outofstyle_judging.md").write_text("\n".join(lines) + "\n")
    print(f"verdicts: {n_sup} of {len(out['verdicts'])} SUPPORTED; "
          f"headline answer: {hq.get('answer')}")


if __name__ == "__main__":
    main()
