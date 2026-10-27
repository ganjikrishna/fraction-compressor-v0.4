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
