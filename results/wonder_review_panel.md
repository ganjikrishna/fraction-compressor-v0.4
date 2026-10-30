# Panel discussion: Wonder's review of Fraction Compressor (internal, local only)

Provenance: Vinay asked on Fri Oct 30, 2026, after Muse Wonder's first project review (results/wonder_review.md): "talk to other agents and add wonder to that panel." Wonder is now a standing panel member (recorded in MEMORY.md). Each panelist received Wonder's verdict, its five new points (N1-N5), and its eight pre-submission recommendations (R1-R8), plus a project-facts pack including the current state of the texts (README and submission draft already carry the lossy/23.2%/first-token/LoRA disclosures; the demo video is finished and its links are Nov 2 go-live placeholders by plan). Voters: Muse Spark 1.3 (Meta Model API), Muse Spark Open (Baseten), Gemini gemini-3.5-flash-lite, Nemotron 3 Ultra, Glimmer, Grok, Claude (antigravity/claude-opus-4-6-thinking route only; served model claude-opus-4-6-thinking confirmed). GPT-OSS returned HTTP 410 model_shutdown again (openai/gpt-oss-120b via Flash OmniRoute), its standing failure since Oct 28: NO ANSWER, recorded, not counted. Glimmer's served-model field confirmed meta/muse-glimmer-30b. Wonder did not vote on its own review; it received the converged conclusion at the end and replied in one paragraph (verbatim at the end). Nothing pushed, nothing posted.

## Plain-words summary

**On Wonder's five new points, the panel sides with Wonder almost completely.** N1 (missing training-free SVD/low-rank baselines at 19 MB; "owns the region" unproven) agreed 7-0. N3 (a weight delta does not swap tokenizer, chat template, or generation config, so "swap a file, swap the behavior" overclaims) agreed 7-0. N5 (the rigor stack verifies arithmetic and file consistency, not benchmark validity, leakage, or statistical robustness) agreed 7-0, with Grok disputing only the "audit theater" motive wording. N2 (byte-unfair search winners exceeding the hard budget by 11.8% to 38% undercut the exact-byte-accounting claim) agreed 6-1; Grok dissents, saying the overrun figures are unverified and the submitted artifact already leads with the byte-fair recipe. N4 (no confidence intervals; headline 23.2% is a bare point estimate on an unstable metric) agreed 6-1; Claude dissents, saying the >1.0 cases are already disclosed anomalies and the real problem is sample size, not missing error bars.

**On the recommendations, the panel adopts the substance with deadline realism.** Unanimous adopts: R3 (one compact per-pair results table in the submission text) and R7 (one-sentence new-work boundary, Oct 26-Nov 2 vs v0.1-v0.3). Adopted-modified: R4 (delete "owns the region / only one that exists" NOW, replaced by "fits below BitDelta's floor; superiority over other training-free low-rank formats was not established"; the SVD baseline run is a stretch goal, not a blocker; Claude alone would attempt the run before settling for wording), R5 (Spark downgraded to recipe search + claim-checking workflow; one-sentence disclosure that Spark generated the held-out questions; quantum audit and Gemini arithmetic leave the main pitch, a one-line repo pointer acceptable), R2 (opening carries the defensible claim and the LoRA defeat, BitDelta crossover, and first-token failure sit in the first third; no wholesale rewrite, most panelists noting the disclosures already exist), R6 (side-by-side base/full/patch including a first-token-gate failure in the submission TEXT; swap times labeled file-load time on the demo machine; narration discussion out of the form; the finished video is NOT reshot), R1 (live YouTube/X links verified at submission on Nov 2, already the plan; not a blocker before then). R8 (reposition as diagnostic/research prototype) is NOT adopted as the plan: 3 adopt, 1 adopt-modified (Grok, who wants repositioning now), 3 reject. Because the panel judges R1-R7 feasible before Nov 2, R8 stays a contingency only.

**Where the panel says Wonder was wrong:** (1) "No confidence intervals anywhere" is false: the LoRA result is reported as 1.362 +/- 0.033 across 3 seeds (Spark, Spark Open, Grok; the headline 0.232 indeed has none). (2) R1 and R2 partly demand what already exists: a finished video awaiting its planned Nov 2 posting, and honesty paragraphs already in the README and draft next to the size claim (Spark, Spark Open, Grok, Gemini). (3) The verdict's framing: Claude calls it a straw man (it judges a training-free tool against the assumption training is always possible), Spark calls the LoRA comparison a category error across different constraints, and Grok notes the verdict omits the adapter's cost (1,500 teacher generations, ~8 h) and its out-of-style drop to 0.620. (4) Grok: "audit theater" imputes a motive; the damaging numbers are printed up front, so the failure is what was audited, not a cover-up. One factual slip on the panel's side: Claude's R6 line says the narration discussion is already absent from the submission draft; it is present (Wonder quoted it from the draft), so the R6 removal item is real.

**Wonder's closing position:** it accepts the converged result, withdraws "no confidence intervals anywhere" and the phrase "audit theater," and revises its verdict: the product case is undermined where training is feasible but remains open, though still unproven against the missing training-free baselines, where it is not. Full paragraph at the end of this file.

## Vote tallies

### New points (7 voters)
| Point | Agree | Disagree | Dissent |
|---|---|---|---|
| N1 missing training-free baselines at 19 MB | 7 | 0 | none |
| N2 byte-unfair winners vs byte-accounting claim | 6 | 1 | Grok |
| N3 patch does not swap tokenizer/template/config | 7 | 0 | none |
| N4 no confidence intervals / unstable headline metric | 6 | 1 | Claude |
| N5 rigor verifies arithmetic, not benchmark validity | 7 | 0 | none (Grok disputes the "audit theater" motive wording only) |

### Recommendations (7 voters)
| Rec | Adopt | Adopt-modified | Reject | Converged |
|---|---|---|---|---|
| R1 fill live links before submitting | 3 | 2 | 2 | Adopt-modified: verify at Nov 2 submission, not a blocker before |
| R2 rewrite opening, defeats into first third | 1 | 5 | 1 | Adopt-modified |
| R3 compact per-pair results table | 7 | 0 | 0 | Adopt |
| R4 run SVD baseline or delete "owns the region" | 2 | 5 | 0 | Adopt-modified: wording now, baseline stretch only |
| R5 downgrade Spark judging claim + disclose question generation | 5 | 2 | 0 | Adopt |
| R6 reframe demo, label swap time, drop narration from form | 4 | 3 | 0 | Adopt-modified: in the text, no video reshoot |
| R7 one-sentence new-work boundary | 7 | 0 | 0 | Adopt |
| R8 fallback repositioning as diagnostic prototype | 3 | 1 | 3 | Not adopted as the plan; contingency only (Grok dissents, wants it now) |

## Converged change list for Nov 2
1. Add the compact per-pair results table (base/full/uniform/winner, log score AND first-token accuracy, bytes; flag the >100% pairs and the 1.5B heldout24 reversal). (R3, unanimous)
2. Add the one-sentence new-work boundary: Oct 26-Nov 2 work vs inherited v0.1-v0.3. (R7, unanimous)
3. Delete "owns the region / only one that exists"; replace with "fits below BitDelta's floor; superiority over other training-free low-rank formats was not established." SVD/Delta-CoMe baseline at ~19 MB only as a stretch attempt if time remains. (R4-modified)
4. Downgrade the Spark judging claim to recipe search + claim-checking workflow; add the one-sentence disclosure that Spark generated the held-out questions; quantum audit and Gemini arithmetic leave the main pitch (one-line repo pointer acceptable). (R5)
5. Submission opening: first sentence carries the defensible claim ("training-free, lossy delta-distribution experiment"); LoRA defeat, BitDelta crossover, first-token failure confirmed in the first third. Verify placement rather than rewriting wholesale. (R2-modified)
6. In the submission text: base vs full vs patch shown side by side including a first-token-gate failure; swap times labeled file-load time on the demo machine; narration discussion removed from the form. No video reshoot. (R6-modified)
7. Nov 2 go-live checklist: post video and X post, insert links, verify both resolve before submitting. (R1-modified)
8. No repositioning. R8 stays on record as a contingency only. (Grok dissenting)

## Compute and failures
- Spark 1.3 (Meta API): attempt 1 max_tokens 8000 returned finish_reason length with all 7,998 reasoning tokens and no content (9,506 total); attempt 2 at max_tokens 32000 answered (9,666 total). Both logged, purpose "wonder review panel."
- Spark Open (Baseten): 7,346 total, answered first try. Logged.
- Gemini (gemini-3.5-flash-lite): 2,174 total, answered first try. Logged.
- Flash OmniRoute (local, not in the hosted log): Nemotron 7,738 total; Glimmer 6,702 (served meta/muse-glimmer-30b); Grok 14,010; Claude attempt 1 returned a 131-char preamble stub (4,996 total), retry with an explicit no-tools instruction answered in full (6,092 total, served claude-opus-4-6-thinking).
- GPT-OSS (openai/gpt-oss-120b via OmniRoute): HTTP 410 model_shutdown, the same failure as every attempt since Oct 28. No answer.
- Wonder closing call (Meta API): 3,758 total, logged, purpose "wonder review panel."

## Panelist answer: Muse Spark 1.3 (Meta Model API)

N1: AGREE - No ~19 MB truncated-SVD or Delta-CoMe baseline exists so below-62 MB fit does not prove best training-free occupant despite 43.6% vs 38.5% at 62 MB.
N2: AGREE - Three search winners exceeded the claimed hard budget by 11.8% to 38% so in-loop scoring failed exact byte accounting until byte-fair mlp_behemoth_lite took headline.
N3: AGREE - 19,358,176 B delta alone cannot swap tokenizer plus chat-template plus generation-config plus safety behavior so file-swap equals Instruct-product language is false.
N4: AGREE - Headline 0.232 gap-closed 23.2% carries no eval-n uncertainty despite >1.0 wins on two pairs and 1.5B reversal losing heldout24 and 26.0% vs 32.3% first-token.
N5: AGREE - 41 of 41 checks plus Gemini arithmetic plus quantum sampling verify file consistency not validity of 96 Spark-made questions with same-model judging and tiny-sample metric instability.
R1: REJECT - Finished 3-minute video with YouTube plus X placeholders pending scheduled Nov 2 posting is not missing work requiring submission block.
R2: REJECT - README plus draft already lead with training-free lossy 23.2% plus 0.010 vs base 0.031 vs full 0.167 plus LoRA 1.362 plus out-of-style 0.620 so demanded honesty rewrite exists.
R3: ADOPT - Single per-pair base slash full slash uniform slash winner log-score plus first-token plus bytes table exposing >100% pairs and 1.5B subset reversal fixes opacity before judging.
R4: ADOPT-MODIFIED - Replace owns-region wording with fits-below-BitDelta-floor superiority-over-low-rank-unproven and log ~19 MB SVD slash CoMe as future work because CPU rerun before Nov 2 is infeasible.
R5: ADOPT-MODIFIED - Keep explicit Spark recipe-search plus claim-check plus Gemini plus Glimmer Meta-tooling credit while adding one-sentence disclosure Spark made 96 held-out questions so not independent and moving quantum plus arithmetic to repo appendix.
R6: ADOPT-MODIFIED - Show base vs full vs patch side-by-side including first-token-gate failure and label 0.104 s slash 0.087 s as file-load on demo machine while compressing MMS slash voice narration to one tooling-credit line.
R7: ADOPT - One-sentence Oct 26-Nov 2 vs v0.1-v0.3 boundary for modules plus benchmarks plus results removes new-work disqualification risk at zero cost.
R8: REJECT - Diagnostic-only retreat concedes Impact 30% unnecessarily when zero-query deterministic 19,358,176 B vs 987,922,432 B sub-BitDelta niche survives honest 23.2% disclosure against 1500-generation plus 8h LoRA.
WRONG: N4 “nowhere” is false - LoRA has 1.362 +/-0.033 across 3 seeds; R1/R2 demand what already exists - finished video pending Nov 2 post and README/draft already lead with lossy 23.2% plus 0.010 below 0.031 plus LoRA/out-of-style; verdict commits category error - zero-query deterministic conversion vs 1500 generations plus ~8h training are different constraints, and below-62 MB is a proven fit-floor not proven dominance.
VERDICT: Adopt table plus wording plus disclosure plus boundary fixes and submit Nov 2 as honest training-free sub-BitDelta experiment - Wonder sharpens disclosure but does not warrant retreat to diagnostic-only.

## Panelist answer: Muse Spark Open (Baseten)

N1: AGREE - At ~19 MB no truncated-SVD, low-rank FP16 delta, or Delta-CoMe-style mixed-precision baseline exists, so "owns the region" conflates BitDelta's ~62 MB infeasibility with proven superiority.
N2: AGREE - Three search winners exceeded the advertised hard byte budget by 11.8% to 38%, proving in-loop scoring and harness did not enforce exact byte accounting until retroactive byte-fair variants were created.
N3: AGREE - A 19 MB weight delta alone does not swap tokenizer, chat template, generation/safety config, or base-version compatibility, so "swap a file, swap the behavior" materially overclaims product parity.
N4: AGREE - Headline 0.232 / 23.2% is a naked point estimate with no CI or significance despite pathologies requiring it: >1.0 gap-closed on two pairs, 1.5B heldout24 reversal, and first-token 26.0% vs uniform 32.3%.
N5: AGREE - Gemini arithmetic, 41/41 file checks, and quantum-audited sampling verify file-to-claim arithmetic consistency, not benchmark validity, code correctness, leakage, or robustness on n=96 Spark-generated same-model questions.
R1: ADOPT-MODIFIED - Do not block for draft placeholders since 3-min video is finished per facts; add Nov 2 go-live checklist to verify public YouTube/X URLs resolve before submitting.
R2: ADOPT-MODIFIED - Retain existing honesty paragraph next to size claim but rewrite opening sentence itself to "training-free lossy delta-distribution experiment closing 23.2% with first-token 0.010 below base 0.031" and ensure LoRA defeat 1.362 vs 0.232 (0.620 out-of-style) and BitDelta 43.6% vs 38.5% crossover are in first third.
R3: ADOPT - Add one compact per-pair table of base/full/uniform/winner on mean logprob AND first-token accuracy plus bytes, explicitly flagging >100% pairs and 1.5B subset reversal.
R4: ADOPT-MODIFIED - Immediately replace "only occupant/owns region" with "fits below BitDelta ~62 MB floor; superiority over other training-free low-rank formats at ~19 MB not established" and run SVD baseline only if trivial before deadline.
R5: ADOPT - Downgrade Spark from independent validator to in-loop recipe search plus claim-checking workflow, disclose in one sentence that Spark generated the 96 held-out questions, and move quantum audit/Gemini arithmetic to repo appendix.
R6: ADOPT - Show base vs full vs patch generations side-by-side including a first-token-gate failure, label 0.104s/0.087s as file-load time on stated demo hardware, and remove cloned-voice/MMS narration from submission form.
R7: ADOPT - Insert one explicit sentence stating which modules, benchmarks and results were created Oct 26-Nov 2 versus inherited from v0.1-v0.3 for new-work compliance.
R8: ADOPT - If R2-R7 cannot be completed before Nov 2, reposition entry as diagnostic/research prototype whose main finding is the first-token gate and floor effect, not an Impact-ready patch distribution system.
WRONG: Wonder treats placeholder links as missing demo work when facts state a finished 3-minute video exists and placeholders are intentional Nov 2 go-live; overstates "no CIs anywhere" - LoRA reports 1.362 +/-0.033 in-style and 0.620 out-of-style, though headline 0.232 indeed has none; understates that README/draft already carry byte-fair recipe and lossy/training-free/23.2%/first-token-below-base/LoRA comparison next to size claim per facts.
VERDICT: Wonder's one-line verdict stands and must change submission: no hard technical block on Nov 2, but Impact/Trust will fail unless R2-R7 wording downgrades, full table, and Spark/judging disclosure are applied - otherwise fallback to diagnostic prototype.

## Panelist answer: Gemini (gemini-3.5-flash-lite)

N1: AGREE - BitDelta's floor does not establish our format's supremacy over simple truncated SVD or low-rank FP16 deltas at the 19 MB mark.
N2: AGREE - Failing the hard byte-budget constraint during early search undermines the core architectural claim of exact byte-accounting.
N3: AGREE - Equating a weight delta swap to a full product swap ignores system-level dependencies like chat templates, tokenizers, and safety configurations.
N4: AGREE - Without variance metrics, confidence intervals, or significance tests, anomalous metric inversions render the headline 23.2% statistically uninterpretable.
N5: AGREE - Verifying arithmetic consistency is audit theater that does nothing to prove benchmark validity, prevent leakage, or ensure code correctness.

R1: ADOPT - All placeholder links must be replaced with live URLs before final submission to avoid instant disqualification.
R2: ADOPT-MODIFIED - Lead with the defensible framing, but keep the candid disclosures in the README and repo rather than burying them.
R3: ADOPT - A single compact results table explicitly exposing subset reversals and first-token failures is essential for transparent peer review.
R4: ADOPT - We must remove the "owns the region" hyperbole and explicitly concede that superiority over other training-free baselines was never tested.
R5: ADOPT - Demote Spark's role from independent validation to a recipe search tool and clearly disclose that it authored the held-out questions.
R6: ADOPT - Reframe the demo to showcase honest side-by-side generations and file-load swap times while purging the voice-narration fluff.
R7: ADOPT - Add a single boundary sentence cleanly separating the Oct 26-Nov 2 hackathon work from the inherited v0.1-v0.3 codebase.
R8: REJECT - Repositioning the entire entry as a diagnostic prototype at this late stage destroys our Impact score when our honest disclosures are already documented.

WRONG: Wonder claims the README and submission draft hide these flaws, but the project facts explicitly state that the lossy nature, LoRA defeat, first-token drop, and out-of-style control results are already fully disclosed in the text.

VERDICT: Wonder's review does not change our core Nov 2 plan because our drafts are already honest, but it forces us to scrub remaining marketing hyperbole (R4, R5) and add the missing summary table (R3) immediately.

## Panelist answer: Nemotron 3 Ultra (Flash OmniRoute)

N1: AGREE - The project compared against uniform quantization and BitDelta but not against truncated SVD, low-rank FP16 delta, or Delta-CoMe-style mixed precision at ~19 MB; "owns the region" overclaims without those baselines.

N2: AGREE - The need for a separate "byte-fair recipe" (mlp_behemoth_lite) after search winners exceeded budget by 11.8–38% confirms the hard constraint was not enforced in-loop, undermining the exact-byte-accounting claim.

N3: AGREE - A weight delta swaps only weights; it does not swap tokenizer, chat template, generation config, safety system behavior, or base-version compatibility, so "swap a file, swap the behavior" is technically false for Instruct patches applied to base models.

N4: AGREE - Gap-closed >1.0 on two pairs and subset reversals at 1.5B (heldout24 loss, first-token accuracy 26.0% vs uniform 32.3%) make the headline 23.2% unstable; no confidence intervals or significance tests are reported anywhere.

N5: AGREE - The 41/41 quantum audit, Gemini arithmetic recomputation, and judge file citations verify internal consistency and arithmetic, not benchmark validity, code correctness, leakage (Spark generated questions, designed recipes, and judged), or statistical robustness; the caveat volume reads as audit theater.

R1: ADOPT - Placeholders for the public demo video and X post must be replaced with live, verified links before submission; submitting broken links is avoidable unforced error.

R2: ADOPT-MODIFIED - Rewrite the opening to the defensible claim ("training-free, lossy delta-distribution experiment") and front-load the LoRA defeat, BitDelta crossover, and first-token failure; the README already has partial honesty but the submission draft must lead with it.

R3: ADOPT - A single compact table (per pair: base/full/uniform/winner on log score and first-token accuracy, plus bytes, with 1.5B subset reversal and >100% pairs noted) would make the mixed results transparent and defensible.

R4: ADOPT-MODIFIED - Immediately replace "only one that exists / owns the region" with "fits below BitDelta's floor; superiority over other training-free low-rank formats was not established"; run the SVD/Delta-CoMe baseline only if time permits before Nov 2.

R5: ADOPT - Downgrade Spark's role to "recipe search + claim-checking workflow," disclose in one sentence that Spark generated the held-out questions, and move quantum audit/Gemini arithmetic to the repo (not the main pitch).

R6: ADOPT - Demo must show base vs full vs patch side-by-side including a first-token-gate failure; state swap time as measured file-load time on the demo machine; cut cloned-voice/MMS narration discussion from the submission form.

R7: ADOPT - Add one explicit sentence delineating Oct 26–Nov 2 work (modules, benchmarks, results) vs inherited v0.1–v0.3 artifacts; hackathon judges need this boundary.

R8: ADOPT - If R1–R7 cannot be completed, reposition as a diagnostic/research prototype whose strongest finding is the first-token gate (patch 0.010 vs base 0.031 vs full 0.167), not an Impact-ready distribution system.

WRONG: nothing

VERDICT: Wonder's review changes the pre-Nov 2 plan: execute R1–R7 (with R4 wording change as minimum, baseline run as stretch) and treat R8 as the explicit fallback if time runs out.

## Panelist answer: Glimmer (Flash OmniRoute, served meta/muse-glimmer-30b)

N1: AGREE - No truncated SVD/low-rank FP16 or Delta-CoMe-style baseline at ~19 MB was run, so "owns the region" is only a BitDelta floor argument not a proven superiority claim.
N2: AGREE - Search winners did exceed the stated hard byte budget by 11.8% to 38% and required post-hoc byte-fair variants, undermining the in-loop exact byte accounting guarantee.
N3: AGREE - A weight delta does not transfer tokenizer files, chat template, generation config, safety system behavior or base-version compatibility, so "swap a file, swap the behavior" is materially overstated.
N4: AGREE - No confidence intervals or significance tests are reported and metric inversion with gap-closed >1.0 and subset reversals shows the headline 23.2% is unstable.
N5: AGREE - Arithmetic recomputation, file-consistency checks and quantum audit sampling verify file consistency not benchmark validity, leakage or statistical robustness, making audit theater a fair characterization.
R1: ADOPT-MODIFIED - Require live demo video and X links at submission time, not placeholders; if posting is planned for Nov 2, submit only after links are live and verified.
R2: ADOPT - Rewrite the opening to the defensible training-free lossy delta-distribution claim and move LoRA defeat, BitDelta crossover and first-token failure into the first third.
R3: ADOPT - Add a compact per-pair results table with base/full/uniform/winner log score and first-token accuracy plus bytes, including the 1.5B subset reversal and >100% pairs.
R4: ADOPT-MODIFIED - Cannot run a new SVD/Delta-CoMe baseline before Nov 2, so delete "only one that exists/owns the region" wording now and state superiority over other training-free low-rank formats was not established.
R5: ADOPT - Downgrade Spark judging to recipe search plus claim-checking workflow, disclose in one sentence that Spark also generated the held-out questions, and move quantum audit and Gemini arithmetic out of the main pitch.
R6: ADOPT - Reframe demo to show base vs full vs patch side-by-side including first-token-gate failure, report swap time as measured file-load on the demo machine, and remove cloned-voice/MMS narration discussion from the submission form.
R7: ADOPT - Make the new-work boundary explicit in one sentence on which modules, benchmarks and results were created Oct 26-Nov 2 versus inherited from v0.1-v0.3.
R8: ADOPT - Keep as fallback repositioning to a diagnostic research prototype whose strongest finding is the first-token gate if R1-R7 cannot be completed before the deadline.
WRONG: nothing
VERDICT: Yes - Wonder's review forces claim downgrades, disclosure fixes and live links before Nov 2 submission.

## Panelist answer: Grok (Flash OmniRoute, served grok-4.7)

N1: AGREE - Ruling out a plain 1-bit delta below ~62 MB only shows BitDelta cannot exist there; with no truncated-SVD or Delta-CoMe-style mixed-precision run at ~19 MB, "owns the region" is unsupported.
N2: DISAGREE - The submitted artifact already leads with the byte-fair recipe, and the 11.8–38% overruns are not in the verified facts, so an intermediate search miss does not falsify the byte budget of the patch being submitted.
N3: AGREE - A weight delta does not carry the tokenizer, chat template, generation config, safety behavior, or base revision, and this project's own template confound already shows an Instruct patch on the wrong stack is not the Instruct product.
N4: AGREE - Gap-closed 0.232 and first-token 0.010 are bare point estimates on 96 items, and a metric that exceeds 1.0 and reverses the 1.5B heldout24 subset cannot carry the headline without intervals or a test.
N5: AGREE - Spark wrote the 96 questions, designed the recipes, and judged the claims; Gemini, Glimmer, script recomputation, and the 41/41 quantum sample check arithmetic and file consistency, not metric validity, leakage, or power.

R1: REJECT - The 3-minute video is finished and the YouTube/X fields are empty only because posting is the planned Nov 2 step, so holding the entry for URLs that cannot exist before upload is a false blocker.
R2: ADOPT-MODIFIED - Do not rewrite done prose: the README and draft already state lossy, training-free, 23.2% gap closed, and first-token 0.010 below base 0.031; only confirm the LoRA loss, the 38.5%-vs-43.6% BitDelta crossover, and that first-token regression sit in the first third of the form.
R3: ADOPT - Add one table with base, full, uniform, and winner on log score and first-token accuracy plus bytes for every pair, including the 1.5B heldout24 reversal and the two gap-closed>1.0 pairs labeled as not a recovery fraction.
R4: ADOPT - Do not block on a new baseline; delete "owns the region / only one that exists" and say it fits under BitDelta's floor and was not shown to beat other training-free low-rank formats at ~19 MB, while keeping 38.5% vs BitDelta's 43.6% at matched budget visible.
R5: ADOPT - One sentence must say Spark generated the held-out items, searched recipes, and checked claims, and the quantum audit plus Gemini arithmetic must leave the pitch for the repo.
R6: ADOPT-MODIFIED - Do not reshoot unless the finished video hides a first-token miss; in the form, show base vs full vs patch including that miss, label 0.104 s / 0.087 s as file-load time on the demo machine, and delete the cloned-voice/MMS narration.
R7: ADOPT - One sentence must name which modules, benchmarks, and results were made Oct 26–Nov 2 versus inherited from v0.1–v0.3.
R8: ADOPT-MODIFIED - Reposition now, not as a fallback: it is a training-free diagnostic experiment whose headline is 0.232 gap closure at ~19 MB with zero teacher data, losing to matched-byte LoRA (1.362 in-style, 0.620 out-of-style) when training is affordable and to BitDelta above the floor — not a product, and not with the first-token gate as the sole finding.

WRONG: "No confidence intervals anywhere" is false — distilled LoRA is 1.362 ± 0.033 over 3 seeds. N2's 11.8–38% figures are not verified and must not be repeated. R1 and R2 misread the current texts: the video exists, the links wait on the Nov 2 post by plan, and the lossy / 23.2% / first-token-below-base paragraph is already beside the size claim, with LoRA and the out-of-style 0.620 result already in the draft. The verdict also omits the adapter's real cost (1,500 teacher generations and ~8 h) and that out-of-style drop, so "too unreliably to justify choosing it whenever training is possible" is harsher than the comparison actually run. "Audit theater" is a motive claim; the documents put the damaging numbers up front. The failure is what was audited, not a cover-up.

VERDICT: Yes on framing, no on logistics — submit Nov 2 as a research prototype with the results table, the region-ownership sentence gone, and Spark's triple role disclosed; do not block on a new SVD baseline or on links published in the same session.

## Panelist answer: Claude (antigravity/claude-opus-4-6-thinking, served claude-opus-4-6-thinking)

**N1: AGREE** - The "owns the region" claim is only a statement about BitDelta's format floor, not about the absence of other training-free compression methods at 19 MB, and truncated SVD of the delta is an obvious omission that any reviewer will notice.

**N2: AGREE** - The byte-fair variants exist precisely because the initial winners blew the budget, and while the project did self-correct, Wonder is right that the harness's hard constraint failing on its own terms is a legitimate credibility issue worth disclosing rather than burying.

**N3: AGREE** - The "swap a file, swap the behavior" framing genuinely overclaims because a weight delta without the tokenizer, chat template, generation config, and safety layers is not a drop-in behavioral replacement, and the submission should scope the claim to "swap the weight delta" explicitly.

**N4: DISAGREE** - Gap-closed exceeding 1.0 is already disclosed as an anomaly attributed to the full fine-tune underperforming base (not as a recovery fraction), and while confidence intervals would strengthen the work, the 96-item eval with per-pair reporting is transparent enough that the absence of CIs does not invalidate the headline; the real problem is sample size, not missing error bars on a deterministic compression.

**N5: AGREE** - The audit stack (quantum sampling, Gemini arithmetic, 41/41 checks) verifies internal consistency and file-level correctness but does not touch metric validity, code correctness, data leakage, or the adequacy of 96 items as a benchmark, and presenting it prominently risks exactly the "audit theater" perception Wonder describes.

**R1: ADOPT** - The placeholders must be filled before submission; this is non-negotiable and already the plan for Nov 2.

**R2: ADOPT-MODIFIED** - The opening should lead with the defensible "training-free, lossy delta-distribution experiment" framing and the LoRA defeat should appear early, but forcing the BitDelta crossover and first-token failure into the literal first third of the Project Description will bury the motivation before judges understand what the tool does; place them immediately after the one-paragraph pitch, not interleaved with it.

**R3: ADOPT** - A single compact results table with base/full/uniform/winner on both metrics plus bytes per pair, including the 1.5B subset reversal and >1.0 pairs, is the single highest-leverage addition for Technical Depth and honesty signaling.

**R4: ADOPT-MODIFIED** - Running a truncated SVD baseline at 19 MB is feasible on CPU in hours and should be attempted before Nov 2; if it cannot be completed, adopt Wonder's replacement wording verbatim, but do not preemptively delete the claim without trying the experiment first since a win here would be the strongest possible rebuttal.

**R5: ADOPT-MODIFIED** - Downgrade the Spark judging claim to "recipe search and claim-checking workflow" and disclose that Spark generated the held-out questions, yes; but the quantum audit and Gemini arithmetic should remain mentioned in the submission as a one-liner pointing to the repo rather than fully removed, because the hackathon scores Use of Meta AI Tooling at 25% and the multi-model workflow is part of that story.

**R6: ADOPT-MODIFIED** - Side-by-side base/full/patch generations including a first-token failure is excellent demo design and should be adopted; stating swap time as file-load time on the demo machine is fair; but the cloned-voice/MMS narration discussion is already absent from the current submission draft text (it was an internal conversation), so "remove" is a non-issue—just confirm it stays out.

**R7: ADOPT** - One sentence delineating the Oct 26–Nov 2 new work from v0.1–v0.3 inherited work costs nothing and preempts any originality question from judges.

**R8: REJECT** - The fallback framing as "diagnostic/research prototype" undersells the actual deliverable (working CLI, hot-swap, deterministic compression, four model pairs, honest metrics) and would crater the Impact score; if R1–R7 are truly impossible, the better fallback is to submit as-is with the existing honesty content rather than actively repositioning downward.

**WRONG:** Wonder's one-line verdict states the results "undermine its product case" and that one should "choose training an adapter whenever training is possible"—but this conflates the project's actual niche (zero-query, zero-GPU, deterministic, sub-second patch distribution) with the adapter-training use case. The LoRA comparison is disclosed and the project never claims to beat training; it claims to occupy a space where training is unavailable or uneconomical. The verdict is rhetorically clean but logically builds a straw man by evaluating a training-free tool against the assumption that training is always possible.

**VERDICT:** Wonder's review does change what should happen before Nov 2—specifically, attempt the SVD baseline (R4), add the compact results table (R3), tighten the "swap" and "owns the region" language (N3, N1), and scope the audit claims (R5)—but its overall verdict is too pessimistic because it judges the project against a use case it explicitly does not claim to serve.

## No answer: GPT-OSS

HTTP 410 model_shutdown (openai/gpt-oss-120b via Flash OmniRoute), same as every attempt since 2026-10-28. Recorded, not counted in any tally.

## Wonder's closing response (verbatim, one paragraph)

I accept the panel's converged result, including where it corrects me outright: “no confidence intervals anywhere” was false and I withdraw it—the LoRA result is 1.362 ± 0.033 across three seeds, though the headline 0.232 has none and, as Claude notes, the deeper problem there is sample size rather than error-bar formatting alone; R1 and R2 did partly demand what already exists, since the video is finished awaiting its planned Nov 2 posting and the README and draft already place the lossy/23.2%/first-token/LoRA disclosures beside the size claim, so verification and earlier placement rather than creation or a wholesale rewrite are the right remedies; and my verdict did silently assume training is available while omitting the adapter's real price of 1,500 teacher generations and roughly eight hours plus its out-of-style fall to 0.620, so LoRA does not costlessly dominate and my revised verdict is that the product case is undermined where training is feasible but remains open—though still unproven against the missing training-free SVD/low-rank baselines at 19 MB—in settings where it is not. On that basis I endorse the adopted package: R3 and R7 as adopted unanimously; R4 with “owns the region” deleted now in favor of “fits below BitDelta's floor; superiority over other training-free low-rank formats was not established,” with the SVD run sensibly demoted to a pre-Nov 2 stretch goal rather than a blocker; R5's downgrading of Spark to recipe search and claim-checking, with one-sentence disclosure that Spark generated the held-out questions and with the quantum audit and Gemini arithmetic out of the main pitch; the modified R2 and R6 that surface the three defeats within the first third and add a side-by-side base/full/patch example with a first-token failure in the submission text while labeling swap times as file-load time on the demo machine, without a wholesale rewrite or reshooting the finished video; R1 as live-link verification at Nov 2 submission; and N3's narrowing of the claim, since the patch swaps weights rather than tokenizer, chat template, or generation config and therefore does not by itself “swap the behavior.” I also take the recorded dissents seriously: Grok is right that I should re-verify the 11.8–38% byte-overrun figures before repeating them as numbers for N2, with the criticism narrowing accordingly if the submitted artifact already leads with the byte-fair recipe, and that “audit theater” imputed a motive I cannot show, so I drop that phrase while retaining the accepted structural point that the rigor stack verifies arithmetic rather than benchmark validity; Grok's preference notwithstanding, R8 is therefore correctly held as a contingency rather than adopted as the plan, because the R1–R7 path is feasible by Nov 2 and preserves both the experiment's unusual honesty and the narrower claim it can actually defend.
