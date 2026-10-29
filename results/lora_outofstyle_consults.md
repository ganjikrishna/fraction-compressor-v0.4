# Out-of-style LoRA control: Phase 1 design consults (verbatim)

Date: Thu Oct 29, 2026. The draft control design (Gemini-authored prompts, different surface style, identical teacher/recipe, one seed, same untouched Spark-96, plus a first-token vs continuation split) was put to four consultants BEFORE the design was frozen, per Vinay's instruction ("Check with other ai before doing it and take there input") and his standing builds rule. The frozen design and what was folded in from each consult: results/lora_outofstyle_design.md.

Routes: Muse Spark 1.3 via the Meta Model API (3,018 total tokens; logged in results/api_usage_log.jsonl, purpose lora_outofstyle_design_consult_spark); Gemini gemini-3.5-flash-lite via the connector (1,150 total tokens; purpose lora_outofstyle_design_consult_gemini); Nemotron 3 Ultra and Glimmer via Flash OmniRoute (Flash-local calls, not in the API log).

Note: the VM /tmp copies of the Spark and Gemini replies were lost to a tmp cleanup during the run; the two texts below are transcribed from the session record of the same calls. The Nemotron and Glimmer texts are from the response files preserved on Flash.

## Muse Spark 1.3 (Meta Model API)

1. Does it isolate style? Only partially.

It breaks the same-author confound, holds buckets, teacher, recipe, and eval fixed — necessary. It does not isolate *style* because you vary prompt style and simultaneously shift: a) train-test match, b) teacher answer distribution. A drop on Spark-96 alone proves distribution sensitivity, not style specialization.

2. What breaks it:

- Asymmetric eval: testing only on Spark-96 favors the in-style adapter by construction. Any generic shift — length, format, vocab — predicts a drop. No 2x2, no interaction claim.
- Teacher degradation confound: teacher is the same full fine-tune distilled on Spark-1500. Queried with Gemini phrasing it may be less accurate / confident. Student then gets noisier, longer, higher-entropy targets under your 48-token greedy cap. You're comparing clean in-distribution targets vs off-distribution targets, not just prompt style.
- KL-mass shift: varied length/format = different tokens-per-example under soft KL at answer positions. Same 1,014 steps, batch 8 is not the same effective token budget.
- N=1 seed: in-style 1.362 ±0.033, n=3. One draw at seed 20261028 cannot separate a true collapse toward patch 0.232 from seed luck / underfit on more variable Gemini data with fixed rank-17, lr 2e-4.
- Unfrozen rule + unmeasured style: "beats clearly / collapses toward" is not numeric. "No template overlap" and Jaccard <0.7 don't quantify style distance or rule out paraphrase leak.

First-token vs continuation split is good but won't save the above.

3. Change before freezing — keep the one training run, add mirrored scoring:

Freeze a 2x2: score stored in-style adapter and new out-of-style adapter on both Spark-96 AND a disjoint Gemini-96 built with the same Gemini conventions. Pre-register: style hypothesis predicts crossover interaction, not just out-of-style < in-style on Spark-96. Also freeze numbers: e.g., still >0.6 closure = not-only-style; <0.4 = mostly style; in-between = inconclusive. Log mean answer length, teacher entropy/confidence for both 1500s to expose b/c.

Without that, a collapse is uninterpretable.

## Gemini (gemini-3.5-flash-lite)

Here is the pressure test for your control design:

**(1) Does this design actually isolate style?**
No, not cleanly. Changing the author to Gemini and varying surface forms breaks author/template overfitting, but it does *not* isolate style. The prompts still occupy the exact same semantic task distribution (knowledge fragments, direct commands, math word problems). You are testing *author and template robustness*, not style independence.

**(2) What breaks it (confounds & failure modes):**
*   **Semantic Domain Confound:** The content buckets remain identical. If the model learned domain priors rather than Muse Spark's literal syntax, the out-of-style adapter will still outperform the factored patch. 
*   **Single-Seed Vulnerability:** Running only one seed (20261028) for the control risks mistaking seed-specific optimization noise for a structural shift.
*   **Gemini Style Leakage:** Unless heavily filtered, Gemini has its own distinctive stylistic footprint (e.g., overly polite framing, structured bullets) which the LoRA may simply learn as a *new* style rather than being style-agnostic.

**(3) Changes to make before freezing:**
*   **Add a true out-of-domain bucket:** Keep the three Gemini buckets, but add a 4th "zero-overlap" bucket (e.g., creative writing or python code snippets) not present in the eval probes. If the adapter still wins here, you've actually disproven the pure-style hypothesis.
*   **Run 3 seeds:** Drop the single-seed constraint and run at least 3 seeds. Given your tight std (0.033), variance will dictate whether the drop from in-style to out-of-style is meaningful or noise.

## NVIDIA Nemotron 3 Ultra (via Flash OmniRoute; served nvidia/nemotron-3-ultra-550b-a55b; 1,411 total tokens)

**(1) Does it isolate style?**
No. It isolates *author identity* and *surface phrasing conventions*, but not *style* as a latent distribution. The teacher model (full FT) was trained on Spark data. Its output distribution on Gemini prompts is still conditioned on Spark-style weights. You are distilling the teacher’s *out-of-distribution behavior*, not a style-agnostic capability. If the adapter wins, it proves the adapter captures the teacher’s OOD generalization, not that the original win was style-independent.

**(2) Specific confounds / failure modes**
*   **Teacher Style Leakage (Critical):** The teacher *is* the Spark fine-tune. Its generations on Gemini prompts will likely retain Spark-isms (verbosity, formatting tics, token preferences). The adapter learns to mimic *those* tics. The eval probes (Spark-authored) match the teacher’s tics, not the Gemini prompts. The adapter wins because it mimics the teacher’s "Spark accent" better than the patch, not because it learned style-invariant reasoning.
*   **Bucket ≠ Style:** "Knowledge/Instruction/Math" are task buckets. Style is token-level distribution (length, hedging, formatting, punctuation). Gemini prompts varying length/format within buckets does not guarantee the *teacher’s responses* shift distribution away from Spark-eval space.
*   **Single Seed Variance:** In-style std=0.033 on a 1.36 gap. A single seed (20261028) has ~10% chance of flipping the "beats patch" conclusion by noise alone.
*   **KL Objective Mismatch:** Forward KL on teacher answers forces mode-covering. If teacher is peaky (Spark style), adapter learns peaks. If teacher is flat (OOD confusion), adapter learns flatness. Score changes reflect teacher entropy shifts, not student capability.

**(3) Change before freeze**
**Swap the Teacher.** Use the *Base* model (or a style-neutral FT) to generate targets for the Gemini prompts. Distill *from Base on Gemini prompts* into the Adapter. Compare that Adapter vs. In-Style Adapter on Spark Eval.
*   *If Base->Gemini Adapter beats Patch:* Capability transfers style-agnostically.
*   *If Spark-FT->Gemini Adapter wins but Base->Gemini loses:* Original win was style mimicry.
*   *Current design cannot distinguish these.*

## Glimmer (via Flash OmniRoute; served meta/muse-glimmer-30b; 1,927 total tokens)

The design breaks the same-author confound but does not cleanly isolate style.

1. Isolation. Changing author from Spark to Gemini and varying surface phrasing/length/format does remove shared author priors and template overlap with the 96 Spark probes. That is progress. It does not isolate style alone: content buckets are identical, so topic semantics, task format and the teacher’s exposure remain shared. You are testing author+style+prompt-distribution shift together, not style in isolation.

2. What breaks it.
* Single seed. In-style result is 3 seeds std 0.033. One seed 20261028 for out-of-style invites seed luck and makes the pre-registered interpretation rule fragile.
* Teacher capability shift. The teacher is a Spark-style fine-tune. Its greedy outputs on Gemini prompts are likely worse/more generic than on Spark prompts. Distillation then targets a degraded teacher, so collapse could be teacher mismatch not style mismatch.
* Difficulty/lexical confound. “Different phrasing conventions, varied length and format” changes prompt length, lexical diversity and likely difficulty per bucket. Novelty hygiene is only exact match / token-set Jaccard >=0.7, no semantic or length matching. A score change can be difficulty, not style.
* Residual content overlap. Same three buckets means semantic overlap remains; you have not shown the train/eval prompt embedding distributions are comparable.
* No style quantification. You change style by fiat, with no measured style distance between Gemini train and Spark eval, so you cannot calibrate how much style was actually moved.

Failure mode: out-of-style adapter underperforms because distillation signal is noisy/weak from a mismatched teacher on harder prompts, not because style specialization was the cause.

3. Change before freezing.
Run ≥3 seeds or at least bootstrap variance for the out-of-style adapter. Report teacher performance on Gemini prompts vs Spark prompts per bucket to quantify teacher degradation. Match prompt statistics per bucket: length, token count, and embedding similarity distribution to the in-style train set, and report them. Add a minimal author-swap control: Spark-authored prompts paraphrased to a different surface style, keeping author constant, to separate author vs style. Keep the first-token vs continuation split, but pre-register a quantitative decision threshold for “beats factored patch clearly”.

That makes the style claim falsifiable.

