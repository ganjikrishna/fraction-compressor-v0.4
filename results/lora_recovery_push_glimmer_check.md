# Glimmer validation of the LoRA + recovery push set (2026-10-29)

Validation run before the approved LoRA + recovery push (Vinay's approval, 2026-10-29: "Push both LoRA and recovery, get it validated, same process"). Glimmer is the default validator for push content.

## Verdict: SUBSTANTIVE FLAGS — push NOT made

The final adjudication returned **SUBSTANTIVE FLAGS** (one flag, in `results/recovery_tuning_judging.md`), plus WORDING notes in three other documents. Under the standing rule the push was stopped. Remote head is unchanged at `f8b54c6d49e2f24008bc99239f740c66909543e8`; the snapshot sync record was not touched. This file is local only and rides a later batch.

## The substantive flag (verbatim from the adjudication)

* Severity: SUBSTANTIVE
  * File: results/recovery_tuning_judging.md
  * Exact quoted text: “first-token mean logprob -5.192 vs -6.150 is not in RESULTS and cannot be verified from numbers given, so \"driven mainly\" is unsupported.”
  * What the evidence says: results/recovery_tuning.json contains first_token_vs_continuation for both re-quantized rows: lite_recovery_tuned_requantized.first_token_mean_logprob = -6.150312033233901; control_recovery_tuned_requantized.first_token_mean_logprob = -5.191730261147248. The first-token mean logprob values are present and verifiable in the repository JSON result file.

In plain words: the Spark judging record for recovery tuning says the first-token numbers behind the "driven mainly" claim are not in the results and cannot be verified. They are in fact present in `results/recovery_tuning.json` in the same push set, so the judging record as written misstates their verifiability for any reader of the repo.

## Wording notes (verbatim quotes)

- `results/lora_baseline_judging.md`: “closes 136.2% of the base-to-full gap” presents a gap-closed value above 1.0 as a recovery fraction; and “the adapter's edge is specialization to this probe distribution's style” states causation where the panel rule requires “consistent with” (oos_gap_closed 0.620 vs in-style 1.395).
- `results/lora_panel_review.md`: the filed interpretation says the overshoot “is attributed to specialization, because the 1,500 distillation prompts and the 96 eval probes were both written by Muse Spark in the same three bucket styles” — causal “because”/“attributed to” where “consistent with” is required.
- `results/lora_outofstyle.md`: “The first-token behavior, the \"decision to start,\" is the part that was style-carried.” and “style match carried the first-token behavior” state causation; and the headline sentence's “139.5% in-style” frames a >1.0 gap-closed as a percentage closed (the sentence was approved verbatim by the earlier Spark judging pass; Glimmer flags it anyway).
- `results/recovery_tuning_judging.md` (wording): “overstatement to call control's ratio \"survived\" since control never contained the 0.232 patch, and it ignores the fp16 accuracy gap 0.198 vs 0.271.” Glimmer: the shares are computed relative to each run's own fp16 gain over the untouched lite baseline, not as survival of the patch's 0.232; the judging note conflates the baseline reference.

Groups with NO FINDINGS: `results/lora_result_discussion.md`, `results/reply_drafts_final.md`, `results/reply_drafts_review.md`, `results/recovery_tuning.md`, `results/recovery_tuning_design.md`, `results/lora_baseline_design.md`, `results/lora_outofstyle_design.md`, `results/lora_outofstyle_consults.md`, `results/lora_outofstyle_judging.md`. All checkable numbers in every audited document matched the evidence digest from the push-set JSONs within rounding.

## Audit record

- Route: Flash-local call over SSH. Pi's model config on Flash routes `nvidia/meta/muse-glimmer-30b` through the local OmniRoute provider (http://localhost:20128/v1) to NVIDIA NIM. Every response's served-model field confirmed `meta/muse-glimmer-30b`. Flash-local NIM call, not a Meta Model API or Baseten call; not logged in `results/api_usage_log.jsonl`.
- Method: six document-scoped calls with `reasoning_effort: low`, each given an evidence digest computed from the push-set JSONs (`results/lora_baseline.json`, `results/lora_outofstyle.json`, `results/recovery_tuning.json`), followed by one adjudication call over the six outputs. Checks: factual consistency of every number against the JSONs, claims stronger than the evidence, internal contradictions, gap closed above 1.0 presented as a recovery fraction, and style-specialization wording held to “consistent with”.
- Call usage (served model `meta/muse-glimmer-30b` in all calls):
  - A, baseline design + judging: prompt 16,606, completion 3,274, total 19,880; finish `stop`.
  - B, panel review + out-of-style design: prompt 19,825, completion 3,951, total 23,776; finish `stop`.
  - C, result discussion: prompt 24,044, completion 1,140, total 25,184; finish `stop`.
  - D, out-of-style report + consults + judging: prompt 20,485, completion 3,342, total 23,827; finish `stop`.
  - E, recovery report + design + judging: prompt 18,684, completion 3,703, total 22,387; finish `stop`.
  - F, reply drafts + review: prompt 16,041, completion 1,972, total 18,013; finish `stop`.
  - Adjudication: prompt 7,913, completion 403, total 8,316; finish `stop`.

## Full group outputs (verbatim)

### Group A: lora_baseline_design.md + lora_baseline_judging.md

**results/lora_baseline_design.md**
NO FINDINGS

**results/lora_baseline_judging.md**

* Severity: WORDING
* File: results/lora_baseline_judging.md
* Exact quoted text:
`At about 19 MB on the Qwen2.5-0.5B pair, a LoRA adapter distilled from the fine-tune closes 136.2% of the base-to-full gap on the combined 96, more than the full fine-tune itself scores on this probe set and far more than the post-hoc factored patch (23.2% lite, 2.1% uniform); the adapter's edge is specialization to this probe distribution's style, bought with gradient training on 1,500 teacher queries instead of a deterministic weight-only conversion, and it does not imply the adapter is the better model off this distribution.`
* What the evidence says:
Evidence digest `results/lora_baseline.json` adapter_summary:
`mean_target_logprob_mean_over_seeds`: -7.598727984334849
`gap_closed_mean_over_seeds`: 1.3619583362730188
Base mean target logprob = -11.149778062515304, full_delta mean target logprob = -8.542466235416498.
Gap closed >1.0 means the configuration outscores the full-delta reference on this probe set; it is not a “recovery fraction” of the base-to-full gap. Describing 1.3619 as “closes 136.2% of the base-to-full gap” presents a >1.0 gap-closed value as a recovery fraction.

* Severity: WORDING
* File: results/lora_baseline_judging.md
* Exact quoted text:
`the adapter's edge is specialization to this probe distribution's style`
* What the evidence says:
The evidence shows an overshoot on the in-style Spark-96 and a reduced but still >0.6 gap closed out-of-style:
`results/lora_outofstyle.json` preregistered_rule `oos_gap_closed`: 0.6202783801053933, `instyle_gap_closed_seed20261028`: 1.3949774190074422.
The LoRA overshoot is consistent with style specialization, it is not proven causation. Style-specialization wording for the LoRA overshoot must be “consistent with” style specialization, never stated as proven causation.

### Group B: lora_panel_review.md + lora_outofstyle_design.md

**results/lora_panel_review.md**

* Severity: WORDING
* File: results/lora_panel_review.md
* Exact quoted text: 
  `THE PROJECT'S FILED INTERPRETATION: the adapter wins at matched bytes on this probe distribution; the adapter out-scoring the full fine-tune itself is attributed to specialization, because the 1,500 distillation prompts and the 96 eval probes were both written by Muse Spark in the same three bucket styles (knowledge fragments, short instructions, grade-school math), with disjoint items; no claim is made off this distribution.`
* Evidence says: The LoRA overshoot is observed on the probe set. Evidence digest `results/lora_baseline.json` shows adapter mean target logprob -7.598727984334849, gap_closed mean over seeds 1.3619583362730188, std 0.032578238750651224; full_delta mean target logprob -8.542466235416498, gap_closed 1.0. The overshoot >1.0 is a measured out-score of the full-delta reference on this probe set. The panel wording rule requires the overshoot to be described as “consistent with” style specialization, never as proven causation. The filed interpretation uses causal “because”/“attributed to”.

No other factual inconsistencies found in this file. Numbers match the digest:
* base mean_target_logprob -11.149778062515304 ≈ -11.1498
* full_delta mean_target_logprob -8.542466235416498 ≈ -8.5425, bytes 987922432
* uniform_rank32 bytes 19434496, mean_target_logprob -11.095640657042859 ≈ -11.0956, gap_closed 0.020763686533300157 ≈ 0.021
* mlp_behemoth_lite bytes 19358176, mean_target_logprob -10.54508293414888 ≈ -10.5451, gap_closed 0.2319228264458408 ≈ 0.232
* lora adapter bytes 18696192, mean_target_logprob mean over seeds -7.598727984334849 ≈ -7.5987, gap_closed mean 1.3619583362730188 ≈ 1.362, std 0.032578 ≈ 0.033
* verification zero_adapter_vs_stored_base_max_abs_per_item_diff 0.0, dense_vs_hooked_seed1_max_abs_per_item_diff 7.07604862526523e-06 ≈ 7.1e-06

**results/lora_outofstyle_design.md**

NO FINDINGS

Design numbers are consistent with the evidence digest where checkable:
* in-style baseline rank-17 LoRA 18,696,192 B, gap closed 1.362 ±0.033 matches adapter_summary mean 1.3619583362730188, std 0.032578238750651224
* lite gap closed 0.232 matches headline_comparison lite_gap_closed 0.2319228264458408
* in-style seed 20261028 gap closed 1.395 matches lora_distilled_seed20261028 gap_closed overall 1.3949774190074422
* best val KL seeds 0.9147 / 0.8974 / 0.9077 match instyle_reference best_val_kl_by_seed 0.9147066904875825 / 0.8973795699464785 / 0.9077361160092929

Pre-registered rule thresholds and the preregistered outcome in `results/lora_outofstyle.json` are internally consistent: oos_gap_closed 0.6202783801053933, instyle_gap_closed_seed20261028 1.3949774190074422, lite_gap_closed 0.2319228264458408, verdict “survives”. No gap-closed >1.0 is presented as a recovery fraction, and the filed interpretation is scoped to “consistent with” style specialization.

### Group C: lora_result_discussion.md

NO FINDINGS.

### Group D: lora_outofstyle.md + lora_outofstyle_consults.md + lora_outofstyle_judging.md

### FILE: results/lora_outofstyle.md

* **Severity: WORDING**
  * **Exact quoted text:** `The first-token behavior, the "decision to start," is the part that was style-carried.`
  * **What the evidence says / rule:** Style-specialization wording for the LoRA overshoot must be described as “consistent with” style specialization, never as proven causation. The document asserts causation that the first-token behavior *was* style-carried.

* **Severity: WORDING**
  * **Exact quoted text:** `That pattern is consistent with two of the panel's warnings at once: style match carried the first-token behavior, and part of any logprob win under a forward-KL objective is a confidence or calibration effect on continuations (Glimmer's point) rather than better first picks.`
  * **What the evidence says / rule:** Same style-specialization wording requirement. The sentence states “style match carried the first-token behavior” as a proven causal attribution rather than “consistent with”.

* **Severity: WORDING**
  * **Exact quoted text:** `Distilled on Gemini-authored prompts in a deliberately different style, the same 18.7 MB LoRA adapter still closes 62.0% of the base-to-full gap on the Spark-written 96 (vs 139.5% in-style and 23.2% for the factored patch), so the adapter's matched-byte win is not only a style-match artifact, though training-style match still adds a large share on top.`
  * **What the evidence says / rule:** Gap-closed values >1.0 must not be presented as a recovery fraction. The evidence digest shows in-style LoRA gap_closed = 1.3949774190074422 on Spark-96, i.e. the configuration outscores the full-delta reference on this probe set. Presenting this as “139.5%” / “closes 139.5%” frames the >1.0 gap-closed as a recovery fraction >100% rather than as an outscore of the full-delta reference.

All numeric values that are checkable against the evidence digest match within rounding:
* base mean_target_logprob -11.1498 vs -11.149778062515304
* full delta mean_target_logprob -8.5425 vs -8.542466235416498, bytes 987,922,432
* uniform rank-32 bytes 19,434,496, mean -11.0956, gap_closed 0.021 ≈ 0.020763686533300157
* mlp_behemoth_lite bytes 19,358,176, mean -10.5451, gap_closed 0.232 ≈ 0.2319228264458408
* LoRA in-style bytes 18,696,192, mean -7.5126, gap_closed 1.395 ≈ 1.3949774190074422, first-token accuracy 0.167 ≈ 0.16666666666666666
* LoRA out-of-style bytes 18,696,192, mean -9.5325, gap_closed 0.620 ≈ 0.6202783801053933, first-token accuracy 0.042 ≈ 0.041666666666666664
* Split scorer values, per-bucket means and mirrored Gemini-96 means all match the `results/lora_outofstyle.json` tables.

Unverifiable items in the document are not checked as wrong: teacher answer-token means 45.62 / 28.19, best val KL 0.0729 / 0.9147, etc., are not present in the evidence digest.

### FILE: results/lora_outofstyle_consults.md

NO FINDINGS

### FILE: results/lora_outofstyle_judging.md

NO FINDINGS

### Group E: recovery_tuning.md + recovery_tuning_design.md + recovery_tuning_judging.md

**results/recovery_tuning.md**
NO FINDINGS

* Factual consistency checks against the evidence digest:
  * base 0 / -11.150 / 0.000 / 0.031 → base mean_target_logprob -11.149778062515304, gap_closed 0.0, first_token_accuracy 0.03125
  * full fine-tune 987,922,432 / -8.543 / 1.000 / 0.167 → full_mean_logprob -8.542466235416498, bytes 987922432, gap_closed 1.0, first_token_accuracy 0.166666666666666666
  * uniform factored patch 19,434,496 / -11.096 / 0.021 / 0.010 → uniform_rank32 bytes 19434496, mean_target_logprob -11.095640657042859, gap_closed 0.020763686533300157, first_token_accuracy 0.010416666666666666
  * lite factored patch (untouched) 19,358,176 / -10.545 / 0.232 / 0.010 → mlp_behemoth_lite bytes 19358176, mean_target_logprob -10.54508293414888, gap_closed 0.2319228264458408, first_token_accuracy 0.010416666666666666
  * patch-init tune-up, re-quantized 19,358,176 / -8.189 / 1.136 / 0.115 → lite_recovery_tuned_requantized mean_target_logprob -8.18885623367786, gap_closed 1.1356224437995606, first_token_accuracy 0.11458333333333333
  * control-init tune-up, re-quantized 19,358,176 / -7.634 / 1.348 / 0.177 → control_recovery_tuned_requantized mean_target_logprob -7.634353652694391, gap_closed 1.3482945819075953, first_token_accuracy 0.17708333333333334
  * patch-init tune-up, fp16 factors 43,422,720 / -6.793 / 1.671 / 0.198 → lite_recovery_tuned_fp16_diagnostic mean_target_logprob -6.793331765621279, gap_closed 1.670857413990833, first_token_accuracy 0.197916666666666666
  * control-init tune-up, fp16 factors 43,422,720 / -6.848 / 1.650 / 0.271 → control_recovery_tuned_fp16_diagnostic mean_target_logprob -6.848188975580444, gap_closed 1.649817655957669, first_token_accuracy 0.2708333333333333
* Gap-closed >1.0 wording is correct: “Gap closed above 1.0 means the configuration's mean logprob on these probes is higher than the full fine-tune's; it is not a recovery fraction above 100 percent.”
* Per-bucket and first-token vs continuation numbers match the JSON rows to rounding.
* No style-specialization causation claim is made; style caveat is retained.

**results/recovery_tuning_design.md**
NO FINDINGS

* Byte target 19,358,176 B matches evidence requant bytes_requantized 19358176 and pricing_table_sum 19358176.
* Model pair, ranks, steps, learning rate, re-quantization definition and scoring pipeline are consistent with the frozen design referenced in results/recovery_tuning.json design field.
* LoRA context numbers 1.362 gap closed, 1,014 steps per seed, 18.7 MB fp16 are consistent with adapter_mean_gap_closed 1.3619583362730188 and bytes 18696192.

**results/recovery_tuning_judging.md**
* Severity: SUBSTANTIVE
  * File: results/recovery_tuning_judging.md
  * Exact quoted text: “first-token mean logprob -5.192 vs -6.150 is not in RESULTS and cannot be verified from numbers given, so \"driven mainly\" is unsupported.”
  * What the evidence says: results/recovery_tuning.json contains first_token_vs_continuation for both re-quantized rows:
    * lite_recovery_tuned_requantized.first_token_mean_logprob = -6.150312033233901
    * control_recovery_tuned_requantized.first_token_mean_logprob = -5.191730261147248
  The first-token mean logprob values are present and verifiable in the repository JSON result file.

* Severity: WORDING
  * File: results/recovery_tuning_judging.md
  * Exact quoted text: “overstatement to call control's ratio \"survived\" since control never contained the 0.232 patch, and it ignores the fp16 accuracy gap 0.198 vs 0.271.”
  * What the evidence says: The document under audit reports survival shares as “shares of each run's own fp16 gain” and the judging verdict itself notes the arithmetic 0.904/1.439=62.8% vs 1.116/1.418=78.7%. The control’s share is computed relative to its own fp16 gain over the untouched lite baseline, not as a survival of the patch’s 0.232. The wording in the judging note conflates the baseline reference.

No other factual inconsistencies, internal contradictions, or prohibited gap-closed >1.0 recovery-fraction wording were found in the audited documents.

### Group F: reply_drafts_final.md + reply_drafts_review.md

NO FINDINGS.

### Final adjudication (verbatim)

SUBSTANTIVE FLAGS

* Severity: SUBSTANTIVE
  * File: results/recovery_tuning_judging.md
  * Exact quoted text: “first-token mean logprob -5.192 vs -6.150 is not in RESULTS and cannot be verified from numbers given, so \"driven mainly\" is unsupported.”
  * What the evidence says: results/recovery_tuning.json contains first_token_vs_continuation for both re-quantized rows: lite_recovery_tuned_requantized.first_token_mean_logprob = -6.150312033233901; control_recovery_tuned_requantized.first_token_mean_logprob = -5.191730261147248. The first-token mean logprob values are present and verifiable in the repository JSON result file.

## Re-check after fixes (2026-10-29, later the same day)

Vinay approved "Fix the wording, re-validate, push". The four flagged documents were edited (no experimental number, JSON, or code changed):

- `results/recovery_tuning_judging.md`: a dated Correction note (2026-10-29, Glimmer re-check) added — claim 6's verifiability objection withdrawn (both first-token mean logprob values are in `results/recovery_tuning.json`: lite re-quantized -6.150312033233901, control re-quantized -5.191730261147248), and claim 3's baseline clarified (the 62.8% / 78.7% shares are relative to each run's own fp16 gain over the untouched lite baseline, not survival of the patch's 0.232). Pointer brackets added on claims 3 and 6.
- `results/lora_baseline_judging.md`: headline sentence reworded to repo convention — "closes 1.362 of the base-to-full gap" with an explicit not-a-recovery-fraction note (was "closes 136.2%"), and "consistent with specialization" (was "is specialization"); a dated wording note records the change.
- `results/lora_panel_review.md`: the flagged filed interpretation sits inside the verbatim question pack sent to the panel and was kept verbatim; a dated editor's note right after it states that in the project's own voice the overshoot is "consistent with" specialization, not attributed to it.
- `results/lora_outofstyle.md`: "the part that was style-carried" and "style match carried the first-token behavior" replaced with non-causal wording ("the part that did not survive the style change" / "the first-token advantage is the part that did not survive the style change"); the headline sentence's "139.5% in-style" reframed to "gap closed 1.395 in-style" with a dated framing note. No numbers changed.

Re-validation route: same as the original audit (Flash-local OmniRoute, model `nvidia/meta/muse-glimmer-30b`; every response's served-model field confirmed `meta/muse-glimmer-30b`). Four document-scoped re-check calls against a digest recomputed from the same three JSONs, plus one adjudication:

- lora_baseline_judging.md: prompt 14,298, completion 2,167, total 16,465; NO REMAINING FINDINGS.
- lora_panel_review.md: prompt 17,146, completion 1,914, total 19,060; NO REMAINING FINDINGS.
- lora_outofstyle.md: prompt 16,881, completion 2,101, total 18,982; NO REMAINING FINDINGS.
- recovery_tuning_judging.md: prompt 14,220, completion 2,701, total 16,921; substantive flag **RESOLVED** (the re-check quotes the correction note and confirms both values against the digest), NO REMAINING FINDINGS.
- Adjudication: prompt 8,567, completion 505, total 9,072; verdict **CLEAN**.

On the CLEAN re-check the push proceeded with the original approved set.
