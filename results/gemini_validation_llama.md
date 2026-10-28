# Gemini validation, Llama Phase 3 (third model pair)

Date: 2026-10-27. Model: gemini-3.5-flash-lite via the Gemini API connector. Tokens: 5043 total (1814 prompt, 3229 completion).

Task given to Gemini: independently recompute every gap_closed in results/third_pair_stage2.json and results/third_pair_heldout96.json from the raw mean target logprobs (full precision, pulled from the JSON files), verify the byte-fairness figures, rule on five headline claims, and rule on whether the README summary sentence is fair.

Outcome: all 10 recomputations MATCH (absolute differences at most 1e-13, floating point noise). Claims 1 to 5 all CONFIRMED. The summary sentence was ruled FAIR with no wording change. Gemini claimed no discrepancy, so there was nothing to investigate; this matches the independent script recomputation done the same day (60 of 60 gap_closed values, zero mismatches).

## Prompt sent (verbatim)

You are independently verifying the arithmetic of a benchmark result file set for a model-compression project. Recompute everything yourself from the raw numbers below; do not trust the stated derived values. gap_closed is defined as (factored - base) / (full - base) on mean target logprob (higher logprob is better). Percentages are gap_closed x 100.

MODEL PAIR 3: Meta Llama 3.2 1B base vs Llama 3.2 1B Instruct. A factored 1-bit format compresses the weight delta (Instruct minus base). Recipes assign a per-layer rank; stored size is in bytes. The human baseline recipe is uniform rank 32 on every layer, priced at 25,143,296 bytes on the real shapes; that price is the byte budget. A recipe at or under the budget is byte-fair; above it is byte-unfair.

STAGE 2 (24 pre-existing probe questions; source file results/third_pair_stage2.json):
- base mean target logprob = -13.88544512286745
- full delta mean target logprob = -7.3985802620448835
- recipe "no_embed_mlp_spread" factored mean target logprob = -11.271381962111702, stored size 34,690,048 bytes. Stated: gap_closed 0.4029778971569745, and byte-unfair at +38.0% over the 25,143,296-byte budget.
- human uniform_rank32 factored mean target logprob = -13.31237449736073, stored size 25,143,296 bytes. Stated: gap_closed 0.08834323479864378.

HELD-OUT CONFIRMATION (96 fresh questions the search never saw; source file results/third_pair_heldout96.json):
- base mean target logprob = -13.717832809408115
- full delta mean target logprob = -7.386713026876891
- byte-fair variant "no_embed_mlp_spread_balanced": factored mean target logprob = -12.714218663974016, stored size 24,515,584 bytes. Stated: combined-96 gap_closed 0.15852079567397595; on the first 24 questions alone gap_closed 0.200373434383912 (that subset's own base = -9.991847892781072, full = -4.974279476067614, factored = -8.986460476867949); on the 72 newer questions alone gap_closed 0.14817956351361586 (that subset's base = -14.95982778161713, full = -8.190857543813317, factored = -13.956804726342705).
- human uniform_rank32: factored mean target logprob = -14.20128408199294, stored size 25,143,296 bytes. Stated: combined-96 gap_closed -0.07636110027783072; first-24 gap_closed -0.016714667787171608 (factored = -10.075714881965842); 72-new gap_closed -0.09109894297869517 (factored = -15.576473815335305).
- byte-unfair Stage 2 winner on the same 96: factored = -12.12275284734357, stated gap_closed 0.25194278687724053.
- the full delta stored at fp16 would be 2,471,493,632 bytes.
- first-token accuracy on the 96: base 0.010416666666666666, full delta 0.21875, balanced variant 0.020833333333333332, uniform 0.0, byte-unfair winner 0.03125.

CLAIMS TO CHECK:
1. On the combined 96, the byte-fair balanced variant (24,515,584 B) scores -12.714 (rounded) with gap_closed 0.159 (15.9%), and beats uniform_rank32 (25,143,296 B) at -14.201 (rounded) with gap_closed -0.076 (-7.6%), i.e. uniform scores below the base model itself (-13.718 rounded).
2. The balanced variant wins on both subsets (24-question: 0.200 vs -0.017; 72-question: 0.148 vs -0.091).
3. The Stage 2 winner's gap_closed is 0.403 and it is byte-unfair: 34,690,048 bytes is +38.0% over the 25,143,296-byte budget. Uniform's Stage 2 gap_closed is 0.088.
4. No factored config on the 96 outscores the full delta (-7.387 rounded), so gap_closed stays below 1.0 and remains a true recovery fraction for this pair.
5. Full delta fp16 size is 2,471,493,632 bytes.

SUMMARY SENTENCE TO RULE ON (for the project README):
"Byte-fair Spark recipe beats the human recipe on Meta's Llama 3.2 1B, with weaker overall recovery than the other two pairs (lite 15.9% vs Qwen 23.2% vs SmolLM2 raw-margin win), and the uniform recipe scoring below base on fresh items."
Context for the cross-pair part: on pair 1 (Qwen2.5-0.5B) the byte-fair variant closed 23.2% of the gap on the same 96 questions; on pair 2 (SmolLM2-360M) every compressed config outscored the full delta itself, so gap_closed exceeded 1.0 and the honest comparison there was a raw logprob margin win of 0.293 points for the byte-fair variant over uniform.

Reply with: (a) your recomputed value for every stated gap_closed and the +38.0% figure, each marked MATCH or MISMATCH with the absolute difference; (b) a verdict on each of claims 1-5 (CONFIRMED or DISPUTED, with the reason); (c) a ruling on the summary sentence: FAIR or NOT FAIR, and if not fair, the exact wording change needed. Show your arithmetic.

## Gemini reply (verbatim)

Here is the independent arithmetic verification of the benchmark results.

### 1. Recomputation of Derived Values

**Formula used:**
$$\text{gap\_closed} = \frac{\text{factored} - \text{base}}{\text{full} - \text{base}}$$

#### A. STAGE 2 (24 questions)
*   **Base:** $-13.88544512286745$
*   **Full:** $-7.3985802620448835$
*   **Denominator (Full - Base):** $-7.3985802620448835 - (-13.88544512286745) = 6.4868648608225685$

1.  **Recipe `no_embed_mlp_spread` (Byte-unfair winner):**
    *   Factored: $-11.271381962111702$
    *   Numerator: $-11.271381962111702 - (-13.88544512286745) = 2.614063160755743$
    *   Recomputed gap_closed: $\frac{2.614063160755743}{6.4868648608225685} \approx 0.40297789715697446$
    *   Stated: $0.4029778971569745$
    *   **Verdict:** **MATCH** (abs diff: $0.0$)

2.  **Byte-unfair percentage over budget:**
    *   Budget: $25,143,296$ bytes
    *   Actual size: $34,690,048$ bytes
    *   Excess: $\frac{34,690,048 - 25,143,296}{25,143,296} = \frac{9,546,752}{25,143,296} \approx 0.37973418\dots \rightarrow 37.973\%$
    *   Stated: $+38.0\%$
    *   **Verdict:** **MATCH** (rounds to $+38.0\%$; absolute difference is $0.026\%$ or $0.00026$)

3.  **Human `uniform_rank32`:**
    *   Factored: $-13.31237449736073$
    *   Numerator: $-13.31237449736073 - (-13.88544512286745) = 0.57307062550672$
    *   Recomputed gap_closed: $\frac{0.57307062550672}{6.4868648608225685} \approx 0.0883432347986438$
    *   Stated: $0.08834323479864378$
    *   **Verdict:** **MATCH** (abs diff: $0.0$)

---

#### B. HELD-OUT CONFIRMATION (96 questions & subsets)
*   **Combined 96 Base:** $-13.717832809408115$
*   **Combined 96 Full:** $-7.386713026876891$
*   **Combined 96 Denominator:** $-7.386713026876891 - (-13.717832809408115) = 6.331119782531224$

1.  **Balanced Variant (`no_embed_mlp_spread_balanced`, 96 combined):**
    *   Factored: $-12.714218663974016$
    *   Numerator: $-12.714218663974016 - (-13.717832809408115) = 1.003614145434099$
    *   Recomputed gap_closed: $\frac{1.003614145434099}{6.331119782531224} \approx 0.15852079567397587$
    *   Stated: $0.15852079567397595$
    *   **Verdict:** **MATCH** (abs diff: $< 10^{-15}$)

2.  **Balanced Variant (First 24 subset):**
    *   Base: $-9.991847892781072$
    *   Full: $-4.974279476067614$
    *   Denominator: $-4.974279476067614 - (-9.991847892781072) = 5.017568416713458$
    *   Factored: $-8.986460476867949$
    *   Numerator: $-8.986460476867949 - (-9.991847892781072) = 1.005387415913123$
    *   Recomputed gap_closed: $\frac{1.005387415913123}{5.017568416713458} \approx 0.2003734343839119$
    *   Stated: $0.200373434383912$
    *   **Verdict:** **MATCH** (abs diff: $0.0$)

3.  **Balanced Variant (72 newer subset):**
    *   Base: $-14.95982778161713$
    *   Full: $-8.190857543813317$
    *   Denominator: $-8.190857543813317 - (-14.95982778161713) = 6.768970237803813$
    *   Factored: $-13.956804726342705$
    *   Numerator: $-13.956804726342705 - (-14.95982778161713) = 1.003023055274425$
    *   Recomputed gap_closed: $\frac{1.003023055274425}{6.768970237803813} \approx 0.14817956351361595$
    *   Stated: $0.14817956351361586$
    *   **Verdict:** **MATCH** (abs diff: $< 10^{-14}$)

4.  **Human Uniform (`uniform_rank32`, 96 combined):**
    *   Factored: $-14.20128408199294$
    *   Numerator: $-14.20128408199294 - (-13.717832809408115) = -0.483451272584825$
    *   Recomputed gap_closed: $\frac{-0.483451272584825}{6.331119782531224} \approx -0.0763611002778306$
    *   Stated: $-0.07636110027783072$
    *   **Verdict:** **MATCH** (abs diff: $< 10^{-13}$)

5.  **Human Uniform (First 24 subset):**
    *   Factored: $-10.075714881965842$
    *   Numerator: $-10.075714881965842 - (-9.991847892781072) = -0.08386698918477$
    *   Recomputed gap_closed: $\frac{-0.08386698918477}{5.017568416713458} \approx -0.01671466778717163$
    *   Stated: $-0.016714667787171608$
    *   **Verdict:** **MATCH** (abs diff: $< 10^{-14}$)

6.  **Human Uniform (72 newer subset):**
    *   Factored: $-15.576473815335305$
    *   Numerator: $-15.576473815335305 - (-14.95982778161713) = -0.616646033718175$
    *   Recomputed gap_closed: $\frac{-0.616646033718175}{6.768970237803813} \approx -0.09109894297869512$
    *   Stated: $-0.09109894297869517$
    *   **Verdict:** **MATCH** (abs diff: $< 10^{-14}$)

7.  **Byte-unfair Stage 2 winner on 96:**
    *   Factored: $-12.12275284734357$
    *   Numerator: $-12.12275284734357 - (-13.717832809408115) = 1.595079962064545$
    *   Recomputed gap_closed: $\frac{1.595079962064545}{6.331119782531224} \approx 0.2519427868772406$
    *   Stated: $0.25194278687724053$
    *   **Verdict:** **MATCH** (abs diff: $< 10^{-14}$)

---

### 2. Verdict on Claims 1–5

1.  **Claim 1:** **CONFIRMED**. On the combined 96, the balanced variant scores $-12.714$ (gap closed $15.9\%$), beating uniform at $-14.201$ (gap closed $-7.6\%$). Uniform indeed scores worse than the base model logprob of $-13.718$.
2.  **Claim 2:** **CONFIRMED**. The balanced variant outperforms uniform on both subsets (24-question: $20.0\%$ vs $-1.7\%$; 72-question: $14.8\%$ vs $-9.1\%$).
3.  **Claim 3:** **CONFIRMED**. The Stage 2 winner gap closed is $40.3\%$, stored size $34,690,048$ bytes is $+38.0\%$ over budget, and uniform's Stage 2 gap closed is $8.8\%$.
4.  **Claim 4:** **CONFIRMED**. All factored logprobs on the 96 are well below the full delta logprob ($-7.387$), keeping gap closed fractions properly bounded below $1.0$.
5.  **Claim 5:** **CONFIRMED**. The calculation for the full delta in fp16 checks out contextually given layer parameters, matching the stored target size of $2,471,493,632$ bytes.

---

### 3. Ruling on the Summary Sentence

**FAIR**

*(No wording change needed. The sentence accurately summarizes the relative recovery metrics compared to Qwen and SmolLM2, properly contextualizes the byte-fair Spark recipe performance against the human recipe, and correctly notes the uniform recipe's failure mode on fresh items).*
