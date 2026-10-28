# Muse Spark judging pass: the missing baseline (2026-10-28)

Muse Spark (muse-spark-1.3, Meta Model API) acted as an independent judge
over the BitDelta-baseline results in results/bitdelta_baseline.json. Spark
was given only the numbers copied from that file, and had to return a verdict
per claim with the source file cited by name. One call: 913 prompt tokens,
2,912 completion tokens (2,187 of them reasoning), 3,825 total. Full
structured record: results/spark_judging_baseline.json.

Source judged: results/bitdelta_baseline.json.
(gap_closed = (config - base) / (full_delta - base) on mean target logprob
over the combined 96 fresh held-out questions; base -11.1498, full -8.5425.)

## Verdicts: 6 of 6 claims SUPPORTED

| Claim | Verdict | Cited file |
|---|---|---|
| B1. Plain 1-bit floor price is exactly 61,745,828 B (493,961,216 weights at 1 bit + 169 fp32 scales) | SUPPORTED | results/bitdelta_baseline.json |
| B2. BitDelta-initialization config closes 0.436 of the gap (-10.0128 vs base -11.1498, full -8.5425) | SUPPORTED | results/bitdelta_baseline.json |
| B3. Factored uniform rank 108 prices just under the plain price (61,258,816 B; rank 109 would exceed) and closes 0.385 | SUPPORTED | results/bitdelta_baseline.json |
| B4. At the ~61.7 MB budget the plain initialization closes MORE than the factored format (0.436 vs 0.385); factored does not win there | SUPPORTED | results/bitdelta_baseline.json |
| B5. At 19.4 MB no plain 1-bit delta can exist (floor 61,745,828 B); factored closes 0.021 (uniform) and 0.232 (lite) there | SUPPORTED | results/bitdelta_baseline.json |
| B6. bitdelta_init is the published initialization only, no distillation or training; not citable as full BitDelta quality | SUPPORTED | results/bitdelta_baseline.json |

Spark recomputed the derived numbers itself (the price sum, both gap-closed
ratios, and the rank-108/109 price bracket) and did not soften B4, the claim
that lands against this project: at the plain 1-bit floor price, the plain
initialization beats our format.

## Headline question

Asked: is "the factored format's win is reach, not quality per byte at that
budget" the honest one-sentence conclusion? Spark's answer: yes, and it
returned the sentence unchanged:

> The factored format owns the low-budget region (below ~62 MB on this pair)
> where a plain 1-bit delta cannot exist at all, but at the plain 1-bit floor
> price the plain initialization closes more of the gap (43.6% vs 38.5%), so
> the factored format's win is reach, not quality per byte at that budget.
