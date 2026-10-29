# Recovery tuning of the factored patch: design (frozen before training)

Date: 2026-10-29. Status: design frozen before any training run, and amended
the same day by the panel amendment recorded at the end of this file, also
before any training run. This experiment is a PILOT: one seed. No
training-cost claim may be drawn from it alone. Local only, not pushed.

## Question

The matched-byte LoRA baseline (results/lora_baseline.md) beat the factored
patch at the same byte budget, but it cost 1,500 teacher generations and about
8 hours of CPU training across 3 seeds (per seed: 1,014 steps, 9,683 s for
seed 20261028). The factored patch costs nothing to produce: it is a
deterministic conversion of weights already held. Vinay's question, worked
out with Gemini: what if the factored patch gets a short training pass of its
own, about a tenth of the LoRA budget? Does a cheap tune-up recover much of
the gap, and does any of the gain survive being put back into the shipped
format?

## The one rule that makes this honest

If the trained factors are kept in floating point, the result is just another
adapter and proves nothing about our format. So the headline result is not
the trained factors. The headline is: train the shipped patch's factors
briefly, form the trained delta, then re-quantize it with the compressor's
own 1-bit factored quantizer (src/factored.py quantize_delta) at the exact
same per-matrix ranks, producing a patch in the exact same format at the
exact same byte count (19,358,176 B, priced the same way the compressor
prices mlp_behemoth_lite, summed over all 169 matrices including the rank-0
ones). Only that re-quantized patch counts as the result. A secondary
diagnostic row keeps the trained factors in fp16 and prices them honestly
(43,422,720 B for U and V in fp16 at these ranks); it is labelled a
diagnostic everywhere and is never the headline.

## Setup

- Model pair: Qwen2.5-0.5B base / Qwen2.5-0.5B-Instruct, same as every other
  row in this repo's results.
- Starting point: the shipped mlp_behemoth_lite factors
  (~/fc-v04-sweep/heldout/factors_mlp_behemoth_lite.npz on Flash), 145
  matrices. Rank map by layer name: embed 10, attn.q_proj 20, attn.k_proj 0
  (no factor stored), attn.v_proj 20, attn.o_proj 20, mlp.gate 45, mlp.up 45,
  mlp.down 40.
- Trainable parameters: the U and V factors of those 145 matrices, in fp32,
  initialized exactly at the shipped values. The base model is frozen. The
  embedding factors are applied at both tied places (input embedding and
  output head), exactly as the shipped format applies them.
- Data: the existing in-style LoRA distillation set, reused as is. 1,500
  Muse Spark prompts in the eval's three styles (knowledge, instruction,
  math), teacher answers are the full fine-tune's own greedy generations,
  stored in ~/fc-v04-sweep/lora_baseline/distill_dataset.json. Train split
  1,350, validation split 150. No new prompts, no new teacher generations,
  no new API calls except the judging call at the end. The style caveat from
  the LoRA baseline applies here unchanged: training prompts and eval
  questions share an author and the same three styles, items are disjoint
  and novelty-checked, and any win is a win on this probe distribution only.
- Objective: identical to the LoRA baseline. Soft forward KL
  (teacher||student, temperature 1) at teacher-answer positions, teacher run
  online from the full Instruct weights, base plus trainable patch as the
  student.
- Budget: 101 optimizer steps at batch size 8 (808 examples, about 0.6 of
  one epoch). That is 10 percent of the LoRA run's 1,014 steps per seed.
  One seed: 20261028, with the same data order the seed produces in the
  LoRA trainer.
- No checkpoint selection: the state after step 101 is the result. The
  validation split KL is logged for transparency only (cadence set by the
  amendment at the end of this file); it does not pick the checkpoint.
  Picking the best checkpoint would quietly spend the validation signal
  and break the fixed budget claim.
- Optimizer: AdamW, betas (0.9, 0.999), weight decay 0, gradient clip 1.0,
  OneCycle schedule, same as the LoRA trainer, except the learning rate.

## Learning rate: 2e-5, and why

- 2e-5 is the panel's converged value for both the headline run and the
  control run (amendment below); it also sits inside the 1e-5 to 5e-5 band
  Gemini suggested for training compressed factors.
- The LoRA run used 2e-4, but it started from a random A and a zero B, so
  it had to search. These factors start at the compressor's converged
  least-squares solution; the job is a nudge, not a search.
- Scale check against the shipped factors: U entries average about 0.009 in
  absolute value (they are per-row scales times signs), V entries average
  about 0.004 with a max near 1.1 on the embedding. With AdamW, one step
  moves a parameter by roughly the learning rate. At 2e-5 for 101 steps the
  largest possible drift is about 0.002, the same order as the factor
  entries themselves: enough to matter, not enough to blow the
  factorization apart. At 2e-4 the drift bound would be 0.02, larger than
  a typical U entry: too hot for a tune-up.

## Re-quantization (frozen definition)

For each of the 145 matrices: trained delta D' = U_trained @ V_trained.T in
fp64, then factored.quantize_delta(D', rank) with the matrix's shipped rank.
That is the compressor's own construction (SVD, U forced to signs times
per-row mean-absolute scales, V refit by least squares against the signed
U). The output is saved in the same npz layout as every other factors file.
Byte check: sum of factored.storage_bytes over all 169 recipe matrices at
the lite rank map (rank 0 matrices priced by the same formula, as in the
original build) must equal 19,358,176 exactly.

## Scoring

Same pipeline as every factored row: the house NumPy forward
(alien_sweep_stage2), dense apply of U @ V.T onto the base weights, same
combined 96 held-out probes, same chat formatting. Rows reported:

- base, full fine-tune, uniform rank-32, lite untouched (from the stored
  heldout96 eval files, recomputed in validation),
- lite + recovery tuning, re-quantized (headline),
- lite + recovery tuning, trained factors in fp16 (diagnostic, priced at
  43,422,720 B),
- the LoRA adapter mean over 3 seeds (context row, from
  results/lora_baseline.json).

Metrics per row: mean target logprob, gap closed against the base-to-full
gap, first-token accuracy, per-bucket breakdown (knowledge, instruction,
math), and a first-token vs continuation split (mean logprob of the first
answer token, and mean per-token logprob over the remaining answer tokens).

Before any new row is trusted, the eval code path used here re-scores the
untouched lite factors and must reproduce the stored lite per-item rows.

## Interpretation rule, frozen in advance

Report whatever comes out. If the re-quantization kills the training gain,
that is the result, stated plainly. If part of the gain survives, the claim
is only ever about this probe distribution and this pair, with the style
caveat attached. Cost is reported honestly: optimizer steps and wall time
for the tune-up, next to the LoRA run's per-seed cost (1,014 steps,
9,683 s) and its one-time teacher generation cost, which this experiment
reused for free and a fresh user of the recipe would not have to repeat
either, since the distillation set is a byproduct of the baseline study.
Validation: independent script recomputation of the headline row from
stored per-item rows, the byte-count check, and Muse Spark judging of the
interpretation claims (logged, purpose "recovery tuning").

## Amendment (panel discussion, 2026-10-29, before training)

Source: results/lora_result_discussion.md. The panel (Muse Spark, Gemini,
Nemotron, Glimmer, Grok) ruled unanimously, 5 of 5, that the run as
originally frozen would be uninterpretable: without a matched control, any
gain is fully confounded between "the patch initialization held part of the
answer" and "101 steps of KL training helps from anywhere." The following
changes are adopted in full.

1. Matched control run, added. Identical to the headline run in every way:
   same U/V parameterization and lite layer allocation (the same 145
   matrices at the same ranks, embedding included), same 101 steps, same
   batch size 8, same 1,350 stored training prompts in the same order,
   same forward-KL objective with the teacher online, same learning rate
   2e-5 and schedule, same seed 20261028, same re-quantizer, same 96
   probes. The only difference is initialization: instead of the shipped
   factors, U is drawn from a normal distribution with standard deviation
   0.02 (the LoRA baseline's A init, same torch seed) and V starts at zero,
   so the control's initial delta is exactly zero everywhere, the same
   starting point the LoRA baseline's adapter had. The headline comparison
   is patch-init re-quantized vs control-init re-quantized at identical
   bytes (19,358,176 B each; the byte check applies to both files).
2. Learning rate 2e-5 for both runs is recorded as panel-set (it was
   already the frozen value; the justification above stands).
3. Pilot label: the whole experiment is a pilot (one seed). Cost figures
   are reported as observed pilot numbers only; no training-cost or
   cost-saving claim is drawn from this experiment alone. The LoRA row
   stays as context only, and the 101-step factors are not compared
   against the 1,014-step LoRA adapter as if like-for-like: the
   parameterizations and fp16 prices differ (43 MB vs 18.7 MB).
4. Validation trajectory (panel's Demand B outcome: frozen rule plus
   trajectory logging): in addition to the full 150-item validation KL at
   steps 0 and 101, both runs log validation KL on a fixed 30-item subset
   of the validation split every 10 steps. Still no checkpoint selection:
   the step-101 state is the result in both runs.
5. Rejected by the panel, not done: best-checkpoint selection,
   quantization-aware training, and promoting any fp16 diagnostic row to
   headline. The fp16 rows for both runs stay labelled diagnostics.
6. Predictions are on record in the discussion file and the design was
   not tuned toward any of them: four panelists cluster at 0.18 to 0.38
   gap closed for the patch-init re-quantized headline (Spark 0.20 to
   0.35, Glimmer 0.20 to 0.35, Grok 0.18 to 0.38, Nemotron 0.20 to 0.38
   after moving down in Round 2); Gemini alone predicts 0.45 to 0.65.
   Named mind-change thresholds: a re-quantized headline at or above
   roughly 0.55 to 0.6, or the patch initialization beating the matched
   control by 0.3 gap closed or more.
