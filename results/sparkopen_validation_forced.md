# Spark Open validation (Baseten): force-start control test (2026-10-28)

Muse Spark Open (meta-models/muse-spark-open-1026) via Baseten independently checked the force-start control test claims, with the same per-prompt evidence extract the other validators received. The helper was imported as a module (the CLI truncates output); max_tokens 16000.

- Verdicts: claims 1 to 3 SUPPORTED (it recounted the per-prompt verdicts and recomputed the margin means itself). Claim 4: the factual part SUPPORTED; the interpretive framing TOO STRONG as written for general use, directionally supported for this narrow test, with a required replacement wording that scopes the claim to the 10-prompt test. The missing-control objection is settled in the specific sense raised: the hypothesis moves from unproven to provisionally supported in this setting.
- Tokens: {"prompt_tokens": 1773, "completion_tokens": 4389, "total_tokens": 6162, "prompt_tokens_details": {"audio_tokens": 0, "cached_tokens": 128}, "completion_tokens_details": {"accepted_prediction_tokens": 3180, "audio_tokens": 0, "reasoning_tokens": 3257, "rejected_prediction_tokens": 5283}}. Logged in results/api_usage_log.jsonl (purpose sparkopen_validation_forced).

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

## Spark Open reply (verbatim)

Verdict per claim — arithmetic checked from per-prompt data:

**CLAIM 1: SUPPORTED. Source: `results/skill_demo.json` — corroborated as unforced reference in `results/skill_demo_forced.json`.**
Per-prompt recalc:
* base: 10x `failed` = 0/0/10 correct.
* base+rank-32: 1x `clean` (`book`), 9x `failed` = 1/0/9 correct.
* base+full delta: `clean` x8 (`product,company,book,sports,recipe,weather,job,model`), `partial` x1 (`person`), `failed` x1 (`event`) = 8/1/1 correct.

**CLAIM 2: SUPPORTED. Source: `results/skill_demo_forced.json`.**
Forced token = fine-tune's own first generated token per prompt, verified `matches_recorded_answer_prefix=True` 10/10 in same file (`{\n` or ` {\n`):
* base forced: `clean` x7 (`person,product,event,book,sports,weather,job`), `partial` x1 (`company`), `failed` x2 (`recipe,model`) = 7/1/2 correct.
* base+rank-32 forced: `clean` x8 (`product,company,book,sports,recipe,weather,job,model`), `partial` x1 (`person`), `failed` x1 (`event`) = 8/1/1 correct.
Second sentence correct: forced patch 8/1/1 exactly equals full fine-tune unforced 8/1/1 from Claim 1.

**CLAIM 3: SUPPORTED. Source: `results/skill_demo_recipe.json`.**
Means recomputed from `per-prompt margins`:
* base sum -63.3197/10 = -6.33197 => -6.332 correct, rounded -6.33.
* rank32 sum -12.9422/10 = -1.29422 => -1.2942 correct, rounded -1.29.
* full sum 46.0053/10 = 4.60053 => +4.6005 correct, rounded +4.60.

**CLAIM 4 — interpretation: Factual part SUPPORTED, interpretive framing TOO STRONG as written for general use. Source for factual part: `results/skill_demo_forced.json` vs `results/skill_demo.json`.**

The factual sub-claim inside it — patch forced 8 clean +1 partial matching fine-tune unforced 8/1/1 — is correct.

The interpretive gloss *"most of the extraction skill was already in the base, what the fine-tune mainly installs is the decision to start ... the gate is the main story"* is directionally supported *for this narrow test* by:
base unforced 0/0/10 -> base forced 7/1/2,
and margins base -6.33 vs full +4.60, rank32 -1.29 — huge gap in start propensity.

But as a general claim it is too strong without qualification for n=10 prompts, 1 skill (JSON template filling), 1 model pair (Qwen2.5-0.5B / NuExtract-1.5-tiny), greedy decoding, and with a head-to-head confound: you are comparing *forced* patch to *unforced* fine-tune. Base forced still trails by 1 clean / 1 fail, and patch mean margin remains negative (-1.29) vs full +4.60 — so patch does not fully recover the gate, and there is a small but real continuation edge beyond trigger that this n cannot quantify precisely.

**Does the control now settle the earlier missing-control objection?**

Yes, in the specific sense raised by Muse Spark. The objection was *UNPROVEN for lack of forced-start control*. That control has now been run (`results/skill_demo_forced.json`, 10/10 verified prefix tokens, greedy continuation) and measured.

It moves the "knowledge transfers, only the trigger does not" hypothesis from unproven to provisionally supported *in this setting*: base alone can continue 7/10 cleanly when given the starter. It does not prove generality, and it does not show base = fine-tune; the small 7/1/2 vs 8/1/1 gap and the -6.33 vs +4.60 margin gap remain.

**Required replacement wording if used in docs:**

> Replace with: "On this 10-prompt structured-extraction test (Qwen2.5-0.5B base vs NuExtract-1.5-tiny, greedy decoding), the base fails all 10 unforced but completes 7/10 cleanly and 1 partly when force-started with the fine-tune's first token; the rank-32 patch force-started matches the fine-tune's unforced score at 8/1/1. Mean first-token margin for the fine-tune's starter is -6.33 base, -1.29 patch, +4.60 fine-tune. Within this narrow setting this suggests continuation is largely latent in the base and the main learned change is propensity to start, plus a small additional continuation gain; broader generalization requires more skills, models and prompts."
