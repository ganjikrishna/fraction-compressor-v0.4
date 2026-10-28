# Glimmer validation: force-start control test (2026-10-28)

Independent validation of the force-start control test (results/skill_demo_forced.json) by Muse Glimmer 30B, the third check on these claims after script recomputation and alongside the Muse Spark judging addendum (results/spark_validation_forced.md).

- Route: Flash-local call. Pi's model config on Flash (~/.pi/agent/models.json) routes `nvidia/meta/muse-glimmer-30b` through the local OmniRoute provider (http://localhost:20128/v1, OpenAI-compatible) to NVIDIA NIM; the call was run as scripted Pi (`pi -p ... --model nvidia/meta/muse-glimmer-30b`) and the route id names the model on the session. In the project's first Glimmer reference the NIM response's served-model field confirmed `meta/muse-glimmer-30b`.
- This was a Flash-local NIM call through Vinay's own Pi/OmniRoute setup, not a Meta Model API or Baseten call, so it is not logged in results/api_usage_log.jsonl; this file is the record (same convention as the earlier Glimmer references).
- Before this review, an independent script recomputation recounted every clean/partial/failed count from the per-prompt records in results/skill_demo_forced.json and results/skill_demo.json (no mismatches), verified all 10 forced tokens as prefixes of the recorded full-delta answers (10 of 10), and verified the first-token margins against results/skill_demo_recipe.json (base -6.332, rank-32 patch -1.2942, full delta +4.6005).
- Verdict: FAIR. Glimmer confirmed the arithmetic and the interpretation, with a small-sample scope caveat (n = 10, one skill, one model pair) and an optional scope-bounded rewording.

## Prompt used (verbatim)

You are giving an independent validation verdict on a compression project's control-test results. You did not run these experiments; check the arithmetic in the counts below and judge whether the interpretation wording is honest. Answer directly in text; do not use any tools.

Context: Fraction Compressor v0.4 stores the weight difference (delta) between a base model and a fine-tuned version as a 1-bit factored patch. A separate skill test used a real third-party fine-tune instead of an Instruct version: NuExtract-1.5-tiny (MIT), a fine-tune of Qwen2.5-0.5B that reads a text plus a JSON template and answers with the template filled in (structured extraction). 10 test prompts. A generation counts as "clean" if it parses as JSON, the keys match the template, and every expected value is present; "partial" if it parses but something is off; "failed" if it does not parse (an empty output counts as failed). Decoding is greedy.

Earlier finding: the skill is gated by the first generated token. The plain base emits end-of-text immediately on all 10 prompts (0 clean), the full fine-tune starts the JSON and passes 9 of 10, and the compressed rank-32 patch starts on only 1 of 10. First-token margins (logprob of the fine-tune's actual first token minus logprob of end-of-text, averaged over the 10 prompts): base -6.33, rank-32 patch -1.29, full fine-tune +4.60. In an earlier review, Muse Spark objected that the claim "the knowledge transfers, only the trigger does not" was unproven, because the control test had never been run: force-start the plain base with the correct first token and see whether it can complete the extraction on its own.

The control test has now been run. The fine-tune's own first generated token for each prompt was forced as the first token, then generation continued greedily (max 64 new tokens including the forced one). Each forced token was verified to be a prefix of the fine-tune's recorded answer for that prompt (10 of 10 match). Results, counts out of 10 (clean / partial / failed):

Unforced reference:
- base (no patch): 0 / 0 / 10
- base + rank-32 patch: 1 / 0 / 9
- base + full fine-tune weights: 8 / 1 / 1

Forced start:
- base, forced start: 7 / 1 / 2
- base + rank-32 patch, forced start: 8 / 1 / 1

So with the start forced, the plain base goes from 0 clean to 7 clean, and the forced patch's counts (8/1/1) exactly equal the full fine-tune's unforced counts (8/1/1). The counts above were independently recounted from the per-prompt records by a script before this review, with no mismatches.

The interpretation now written in the project's docs (docs/why-it-matters.md) is:

"most of the extraction skill was already in the base, and what the fine-tune mainly installs is the decision to start. The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own unforced score: a small real edge beyond the trigger, but the gate is the main story."

Your task:
1. Check the arithmetic and the comparisons in the counts above (do the forced counts support the sentences that cite them?).
2. Rule on the interpretation: is it fair, too strong, or too weak, given that n = 10 prompts, one skill, one model pair? Pay special attention to (a) "most of the extraction skill was already in the base", (b) "matching the fine-tune's own unforced score" as a description of 8/1/1 vs 8/1/1, and (c) "a small real edge beyond the trigger" for the patch's forced 8/1/1 vs the base's forced 7/1/2.
3. If any wording is too strong or too weak, give the exact replacement wording you would accept.
End with a one-line verdict: FAIR, TOO STRONG, or TOO WEAK, followed by the reason in one sentence.

## Glimmer reply (verbatim)

The counts you quote are internally consistent and the comparisons drawn from them are arithmetically correct.

* Unforced: base 0/0/10, base+rank-32 1/0/9, base+full fine-tune 8/1/1.
* Forced start: base forced 7/1/2, base+rank-32 forced 8/1/1.
* Forced start patch 8/1/1 is numerically identical to full fine-tune unforced 8/1/1.
* Forced start patch vs forced start base is +1 clean, same partial, 2 failed →1 failed. That is a small edge.

On the wording:

a) “most of the extraction skill was already in the base” – the forced-start move lifts the base from 0 clean to 7 clean /1 partial /2 failed on this 10-prompt set. That is strong evidence that completion capability is largely present and is gated by first-token choice. “Most” is a qualitative summary of 7/10 clean after forcing; it is defensible for this set but is a generalisation from n=10.

b) “matching the fine-tune's own unforced score” as a description of 8/1/1 vs 8/1/1 – true numerically for the reported counts.

c) “a small real edge beyond the trigger” for patch forced 8/1/1 vs base forced 7/1/2 – true: the patch adds one extra clean completion and removes one failure on this set. The edge is small.

The only overreach is extrapolation beyond the data. With n=10, one skill, one model pair the claims are set-specific. An honest version that keeps the numbers but bounds the scope is:

“The base can complete 7 of 10 cleanly and 1 partly when forced to start, suggesting much of the extraction capability is present but gated by the first token. On this 10-prompt set the rank-32 patch under forced start scores 8 clean /1 partial /1 failed, numerically matching the full fine-tune’s unforced score of 8/1/1, with a modest +1 clean edge over the forced-start base.”

Verdict: FAIR, the arithmetic holds and the interpretation is supported on this 10-prompt control test, with the usual small-sample generalisation caveat.
