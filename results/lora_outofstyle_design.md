# Out-of-style LoRA control: design (frozen before any training)

Date: Thu Oct 29, 2026. Status: design frozen before any training or generation for
this control; local only, nothing pushed.
Origin: results/lora_panel_review.md voted 4-1 for this control (Gemini, Nemotron,
Grok, Glimmer for; Spark against). Vinay approved Oct 29: "Good call. Check with
other ai before doing it and take there input." This document is that check: the
draft design was pressure-tested with Muse Spark, Gemini, Nemotron, and Glimmer
before freezing (consults logged: Spark and Gemini in results/api_usage_log.jsonl,
purposes lora_outofstyle_design_consult_spark / _gemini; Nemotron and Glimmer via
Flash OmniRoute, Flash-local, not in the API log).

## The question

The in-style baseline (results/lora_baseline.json): a rank-17 LoRA adapter
(18,696,192 B fp16) distilled from the full Qwen2.5-0.5B-Instruct fine-tune on
1,500 Spark-written prompts in the same three bucket styles as the 96 Spark-written
eval probes closed 1.362 +- 0.033 of the base-to-full gap, beating the factored
patch (lite 0.232) and the full fine-tune itself on that distribution. The filed
interpretation: the overshoot is "consistent with" style specialization (panel
wording rule), not a proven cause, because training prompts and eval probes share
one author and one style family.

This control asks: does the adapter win survive when the distillation prompts
come from a different author in a deliberately different surface style, scored on
the same untouched 96?

## Consult verdicts and what was folded in

All four consultants agreed on the central limit: changing author + surface
phrasing does NOT isolate "style" as a latent variable. Content buckets, the
teacher, and the eval stay shared, so what this control actually tests is whether
the win survives an author/phrasing distribution shift in the training prompts.
The interpretation below is scoped to exactly that. Specific input adopted:

- Spark (strongest consult): (a) an eval only on Spark-96 is asymmetric and
  favors the in-style adapter by construction; ADOPTED as a mirrored 2x2: a new
  Gemini-authored 96-probe eval set, and both adapters scored on both eval sets.
  The style hypothesis predicts a crossover interaction, not just a drop on
  Spark-96. (b) Freeze numeric thresholds in advance; ADOPTED below. (c) Log
  teacher answer statistics for both prompt sets (answer length, end-token rate)
  so a teacher-degradation confound is visible, not hidden; ADOPTED.
- Glimmer: teacher-capability shift and difficulty/length confounds named;
  ADOPTED as reporting (per-bucket prompt length stats for both training sets;
  teacher generation stats; best validation KL compared across runs as a
  target-learnability signal). Its author-swap paraphrase control (a third
  training run) is NOT adopted: budget; the mirrored eval separates home-turf
  advantage symmetrically, which is the operative question. Recorded as future
  work.
- Nemotron: teacher-swap proposal (distill from the BASE model on Gemini
  prompts) NOT adopted, with reason: the baseline claim is "adapter distilled
  from the fine-tune"; a base-teacher adapter carries no fine-tune information
  and cannot speak to the base-to-full gap this comparison is scored on. Its
  teacher-accent concern is handled by the 2x2 and the teacher-stat reporting.
- Gemini: 3 seeds and a 4th out-of-domain training bucket NOT adopted: the panel
  mandate and the time box are one seed, the in-style seed spread is 0.033
  (small against the 0.4/0.6 thresholds below), and a 4th bucket would break the
  identical-recipe comparability. The single-seed fragility is recorded as a
  stated limit, and the mirrored eval is the hedge.

## Frozen design

Distillation prompts (control set):
- 1,500 prompts authored by GEMINI (gemini-3.5-flash-lite), 500 per bucket
  (knowledge, instruction, math), same CONTENT buckets as the eval, deliberately
  different SURFACE style: knowledge as full questions / exam items /
  fill-in-the-blank / true-false / conversational asks (bare fragments rejected
  by an end-punctuation check); instruction as polite requests, scenario
  framing, prose constraints (not bare commands); math as varied question
  formats with NO fixed suffix (the Spark suffix phrase "Answer with just the
  number" is banned outright and rejected on sight).
- Hygiene identical to the in-style run: exact normalized match or token-set
  Jaccard >= 0.7 against all 96 eval prompts, the 24 Signet prompts, and (extra)
  the 1,500 in-style Spark prompts is rejected; accepted prompts exclude each
  other at Jaccard >= 0.6. One logged regeneration retry per failed batch;
  buckets topped up with extra batches. Note: the original /tmp Signet list did
  not survive; the Signet 24 are the heldout24-subset prompts, already inside
  the 96, so eval-side coverage is complete either way.
- Split identical: fixed-seed (20261028) per-bucket shuffle, 450 train +
  50 validation per bucket. Validation used ONLY for early stopping on
  distillation KL. The eval probes are never used for training, stopping, or
  selection.

Teacher and training (identical recipe to the in-style run):
- Teacher: the same full fine-tuned Qwen2.5-0.5B-Instruct, its own greedy
  generations, max 48 tokens, stop at <|im_end|>. Teacher answers generated with
  the same validated batched torch port as the in-style run.
- Soft forward KL (teacher||student, T=1) at teacher-answer positions, teacher
  online. Rank 17 on all seven block linears x 24 blocks, no embedding adapter,
  alpha 32 folded into B at export, scored from the fp16-rounded file. AdamW
  lr 2e-4 cosine, batch 8, up to 6 epochs (1,014 steps), val KL every 100
  steps, early stop patience 2. ONE seed: 20261028 (the in-style headline seed).
- Forward-port validation reruns as part of prep (torch port vs stored NumPy
  base scores; KV-cache vs full-forward greedy check), same as the in-style run.

Mirrored eval set (Gemini-96):
- 96 NEW probes authored by Gemini with reference answers, 32 per bucket
  (subset split mirroring the Spark 96: 8 per bucket labelled heldout24, 24 per
  bucket labelled heldout72_new), in the same Gemini conventions as the control
  prompts. Eval-only: never trained on. Novelty-checked against the Spark 96,
  both 1,500-prompt training sets (>= 0.7 rejected), and within itself
  (>= 0.6). Reference answers are Gemini's short correct responses (math: the
  number; knowledge: the fact; instruction: a minimal correct response).

Scoring:
- Primary: the same untouched Spark combined-96 through the canonical
  lora_baseline.py eval path. Table: base / full delta / uniform rank-32 /
  lite / in-style adapter seed 20261028 (stored rows) / out-of-style adapter,
  with gap closed, first-token accuracy, per-bucket breakdown.
- Mirrored: all six rows scored on the Gemini-96 through the same machinery
  (factored and reference rows via the stage-2 forward, adapters via the hooked
  forward), same table shape.
- First-token vs continuation split (Glimmer's KL-shape check): for both
  adapters on both eval sets, and for base and full on both sets, a split
  scorer reports mean first-answer-token logprob separately from mean
  continuation logprob per item (first-token share of the total). The split
  scorer must reproduce the canonical per-item totals before its splits are
  trusted (checked in validation).
- Reported alongside: per-bucket prompt word-length stats for both training
  sets; teacher generation stats for both sets (answer tokens mean/min/max,
  ended-with-im_end count); best val KL of this run vs the in-style seeds
  (0.9147 / 0.8974 / 0.9077).

## Pre-registered interpretation rule (frozen)

On the Spark-96 (gap closed, out-of-style adapter, one seed; in-style reference
1.362 for seed 20261028: 1.395; lite patch 0.232):
- >= 0.60: the adapter win is NOT only style. It survives an author/phrasing
  shift in training prompts, far above the factored patch.
- 0.40 to 0.60: PARTLY. Clearly above the patch, well below in-style: the
  style match explains a large share of the in-style win, not all of it.
- < 0.40: MOSTLY STYLE. The in-style win was mostly the shared style; at
  <= 0.33 the adapter no longer clearly beats the factored patch either.
Mirrored read: if on the Gemini-96 the out-of-style adapter beats the in-style
adapter while the in-style adapter wins on Spark-96 (crossover), home-turf
style match is a real, symmetric effect. If the in-style adapter wins on both
eval sets, style match alone does not explain the ranking.
Wording rule (panel): whatever the outcome, "specialization" is stated as
"consistent with" unless the crossover plus the Spark-96 thresholds jointly
support the stronger reading; disagreements between the checks are reported,
not averaged away.

## Budget

Teacher generation ~35 min batched, training ~2.6-2.9 h (one seed), canonical
eval ~5 min, mirrored + split passes ~40 min, all on Flash, one heavy stage at
a time, peak RSS under ~6.5 GB. Validation: independent script recomputation of
the new rows from per-item data, plus a Muse Spark judging pass over the
interpretation claims with file citations (Meta API, logged, purpose
"lora out-of-style").

## Files

- Prompts: examples/lora_outofstyle_gen.py -> data/distill_prompts_gemini_oos.json
  (gitignored data/); generation record /tmp/lora_oos_gen_record.json (copied
  into the results JSON).
- Mirror probes: examples/lora_outofstyle_mirror_gen.py ->
  data/mirror96_probes_gemini.json; record /tmp/lora_oos_mirror_record.json.
- Flash pipeline: examples/lora_baseline.py (prep / train / eval, unchanged),
  workdir ~/fc-v04-sweep/lora_outofstyle on Flash; split scorer
  examples/lora_outofstyle_split.py.
- Results: results/lora_outofstyle.json and results/lora_outofstyle.md;
  judging in results/lora_outofstyle_judging.md/.json.
