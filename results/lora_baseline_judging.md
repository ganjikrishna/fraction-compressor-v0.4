# Muse Spark judging pass: the LoRA baseline (2026-10-28)

Muse Spark (muse-spark-1.3, Meta Model API) acted as an independent judge over the LoRA-baseline results in results/lora_baseline.json. Spark was given an extract copied verbatim from that file (table, adapter summary, verification block), and had to return a verdict per claim with the source file cited by name. Final judging call: 3288 prompt tokens, 3920 completion tokens, 7208 total. Full structured record: results/lora_baseline_judging.json.

Source judged: results/lora_baseline.json.
(gap_closed = (config - base) / (full_delta - base) on mean target logprob over the combined 96 fresh held-out questions; base -11.1498, full -8.5425.)

## Verdicts: 7 of 7 claims SUPPORTED

| Claim | Verdict | Cited file |
|---|---|---|
| L1. The LoRA adapter prices at exactly 18,696,192 bytes fp16 (9,348,096 params, rank 17, all seven block linears x 24 blocks, no embedding), under the uniform factored budget of 19,434,496 B and the lite budget of 19,358,176 B. | SUPPORTED | results/lora_baseline.json |
| L2. Adapter mean target logprob over 3 seeds is -7.5987 (std 0.0849), closing 1.362 of the base-to-full gap (base -11.1498, full -8.5425). | SUPPORTED | results/lora_baseline.json |
| L3. The uniform factored patch closes 0.021 and the lite factored patch closes 0.232 on the same 96; the adapter's mean gap closed is higher than both. | SUPPORTED | results/lora_baseline.json |
| L4. Blocks-only comparison: with the embedding delta dropped, uniform closes 0.116 at 18,161,664 B and lite closes 0.172 at 18,542,592 B, vs the adapter's 1.362 at 18,696,192 B. | SUPPORTED | results/lora_baseline.json |
| L5. Forward-path verification: the zero adapter reproduces the stored base per-item logprobs with max abs diff 0.00e+00, and the dense W+B@A reference matches the hooked (X@A.T)@B.T path with max abs per-item diff 7.08e-06. | SUPPORTED | results/lora_baseline.json |
| L6. Precision sensitivity: scoring seed 1 from fp32-unrounded A/B gives -7.5126 vs -7.5126 from the fp16-rounded file; the factored rows re-scored with V rounded through fp16 move uniform to -11.0955 (from -11.0956) and lite to -10.5451 (from -10.5451). | SUPPORTED | results/lora_baseline.json |
| L7. Hygiene: the adapter trained only on 1,350 fresh prompts (150 more used only for early stopping) with teacher-generated supervision; the 96 eval prompts and their reference answers were never used for training, stopping, or selection; hyperparameters were frozen in results/lora_baseline_design.md before training. | SUPPORTED | results/lora_baseline.json |

## Headline question

Asked whether the honest one-sentence conclusion is: "At about 19 MB on the Qwen2.5-0.5B pair, a LoRA adapter distilled from the fine-tune closes 1.362 of the base-to-full gap on the combined 96 (a gap-closed value above 1.0: the adapter outscores the full-delta reference on this probe set; it is not a recovery fraction above 100%), more than the full fine-tune itself scores on this probe set and far more than the post-hoc factored patch (23.2% lite, 2.1% uniform); the adapter's edge is consistent with specialization to this probe distribution's style, bought with gradient training on 1,500 teacher queries instead of a deterministic weight-only conversion, and it does not imply the adapter is the better model off this distribution."
Spark's answer: yes.

Wording note (2026-10-29, Glimmer re-check): the headline sentence above was reworded to the repo convention — gap closed stated as 1.362 rather than "136.2%", and the specialization wording softened to "consistent with specialization". No numbers were changed; the sentence is otherwise the one Spark approved.

