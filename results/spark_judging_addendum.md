# Muse Spark judging addendum: strengthening results (2026-10-27)

Second judging pass under Vinay's validation rule. Muse Spark (muse-spark-1.3,
Meta Model API) judged the claims from the strengthening runs, given only the
numbers copied from the three result files below, with a verdict and a file
citation required per claim. One call: 1,507 prompt tokens, 4,283 completion
tokens (3,389 of them reasoning), 5,790 total. Full structured record:
results/spark_judging_addendum.json.

Sources judged: results/alien_sweep_heldout96.json,
results/second_pair_stage2.json, results/second_pair_heldout96.json.
(gap_closed = (factored - base) / (full - base) on mean target logprob.)

## Verdicts: 4 of 5 claims SUPPORTED, 1 NOT SUPPORTED

| Claim | Verdict | Cited file |
|---|---|---|
| A. Combined 96 (Qwen pair): lite closes 23.2% vs uniform 2.1%, at fewer bytes (19,358,176 vs 19,434,496 B) | SUPPORTED | results/alien_sweep_heldout96.json |
| B. Lite beats uniform on both subsets (9.5% vs 1.6%; 30.4% vs 2.3%); the earlier shrinkage pattern reversed on fresh items | SUPPORTED | results/alien_sweep_heldout96.json |
| C. Pair 2: byte-fair o-down-rebalanced (19,683,328 B, inside the 19,705,856 B budget) beats uniform on the same 96 by 0.293 nats raw logprob | SUPPORTED | results/second_pair_heldout96.json |
| D. Pair 2: gap_closed exceeds 1.0 for all factored configs because they outscore the full fp16 delta; not a recovery fraction on that pair | SUPPORTED | results/second_pair_heldout96.json |
| E. The headline ruling still stands: lite is named the byte-fair leader on pair 1, mlp_behemoth only as the byte-unfair parent | NOT SUPPORTED | results/alien_sweep_heldout96.json |

## The one disagreement: claim E

Spark's note, verbatim: "Numbers show lite beats uniform and parent is
byte-unfair, but leadership among all byte-fair configs and prose naming
cannot be verified from numbers alone." Its values relied on: "excerpt lists
only uniform, lite, and reference mlp_behemoth (21,719,776 B, gap 0.265984);
no full byte-fair ranking or quoted prose provided."

Ember's read: this is a scope objection, not a numbers dispute. Spark agrees
with every number inside claim E (lite beats uniform byte-fair; the parent
is byte-unfair). What it refuses to certify is the ruling itself, because
the ruling is a wording decision recorded in BUILD_PLAN.md and the project's
prose, and a judge shown only result numbers cannot verify prose. On the one
checkable sub-point, the file does support the ruling: in
results/alien_sweep_heldout96.json the only byte-fair configs on pair 1 are
uniform_rank32 and mlp_behemoth_lite (mlp_behemoth is recorded byte-unfair),
and lite leads those two on combined and on both subsets. The NOT SUPPORTED
verdict is recorded as-is; the ruling stands on its original basis (Vinay's
decision following Glimmer's stricter reference check), not on this pass.

## Spark's updated headline statement

Verbatim, as requested (one paragraph):

> On Qwen2.5-0.5B the byte-fair mlp_behemoth_lite closes 23.2% of the mean target-logprob gap on 96 fresh items versus 2.1% for uniform rank32 at fewer bytes, winning both subsets (9.5% vs 1.6% on heldout24 and 30.4% vs 2.3% on heldout72_new) so the combined figure exceeds the earlier 9.5% first-24 figure, with byte-unfair parent mlp_behemoth at 26.6% for reference only, while on SmolLM2-360M the byte-fair o-down-rebalanced beats uniform by 0.293 nats raw mean logprob within budget, but all factored configs outscore the full fp16 delta itself so gap_closed exceeds 1.0 and is not a recovery fraction with math-bucket gaps recorded as null where full scored below base, and all results remain mean target logprob of correct tokens not task accuracy.
