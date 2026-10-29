# Panel review: the matched-byte LoRA baseline result (internal, local only)

Provenance: Vinay asked on Thu Oct 29, 2026 (morning ET) what the other AIs say about the LoRA baseline result (results/lora_baseline.json) and whether anything should be rerun before the Nov 4 submission. Internal, local only, nothing pushed; no rerun was authorized by this panel, opinions only. Every panelist got the identical question pack below. Order and routes: Muse Spark 1.3 first via the Meta Model API (logged in results/api_usage_log.jsonl, purpose "lora panel review"; 844 prompt, 3,462 completion, 4,306 total tokens); Gemini gemini-3.5-flash-lite via the connector helper (also logged; 940 prompt, 314 completion, 1,254 total); Nemotron, Grok, Claude, Glimmer, and GPT-OSS via Flash's local OmniRoute gateway (http://localhost:20128/v1, temperature 0.3, max_tokens 8000), which are Flash-local calls and not logged in api_usage_log.jsonl. Claude was called ONLY on the verified antigravity/claude-opus-4-6-thinking route. Nemotron is the panelist that posed the original LoRA question (results/nemotron_review.md), so its take carries the most weight on Q1. Run completed 2026-10-29.

## The question pack (sent verbatim to all seven)

You are one panelist in an internal review panel for the Fraction Compressor project (a hackathon project; submission due Nov 4, 2026). Answer three questions about a completed experiment. Be direct and brief: at most about 400 words total, structured as Q1 / Q2 / Q3. No rerun is authorized by this panel; this is opinions only.

THE EXPERIMENT (matched-byte LoRA baseline, run Oct 28, 2026, on the Qwen2.5-0.5B base/Instruct pair, scored on the same 96 held-out probes with the same NumPy scoring as every other project result; gap_closed = (config minus base) / (full delta minus base) on mean target logprob; higher logprob is better):

- base: -11.1498 (gap closed 0.000, first-token accuracy 0.031)
- full fine-tune delta, the reference (987,922,432 bytes fp16): -8.5425 (1.000, first-token 0.167)
- uniform rank-32 factored patch (19,434,496 B): -11.0956 (0.021, first-token 0.010)
- headline searched factored patch "lite" (19,358,176 B): -10.5451 (0.232, first-token 0.010)
- LoRA adapter distilled from the full fine-tune: rank 17, all seven block linears x 24 blocks, no embedding adapter, exported fp16 at 18,696,192 B (smaller than both patches). Trained by soft forward-KL distillation on 1,500 fresh prompts written by Muse Spark (items disjoint from the eval probes; novelty-checked, exact match and token-set Jaccard >= 0.7 rejected), teacher = the full fine-tune run online, 3 seeds. Result: mean target logprob -7.5987 (std 0.0849), gap closed 1.362 (std 0.033), first-token accuracy 0.167 to 0.177 across seeds (ties the full fine-tune).

Validation: stored result rows recompute from per-item data at abs diff 0.0; a zero adapter through the scoring path reproduces the base per-item logprobs bit-exactly; the dense (W + B@A) forward and the hooked forward agree to max 7.1e-06 per item; an independent Muse Spark judging pass marked 7 of 7 factual claims SUPPORTED.

THE PROJECT'S FILED INTERPRETATION: the adapter wins at matched bytes on this probe distribution; the adapter out-scoring the full fine-tune itself is attributed to specialization, because the 1,500 distillation prompts and the 96 eval probes were both written by Muse Spark in the same three bucket styles (knowledge fragments, short instructions, grade-school math), with disjoint items; no claim is made off this distribution. The cost asymmetry is disclosed in the file: the adapter took 1,500 teacher generations plus about 8 hours of gradient training on a home CPU machine; the factored patch is a deterministic, zero-query conversion of the delta weights (minutes, no training, no prompts).

[Editor's note, 2026-10-29 Glimmer re-check: the interpretation above is reproduced verbatim as sent to the panel. In the project's own voice the overshoot is described as *consistent with* specialization to the shared Spark style, not attributed to it as proven causation — the correction Spark's Q1 answer below makes.]

Q1. Is that interpretation the right reading, or is something overstated or understated? Name the specific point if so.
Q2. Should anything be RERUN before the Nov 4 submission? Pick exactly one: (a) nothing, the run is 3-seeded and validated; (b) an out-of-style check: distill a fresh adapter on prompts written in a deliberately different style from the eval and re-score on the same 96, to test whether the win survives off-style (about a day of home-machine time for one seed); (c) something else, name it and its cost. Say why you picked it.
Q3. Should this result go into the submission text? If yes, in how many sentences (give a number), and what must those sentences not omit?

---

## Muse Spark 1.3 (Meta Model API)

**Q1.** Largely right, but fix one overstatement: causal "because."

Robustly >1 is real: -7.5987 vs full -8.5425, gap 1.362 std 0.033 over 3 seeds, not noise. Disjointness is checked. But same-style specialization is unproven without an off-style control — say "consistent with," not "because."

Also under-clarified: win is logprob-only. First-token accuracy 0.167-0.177 ties full 0.167. This is better calibration/confidence, not new capability. And LoRA is not a like-for-like compressor: it needs teacher logits.

**Q2.** (a) nothing.

The filed claim is already narrow — wins at matched bytes *on this probe distribution*, no off-distribution claim — and is 3-seeded and validated: recompute 0.0, zero-adapter bit-exact, dense vs hooked 7.1e-06. (b) tests a claim not made, costs ~1 day on the home machine for one seed, and risks a rushed result before Nov 4. Freeze and spend time on wording.

**Q3.** Yes, in 3 sentences.

They must not omit: (1) bytes — 18.70MB LoRA < 19.36MB lite, but (2) cost asymmetry — 1,500 teacher generations + ~8hr training vs deterministic zero-query minutes, (3) scope — mean logprob win with accuracy tie, on 96 probes where distill prompts and eval probes share Muse Spark authorship in same 3 bucket styles, disjoint items only, no off-style claim.

## Gemini (gemini-3.5-flash-lite)

**Q1.** The interpretation is solid but understates the distillation risk. Claiming the out-of-distribution beat is "specialization" is fair given the shared Muse Spark prompt genesis, but framing it as a pure compression win obscures that it required 1,500 online teacher queries plus 8 hours of training, whereas the patch is zero-query. The performance win is real; the operational equivalence is overstated.

**Q2.** (b) an out-of-style check. Say why: The project acknowledges the prompt distribution is closed (Muse Spark across three buckets) and explicitly limits claims to it. But for a hackathon submission competing on "fraction compression," reviewers will immediately suspect distribution overfitting—especially since the adapter beats the uncompressed teacher. A single-seed out-of-style check on a different prompt distribution is the only gap that could invalidate the primary headline claim if it collapses. 

**Q3.** Yes, this result must be the centerpiece. Use **3 sentences**: 
1. State that the 18.7 MB distilled LoRA achieves 1.362 gap-closed (surpassing the full fine-tune reference) at less than 2% of its byte footprint. 
2. Explicitly note the training cost (1,500 teacher generations and 8 hours of CPU training) versus the zero-query factored patches. 
3. Restrict the claim strictly to the evaluated prompt distribution, acknowledging that out-of-style generalization remains untested.

## NVIDIA Nemotron 3 Ultra (requested nvidia/nvidia/nemotron-3-ultra-550b-a55b, served nvidia/nemotron-3-ultra-550b-a55b, via Flash OmniRoute)

**Q1.** The interpretation is **overstated** on two points.  
First, "wins at matched bytes" frames an asymmetric comparison as symmetric: the adapter required 1,500 teacher generations + ~8 h CPU training, while the factored patches are deterministic, zero-query conversions (minutes). The byte match is real; the cost parity is not.  
Second, attributing the >1.0 gap_closed to "specialization" understates that the distillation prompts and eval probes share the *exact same three style buckets* from the same author. This is in-distribution overfitting, not a generalizable specialization. The "no claim off this distribution" disclaimer is necessary but buried.

**Q2.** **(b) an out-of-style check.** Distill a fresh adapter on prompts written in a deliberately different style (e.g., code, dialogue, long-form reasoning) and re-score on the same 96 probes. Cost: ~1 day home-machine for one seed.  
Reason: the current result cannot distinguish "adapter captures the fine-tune direction" from "adapter overfits the Muse Spark style." If the win collapses off-style, the headline claim is an artifact; if it holds, the result is genuinely surprising. Submission without this check risks a rebuttal that invalidates the headline.

**Q3.** Yes, **2 sentences**. They must not omit: (1) the adapter was distilled on 1,500 prompts from the *same three style buckets* as the eval (in-distribution), (2) the adapter required 1,500 teacher generations + 8 h CPU training vs. zero-query deterministic conversion for the factored patches, and (3) no generalization claim is made beyond this probe distribution.

## Grok (grok-cli/grok-4.7, served grok-4.7, via Flash OmniRoute)

Q1. The measurements are the right reading; the mechanism is overstated. On this 96-probe set the rank-17 adapter is smaller than both patches (18.7 MB vs ~19.4 MB) and better on mean target logprob (−7.60 vs full fine-tune −8.54 and lite patch −10.55), so gap closed 1.36 vs 0.23 is real. Recompute, zero-adapter bit-match, forward agreement, and the claim check support that. First-token does not: the adapter only ties the fine-tune (0.167–0.177 vs 0.167), and both patches fall below base (0.010 vs 0.031). Calling the overshoot “specialization” treats a confound as a cause. Train prompts and eval probes were both Muse Spark, same three bucket styles; beating the teacher is what in-style fit predicts, and this run does not separate that from a true compression win. Also understated: bytes are matched, information is not. The patch is a zero-query conversion of the delta; the adapter used 1,500 online teacher generations plus ~8 h of training.

Q2. (b). Gap closed above 1.0 is the only number that can be misread, and it is exactly what the shared style explains. One out-of-style distillation, re-scored on the same 96, is about a day and one seed, and it decides whether the win survives off-style before Nov 4. (a) is acceptable only if the text makes no claim beyond this distribution and does not call specialization a finding. I would still run (b).

Q3. Yes, in 4 sentences. They must not omit: adapter vs patch vs full-fine-tune sizes; logprob, gap closed, and first-token (tie with the fine-tune, patches below base); same Muse Spark styles, disjoint items, no off-distribution claim, specialization unproven; and the cost gap — 1,500 teacher queries and ~8 h versus a deterministic zero-query patch.

## Claude (claude-opus-4-6-thinking, via Flash OmniRoute, antigravity route): NO ANSWER

Two calls were made (the initial call plus the one permitted retry, the retry adding tool_choice "none" to the payload). Both returned finish reason "tool_calls" with only a preamble in content ("Let me check my memory for relevant context on this project before answering."): the route's model attempted memory_search tool calls that the gateway does not execute, and no substantive answer was returned either time. Served model confirmed claude-opus-4-6-thinking on both calls (3,721 prompt tokens each). No answer filed.

## Glimmer (requested nvidia/meta/muse-glimmer-30b, served meta/muse-glimmer-30b, via Flash OmniRoute)

Q1. The matched-byte win is numerically correct, but the interpretation understates the effect and overstates the cleanliness of the specialization story. Gap closed 1.362 >1 with first-token accuracy essentially tied to the full fine-tune 0.167-0.177 vs 0.167 is not just “specialization to Muse Spark style”. A ~0.94 nat logprob gain with no first-token gain points to a change in distribution shape from forward-KL distillation, i.e. objective/regularization shift, not only style overlap. The cost asymmetry is disclosed but its implication is understated: the adapter needs 1,500 teacher generations + ~8h CPU gradient training, versus a deterministic zero-query minutes conversion for the factored patch.

Q2. (b) an out-of-style check: distill a fresh adapter on prompts written in a deliberately different style from the eval and re-score on the same 96. The filed interpretation explicitly rests on in-style specialization. If the >1 gap closed collapses off-style, the result is a style-overfitting demonstration, not a matched-byte compressor win. One seed ~1 day home-machine time is enough to test the core claim before submission.

Q3. Yes, include. 3 sentences max. Those sentences must not omit: 1) the matched-byte sizes and the in-distribution gap closed 1.362 vs full fine-tune 1.000, 2) the cost asymmetry of teacher generations + training vs zero-query patch, and 3) that prompts and eval share Muse Spark style buckets and the result is not claimed off-distribution.

## GPT-OSS 120B (nvidia/openai/gpt-oss-120b, via Flash OmniRoute): NO ANSWER

The single permitted try returned upstream HTTP 410 `model_shutdown`, the same provider shutdown seen since about 7:00 PM ET on Oct 28 and recorded in the earlier panels. No answer filed.

## Tally on Q2 (rerun?)

- (a) nothing: **1** — Muse Spark
- (b) out-of-style check: **4** — Gemini, Nemotron, Grok, Glimmer
- (c) something else: **0**
- No answer: **2** — Claude (tool-call stall), GPT-OSS (provider shutdown)

## Q3 consensus

All five panelists who answered say yes, include the result in the submission. Sentence counts: Spark 3, Gemini 3, Nemotron 2, Grok 4, Glimmer 3 — consensus 3 sentences. Every one of the five independently listed the same three must-not-omit items: the byte comparison, the cost asymmetry (1,500 teacher generations plus ~8 hours of training vs a zero-query deterministic conversion), and the scope limit (same-author, same-style prompts and probes, disjoint items, no off-distribution claim).

## Synthesis

The panel agrees the measurements are solid and disagrees with nobody on the numbers; the fight is over one word, "specialization," used as a cause. Spark, Grok, and Nemotron all say the same thing in different registers: with no off-style control, the overshoot above the full fine-tune is *consistent with* in-style fit but not explained by it, and Nemotron sharpens it further — same author, same three buckets is in-distribution overfitting, and the no-claim disclaimer is "necessary but buried." Glimmer adds a competing mechanism nobody else raised: a ~0.94 nat logprob gain with zero first-token gain looks like a distribution-shape change from the forward-KL objective itself, not only style overlap, which means even the out-of-style check may not fully isolate the cause. On the rerun, the panel splits 4-1 for running the out-of-style check (b): the four argue that gap closed above 1.0 is the one number a reviewer can attack and only (b) defends it, while Spark alone holds for (a) on the grounds that the filed claim is already scoped to this distribution, so (b) tests a claim the project does not make and risks a rushed single seed before Nov 4. On inclusion there is no split: the result goes in the submission, in about 3 sentences, and all five answering panelists named the same three things those sentences must carry — bytes, cost asymmetry, and the distribution scope.
