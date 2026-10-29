# Muse Spark judging pass: the out-of-style LoRA control (2026-10-29)

Muse Spark (muse-spark-1.3, Meta Model API) acted as an independent judge over the out-of-style control results in results/lora_outofstyle.json. Spark was given an extract copied verbatim from that file and had to return a verdict per claim with the source file cited by name. Judging call: 2884 prompt tokens, 5483 completion tokens, 8367 total. Full structured record: results/lora_outofstyle_judging.json.

Source judged: results/lora_outofstyle.json.

## Verdicts: 4 of 7 claims SUPPORTED

| Claim | Verdict | Cited file |
|---|---|---|
| O1. The out-of-style adapter is the identical artifact shape to the in-style adapter (rank 17, all seven block linears x 24 blocks, no embedding, 18,696,192 B fp16) and was trained with the identical recipe and seed 20261028; only the distillation prompt set changed (1,500 Gemini-authored prompts, varied surface style, vs 1,500 Spark-authored prompts in the Spark eval style). | UNVERIFIABLE | results/lora_outofstyle.json |
| O2. On the untouched Spark 96: base -11.1498, full delta -8.5425, uniform -11.0956 (gap closed 0.021), lite -10.5451 (gap closed 0.232), in-style adapter -7.5126 (gap closed 1.395), out-of-style adapter -9.5325 (gap closed 0.620). | SUPPORTED | results/lora_outofstyle.json |
| O3. Under the interpretation rule frozen in results/lora_outofstyle_design.md before training (>= 0.60 the win is not only style; 0.40-0.60 partly; < 0.40 mostly style), the out-of-style gap closed of 0.620 gives the verdict: survives. | UNVERIFIABLE | results/lora_outofstyle.json |
| O4. Mirrored eval on the Gemini-authored 96: the full fine-tune scores BELOW the base there (base -9.8679, full -11.3424), so mirror gap closed is recorded as null (negative denominator) and the read is on raw mean logprob: in-style adapter -7.2574 beats the out-of-style adapter -10.1504 on the Gemini set too, so crossover (each adapter wins on its own author's set) is False. | SUPPORTED | results/lora_outofstyle.json |
| O5. First-token vs continuation split on the Spark 96: in-style adapter mean first-token logprob -5.6539 and continuation -1.8587 (first-token accuracy 0.167); out-of-style adapter first-token -7.5153 and continuation -2.0173 (first-token accuracy 0.042). | SUPPORTED | results/lora_outofstyle.json |
| O6. Verification: the zero adapter in the new workdir reproduces the stored base per-item logprobs with max abs diff 0.00e+00; the dense W+B@A reference matches the hooked path at 9.66e-06; every published aggregate was recomputed from per-item rows by an independent script (worst stored-vs-recomputed diff 0.00e+00). | SUPPORTED | results/lora_outofstyle.json |
| O7. Hygiene: the control adapter trained only on the 1,350 Gemini train prompts (150 more used only for early stopping) with teacher-generated supervision; the Spark 96 and the Gemini mirror-96 were never used for training, stopping, or selection; the design, thresholds, and interpretation rule were frozen in results/lora_outofstyle_design.md before any training, after consults with Spark, Gemini, Nemotron, and Glimmer. | UNVERIFIABLE | results/lora_outofstyle.json |

## Headline question

Asked whether the honest one-sentence conclusion is: "Distilled on Gemini-authored prompts in a deliberately different style, the same 18.7 MB LoRA adapter still closes 62.0% of the base-to-full gap on the Spark-written 96 (vs 139.5% in-style and 23.2% for the factored patch), so the adapter's matched-byte win is not only a style-match artifact, though training-style match still adds a large share on top."
Spark's answer: yes.


## Follow-up passes (same pattern as the baseline judging)

Pass 1 left O1, O3, and O7 UNVERIFIABLE because the judge had not been given the
design file. Two follow-up passes embedded verbatim extracts from
results/lora_outofstyle_design.md, results/lora_outofstyle_consults.md, the
result file's control and generation records, and a script count over the prompt
file (full record: results/lora_outofstyle_judging.json).

- O1: SUPPORTED (pass 2). O3: SUPPORTED (pass 2).
- O7: still UNVERIFIABLE, on one component only: whether the design was frozen
  before training in wall-clock time cannot be proven from file extracts, as the
  judge itself noted. Its substantive parts (1,350 train / 150 validation split,
  teacher-generated supervision, eval sets never used for training, stopping, or
  selection) are documented in the frozen design and were confirmed present in
  the pass-3 extract.

Final tally: 6 of 7 claims SUPPORTED, 0 CONTRADICTED, O7 unverifiable on the
timing component only. The headline sentence was approved verbatim.
