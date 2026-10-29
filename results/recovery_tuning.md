# Recovery tuning: the cheap tune-up, tested with a matched control

Pilot, one seed (20261028), local only. Design frozen before training in
results/recovery_tuning_design.md, including the panel amendment in
results/lora_result_discussion.md. Numbers: results/recovery_tuning.json,
independently recomputed from stored per-item rows by
examples/recovery_tuning_check.py.

## Plain-words summary

We gave the shipped patch a short training pass (101 steps, about 21
minutes) to see if a cheap tune-up recovers what the full LoRA training
bought at 10 times the steps. The panel required a matched control: the
exact same run starting from random and zero factors instead of from the
patch. Both trained factor sets were then squeezed back through the
project's own 1-bit quantizer to the exact same size as the shipped
patch, 19,358,176 bytes.

Three findings. First, the tune-up works far better than anyone on the
panel predicted: from 0.232 gap closed for the untouched patch, the
re-quantized artifacts reach 1.136 (patch start) and 1.348 (control
start), past every recorded prediction (four panelists said 0.18 to
0.38, Gemini said 0.45 to 0.65). Second, the patch start did not win.
Before the squeeze the two runs were effectively tied, and after it the
control is ahead by 0.213. Starting from the patch helped the training
objective a lot and the shipped format not at all. Third, this is a
one-seed pilot: it says what happened once, on this pair and this probe
set, and no training-cost claim is drawn from it.

## Results (combined 96 held-out probes, same scoring as all other rows)

| Config | Bytes | Mean logprob | Gap closed | First-token acc |
|---|---|---|---|---|
| base | 0 | -11.150 | 0.000 | 0.031 |
| full fine-tune | 987,922,432 | -8.543 | 1.000 | 0.167 |
| uniform factored patch | 19,434,496 | -11.096 | 0.021 | 0.010 |
| lite factored patch (untouched) | 19,358,176 | -10.545 | 0.232 | 0.010 |
| patch-init tune-up, re-quantized | 19,358,176 | -8.189 | 1.136 | 0.115 |
| control-init tune-up, re-quantized | 19,358,176 | -7.634 | 1.348 | 0.177 |
| patch-init tune-up, fp16 factors (diagnostic) | 43,422,720 | -6.793 | 1.671 | 0.198 |
| control-init tune-up, fp16 factors (diagnostic) | 43,422,720 | -6.848 | 1.650 | 0.271 |

Gap closed above 1.0 means the configuration's mean logprob on these
probes is higher than the full fine-tune's; it is not a recovery
fraction above 100 percent. The style caveat from the LoRA baseline
applies unchanged: distillation prompts and eval probes share an author
(Muse Spark) and the same three style buckets, items disjoint and
novelty-checked, so these are wins on this probe distribution.

Per-bucket mean logprob for the two re-quantized rows: patch-init
knowledge -6.716, instruction -13.743, math -4.107; control-init
knowledge -5.765, instruction -13.550, math -3.588. The control leads in
all three buckets. First-token vs continuation split: the control leads
on first-token mean logprob (-5.192 vs -6.150) and first-token accuracy;
the patch-init row leads only on continuation logprob per token
(-1.208 vs -1.447).

## What we think it means

The patch really did hold part of the answer for the training
objective. On the distillation validation split, the patch start began
at KL 1.079 where the control began at 2.560, and finished at 0.212
where the control finished at 1.205. Warm starting worked exactly as
advertised, on the objective it was trained on.

It did not survive the trip back into the format. The two trained
factor sets were effectively tied on probe logprob before
re-quantization (fp16 diagnostics 1.671 vs 1.650, though the control
already led on first-token accuracy there, 0.271 vs 0.198). After
re-quantization, the share of the fp16 gain over the untouched patch
that remained was 62.8 percent for the patch start and 78.7 percent
for the control. One plausible mechanism, stated as a hypothesis: the
patch start's trained delta still carries large components inherited
from the original full delta, and the 1-bit sign quantizer damages
exactly those; the control's delta was built by gradient descent
inside the factored form, so more of it sits in directions the format
represents well. The pilot cannot confirm that mechanism; it can only
report that the ordering is created at the quantizer, not in training.

The wider surprise is the parameterization, not the initialization.
101 steps on these factors (21.7M trainable parameters including the
embedding, per-matrix ranks up to 45) moved the re-quantized artifact
from 0.232 to above 1.1 from either start. The panel's predictions
were anchored on the LoRA run's economics; this run's factors have
more capacity and a different shape, and the comparison to the LoRA
adapter (1.362 gap closed, 1,014 steps per seed, 18.7 MB fp16) is
context only, not like-for-like.

Observed cost, pilot numbers only: 101 steps and 1,260 s wall for the
patch run, 101 steps and 1,254 s for the control, peak memory 5.78 GB
each on the home machine; re-quantization 83 s per run; the teacher
answers were reused from the LoRA baseline study, so neither run paid
any generation cost. Factor drift during the tune-up was small, as
designed at lr 2e-5: largest single-entry change 0.0011 in U and
0.0009 in V for the patch run.

## Validation

- Eval machinery: the eval path used here re-scored the untouched lite
  factors and reproduced the stored lite per-item logprobs bit-exactly
  (max abs diff 0.0, first-token flags identical).
- Training forward: the factored torch forward reproduced the stored
  NumPy scores on 12 eval items before each run (max abs diff 3.4e-05
  against lite for the patch init, 8.6e-05 against base for the
  zero-delta control init).
- Byte counts: both re-quantized files verified at exactly 19,358,176
  bytes three ways (repricing from array shapes, pricing-table sum,
  cross-checks of shapes, ranks, and stored flags against the base
  model header and the factor files).
- Recomputation: every aggregate in results/recovery_tuning.json was
  recomputed by an independent script from stored per-item rows.
- Judging: Muse Spark judged 7 interpretation claims
  (results/recovery_tuning_judging.md): 4 supported, 3 partly
  supported, 0 unsupported. The three partly-supported verdicts were
  wording corrections, applied above: the control's result is not
  described as a gain "from 0.232" (its delta started at zero), the
  survival shares are phrased as shares of each run's own fp16 gain,
  and no "driven mainly" causal claim is made for the bucket pattern.

## Files

- Design: results/recovery_tuning_design.md
- Numbers: results/recovery_tuning.json
- Judging: results/recovery_tuning_judging.md
- Code: examples/recovery_tuning.py (train, requant, eval),
  examples/recovery_tuning_check.py (independent recomputation)
- Run artifacts on Flash: ~/fc-v04-sweep/recovery_tuning/ (train logs,
  trained and re-quantized factor files, per-config eval JSONs)
