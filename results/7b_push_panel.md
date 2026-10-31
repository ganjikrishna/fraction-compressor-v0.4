# 7B push panel, Sat Oct 31, 2026

Question put by Vinay: what to do with the 7B fifth-pair material. His lean, given to the panel: "I think we can push 7B too, but keep it simple not too much." His earlier same-day decision was keep local; he reopened it and ordered this consult before deciding. **Advisory only: no files were changed and nothing was pushed by this panel run.**

## Context completeness (Vinay's follow-up, applied before tallying)

All counted votes were cast on the complete context pack (v2, verbatim below), which contains all five required elements: (1) the project in one line, including the Nov 2 submission, the four-pair claim surface passed by two fresh judges, and the submission doc judged ready as-is; (2) what the 7B run was and its exact results; (3) the awkward facts (reference inversion, no recovery fraction possible, scaled-delta regularization result); (4) the current repo state (no 7B results live, four mentions exist); (5) Vinay's lean and options A/B/C as defined.

The first pack sent to five panelists (Spark 1.3, Spark 1.2, Spark 1.1, Wonder, Gemini) was missing the fresh-judges and doc-ready detail in element (1) and the stage-2 figure (-9.584) in element (2). Those five were re-run on the complete pack and only the re-run votes are counted. The superseded first-round votes, for the record, were: Spark 1.3 A, Spark 1.2 B, Spark 1.1 B, Wonder B, Gemini B. The completed pack changed one vote (Spark 1.2, B to A). The five OmniRoute panelists (Glimmer, Nemotron, Grok, Claude, GPT-OSS) received the complete pack on their first call.

## Tally (counted votes, complete pack)

| Panelist | Route | Vote |
|---|---|---|
| Muse Spark 1.3 | Meta Model API | A |
| Muse Spark 1.2 | Meta Model API | A |
| Muse Spark 1.1 | Meta Model API | B |
| Muse Wonder | Meta Model API | B |
| Gemini 3.5 Flash Lite | Google Gemini API | B |
| Muse Glimmer 30B (served: meta/muse-glimmer-30b) | Flash OmniRoute | A |
| Nemotron 3 Ultra 550B | Flash OmniRoute | B |
| Grok 4.7 | Flash OmniRoute | B |
| Claude Opus 4.6 Thinking | Flash OmniRoute, verified antigravity route | NO ANSWER |
| GPT-OSS 120B (medium) | Flash OmniRoute, antigravity route | NO ANSWER |

**A: 3. B: 5. C: 0. B wins among the eight answering panelists.**

No answers, recorded honestly: Claude and GPT-OSS were each attempted twice (about 18:03Z and again after the stated quota reset, about 18:09Z). Both times the antigravity gateway returned "All antigravity accounts have exhausted their quota (cached quota state, no upstream attempt)"; the calls never reached the models. No other route was substituted for Claude, per the verified-route rule.

## The pack (v2, verbatim, as sent to every counted panelist)

You are one member of an independent review panel advising on a decision. This panel is advisory only.

PROJECT IN ONE LINE: Fraction Compressor, a Meta Global AI Developer Hackathon entry (author of record Vinay K Ganji Krishna), submitting Monday Nov 2, 2026; its four-pair claim surface has already been passed by two fresh independent judges (a fresh-eyes hard check of every file against the result files) and the submission document has been judged ready to submit as-is.

DECISION: what to do with the "fifth pair" (7B) experiment material.

OWNER CONTEXT (his lean; judge independently): "I think we can push 7B too, but keep it simple not too much." Earlier today he decided keep-local; he has reopened the question and asked this panel before deciding.

WHAT THE 7B WORK IS
- Pair: Qwen2.5-7B base / Instruct. The project's factored 1-bit patch format, run with AirLLM-style layer streaming in the project's own NumPy runtime on a CPU-only 11 GB RAM machine (a 7B model can never be held whole in memory there).
- Stage 2 winner ("down_king") scored -9.584 at the selection stage. Final held-out 96-question set, mean logprob: base -6.916, full fine-tune delta -15.974, down_king -8.694, uniform rank-32 -13.158. down_king first-token accuracy 0.344, best of the set.
- The 86 MB factored patch beat the plain 1-bit baseline (951,911,192 bytes) outright on score (-8.694 vs -11.378) at about one eleventh of the bytes.

THE AWKWARD FACTS, PLAINLY
- Reference inversion: the full fine-tune scores BELOW the base model on both probe sets, so gap_closed is null at 7B and NO recovery fraction can honestly be claimed for any 7B config.
- Yardstick fix (Oct 29): a corrected eval battery removed an echo artifact; the full delta's deficit shrank but it still does not beat the base on mean logprob anywhere. The honest 7B claim is behavioral: first-token accuracy base 0.05 to full 0.33 overall, math subset 0.03 to 0.75; down_king keeps math at 0.75.
- Regularization test: a plain 25%-scaled copy of the full delta reproduces and exceeds down_king's whole profile, supporting the explanation that the patch's apparent 7B skill is mostly a regularization effect, not recovered fine-tune behavior. down_king generations carry the right content but trail junk tokens.
- The 7B numbers themselves are verified: script recomputation 78/78 checks pass; Muse Spark judged all 12 stated claims SUPPORTED.

CURRENT REPO STATE
- All 7B result files are LOCAL only. The public repo (head 2ce0036) contains NO 7B results or numbers. It only mentions the work in four places: BUILD_PLAN.md (2 items), results/airllm_design_consult.md (a design consult), one line in results/glimmer_repo_sweep.md, and two api_usage_log purpose strings.
- The four-pair submission text claims nothing about 7B. A Nov 2 push batch is already approved; any 7B material would ride it or a later push.

OPTIONS
A. Keep 7B local entirely. Repo stays four pairs; the existing mentions stay as they are.
B. Push it SIMPLE (the owner's lean): the fifth-pair result files as one compact results section (the report including the yardstick and regularization writeup, plus the eval JSONs). No README claims, no submission mention, with the inversion and the regularization result stated up front in the report itself.
C. Push it fuller: a README section with claims. (If you pick C, say what extra verification or framing that would require.)

ANSWER FORMAT (keep it tight):
VOTE: A, B, or C
STRONGEST REASON: one or two sentences
BIGGEST RISK OF MY OWN PICK: one sentence
GUARDRAILS (only if your pick is B or C): the exact wording rules the published text must follow
ONE-LINE SUMMARY: your vote and reason in one line

## Verbatim counted votes

### Muse Spark 1.3 (A)

VOTE: A
STRONGEST REASON: The four-pair submission is already twice-verified clean and ready to submit; 7B has null gap_closed and a regularization confound that adds judging risk with zero submission upside 48 hours before deadline.
BIGGEST RISK OF MY OWN PICK: The four dangling public mentions of 7B stay without results and could read as incomplete.
ONE-LINE SUMMARY: Vote A - freeze the clean four-pair win for Nov 2, push honest 7B after judging.

### Muse Spark 1.2 (A)

VOTE: A

STRONGEST REASON: The 4-pair submission is already frozen and passed by two fresh hard checks; the 7B experiment has null gap_closed (full -15.974 < base -6.916 on held-out logprob, so no recovery fraction can be claimed), its apparent skill is reproduced by a trivial 25%-scaled full delta, and generations trail junk tokens - adding it pre-deadline offers no scoring upside and only risks diluting/ confusing judges about the validated core.

BIGGEST RISK OF MY OWN PICK: Lose time-stamped public provenance for a real verified engineering result (86 MB factored 1-bit patch beating 951 MB baseline at -8.694 vs -11.378 on 11 GB CPU streaming, math 0.75 retained) and leave the four existing 7B mentions without supporting data.

ONE-LINE SUMMARY: Vote A - keep 7B local until after Nov 2 submission; inversion + regularization null result adds pre-deadline risk with zero benefit to an already-approved 4-pair entry, push as exploratory appendix after judging.

### Muse Spark 1.1 (B)

VOTE: B

STRONGEST REASON: 7B shows real engineering - 7B streamed on 11 GB CPU-only + 86 MB factored patch beating 951 MB plain 1-bit (-8.694 vs -11.378) - and responsible science if presented as supplementary with inversion and regularization disclosed, leaving the verified four-pair submission untouched.

BIGGEST RISK OF MY OWN PICK: A casual repo browser anchors on full -15.974 < base -6.916 and junk-token generations and misreads it as method failure, diluting the clean four-pair story right before deadline.

GUARDRAILS:
- Put only under results/7B_supplementary_exploratory/ - no README.md edit, no submission doc mention.
- Report first paragraph must state verbatim: "7B inversion: mean logprob base -6.916, full fine-tune -15.974, so gap_closed is null and NO recovery fraction is claimed for 7B."
- Second paragraph must state: "Yardstick fix Oct 29 removed echo artifact; deficit remains. Regularization test: 25%-scaled full delta reproduces and exceeds down_king profile, so down_king skill is explained as regularization, not recovered fine-tune behavior."
- Allowed 7B claim wording only: "behavioral first-token accuracy base 0.05->full 0.33 overall, 0.03->0.75 math; down_king keeps math 0.75" and "down_king generations carry right content but trail junk tokens."
- Forbid for 7B: words "recovery", "recovered", "gap_closed", "%" / fraction closed, "beats base" on logprob.

ONE-LINE SUMMARY: B - push 7B as isolated supplementary results with null recovery disclosed, because 86MB beats 951MB baseline and documents 11GB CPU streaming without touching the verified 4-pair submission.

### Muse Wonder (B)

VOTE: B

STRONGEST REASON: The 7B numbers are independently verified, and a compact, results-only publication preserves a useful scale/streaming datapoint—86 MB patch beating the 952 MB 1-bit baseline—without touching the already-approved four-pair submission claim surface.

BIGGEST RISK OF MY OWN PICK: A skimming judge may still conflate the fifth pair with the validated four, or read the reference inversion as a general failure of the method despite the caveats.

GUARDRAILS:
- No README, submission-document, or headline claims about 7B; publish only the compact report and eval JSONs.
- The report's opening must state verbatim in substance: "The full fine-tune underperforms the base model on mean logprob, gap_closed is null, and no recovery fraction is claimed at 7B."
- It must also state up front that a 25%-scaled full delta reproduces/exceeds down_king, so the apparent benefit is mostly consistent with regularization, not demonstrated recovery of fine-tune behavior.
- Any accuracy figures must be labeled "first-token accuracy," shown alongside base and full-delta values, and never converted into a recovery or success percentage.
- The 86 MB vs 951,911,192-byte comparison may be described only as beating that 1-bit baseline on this eval, not as 7B validation or scaling success.
- Note the trailing-junk-token generation issue wherever generation quality is mentioned.

ONE-LINE SUMMARY: B — publish the verified 7B results simply and negatively framed in the repo only, with no addition to the submission claims.

### Gemini 3.5 Flash Lite (B)

VOTE: B

STRONGEST REASON: Option B respects the owner's lean to "push 7B simple" while maintaining complete scientific integrity by transparently publishing the inversion and regularization caveats alongside the raw results without inflating the official submission claims.

BIGGEST RISK OF MY OWN PICK: Readers or hackathon judges might gloss over the caveats in the report and mistakenly cite the 7B token-accuracy wins as recovered fine-tune behavior.

GUARDRAILS:
1. Any published 7B text must explicitly state that the full fine-tune scores below the base model, meaning no recovery fraction can be claimed.
2. The regularization test findings (showing that a 25%-scaled full delta reproduces the profile) must appear with equal prominence beside the down_king results.

ONE-LINE SUMMARY: Vote B pushes the 7B material simply and transparently, sharing the verified numbers and caveats in a local report without corrupting the core four-pair submission claims.

### Muse Glimmer 30B (A) (served model confirmed: meta/muse-glimmer-30b)

VOTE: A
STRONGEST REASON: The 7B pair has a reference inversion with full fine-tune below base on mean logprob, so gap_closed is null and no honest recovery fraction can be claimed; publishing it would risk contaminating the clean four-pair claim surface already independently approved for submission.
BIGGEST RISK OF MY OWN PICK: A verified exploratory experiment remains unpublished, losing transparency and a reproducibility signal for future work.
ONE-LINE SUMMARY: Vote A – keep 7B local to protect the verified four-pair submission from an invalid recovery claim.

### Nemotron 3 Ultra 550B (B)

VOTE: B
STRONGEST REASON: The 7B results are verified and scientifically interesting (regularization effect, first-token accuracy gains), but the reference inversion means zero recovery fraction can be claimed; pushing them SIMPLE with the inversion and regularization explanation stated upfront serves honest transparency without polluting the four-pair submission narrative.
BIGGEST RISK OF MY OWN PICK: A reader skimming the repo may still associate the 7B patch with the project's "recovery" brand despite the caveats.
GUARDRAILS: The published 7B report must (1) lead with "Full fine-tune underperforms base on mean logprob; no recovery fraction is defined or claimed," (2) state "down_king's advantage is a regularization effect, confirmed by 25%-scaled full delta matching/exceeding it," (3) note "generations carry correct first tokens but trail junk," (4) include the yardstick-fix note and the first-token accuracy table (base 0.05→full 0.33 overall, math 0.03→0.75; down_king math 0.75), and (5) carry zero README badges, zero submission references, and zero "fifth pair" language—just a results/7B/ folder with the report and eval JSONs.
ONE-LINE SUMMARY: Vote B—publish the verified 7B artifacts simply and transparently, with the inversion and regularization caveats as the headline, not the footnote.

### Grok 4.7 (B)

VOTE: B

STRONGEST REASON: The 7B numbers are verified, and the public repo already names the work, so a compact local-only silence is selective reporting; the honest content is a null recovery (gap_closed undefined) plus a regularization explanation, which belongs in a side report and nowhere near the four-pair claim surface.

BIGGEST RISK OF MY OWN PICK: A hackathon reviewer skims −8.694 vs −11.378, 86 MB, and math accuracy 0.75, quotes them as a fifth-pair win, and either credits a result the data do not support or punishes the submission for a metric inversion.

GUARDRAILS:
- Title the section as a scale probe that is not part of the claim set. No README edit, no submission-doc mention, no pointer from the four-pair text.
- First two sentences, before any table: the full fine-tune is worse than base on mean logprob on both probes, so gap_closed is null and no recovery fraction is claimed; a plain 25%-scaled copy of the full delta matches or beats down_king, so the apparent skill is mostly regularization, not recovered fine-tune behavior.
- Forbidden, including captions and file blurbs: "recovers," "recovery," "gap closed," "fraction of the fine-tune," "validates at 7B," "scales," "winner," "outright," "best."
- Baseline byte/score comparison only in the same paragraph as the regularization sentence, as a score-and-size fact, never as recovered behavior.
- First-token and math accuracy only as behavioral, with the junk-token trailing stated in the same sentence; not in a headline.

ONE-LINE SUMMARY: Push B only — verified 7B files as a clearly labeled non-claim probe that leads with null recovery and the regularization result, with no README or submission claims.

## Guardrails synthesis (B wins; the rules all five B voters converge on)

1. Results only, fully isolated: one compact folder (results/7B/ or results/7B_supplementary_exploratory/) holding the report (with the yardstick and regularization writeup) and the eval JSONs. No README edit, no submission mention, no pointer from the four-pair text, no badges.
2. The report leads, before any table, with the inversion in substance: the full fine-tune scores below the base on mean logprob (base -6.916, full -15.974), gap_closed is null, and NO recovery fraction is claimed for 7B.
3. The regularization result gets equal, up-front prominence: a plain 25%-scaled copy of the full delta reproduces and exceeds down_king's profile, so the apparent 7B skill is explained as regularization, not recovered fine-tune behavior. The yardstick-fix note (echo artifact removed Oct 29, deficit remains) goes with it.
4. Accuracy figures only as behavioral first-token accuracy, always with base and full values beside them (0.05 to 0.33 overall, math 0.03 to 0.75, down_king keeps math 0.75), never converted into a recovery or success percentage.
5. The 86 MB vs 951,911,192-byte, -8.694 vs -11.378 comparison appears only as a score-and-size fact in the same paragraph as the regularization sentence, never framed as 7B validation, scaling success, or recovered behavior.
6. Forbidden wording for 7B, including captions and file blurbs: recovery, recovers, recovered, gap closed, fraction of the fine-tune, validates at 7B, scales, winner, outright, best, beats base (on logprob).
7. The junk-token trailing in down_king generations is stated wherever generation quality is mentioned, and in the same sentence as any accuracy claim.
8. Frame the section as a scale probe / supplementary exploratory material that is not part of the submission claim set.

## The dissent (A bloc: Spark 1.3, Spark 1.2, Glimmer)

The A voters do not dispute the numbers; they dispute the timing and the risk asymmetry. The four-pair submission is frozen, twice verified, and judged ready; 7B adds no scoring upside before the Nov 2 deadline and carries a real dilution risk if a judge skims the inversion as a method failure. Spark 1.3 and Spark 1.2 both land on the same compromise inside their A votes: publish the honest 7B material AFTER judging, as an exploratory appendix. Spark 1.2 is the strongest single dissent, adding that the 25%-scaled-delta result and the junk-token generations make the 7B story easy to misread under deadline pressure. Glimmer's A is the strictest: publishing at all risks contaminating an independently approved claim surface.

## Token usage (all calls logged in results/api_usage_log.jsonl, purpose "7B push panel")

Counted round (complete pack v2):
- muse-spark-1.3: 3,065 (922 in / 2,143 out)
- muse-spark-1.2: 3,987 (922 / 3,065)
- muse-spark-1.1: 4,320 (922 / 3,398)
- muse-wonder-1.0: 2,135 (922 / 1,213)
- gemini-3.5-flash-lite: 1,200 (996 / 204)
- nvidia/meta/muse-glimmer-30b: 2,706 (970 / 1,736)
- nvidia/nvidia/nemotron-3-ultra-550b-a55b: 1,863 (1,021 / 842)
- grok-cli/grok-4.7: 4,445 (2,162 / 2,283)
- Claude, GPT-OSS: 0 (no usage; antigravity quota errors, no upstream attempt)
- Counted round total: 23,721

Superseded first round (incomplete pack, votes not counted): muse-spark-1.3 5,952; muse-spark-1.2 5,410; muse-spark-1.1 3,192; muse-wonder-1.0 1,704; gemini-3.5-flash-lite 1,130. Subtotal 17,388.

Grand total across all panel calls: 41,109 tokens.
