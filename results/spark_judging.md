# Muse Spark judging pass (2026-10-27)

Per Vinay's validation rule and the Agents 101 grounding takeaway, Muse Spark
(muse-spark-1.3, Meta Model API) acted as an independent judge over the finished
Alien Sweep results. Spark was given only the numbers, copied from the three
result files below, and had to return a verdict per claim with the source file
cited by name. One call, no retry needed (every verdict carried its citation):
2,384 prompt tokens, 5,352 completion tokens (4,085 of them reasoning), 7,736
total. Full structured record: results/spark_judging.json.

Sources judged: results/alien_sweep_stage2.json,
results/alien_sweep_heldout.json, results/hotswap_demo.json.
(gap_closed = (factored - base) / (full - base) on mean target logprob.)

## Verdicts: 10 of 10 claims SUPPORTED

| Claim | Verdict | Cited file |
|---|---|---|
| C1. Patches ~51x smaller than the full fp16 delta (987,922,432 B vs 19,434,496 / 19,358,176 B) | SUPPORTED | results/hotswap_demo.json |
| C2. mlp_behemoth (Spark recipe) best overall on Stage 2, gap_closed 0.457 | SUPPORTED | results/alien_sweep_stage2.json |
| C3. That win was NOT byte-fair: 11.8% more bytes than uniform, the cheapest config | SUPPORTED | results/alien_sweep_stage2.json |
| C4. mlp_behemoth still first overall on fresh held-out items (0.108 vs 0.016) | SUPPORTED | results/alien_sweep_heldout.json |
| C5. Byte-matched lite, at FEWER bytes than uniform, still beats it held-out (0.095 vs 0.016) | SUPPORTED | results/alien_sweep_heldout.json |
| C6. The edge shrank sharply on fresh items: 45.7% to 10.8% gap_closed | SUPPORTED | results/alien_sweep_stage2.json, results/alien_sweep_heldout.json |
| C7. Held-out win is aggregate only: uniform wins knowledge (0.272 vs 0.267); no factored config recovers instruction (all negative) | SUPPORTED | results/alien_sweep_heldout.json |
| C8. Logprob only: first-token accuracy ~0 for factored configs, no task-solving claim | SUPPORTED | results/alien_sweep_stage2.json, results/alien_sweep_heldout.json |
| C9. Held-out math gap_closed (11.771 etc.) is a 0.0797-nat denominator artifact | SUPPORTED | results/alien_sweep_heldout.json |
| C10. Hot-swap: base fails strict JSON and rambles; both patches return exact JSON and stop; swaps ~0.1 s | SUPPORTED | results/hotswap_demo.json |

Note what got supported: the claims as written already carry the caveats (the
byte-fairness limit in C3, the shrinkage in C6, the bucket losses in C7, the
metric limit in C8, the artifact warning in C9). Spark did not soften any of
them, and its spot arithmetic checks out (it recomputed the 11.76% overage and
the ~0.94-nat math gain over the 0.0797 denominator itself).

## Headline question

Asked: is "leading recipe, conditionally validated" the honest headline, as
opposed to "confirmed winner"? Spark's answer, verbatim:

> yes. mlp_behemoth leads overall on both Stage 2 and held-out including
> byte-matched lite vs uniform, but the lead shrinks from 45.7% to 10.8%, loses
> knowledge to uniform, fails instruction, has no accuracy gain, and relies on
> a math ratio artifact. That pattern supports leading but only conditionally,
> not confirmed winner.

## Spark's demo sentence

The single sentence Spark would use in the 3-minute demo, verbatim:

> mlp_behemoth leads on overall logprob in Stage 2 and held-out even when
> byte-matched, but the lead shrinks sharply on fresh items with no accuracy
> gain and no instruction recovery.

## Where Spark and Gemini land

Both independent judges now agree on the headline. Gemini (see
results/gemini_validation_day2.md) recomputed every number exactly, ruled
"confirmed winner" too strong, and recommended "conditionally validated
leading recipe" with the same wording limits. Spark, judging from the numbers
alone, reached the same wording and the same caveats. No disagreement to
report; the headline in the demo and submission stays "leading recipe,
conditionally validated," with the shrinkage, bucket trade-offs, and
logprob-only metric stated next to it.
