# Fresh-check fixes: panel review, applied edits, and the judge loop, Oct 31, 2026

Ordered by Vinay on Oct 31, 2026: panel-review the fixes for the fresh-eyes hard check flags (results/fresh_hard_check.md) and apply them; then loop the revised files back to the two fresh judges (muse-spark-1.2, muse-spark-1.1) until both PASS, cap 3 judge rounds; then a judge-role review of the final submission draft. All edits local only; everything here rides the Nov 2 pre-submission batch. Narration v7 untouched throughout (settled by Vinay: stays as is). The Qwen2.5-7B fifth-pair material stays local and out of the batch (settled).

## Round 0: drafted fixes, panel review, applied

Drafted fixes for flags 1-7 of the hard check (flag 8, narration, recommendation only). Panel: Glimmer (Flash OmniRoute, served model confirmed meta/muse-glimmer-30b), Muse Spark 1.3, Gemini (gemini-3.5-flash-lite), Muse Wonder.

Panel verdicts:
- Items 1 (LoRA ratios 1.362 / 0.620 / 1.395 replacing 136% / 139.5%), 2 (cover note v5 to v7), 3 (size-claim adjacency: README naming paragraph, README Do-it-yourself, draft 988 MB vs 19 MB, each gaining lossy + 0.010 vs 0.031), 4 (draft rollback line gains file-load label): PASS from all four.
- Item 5 (draft NuExtract line): Glimmer PASS, Gemini PASS; Spark 1.3 and Wonder FLAG for fuller counts. Majority applied: Wonder's wording adopted ("the full fine-tune gets 8 of 10 prompts clean (9 of 10 parseable: 8 clean / 1 partial / 1 failed) while the rank-32 patch gets only 1 of 10 prompts clean and the base gets none at all..."), verified exact against results/skill_demo.json.
- Item 6 (demo_script 0.49 s): Glimmer and Spark 1.3 FLAG with strengthened label wording; Wonder, Gemini PASS. Applied the merged form: 6a uses Spark's text ("the file-load time on the demo machine of record is 0.104 s to uniform and 0.087 s to lite; a separate contended recording of the same demo took 0.49 s wall-clock under load, which is not a file-load measurement..."), 6b uses Glimmer's text plus Spark's "not a file-load measurement" clause.
- Item 7 (README quickstart): PASS from all four, preference A unanimous: requirements.txt created (numpy, tokenizers; derived from the public scripts' imports: quickstart needs NumPy alone, make_patch NumPy, hotswap_demo NumPy + tokenizers; safetensors files are read by hand-rolled code) plus the install step in the README.
- Item 8 (narration): NO from all four panelists. The on-screen slide already prints the numeric accuracies, the spoken "well under a second" is true of both recordings, and re-recording the adopted v7 cut two days before submission risks the deadline for negligible gain. Vinay settled this the same day: narration stays as is. OPEN ITEM CLOSED by his decision.

Glimmer spot-check of the applied round 0 sections (two calls; an interim delivery of the first call's output showed Flash safety-filter placeholders, the completed output later arrived in full and supersedes that reading): the full-quote call returned PASS on items 1, 2, 3, 6, 7, 9, 10, 11 and FLAG on 4, 5, 8, all three adjudicated: item 4 (the draft's "0.232 (23.2%)" is a value at or below 1.0, where percentages are permitted, and the LoRA accuracy tie it questioned is supported by results/lora_baseline.json, 0.167-0.177 against the full fine-tune's 0.167; the spot-check prompt's evidence line had omitted the LoRA accuracy); item 5 (same percentage point; the adjacency concern was later closed for good by the round 1 P4/P5 accuracy parentheticals on those very LoRA sentences, after which both judges passed the draft); item 8 (the flag overlooks the file-load label present in the very sentence it quotes; reviewer error). The summary-form retry returned PASS on 9 of 11 with FLAGs on its items 5 and 10, both summary artifacts (the item 10 flag claimed the demo-machine label was missing, but the applied note opens "the file-load time on the demo machine of record is..."). The full-text judges re-checked all these passages in round 1 and passed them.

## Judge round 1

Both judges re-checked README.md, docs/submission_draft.md, docs/demo_script.md, PROVENANCE.md, requirements.txt against the same evidence pack (plus a coordinator addendum: both patches parse the Arrival JSON per the full hotswap_demo.json).

- spark-1.1: README PASS; demo_script, PROVENANCE, requirements PASS; draft FLAG (2 trap-b sentences: "With patches, an update is a 19 MB file on a stable base." and "At 19 MB our format fits below BitDelta's floor...").
- spark-1.2: demo_script, PROVENANCE, requirements PASS; draft FLAG (the same 2 sentences plus the Known-limits BitDelta floor sentence, the LoRA intro sentence, and the out-of-style sentence, all trap-b adjacency); README FLAG: one real catch (the "What is in this repo" hot-swap line, "in about a tenth of a second" with no file-load label), a broad trap-b reading (accuracies adjacent to every byte figure), and the NOT IN EVIDENCE set from the original check (0.28 bpw, 8.4 MB / 144 KB, rank-64/128, 19,434,400 B recipe, knowledge split, pair 2/3 subset halves, pair 4 five recipes).

Coordinator file verification of the NOT IN EVIDENCE set (every value confirmed in the repo's own files): skill_demo_ranks.json conclusion (rank 64 = 2/10 at 37,044,736 B; rank 128 = 2/10 at 72,265,216 B); skill_demo_recipe.json (Gatekeeper Embed+O 19,434,400 B, clean 0); glimmer_repo_sweep.md (Glimmer's own earlier derivation from src/factored.py: 147,456 B = 144 KB, 0.28125 bpw, full layer about 8.4 MB); alien_sweep_heldout96.json per-bucket logprobs (knowledge gap closed uniform 0.078, lite 0.037); second_pair_heldout96.json (rebalanced beats uniform on both halves); third_pair_heldout96.json (halves 0.200 vs -0.017 and 0.148 vs -0.091, matching the README's 20.0% / -1.7% / 14.8% / -9.1%); fourth_pair_stage2.json (all five Spark recipes 38,564,096 to 38,960,128 B, under the 39,046,144 B budget).

## Panel round 1 (items P1-P8), applied fixes, spot-check

- P1 (draft 19 MB sentence): PASS x3 (Glimmer timed out twice on this pack; Spark 1.3, Gemini, Wonder covered). Fix applied: the following lossy sentence now carries the numbers ("its first-token accuracy is 0.010, below the base model's own 0.031").
- P2 (draft At 19 MB sentence): PASS x3. Applied: "(lossy: first-token accuracy 0.010 against the base's 0.031)" inserted.
- P3 (Known-limits BitDelta floor sentence): Gemini and Spark 1.3 ruled LEAVE (P2's adjacency two sentences later satisfies the disclosure); Wonder PASS ambiguous. Majority ruling: no change.
- P4 (LoRA intro sentence): PASS x3. Applied: parenthetical with adapter 0.167 to 0.177, full 0.167, patch 0.010, base 0.031.
- P5 (out-of-style sentence): PASS x3. Applied: parenthetical with out-of-style 0.042, in-style 0.167, patch 0.010, base 0.031.
- P6 (README hot-swap bullet): both "FLAG"s quoted the drafted fix verbatim. Applied: "(file-load time on the demo machine; examples/hotswap_demo.py, transcript in results/)".
- P7 (NOT IN EVIDENCE set): panel ruling, pack artifact, claims stand; verified values added to the round 2 judge pack addendum.
- P8 (broad trap-b scope): PASS x3: headline-adjacency standard met, no per-figure change. Scope rulings recorded for round 2: the ratio-only rule governs gap-closed values, not first-token accuracies; trap (b) is judged at headline claims, pair sections state accuracies in their own text.

Two additions from Vinay, folded into this round:
- Hygiene fix (approved): results/skill_limit_consultation.md line 11, "scores 9/10 clean extractions itself" corrected to "scores 9/10 parseable extractions itself (8 clean, 1 partial, 1 failed)", verified against results/skill_demo.json. This file joins the Nov 2 batch list.
- Spark Open sentence (approved): one sentence added to the draft's Meta products section naming Muse Spark Open's role. Verified role from the records: Baseten Spark Open generated candidate recipes in the sweeps and independently validated results. Applied sentence (after Spark 1.3's spot-check refinement): "Muse Spark Open's part in that loop was load-bearing, not decorative: run through Baseten, it generated candidate recipes inside the search and served as the second judge in the claim-checking, so no recipe win or headline claim rests on a single model's judgment."

Spot-check of the round 1 applied items (Glimmer, Spark 1.3, Gemini): items 2, 5, 6 PASS from all three (Glimmer served model confirmed). Glimmer flagged items 1, 3, 4 and Gemini items 3, 4 on a rule misreading (applying the gap-closed ratio rule to first-token accuracies); adjudicated as reviewer errors: accuracies are absolute decimals everywhere in the project, and trap (b) itself requires them numeric. Spark 1.3 passed all three on the numbers. Spark 1.3's item 7 flag (sentence omitted the generator role) was applied as the refinement above.

## Judge round 2

Pack: same evidence pack plus the P7 verified-values addendum and the panel scope rulings.
- spark-1.1: PASS on all five files.
- spark-1.2: PASS on draft, demo_script, PROVENANCE, requirements. README FLAG, one sentence: pair 4's "(130.7% against 127.9%)" presents gap closed above 1.0 as percentages (with the NOT-a-share disclaimer). Fix proposed by the judge: ratios only.

## Panel round 2 and judge round 3

Panel round 2 (all four): PASS on the fix ("the gap-closed figure goes above 1.0 (1.307 against 1.279)"). On whether the parallel pair-2 sentence ("goes above 100% here", no figures) must also change: Glimmer, Spark 1.3, Gemini NO; Wonder YES (dissent noted, majority rules, no change). Applied to README.

Judge round 3 (README only, the only file changed since round 2): spark-1.2 PASS, spark-1.1 PASS.

LOOP CLOSED in 3 judge rounds: both fresh judges PASS every file (README.md, docs/submission_draft.md, docs/demo_script.md, PROVENANCE.md, requirements.txt).

## Submission doc judge panel (final draft, judge role)

Both judges read the final form text field by field (the draft exactly as it will be pasted, including the Spark Open sentence and all loop fixes), purposes logged as "submission doc judge panel spark-1.2/1.1".

- muse-spark-1.1: every field clear (1-11). Claims it would discount: the multi-behavior serving line as aspirational beyond the single swap demo; the 0.1 s swap as machine-specific file-load; the "updates ship as whole new models" line as an overgeneralization; the below-base first-token accuracy as an Impact discount. Missing: nothing. OVERALL: PASS, ready to submit as-is.
- muse-spark-1.2: fields 1, 2, 3, 5, 6, 7, 8, 9, 10, 11 clear; field 4 clear for compliance, risky for scoring (the honest weak results weigh down Impact; no text defect). Stage One gate: strong pass (field 7's three Meta roles, including the Spark Open sentence, quoted approvingly). Claims it would challenge: the 0.31 bpw metric as unstandard; 51x as pair-specific; swap times as one machine's file-load; gap closed above 1.0 as evaluation variance; the BitDelta and LoRA concessions; validation records living in the repo rather than the pitch. Missing: nothing for the gate or credibility. OVERALL: PASS, ready to submit as-is. Optional polish it suggested (not required, not applied, left for Vinay): a "byte-fair below BitDelta floor" framing next to the 0.010 vs 0.031 line; one line in field 7 naming the call routes (Meta API; Baseten/Fireworks hosting); a file path for the Spark call log (results/api_usage_log.jsonl).

No mini-loop needed: neither judge required a text change.

## Final changed files (Nov 2 batch)

- README.md: lossy + accuracy sentence added after the naming-paragraph size claim; lossy + accuracy sentence added after the Do-it-yourself 51x claim; install step added to Do it yourself (pip install -r requirements.txt); hot-swap bullet gains the file-load label; fourth-pair sentence now states gap closed as ratios (1.307 against 1.279).
- docs/submission_draft.md: LoRA gaps as ratios (1.362; 0.620 with 1.395 as ratio); cover note v5 corrected to v7; 988 MB vs 19 MB sentence gains lossy + accuracies; rollback line gains the file-load label; NuExtract side-by-side corrected to the full counts; impact lossy sentence gains numeric accuracies (P1); At 19 MB sentence gains the lossy parenthetical (P2); LoRA intro sentence gains the accuracy parenthetical (P4); out-of-style sentence gains the accuracy parenthetical (P5); Meta products section gains the Spark Open load-bearing sentence.
- docs/demo_script.md: V3 wording note rewritten to separate the file-load times of record from the contended recording's 0.49 s wall-clock; ON SCREEN note gains the same clarification.
- results/skill_limit_consultation.md: "9/10 clean" corrected to the 8 clean / 1 partial / 1 failed split.
- requirements.txt: NEW (numpy, tokenizers).
- Unchanged: PROVENANCE.md, video/narration_v7.txt.

## Open items

- Optional scoring polish from the submission-doc judge (spark-1.2), listed above; Vinay's call, deliberately not applied so the PASS-as-is verdict stands on the reviewed text.
- Glimmer gave no verdict in panel round 1 (two timeouts on the full pack); the other three panelists covered every item, and Glimmer spot-checked the applied round 1 items afterwards.

## Token totals for this run (results/api_usage_log.jsonl)

- muse-spark-1.2 (judges): 143,074 (8 calls: judge rounds 1-3 + submission doc)
- muse-spark-1.1 (judges): 134,088 (8 calls: judge rounds 1-3 + submission doc)
- muse-spark-1.3 (panel): 59,483 (7 calls, incl. one empty return that burned an 8,192 cap on reasoning and one retry)
- nvidia/meta/muse-glimmer-30b (panel + spot-checks): 22,701 (7 calls with usage; 2 further calls timed out with no usage returned)
- muse-wonder-1.0 (panel): 10,651 (4 calls)
- gemini-3.5-flash-lite (panel): 5,228 (4 calls)
- Grand total: 375,225 tokens.
