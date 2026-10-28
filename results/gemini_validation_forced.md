# Gemini validation: force-start control test (2026-10-28)

Google Gemini (gemini-3.5-flash-lite, via the custom.google-gemini connector) independently checked the force-start control test claims, with the same per-prompt evidence extract the other validators received.

- Verdicts: claims 1 to 3 SUPPORTED (arithmetic verified against the per-prompt records); claim 4 (interpretation) ruled FAIR, no wording change required; the earlier missing-control objection is settled. Gemini claimed no discrepancy, so there was nothing to recompute on its side. (One prose slip in its reply, "7/1/10" for the forced base, contradicts its own correct counts elsewhere in the same reply; the recorded counts are 7/1/2.)
- Tokens: 1,785 prompt / 655 completion / 2,440 total. Logged in results/api_usage_log.jsonl (purpose gemini_validation_forced).

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

## Gemini reply (verbatim)

### Verdicts on Claims

**CLAIM 1: SUPPORTED**
* **Source:** `results/skill_demo.json` (also referenced in `results/skill_demo_forced.json`).
* **Verification:** Arithmetic check matches recorded counts: base is 0/0/10, base + rank-32 patch is 1/0/9 (`book` is clean), and full fine-tune weights is 8/1/1 (`person` is partial, `event` is failed, rest are clean).

**CLAIM 2: SUPPORTED**
* **Source:** `results/skill_demo_forced.json`.
* **Verification:** Forcing the first token (all 10 verified as prefixes) yields: base forced = 7/1/2; base + rank-32 patch forced = 8/1/1 (`person` is partial, `event` is failed, rest are clean/partial matching fine-tune counts). The forced patch counts (8/1/1) exactly equal the full fine-tune's unforced counts (8/1/1).

**CLAIM 3: SUPPORTED**
* **Source:** `results/skill_demo_recipe.json`.
* **Verification:** Mean margins (fine-tune logprob minus end-of-text logprob) are: base `-6.332` (rounds to `-6.33`), rank-32 patch `-1.2942` (rounds to `-1.29`), and full fine-tune `+4.6005` (rounds to `+4.60`). Arithmetic checks out.

**CLAIM 4: FAIR (SUPPORTED)**
* **Assessment:** The interpretation is fair and appropriately modest given the data ($n = 10$). It accurately reflects the stark contrast between the base model's unforced performance (0/10) and its forced-start performance (7/1/10), proving that the base already possesses the extraction capability and primarily lacks the conversational/structural initiation gate. The patch provides a small additional bridge (raising clean extractions from 7 to 8, matching the full fine-tune), which justifies the nuance that the gate is the main story with a minor real edge beyond it. No wording change is required.

---

### Does the control test settle the earlier missing-control objection?

**Yes.** Muse Spark's objection was that claiming "the knowledge transfers, only the trigger does not" was unproven because no one had tested whether the plain base model could complete the structured extraction task if simply forced to output the correct starting token. 

The forced-start control test (`results/skill_demo_forced.json`) decisively answers this: the plain base model, when given the correct first token, successfully completes the extraction 7 times cleanly and 1 time partially (7/1/2 total). This proves that the underlying domain knowledge and format-following mechanics were already resident in the base model weights, and the fine-tune's primary behavioral contribution is indeed the trigger/gate to start.
