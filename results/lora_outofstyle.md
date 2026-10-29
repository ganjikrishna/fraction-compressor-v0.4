# Out-of-style LoRA control: does the adapter win survive off-style?

Date: Thu Oct 29, 2026. Local only, not pushed. Machine record:
results/lora_outofstyle.json. Frozen design: results/lora_outofstyle_design.md.
Design consults: results/lora_outofstyle_consults.md. Spark judging:
results/lora_outofstyle_judging.md.

## Plain-words summary

Short answer: yes by the rule we froze before training, but only just, and the
part that survives is narrower than the headline.

The same 18.7 MB LoRA adapter shape, trained the same way on 1,500 prompts
written by Gemini in a deliberately different style instead of Spark prompts in
the eval's own style, still closes 0.620 of the base-to-full gap on the
untouched Spark 96. The factored patch closes 0.232. So at matched bytes the
adapter still beats the patch by a wide margin with no style match at all: the
win is not only style.

Three honest qualifiers. First, 0.620 sits just 0.02 above the 0.60 line we
froze in advance for "survives" (below 0.40 would have been "mostly style"),
and this is one seed, so the exact placement near the line should not be
over-read. Second, the surviving win lives in continuation confidence, not in
first-token picks: off-style, the adapter's first-token accuracy is 0.042
(in-style 0.167, full fine-tune 0.167), while its continuation logprob (-2.017)
stays close to the in-style adapter's (-1.859). The first-token behavior, the
"decision to start," is the part that did not survive the style change. Third, style match
still adds a lot on top: the in-style adapter closes 1.395, more than double
the off-style 0.620.

The honest sentence for the submission (wording approved by the Spark
judging pass, with one framing adjustment noted below):

> Distilled on Gemini-authored prompts in a deliberately different style, the
> same 18.7 MB LoRA adapter still closes 62.0% of the base-to-full gap on the
> Spark-written 96 (vs gap closed 1.395 in-style and 23.2% for the factored patch), so
> the adapter's matched-byte win is not only a style-match artifact, though
> training-style match still adds a large share on top.

Framing note (2026-10-29, Glimmer re-check): the sentence as approved read
"139.5% in-style"; it is stated here as gap closed 1.395 per the repo
convention, since a value above 1.0 is an outscore of the full-delta
reference, not a recovery fraction. No number changed.

## Why this control exists

The matched-byte LoRA baseline (results/lora_baseline.md) beat the factored
patch by a wide margin, but its distillation prompts were written by Muse
Spark in the same three bucket styles as the Spark-written eval probes. The
panel review (results/lora_panel_review.md) voted 4-1 to run this control:
distill on prompts from a different author in a different surface style, and
re-score on the same untouched 96. Vinay approved, with the instruction to
consult other AIs on the design first and take their input.

## Phase 1: design consults (before anything was built)

Four consultants pressure-tested the draft design. Full texts:
results/lora_outofstyle_consults.md. Convergent verdict: no consultant said
the design cleanly isolates "style" as a latent variable. What it does test is
whether the win survives an author and phrasing distribution shift in the
training prompts. Their main breaks, and what was folded into the frozen
design (results/lora_outofstyle_design.md):

- Spark (Meta API): an eval only on Spark-96 is asymmetric by construction;
  teacher targets degrade off-distribution; varied prompt length shifts the
  KL token mass at fixed steps; one seed; the interpretation rule needed
  numbers. Adopted: a mirrored 2x2 (both adapters scored on a new
  Gemini-authored 96 as well), pre-registered thresholds (0.60 / 0.40),
  teacher answer-length logging.
- Gemini: the control tests author and template robustness, not style
  independence; same content buckets; Gemini has its own style footprint.
  Suggested a fourth off-domain bucket and 3 seeds. Not adopted: the panel
  mandate and time box were one seed, and a fourth bucket breaks the
  identical-recipe comparison. Recorded in the frozen design.
- Nemotron (Flash OmniRoute): the teacher is the fine-tune itself, so its
  answers on Gemini prompts keep Spark-isms (teacher style leakage); the
  bucket structure is content, not style. Proposed distilling from the base
  model instead. Not adopted: a base-teacher adapter carries no fine-tune
  information and cannot speak to the base-to-full gap. Handled instead by
  the 2x2 plus teacher-stat reporting.
- Glimmer (Flash OmniRoute): single seed; teacher capability shift could
  explain a collapse; no measured style distance; report teacher performance
  on both prompt sets and best val KL for both runs. Adopted as reporting.

One operational note: the reference answers for the primary eval are
Spark-written, so "gap closed" on either set is measured against that
author's answer style. The mirrored set exists to make that asymmetry visible
rather than hide it.

## What ran

- Prompts: 1,500 from gemini-3.5-flash-lite, 500 per bucket (knowledge,
  instruction, math), 450 train / 50 validation per bucket. Different surface
  conventions by design: knowledge as full questions, exam items, fill-in and
  true/false (bare fragments rejected); instruction as polite requests and
  scenario framing (bare commands rejected); math in varied formats with the
  Spark suffix "Answer with just the number" banned and rejected on sight.
  Hygiene matched the in-style run: exact normalized match or token-set
  Jaccard >= 0.7 against the 96 eval, the 24 Signet prompts, and the 1,500
  in-style prompts rejected; within-set >= 0.6 rejected; dropped items logged,
  one regeneration retry per batch, buckets topped up.
- Prompt length (words, mean / min / max): Gemini knowledge 14.1 / 6 / 24 vs
  Spark 9.8 / 4 / 17; instruction 13.8 / 7 / 22 vs 11.0 / 3 / 23; math
  19.8 / 4 / 47 vs 19.4 / 12 / 30.
- Teacher: the same full fine-tuned Qwen2.5-0.5B, its own greedy generations,
  same caps, produced with the validated batched port after the forward port
  was re-validated on these prompts (checks below).
- Training: identical recipe and seed 20261028. One seed, per the panel
  mandate and the time box.
- Scoring: the untouched combined 96 through the canonical house NumPy eval,
  plus a first-token vs continuation split scorer certified against the
  canonical per-item totals, plus the mirrored Gemini-96 for all six configs.

## Results on the untouched Spark 96

| Config | Bytes | Mean logprob | Gap closed | First-token acc |
|---|---|---|---|---|
| base | 0 | -11.1498 | 0.000 | 0.031 |
| full delta (reference) | 987,922,432 | -8.5425 | 1.000 | 0.167 |
| uniform rank-32 (factored) | 19,434,496 | -11.0956 | 0.021 | 0.010 |
| mlp_behemoth_lite (factored) | 19,358,176 | -10.5451 | 0.232 | 0.010 |
| LoRA in-style (seed 20261028) | 18,696,192 | -7.5126 | 1.395 | 0.167 |
| LoRA out-of-style (this control) | 18,696,192 | -9.5325 | 0.620 | 0.042 |

Per bucket (mean logprob), out-of-style adapter: knowledge -6.269 (better
than the full fine-tune's -7.850), instruction -15.459 (near base -16.281; the
Gemini instruction set used polite scenario framing, the eval uses terse
commands), math -6.870 (the Gemini math set skewed harder than the eval's
grade-school word problems). In-style adapter per bucket: knowledge -6.380,
instruction -13.524, math -2.641.

First-token vs continuation split (mean logprob per item):

| Config | First token | Continuation |
|---|---|---|
| base | -8.161 | -2.989 |
| full delta | -6.785 | -1.757 |
| lite | -7.777 | -2.768 |
| LoRA in-style | -5.654 | -1.859 |
| LoRA out-of-style | -7.515 | -2.017 |

Read: off-style, the adapter keeps most of its continuation advantage and
loses most of its first-token advantage. That pattern is consistent with two
of the panel's warnings at once: the first-token advantage is the part that
did not survive the style change, and part of any logprob win under a forward-KL objective is a
confidence or calibration effect on continuations (Glimmer's point) rather
than better first picks.

## The mirrored Gemini-96 (the 2x2)

| Config | Mean logprob on Gemini-96 |
|---|---|
| base | -9.8679 |
| full delta | -11.3424 |
| uniform rank-32 | -10.3782 |
| lite | -9.6821 |
| LoRA in-style | -7.2574 |
| LoRA out-of-style | -10.1504 |

The mirror reference inverts: the full fine-tune scores below the base model
on Gemini's probes, so no mirror gap-closed fraction is meaningful (negative
denominator) and results/lora_outofstyle.json records it as null with this
reason. The crossover read is therefore on raw score: the in-style adapter
beats the out-of-style adapter on the Gemini set too. There is no home-turf
advantage for the out-of-style adapter on its own author's set, and no
symmetric style story. One plausible mechanism, visible in the teacher stats
below: the in-style adapter was distilled on short, mostly terminated teacher
answers, and the mirror references are short answers; the out-of-style
adapter was distilled on long, mostly unterminated ones.

## Teacher and training stats, both runs

| | In-style (Spark prompts) | Out-of-style (Gemini prompts) |
|---|---|---|
| Teacher answer tokens, mean | 28.19 | 45.62 |
| Answers ending with im_end | 753 / 1500 | 125 / 1500 |
| Best val KL, seed 20261028 | 0.9147 | 0.0729 |

The consultants' teacher confound, measured: on Gemini phrasing the teacher
produces much longer answers that usually run to the 48-token cap, and those
targets are far easier to fit per token (best val KL 0.073 vs 0.915). The
control therefore varies the teacher-target distribution along with prompt
style. That is part of what a real author shift does, and it is reported
here rather than designed away; Nemotron's base-teacher variant was the
alternative and was declined for the reason recorded in the frozen design.

## Validation

- Independent recomputation: every aggregate in results/lora_outofstyle.json
  was recomputed from per-item rows by a separate script; worst
  stored-vs-recomputed difference 0.0 (12 rows checked).
- Zero adapter in the new workdir vs stored base per-item logprobs: max abs
  diff 0.0. Dense W+B@A reference vs hooked path for the new adapter:
  9.7e-06.
- Split scorer certified: its per-item totals match the canonical eval at
  3.6e-15 max abs diff for all six configs on the Spark 96, before any split
  numbers were trusted.
- Forward port re-validated on the new prompts: torch vs stored NumPy base
  max abs logprob diff 8.6e-05 (12 items); KV-cache vs full-forward greedy
  0/6 sequence mismatches; batched vs single-stream teacher decoder 0/20
  mismatches.
- Muse Spark judging (Meta API, three passes, file-cited): the numeric
  claims (table values, verdict application, mirror read, split values,
  verification values) were recomputed by Spark itself and SUPPORTED.
  Procedural claims were SUPPORTED once the judge was given the design and
  consult extracts. One claim (O7, hygiene and freeze) remains UNVERIFIABLE
  on a single component: that the design was frozen before training cannot
  be proven from file contents alone, as the judge itself put it. Its
  substantive parts (1,350 / 150 split, teacher supervision, eval sets never
  used for training, stopping, or selection) are documented in the frozen
  design. Nothing was CONTRADICTED. The headline sentence above was approved
  verbatim. Record: results/lora_outofstyle_judging.md.

## Compute

Flash (CPU, one heavy stage at a time; queued behind the 7B yardstick job
until it finished): forward validation about 3 min; teacher generation
1,258 s; training 12,228 s (full 1,014 steps, peak RSS 5,781 MB); canonical
evals 3 x about 283 s; split scorer 12 passes at about 283 s each.
Hosted API: Gemini 251,450 tokens for the control prompts (including the
first attempt lost to a VM tmp cleanup and retries), 17,695 for the
mirror-96, 1,150 for its design consult; Muse Spark 3,018 tokens for its
design consult and 18,570 across the three judging passes. Nemotron and
Glimmer consults ran on Flash-local OmniRoute (1,411 and 1,927 tokens). All
hosted calls are logged in results/api_usage_log.jsonl.

## Caveats, stated plainly

- One seed. The in-style seed spread was tight (gap closed std 0.033), but a
  single off-style seed cannot separate a small true effect from seed luck,
  and 0.620 sits close to the frozen 0.60 line.
- The control varies more than surface style: prompt difficulty shifted too
  (Gemini math runs harder, its knowledge items ask for explanations more
  often), and the teacher's answer distribution shifted with it (stats
  above). "Consistent with" remains the right wording for any causal story.
- The mirror eval's reference inversion (full below base) limits what the
  2x2 can show: it rules out a symmetric home-turf story on raw score, but
  it cannot price the style effect as a fraction.
- Off-style first-token accuracy (0.042) is near base level (0.031): whatever
  the adapter transfers off-style, it is not the first-token gate behavior
  that the skill experiments showed matters most.

Files: results/lora_outofstyle.json (machine record),
results/lora_outofstyle_design.md (frozen design),
results/lora_outofstyle_consults.md (Phase 1 consults, verbatim),
results/lora_outofstyle_judging.md and .json (validation). Code:
examples/lora_outofstyle_gen.py, examples/lora_outofstyle_mirror_gen.py,
examples/lora_outofstyle_prepval.py, examples/lora_outofstyle_split.py,
examples/lora_outofstyle_assemble.py, examples/lora_outofstyle_judge.py.
Flash workdir: ~/fc-v04-sweep/lora_outofstyle/ (prompts, teacher dataset,
adapters, train log, eval and split JSONs).
