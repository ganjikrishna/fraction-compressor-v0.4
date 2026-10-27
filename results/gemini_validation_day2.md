# Gemini cross-validation, Day 2 Alien Sweep results (2026-10-27)

Per Vinay's validation rule: key results are checked by Muse Spark AND Gemini, on
top of the script reruns. Muse Spark generated the recipes (check 1); the scripts
produced checks 2 to 4; this file is the independent recomputation plus Gemini's
independent judgment. Nothing here was pushed to GitHub.

## Independent recomputation (Ember, from the files on disk)

Pricing formula (from the check-1 prompt): bytes(layer, r) = ceil(rows * r / 8) +
4 * rows + 2 * cols * r. Budget 420,864 bytes.

| Recipe | Recomputed bytes | Recorded bytes | Verdict |
|---|---|---|---|
| budget basis (uniform rank 32, all 8 layers) | 420,864 | 420,864 | MATCH |
| embed_guardian | 418,336 | 418,336 | MATCH, under budget |
| attn_output_focus | 411,776 | 411,776 | MATCH, under budget |
| mlp_behemoth | 418,016 | 418,016 | MATCH, under budget |
| sparse_extremes | 402,816 | 402,816 | MATCH, under budget |
| balanced_uneven | 395,136 | 395,136 | MATCH, under budget |

All 5 recipes: totals match the recorded validation exactly and stay under budget.

## Arithmetic sanity checks on results/alien_sweep_checks234.json

- Check 2: per-layer times sum to 18.44 s vs recorded total 18.5 s. Difference is
  0.06 s, consistent with rounding of the per-layer figures (2 decimal places)
  plus unitemized overhead. Not an inconsistency. Matrix count sums to 169 as
  stated. 18.5 s is well under the 600 s budget.
- Check 3: ranking order matches the error values exactly (ascending:
  0.902160, 0.906639, 0.908486, 0.910212, 0.963903). Winner embed_guardian is
  the minimum. The human baseline 0.905687 sits between the winner and the
  second recipe, exactly as the file's note claims.
- Check 4: 20,643,840 / 488,208 = 42.2849, matching the recorded
  compression_ratio 42.2849277357192. Wall time 3.36 s < 600 s budget; peak RSS
  523.4 MB < 6,144 MB budget. Accuracies are exact multiples of 1/120 probes
  (base 81/120, full delta 120/120, factored 84/120), consistent with n_probes.
- No arithmetic inconsistency found anywhere in the two files.

## Gemini's independent judgment (verbatim)

Model: gemini-3.5-flash-lite, one call, 1747 tokens
(prompt 1226, completion 521).
Prompt: the recipe table, Stage 1 ranking, check timings, and four questions
(inconsistencies, ranking meaningfulness, budget fairness at real scale, other
weaknesses).

---

### 1. Inconsistent or Overstated Numbers?
* **Nothing is mathematically inconsistent:** The byte-formula recomputations match, runtimes are well within budgets, and memory footprints are low. 
* **The accuracy claims are properly scoped:** Check 4 explicitly notes the accuracy probe is a feasibility check only (teacher-built targets, no quality evidence), preventing overstatement of the end-to-end performance.

### 2. Meaning of Stage 1 Ranking
* **Methodologically weak:** A relative Frobenius error of ~0.90 to 0.96 means these low ranks retain almost none of the delta's energy (~90% unexplained error). Selecting a "winner" (`embed_guardian` at 0.9021) based on a 0.003 spread over a human baseline (0.9056) in this high-error regime is noise-chasing. 
* **Scale mismatch:** Defining the byte budget on a single generic block and applying the same rank map blindly to 24 blocks of drastically different shapes (e.g., embedding shape 151936x896 vs. 1024x512) invalidates the tight byte-budget equivalence established in Check 1.

### 3. Fairness of the Budget Comparison Across 24 Blocks
* **Unfair / Broken at scale:** The budget of 420,864 bytes was meticulously calculated for *one* block set with specific shapes. Applying the *same rank integer* across 24 real blocks with different dimensions means the true byte footprint will wildly exceed the original budget constraint. The strict budget validation performed in Check 1 is functionally bypassed at real-model scale.

### 4. Other Methodological Weaknesses
* **Zero-allocation layer mapping:** Some recipes assign a rank of `0` to critical layers (e.g., `sparse_extremes` sets `embed` and `k` to 0; `attn_output_focus` sets `k` to 0). Zero-ranking completely zeros out the delta for those layers, yet the pipeline treats this as a valid compression recipe without checking if dropping entire projection matrices breaks structural assumptions in the attention or embedding pathways.
* **Over-reliance on SVD slicing:** Slicing singular values assumes linear independence and squared error additivity that rarely hold up after quantization or downstream task execution, especially at such aggressive compression ratios (42x).
---

## Ember's read of the disagreement

The arithmetic is fully confirmed by two independent routes (script rerun and
this recomputation). Gemini does not dispute any number. Its objections are
methodological, and two of them stand:

1. The Stage 1 winner's margin is tiny (0.9022 vs the human 0.9057) in a regime
   where all recipes leave about 90% of the delta's energy unexplained, so
   calling embed_guardian a "winner" overstates what Stage 1 can show. Stage 1
   is a filter, and the plan's honest-outcome rule already requires the real
   test at Stage 2 on task accuracy.
2. The equal-bytes fairness was proven only on the generic single-block shapes.
   At real-model scale the shapes change (above all the 151936x896 embedding),
   so the recipes are not byte-equal to uniform rank-32 on the real model, and
   Stage 1 did not re-price them there. Any Stage 2 comparison should re-price
   every recipe, including the human baseline, on the real shapes first.

The GO verdict itself (the sweep machinery runs, recipes are valid, timings are
far inside budget) is not challenged by Gemini; its points 1 and 2 qualify what
Stage 1's ranking means, not whether the gates passed.

---

# Addendum: Gemini cross-validation, Stage 2 and held-out (2026-10-27)

Second round of the same validation rule, applied to the real-model results:
results/alien_sweep_stage2.json (24 pre-existing Signet items) and
results/alien_sweep_heldout.json (24 fresh Muse Spark items the sweep never
saw). Independent recomputation by Ember from the files' own numbers, plus one
Gemini call judging the headline conclusion. Nothing here was pushed to GitHub.

## Independent recomputation (Ember, from the files on disk)

gap_closed = (factored - base) / (full - base) on mean target logprob, recomputed
for every config, overall and per bucket, in both files.

Stage 2 (alien_sweep_stage2.json), overall gap_closed:

| Config | Recomputed | Recorded | Verdict |
|---|---|---|---|
| mlp_behemoth | 0.457172 | 0.457172 | MATCH |
| attn_output_focus | 0.189517 | 0.189517 | MATCH |
| uniform_rank32 (human) | 0.133181 | 0.133181 | MATCH |
| ablation_k0_embed_guardian | 0.095530 | 0.095530 | MATCH |
| balanced_uneven | 0.045325 | 0.045325 | MATCH |
| ablation_embed80_sparse_extremes | 0.044345 | 0.044345 | MATCH |
| embed_guardian | 0.026001 | 0.026001 | MATCH |
| sparse_extremes | -0.164942 | -0.164942 | MATCH |

All per-bucket values (knowledge, instruction, math) also recompute exactly for
all 8 configs. Every overall mean logprob equals the mean of its three bucket
means (equal n=8), in every config. The recorded ranking matches the factored
logprobs in exact descending order (mlp_behemoth -10.507 down to sparse_extremes
-12.037), and the ranking's gap values match each config's own gap_closed.

Rank-0 analysis: the k_proj-drop delta (+0.170996 nats) and the embed-restore
delta (+0.514713 nats), and all six per-bucket deltas, recompute exactly from
the parent and ablation configs.

Bytes, Stage 2: the generic-shape totals match the Day-2 verified figures.
Against the full fp16 delta on real shapes (987,922,432 B): mlp_behemoth
21,719,776 B is 2.199% (45.48x smaller); uniform_rank32 19,434,496 B is 1.967%
(50.83x smaller). mlp_behemoth spends 2,285,280 B more than uniform on real
shapes, the 11.8% overage the held-out file records.

Held-out (alien_sweep_heldout.json), overall gap_closed:

| Config | Recomputed | Recorded | Verdict |
|---|---|---|---|
| mlp_behemoth | 0.108311 | 0.108311 | MATCH |
| mlp_behemoth_lite | 0.094723 | 0.094723 | MATCH |
| uniform_rank32 (human) | 0.015642 | 0.015642 | MATCH |

All per-bucket values recompute exactly. The per-item records check out too:
bucket means recomputed from the 24 per-item logprobs match the recorded
factored bucket means for all 3 configs, and first-token accuracy from the
per-item flags matches (mlp_behemoth 1/24 = 0.042, lite 0, uniform 0). The
held-out ranking order matches the factored logprobs exactly.

Byte-fairness arithmetic: mlp_behemoth minus lite is exactly 2,361,600 B (the
shed the variant's reason states). The overage over uniform is exactly
2,285,280 B = 11.759%, recorded as 11.8% (rounding, matches). Lite at
19,358,176 B sits 76,320 B UNDER the uniform budget of 19,434,496 B, and the
price validation computed on Flash matches the generation claim exactly.

Degenerate math gap: the held-out math denominator (full - base) is 0.0797 nats,
exactly as caveated. The math gap_closed values (mlp_behemoth 11.771, lite
11.153, uniform 1.236) recompute exactly and are ratio artifacts of that
near-zero denominator; the raw math logprobs are base -7.056, full -6.976,
mlp_behemoth -6.118, lite -6.167, uniform -6.958.

Shrinkage: the winner's overall gap_closed is 45.7% on the Stage 2 development
items and 10.8% on held-out, exactly the stated caveat. Lite's held-out 9.47%
still beats uniform's 1.56%.

No mismatch found anywhere in the two files.

## Gemini's independent judgment (verbatim)

Model: gemini-3.5-flash-lite, one completed call, 2,759 tokens
(prompt 1,620, completion 1,139). A first attempt timed out inside the helper
at 120 s with no reply; it is logged in the usage log with null token counts.
Prompt: the Stage 2 table, the held-out table, the six known caveats, and three
questions (is the conclusion honestly supported, is "confirmed winner"
defensible, what wording limits should the submission keep).

---

Based on the rigorous data provided from the validation run, here is an independent analysis of the claim: **"Spark recipe mlp_behemoth confirmed winner, and its byte-matched variant beats the human uniform recipe on held-out tasks."**

---

### 1. Is the conclusion honestly supported by the numbers? Where does it overreach?

**Yes, the narrow technical claim is supported, but the broader narrative is heavily overreached.**

*   **Where it holds up (The Facts):**
    *   On the byte-fair comparison using held-out data, `mlp_behemoth_lite` (19,358,176 B) outperforms `uniform_rank32` (19,434,496 B) in overall `gap_closed` (**0.095 vs. 0.016**) and raw mean logprob (**-8.568 vs. -8.852**).
    *   The original `mlp_behemoth` also beats uniform on held-out gap_closed (**0.108 vs. 0.016**) and logprob (**-8.519**).
*   **Where it overreaches (The Caveats):**
    *   **The Math Bucket Illusion:** The held-out math bucket numbers (`11.771` and `11.153` gap_closed) are mathematically misleading. As noted in Caveat 2, the denominator is a near-zero 0.0797 nats. In reality, the factored models actually *overshot* the full delta in raw logprob space (Base: -7.056, Full: -6.976, Behemoth: -6.118), indicating a possible destabilization or non-linear compression artifact rather than "super-recovery."
    *   **The Instruction Bucket Failure:** On held-out instruction items, the winner performs *worse than the base model* (`-0.170` gap_closed), despite performing well (`0.754`) on the development set (Caveat 3).
    *   **Knowledge Regression:** On held-out knowledge items, the human uniform baseline actually beats both the winner (`0.272` vs `0.267`) (Caveat 6).

---

### 2. Is "confirmed winner" defensible language, or should it be weakened?

**"Confirmed winner" is too strong and must be weakened.**

Calling it a "confirmed winner" implies robust, generalizable superiority across tasks and distributions. With a massive performance shrinkage from **45.7% to 10.8%** gap_closed, a sample size of only **24 items**, and failures in specific buckets (instruction regression on held-out, knowledge loss to uniform), the victory is fragile.

**How it should be weakened:**
*   Instead of *"confirmed winner,"* use **"conditionally validated leading recipe"** or **"byte-efficiently superior on aggregate held-out logprob, though domain-dependent."**
*   Furthermore, because first-token accuracy is essentially zero across the board (0.042 for the winner, 0.0 for everyone else), it cannot be called a winner on *task execution*—only on *next-token probability shaping*.

---

### 3. What wording limits should the project keep in its submission?

To maintain scientific integrity, the project's documentation and final submission must enforce strict guardrails.

#### **What MUST always be stated alongside the claim:**
1.  **The Byte-Fair Caveat:** Any citation of `mlp_behemoth`'s raw score must be paired with the acknowledgment that it exceeded the uniform budget by ~2.28 MB (11.8%), and that the true byte-fair comparison relies on `mlp_behemoth_lite`.
2.  **The Shrinkage Warning:** The drop in overall `gap_closed` from 45.7% (development) to 10.8% (held-out) must be explicitly disclosed to show lack of generalization stability.
3.  **Domain-Specific Trade-offs:** It must be stated that the victory is driven primarily by anomalous math logprob shifts, while knowledge is won by the uniform baseline and instruction items remain unrecovered (negative gap closed).
4.  **Metric Limitation:** It must be noted that all evaluations rest exclusively on logprob, as first-token accuracy is 0.0 for factored configs on the held-out set.

#### **What must NEVER be claimed:**
1.  **Never claim task-solving superiority:** Do not say the model "solves math" or "recovers instruction-following" (first-token accuracy is 0.0; math gap_closed is a mathematical artifact of a tiny denominator).
2.  **Never claim universal domain dominance:** Do not claim the Spark recipe beats uniform *across all buckets* (uniform wins held-out knowledge; all factored recipes hurt held-out instruction).
3.  **Never present `mlp_behemoth` as strictly byte-fair** without specifying that its lite variant was required to match the human baseline's budget.

---

## Ember's read of the disagreement

The arithmetic is fully confirmed by recomputation: every gap_closed, ranking,
per-item mean, and byte figure in both result files matches its own inputs.
Gemini disputes no number. The disagreement is over one word: "confirmed."

Gemini is right that "confirmed winner" overreaches. What the two files
actually support is narrower, and still real:

1. On both item sets, mlp_behemoth has the best overall factored logprob of
   every config tested, and on held-out items the byte-matched lite variant
   (76,320 B under the uniform budget) beats the human uniform recipe on
   overall gap_closed (0.095 vs 0.016) and raw logprob (-8.568 vs -8.852).
   That byte-fair held-out win is the honest headline.
2. The effect is much weaker on held-out items (45.7% down to 10.8%), the
   sample is 24 items per set, and the win is aggregate only: uniform takes
   held-out knowledge (0.272 vs 0.267), every factored config is worse than
   base on held-out instruction, and the held-out math ratios are artifacts
   of a 0.0797-nat denominator. One extra observation from Gemini worth
   keeping: on held-out math the factored configs overshoot even the full
   delta in raw logprob (-6.118 vs full -6.976), which reads as a compression
   artifact, not recovery.
3. First-token accuracy is 0.0 for nearly every factored config on both sets,
   so nothing here is a task-solving claim; it is a logprob claim only.

Recommended submission wording, following Gemini's limits: call mlp_behemoth
the sweep's leading recipe, say its byte-matched variant beat the human uniform
recipe on aggregate held-out logprob (0.095 vs 0.016 of the gap closed, at
19,358,176 vs 19,434,496 bytes), and always carry alongside it the shrinkage
(45.7% to 10.8%), the unrecovered instruction bucket, the knowledge loss to
uniform, the degenerate math denominator, and the logprob-only metric. Never
"confirmed winner," never per-bucket dominance, never byte-fairness for
mlp_behemoth itself.
