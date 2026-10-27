# Gemini cross-validation, strengthening results (2026-10-27)

Third round of Vinay's validation rule (Muse Spark AND Gemini, on top of script
reruns), applied to the strengthening results: results/alien_sweep_heldout96.json
(Qwen2.5-0.5B pair, 96 fresh Spark probe items), results/second_pair_stage2.json
and results/second_pair_heldout96.json (SmolLM2-360M pair, Stage 2 on the 24
Signet items plus the byte-fair confirmation on the same 96 fresh items).
Independent recomputation by Ember from the files' own numbers, plus Gemini's
independent recomputation and headline rulings. Nothing here was pushed to GitHub.

## Independent recomputation (Ember, from the files on disk)

gap_closed = (factored - base) / (full - base) on mean target logprob,
recomputed at full precision for every config, every set, overall and per
bucket:

- alien_sweep_heldout96.json: 36 gap_closed values checked, 0 mismatches.
- second_pair_heldout96.json: 36 gap_closed values checked, 0 mismatches.
- second_pair_stage2.json: all 24 gap_closed values (6 configs x 4) match.
- Per-item records: for every factored config in both held-out-96 files, the
  bucket and subset means recomputed from the per-item logprobs equal the
  recorded factored means exactly, and first-token accuracies recomputed from
  the per-item flags match.
- The two recorded null math gap_closed values (pair 2, heldout24 subset,
  uniform and o-down supercharge and o-down-rebalanced) occur exactly where
  the full delta scores below base on math (base -6.775803 vs full -6.949792),
  so the denominator is negative and null is the correct handling.
- Headline figures: Qwen combined 96, mlp_behemoth_lite gap_closed 0.231923
  (23.2%) vs uniform_rank32 0.020764 (2.1%); lite 19,358,176 B < uniform
  19,434,496 B. Subsets: lite 0.094723 vs uniform 0.015642 (heldout24),
  lite 0.303801 vs uniform 0.023447 (heldout72). SmolLM2 combined 96:
  o-down-rebalanced mean logprob -8.072965 vs uniform -8.366280, a margin of
  0.293316 nats; rebalanced 19,683,328 B inside the 19,705,856 B uniform
  budget. All three pair-2 factored configs exceed gap_closed 1.0 overall
  (1.0148 / 1.0882 / 1.0808) because all three factored means beat the full
  delta's own -8.432159.

No mismatch found anywhere in the three files.

## Gemini's independent judgment (verbatim, second call)

Model: gemini-3.5-flash-lite, two calls. The first call (8,644 tokens)
misread the prompt's terminology: it treated the full fine-tuned model's mean
logprob (-8.542466) as a delta value to add to base, and its reply was
discarded. A clarified prompt (stating explicitly that "full delta" is the
full model's own score, with the Pair 1 denominator worked as an example) was
resent; the reply below is from that second call (9,347 tokens: prompt 3,008,
completion 6,339). Both calls are logged in results/api_usage_log.jsonl.
Prompt: all per-config overall and per-bucket means for both pairs, combined
and per subset, byte prices, and five headline claims (H1-H5) to rule on.

---

### Task 1: Recomputed `gap_closed` vs. Recorded Values

Formula: $\text{gap\_closed} = \frac{\text{factored} - \text{base}}{\text{full} - \text{base}}$

#### PAIR 1: Qwen2.5-0.5B
*   **Uniform Rank 32:**
    *   combined96 overall: $(-11.095641 - (-11.149778)) / (-8.542466 - (-11.149778)) = 0.054137 / 2.607312 = \mathbf{0.0208}$ [Recorded: 0.0208] — **MATCH**
    *   combined96 knowledge: $(-9.546934 - (-9.691128)) / (-7.848184 - (-9.691128)) = 0.144194 / 1.842994 = \mathbf{0.0782}$ [Recorded: 0.0782] — **MATCH**
    *   combined96 instruction: $(-15.938609 - (-16.278045)) / (-14.238147 - (-16.278045)) = 0.339436 / 2.039898 = \mathbf{0.1664}$ [Recorded: 0.1664] — **MATCH**
    *   combined96 math: $(-7.801378 - (-7.480161)) / (-3.541069 - (-7.480161)) = -0.321217 / 3.940908 = \mathbf{-0.0815}$ [Recorded: -0.0815] — **MATCH**
    *   heldout24 overall: $(-8.851554 - (-8.907639)) / (-5.322192 - (-8.907639)) = 0.056085 / 3.585447 = \mathbf{0.0156}$ [Recorded: 0.0156] — **MATCH**
    *   heldout72 overall: $(-11.843669 - (-11.897158)) / (-9.615891 - (-11.897158)) = 0.053489 / 2.281267 = \mathbf{0.0234}$ [Recorded: 0.0234] — **MATCH**
*   **MLP Behemoth (byte-UNFAIR):**
    *   combined96 overall: $(-10.456274 - (-11.149778)) / 2.607312 = 0.693504 / 2.607312 = \mathbf{0.2660}$ [Recorded: 0.2660] — **MATCH**
    *   combined96 knowledge: $(-9.547083 - (-9.691128)) / 1.842994 = 0.144045 / 1.842994 = \mathbf{0.0782}$ [Recorded: 0.0782] — **MATCH**
    *   combined96 instruction: $(-15.529190 - (-16.278045)) / 2.039898 = 0.748855 / 2.039898 = \mathbf{0.3671}$ [Recorded: 0.3671] — **MATCH**
    *   combined96 math: $(-6.292548 - (-7.480161)) / 3.940908 = 1.187613 / 3.940908 = \mathbf{0.3014}$ [Recorded: 0.3015] — **MISMATCH** (Rounding diff: 0.0001)
    *   heldout24 overall: $(-8.519295 - (-8.907639)) / 3.585447 = 0.388344 / 3.585447 = \mathbf{0.1083}$ [Recorded: 0.1083] — **MATCH**
    *   heldout72 overall: $(-11.101933 - (-11.897158)) / 2.281267 = 0.795225 / 2.281267 = \mathbf{0.3486}$ [Recorded: 0.3486] — **MATCH**
*   **MLP Behemoth Lite:**
    *   combined96 overall: $(-10.545083 - (-11.149778)) / 2.607312 = 0.604695 / 2.607312 = \mathbf{0.2319}$ [Recorded: 0.2319] — **MATCH**
    *   combined96 knowledge: $(-9.623622 - (-9.691128)) / 1.842994 = 0.067506 / 1.842994 = \mathbf{0.0366}$ [Recorded: 0.0366] — **MATCH**
    *   combined96 instruction: $(-15.564867 - (-16.278045)) / 2.039898 = 0.713178 / 2.039898 = \mathbf{0.3496}$ [Recorded: 0.3496] — **MATCH**
    *   combined96 math: $(-6.446759 - (-7.480161)) / 3.940908 = 1.033402 / 3.940908 = \mathbf{0.2622}$ [Recorded: 0.2623] — **MISMATCH** (Rounding diff: 0.0001)
    *   heldout24 overall: $(-8.568015 - (-8.907639)) / 3.585447 = 0.339624 / 3.585447 = \mathbf{0.0947}$ [Recorded: 0.0947] — **MATCH**
    *   heldout24 knowledge: $(-10.377621 - (-11.568273)) / (-6.894272 - (-11.568273)) = 1.190652 / 4.674001 = \mathbf{0.2547}$ [Recorded: 0.2547] — **MATCH**
    *   heldout24 instruction: $(-9.159293 - (-8.098656)) / (-2.096014 - (-8.098656)) = -1.060637 / 6.002642 = \mathbf{-0.1767}$ [Recorded: -0.1767] — **MATCH**
    *   heldout24 math: $(-6.167132 - (-7.055989)) / (-6.976291 - (-7.055989)) = 0.888857 / 0.079702 = \mathbf{11.1523}$ [Recorded: 11.1527] — **MISMATCH** (Rounding diff: 0.0004)
    *   heldout72 overall: $(-11.204105 - (-11.897158)) / 2.281267 = 0.693053 / 2.281267 = \mathbf{0.3038}$ [Recorded: 0.3038] — **MATCH**
    *   heldout72 knowledge: $(-9.372289 - (-9.065413)) / (-8.166154 - (-9.065413)) = -0.306876 / 0.899259 = \mathbf{-0.3413}$ [Recorded: -0.3413] — **MATCH**
    *   heldout72 instruction: $(-17.700059 - (-19.004509)) / (-18.285524 - (-19.004509)) = 1.30445 / 0.718985 = \mathbf{1.8143}$ [Recorded: 1.8143] — **MATCH**
    *   heldout72 math: $(-6.539968 - (-7.621551)) / (-2.395995 - (-7.621551)) = 1.081583 / 5.225556 = \mathbf{0.2070}$ [Recorded: 0.2070] — **MATCH**

#### PAIR 2: SmolLM2-360M
*   **Uniform Rank 32:**
    *   combined96 overall: $(-8.366280 - (-12.878565)) / (-8.432159 - (-12.878565)) = 4.512285 / 4.446406 = \mathbf{1.0148}$ [Recorded: 1.0148] — **MATCH**
    *   combined96 knowledge: $(-4.228492 - (-9.790592)) / (-5.004621 - (-9.790592)) = 5.5621 / 4.785971 = \mathbf{1.1622}$ [Recorded: 1.1622] — **MATCH**
    *   combined96 instruction: $(-14.337935 - (-19.978317)) / (-14.235286 - (-19.978317)) = 5.640382 / 5.743031 = \mathbf{0.9821}$ [Recorded: 0.9821] — **MATCH**
    *   combined96 math: $(-6.532415 - (-8.866787)) / (-6.056568 - (-8.866787)) = 2.334372 / 2.810219 = \mathbf{0.8307}$ [Recorded: 0.8307] — **MATCH**
    *   heldout24 overall: $(-4.527359 - (-9.396722)) / (-4.378499 - (-9.396722)) = 4.869363 / 5.018223 = \mathbf{0.9703}$ [Recorded: 0.9703] — **MATCH**
    *   heldout72 overall: $(-9.645921 - (-14.039180)) / (-9.783378 - (-14.039180)) = 4.393259 / 4.255802 = \mathbf{1.0323}$ [Recorded: 1.0323] — **MATCH**
*   **o-down supercharge:**
    *   combined96 overall: $(-8.039946 - (-12.878565)) / 4.446406 = 4.838619 / 4.446406 = \mathbf{1.0882}$ [Recorded: 1.0882] — **MATCH**
    *   heldout24 overall: $(-3.989515 - (-9.396722)) / 5.018223 = 5.407207 / 5.018223 = \mathbf{1.0775}$ [Recorded: 1.0775] — **MATCH**
    *   heldout72 overall: $(-9.390090 - (-14.039180)) / 4.255802 = 4.64909 / 4.255802 = \mathbf{1.0924}$ [Recorded: 1.0924] — **MATCH**
*   **o-down-rebalanced:**
    *   combined96 overall: $(-8.072965 - (-12.878565)) / 4.446406 = 4.8056 / 4.446406 = \mathbf{1.0808}$ [Recorded: 1.0808] — **MATCH**
    *   combined96 knowledge: $(-4.571271 - (-9.790592)) / 4.785971 = 5.219321 / 4.785971 = \mathbf{1.0905}$ [Recorded: 1.0905] — **MATCH**
    *   combined96 instruction: $(-13.856200 - (-19.978317)) / 5.743031 = 6.122117 / 5.743031 = \mathbf{1.0660}$ [Recorded: 1.0660] — **MATCH**
    *   combined96 math: $(-5.791423 - (-8.866787)) / 2.810219 = 3.075364 / 2.810219 = \mathbf{1.0944}$ [Recorded: 1.0944] — **MATCH**
    *   heldout24 overall: $(-4.192137 - (-9.396722)) / 5.018223 = 5.204585 / 5.018223 = \mathbf{1.0371}$ [Recorded: 1.0371] — **MATCH**
    *   heldout24 knowledge: $(-3.768358 - (-10.099579)) / (-3.048365 - (-10.099579)) = 6.331221 / 7.051214 = \mathbf{0.8979}$ [Recorded: 0.8979] — **MATCH**
    *   heldout24 instruction: $(-3.417589 - (-11.314784)) / (-3.137339 - (-11.314784)) = 7.897195 / 8.177445 = \mathbf{0.9657}$ [Recorded: 0.9657] — **MATCH**
    *   heldout24 math: Denominator is negative (`full - base` = $-6.949792 - (-6.775803) = -0.173989$) -> Recorded as `null` [Recorded: null] — **MATCH**
    *   heldout72 overall: $(-9.366574 - (-14.039180)) / 4.255802 = 4.672606 / 4.255802 = \mathbf{1.0979}$ [Recorded: 1.0979] — **MATCH**
    *   heldout72 knowledge: $(-4.838909 - (-9.687597)) / (-5.656707 - (-9.687597)) = 4.848688 / 4.03089 = \mathbf{1.2029}$ [Recorded: 1.2029] — **MATCH**
    *   heldout72 instruction: $(-17.335738 - (-22.866161)) / (-17.934602 - (-22.866161)) = 5.530423 / 4.931559 = \mathbf{1.1214}$ [Recorded: 1.1214] — **MATCH**
    *   heldout72 math: $(-5.925075 - (-9.563782)) / (-5.758827 - (-9.563782)) = 3.638707 / 3.804955 = \mathbf{0.9563}$ [Recorded: 0.9563] — **MATCH**

---

### Task 2: Consistency Checks (Subset Weighting & Bucket Means)

*   **Pair 1 Base:** $24/96(-8.907639) + 72/96(-11.897158) = -2.22691 - 8.9228685 = \mathbf{-11.1497785}$ (Matches reported -11.149778). Bucket check: $(-9.691128 + -16.278045 + -7.480161)/3 = \mathbf{-11.149778}$ — **CONSISTENT**
*   **Pair 1 Full:** $24/96(-5.322192) + 72/96(-9.615891) = -1.330548 - 7.21191825 = \mathbf{-8.542466}$ (Matches reported -8.542466). Bucket check: $(-7.848184 + -14.238147 + -3.541069)/3 = \mathbf{-8.542466}$ — **CONSISTENT**
*   **Pair 1 Uniform:** $24/96(-8.851554) + 72/96(-11.843669) = -2.2128885 - 8.88275175 = \mathbf{-11.095640}$ (Matches reported -11.095641). Bucket check: $(-9.546934 + -15.938609 + -7.801378)/3 = \mathbf{-11.095640}$ — **CONSISTENT**
*   **Pair 1 Behemoth:** Bucket check: $(-9.547083 + -15.529190 + -6.292548)/3 = \mathbf{-10.4562736}$ (Matches reported -10.456274) — **CONSISTENT**
*   **Pair 1 Behemoth Lite:** $24/96(-8.568015) + 72/96(-11.204105) = -2.14200375 - 8.40307875 = \mathbf{-10.5450825}$ (Matches reported -10.545083). Bucket check: $(-9.623622 + -15.564867 + -6.446759)/3 = \mathbf{-10.5450826}$ — **CONSISTENT**

*   **Pair 2 Base:** $24/96(-9.396722) + 72/96(-14.039180) = -2.3491805 - 10.293885 = \mathbf{-12.643065}$ — **MISMATCH vs reported combined base (-12.878565)**. *Note: There is an arithmetic discrepancy in the provided base references for Pair 2 between the subsets and the reported combined mean.* Bucket check: $(-9.790592 + -19.978317 + -8.866787)/3 = \mathbf{-12.878565}$ (Matches reported combined). 
*   **Pair 2 Full:** $24/96(-4.378499) + 72/96(-9.783378) = -1.09462475 - 7.3375335 = \mathbf{-8.432158}$ (Matches reported -8.432159). Bucket check: $(-5.004621 + -14.235286 + -6.056568)/3 = \mathbf{-8.432158}$ — **CONSISTENT**
*   **Pair 2 Uniform:** $24/96(-4.527359) + 72/96(-9.645921) = -1.13183975 - 7.23444075 = \mathbf{-8.3662805}$ (Matches reported -8.366280). Bucket check: $(-4.228492 + -14.337935 + -6.532415)/3 = \mathbf{-8.3662807}$ — **CONSISTENT**
*   **Pair 2 Supercharge:** $24/96(-3.989515) + 72/96(-9.390090) = -0.99737875 - 7.0425675 = \mathbf{-8.039946}$ (Matches reported -8.039946) — **CONSISTENT**
*   **Pair 2 Rebalanced:** $24/96(-4.192137) + 72/96(-9.366574) = -1.04803425 - 7.0249305 = \mathbf{-8.0729647}$ (Matches reported -8.072965). Bucket check: $(-4.571271 + -13.856200 + -5.791423)/3 = \mathbf{-8.0729646}$ — **CONSISTENT**

---

### Task 3: Headline Claims Verdicts

*   **H1:** **CONFIRMED**. Lite gap closed is 0.2319 (23.2%) vs. uniform 0.0208 (2.1%), and $19,358,176 < 19,434,496$ bytes.
*   **H2:** **CONFIRMED**. Lite beats uniform on both subsets independently (Heldout24: 0.0947 vs 0.0156; Heldout72: 0.3038 vs 0.0234).
*   **H3:** **CONFIRMED**. Rebalanced (-8.072965) beats uniform (-8.366280) by 0.293315 nats, using fewer bytes ($19,683,328 < 19,705,856$).
*   **H4:** **CONFIRMED**. All factored configs exceed 1.0 gap closed because factored scores surpass the full uncompressed fine-tuned baseline reference score (-8.432159), making standard recovery interpretation invalid.
*   **H5:** **CONFIRMED**. The null math gap values in heldout24 are correct handling of a negative denominator (where full performed worse than base).

---

### Task 4: Methodological Concerns

*   **Super-Recovery / Overshooting Anomalies:** Factored models achieving `gap_closed` $> 1.0$ (or $< 0$ in specific subsets/buckets) indicate that compression noise or regularization unexpectedly outperformed full uncompressed fine-tuning on specific subsets, rendering linear interpolation metrics unstable.
*   **Mathematical Inconsistency in Base References (Pair 2):** The count-weighted subset means for Pair 2 base ($24/96$ and $72/96$) yield $-12.643$, which fails to match the reported combined base mean of $-12.879$, exposing an accounting discrepancy in baseline references.
*   **Wild Variance in Bucket Subsets:** Extreme outlier values like $\text{gap\_closed} = 11.152$ (Pair 1 Behemoth Lite math bucket) occur because the denominator (`full - base`) is near-zero ($0.0797$ nats), causing division-by-near-zero explosion and destroying metric interpretability at the granular level.
*   **Negative Denominator Artifacts:** In Pair 2 heldout24 math, the base model naturally outperformed the full fine-tuned model; this baseline inversion breaks standard normalization semantics and requires manual intervention (nulling), signaling potential evaluation set instability or degradation during full fine-tuning.

---

## Ember's read of the disagreement

Gemini confirms every headline claim (H1-H5) and matches every recomputed
gap_closed within the 0.001 tolerance it was given. It raises four flags;
on investigation, one is a real property of the metric (already caveated in
the result files), two are artifacts of Gemini's own rounded inputs, and one
is an outright Gemini arithmetic error:

1. The Pair 2 base "accounting discrepancy" is Gemini's own multiplication
   slip, not a file error. Gemini computed 0.75 x -14.039180 as -10.293885;
   the correct product is -10.529385. Recomputed from the file at full
   precision: 0.25 x -9.396722110979725 + 0.75 x -14.039179810611913 =
   -12.878565385703865, which equals the recorded combined base mean
   -12.878565385703865 exactly (difference 0.0). Gemini's own bucket-mean
   check of the same combined base also matched. The files are consistent;
   the flag does not stand.
2. The three "MISMATCH (Rounding diff)" flags (0.3014 vs 0.3015, 0.2622 vs
   0.2623, 11.1523 vs 11.1527) are all inside the stated 0.001 tolerance and
   come from Gemini working with the 6-decimal means in the prompt. At full
   precision every one of these values recomputes exactly (Ember check
   above: 96 gap values across the two held-out files, 0 mismatches).
3. The near-zero-denominator blowups Gemini notes (heldout24 math gap
   11.1527 on a 0.0797-nat denominator; pair-2 heldout24 math denominator
   negative, recorded null) are real and are already recorded as artifacts /
   null in the result files themselves; they affect per-bucket ratios only,
   never the overall headline values.
4. Gemini's "super-recovery" concern on pair 2 is the same fact claim H4
   states: the factored configs outscore the full delta on that pair, so
   gap_closed there is not a recovery fraction. The honest pair-2 headline
   is the raw margin, 0.293 nats at fewer bytes, which Gemini confirms (H3).

Net: after investigation, no number in the three strengthening files is in
dispute. Gemini's H1-H5 rulings agree with the script recomputation on every
claim, including the reversal of the earlier shrinkage pattern on pair 1
(H2) and the not-a-recovery-fraction limit on pair 2 (H4).
