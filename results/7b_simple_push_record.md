# 7B simple push: preparation record, Sat Oct 31, 2026

Pipeline run under Vinay's pre-authorization (Oct 31, 2026: "If they agree. Add it get reviewed. Then judged, the loop and final one push to git."). The panel voted B (push simple), 5 to 3 (record: results/7b_push_panel.md). Everything here is LOCAL prep in the local snapshot tree; nothing was pushed. The added folder, this record, and results/7b_push_panel.md join the Nov 2 push batch; the actual git push happens Nov 2 with the main batch.

## Step 1: what was added

New isolated folder `results/fifth_pair_supplementary/` (24 files, about 1 MB), copies only, originals unmoved. The per-item .logp.npz arrays were NOT copied and stay local only.

Copied verbatim (23):
- Report: fifth_pair_yardstick_and_regularization.md
- Eval JSONs: fifth_pair_heldout96.json, fifth_pair_stage2.json, fifth_pair_recompute.json, fifth_pair_yardstick_recompute.json, fifth_pair_yardstick_gen.json, fifth_pair_yardstick_eval_chat_base.json, fifth_pair_yardstick_eval_chat_down_king.json, fifth_pair_yardstick_eval_chat_full_a025.json, fifth_pair_yardstick_eval_chat_full_a05.json, fifth_pair_yardstick_eval_chat_full_delta.json, fifth_pair_yardstick_eval_chat_uniform_rank32.json, fifth_pair_yardstick_eval_corrected_base.json, fifth_pair_yardstick_eval_corrected_down_king.json, fifth_pair_yardstick_eval_corrected_full_a025.json, fifth_pair_yardstick_eval_corrected_full_a05.json, fifth_pair_yardstick_eval_corrected_full_delta.json, fifth_pair_yardstick_eval_corrected_uniform_rank32.json
- Spark judging records: spark_judging_7b.json, spark_judging_7b.md, fifth_pair_yardstick_spark_gen_judging.json, fifth_pair_yardstick_spark_interpretation.json, fifth_pair_yardstick_spark_interpretation.md

New framing text (1): index.md, the folder header, written to the panel guardrails (synthesis in results/7b_push_panel.md): framed as a supplementary scale probe, not part of the claim set; the inversion leads before any patch-favorable numbers; the 25%-scaled-delta regularization result and the yardstick-fix note carry equal up-front prominence; accuracies appear only as behavioral first-token accuracy with base and full values beside the patch's; the 86 MB patch vs 951,911,192-byte baseline appears only as a score-and-size fact inside the regularization paragraph; the junk-token trailing is stated in the same sentence as the accuracy figures. Forbidden-word scan of the final header (recovery / recovers / recovered, gap closed prose form, fraction of the fine-tune, validates at 7B, scales, winner, outright, best, beats base): 0 matches. The copied report and JSON files are verbatim records of the runs and were not rewritten.

No pointer was added anywhere: README.md, docs/submission_draft.md, docs/demo_script.md, video/, and PROVENANCE.md were not touched by this run.

### Header text as finalized (results/fifth_pair_supplementary/index.md)

# Fifth pair (Qwen2.5-7B): supplementary scale probe

Supplementary exploratory material, published for transparency. This folder is not part of the submission claim set, and no four-pair result depends on anything in it.

**The reference inverts on this pair.** On the held-out 96-question battery, the full fine-tune delta scores below the base model on mean target logprob (full delta -15.974, base -6.916), and it stays below base on the corrected battery as well (full delta -8.634, base -8.043). With the reference inverted, gap_closed is null at 7B: no fraction figure is defined for this pair, and none is claimed for any 7B configuration.

**A shrinkage control explains the patch's profile.** A plain copy of the full delta turned down to 25% strength reproduces and exceeds the selected factored configuration's (down_king) profile on both batteries (corrected battery: scaled copy -7.096 vs down_king -7.556; original battery: -6.360 vs -8.694). The apparent 7B skill of the factored patch is therefore explained as mostly a regularization effect of shrinking the delta, not as the factored format reproducing fine-tune behavior. As a score-and-size fact in the same comparison: the factored down_king patch file is 86,401,024 bytes and scores -8.694 on the original battery, where the plain 1-bit baseline file is 951,911,192 bytes and scores -11.378.

**Yardstick note, with the same prominence.** On Oct 29 an eval fix removed a chat-template echo artifact from this pair's battery (the prompt-restart echo was eliminated). Under the corrected battery the full delta's deficits shrank, and the inversion stated above remained: the full delta still does not score above the base on mean target logprob on any subset, on either battery.

**Behavioral numbers only.** First-token accuracy on the corrected battery, with base and full delta beside the patch: overall, base 0.052, full delta 0.333, down_king 0.313; on the math subset, base 0.031, full delta 0.750, down_king 0.750, and down_king's generations carry the right content but trail junk tokens. On the knowledge subset no configuration shows a gain on either battery.

**The run.** Oct 28-29, 2026: the project's factored 1-bit patch format on Qwen2.5-7B base vs Qwen2.5-7B-Instruct, executed with layer-by-layer streaming in the project's own NumPy runtime on a CPU-only machine with 11 GB of RAM, the 7B model never held whole in memory. down_king is the configuration carried forward from the Stage 2 selection (selection score -9.584). The uniform rank-32 configuration at a near-identical size (86,499,328 bytes) scored -13.158 on the original battery. The per-item logprob arrays (.logp.npz) behind the JSON files are not included in this folder.

(Contents list follows in the file; omitted here.)

## Step 2: panel review (purpose "7B simple push panel review", all calls logged)

- Muse Glimmer 30B (Flash OmniRoute; served model confirmed meta/muse-glimmer-30b). The first single-call attempt timed out with no return (curl cap; known Glimmer long-prompt failure mode; no usage recorded). The allowed retry was chunked into two calls. Chunk A (numbers): every number SUPPORTED except the two-decimal accuracy forms, flagged CONTRADICTED against the three-decimal evidence (0.05 vs 0.052, 0.33 vs 0.333, 0.31 vs 0.313, 0.03 vs 0.031). Chunk B (guardrails): the call returned 5,341 tokens with empty content (reasoning consumed the cap); no guardrail verdict from Glimmer. Glimmer totals: 10,453 tokens across the two returned calls.
- Muse Spark 1.3 (Meta Model API). First attempt returned no content (all 8,192 completion tokens were reasoning); one retry at max_tokens 24,576 returned the review. Verdict: PASS. Every number SUPPORTED (two-decimal accuracies accepted as rounding); guardrails 1-7 all PASS; it noted the score-and-size sentence and the accuracy sentence as residual skim risk, mitigated by the mandated framing, not violations. Totals: 25,924 tokens across both attempts.
- Gemini 3.5 Flash Lite: PASS. Every number SUPPORTED (rounding accepted); guardrails 1-7 all PASS; no skim-risk sentences found. 3,933 tokens.
- Muse Wonder 1.0: FLAG on scope, not digits. All numbers correct and guardrails 1-7 PASS, but two sentences were flagged as unsupported by the condensed evidence extract it was given: (A) "does not score above the base on mean target logprob on any subset, on either battery" (the extract carried overall means only); (B) "On the knowledge subset no configuration shows a gain on either battery" (the extract carried corrected-battery knowledge accuracy only). 6,111 tokens.

## Adjudications and fix (before judging)

- Glimmer rounding flag: FIXED. The header's accuracies now use the exact three-decimal values from the eval JSONs (0.052, 0.333, 0.313, 0.031, 0.750), matching the project's exact-figure discipline. Spark 1.3 and Gemini had accepted the rounding; the stricter form costs nothing.
- Wonder flag A: ADJUDICATED as an evidence-extract artifact, no text change. The folder's own report (fifth_pair_yardstick_and_regularization.md, Part A tables) gives per-subset means on both batteries, and the full delta is below base on all six subset/battery combinations (original: knowledge -19.539 vs -3.977, instruction -23.182 vs -12.164, math -5.200 vs -4.606; corrected: -13.176 vs -12.154, -7.527 vs -7.370, -5.200 vs -4.606). The report states the same sentence in substance ("still does not beat the base model on mean target log-probability on any subset, on either battery").
- Wonder flag B: ADJUDICATED as an evidence-extract artifact, no text change. Original-battery knowledge accuracy from fifth_pair_heldout96.json: base 0.094, full 0.000, down_king 0.031, uniform 0.000 (no configuration above base), and knowledge logprob favors base on both batteries (report, Question 1: "Knowledge: no config shows a gain... logprob favors base in both formats").

## Step 3 and 4: judged, the loop (purpose "7B simple push judge spark-1.2/1.1", all calls logged)

The judges received the fixed header plus a fuller evidence pack including both batteries' per-subset tables and the original-battery knowledge rows, so the adjudicated scope claims could be checked directly.

- Judge round 1, Muse Spark 1.2: PASS. All 18 header claims SUPPORTED (including the two adjudicated scope claims, verified against the per-subset evidence), guardrails 1-7 PASS, no fix required. 9,729 tokens.
- Judge round 1, Muse Spark 1.1: PASS. All 37 listed numbers/claims SUPPORTED (same two scope claims verified), guardrails 1-7 PASS. 8,859 tokens.

Loop closed after 1 judge round (of a maximum 3): both judges PASS the added material. No round-2 flags exist.

## Token totals for this pipeline (all logged in results/api_usage_log.jsonl)

- meta/muse-glimmer-30b (flash-omniroute): 10,453 (two returned calls; one timed-out attempt and one empty-content call included in the count where usage was returned: chunk A 5,112, chunk B 5,341)
- muse-spark-1.3 (meta-model-api): 25,924 (10,114 empty-content attempt + 15,810 review)
- gemini-3.5-flash-lite (google-gemini): 3,933
- muse-wonder-1.0 (meta-model-api): 6,111
- muse-spark-1.2 (meta-model-api): 9,729
- muse-spark-1.1 (meta-model-api): 8,859
- Grand total: 65,009

## Nov 2 push batch additions from this pipeline

- results/fifth_pair_supplementary/ (24 files, listed above)
- results/7b_simple_push_record.md (this file)
- results/7b_push_panel.md (already local; rides the same batch)
- results/api_usage_log.jsonl (updated with all calls above; already on the batch list)

Final verdict: the added 7B material is guardrail-compliant, every header number is supported by the folder's own eval JSONs, panel review is complete (2 PASS, 1 PASS-on-numbers with the guardrail chunk unreturned, 1 FLAG fully adjudicated/fixed), and both fresh judges PASS. Ready for the Nov 2 push.
