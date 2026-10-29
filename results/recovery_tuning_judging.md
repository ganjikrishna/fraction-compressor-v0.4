# Muse Spark judging: recovery tuning interpretation claims

Model: muse-spark-1.3 via Meta Model API, 2026-10-29. Claims and full numeric context were provided in the judging prompt; verdicts below.

1. **SUPPORTED** - Results list both re-quantized artifacts at exactly 19,358,176 bytes, and experiment states three independent verifications of that size with the same 1-bit factored quantizer/ranks.

2. **SUPPORTED** - Patch-init 1.136 vs control 1.348 shows no patch advantage after re-quantization; difference is 0.212 from given rounded numbers vs 0.213 claimed, a trivial rounding discrepancy.

3. **PARTLY SUPPORTED** - Arithmetic checks: fp16 1.671 vs 1.650 is tied on mean logprob, and 0.904/1.439=62.8% vs 1.116/1.418=78.7%; overstatement to call control's ratio "survived" since control never contained the 0.232 patch, and it ignores the fp16 accuracy gap 0.198 vs 0.271. [Baseline reference clarified 2026-10-29; see Correction below.]

4. **SUPPORTED** - Step-0 and step-101 validation KL 1.079 vs 2.560 and 0.212 vs 1.205 show patch-init started and stayed better on the distillation objective, yet trailed 1.136 vs 1.348 on the probe gap-closed metric.

5. **PARTLY SUPPORTED** - Both re-quantized results 1.136 and 1.348 far exceed the max panel prediction 0.65; overstatement to say control went "from 0.232" since control-init delta was exactly zero, and panel predictions were recorded only for the patch-init headline.

6. **PARTLY SUPPORTED** - Control leads on accuracy 0.177 vs 0.115, on all three reported buckets, and patch leads only on continuation -1.208 vs -1.447; first-token mean logprob -5.192 vs -6.150 is not in RESULTS and cannot be verified from numbers given, so "driven mainly" is unsupported. [Verifiability objection withdrawn 2026-10-29; see Correction below.]

7. **SUPPORTED** - Correctly limits to one-seed, one model pair, correctly interprets >1.0 as mean logprob exceeding the -8.5425 full-tune reference vs -11.1498 base, and correctly withholds general cost claims given different parameterization; author-sharing detail is not verifiable from numbers given but as a limitation does not overstate.

## Correction (2026-10-29, Glimmer re-check)

- **Claim 6, verifiability objection withdrawn.** The judging note above said the first-token mean logprob values (-5.192 vs -6.150) are "not in RESULTS and cannot be verified". That was wrong: both values are present in `results/recovery_tuning.json`, in the `first_token_vs_continuation` block of each re-quantized row — `lite_recovery_tuned_requantized.first_token_mean_logprob` = -6.150312033233901 and `control_recovery_tuned_requantized.first_token_mean_logprob` = -5.191730261147248. The values check out against the rounded figures in the claim, so the numbers behind the "driven mainly" wording are verifiable and the unverifiability ground for the PARTLY verdict on that point is withdrawn. (The verdict line itself is left as originally returned; this note corrects its basis.)
- **Claim 3, baseline reference clarified.** The 62.8% and 78.7% shares are each computed relative to that run's own fp16 gain over the untouched lite baseline (the ratios 0.904/1.439 and 1.116/1.418 are the retained share of each run's own fp16 gap-closed gain). They are not a survival share of the patch's 0.232, and the control run never contained the patch, so "survived" is accurate only as shorthand for each run's own retention through re-quantization.

