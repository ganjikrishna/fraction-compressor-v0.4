# Gemini validation, scale test (fourth model pair)

Date: 2026-10-28. Model: gemini-3.5-flash-lite via the Gemini API connector. Tokens: 4802 total (2182 prompt, 2620 completion).

Task given to Gemini: independently recompute every gap_closed in results/fourth_pair_stage2.json and results/fourth_pair_heldout96.json from the raw mean target logprobs (full precision, pulled from the JSON files), verify the byte-fairness figures, rule on six headline claims, and rule on whether the README summary sentence is fair.

Outcome: every recomputation MATCH (all 14 gap_closed values, the 422,912-byte budget difference, and the ~79x full-delta ratio). Claims 1 to 6 all CONFIRMED. The summary sentence was ruled FAIR with no wording change. Gemini claimed no discrepancy, so there was nothing to investigate; this matches the independent script recomputation done the same day (61 of 61 gap_closed values across both files, zero mismatches) and the Muse Spark judging pass (results/spark_judging_scale.md, 5 of 5 claims SUPPORTED).

## Prompt sent (verbatim)

You are independently verifying the arithmetic of a benchmark result file set for a model-compression project. Recompute everything yourself from the raw numbers below; do not trust the stated derived values. gap_closed is defined as (factored - base) / (full - base) on mean target logprob (higher logprob is better). Percentages are gap_closed x 100.

MODEL PAIR 4 (SCALE TEST): Qwen2.5-1.5B base vs Qwen2.5-1.5B Instruct (1.54B parameters, Apache 2.0). A factored 1-bit format compresses the weight delta (Instruct minus base). Recipes assign a per-layer rank; stored size is in bytes. The human baseline recipe is uniform rank 32 on every layer type, priced at 39,046,144 bytes on the real shapes; that price is the byte budget. A recipe at or under the budget is byte-fair; above it is byte-unfair.

STAGE 2 (24 pre-existing probe questions; source file results/fourth_pair_stage2.json):
- base mean target logprob = -13.755791928387005
- full delta mean target logprob = -8.34454360266215
- Spark recipe "Down Dominator" factored mean target logprob = -6.770329668759838, stored size 38,623,232 bytes. Stated: gap_closed 1.290915115911159, byte-fair.
- human uniform_rank32 factored mean target logprob = -7.612950983984054, stored size 39,046,144 bytes. Stated: gap_closed 1.1351984929614363.
- the other four Spark recipes: K-V Zero Reallocator factored = -7.554154307813417 (stated gap_closed 1.1460641329453045, 38,788,096 bytes); Tied Head Guardian factored = -7.7636348573291984 (stated 1.1073520767049876, 38,764,800 bytes); Attention Citadel factored = -7.8781829602926905 (stated 1.08618355955915, 38,564,096 bytes); MLP Expansion Surge factored = -8.006503283710133 (stated 1.0624699327408402, 38,960,128 bytes).
- forward validation: the full-delta config beats base overall by 5.411248325724856 nats, verdict PASS by internal consistency (no external battery exists for this pair).
- the full delta stored at fp16 would be 3,087,138,816 bytes.

HELD-OUT CONFIRMATION (96 fresh questions the search never saw; source file results/fourth_pair_heldout96.json):
- base mean target logprob = -12.584130268980408
- full delta mean target logprob = -7.809744927574116
- byte-fair "Down Dominator" (the Stage 2 winner, already inside the budget, so it is its own byte-fair contender): factored mean target logprob = -6.343687772752477, stored size 38,623,232 bytes. Stated: combined-96 gap_closed 1.3070672034171866; on the first 24 questions alone gap_closed 1.1242514732201125 (that subset's own base = -10.06832344342999, full = -4.667459689568725, factored = -3.9963944114903547); on the 72 newer questions alone gap_closed 1.3791549665115759 (that subset's base = -13.422732544163878, full = -8.85717334024258, factored = -7.126118893173183).
- human uniform_rank32: factored mean target logprob = -6.478079873557243, stored size 39,046,144 bytes. Stated: combined-96 gap_closed 1.2789186374354595; first-24 gap_closed 1.152286379770239 (factored = -3.8449817008608904); 72-new gap_closed 1.3288521753254294 (factored = -7.355779264456026).
- first-token accuracy on the 96: base 0.010416666666666666, full delta 0.3333333333333333, Down Dominator 0.2604166666666667, uniform 0.3229166666666667.

CLAIMS TO CHECK:
1. On the combined 96, the byte-fair Down Dominator scores -6.344 (rounded) with gap_closed 1.307, and beats uniform_rank32 at -6.478 (rounded) with gap_closed 1.279: a raw margin of about 0.134 nats. Both factored configs outscore the full delta (-7.810 rounded), so gap_closed exceeds 1.0 and is not a recovery fraction for this pair.
2. The win is not consistent across subsets: uniform wins the first-24 subset (gap_closed 1.152 vs 1.124) and Down Dominator wins the 72-new subset (1.379 vs 1.329).
3. Down Dominator is byte-fair: 38,623,232 bytes is 422,912 bytes under the 39,046,144-byte budget (about 1.1% under). All five Spark recipes from this round price under the budget on the real shapes.
4. On Stage 2 (24 items), Down Dominator's gap_closed is 1.291 and uniform's is 1.135; every factored config outscores the full delta (-8.345 rounded) there too.
5. The full delta fp16 size is 3,087,138,816 bytes, which is about 79x the uniform patch's 39,046,144 bytes.
6. First-token accuracy: uniform (0.323) exceeds Down Dominator (0.260) on the 96 and nearly matches the full delta (0.333), so the recipe's logprob edge is not an accuracy edge.

SUMMARY SENTENCE TO RULE ON (for the project README):
"At 1.5B scale the byte-fair Spark recipe still edges the human uniform recipe on the 96 fresh questions (-6.344 against -6.478, about 0.13 score points), but the win does not hold on both halves of the set, and on this pair every compressed version outscores the full patch itself, so the gap-closed percentage is not a share of the fine-tune recovered here; the raw score margin is the honest measure."
Context for the cross-pair part: on pair 1 (Qwen2.5-0.5B) the byte-fair variant closed 23.2% of the gap on the same 96 questions against uniform's 2.1%, a much wider win; on pair 3 (Llama 3.2 1B) the byte-fair variant closed 15.9% against uniform's -7.6%. This pair's pattern (factored configs outscoring the full delta itself) matches pair 2 (SmolLM2-360M), where the same not-a-recovery-fraction wording was required.

Reply format: for each recomputation, state MATCH or MISMATCH with your recomputed value; for each claim, CONFIRMED or DISPUTED with a one-line reason; finally rule the summary sentence FAIR or UNFAIR, and if unfair give the exact replacement sentence.


## Gemini reply (verbatim)

**Recomputations:**

*   **Stage 2 gap_closed (Down Dominator):** 
    $\frac{-6.770329668759838 - (-13.755791928387005)}{-8.34454360266215 - (-13.755791928387005)} = \frac{6.985462259627217}{5.411248325724856} = 1.2909151159111593$ -> **MATCH** (1.2909)
*   **Stage 2 gap_closed (human uniform_rank32):** 
    $\frac{-7.612950983984054 - (-13.755791928387005)}{-8.34454360266215 - (-13.755791928387005)} = \frac{6.142840944402951}{5.411248325724856} = 1.135198492961436$ -> **MATCH** (1.1352)
*   **Stage 2 gap_closed (K-V Zero Reallocator):** 
    $\frac{-7.554154307813417 - (-13.755791928387005)}{-8.34454360266215 - (-13.755791928387005)} = \frac{6.201637620573588}{5.411248325724856} = 1.1460641329453045$ -> **MATCH** (1.1461)
*   **Stage 2 gap_closed (Tied Head Guardian):** 
    $\frac{-7.7636348573291984 - (-13.755791928387005)}{-8.34454360266215 - (-13.755791928387005)} = \frac{5.9921570710578066}{5.411248325724856} = 1.1073520767049876$ -> **MATCH** (1.1074)
*   **Stage 2 gap_closed (Attention Citadel):** 
    $\frac{-7.8781829602926905 - (-13.755791928387005)}{-8.34454360266215 - (-13.755791928387005)} = \frac{5.8776089680943145}{5.411248325724856} = 1.08618355955915$ -> **MATCH** (1.0862)
*   **Stage 2 gap_closed (MLP Expansion Surge):** 
    $\frac{-8.006503283710133 - (-13.755791928387005)}{-8.34454360266215 - (-13.755791928387005)} = \frac{5.749288644676872}{5.411248325724856} = 1.0624699327408402$ -> **MATCH** (1.0625)
*   **Held-out combined-96 gap_closed (Down Dominator):** *(Note: combined base = -12.584130268980408, full = -7.809744927574116, factored = -6.343687772752477)*
    $\frac{-6.343687772752477 - (-12.584130268980408)}{-7.809744927574116 - (-12.584130268980408)} = \frac{6.240442496227931}{4.774385341406292} = 1.3070672034171866$ -> **MATCH** (1.3071)
*   **Held-out first-24 gap_closed (Down Dominator):** 
    $\frac{-3.9963944114903547 - (-10.06832344342999)}{-4.667459689568725 - (-10.06832344342999)} = \frac{6.0719290319396353}{5.400863755861265} = 1.1242514732201125$ -> **MATCH** (1.1243)
*   **Held-out 72-new gap_closed (Down Dominator):** 
    $\frac{-7.126118893173183 - (-13.422732544163878)}{-8.85717334024258 - (-13.422732544163878)} = \frac{6.296613650990695}{4.565559406078702} = 1.3791549665115759$ -> **MATCH** (1.3792)
*   **Held-out combined-96 gap_closed (uniform_rank32):** 
    $\frac{-6.478079873557243 - (-12.584130268980408)}{-7.809744927574116 - (-12.584130268980408)} = \frac{6.106050395423165}{4.774385341406292} = 1.2789186374354595$ -> **MATCH** (1.2789)
*   **Held-out first-24 gap_closed (uniform_rank32):** 
    $\frac{-3.8449817008608904 - (-10.06832344342999)}{-4.667459689568725 - (-10.06832344342999)} = \frac{6.2233417425690996}{5.400863755861265} = 1.152286379770239$ -> **MATCH** (1.1523)
*   **Held-out 72-new gap_closed (uniform_rank32):** 
    $\frac{-7.355779264456026 - (-13.422732544163878)}{-8.85717334024258 - (-13.422732544163878)} = \frac{6.066953279707852}{4.565559406078702} = 1.3288521753254294$ -> **MATCH** (1.3289)
*   **Byte budget difference:** 
    $39,046,144 - 38,623,232 = 422,912$ bytes; $422,912 / 39,046,144 = 0.01083107$ (~1.1% under budget). -> **MATCH**
*   **Full delta fp16 size ratio:** 
    $3,087,138,816 / 39,046,144 = 79.0640$ (~79x). -> **MATCH**

---

**Claims to Check:**

1. **CONFIRMED** — Logprob values, rounded metrics, gap percentages, and raw score margins match the underlying computed data correctly.
2. **CONFIRMED** — Uniform wins first-24 (1.152 vs 1.124) while Down Dominator wins the 72-new subset (1.379 vs 1.329), demonstrating inconsistency across splits.
3. **CONFIRMED** — Down Dominator sits 422,912 bytes (~1.1%) below the budget limit, and all five Spark recipes price under the threshold.
4. **CONFIRMED** — Stage 2 metrics check out identically (Down Dominator at 1.291, uniform at 1.135, and all compressed versions beating the full delta logprob).
5. **CONFIRMED** — Full delta fp16 size is indeed 3,087,138,816 bytes, dividing out to roughly 79x the size of the uniform patch.
6. **CONFIRMED** — First-token accuracies (uniform at 0.323 vs Down Dominator at 0.260) verify that the raw logprob advantage does not translate into an execution/generation accuracy edge.

---

**Summary Sentence Ruling:**

**FAIR**
