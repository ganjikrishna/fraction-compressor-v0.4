# Spark Open validation (Fireworks): force-start control test (2026-10-28)

Muse Spark Open (accounts/fireworks/models/muse-spark-open) via the new custom.fireworks connector independently checked the force-start control test claims, with the same per-prompt evidence extract the other validators received. One call, inside Vinay's $100 Fireworks credit limit. The helper was imported as a module; max_tokens 16000.

- Verdicts: claims 1 to 3 SUPPORTED (it recounted the per-prompt verdicts, verified all 10 forced-token prefix flags, and recomputed the margin means itself). Claim 4: fair as a description of this experiment, TOO STRONG if read as general proof; it requires a scope and uncertainty qualifier (the 7 vs 8 clean difference is 1 of 10, within sampling error at n = 10, so "a small real edge" should be hedged). The missing-control objection is settled: YES.
- Tokens: {"prompt_tokens": 1772, "total_tokens": 7620, "completion_tokens": 5848, "prompt_tokens_details": {"cached_tokens": 0}, "completion_tokens_details": {"reasoning_tokens": 4747}, "output_tokens_details": {"reasoning_tokens": 4747}}. Logged in results/api_usage_log.jsonl (purpose sparkopen_fireworks_validation_forced).

## Prompt used (verbatim)

You are judging claims from a compression project's control test. You did not run the experiments; the underlying records are in results/skill_demo_forced.json (forced-start runs), results/skill_demo.json (unforced runs), and results/skill_demo_recipe.json (first-token margins). Give a verdict per claim: SUPPORTED or NOT SUPPORTED, citing the source file for each. Check the arithmetic yourself.

Context: Fraction Compressor v0.4 compresses the weight delta between a base model (Qwen2.5-0.5B) and a fine-tune into a 1-bit factored patch. The skill test used NuExtract-1.5-tiny (MIT), a fine-tune of the same base that fills a JSON template from a text (structured extraction). 10 test prompts. "Clean" = output parses as JSON, keys match the template, every expected value present. "Partial" = parses but something is off. "Failed" = does not parse; empty output counts as failed. Greedy decoding.

Background you should know: in an earlier debate about this project, Muse Spark raised the objection that the claim "the knowledge transfers, only the trigger does not" was UNPROVEN, because the control test had never been run: force-start the plain base with the correct first token and see whether it completes the extraction on its own. That control test has now been run, and the claims below are its results.

CLAIM 1 (unforced reference counts, clean / partial / failed out of 10): base 0/0/10; base + rank-32 patch 1/0/9; base + full fine-tune weights 8/1/1. Source: results/skill_demo.json, recounted in results/skill_demo_forced.json as its unforced reference.

CLAIM 2 (forced start): with the fine-tune's own first generated token forced for each prompt (each verified as a prefix of the fine-tune's recorded answer, 10 of 10), then greedy continuation: base 7/1/2; base + rank-32 patch 8/1/1. The forced patch counts exactly equal the full fine-tune's unforced counts (8/1/1). Source: results/skill_demo_forced.json.

CLAIM 3 (first-token margins, mean over the 10 prompts, logprob of the fine-tune's actual first token minus logprob of end-of-text): base -6.332, rank-32 patch -1.2942, full fine-tune +4.6005; rounded in the docs to -6.33, -1.29, +4.60. Source: results/skill_demo_recipe.json.

CLAIM 4 (interpretation, as written in docs/why-it-matters.md): "most of the extraction skill was already in the base, and what the fine-tune mainly installs is the decision to start. The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own unforced score: a small real edge beyond the trigger, but the gate is the main story." Judge whether this is fair, too strong, or too weak given claims 1 to 3, n = 10 prompts, one skill, one model pair. If too strong or too weak, give exact replacement wording.

Also answer directly: does the control test now settle the earlier missing-control objection? Answer per claim first (verdict + one or two sentences each), then the objection question, then any wording change you require.


EVIDENCE EXTRACTED FROM THE FILES (per-prompt verdicts):
- results/skill_demo.json | base (no patch): counts={'clean': 0, 'partial': 0, 'failed': 10} per-prompt={'person': 'failed', 'product': 'failed', 'event': 'failed', 'company': 'failed', 'book': 'failed', 'sports': 'failed', 'recipe': 'failed', 'weather': 'failed', 'job': 'failed', 'model': 'failed'}
- results/skill_demo.json | base + compressed patch (uniform rank 32): counts={'clean': 1, 'partial': 0, 'failed': 9} per-prompt={'person': 'failed', 'product': 'failed', 'event': 'failed', 'company': 'failed', 'book': 'clean', 'sports': 'failed', 'recipe': 'failed', 'weather': 'failed', 'job': 'failed', 'model': 'failed'}
- results/skill_demo.json | base + full delta (fine-tune weights): counts={'clean': 8, 'partial': 1, 'failed': 1} per-prompt={'person': 'partial', 'product': 'clean', 'event': 'failed', 'company': 'clean', 'book': 'clean', 'sports': 'clean', 'recipe': 'clean', 'weather': 'clean', 'job': 'clean', 'model': 'clean'}
- results/skill_demo_forced.json | base, forced start: counts={'clean': 7, 'partial': 1, 'failed': 2} per-prompt={'person': 'clean', 'product': 'clean', 'event': 'clean', 'company': 'partial', 'book': 'clean', 'sports': 'clean', 'recipe': 'failed', 'weather': 'clean', 'job': 'clean', 'model': 'failed'}
- results/skill_demo_forced.json | base + compressed patch (uniform rank 32), forced start: counts={'clean': 8, 'partial': 1, 'failed': 1} per-prompt={'person': 'partial', 'product': 'clean', 'event': 'failed', 'company': 'clean', 'book': 'clean', 'sports': 'clean', 'recipe': 'clean', 'weather': 'clean', 'job': 'clean', 'model': 'clean'}
- forced tokens (token_text, matches_recorded_answer_prefix): {'person': ('{\n', True), 'product': ('{\n', True), 'event': (' {\n', True), 'company': ('{\n', True), 'book': (' {\n', True), 'sports': ('{\n', True), 'recipe': (' {\n', True), 'weather': (' {\n', True), 'job': ('{\n', True), 'model': ('{\n', True)}
- results/skill_demo_recipe.json | first_token_margins.mean_margin = {'base': -6.332, 'full_delta': 4.6005, 'rank32_uniform': -1.2942, 'spark_recipe': -4.1422}
- per-prompt margins (base / rank32_uniform / full_delta):
    person: -6.6637 / -1.881 / 5.466
    product: -7.0406 / -2.2765 / 4.5432
    event: -4.7228 / -0.4662 / 3.2111
    company: -7.1664 / -0.5471 / 8.0449
    book: -6.7498 / 0.7316 / 6.5009
    sports: -5.3831 / -1.0533 / 4.4924
    recipe: -3.3878 / -1.8888 / 2.7689
    weather: -5.0015 / -2.7451 / 3.1694
    job: -8.0339 / -2.2987 / 2.537
    model: -9.1701 / -0.5171 / 5.2715

## Spark Open (Fireworks) reply (verbatim)

All arithmetic checked from per-prompt data supplied.

**CLAIM 1: SUPPORTED**
Source: `results/skill_demo.json` - counts verified. `results/skill_demo_recipe.json` recapitulates same.
* `base`: per-prompt `failed x10` = `0/0/10` as claimed.
* `base+rank-32`: per-prompt `clean=1` (`book`), `failed x9` = `1/0/9` as claimed.
* `base+full delta`: per-prompt `clean 8, partial 1 (person), failed 1 (event)` = `8/1/1` as claimed.

**CLAIM 2: SUPPORTED**
Source: `results/skill_demo_forced.json`
* Forced tokens all `matches_recorded_answer_prefix=True`, `10/10` as claimed: `{\n` or ` {\n`.
* Greedy continuation after forcing: `base` per-prompt `clean 7, partial 1 (company), failed 2 (recipe,model)` = `7/1/2` as claimed.
* `base+rank-32, forced` per-prompt `clean 8, partial 1 (person), failed 1 (event)` = `8/1/1` as claimed.
* This numerically equals `full fine-tune unforced 8/1/1` from Claim 1, in fact per-prompt identical: `person partial, product clean, event failed, company clean, book clean, sports clean, recipe clean, weather clean, job clean, model clean`.

**CLAIM 3: SUPPORTED**
Source: `results/skill_demo_recipe.json` + per-prompt margins supplied. Means recomputed:
* `base`: sum -63.3197 /10 = -6.33197 = `-6.332` reported, `-6.33` rounded OK.
* `rank32_uniform`: sum -12.9422 /10 = -1.29422 = `-1.2942` reported, `-1.29` rounded OK.
* `full_delta`: sum 46.0053 /10 = 4.60053 = `4.6005` reported, `+4.60` rounded OK.

**CLAIM 4: Fair description of *this* experiment, TOO STRONG if read as general proof without scope/uncertainty qualifier.**
As a summary of Claims 1-3 for `n=10`, one skill, one model pair: `base unforced 0/0/10 -> forced 7/1/2` shows most completion ability is latent; `full delta unforced 8/1/1` and margin shift `base -6.33 -> rank32 -1.29 -> full +4.60` shows the main installed effect in unforced generation is the gate/start decision; `patch forced 8/1/1` matching `full unforced 8/1/1` is consistent with "gate is main story, at most small additional edge."

Too strong in two respects: `7 vs 8` clean is `1/10` difference, well within sampling error for `n=10` - cannot assert a "real" edge vs noise; and `rank32` mean margin `-1.29` is still negative (still favours EOS), unlike full `+4.60`, and unforced `rank32` is still `1/0/9`.

**Does the control settle Muse Spark's missing-control objection? YES.**
The objection was `UNPROVEN because forced-start control never run`. It has now been run: `results/skill_demo_forced.json` provides the 10-prompt forced-start for `base` and `patch`. It shows the base completes when forced, settling that the data gap is closed. For this skill/model it overturns "knowledge transfers, only trigger does not" as a strong knowledge-insertion claim - here the gate is the dominant effect. It does not generalize beyond this 10-prompt, 1-skill, 1-model-pair test.

**Required wording change - add scope and uncertainty:**

> "In this 10-prompt NuExtract-1.5-tiny test on Qwen2.5-0.5B, most completion ability is already latent in the base: forced with the fine-tune's first token the base is 7 clean/1 partial/2 failed vs 8/1/1 for the full fine-tune unforced and for the rank-32 patch forced. First-token EOS-vs-start margins (base -6.33, patch -1.29, fine-tune +4.60) indicate the fine-tune mainly shifts the decision to start, which the patch only partially reproduces (unforced patch still 1/0/9). Any additional completion edge beyond the trigger is at most ~1/10 in this sample, within sampling error for n=10, and requires larger-scale testing to generalize."

Without such qualifier the sentence "a small real edge beyond the trigger" should be hedged to "consistent with at most a small edge, within sampling error" and "most of the extraction skill was already in the base *in this test*" .
