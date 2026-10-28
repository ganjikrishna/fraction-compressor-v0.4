# Spark judging: force-start control test (2026-10-28)

Muse Spark 1.3 (Meta Model API) judging pass on the force-start control test, the direct follow-up to Spark's own earlier objection in results/why_debate.md that "the knowledge transfers" was unproven without a force-start control.

- Verdicts: claims 1 to 3 SUPPORTED (Spark recounted the per-prompt verdicts and recomputed the margin means itself: base -63.3197/10 = -6.332, patch -12.9422/10 = -1.2942, full +46.0053/10 = +4.6005). Claim 4 (interpretation) ruled TOO STRONG on two wording points, with replacement wording required. The missing-control objection is settled for this test.
- Procedure note: the first call (750 prompt / 5,664 completion / 6,414 total tokens) returned NOT SUPPORTED on everything because the prompt named the source files without including their contents, and Spark declined to support assertions it could not see. The claims were re-judged unchanged on a second call (1,636 prompt / 5,425 completion / 7,061 total tokens) with a per-prompt evidence extract from the three files embedded in the prompt. Both calls are logged in results/api_usage_log.jsonl (purpose spark_validation_forced).

## Prompt used (verbatim, second call)

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

## Spark reply (verbatim, second call)

**Per-claim verdicts:**

**CLAIM 1: SUPPORTED. Source: `results/skill_demo.json`**
Per-prompt recount matches: base 10x failed = 0/0/10; rank-32 patch 1x clean (book) + 9x failed = 1/0/9; full delta 8x clean + 1x partial (person) + 1x failed (event) = 8/1/1.

**CLAIM 2: SUPPORTED. Source: `results/skill_demo_forced.json`**
Base forced: person,product,event,book,sports,weather,job clean (7) + company partial (1) + recipe,model failed (2) = 7/1/2. Patch forced: product,company,book,sports,recipe,weather,job,model clean (8) + person partial (1) + event failed (1) = 8/1/1, numerically and per-prompt identical to full unforced 8/1/1. All 10 forced tokens listed as `matches_recorded_answer_prefix: True`.

**CLAIM 3: SUPPORTED. Source: `results/skill_demo_recipe.json`**
Recomputed mean from per-prompt margins: base sum -63.3197/10 = -6.332; rank32_uniform sum -12.9422/10 = -1.2942; full_delta sum 46.0053/10 = 4.6005. Rounded -6.33, -1.29, +4.60 is correct.

**CLAIM 4: TOO STRONG as written.**
Direction is right, but "small real edge" asserts reality from a 1-prompt difference with n=10, and "most of the extraction skill was already in the base" is unqualified to one skill, one pair, greedy decoding.

**Earlier missing-control objection:**
Yes, now settled for this test. The objection was: never force-started the plain base to test completion vs trigger. That control was now run: base goes 0/0/10 unforced to 7/1/2 forced, and base first-token margin -6.332 vs full +4.6005 shows strong trigger gating. Knowledge largely present, trigger is main barrier - proven here, not generalizable beyond this 10-prompt skill/pair.

**Required replacement wording for `docs/why-it-matters.md`:**

> In this 10-prompt structured-extraction test on this base/fine-tune pair, most of the tested completion ability was already in the base, and what the fine-tune mainly installs is the decision to start: forcing the fine-tune's first token lifts the base from 0/0/10 to 7/1/2, with first-token margins base -6.33, patch -1.29, fine-tune +4.60. Under the same forced start the rank-32 patch scores 8/1/1, numerically matching the fine-tune's unforced 8/1/1 in this sample - one clean more than the forced base - consistent with the gate being the main story, but with n=10 this does not establish a real beyond-trigger edge and does not generalize beyond this skill, pair and greedy decoding.

