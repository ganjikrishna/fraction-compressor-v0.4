# Muse Spark judging: scale test (fourth model pair, Qwen2.5-1.5B)

Date: 2026-10-28 (corrected pass; see the correction note in spark_judging_scale.json: the first pass carried two hand-copied Stage 2 values off by ~4e-4, this pass reads every value from the files; no verdict changed). Judge: Muse Spark 1.3 via the Meta Model API (5192 tokens: 959 prompt, 4233 completion). Spark judged the headline claims for the Qwen2.5-1.5B scale test against the numbers copied at full precision from results/fourth_pair_stage2.json and results/fourth_pair_heldout96.json, and had to cite its source file for every verdict.

## Verdicts

### Claim A: SUPPORTED

Stage 2 on the 24 pre-existing Signet items: the Spark recipe Down Dominator wins at factored mean target logprob -6.770329668759838 (gap_closed 1.290915115911159) at 38,623,232 bytes, inside the uniform budget of 39,046,144 bytes; the human uniform_rank32 scores -7.612950983984054 (gap_closed 1.1351984929614363) at 39,046,144 bytes. Every factored config outscores the full delta itself (-8.34454360266215), so gap_closed exceeds 1.0 for all of them.

- Cited file: results/fourth_pair_stage2.json
- Values relied on: Down Dominator -6.770329668759838 gap 1.290915115911159 at 38623232 bytes; uniform_rank32 -7.612950983984054 gap 1.1351984929614363 at 39046144 bytes; full -8.34454360266215
- Note: Down Dominator is byte-fair and leads on mean logprob, and both factored means exceed full so gaps over 1.0 check out.

### Claim B: SUPPORTED

On the combined 96 fresh items, the byte-fair Down Dominator (38,623,232 bytes) beats uniform_rank32: factored mean target logprob -6.343687772752477 vs -6.478079873557243, a raw margin of about 0.134 nats; gap_closed 1.3070672034171866 vs 1.2789186374354595. Both factored configs outscore the full delta (-7.809744927574116) and the base is -12.584130268980408, so gap_closed is above 1.0 and is not a recovery fraction on this pair.

- Cited file: results/fourth_pair_heldout96.json
- Values relied on: Down -6.343687772752477 gap 1.3070672034171866 vs uniform -6.478079873557243 gap 1.2789186374354595 at 38623232 bytes; full -7.809744927574116 base -12.584130268980408 margin ~0.134
- Note: Arithmetic verifies 0.134-nat margin and both gaps above 1.0, so not a recovery fraction.

### Claim C: SUPPORTED

The byte-fair recipe's combined-96 win is NOT consistent across subsets: on the heldout24 subset uniform_rank32 wins (gap_closed 1.152286379770239 vs Down Dominator 1.1242514732201125), while on the heldout72_new subset Down Dominator wins (1.3791549665115759 vs 1.3288521753254294).

- Cited file: results/fourth_pair_heldout96.json
- Values relied on: heldout24 uniform 1.152286379770239 vs Down 1.1242514732201125; heldout72_new Down 1.3791549665115759 vs uniform 1.3288521753254294
- Note: Subset gaps show opposite winners, so combined win is inconsistent across subsets.

### Claim D: SUPPORTED

On the combined 96, uniform_rank32's first-token accuracy (0.3229166666666667) exceeds Down Dominator's (0.2604166666666667) and nearly matches the full delta's (0.3333333333333333): the Spark recipe's logprob edge does not come with a first-token accuracy edge.

- Cited file: results/fourth_pair_heldout96.json
- Values relied on: combined96 first-token accuracy uniform 0.3229166666666667 vs Down 0.2604166666666667 vs full 0.3333333333333333
- Note: Uniform leads Down on accuracy and nears full despite losing on logprob.

### Claim E: SUPPORTED

The adapted Qwen2.5 NumPy forward is validated by internal consistency: graft check max abs diff 1.1641532182693481e-10, quantize_from_svd vs factored.quantize_delta max abs diff 0.0, and the full-delta config beats base overall by 5.411248325724856 nats with a positive gap in every bucket (knowledge 5.100221749843705, instruction 3.9774035670447834, math 7.156119660286076); verdict PASS. The full delta at fp16 is 3,087,138,816 bytes, about 79x the uniform patch's 39,046,144 bytes.

- Cited file: results/fourth_pair_stage2.json
- Values relied on: graft max diff 1.1641532182693481e-10, quantize diff 0.0, full-beats-base 5.411248325724856 buckets 5.100221749843705/3.9774035670447834/7.156119660286076 PASS; fp16 3087138816 vs 39046144 ~79x
- Note: Tiny consistency diffs and positive gaps in all buckets support PASS and size ratio.

## Headline

Question: Does the evidence support saying the byte-fair Spark recipe still beats the human uniform recipe at 1.5B scale, with the win narrowed to a small raw-logprob margin and not consistent across subsets? Answer yes or no, then give exactly one sentence I can quote as the headline.

Answer: yes

Sentence: Byte-fair Spark Down Dominator edges uniform_rank32 on combined fresh items by a small logprob margin while losing on one subset.

Summary: Down Dominator is byte-fair and leads on Stage2 24 and combined 96 logprob by about 0.13 nats but trails uniform on heldout24 and first-token accuracy. Gaps exceed 1.0 throughout, confirming full-delta outperformance rather than fractional recovery.
