# Panel wording adoption review (2026-10-29, local only)

Review of the two panel-wording edits proposed after the patch-value discussion, run BEFORE applying anything, per Vinay's instruction "apply both and review before you do it." Reviewers: Muse Spark 1.3 via the Meta Model API, and Muse Glimmer via Flash OmniRoute (served model confirmed `meta/muse-glimmer-30b`). Both reviewers got the two edit texts verbatim, their placements, and the same evidence pack.

**Outcome: BOTH edits BLOCKED. Nothing was applied to README.md or docs/submission_draft.md.**

- Spark: Edit 1 PASS (one minor wording note, explicitly non-substantive). Edit 2 SUBSTANTIVE FLAG on placement (point c).
- Glimmer: Edit 1 SUBSTANTIVE FLAG on numbers/claim strength (points a and b). Edit 2 SUBSTANTIVE FLAG on placement (point c), agreeing with Spark.

## Where the reviewers converge

Both reviewers independently flagged Edit 2's placement: in the Impact paragraph the size claim ("an update is a 19 MB file on a stable base") sits in sentence 2, while the lossy/first-token sentence would land after the limits sentence, separated by the rollout/rollback and limits sentences, so the qualifier does not stand next to the size claim under the panel rule.

## Spark verdict (verbatim)

EDIT 1: PASS
(a) Numbers exact: 19,358,176 bytes, 23.2% = 0.232, 0.605 of 2.607 nats, first-token 0.010 below base 0.031, ~0.1 s matches 0.104 s and 0.087 s. About 23% rounding is exact.
(b) No stronger claim: lossy + degraded first-token matches evidence, training-free / no teacher bill matches deterministic conversion, not a training aid mirrors pilot conclusion trailed by 0.213 gap-closed, limited to where training cannot happen matches LoRA 1.362 +/-0.033 winning on recovery. "Matched-byte" for 18,696,192 vs 19,358,176 is inexact in strict bytes but minor wording only - LoRA is just under, still wins, does not change claim.
(c) Passes panel rule: lossy qualifier and first-token regression are in same sentence as the byte-exact size claim, in paragraph immediately after the existing about 1GB to about 19MB size claim.

EDIT 2: SUBSTANTIVE FLAG
(a) Pass: only number 23.2% is exact for 0.232 gap closed. "Below the base model's own" matches 0.010 < 0.031, no inexact number.
(b) Pass: no hype. Partial recovery scope is consistent with LoRA winning where training available.
(c) FLAG - substantive: size claim is "an update is a 19 MB file" in sentence 2. Proposed lossy + first-token sentence is inserted after the limits sentence, 2-3 sentences later, separated by rollout/rollback/one-base sentences. Qualifier and regression do not stand next to the size claim, leaving the size claim unqualified.
(d) Pass: fits without duplicating or contradicting. Existing Impact limits are base-lifetime / breakage / need new models; Technical Depth LoRA passage is 18,696,192 just under 19,358,176, 136% across 3 seeds vs 23%, ties full fine-tune on first-token, 1,500 generations + ~8h vs deterministic no-training conversion. Added sentence repeats only 23.2% + below-base and gives same training-cannot-happen rationale, complementary not contradictory.

## Glimmer verdict (verbatim)

EDIT 1: SUBSTANTIVE FLAG

(a) Numbers not exact. The paragraph uses "about 23% gap closure" for a 0.232 / 23.2% gap closed value, and "~0.1 s hot-swap" for the demo 0.104 s and 0.087 s swaps. Both are approximations, not exact against evidence. The "matched-byte distilled LoRA" claim is also numerically inaccurate: LoRA is 18,696,192 bytes vs patch 19,358,176 bytes.

(b) Claim stronger than evidence. "Where training is available, a matched-byte distilled LoRA wins." The evidence shows a LoRA at 18,696,192 bytes, just under the patch's 19,358,176 bytes, with gap closed 1.362±0.033 and first-token 0.167-0.177. It is not matched-byte and "wins" is an overall superiority claim not fully established by the evidence alone.

(c) Placement. The lossy qualifier "The patch is a lossy, training-free distribution format..." and first-token regression "first-token accuracy 0.010 (below base 0.031)" are in the new paragraph immediately after the existing paragraph that contains the size claim "from about 1 GB to about 19 MB". The size claim is repeated in the new paragraph as 19,358,176 bytes, so the qualifier/regression do stand next to a size claim in the adjacent paragraph.

EDIT 2: SUBSTANTIVE FLAG

(a) Numbers exact. "closes 23.2% of the gap" matches gap closed 0.232. No other numeric values are given.

(b) No over-claim. "its first-token accuracy sits below the base model's own" is supported by patch 0.010 < base 0.031, and the offer for cases where training cannot happen and partial recovery is acceptable is consistent with the recovery-tuning pilot showing the patch is not supported as a training aid/warm start and the LoRA cost of 1,500 teacher generations + ~8 h training.

(c) Placement does not satisfy the panel rule. The size claim in the Impact paragraph is "an update is a 19 MB file on a stable base." The added sentence with the lossy qualifier and first-token regression is appended after the limits sentence, separated from the size claim by the rollout sentence and the limits sentence. The qualifier/regression are therefore not standing next to the size claim.

(d) Honesty fit. The added sentence is consistent with and does not duplicate or contradict the Technical Depth LoRA paragraph. The paragraph states patch's 23% vs adapter's 136% gap closed and adapter ties full fine-tune on first-token accuracy, with adapter needing 1,500 teacher generations and ~8 h training while the patch is a deterministic conversion with no training. The new sentence's 23.2% gap closure, first-token below base, and use for no-training/partial-recovery cases fits that honesty framing.

## Fixes a revised version would need (reviewer's points, not applied)

1. Edit 1: drop "matched-byte" (the adapter is 18,696,192 B, just under the patch's 19,358,176 B, not byte-identical), soften or scope "wins," and replace the approximations "about 23%" and "~0.1 s" with the exact values already used elsewhere in the same paragraph (23.2%; 0.104 s and 0.087 s).
2. Edit 2: move the lossy/first-token qualifier next to the size claim itself (the "19 MB file" sentence), instead of after the limits sentence, to satisfy the panel proximity rule both reviewers applied.

## Compute

- Muse Spark 1.3, Meta Model API: prompt 1,151, completion 6,722 (incl. 6,225 reasoning), total 7,873 tokens. Logged in results/api_usage_log.jsonl, purpose "panel wording adoption review".
- Muse Glimmer, Flash OmniRoute (model requested nvidia/meta/muse-glimmer-30b, served meta/muse-glimmer-30b): prompt 1,199, completion 4,438, total 5,637 tokens. Flash-local, not in the hosted log.

## Addendum (2026-10-29): revised edits, Glimmer re-check, applied

The two edits were revised per the reviewers' fixes above (Edit 1: "matched-byte" dropped, "wins" scoped to "on these tests," exact 23.2% and 0.104 s / 0.087 s replacing the approximations; Edit 2: the lossy sentence moved to immediately after the "19 MB file" size claim). Vinay approved the revised pair. Glimmer re-checked the changed spots before anything was applied.

Glimmer re-check verdict (model requested nvidia/meta/muse-glimmer-30b, served meta/muse-glimmer-30b; prompt 933, completion 4,096, total 5,029 tokens; Flash-local, not in the hosted log):

EDIT 1: PASS. (a) Numbers exact: 19,358,176 bytes; 23.2% = 0.232; 0.605 of 2.607 nats; first-token 0.010 < base 0.031; hot-swap 0.104 s and 0.087 s; LoRA 18,696,192 bytes, gap closed 1.362 vs 0.232. (b) LoRA claim properly scoped: "just under the patch's size," "closes far more of the gap on these tests"; no matched-byte claim, no unscoped win.

EDIT 2: PASS. (a) Numbers exact (23.2%; first-token regression qualitative, matching 0.010 < 0.031). (c) Proximity satisfied: the inserted sentence stands immediately after the size claim "an update is a 19 MB file on a stable base" and immediately before the rollout sentence.

Both edits were applied on 2026-10-29 exactly as re-checked, and the applied texts were read back from both files to verify placement.

Applied Edit 1 (README.md, new paragraph after the "One thing to be clear about" paragraph):
"The patch is a lossy, training-free distribution format for a fine-tune delta: at 19,358,176 bytes it closes 23.2% of the gap (0.605 of 2.607 nats), with first-token accuracy 0.010 (below base 0.031), and it is not a training aid. It is useful only where training cannot happen and 23.2% gap closure with degraded first-token accuracy is acceptable: weights-only fine-tunes, many variants against one base, live hot-swap (0.104 s and 0.087 s in the recorded demo), deterministic checkable bytes, no data trail or teacher bill. Where training is available, a distilled LoRA at 18,696,192 bytes, just under the patch's size, closes far more of the gap on these tests (1.362 against 0.232)."

Applied Edit 2 (docs/submission_draft.md, Impact paragraph, inserted after "...on a stable base." and before "Rollout is a small download"):
"The patch is also lossy: on our main pair it closes 23.2% of the gap to the full fine-tune, and its first-token accuracy sits below the base model's own, which is why the format is offered for cases where training cannot happen and partial recovery is acceptable."
