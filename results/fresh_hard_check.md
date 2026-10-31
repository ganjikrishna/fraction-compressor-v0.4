# Fresh-eyes hard check, Oct 31, 2026

Ordered by Vinay on Oct 31, 2026: independent verification of the submission surface by two Meta models never used on this project, **muse-spark-1.2** and **muse-spark-1.1** (Meta Model API), after another project chat falsely confirmed work it never did. Each reviewer worked independently from ONE shared evidence pack (below) plus the five target files; neither saw the other's output. A second pass put each model in a hackathon judge's chair using only what a judge sees (live GitHub repo, submission draft as form text, demo script + narration as the video stand-in; the video itself cannot be watched through the API).

Token totals (all calls logged in results/api_usage_log.jsonl):
- Hard check: spark-1.2 = 90,918; spark-1.1 = 101,769 + 20,055 supplementary completion call = 121,824.
- Judge pass: spark-1.2 = 44,313; spark-1.1 = 43,410.
- Per model: spark-1.2 = 135,231; spark-1.1 = 165,234. Grand total = 300,465.

Coordinator notes on completeness: spark-1.1's first-pass output truncated mid-table (output cap) before the wording-trap sections and verdicts for docs/submission_draft.md, video/narration_v7.txt and PROVENANCE.md, and before any verdict on docs/demo_script.md; a supplementary 1.1 call (logged, purpose "fresh hard check spark-1.1") completed the submission draft, narration and provenance checks, and is included verbatim after 1.1's main output. 1.1 never returned a formal verdict on docs/demo_script.md; its checked claims for that file were all SUPPORTED.

## Verdict summary

| File | spark-1.2 | spark-1.1 |
|---|---|---|
| README.md | FLAG | FLAG |
| docs/submission_draft.md | FLAG | FLAG |
| docs/demo_script.md | FLAG | (no formal verdict returned; all checked claims SUPPORTED) |
| video/narration_v7.txt | FLAG | FLAG |
| PROVENANCE.md | PASS | PASS |
| Cross-file consistency | PASS | PASS |

Judge pass: Stage One gate: spark-1.1 PASS; spark-1.2 FAIL in its gate call, then PASS inside its own scoring call (self-contradiction, see disagreements). Scores (Impact / Meta Tooling / Demo / Depth, weighted total): spark-1.2 = 55 / 82 / 67 / 84, total 70.6; spark-1.1 = 58 / 84 / 81 / 86, total 75.9.

## Flags raised (both reviewers unless noted)

1. **docs/submission_draft.md, LoRA percentages:** "the adapter closes 136% of the gap" (gap closed 1.362) and "vs 139.5% in-style" (1.395) present gap-closed values above 1.0 as percentages of the gap, the exact framing the project's own rule forbids. (The 0.620 out-of-style figure is below 1.0; 1.2 still grouped the sentence as a violation, 1.1 flagged only the >1.0 figures.)
2. **docs/submission_draft.md, rollback sentence:** "rollback is swapping the previous file back in about a tenth of a second" has no file-load-time label, unlike the correctly labeled swap sentence elsewhere in the draft.
3. **Size-claim adjacency (trap b):** README.md "Do it yourself" sentence ("rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller") carries no adjacent lossy disclosure or accuracy figures; spark-1.1 additionally flags the README naming paragraph ("from about 1 GB to about 19 MB"); both flag the draft's "the full patch is 988 MB and ours is 19 MB, about 51x smaller" because the following lossy paragraph gives no numeric accuracies (0.010 vs 0.031).
4. **docs/submission_draft.md, internal inconsistency (CONFIRMED by the coordinator against the file):** the cover note (line 6) says "v5 is the current cut" while section 6 (line 74) says "Current cut is v7, 178.63 seconds, adopted Oct 30."
5. **Narration and demo script swap wording:** "swaps behavior live, well under a second" (narration, twice; demo script) is not labeled as file-load time on the demo machine. Both reviewers flag the narration; 1.2 also flags the demo script, including the on-screen "loaded live in 0.49s" line from the contended recording sitting next to the 0.104 s / 0.087 s figures of record.
6. **Narration trap b (both):** the size claims are spoken without the numeric first-token accuracies; the printed slide line carries them, the transcript does not.
7. **docs/submission_draft.md, NuExtract side-by-side (spark-1.2 only):** "the rank-32 patch, like the base, produces nothing at all" understates the patch (1 clean of 10 in skill_demo.json).

## Disagreements and adjudications

1. **Stage One gate (biggest split):** spark-1.1 rules PASS (Llama 3.2 1B runs in the pipeline as a Meta open-weight subject, Spark is the in-loop recipe designer). Spark-1.2's gate call rules FAIL (Spark's roles are build-time/evaluation, not product runtime; Llama is a benchmark subject, not a runtime integration), but its own scoring call then says "Clear Stage One PASS" and scores Meta Tooling 82. The two models disagree, and 1.2 disagrees with itself across its two calls.
2. **Hotswap attribution FLAG vs ground truth:** both reviewers flagged the draft sentence crediting mlp_behemoth_lite with the parseable Arrival JSON, because the evidence pack summary named only the uniform rank-32 patch. Coordinator check of the full results/hotswap_demo.json: BOTH patches return parseable JSON with exact keys and values (uniform: parseable True, exact True/True; lite: parseable True, exact True/True). The draft's sentence is supported by the underlying file; the flag is an artifact of the pack's one-line summary. Recorded here so the flag is not acted on blindly.
3. **Force-start count wording:** on the draft's "the plain base completes 7 of 10 cleanly (2 failed)", spark-1.2 calls it CONTRADICTED/incomplete (7 + 2 = 9, the 1 partial is dropped); spark-1.1's supplementary pass calls the counts correct (failed count 2 matches, partial implied). The underlying counts (7 clean / 1 partial / 2 failed) are not in dispute.
4. **README trap-b scope:** 1.2 flags one size sentence, 1.1 flags two. Agreement that the file is FLAG either way.
5. **Judge scores:** Demo differs most (67 from 1.2 vs 81 from 1.1; 1.2 penalizes the 0.49 s on-screen swap line and the two-prompt narrowness harder). Impact 55 vs 58, Tooling 82 vs 84, Depth 84 vs 86. Both name the same strongest point (the verification harness with adverse baselines published) and the same weakest point (the trained LoRA adapter dominates at matched bytes wherever training is possible).
6. **Known-good list cross-check:** every known-good headline fact was confirmed by both reviewers against the pack (Qwen lite 23.2%, 19,358,176 B, accuracy 0.010 vs base 0.031; LoRA 1.362; out-of-style 0.620; swap times 0.104 s / 0.087 s file-load; full delta 987,922,432 B). The recovery pilot figures (patch-init 1.136 vs control 1.348) are not claimed in any target file, so there was nothing to contradict (1.1 supplementary notes their absence explicitly). No reviewer contradicted the known-good list on any number both actually checked.
7. **NOT IN EVIDENCE items (both reviewers, same list):** README's 0.28 bits per weight for one large layer, the 8.4 MB / 144 KB layer example, rank-64 (37,044,736 B) and rank-128 (72,265,216 B) skill counts of 2 of 10, the 19,434,400 B Spark-recipe skill entry, the knowledge-bucket split (7.8% vs 3.7%), and pair 2 / pair 3 subset-half gap closeds. These sit in underlying repo files outside the pack's extraction scope (per-bucket sections of the heldout96 JSONs, results/skill_demo_ranks.json); the pack as given cannot confirm or refute them. They are unverified by this check, not shown wrong.

## GitHub live repo section (coordinator-bridged; the API models cannot browse)

Public repo: https://github.com/ganjikrishna/fraction-compressor-v0.4, live head 2ce00363b97fbb278b133cea17852542aee0743d at check time (Oct 31, 2026). The coordinator shallow-cloned the live repo and SHA-256 compared every file against the local tree:
- README.md: live and byte-identical to the local file reviewed. The README the reviewers checked IS the live README judges will open; no separate live text was needed in the pack.
- docs/demo_script.md: live and byte-identical to local.
- video/narration_v7.txt: live and byte-identical to local.
- docs/submission_draft.md and PROVENANCE.md: local-only by design (held for the Nov 2 push). Their absence from the live repo is expected, was stated in the pack, and neither reviewer treated it as a finding.
- Whole tree: all 147 live files exist locally. Only two shared files differ, NOTICE.md and results/api_usage_log.jsonl (local copies carry later additions: an AirLLM prior-art credit and a Qwen2.5-7B model credit in NOTICE.md, newer log entries). Neither is a review target; no pack number is affected.
- Both judge passes were given the live repo file listing and the live README text, and both independently tripped on the same quickstart gap: no requirements.txt and no install step anywhere, while examples/hotswap_demo.py imports the tokenizers package (the gap recorded in docs/judge_path_check.md is still open in the live README).

---

## The shared evidence pack (exact text given to both reviewers)

EVIDENCE PACK: exact numbers extracted by script from the project's result files. "gap closed" = (factored_mean_logprob - base_mean_logprob) / (full_mean_logprob - base_mean_logprob), computed on mean target logprob over 96 held-out questions (combined96), unless a subset is named. Accuracy = first-token accuracy.

== PAIR 1: Qwen2.5-0.5B base vs Qwen2.5-0.5B-Instruct (results/alien_sweep_heldout96.json) ==
full_delta_fp16_bytes = 987,922,432
base: mean logprob -11.150 (exact -11.1498), accuracy 0.031 (0.03125)
full delta (fp16): mean logprob -8.543 (-8.5425), accuracy 0.167 (0.16667)
uniform_rank32 (19,434,496 B): factored mean logprob -11.096, accuracy 0.010 (0.01042), gap closed 0.021 (2.1%)
mlp_behemoth (21,719,776 B, BYTE-UNFAIR, +11.8% over uniform budget, reference only): factored -10.456, accuracy 0.021, gap closed 0.266
mlp_behemoth_lite (19,358,176 B, byte-fair headline): factored -10.545, accuracy 0.010 (0.01042), gap closed 0.232 (23.2%)
Subsets, factored gap closed: lite heldout24 0.095, heldout72 0.304; uniform heldout24 0.016, heldout72 0.023. Lite beats uniform on both subsets.
Factored format all-in effective rate on this pair: about 0.31 bits per weight (0.315 bpw).

== PAIR 2: SmolLM2-360M vs SmolLM2-360M-Instruct (results/second_pair_heldout96.json) ==
full_delta_fp16_bytes = 723,517,440
base: -12.879, accuracy 0.010
full delta: -8.432, accuracy 0.094 (0.09375)
uniform_rank32 (19,705,856 B): factored -8.366, accuracy 0.083, gap closed 1.015
o-down supercharge (27,660,288 B, BYTE-UNFAIR winner): factored -8.040, accuracy 0.094, gap closed 1.088
o-down-rebalanced (19,683,328 B, byte-fair): factored -8.073, accuracy 0.083, gap closed 1.081
NOTE: all gap-closed values for this pair exceed 1.0 (factored configs outscore the full delta itself). They must NOT be described as a recovery fraction or percentage recovered.

== PAIR 3: Llama 3.2 1B vs Llama 3.2 1B-Instruct, Meta open weights (results/third_pair_heldout96.json) ==
full_delta_fp16_bytes = 2,471,493,632
base: -13.718, accuracy 0.010
full delta: -7.387, accuracy 0.219 (0.21875)
uniform_rank32 (25,143,296 B): factored -14.201 (BELOW base), accuracy 0.000, gap closed -0.076 (negative)
no_embed_mlp_spread (34,690,048 B, BYTE-UNFAIR winner): factored -12.123, accuracy 0.031 (0.03125), gap closed 0.252
no_embed_mlp_spread_balanced (24,515,584 B, byte-fair): factored -12.714, accuracy 0.021, gap closed 0.159 (15.9%)

== PAIR 4: Qwen2.5-1.5B vs Qwen2.5-1.5B-Instruct (results/fourth_pair_heldout96.json) ==
full_delta_fp16_bytes = 3,087,138,816 (the patch is about 80x smaller than the full difference)
base: -12.584, accuracy 0.010
full delta: -7.810, accuracy 0.333 (0.33333)
uniform_rank32 (39,046,144 B): factored -6.478, accuracy 0.323 (0.32292), gap closed 1.279
Down Dominator (38,623,232 B, byte-fair winner): factored -6.344, accuracy 0.260 (0.26042), gap closed 1.307
NOTE: gap closed exceeds 1.0 for both configs here; NOT a recovery fraction. Down Dominator beats uniform on combined96 logprob by 0.134 nats.
Subset reversal (mean logprob): heldout24 uniform -3.845 beats Down Dominator -3.996; heldout72 Down Dominator -7.126 beats uniform -7.356. Uniform first-token accuracy 0.323 beats winner 0.260 on combined96.

== BITDELTA BASELINE, Qwen pair (results/bitdelta_baseline.json) ==
Plain 1-bit (BitDelta initialization, sign x mean|delta|, no training): 61,745,828 B, mean logprob -10.013, gap closed 0.436 (43.6%), first-token accuracy 0.0625.
Factored format at matched budget (uniform rank 108, 61,258,816 B): gap closed 0.385 (38.5%).
A plain 1-bit delta cannot fit below its floor price of 61,745,828 B; at the 19.4 MB headline budget only the factored format fits.

== LORA MATCHED-BYTE BASELINE, Qwen pair (results/lora_baseline.json) ==
LoRA rank 17, uniform on all seven block linears x 24 blocks, distilled on 1,500 teacher (full fine-tune) generations, 3 seeds. Adapter size exactly 18,696,192 B fp16.
LoRA combined96: mean logprob -7.599 +/- 0.085, gap closed 1.362 +/- 0.033, first-token accuracy 0.167 to 0.177 across seeds (ties the full fine-tune's 0.167).
Compare: lite factored patch gap closed 0.232, accuracy 0.010; uniform 0.021, accuracy 0.010.
The LoRA adapter BEATS the factored patch at matched bytes. Cost asymmetry: the adapter needed 1,500 teacher generations plus about 8 hours of training (about 11 h total wall); the factored patch is a deterministic zero-query conversion with no training.

== OUT-OF-STYLE LORA CONTROL (results/lora_outofstyle.md) ==
Same LoRA recipe trained on 1,500 GEMINI-authored prompts (different author style), one seed.
Out-of-style adapter: mean logprob -9.5325, gap closed 0.620, first-token accuracy 0.042.
In-style same seed: gap closed 1.395, first-token accuracy 0.167. Lite factored patch: 0.232, 0.010.
Frozen verdict rule: "survives" (0.620 above the 0.60 threshold), narrowly.

== RECOVERY TUNING PILOT, Qwen pair (results/recovery_tuning.md) ==
Brief training (101 steps, about 10% of the LoRA budget) of factored patches, then re-quantized into the exact same 1-bit format at exactly 19,358,176 B.
Untouched lite: gap closed 0.232, accuracy 0.010, mean logprob -10.545.
Patch-init re-quantized: gap closed 1.136, accuracy 0.115, mean logprob -8.189.
Control-init (random) re-quantized: gap closed 1.348, accuracy 0.177, mean logprob -7.634.
Patch advantage over control: -0.213 (the patch start did NOT win).
Share of each run's own fp16 gain surviving re-quantization: patch 62.8%, control 78.7%. One-seed pilot.

== HOT-SWAP DEMO, Qwen pair (results/hotswap_demo.json) ==
One base model loaded once; patches swapped live in factored form. Swap times are FILE-LOAD times measured on the demo machine: to uniform_rank32 0.104 s, to mlp_behemoth_lite 0.087 s.
JSON prompt (Arrival: title/year/director): base output fails json.loads (extra text appended); base + uniform rank-32 patch output parses exactly with exact keys and values.
Knowledge prompt (capital of Japan): base rambles/repeats; patched answers "The capital of Japan is Tokyo." Math prompt (15% of 200): patched answers 30.

== SKILL LIMIT TEST, NuExtract-1.5-tiny on Qwen2.5-0.5B base (results/skill_demo.json) ==
Task: structured JSON extraction, 10 prompts. Full fine-tune (NuExtract): 9/10 parseable = 8 clean / 1 partial / 1 failed. Base alone: 0/10. Uniform rank-32 factored patch: 1 clean / 0 partial / 9 failed.
Force-start control (forcing the fine-tune's actual first token): base 7 clean / 1 partial / 2 failed; base + rank-32 patch 8/1/1, matching the full fine-tune unforced.

== QUANTUM AUDIT ==
41 of 41 checks pass. One IBM job, backend ibm_fez, job ID dbfouq7pc3tc739nvkt0. About 395 s QPU used of a 480 s guardrail.

== PROJECT FACTS (not numbers, for wording checks) ==
- The method compresses the DIFFERENCE a fine-tune makes (the delta), not the model itself. The base model stays full size and must be loaded for a patch to work.
- Prior work: Fraction Compressor v0.1 to v0.3 and the Signet experiments predate the hackathon and live in the older repository github.com/ganjikrishna/fraction-compressor. They must be disclosed as prior work, never claimed as work built during the event (event window Oct 26 to Nov 4, 2026).
- A fifth pair (Qwen2.5-7B) was tested during the event but is DELIBERATELY EXCLUDED from the submission. Any claim, number, or mention presenting 7B results as part of the submission is a FLAG.
- The demo video narration is a Chatterbox voice clone of the author's voice, disclosed in the video and the submission text. The product uses no TTS at runtime.
- Runtime models are Meta models (Muse Spark family). Muse Spark also generated the 96 held-out questions; that dual role is disclosed in the submission draft.
- Author of record: Vinay K Ganji Krishna, sole participant. Ember (AI agent powered by Muse Spark) is credited as collaborator, not a team member.

== GITHUB LIVE REPO (bridged by the coordinator; you cannot browse) ==
Public repo: https://github.com/ganjikrishna/fraction-compressor-v0.4
Live head at check time (Oct 31, 2026): 2ce00363b97fbb278b133cea17852542aee0743d. The coordinator shallow-cloned the live repo and SHA-256 compared every file against the local tree you are reviewing.
- README.md: live on GitHub and BYTE-IDENTICAL to the local README.md in this review. The README text in this pack's targets IS the live README content the judges will open. No separate live copy follows, because there is no difference.
- docs/demo_script.md: live and byte-identical to local.
- video/narration_v7.txt: live and byte-identical to local.
- docs/submission_draft.md and PROVENANCE.md: NOT on GitHub. They are local prep files held for the Nov 2 push. Their absence from the live repo is expected and by design; do NOT flag it as a discrepancy. Judge their content on its own claims.
- Whole tree: all 147 live files exist locally. Only two shared files differ, NOTICE.md and results/api_usage_log.jsonl (the local copies carry later additions: an added prior-art credit and a 7B model credit in NOTICE.md, and newer log entries; neither is a review target, and neither difference changes any number in the evidence pack).
- A separate live check on Oct 31 (record: results/provenance_live_check.md) compared this repo against the OLDER repository github.com/ganjikrishna/fraction-compressor (live head c2bf28d1f52c4905d0b13a78fd93467328ea958f, 32 files): exactly one byte-identical file across the two repos, a generic four-line .gitignore; README.md, NOTICE.md and LICENSE exist in both but with different content; both use the MIT license but the texts are not identical.


---

## Reviewer output: muse-spark-1.2 (hard check, verbatim)

# Fresh hard check reviewer output: muse-spark-1.2

## Chunk: README.md (tokens this call: 19097)

EVIDENCE CHECK — README.md

1. NUMERIC CLAIMS

- Claim: "about 0.31 bits per weight on the Qwen pair" | Evidence: 0.315 bpw (about 0.31) | VERDICT: SUPPORTED (rounded)
- Claim: "from about 1 GB to about 19 MB on the Qwen2.5-0.5B pair" | Evidence: full_delta 987,922,432 B (~0.99 GB) patch 19,358,176 B (~19 MB) | SUPPORTED (rounded)
- Claim: "at 19,358,176 bytes it closes 23.2% of the gap (0.605 of 2.607 nats)" | Evidence: lite 19,358,176 B gap 0.232 (23.2%) , base -11.1498 full -8.5425 delta 2.6073 factored -10.545 delta 0.6048 | SUPPORTED
- Claim: "with first-token accuracy 0.010 (below base 0.031)" | Evidence: lite 0.01042 base 0.03125 | SUPPORTED (rounded)
- Claim: "a distilled LoRA at 18,696,192 bytes, just under the patch's size, closes far more of the gap on these tests (1.362 against 0.232)" | Evidence: LoRA 18,696,192 B gap 1.362 lite 0.232 | SUPPORTED
- Claim: "0.28 bits per weight for one large layer at rank 32" | Evidence: only overall 0.315 bpw given; no per-layer 0.28 in pack | NOT IN EVIDENCE
- Claim: "One layer stored the normal way takes 8.4 MB; our rank-32 file takes 144 KB" | Evidence: no such layer sizes in pack | NOT IN EVIDENCE
- Claim: "rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller" | Evidence: uniform 19,434,496 vs 987,922,432 = 50.83x | SUPPORTED (rounded 51x)
- Claim: "share of questions whose first answer token is exactly right stays low ... (about 1 to 2% on the first pair, about 8 to 9% on the second, 0 to about 3% on the third; the fourth pair ... where the compressed versions reach 26 to 32% against the full patch's own 33.3%)" | Evidence: pair1 1.0% pair2 8.3% pair3 0.0-2.1% pair4 uniform 32.3% Down 26.0% full 33.3% | SUPPORTED
- Claim: "The fine-tune itself passes 9 of 10 test prompts (eight fully clean, one with a single reworded value); the plain base passes 0 of 10" | Evidence: full 9/10 =8/1/1 base 0/10 | SUPPORTED
- Claim: "Our rank-32 patch passes only 1 of 10." | Evidence: uniform rank-32 1/0/9 | SUPPORTED
- Claim: "force that first token and the plain base completes 7 of 10 cleanly" | Evidence: base forced 7/1/2 | SUPPORTED (7 clean)
- Claim: "The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own score: one clean more than the forced base" | Evidence: patch forced 8/1/1 vs base forced 7/1/2, full unforced 8/1/1 | SUPPORTED
- Claim: "a rank-64 patch (37,044,736 bytes) and a rank-128 patch (72,265,216 bytes) each pass 2 of 10" | Evidence: no rank-64/128 sizes/counts in pack | NOT IN EVIDENCE
- Claim: "Muse Spark recipe that puts most of the rank-32 budget into the embedding and the attention output layer (19,434,400 bytes, the same budget) passes 0 of 10" | Evidence: no 19,434,400 entry (uniform is 19,434,496) | NOT IN EVIDENCE
- Claim: "Instruct patch below closes 23.2% of the score gap on 96 fresh questions" | Evidence: lite 23.2% on 96 | SUPPORTED
- Claim: "mlp_behemoth, is byte-unfair: at 21,719,776 bytes it spends 11.8% more than the human recipe's budget" | Evidence: mlp_behemoth 21,719,776 +11.8% over uniform | SUPPORTED
- Claim: "mlp_behemoth_lite: 19,358,176 bytes, fewer than the human uniform rank-32 recipe's 19,434,496 bytes" | Evidence: 19,358,176 < 19,434,496 | SUPPORTED
- Claim: "On all 96, lite closes 23.2% of the gap, against 2.1% for the human recipe" | Evidence: lite 0.232 uniform 0.021 | SUPPORTED
- Claim: "Lite also wins on each half alone: 9.5% vs 1.6% on the original 24 questions, and 30.4% vs 2.3% on the 72 new ones" | Evidence: lite 0.095/0.304 uniform 0.016/0.023 | SUPPORTED
- Claim: "on knowledge questions the human recipe closes more of the gap (7.8% vs 3.7%)" | Evidence: no subset by knowledge in pack | NOT IN EVIDENCE
- Claim: "o-down-rebalanced: 19,683,328 bytes, inside the human recipe's budget of 19,705,856 bytes" | Evidence: 19,683,328 < 19,705,856 | SUPPORTED
- Claim: "it beats the human uniform recipe by 0.293 score points on average" | Evidence: -8.073 vs -8.366 = 0.293 | SUPPORTED
- Claim: "and it wins on both halves of the set separately" (pair2) | Evidence: no halves given for pair2 | NOT IN EVIDENCE
- Claim: "no_embed_mlp_spread, was byte-unfair again: at 34,690,048 bytes it spends 38.0% more than the human recipe's budget of 25,143,296 bytes" | Evidence: (34,690,048-25,143,296)/25,143,296=37.97% ~38.0% | SUPPORTED
- Claim: "no_embed_mlp_spread_balanced: 24,515,584 bytes, inside the budget" | Evidence: 24,515,584 | SUPPORTED
- Claim: "byte-fair variant scores -12.714 against the human uniform recipe's -14.201: it closes 15.9% of the gap, while the human recipe closes -7.6%, which is below the base model itself (-13.718)" | Evidence: -12.714 gap 0.159 -14.201 gap -0.076 base -13.718 | SUPPORTED
- Claim: "The byte-fair variant also wins on each half alone: 20.0% vs -1.7% on the original 24 questions, and 14.8% vs -9.1% on the 72 new ones" (pair3) | Evidence: no halves for pair3 in pack | NOT IN EVIDENCE
- Claim: "first-token accuracy stays low ... 2.1% for the byte-fair variant, against 21.9% for the full patch itself" (pair3) | Evidence: balanced 0.021 full 0.21875 | SUPPORTED
- Claim: "recipes were priced ... human recipe's budget of 39,046,144 bytes. The search winner, Down Dominator, is byte-fair itself at 38,623,232 bytes" | Evidence: uniform 39,046,144 Down 38,623,232 | SUPPORTED
- Claim: "Down Dominator scores -6.344 against the human uniform recipe's -6.478: it still wins, but by about 0.13 score points" | Evidence: difference 0.134 | SUPPORTED (rounded)
- Claim: "human recipe wins the first 24 questions; Down Dominator wins the 72 newer ones" (pair4 heldout24 -3.845 vs -3.996, heldout72 -7.126 vs -7.356) | Evidence: matches | SUPPORTED
- Claim: "every compressed version outscores the full patch itself (full patch -7.810), so the gap-closed percentage goes above 100% (130.7% against 127.9%)" | Evidence: Down 1.307 uniform 1.279 full -7.810 | SUPPORTED
- Claim: "human recipe's first-token accuracy on the 96 is 32.3%, against Down Dominator's 26.0% and the full patch's own 33.3%" | Evidence: uniform 0.32292 Down 0.26042 full 0.33333 | SUPPORTED
- Claim: "a roughly 39 MB patch against a 3,087,138,816-byte full patch, about 79x smaller" | Evidence: 3,087,138,816 / 39,046,144 =79.0x (pack says about 80x) | SUPPORTED (rounded)
- Claim: "plain 1-bit delta cannot go below 1 bit per weight, which on the first pair's 169 matrices is 61,745,828 bytes" | Evidence: 61,745,828 B floor | SUPPORTED
- Claim: "BitDelta initialization ... closes 43.6% of the gap ... against 38.5% for our factored format at uniform rank 108 priced just under it (61,258,816 bytes)" | Evidence: BitDelta 0.436 rank108 0.385 61,258,816 | SUPPORTED
- Claim: "below about 62 MB on this pair the factored format fits where the plain one cannot, and at about 62 MB the plain initialization wins" | Evidence: floor 61,745,828 | SUPPORTED (rounded)
- Claim: "41 of 41 checks passed" (quantum audit) | Evidence: 41 of 41 pass | SUPPORTED
- Claim: "live hot-swap (0.104 s and 0.087 s, file-load times on the demo machine, in the recorded demo)" | Evidence: to uniform_rank32 0.104s to lite 0.087s FILE-LOAD times demo machine | SUPPORTED
- Claim: "about a tenth of a second (examples/hotswap_demo.py)" | Evidence: 0.104/0.087 ~0.1s | SUPPORTED (rounded)
- Claim: "October 26 to November 4, 2026" event window | Evidence: project facts Oct 26-Nov 4 | SUPPORTED

2. WORDING TRAPS

a. Gap-closed >1.0 as recovery fraction: README states for pair2 "every compressed version scores better than the full patch itself, so the gap-closed percentage goes above 100% here. That means the percentage is NOT a share ..." and for pair4 "every compressed version outscores the full patch itself ... so the gap-closed percentage goes above 100% (130.7% against 127.9%) and is NOT a share ..." | PASS – correctly avoids presenting >1.0 as recovery percentage, gives raw margin instead (0.293 and 0.13).
b. Size claims adjacency to lossy + accuracy: Intro paragraph DOES pair 19,358,176 B with "lossy, training-free" and "first-token accuracy 0.010 (below base 0.031)" – compliant. SECOND size claim "rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes ... about 51x smaller." appears under "Do it yourself" with NO adjacent lossy disclosure or accuracy figures. | FLAG – trap violated.
c. Swap times labeled as file-load on demo machine not general speed: README says "0.104 s and 0.087 s, file-load times on the demo machine, in the recorded demo" – correctly labeled | PASS
d. 7B / Qwen2.5-7B fifth pair: No mention of 7B appears in README | PASS
e. Prior work predating event: README "Prior art" + "Built during the hackathon ... Pre-existing work (not part of this submission): Fraction Compressor v0.1 to v0.3 and the Signet delta-transfer experiments live in the original repository ... were designed and validated there before the event." – correctly disclosed as prior, not claimed as built during event | PASS
f. Compresses delta not whole model: README "this tool does not compress a model. It compresses the difference a fine-tune makes ... The base model stays its full size and has to be loaded" and "This shrinks only the patch" | PASS

3. INTERNAL INCONSISTENCY
No contradictory duplicate values found. All byte counts and percentages consistent where repeated. Minor rounding differences (79x vs evidence "about 80x") are within rounding tolerance.

4. VERDICT for this file: FLAG

For every FLAG, exact sentence and fix:

- FLAG 1 – Trap b violation:
Exact sentence: "On the model pair used in this repo's benchmark (Qwen2.5-0.5B base and Instruct), rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller."
Fix: Append the required disclosure adjacent to the size claim in the same sentence/parenthetical, e.g.: "On the model pair used in this repo's benchmark (Qwen2.5-0.5B base and Instruct), rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller — lossy; first-token accuracy 0.010 vs base 0.031 on this pair (see limit above) —."
Without this adjacency the 51x claim is isolated from the mandatory lossy/accuracy disclosure.

Note: Claims marked NOT IN EVIDENCE above (0.28 bpw per layer, 8.4 MB / 144 KB, rank-64 37,044,736 B / rank-128 72,265,216 B, 19,434,400 B recipe, 7.8% vs 3.7% knowledge split, subset halves for pairs 2 and 3) are not in the provided evidence pack and must be sourced or removed; they are not flagged as traps but require citation.



## Chunk: docs/submission_draft.md (tokens this call: 21966)

Independent Fact-Check — docs/submission_draft.md vs EVIDENCE PACK
Judged ONLY against Evidence Pack. No outside knowledge.

### 1. NUMERIC CLAIMS — line by line

**Cover note / meta:**

1. Claim: "This repository (fraction-compressor-v0.4) was created on October 26, 2026, the first day of the event"
   Evidence: Event window Oct 26 to Nov 4, 2026 (Project Facts). Creation date Oct 26 not separately script-extracted but consistent with window.
   Verdict: **SUPPORTED** (within window; rounding/date as fact)

2. Claim: "The form map (read Oct 26, 2026) shows no character limit"
   Evidence: No evidence value for form map character limit
   Verdict: **NOT IN EVIDENCE**

3. Claim: "LoRA matched-byte baseline: landed Oct 29, approved by Vinay the same day"
   Evidence: No dated landing in pack; LoRA baseline exists in results/lora_baseline.json but date not in pack
   Verdict: **NOT IN EVIDENCE**

4. Claim: "The 7B streamed test is not claimed anywhere in this draft."
   Evidence: Project Facts: fifth pair (Qwen2.5-7B) was tested but is DELIBERATELY EXCLUDED from submission
   Verdict: **SUPPORTED** — disclosure of exclusion, no numbers claimed

5. Claim: "Panel review changelog (Oct 28, 2026...)" , "uniform recipe on the Qwen pair now reads 'at a slightly larger byte budget'" , "BitDelta comparison now reads 'at a matched budget (61,258,816 B against the 61,745,828 B floor)'"
   Evidence: Pack does not contain panel changelog dates/text; byte values themselves are in evidence (see #20)
   Verdict: Dates/text **NOT IN EVIDENCE**; byte values **SUPPORTED** (see below)

6. Claim: "the 1.5B result now spells out the subset split (uniform wins heldout24, the winning recipe wins heldout72)"
   Evidence: Pair 4 subset reversal: heldout24 uniform -3.845 beats -3.996, heldout72 winner -7.126 beats -7.356
   Verdict: **SUPPORTED**

7. Claim: "skill numbers now read '1 clean of 10', base force-start '(2 failed)' added, and patch force-start '8 clean, 1 partial, and 1 failed of 10, matching the full fine-tune's own unforced score (8 clean, 1 partial, 1 failed)'"
   Evidence: skill_demo.json: Full fine-tune 9/10 parseable = 8 clean/1 partial/1 failed; base 0/10; uniform rank-32 1 clean/0 partial/9 failed; force-start base 7 clean/1 partial/2 failed; base+patch 8/1/1 matching full unforced 8/1/1
   Verdict: **SUPPORTED** (rounded/partial accounting correct)

8. Claim: "v5 is the current cut" (cover note placeholder §3)
   Evidence: Section 6 says "Current cut is v7" ; no pack value for video version
   Verdict: **NOT IN EVIDENCE** and **INTERNAL INCONSISTENCY** (see §3)

**Section 4 — What it is / Why it matters:**

9. Claim: "priced at about 0.31 bits per weight all in (signs, factors, and scales together)"
   Evidence: Factored format all-in effective rate on this pair: about 0.31 bits per weight (0.315 bpw)
   Verdict: **SUPPORTED (rounded)**

10. Claim: "On the Qwen2.5-0.5B pair, the full patch is 988 MB and ours is 19 MB, about 51x smaller."
    Evidence: full_delta_fp16_bytes = 987,922,432 (= ~988 MB); winner mlp_behemoth_lite = 19,358,176 B (= ~19.36 MB); ratio 51.04x
    Verdict: **SUPPORTED (rounded)**

11. Claim: "patches swap in and out of one running base model live, in about 0.1 seconds (file-load time on the demo machine; the two recorded swaps measured 0.104 s and 0.087 s)"
    Evidence: hotswap_demo.json: Swap times are FILE-LOAD times on demo machine: to uniform_rank32 0.104 s, to mlp_behemoth_lite 0.087 s
    Verdict: **SUPPORTED** and correctly labeled as file-load times (Trap c PASS for this sentence)

12. Claim: "With patches, an update is a 19 MB file"
    Evidence: 19,358,176 B (≈19 MB) headline lite patch
    Verdict: **SUPPORTED (rounded)**

13. Claim: "on our main pair it closes 23.2% of the gap to the full fine-tune"
    Evidence: mlp_behemoth_lite gap closed 0.232 (23.2%)
    Verdict: **SUPPORTED**

14. Claim: "its first-token accuracy sits below the base model's own"
    Evidence: lite accuracy 0.010 (0.01042) vs base 0.031 (0.03125)
    Verdict: **SUPPORTED** (qualitative; numbers omitted here — see Trap b)

15. Claim: "rollback is swapping the previous file back in about a tenth of a second"
    Evidence: 0.104 s / 0.087 s file-load times ≈0.1 s, but evidence requires label "file-load time on the demo machine, not general swap/inference"
    Verdict: **SUPPORTED numerically but MISLABELED** — no "file-load time" qualifier in this sentence (Trap c)

**Results paragraph:**

16. Claim: "On 96 fresh questions the search never saw, the headline recipe closes 23.2% of the score gap between base and full fine-tune on the Qwen pair"
    Evidence: combined96 gap closed 0.232
    Verdict: **SUPPORTED**

17. Claim: "against 2.1% for a plain uniform recipe at a slightly larger byte budget."
    Evidence: uniform_rank32 gap 0.021 (2.1%), bytes 19,434,496 B vs lite 19,358,176 B (+76,320 B, +0.39%)
    Verdict: **SUPPORTED**

18. Claim: "On Meta's Llama 3.2 1B pair, recovery is weaker (15.9%)"
    Evidence: no_embed_mlp_spread_balanced gap 0.159 (15.9%)
    Verdict: **SUPPORTED**

19. Claim: "the uniform recipe scored below the base model itself, worse than no patch at all."
    Evidence: uniform -14.201 vs base -13.718, gap -0.076 negative
    Verdict: **SUPPORTED**

20. Claim: "On the Qwen2.5-1.5B scale test, the winning recipe's patch is about 80x smaller than the full patch"
    Evidence: full 3,087,138,816 B / winner 38,623,232 B = 79.9x; pack explicitly states "about 80x smaller"
    Verdict: **SUPPORTED**

21. Claim: "beats the uniform recipe by 0.134 nats on the combined 96 questions"
    Evidence: uniform -6.478 vs winner -6.344 difference 0.134 nats
    Verdict: **SUPPORTED**

22. Claim: "the uniform recipe wins the heldout24 subset and the winning recipe wins heldout72."
    Evidence: heldout24 uniform -3.845 beats -3.996 ; heldout72 winner -7.126 beats -7.356
    Verdict: **SUPPORTED**

23. Claim: "Where a compressed patch outscores the full patch, the gap-closed figure goes above 1.0 and we never call it a recovery fraction; the raw score margin is the honest measure there."
    Evidence: Pair 2 and Pair 4 NOTE: gap >1.0 must NOT be described as recovery fraction
    Verdict: **SUPPORTED** (correct disclosure)

**Full table (combined 96, mean target logprob in nats, accuracy = first-token accuracy):**

24. Qwen base -11.150 / 0.031
    Evidence: -11.150 (exact -11.1498) / 0.031 (0.03125)
    Verdict: **SUPPORTED (rounded)**

25. Qwen full delta -8.542 / 0.167 / 987,922,432 B
    Evidence: -8.543 (-8.5425) / 0.167 (0.16667) / 987,922,432 B
    Verdict: **SUPPORTED (rounded: -8.542 vs -8.5425)**

26. Qwen uniform rank-32 -11.096 / 0.010 / 19,434,496 B
    Evidence: -11.096 / 0.010 (0.01042) / 19,434,496 B
    Verdict: **SUPPORTED**

27. Qwen winner mlp_behemoth_lite -10.545 / 0.010 / 19,358,176 B
    Evidence: -10.545 / 0.010 (0.01042) / 19,358,176 B
    Verdict: **SUPPORTED**

28. SmolLM2 base -12.879 / 0.010
    Evidence: -12.879 / 0.010
    Verdict: **SUPPORTED**

29. SmolLM2 full delta -8.432 / 0.094 / 723,517,440 B
    Evidence: -8.432 / 0.094 (0.09375) / 723,517,440 B
    Verdict: **SUPPORTED**

30. SmolLM2 uniform -8.366 / 0.083 / 19,705,856 B
    Evidence: -8.366 / 0.083 / 19,705,856 B
    Verdict: **SUPPORTED**

31. SmolLM2 winner o-down-rebalanced -8.073 / 0.083 / 19,683,328 B
    Evidence: -8.073 / 0.083 / 19,683,328 B
    Verdict: **SUPPORTED**

32. Llama base -13.718 / 0.010
    Evidence: -13.718 / 0.010
    Verdict: **SUPPORTED**

33. Llama full delta -7.387 / 0.219 / 2,471,493,632 B
    Evidence: -7.387 / 0.219 (0.21875) / 2,471,493,632 B
    Verdict: **SUPPORTED**

34. Llama uniform -14.201 / 0.000 / 25,143,296 B
    Evidence: -14.201 / 0.000 / 25,143,296 B
    Verdict: **SUPPORTED**

35. Llama winner no_embed_mlp_spread_balanced -12.714 / 0.021 / 24,515,584 B
    Evidence: -12.714 / 0.021 / 24,515,584 B
    Verdict: **SUPPORTED**

36. Qwen 1.5B base -12.584 / 0.010
    Evidence: -12.584 / 0.010
    Verdict: **SUPPORTED**

37. Qwen 1.5B full delta -7.810 / 0.333 / 3,087,138,816 B
    Evidence: -7.810 / 0.333 (0.33333) / 3,087,138,816 B
    Verdict: **SUPPORTED**

38. Qwen 1.5B uniform -6.478 / 0.323 / 39,046,144 B
    Evidence: -6.478 / 0.323 (0.32292) / 39,046,144 B
    Verdict: **SUPPORTED**

39. Qwen 1.5B winner Down Dominator -6.344 / 0.260 / 38,623,232 B
    Evidence: -6.344 / 0.260 (0.26042) / 38,623,232 B
    Verdict: **SUPPORTED**

**Flags on that table:**

40. Claim: "On SmolLM2-360M and Qwen2.5-1.5B the factored patches outscore the full delta itself, so gap closed exceeds 1.0 there (SmolLM2: uniform 1.015, winner 1.081; 1.5B: uniform 1.279, winner 1.307) and is not a recovery fraction"
    Evidence: Pair2 uniform 1.015 winner 1.081 ; Pair4 uniform 1.279 winner 1.307 ; NOTE says must NOT be recovery fraction
    Verdict: **SUPPORTED** and correctly NOT presented as percentage recovered (Trap a PASS for this paragraph)

41. Claim: "On Llama, the uniform recipe scores below the base model itself (-14.201 against -13.718, gap closed -0.076) with zero first-token accuracy."
    Evidence: -14.201 vs -13.718 gap -0.076 accuracy 0.000
    Verdict: **SUPPORTED**

42. Claim: "uniform wins the heldout24 subset (-3.845 against -3.996) and the winner wins heldout72 (-7.126 against -7.356), and uniform's first-token accuracy (0.323) beats the winner's (0.260)."
    Evidence: exactly those subset logprobs and accuracies
    Verdict: **SUPPORTED**

**Side by side demos:**

43. Claim: "Asked for a strict JSON object (the title, year, and director of the film Arrival, and nothing else), the base model writes the object and then rambles on with stray text, so its answer fails parsing; with the mlp_behemoth_lite patch swapped in, the same base returns exactly the object, parseable with the exact keys and values (results/hotswap_demo.json)."
    Evidence: hotswap_demo.json: JSON prompt: base fails json.loads (extra text appended); base + uniform rank-32 patch parses exactly. No evidence that mlp_behemoth_lite achieves parse.
    Verdict: **NOT IN EVIDENCE / CONTRADICTED on attribution** — evidence supports uniform_rank32, not mlp_behemoth_lite

44. Claim: "on a NuExtract extraction prompt (pull the product, price, weight, and maker out of a short product description), the full fine-tune answers with clean JSON while the rank-32 patch, like the base, produces nothing at all"
    Evidence: skill_demo.json: Full 9/10 parseable (8 clean/1 partial/1 failed); base 0/10; uniform rank-32 1 clean/0 partial/9 failed — not "nothing at all"
    Verdict: **CONTRADICTED** — understates patch (1 clean) and overstates failure

45. Claim: "On a real JSON extraction fine-tune (NuExtract-1.5-tiny on the Qwen pair), the fine-tune starts correctly on 9 of 10 prompts, the base on 0 of 10, and our rank-32 patch on 1 clean of 10."
    Evidence: Full 9/10 parseable, base 0/10, patch 1 clean/0 partial/9 failed
    Verdict: **SUPPORTED** (9 of 10 = 8 clean +1 partial)

46. Claim: "force the fine-tune's first token and the plain base completes 7 of 10 cleanly (2 failed)"
    Evidence: Force-start base: 7 clean /1 partial /2 failed (total 10)
    Verdict: **CONTRADICTED (incomplete)** — claim omits the 1 partial; 7+2=9 ≠10. Rounded sum misstates evidence.

47. Claim: "Under the same forced start, the patch completes 8 clean, 1 partial, and 1 failed of 10, matching the full fine-tune's own unforced score (8 clean, 1 partial, 1 failed)."
    Evidence: base+patch force-start 8/1/1 matches full unforced 8/1/1
    Verdict: **SUPPORTED**

**Known limits / BitDelta:**

48. Claim: "A plain 1-bit delta (the BitDelta initialization) cannot go below about 62 MB on the first pair, and at that floor it closes 43.6% of the gap against 38.5% for our factored format at a matched budget (61,258,816 B against the 61,745,828 B floor)."
    Evidence: BitDelta 61,745,828 B gap 0.436 (43.6%); factored at matched budget 61,258,816 B gap 0.385 (38.5%); floor 61,745,828 B cannot fit below
    Verdict: **SUPPORTED**

49. Claim: "At 19 MB our format fits below BitDelta's floor, where no plain 1-bit patch fits at all"
    Evidence: headline 19,358,176 B < 61,745,828 B floor; "cannot fit below floor" in evidence
    Verdict: **SUPPORTED**

**Technical depth — LoRA comparisons:**

50. Claim: "a LoRA adapter distilled ... to 18,696,192 bytes, just under the factored patch's 19,358,176 bytes."
    Evidence: LoRA adapter exactly 18,696,192 B fp16
    Verdict: **SUPPORTED**

51. Claim: "On the same 96 questions the adapter closes 136% of the gap on average across three seeds, against the patch's 23%, and it ties the full fine-tune on first-token accuracy."
    Evidence: LoRA gap 1.362 ±0.033 (136.2%), lite patch 0.232 (23.2%), LoRA accuracy 0.167–0.177 ties full 0.167. However gap >1.0.
    Verdict: **NUMERICALLY SUPPORTED but WORDING TRAP a VIOLATION** — 136% (>1.0) presented as "closes ...% of the gap" / percentage recovered. Must not be recovery fraction; raw gap 1.36 and outscores-full-delta phrasing required.

52. Claim: "the adapter needed 1,500 teacher generations and about 8 hours of training"
    Evidence: 1,500 teacher generations + about 8 hours training (about 11 h total wall); patch deterministic zero-query conversion with no training
    Verdict: **SUPPORTED**

53. Claim: "while the patch is a deterministic conversion of weights already on disk, with no training and no queries."
    Evidence: factored patch is deterministic zero-query conversion with no training
    Verdict: **SUPPORTED**

54. Claim: "Distilled on Gemini-authored prompts ... the same 18.7 MB LoRA adapter still closes 62.0% of the base-to-full gap on the Spark-written 96 (vs 139.5% in-style and 23.2% for the factored patch)"
    Evidence: Out-of-style gap 0.620 (62.0%), in-style same seed 1.395 (139.5%), lite 0.232 (23.2%)
    Verdict: **NUMERICALLY SUPPORTED but WORDING TRAP a VIOLATION** — both 62% and especially 139.5% (>1.0) presented as "closes ...%". 1.395 must not be percentage recovered.

**Other numeric details:**

55. Claim: "178.63 seconds, adopted Oct 30" (Section 6 video length)
    Evidence: No video length in Evidence Pack
    Verdict: **NOT IN EVIDENCE**

56. Claim: "engagement counts through November 8 end of day" (Section 11)
    Evidence: No date in pack for viral counting window
    Verdict: **NOT IN EVIDENCE**

### 2. WORDING TRAPS

a. **Gap >1.0 as recovery fraction — VIOLATED**
   - SmolLM2/1.5B flags correctly handled (PASS).
   - LoRA sentences violate: "closes 136% of the gap" (gap 1.362), "still closes 62.0% ... (vs 139.5% in-style)" — both gaps >1.0 (1.362, 1.395) presented as percentage recovered. Evidence NOTE: >1.0 means factored config outscored full delta itself, not a recovery fraction. Must use "gap closed 1.36, outscoring full delta by X nats" language.

b. **Size claims next to lossy disclosure + accuracy numbers — VIOLATED**
   - Size claim isolated: "On the Qwen2.5-0.5B pair, the full patch is 988 MB and ours is 19 MB, about 51x smaller." appears in "What it is" paragraph.
   - Lossy disclosure "closes 23.2% ... first-token accuracy sits below the base" is in next paragraph with NO numeric accuracies (requires "patch 0.010 vs base 0.031"). The required adjacency and numeric figures are missing.

c. **Swap times labeled as file-load times — PARTIAL VIOLATION**
   - Correct in: "in about 0.1 seconds (file-load time on the demo machine; the two recorded swaps measured 0.104 s and 0.087 s)" — PASS.
   - Violated in: "rollback is swapping the previous file back in about a tenth of a second" — no file-load label.

d. **7B fifth pair — PASS (with note)**
   - No result numbers claimed. Sentence "The 7B streamed test is not claimed..." is an exclusion disclosure, not a result claim. No FLAG under trap d, but any addition of 7B numbers would be FLAG.

e. **Prior work disclosure — PASS**
   - Correctly states v0.1–v0.3 and Signet experiments live in older repo github.com/ganjikrishna/fraction-compressor, predate event, not claimed as event work; event-built items listed as Oct 26–Nov 2.

f. **Delta vs model compression — PASS**
   - Explicit: "this tool does not compress the model itself; the base model stays full size, and what is compressed is only the fine-tune's difference from it." No implication whole model compressed.

### 3. INTERNAL INCONSISTENCY

- **Video cut version:** Cover note says "v5 is the current cut" vs Section 6 says "Current cut is v7, 178.63 seconds". Two different values for same quantity within one file.
- **Hotswap attribution inconsistency:** Table and hotswap demo describe uniform_rank32 as parsing success; side-by-side prose attributes success to mlp_behemoth_lite — contradictory attribution within file/evidence.
- **Skill demo counting:** "7 of 10 cleanly (2 failed)" sums to 9, missing the 1 partial documented elsewhere in same file (8/1/1 framework), creating internal sum inconsistency.

### 4. VERDICT FOR THIS FILE: **FLAG**

**Exact sentences requiring fix:**

1. **Sentence:** "On the Qwen2.5-0.5B pair, the full patch is 988 MB and ours is 19 MB, about 51x smaller."
   **Fix:** Keep size but immediately append lossy + numeric accuracy disclosure in same paragraph/sentence, e.g.: "On the Qwen2.5-0.5B pair, the full patch is 988 MB (987,922,432 B) and the factored patch is 19,358,176 B (~19 MB, about 51× smaller). This 19 MB patch is lossy: it closes 23.2% of the base-to-full gap and its first-token accuracy is 0.010 vs the base's 0.031, below the base itself."

2. **Sentence:** "rollback is swapping the previous file back in about a tenth of a second"
   **Fix:** "rollback is swapping the previous file back in about a tenth of a second (file-load time on the demo machine; measured swaps 0.104 s and 0.087 s, not general inference speed)"

3. **Sentence:** "On the same 96 questions the adapter closes 136% of the gap on average across three seeds, against the patch's 23%, and it ties the full fine-tune on first-token accuracy."
   **Fix:** Do NOT present >1.0 as percentage recovered. Change to: "On the same 96 questions the adapter outscores the full fine-tune (gap closed 1.36 ±0.03, mean logprob -7.599 vs full -8.543) against the patch's gap closed 0.232 (23.2%), and it ties the full fine-tune on first-token accuracy (0.167–0.177 vs full 0.167)."

4. **Sentence:** "Distilled on Gemini-authored prompts in a deliberately different style, the same 18.7 MB LoRA adapter still closes 62.0% of the base-to-full gap on the Spark-written 96 (vs 139.5% in-style and 23.2% for the factored patch)"
   **Fix:** "Distilled on Gemini-authored prompts ... the same 18.7 MB LoRA adapter achieves gap closed 0.620 on the Spark-written 96 vs gap closed 1.395 in-style (both out-of-style 0.62 is recovery, 1.395 means it outscores the full delta) and 0.232 (23.2%) for the factored patch — raw gap/mean-logprob is the measure where gap exceeds 1.0."

5. **Sentence:** "with the mlp_behemoth_lite patch swapped in, the same base returns exactly the object, parseable with the exact keys and values (results/hotswap_demo.json)."
   **Fix:** Align with evidence: "with the uniform rank-32 patch swapped in (0.104 s file-load), the same base returns exactly the object, parseable with the exact keys and values (results/hotswap_demo.json; lite patch swap 0.087 s file-load not documented for this JSON prompt)."

6. **Sentence:** "while the rank-32 patch, like the base, produces nothing at all, because the behavior never gets past its first token"
   **Fix:** "while the rank-32 patch produces 1 clean of 10 (base 0 of 10), effectively failing to transfer the skill because the behavior rarely gets past its first token"

7. **Sentence:** "force the fine-tune's first token and the plain base completes 7 of 10 cleanly (2 failed)"
   **Fix:** "force the fine-tune's first token and the plain base completes 7 clean, 1 partial, and 2 failed of 10"

8. **Internal inconsistency — Sentence in cover note:** "v5 is the current cut"
   **Fix:** Change to "v7 is the current cut (178.63 seconds, adopted Oct 30)" to match Section 6, or remove version from cover note.

All other numeric claims are SUPPORTED (or SUPPORTED rounded) against Evidence Pack byte counts, gaps, logprobs, and accuracies.



## Chunk: docs/demo_script.md + video/narration_v7.txt + PROVENANCE.md (tokens this call: 21295)

As independent fact-checker judging ONLY Evidence Pack vs target file text:

### 1. docs/demo_script.md

#### A. Numeric Claims

> Quote as written | Evidence value | Verdict
> "Target 178 to 179.5 seconds" | No evidence value (video length not in pack) | NOT IN EVIDENCE
> "480 words" | No evidence | NOT IN EVIDENCE
> "178.63 seconds (v6: 178.63, v5: 178.85, v4: 178.87)" | No evidence (pack has no video durations) | NOT IN EVIDENCE
> "loudness spread 0.86 LU ... spread down to 0.40 LU ... -16.0 LUFS ... -16.03 LUFS" | No evidence | NOT IN EVIDENCE
> "atempo 0.886" / "pauses 1.68s and 1.79s" / "about 1.3s" / "over 0.34s capped at 0.34s" / "0.676s to 0.34s now 0.633s" etc | No evidence | NOT IN EVIDENCE
> "about 0.3 bits per weight, all in" | Evidence: about 0.31 bits per weight (0.315 bpw) on Qwen pair | SUPPORTED (rounded)
> "full difference file at 987,922,432 bytes" | Evidence full_delta_fp16_bytes = 987,922,432 | SUPPORTED
> "patch byte price 19,434,496 B (the uniform rank-32 patch)" | Evidence uniform_rank32 = 19,434,496 B | SUPPORTED
> "full delta 987,922,432 B, 50.8x smaller" | Evidence 987,922,432 / 19,434,496 = 50.83x | SUPPORTED (rounded)
> "well under a second" (swap) | Evidence HOT-SWAP DEMO swap times are FILE-LOAD times: 0.104s to uniform_rank32, 0.087s to mlp_behemoth_lite on demo machine. "well under a second" is true for both but see Wording Trap c | SUPPORTED (value true) but mis-labeled (see below)
> "0.104s transcript of record and the 0.49s contended recording" | Evidence 0.104s matches uniform_rank32 file-load 0.104s; 0.49s has no evidence entry | 0.104s SUPPORTED, 0.49s NOT IN EVIDENCE (explained as contended recording, not claimed as file-load time in pack)
> "loaded live in 0.49s" (ON SCREEN boxed line) | Evidence file-load times are 0.104s/0.087s, not 0.49s | NOT IN EVIDENCE and contradicts pack if claimed as file-load time (file correctly notes it as contended vs transcript)
> "full difference 988 MB vs patch 19 MB, '51x smaller'" | Evidence 987,922,432 ~=988 MB, patch ~19.3-19.4 MB, ratio ~50.8-51.0x | SUPPORTED (rounded)
> "on 96 fresh questions, Spark's recipe ... closes 23.2% ... human recipe, 2.1%" | Evidence mlp_behemoth_lite gap 0.232=23.2%, uniform gap 0.021=2.1% on combined96 (96 held-out) | SUPPORTED (percentage matches fraction)
> "winner patch (mlp_behemoth_lite) 19,358,176 bytes" | Evidence 19,358,176 B | SUPPORTED
> "uniform rank-32 patch 19,434,496 bytes" | Evidence 19,434,496 B | SUPPORTED
> "Qwen2.5-1.5B scale test, Spark recipe 38,623,232 bytes inside the 39,046,144 byte budget, +0.134 nats, about 80x smaller" | Evidence PAIR 4: Down Dominator 38,623,232 B, uniform 39,046,144 B, delta logprob 0.134 nats (-6.344 vs -6.478), full delta 3,087,138,816 /38,623,232=79.94x | SUPPORTED
> "at 61,745,828 bytes a plain 1-bit patch closes 43.6% vs our 38.5%; at 19 MB no plain 1-bit patch fits at all" | Evidence BitDelta 61,745,828 B gap 0.436=43.6%, factored at matched budget gap 0.385=38.5%, floor price 61,745,828 B, factored fits at 19.4 MB | SUPPORTED
> "First-token accuracy: patch 0.010 vs base 0.031" (printed line described in V7 changes) | Evidence Qwen pair base accuracy 0.03125=0.031, mlp_behemoth_lite/uniform accuracy 0.01042=0.010 | SUPPORTED
> "all forty-one checks passed" | Evidence QUANTUM AUDIT 41 of 41 checks pass | SUPPORTED

Wording traps:
a. Gap >1.0 as recovery fraction: File does NOT present SmolLM2 (gap 1.015-1.081) or Qwen1.5B (gap 1.279/1.307) as percentage recovered. It says "Same pattern on SmolLM2." (no percentage) and for 1.5B gives "+0.134 nats, inside budget" not a percentage. PASS.
b. Size claims next to lossy disclosure + accuracy figures: PASS - size claims (19 MB/988 MB/51x) in 0:00 and 1:48 blocks are accompanied by (i) spoken disclosure in V7 "Honestly, the patch's first-word accuracy stays below the base model's own: this is probability recovery, not solved tasks." described in file, and (ii) printed line "First-token accuracy: patch 0.010 vs base 0.031" added to numbers slide per V7 changes paragraph. File also contains delta-vs-model clarification "To be clear: it does not compress the model. Only the fine-tune's change gets small. The base stays full size, loaded once." PASS.
c. Swap times labeling: PARTIAL FLAG - File correctly avoids stating "swap =0.104s" as general inference speed and uses "well under a second." However the file does quote "0.104s transcript of record" and "loaded live in 0.49s" without the required qualifier "file-load times on the demo machine." Evidence pack defines those numbers as FILE-LOAD times on demo machine. See FLAG below.
d. 7B / Qwen2.5-7B fifth pair: No claim, number or mention. PASS (absent as required).
e. Prior work disclosure: PASS - "our earlier compressor work" listed under "Published before" and narration "one-bit delta compression is published, BitDelta and Delta-CoMe, and our work predates this week. Built fresh this week: factored runtime..." correctly separates pre-event work (Fraction Compressor v0.1-0.3, Signet) from event work.
f. Delta vs model: PASS - explicit "To be clear: it does not compress the model. Only the fine-tune's change gets small." and "a fine-tune is a base plus a patch: their difference. ... It keeps a fraction: nought point three bits per weight, all in."

Internal inconsistency: None. Different durations refer to different cuts (v4/v5/v6/v7). Different patch sizes (19,434,496 vs 19,358,176) refer to uniform vs lite winner. 0.104s vs 0.49s explained as transcript vs contended recording, not same quantity.

**VERDICT for docs/demo_script.md: FLAG**

* FLAG sentence 1 (Trap c): `"It plugs into the base and swaps behavior live, well under a second."` and `"Watch: the patch swaps in live, well under a second."` + historical note `"(true for both the 0.104s transcript of record and the 0.49s contended recording;"`
  * Fix: Label as file-load time on demo machine: `"It plugs into the base and swaps behavior live, file-load well under a second on the demo machine (0.104s to load uniform_rank32, 0.087s to load mlp_behemoth_lite – file-load times, not inference speed)."` and on-screen caption should read `">>> SWAP: ... loaded live in 0.104s (file-load time on demo machine)"` (or 0.087s for lite). Do not present 0.49s without qualifier "contended recording, not the file-load measurement of record (0.104s/0.087s)". 

If strict adjacency is not required to be in file text, file would be PASS after that labeling fix. No other numeric contradiction.

---

### 2. video/narration_v7.txt

#### A. Numeric Claims

> "about nineteen megabytes instead of about a gigabyte." | Evidence patch ~19.3 MB, full 987,922,432 ~=0.988 GB | SUPPORTED (rounded)
> "nine hundred eighty-eight million bytes." | Evidence 987,922,432 | SUPPORTED (rounded)
> "nought point three bits per weight, all in." | Evidence 0.315 bpw (~0.31) | SUPPORTED (rounded)
> "about nineteen million bytes." | Evidence 19,434,496 /19,358,176 | SUPPORTED (rounded)
> "nineteen million bytes against nine hundred eighty-eight million, fifty-one times smaller." | Evidence ratio ~50.8-51x | SUPPORTED (rounded)
> "On ninety-six questions, Spark's recipe ... closes twenty-three point two percent ... human recipe, two point one." | Evidence gap 0.232=23.2%, 0.021=2.1% on 96 held-out | SUPPORTED
> "Spark's recipe won by nought point one three four nats, inside budget." | Evidence Down Dominator beats uniform by 0.134 nats on Pair4 inside 39,046,144 budget | SUPPORTED
> "plain one-bit closes more at sixty-two megabytes." | Evidence 61,745,828 B (~61.7 MB) | SUPPORTED (rounded, "62 megabytes" = 61.7 MB)
> "at nineteen million, no one-bit patch fits, ours does." | Evidence floor 61,745,828 B, factored fits at 19.4 MB budget | SUPPORTED
> "all forty-one checks passed." | Evidence 41 of 41 | SUPPORTED
> "well under a second" (swap) | Evidence file-load times 0.104s/0.087s – true but unlabeled | SUPPORTED value, but labeling trap see below.

No gap >1.0 percentage, no 7B, no byte-contradiction.

Wording traps:
a. PASS - no >1.0 gap presented as recovery %.
b. **FLAG** - Size claims ("nineteen megabytes ... gigabyte", "nineteen million ... fifty-one times smaller") appear WITHOUT adjacent numeric first-token accuracy figures "patch 0.010 vs base 0.031" inside the transcript. Transcript does contain spoken lossy disclosure "Honestly, the patch's first-word accuracy stays below the base model's own: this is probability recovery, not solved tasks." which satisfies disclosure part, but the required numeric figures are only described as a printed slide line in demo_script.md, not present in narration_v7.txt text itself. Strict per-file check fails adjacency requirement.
c. **FLAG** - "swaps behavior live, well under a second." and "Watch: the patch swaps in live, well under a second." presented as general swap speed without qualifier "file-load times on the demo machine (0.104s /0.087s)". Evidence defines those as FILE-LOAD times.
d. PASS - no 7B mention.
e. PASS - "one-bit delta compression is published, BitDelta and Delta-CoMe, and our work predates this week." correct.
f. PASS - "To be clear: it does not compress the model. Only the fine-tune's change gets small. The base stays full size, loaded once."

Internal inconsistency: None.

**VERDICT for video/narration_v7.txt: FLAG**

* FLAG sentence 1 (Trap b): `"The headline pair, Qwen2.5-0.5B: nineteen million bytes against nine hundred eighty-eight million, fifty-one times smaller."` spoken without adjacent accuracy numbers in the audio transcript.
  * Fix: Retain V7 spoken disclosure already present and ensure the size claim sits next to printed/spoken accuracy figures in the same presentation. Add spoken or on-slide text adjacent to size visual: `"First-token accuracy: patch 0.010 vs base 0.031 on the Qwen pair (lossy: probability recovery, not solved tasks – 0.010 < 0.031)."` The transcript should note `[ON SCREEN: First-token accuracy: patch 0.010 vs base 0.031]` immediately after size line, or add to narration: `"Honestly, the patch's first-word accuracy stays below the base model's own at 0.010 vs base 0.031: this is probability recovery, not solved tasks."`

* FLAG sentence 2 (Trap c): `"It plugs into the base and swaps behavior live, well under a second."` and `"Watch: the patch swaps in live, well under a second."`
  * Fix: `"It plugs into the base and swaps behavior live, file-load well under a second on the demo machine (uniform_rank32 0.104s, mlp_behemoth_lite 0.087s file-load times)."` Do not use bare "well under a second" as general swap/inference speed.

If video is judged as composite (audio transcript + slide visual that adds first-token accuracy line per docs/demo_script.md V7), trap b would be considered satisfied at presentation level; transcript-only view remains FLAG as above.

---

### 3. PROVENANCE.md

#### A. Numeric Claims

> "this repository ... was created on Oct 26, 2026." | Evidence event window Oct 26 to Nov 4, 2026; repo created Oct 26 per project facts | SUPPORTED
> "verified against the live older repository ... head c2bf28d1f52c4905d0b13a78fd93467328ea958f on Oct 31, 2026" | Evidence older repo live head c2bf28d1f52c4905d0b13a78fd93467328ea958f at check Oct 31, 2026 | SUPPORTED
> "of 147 files here and 32 files there, exactly one file is byte-identical in both, a generic four-line .gitignore." | Evidence whole tree 147 live files; older repo 32 files; exactly one byte-identical generic four-line .gitignore | SUPPORTED
> "README.md, NOTICE.md and LICENSE exist in both repositories but have different content." | Evidence README etc exist in both but different content | SUPPORTED
> "Both repositories use the MIT license, but the license texts are not identical." | Evidence Both use MIT but texts not identical | SUPPORTED
> "No code, benchmark, result, or script file is byte-identical, and no git history was carried over." | Evidence no code/benchmark/result/script byte-identical, no git history carried over | SUPPORTED

Wording traps: Not applicable (no size/swap/percentage/prior-work claims). Prior work not misclaimed as event work.

Internal inconsistency: None.

**VERDICT for PROVENANCE.md: PASS**

No numeric contradiction, no trap violation, no internal inconsistency.

## Cross-file consistency (tokens this call: 28560)

CROSS-FILE CONSISTENCY CHECK vs EVIDENCE PACK

All numbers below checked against `results/*.json` ground truth in Evidence Pack. No number contradicts evidence beyond rounding.

FINDING 1 - Swap / file-load time - CONSISTENT-BUT-DIFFERENT-FRAMING
* README.md: "live hot-swap (0.104 s and 0.087 s, file-load times on the demo machine, in the recorded demo)"
* docs/submission_draft.md: "patches swap in and out ... in about 0.1 seconds (file-load time on the demo machine; the two recorded swaps measured 0.104 s and 0.087 s)"
* docs/demo_script.md ON SCREEN: "the swap line `>>> SWAP: ... loaded live in 0.49s` boxed in amber." AND docs/demo_script.md V3 notes: "Swap wording is now 'well under a second' everywhere (true for both the 0.104s transcript of record and the 0.49s contended recording; 'about a tenth of a second' removed)."
* Correct per Evidence Pack `results/hotswap_demo.json`: swap times are FILE-LOAD times 0.104s to uniform_rank32 and 0.087s to mlp_behemoth_lite. 0.49s is the alternate `hotswap_v2.cast` recording explicitly disclosed in demo_script.md as the contended recording. Spoken narration in all files uses the broadened wording "well under a second" which is true for both (0.104s, 0.087s and 0.49s). Not a contradiction, explained dual recording.

FINDING 2 - Compression ratio rounding - CONSISTENT-BUT-DIFFERENT-FRAMING
* README.md: "rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller."
* docs/demo_script.md: "patch byte price 19,434,496 B (the uniform rank-32 patch), full delta 987,922,432 B, 50.8x smaller."
* README.md Fourth pair: "about 79x smaller" vs Evidence Pack: "about 80x smaller than the full difference" for Qwen2.5-1.5B (3,087,138,816 / 38,623,232 = 79.94x)
* Correct per Evidence Pack: 987,922,432 / 19,434,496 = 50.84x ; 987,922,432 / 19,358,176 = 51.04x ; 3,087,138,816 / 38,623,232 = 79.9x. "51x", "50.8x", "79x", "80x" are all roundings of same exact byte counts, not contradictions.

FINDING 3 - Bits-per-weight phrasing - CONSISTENT-BUT-DIFFERENT-FRAMING
* README.md top: "priced all in ... that comes to about 0.31 bits per weight on the Qwen pair"
* README.md plain words: "0.28 bits per weight for one large layer at rank 32 (the exact price depends on layer size and rank)."
* docs/demo_script.md: "about 0.3 bits per weight, all in." ; video/narration_v7.txt: "nought point three bits per weight, all in."
* Correct per Evidence Pack: "about 0.31 bits per weight (0.315 bpw) all-in effective rate on this pair." 0.3 is rounding of 0.31; 0.28 is explicitly scoped to "one large layer at rank 32" not the all-in average, disclosed as size-dependent.

FINDING 4 - Event window wording - CONSISTENT-BUT-DIFFERENT-FRAMING
* README.md: "This repository contains only work built during the Meta Global AI Developer Hackathon, October 26 to November 4, 2026"
* docs/submission_draft.md: "everything in this repository ... was built during the event, October 26 to November 2"
* Correct per Evidence Pack PROJECT FACTS: event window Oct 26 to Nov 4, 2026. Submission draft does not claim the event ends Nov 2, it states the build window inside the event (creation Oct 26, draft written Nov 2 push planned). README states the full event window. No claim that prior work (v0.1-v0.3, Signet in github.com/ganjikrishna/fraction-compressor) was built during event; both files disclose it as prior work per requirement.

FINDING 5 - Prior-art citation list - CONSISTENT-BUT-DIFFERENT-FRAMING
* README.md lists: BitDelta, Delta-CoMe, LittleBit + GraftLLM/Skill Weaving SkillZip
* docs/submission_draft.md lists: BitDelta, Delta-CoMe, D-QRELO, LittleBit
* Correct per Evidence Pack: prior work to be disclosed is Fraction Compressor v0.1-v0.3 + Signet (both files do so). Published delta-compression ideas are correctly cited as ideas-only, no code, 1-bit format not claimed as ours. List differences are framing, no contradictory claim of ownership or number.

FINDING 6 - Numbers vs Evidence Pack (exhaustive check) - NO CONTRADICTION
Checked all numeric claims in README.md, docs/submission_draft.md, docs/demo_script.md, video/narration_v7.txt:
* Qwen 0.5B: base -11.150 acc 0.031, full -8.542/-8.543 acc 0.167, uniform 19,434,496 -11.096 acc 0.010 gap 0.021/2.1%, lite 19,358,176 -10.545 acc 0.010 gap 0.232/23.2%, subsets lite 0.095/0.304 vs uniform 0.016/0.023 - all match.
* SmolLM2: uniform 19,705,856 -8.366 gap 1.015, rebalanced 19,683,328 -8.073 gap 1.081, margin 0.293 - match, correctly NOT described as recovery fraction.
* Llama 1B: uniform 25,143,296 -14.201 gap -0.076 below base -13.718, balanced 24,515,584 -12.714 gap 0.159/15.9% - match.
* Qwen 1.5B: uniform 39,046,144 -6.478 gap 1.279 acc 0.323, Down Dominator 38,623,232 -6.344 gap 1.307 acc 0.260 margin 0.134, subset reversal heldout24 -3.845 vs -3.996, heldout72 -7.126 vs -7.356 - match, correctly NOT described as recovery fraction.
* BitDelta floor 61,745,828 gap 0.436 vs factored 61,258,816 gap 0.385 - match.
* LoRA 18,696,192 gap 1.362 acc 0.167-0.177 tie full 0.167 - match.
* Skill demo 9/10 =8/1/1 full, 0/10 base, 1/0/9 uniform, force-start 7/1/2 base vs 8/1/1 patch matching full unforced - match.
* Quantum audit 41/41 ibm_fez - match.
* 7B pair deliberately excluded - no file presents 7B numbers as submission - compliant per Evidence Pack.
* Provenance: 147 vs 32 files, exactly one byte-identical .gitignore, README/NOTICE/LICENSE exist but different content, both MIT but texts not identical, no code/history carried over - matches Evidence Pack live check. docs/submission_draft.md and PROVENANCE.md not on GitHub by design - correctly disclosed.

CROSS-FILE VERDICT: PASS (no contradictions) - 0 CONTRADICTION, 5 CONSISTENT-BUT-DIFFERENT-FRAMING (rounding / scope / disclosed dual recording)

TOTAL TOKENS muse-spark-1.2: 90918


---

## Reviewer output: muse-spark-1.1 (hard check, verbatim, plus supplementary completion call)

# Fresh hard check reviewer output: muse-spark-1.1

## Chunk: README.md (tokens this call: 20757)

Evidence checked for README.md:

**Numeric claims:**

- "about 0.31 bits per weight on the Qwen pair" -> evidence 0.315 bpw -> SUPPORTED (rounded)
- "from about 1 GB to about 19 MB on the Qwen2.5-0.5B pair" -> full 987,922,432 B (~0.99GB), patch 19,358,176 B (~19MB) -> SUPPORTED (rounded) - but see wording trap b
- "at 19,358,176 bytes" -> evidence 19,358,176 -> SUPPORTED
- "closes 23.2% of the gap (0.605 of 2.607 nats)" -> evidence gap closed 0.232=23.2%, base -11.150 to full -8.543 =2.607, factored -10.545 diff 0.605 -> SUPPORTED
- "first-token accuracy 0.010 (below base 0.031)" -> evidence lite 0.01042=0.010, base 0.03125=0.031 -> SUPPORTED
- "0.104 s and 0.087 s, file-load times on the demo machine" -> evidence 0.104s to uniform_rank32, 0.087s to mlp_behemoth_lite file-load times demo machine -> SUPPORTED
- "distilled LoRA at 18,696,192 bytes" -> evidence 18,696,192 -> SUPPORTED
- "closes far more of the gap on these tests (1.362 against 0.232)" -> evidence LoRA 1.362, lite 0.232 -> SUPPORTED
- "0.28 bits per weight for one large layer at rank 32" -> not in evidence pack -> NOT IN EVIDENCE
- "One layer stored the normal way takes 8.4 MB; our rank-32 file takes 144 KB" -> not in evidence pack -> NOT IN EVIDENCE
- "rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller" -> evidence uniform 19,434,496, full 987,922,432, ratio 50.8=~51x -> SUPPORTED (rounded) - but see wording trap b
- "about 1 to 2% on the first pair" -> evidence 0.010-0.021 =1-2.1% -> SUPPORTED
- "about 8 to 9% on the second" -> evidence second pair factored 0.083=8.3% -> SUPPORTED
- "0 to about 3% on the third" -> evidence third pair 0.000, 0.021, 0.031=0-3.1% -> SUPPORTED
- "26 to 32% against the full patch's own 33.3%" -> evidence fourth full 0.333=33.3%, uniform 0.323=32.3%, dominator 0.260=26.0% -> SUPPORTED
- "passes 9 of 10 test prompts (eight fully clean, one with a single reworded value)" -> evidence 9/10 =8 clean/1 partial/1 failed -> SUPPORTED
- "plain base passes 0 of 10" -> evidence base 0/10 -> SUPPORTED
- "Our rank-32 patch passes only 1 of 10" -> evidence 1 clean/0 partial/9 failed -> SUPPORTED
- "plain base completes 7 of 10 cleanly" -> evidence forced base 7 clean/1 partial/2 failed -> SUPPORTED
- "patch under the same forced start completes 8 of 10 cleanly and 1 partly" -> evidence base+patch 8/1/1 -> SUPPORTED
- "rank-64 patch (37,044,736 bytes) and a rank-128 patch (72,265,216 bytes) each pass 2 of 10" -> bytes and 2/10 not in evidence pack -> NOT IN EVIDENCE
- "Muse Spark recipe ... (19,434,400 bytes, the same budget) passes 0 of 10" -> not in evidence pack -> NOT IN EVIDENCE
- "closes 23.2% of the score gap on 96 fresh questions" -> lite 23.2% -> SUPPORTED
- "mlp_behemoth, is byte-unfair: at 21,719,776 bytes it spends 11.8% more" -> evidence 21,719,776 B, +11.8% -> SUPPORTED
- "mlp_behemoth_lite: 19,358,176 bytes, fewer than the human uniform rank-32 recipe's 19,434,496 bytes" -> SUPPORTED
- "lite closes 23.2% of the gap, against 2.1% for the human recipe" -> SUPPORTED
- "9.5% vs 1.6% on the original 24 questions" -> evidence lite heldout24 0.095, uniform 0.016 -> SUPPORTED
- "30.4% vs 2.3% on the 72 new ones" -> evidence lite 0.304, uniform 0.023 -> SUPPORTED
- "knowledge questions ... (7.8% vs 3.7%)" -> not in evidence pack -> NOT IN EVIDENCE
- "o-down-rebalanced: 19,683,328 bytes, inside the human recipe's budget of 19,705,856 bytes" -> evidence 19,683,328 and 19,705,856 -> SUPPORTED
- "beats the human uniform recipe by 0.293 score points on average" -> evidence -8.073 vs -8.366 diff 0.293 -> SUPPORTED
- "gap-closed percentage goes above 100% here" second pair -> evidence 1.015,1.088,1.081 >1 -> SUPPORTED
- "raw score margin (0.293 points)" -> SUPPORTED
- "no_embed_mlp_spread, was byte-unfair again: at 34,690,048 bytes it spends 38.0% more than the human recipe's budget of 25,143,296 bytes" -> evidence 34,690,048, 25,143,296, 38.0% calc -> SUPPORTED
- "no_embed_mlp_spread_balanced: 24,515,584 bytes" -> SUPPORTED
- "scores -12.714 against the human uniform recipe's -14.201: it closes 15.9% of the gap, while the human recipe closes -7.6%, which is below the base model itself (-13.718)" -> evidence -12.714, -14.201, 0.159, -0.076, base -13.718 -> SUPPORTED
- "20.0% vs -1.7% on the original 24 questions, and 14.8% vs -9.1% on the 72 new ones" -> subset numbers for third pair not in evidence pack -> NOT IN EVIDENCE
- "15.9% here against 23.2% on the Qwen pair" -> SUPPORTED
- "first-token accuracy ... 2.1% for the byte-fair variant, against 21.9% for the full patch" -> evidence 0.021 vs 0.21875 -> SUPPORTED
- "human recipe's budget of 39,046,144 bytes" fourth pair -> SUPPORTED
- "Down Dominator, is byte-fair itself at 38,623,232 bytes" -> SUPPORTED
- "scores -6.344 against the human uniform recipe's -6.478" -> SUPPORTED
- "by about 0.13 score points" -> diff 0.134 -> SUPPORTED (rounded)
- "human recipe wins the first 24 questions; Down Dominator wins the 72 newer ones" -> evidence heldout24 uniform -3.845 beats -3.996, heldout72 -7.126 beats -7.356 -> SUPPORTED
- "full patch -7.810" -> SUPPORTED
- "gap-closed percentage goes above 100% (130.7% against 127.9%)" fourth pair -> evidence 1.307=130.7%, 1.279=127.9% -> SUPPORTED
- "raw score margin (about 0.13 points)" -> SUPPORTED
- "human recipe's first-token accuracy ... 32.3%, against Down Dominator's 26.0% and the full patch's own 33.3%" -> evidence 0.32292, 0.26042, 0.33333 -> SUPPORTED
- "roughly 39 MB patch against a 3,087,138,816-byte full patch, about 79x smaller" -> full 3,087,138,816, patch ~39,046,144 ratio ~79 -> SUPPORTED (evidence says about 80x)
- "plain 1-bit delta cannot go below 1 bit per weight, which on the first pair's 169 matrices is 61,745,828 bytes" -> evidence 61,745,828 B -> SUPPORTED for bytes, 169 matrices -> NOT IN EVIDENCE
- "closes 43.6% of the gap ... against 38.5% for our factored format at uniform rank 108 priced just under it (61,258,816 bytes)" -> evidence BitDelta 0.436, factored 0.385, 61,258,816 -> SUPPORTED
- "41 of 41 checks passed" -> evidence 41 of 41 -> SUPPORTED
- Dates "October 26 to November 4, 2026" -> event window in facts -> SUPPORTED

**Wording traps:**

a. Gap-closed >1.0 as recovery fraction: MUST NOT present as recovery fraction. File says for second pair "percentage is NOT a share" and fourth pair "is NOT a share" -> PASS
b. Size claims (~19 MB, ~51x vs full delta) must sit next to lossy disclosure + accuracy 0.010 vs base 0.031: Claim "What shrinks to a fraction is the fine-tune's change: from about 1 GB to about 19 MB" appears without lossy disclosure/accuracy in same sentence/paragraph. Claim "rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller" appears without lossy disclosure/accuracy. Only the 19,358,176 bytes paragraph complies. -> FAIL
c. Swap times must be labeled file-load times on demo machine: File says "0.104 s and 0.087 s, file-load times on the demo machine, in the recorded demo" -> PASS
d. No 7B / Qwen2.5-7B fifth pair: No mention -> PASS
e. Prior work disclosure: Prior work v0.1-v0.3 and Signet disclosed as predating event, not claimed as built during event -> PASS
f. Compresses delta not model, base stays full size: Explicit statement -> PASS

**Internal inconsistency:** None detected.

**VERDICT for this file: FLAG**

FLAG details:

1. Exact sentence: "What shrinks to a fraction is the fine-tune's change: from about 1 GB to about 19 MB on the Qwen2.5-0.5B pair used in these tests."
   Issue: size claim (~19 MB) without adjacent lossy disclosure and first-token accuracy figures required by trap b.
   Fix: Append adjacent disclosure, e.g., "What shrinks to a fraction is the fine-tune's change: from about 1 GB (987,922,432 bytes) to about 19 MB (19,358,176 bytes) on the Qwen2.5-0.5B pair; the patch is lossy, with first-token accuracy 0.010 vs base 0.031 and 23.2% gap closed, not a full recovery."

2. Exact sentence: "On the model pair used in this repo's benchmark (Qwen2.5-0.5B base and Instruct), rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller."
   Issue: same trap b – 51x size claim without adjacent lossy disclosure and accuracy 0.010 vs 0.031.
   Fix: Add lossy disclosure in same paragraph, e.g., "On the model pair ... about 51x smaller. This 19.4 MB patch is lossy (first-token accuracy 0.010 vs base 0.031, gap closed 2.1% for this uniform rank; lite variant 23.2% at 19,358,176 bytes)."

## Chunk: docs/submission_draft.md (tokens this call: 24881)

Checked file: docs/submission_draft.md against EVIDENCE PACK

#### Numeric Claims

1. Quote: "about 0.31 bits per weight all in (signs, factors, and scales together)" Evidence: 0.315 bpw on Qwen pair all-in -> **SUPPORTED** (rounded)
2. Quote: "the full patch is 988 MB and ours is 19 MB, about 51x smaller" Evidence: full 987,922,432 B ~987.9 MB, lite 19,358,176 B ~19.36 MB, 987,922,432/19,358,176=51.03 -> **SUPPORTED** (rounded) for all three numbers but fails proximity rule - see trap b
3. Quote: "in about 0.1 seconds (file-load time on the demo machine; the two recorded swaps measured 0.104 s and 0.087 s)" Evidence: swap file-load times 0.104 s to uniform_rank32, 0.087 s to mlp_behemoth_lite -> times **SUPPORTED**, labeling as file-load time **SUPPORTED**
4. Quote: "an update is a 19 MB file" Evidence: 19,358,176 B -> **SUPPORTED** (rounded)
5. Quote: "it closes 23.2% of the gap" Evidence: lite gap 0.232 =23.2% -> **SUPPORTED**
6. Quote: "about a tenth of a second" Evidence: 0.104/0.087 -> **SUPPORTED** (rounded)
7. Quote: "On 96 fresh questions" Evidence: combined96 =96 -> **SUPPORTED**
8. Quote: "the headline recipe closes 23.2% of the score gap" Evidence: 0.232 -> **SUPPORTED**
9. Quote: "against 2.1% for a plain uniform recipe at a slightly larger byte budget" Evidence: uniform 0.021=2.1%, bytes 19,434,496 vs 19,358,176 slightly larger -> **SUPPORTED**
10. Quote: "recovery is weaker (15.9%)" Evidence: no_embed_mlp_spread_balanced 0.159=15.9% -> **SUPPORTED**
11. Quote: "about 80x smaller than the full patch" Evidence: 3,087,138,816 / 38,623,232 =79.93 -> **SUPPORTED** (rounded)
12. Quote: "beats the uniform recipe by 0.134 nats on the combined 96 questions" Evidence: -6.344 vs -6.478 =0.134 nats per pack -> **SUPPORTED**
13. Table - Qwen base "-11.150" "0.031" Evidence -11.1498 -> -11.150, accuracy 0.03125 ->0.031 -> **SUPPORTED**
14. Table - Qwen full "-8.542" "0.167" "

## Chunk: docs/demo_script.md + video/narration_v7.txt + PROVENANCE.md (tokens this call: 24760)

### TARGET: docs/demo_script.md

**Numeric claims vs Evidence Pack**

- "about 19 MB instead of about 1 GB" - evidence uniform 19,434,496 B / lite 19,358,176 B ~19 MB, full 987,922,432 B ~0.988 GB -> SUPPORTED (rounded)
- "987,922,432 bytes" - full_delta_fp16_bytes Pair1 = 987,922,432 -> SUPPORTED
- "about 0.3 bits per weight, all in" / "nought point three bits per weight" - evidence 0.315 bpw, about 0.31 -> SUPPORTED (rounded)
- "nine hundred eighty-eight million bytes" - 987,922,432 -> SUPPORTED (rounded)
- "patch byte price 19,434,496 B" - evidence uniform_rank32 19,434,496 B -> SUPPORTED
- "full delta 987,922,432 B" - same as above -> SUPPORTED
- "50.8x smaller" - 987,922,432/19,434,496=50.828 -> SUPPORTED (rounded)
- "about nineteen million bytes" - 19.4M -> SUPPORTED
- PATCH SIZES block "full delta 987,922,432 B" -> SUPPORTED
- "uniform rank-32 patch 19,434,496 B" -> SUPPORTED
- "mlp_behemoth_lite patch 19,358,176 B" -> evidence lite 19,358,176 B -> SUPPORTED


## Cross-file consistency (tokens this call: 31371)

Checked 5 files vs evidence pack.

**FINDING 1 – Build window end date**
- README.md: "This repository contains only work built during the Meta Global AI Developer Hackathon, October 26 to November 4, 2026"
- docs/submission_draft.md: "everything in this repository (the factored runtime, the four-pair benchmark, the recipe search, the BitDelta and LoRA baselines, and the verification harness) was built during the event, October 26 to November 2"
- Correct per evidence pack PROJECT FACTS: event window Oct 26 to Nov 4, 2026. README matches. Draft's Nov 2 is its drafting cutoff, still inside window.
- **CONSISTENT-BUT-DIFFERENT-FRAMING**

**FINDING 2 – Swap-time numbers**
- docs/demo_script.md: "and the swap line `>>> SWAP: ... loaded live in 0.49s` boxed in amber."
- README.md: "live hot-swap (0.104 s and 0.087 s, file-load times on the demo machine, in the recorded demo)" ; docs/submission_draft.md: "the two recorded swaps measured 0.104 s and 0.087 s"
- Correct per evidence pack HOT-SWAP DEMO: FILE-LOAD times to uniform_rank32 0.104 s, to mlp_behemoth_lite 0.087 s. Demo script itself explains: "Swap wording is now 'well under a second' everywhere (true for both the 0.104s transcript of record and the 0.49s contended recording; 'about a tenth of a second' removed)." 0.49s is a separate contended recording, not the file-load time of record.
- **CONSISTENT-BUT-DIFFERENT-FRAMING**

**FINDING 3 – Compression ratio rounding**
- README.md: "rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller."
- docs/demo_script.md: "PATCH SUMMARY: patch byte price 19,434,496 B (the uniform rank-32 patch), full delta 987,922,432 B, 50.8x smaller."
- Correct per evidence pack: 987,922,432 / 19,434,496 = 50.83x. Both are roundings.
- **CONSISTENT-BUT-DIFFERENT-FRAMING**

No number in any file contradicts evidence pack outside rounding. All gap-closed, byte sizes, accuracies, mean logprobs, BitDelta floor 61,745,828 B vs factored 61,258,816 B, LoRA size 18,696,192 B, Llama uniform below base -14.201 vs base -13.718, SmolLM2 and 1.5B gap >1.0 warnings, 41/41 quantum audit, disclosure of prior work v0.1-v0.3/Signet, delta-not-model definition, no 7B claim, Chatterbox voice clone disclosure – all consistent across files and with evidence pack.

**CROSS-FILE VERDICT: PASS (no contradictions)** – 0 CONTRADICTION, 3 CONSISTENT-BUT-DIFFERENT-FRAMING notes listed.

TOTAL TOKENS muse-spark-1.1: 101769


### Supplementary completion call (muse-spark-1.1, verbatim)

**A. docs/submission_draft.md**

**Numeric checks – remaining half:**

* LoRA 136% : evidence LoRA mean logprob -7.599 gap 1.362 +/-0.033 accuracy 0.167-0.177 tying full 0.167. File says `closes 136% of the gap` – numeric value 1.362 -> 136% is correct math, but violates wording trap >1.0 as percentage.
* Out-of-style 62.0% / in-style 139.5% : evidence out-of-style 0.620 in-style 1.395 lite 0.232 – numeric values 62.0% and 139.5% match, but 139.5% is >1.0 violation.
* Recovery pilot 1.136 vs 1.348 : not present in this file – no claim to check. If present elsewhere must be >1.0 not as recovery.
* Arrival JSON patch credit: File says

> `with the mlp_behemoth_lite patch swapped in, the same base returns exactly the object, parseable with the exact keys and values (results/hotswap_demo.json).`

Evidence `results/hotswap_demo.json` : base fails json.loads, **base + uniform_rank32** parses exactly. File credits wrong patch. **FLAG – misattribution**.

* NuExtract wording: File says

> `our rank-32 patch on 1 clean of 10.`

Evidence `skill_demo.json` uniform_rank32 = 1 clean /0 partial /9 failed – correct.

> `force the fine-tune's first token and the plain base completes 7 of 10 cleanly (2 failed)`

Evidence base force-start = 7 clean /1 partial /2 failed – failed count 2 is correct, partial implied but not named. Counts match.

> `the patch completes 8 clean, 1 partial, and 1 failed of 10, matching the full fine-tune's own unforced score (8 clean, 1 partial, 1 failed).`

Evidence base+rank32 patch 8/1/1 matching full fine-tune unforced 8/1/1 (=9/10 parseable) – correct.

**Wording traps:**

* gap-closed >1.0 as recovery fraction/percentage: File correctly handles SmolLM2 and 1.5B pairs:

> `gap closed exceeds 1.0 there (SmolLM2: uniform 1.015, winner 1.081; 1.5B: uniform 1.279, winner 1.307) and is not a recovery fraction`

PASS for those.

FAIL for LoRA:

> `On the same 96 questions the adapter closes 136% of the gap on average across three seeds`

> `still closes 62.0% of the base-to-full gap on the Spark-written 96 (vs 139.5% in-style and 23.2% for the factored patch)`

1.362 and 1.395 (>1.0) described as `136%` and `139.5%` – prohibited. Must state raw mean logprob and note not a recovery fraction.

* size claim + lossy + numeric accuracy 0.010 vs base 0.031: File has size claim:

> `On the Qwen2.5-0.5B pair, the full patch is 988 MB and ours is 19 MB, about 51x smaller.`

Evidence 987,922,432 vs 19,358,176 = 51x correct. Next paragraph disclosure:

> `The patch is also lossy: on our main pair it closes 23.2% of the gap to the full fine-tune, and its first-token accuracy sits below the base model's own`

Missing numeric accuracies 0.010 vs base 0.031 required by trap. **FLAG**.

* swap times labeled file-load times in EVERY mention: Evidence defines swap times as FILE-LOAD times 0.104s and 0.087s.

File mention 1 PASS:

> `patches swap in and out of one running base model live, in about 0.1 seconds (file-load time on the demo machine; the two recorded swaps measured 0.104 s and 0.087 s).`

File mention 2 FAIL:

> `rollback is swapping the previous file back in about a tenth of a second,`

No file-load label. **FLAG**.

* 7B claims: PASS. File explicitly says tested `four open base models up to 1.5B` and cover note says `The 7B streamed test is not claimed anywhere`. No 7B numbers in body.
* prior-work disclosure: PASS. File says `Fraction Compressor v0.1 to v0.3 and the Signet delta-transfer experiments live in the earlier repository... inherited from v0.1 to v0.3 and are not claimed as event work.`
* delta-not-model: PASS. `this tool does not compress the model itself; the base model stays full size, and what is compressed is only the fine-tune's difference`

**Internal inconsistency:** Cover note:

> `(1) the demo video YouTube link, final cut pending, v5 is the current cut;`

Section 6:

> `[PLACEHOLDER: YouTube link for the final cut. Current cut is v7, 178.63 seconds, adopted Oct 30.`

v5 vs v7 mismatch. **FLAG**.

**VERDICT for docs/submission_draft.md: FLAG**

Fixes required:

1. Change `with the mlp_behemoth_lite patch swapped in` to `with the uniform rank-32 patch swapped in` – evidence attributes parseable Arrival JSON to uniform_rank32.
2. Add file-load qualifier to every swap time: change `rollback is swapping the previous file back in about a tenth of a second,` to `rollback is swapping the previous file back in about a tenth of a second (file-load time on the demo machine),`
3. Reconcile video version: change cover note `v5 is the current cut` to `v7 is the current cut` to match section 6.
4. Remove >1.0 percentage phrasing: change `closes 136% of the gap` to `scores mean logprob -7.599 (vs base -11.150, full -8.542, gap 1.362) – outscoring the full delta, so not described as a recovery fraction`. Change `139.5% in-style` to `mean logprob -9.5325 out-of-style gap 0.620 vs in-style same seed gap 1.395 (mean logprob exceed full), raw logprob is measure`.
5. Adjacent to `19 MB, about 51x smaller` add lossy numbers: `its first-token accuracy 0.010 vs base 0.031 (below base) and gap closed 23.2%` in same/next sentence.

**B. video/narration_v7.txt**

Numeric:

* 19MB vs ~1GB – evidence 19,358,176 vs 987,922,432 PASS
* `nine hundred eighty-eight million bytes` – evidence 987,922,432 PASS
* `nought point three bits per weight` – evidence 0.31 (0.315) all-in PASS approximate
* `about nineteen million bytes` PASS
* `nineteen million bytes against nine hundred eighty-eight million, fifty-one times smaller.` – 51x PASS
* `closes twenty-three point two percent … two point one` – evidence 0.232 and 0.021 PASS
* `mlp_behemoth_lite` winner PASS
* first-word accuracy below base PASS (0.010 vs 0.031)
* `won by nought point one three four nats, inside budget` – evidence 0.134 nats Down Dominator beats uniform, byte-fair 38,623,232 vs 39,046,144 PASS
* `plain one-bit closes more at sixty-two megabytes.` – evidence BitDelta at 61,745,828 B gap 0.436 vs factored 0.385 at matched 61,258,816 B PASS
* `at nineteen million, no one-bit patch fits` – evidence floor 61,745,828 B PASS
* `all forty-one checks passed` – evidence quantum audit 41 pass PASS

Wording traps:

* gap>1.0 – no claim >1.0 in narration – PASS
* delta-not-model PASS: `it does not compress the model. Only the fine-tune's change gets small. The base stays full size`
* 7B – none – PASS
* prior-work: says `one-bit delta compression is published, BitDelta and Delta-CoMe, and our work predates this week.` Does not name v0.1-v0.3/SignET repo, but does state not new; borderline, but main flags below are definitive.
* size + lossy + numeric accuracy: sentence `nineteen million bytes against nine hundred eighty-eight million, fifty-one times smaller.` followed by `patch's first-word accuracy stays below the base model's own: this is probability recovery, not solved tasks.` No numeric 0.010 vs 0.031 – **FLAG**.
* swap times file-load label EVERY mention: Two mentions:

> `It plugs into the base and swaps behavior live, well under a second.`
> `Watch: the patch swaps in live, well under a second.`

Neither says file-load time. Evidence requires label. **FLAG**.

**VERDICT for video/narration_v7.txt: FLAG**

Exact fixes:

* Change `swaps behavior live, well under a second.` to `swaps behavior live, well under a second (file-load time on the demo machine, 0.104 s to uniform and 0.087 s to lite).`
* Change `Watch: the patch swaps in live, well under a second.` to `Watch: the patch swaps in live, well under a second (file-load time).`
* Change `Honestly, the patch's first-word accuracy stays below the base model's own` to `Honestly, the patch's first-token accuracy 0.010 stays below the base 0.031`
* Add adjacent lossy note after size claim if not already adjacent.

**C. PROVENANCE.md**

Claims:

* repo `github.com/ganjikrishna/fraction-compressor-v0.4 was created on Oct 26, 2026` – matches evidence Project Facts creation Oct 26 – PASS
* `verified against the live older repository github.com/ganjikrishna/fraction-compressor, head c2bf28d1f52c4905d0b13a78fd93467328ea958f on Oct 31, 2026: of 147 files here and 32 files there, exactly one file is byte-identical in both, a generic four-line .gitignore.` – matches `results/provenance_live_check.md` 147 vs 32, one identical .gitignore – PASS
* `README.md, NOTICE.md and LICENSE exist in both repositories but have different content.` – matches evidence – PASS
* `Both repositories use the MIT license, but the license texts are not identical.` – matches evidence – PASS
* `No code, benchmark, result, or script file is byte-identical, and no git history was carried over.` – implied by exactly one identical file (.gitignore) – PASS

**VERDICT for PROVENANCE.md: PASS**

---

## Judge pass: muse-spark-1.2 (verbatim)

# Judge pass reviewer output: muse-spark-1.2

## Gate and blockers (tokens this call: 23600)

**1. STAGE ONE GATE**

**GATE: FAIL**

The texts do not show a Meta model (Muse Spark) running *inside the shipped product at runtime*. Every described Spark use is offline build-time / evaluation-time tooling or judging, not a runtime feature of `Fraction Compressor` itself.

Product runtime as defined where a judge looks:

* README.md `How it works / In plain words`: *"`v0.4 runs it through a factored runtime: two small multiplies, Y = (X U) V^T, without ever rebuilding the full weight matrix.`"*
* README.md `Do it yourself / Use it`: *"Use it: load the patch together with the base model, as in `examples/hotswap_demo.py`, where patches swap in and out of one running base model live."* — no Spark call in the hot-swap path. File listing shows no Spark runtime dependency.

What the README and Form Text *do* claim for Spark, in the exact places a judge checks:

* README.md `Prior art`: *"`What is ours is not the 1-bit format itself: it is the in-loop recipe search and judging by Muse Spark in one narrow form (the model allocates ranks for a post-hoc fine-tune delta under a hard byte budget, training-free, and the same loop judges the result against the files;`...`"`*
* README.md `What is in this repo`: *"`where Muse Spark proposed compression recipes that were scored, cross-validated (Gemini arithmetic checks, a Muse Spark judging pass, a Muse Glimmer reference check), and confirmed on 96 fresh held-out questions generated by Muse Spark, on four model pairs.`"*
* README.md `How these numbers are checked`: *"`a Muse Spark judging pass checked each headline claim against the exact result files it cites`"* and *"`Implementation, benchmarking, and documentation were carried out with Ember, an AI agent powered by Muse Spark, working under the author's direction`"'*
* Demo narration transcript (stand-in for video): *"`I built it with Ember, my AI agent, powered by Muse Spark.`"* and *"`Muse Spark proposed the per-layer recipes, generated the fresh test questions, and judged every claim against its result file.`"*
* Submission Form Text §7: *"`Second, Muse Spark is the recipe designer in the loop. In the recipe search we call the Alien Sweep ... Spark proposes per-layer rank allocations (recipes) for compressing a fine-tune's patch under a hard byte budget, training-free.`"*
* Submission Form Text §7: *"`Third, Muse Spark is the claim checker. After each benchmark, a Spark claim-checking pass checks every headline claim against the exact result files, and each verdict must cite the file it rests on.`"*
* Submission Form Text §7: *"`Muse Glimmer set the wording rules for the public claims and audited the repository before pushes.`"*

That is explicitly **development / recipe-search / question-generation / claim-checking** — all offline, before or after the fact. The Form Text also offers a third leg:

* Form Text §7: *"`First, Meta's open weights are one of the test subjects. The third benchmark pair is Llama 3.2 1B base and Instruct, run through the same pipeline as the other pairs. Per the organizers' October 28 clarification, open-source Meta models count for the Stage One gate`"'* — echoed in README.md: *"`The same contest also ran on Meta's own open weights, Llama 3.2 1B base and Instruct.`"*

Llama is used as a **benchmark subject being compressed**, not as a model invoked to perform a product feature at runtime. The organizer clarification is cited only in the Form Text, not in the README, and it does not convert an evaluation dataset into a runtime integration. The gate requirement is the Muse Spark family in a real runtime role in the product itself. On this surface it is not shown.

**2. JUDGE-LEVEL BLOCKERS**

**BLOCKER 1 — (c) Contradicted headline timing and (b) unsupported do-it-yourself reproducibility**

README.md claims: *"`live hot-swap (0.104 s and 0.087 s, file-load times on the demo machine, in the recorded demo)`"* and *"`about 0.1 seconds (file-load time on the demo machine; the two recorded swaps measured 0.104 s and 0.087 s)`"*

Same surface, demo script: ON SCREEN description shows *"`and the swap line >>> SWAP: ... loaded live in 0.49s boxed in amber.`"* Script notes explain: *"`Swap wording is now 'well under a second' everywhere (true for both the 0.104s transcript of record and the 0.49s contended recording; 'about a tenth of a second' removed).`"* Two different numbers for the same claimed moment, with wording softened to hide the gap. A judge sees a headline metric that does not survive its own transcript.

Related runnable-claim blocker — README.md `Do it yourself`: *"`You need two models: a base model and a fine-tuned version of that same base, in safetensors format. 1. Make a patch ... python examples/make_patch.py --base <base-model-dir> --finetuned <finetuned-model-dir> --rank 32 --out patch.npz`"* — Repo file listing shows **no `requirements.txt`** and no install step, while `examples/hotswap_demo.py` imports `tokenizers`. Verifier fact confirmed. A judge following the README on bare Python hits `ModuleNotFoundError` — the "clone and run" claim is not self-contained where a judge looks.

**BLOCKER 2 — (d) Circular evaluation — same model writes the test and grades the test**

README.md / Form Text disclose but do not mitigate: *"`96 fresh held-out questions generated by Muse Spark`"* and *"`Muse Spark judging pass checked each headline claim against the exact result files`"* and *"`Muse Spark proposed the per-layer recipes, generated the fresh test questions, and judged every claim`"*

Form Text adds disclosure: *"`the held-out questions were also generated by Spark (the probe file is heldout96_probes_spark.json), so the question author and the claim checker are the same model; the recipe search never saw the questions before scoring, and we state the shared authorship plainly.`"* A judge reads this as Spark grading Spark's own homework — disclosed, but trust in the 23.2% headline rests entirely on a closed loop.

**BLOCKER 3 — (d) Trust theater — quantum audit and narrated demo**

README.md: *"`A subset of the results, picked using true quantum random numbers from IBM Quantum hardware, was re-audited end to end: 41 of 41 checks passed.`"* Fixture cited is `fixtures/qrng_fixture.json` with backend/job logged, but no verifiable proof in the surface that the numbers are quantum or that sampling was not cherry-picked. Reads as authority signaling.

Demo script production notes: *"`Narration: Vinay's voice, cloned locally with Chatterbox.`"* and Form Text §6: *"`the voice on the demo is the author's own voice, cloned locally with an open-source tool running on his own machine (disclosed on the video's closing slide). The submitted product itself uses no text-to-speech at runtime.`"* Disclosed, but a synthetic-voice demo with extensive panel-vote logs (`results/narration_vote.md`, `results/video_review_v5_panel.md` etc.) invites a judge to question what else is synthetic.

**BLOCKER 4 — (a) Prior work boundary — disclosed but structurally risky**

README.md and Form Text both state: *"`This repository contains only work built during the Meta Global AI Developer Hackathon, October 26 to November 4, 2026`"* and *"`Pre-existing work (not part of this submission): Fraction Compressor v0.1 to v0.3 and the Signet delta-transfer experiments live in the original repository, github.com/ganjikrishna/fraction-compressor. The compression and Signet methods were designed and validated there before the event. What is new in this repo is the factored runtime, the end-to-end task benchmark, and the Meta model comparison.`"* and *"`All code in this repo is original and was written during the event. What is ours is not the 1-bit format itself`"* 

Disclosure is present where a judge looks, which avoids an undisclosed-copy failure, but the repo still lists `BUILD_PLAN.md` and `docs/literature_sweep_2026-10-28.md` and builds on BitDelta/Delta-CoMe/LittleBit ideas *"`ideas only, no code`"* — a judge on a cold read cannot verify the clean-room claim from the surface alone and must take it on trust.

No additional headline math was found arithmetically unsupported beyond the timing contradiction; gap-closed percentages check against the table where flagged (e.g., second pair and 1.5B pair correctly noted as >100% and not a recovery fraction).



## Scores, quickstart, credibility (tokens this call: 20713)

As a cold judge (repo + README + form text + script/transcript only) — no benefit of doubt, no running code:

### SCORES

**Impact: 55/100 (weight 30%)**
*Why a judge lands here:* The `0.31 bits/weight, 51x smaller (19MB vs 988MB)` and `0.104s / 0.087s hot-swap` is a real frontier mechanism - one base, many behaviors, chip-not-note vs prompt memory. But the README itself prices the impact as narrow and lossy: patch closes only `23.2% of gap (0.605/2.607 nats)` on the headline Qwen2.5-0.5B pair, `15.9%` on Meta's Llama 3.2 1B, and `first-token accuracy 0.010 < base 0.031` - degraded. The judge reads `results/skill_demo.json: 1/10 clean` and the video's own line *"this is probability recovery, not solved tasks."* The submission correctly positions it as *only* for `weights-only, training-impossible, many-variants against one base` - a valid but niche wedge. Where training is available, your own LoRA baseline at *smaller* bytes `18,696,192 vs 19,358,176` closes `136% vs 23.2%` and ties full fine-tune accuracy. Impact is honest, bounded, not general.

**Use of Meta AI Tooling: 82/100 (weight 25%)**
*Why:* Clear Stage One PASS - Llama 3.2 1B is explicitly the third pair in pipeline (`results/third_pair_*`, README Benchmark Results), reported with weaker recovery and even `uniform -7.6% gap closed, below base`. That's the honesty test. Spark is not decoration: **in-loop** recipe designer (Alien Sweep per-layer rank allocation, `mlp_behemoth_lite` beating uniform `23.2% vs 2.1%` on 96 held-out), **over-loop** claim-judge citing result files, and generator of `heldout96_probes_spark.json`. Spark Open via Baseten/Fireworks + Glimmer wording rules corroborate. Deduction: judge flags the disclosed circularity - same model (Spark) authors the held-out questions *and* judges the claims (README `How these numbers are checked` + form `held-out questions were also generated by Spark`). Disclosed and search-never-saw-questions, but still single-model dependency.

**Demo: 67/100 (weight 25%)**
*Why:* On paper this is a polished, verifiable 178.63s cut: one AAC stream, -16 LUFS, real `asciinema` captures (not slides), boxed `JSON SCORE: parseable=False -> True` and `Capital of Japan: Lauderdale loop -> Tokyo`, spoken + printed clarification `does not compress the model... base stays full size`. But cold judge trips: 1) Narrow win - 2 prompts only, both format/instruction; the README failure case (NuExtract 1/10) is not in the video. 2) Timing slip: README claims `0.104s and 0.087s file-load times`, narration says `well under a second`, but script ON SCREEN box shows `>>> SWAP: ... loaded live in 0.49s` (v2 cast). Judge sees hedging after the 0.49s contested recording. 3) Cloned Chatterbox voice disclosed in small print - organizer-cleared but judge cannot assess delivery, plus heavy reliance on text boxes. Does the job, but does not prove generalization.

**Technical Depth and Execution: 84/100 (weight 20%)**
*Why:* Exceptional artifact trail for a solo indie track: factored runtime `Y=(XU)V^T` without rebuilding full matrix (`src/factored.py` + `tests/test_factored.py`), byte-exact pricing (`0.28 bits/weight at rank 32`), 4 pairs to 1.5B (Qwen 0.5B/1.5B, SmolLM2-360M, Llama 3.2 1B), 96 fresh held-out (24+72 split wins), BitDelta honest floor (`61.7MB` vs `38.5% vs 43.6%`) and LoRA out-of-style control (`62.0%` still beats `23.2%`), first-token gate + force-start control, Gemini recompute, Spark file-cited judging, quantum audit `41/41` from `fixtures/qrng_fixture.json`. Deduction: core 1-bit/factored idea is explicitly *inherited* from v0.1-v0.3 / BitDelta/Delta-CoMe (`NOTICE.md`, README `Prior art` - `ideas only, no code`), event work is the runtime + search + harness. Scale capped at 1.5B on one CPU home machine, and at 1.5B the Spark edge collapses to `+0.134 nats` and loses heldout24.

**WEIGHTED TOTAL: ~70.6 / 100**
`55*0.30=16.5 + 82*0.25=20.5 + 67*0.25=16.75 + 84*0.20=16.8 = 70.55`

---

### QUICKSTART TRIP POINTS (paper walk of README `Do it yourself`)

Judge follows README without API keys and without guessing installs:

1. **No dependency install step - immediate ModuleNotFoundError:** README `Do it yourself` step 1 starts `python examples/make_patch.py --base <base-model-dir>...` and `examples/hotswap_demo.py`. Repo listing has **no `requirements.txt` / `pyproject.toml` / `environment.yml`**. `examples/quickstart.py` says `needs only numpy` but `make_patch.py`/`hotswap_demo.py` import `tokenizers` (per Coordinator Fact) + `safetensors`/`transformers`. Judge on bare Python hits `ModuleNotFoundError: tokenizers`. README never mentions `pip install tokenizers safetensors transformers numpy`.

2. **No clone / Python version / hardware guidance:** Heading `In plain words` says `rank-32 file takes 144KB` but never defines `rank`, `recipe`, `bits per weight`. `Do it yourself` says `You need two models... in safetensors format` with placeholders `<base-model-dir>` - no example HF ID, no download command, no disk/RAM estimate (987M delta). No Python version.

3. **`--recipe` vs `--rank` dead end:** Step 1: `or pass a per-layer recipe file with --recipe instead of --rank` - no format, no example path. `examples/` has no `*.json` recipe example linked; judge can't discover schema.

4. **`--verify` step unexplained:** Step 2: `python examples/make_patch.py --verify patch.npz ...` - first mention of `--verify`; no output description, no failure mode.

5. **`Use it: load the patch together with the base model, as in examples/hotswap_demo.py`** - not runnable from README. No CLI given for hotswap, no model paths, no `python examples/hotswap_demo.py --base ... --patch ...` invocation. Judge must open file to guess.

6. **`results/make_patch_demo.txt` reference but not linked to command:** The `50.8x smaller` claim cites that file, but quickstart doesn't tell judge that file is the expected output to compare against.

7. **Small print vs spoken mismatch a judge notes but can't verify without watching:** Script notes `0.104s and 0.087s, file-load times on the demo machine` vs ON SCREEN `0.49s` - README and script disagree on the headline live metric.

### CREDIBILITY READ

**Rigorous, not undermining - but at a cost.** Judge reads the `lossy, 23.2% gap, 0.010 < 0.031, LoRA at matched bytes closes far more` framing as **scientific rigor that buys trust**. Byte-fair variants (`mlp_behemoth_lite 19,358,176 < 19,434,496`), `>100% gap` warnings, quantum audit, and file-cited Spark judging are what make the 23.2% believable at all.

**Single Strongest Point a judge would name:** The full verification harness with adverse baselines included in-repo - Spark-generated 96 held-out + Spark file-cited judging + Gemini recompute + Glimmer wording rules + quantum-sampled `41/41` audit + honest BitDelta (`62MB floor wins 43.6% vs 38.5%`) and LoRA (`62.0% out-of-style still beats 23.2%`) comparisons. Almost no hackathon submission shows its losing comparisons.

**Single Weakest Point a judge would name:** The headline result is *probability recovery with degraded task accuracy* - `first-token accuracy 0.010 vs base 0.031` and `23.2%` vs LoRA `136% (139.5% in-style)` at *fewer* bytes with ~8 hours training - which, in the judge's chair, frames the patch as strictly dominated wherever training is possible (the common case) and only useful for the narrow `weights-only, no-training, hot-swap many variants` niche that the submission itself defines.

TOTAL JUDGE TOKENS muse-spark-1.2: 44313


---

## Judge pass: muse-spark-1.1 (verbatim)

# Judge pass reviewer output: muse-spark-1.1

## Gate and blockers (tokens this call: 23431)

### 1. STAGE ONE GATE

**GATE: PASS**

Meta model use is stated where a judge looks (README + form text Section 7) and is more than judging:

From README - Llama as runtime base model:
> "The same contest also ran on Meta's own open weights, Llama 3.2 1B base and Instruct."

From README - Spark as in-loop recipe designer:
> "Muse Spark proposed uneven per-layer compression recipes (the Alien Sweep)."

From README - Spark as claim checker (judging role):
> "a Muse Spark judging pass checked each headline claim against the exact result files it cites"

From Form Text Section 7 - explicitly names gate qualification:
> "First, Meta's open weights are one of the test subjects. The third benchmark pair is Llama 3.2 1B base and Instruct, run through the same pipeline as the other pairs."
> "Per the organizers' October 28 clarification, open-source Meta models count for the Stage One gate and the tooling criterion"
> "Second, Muse Spark is the recipe designer in the loop. In the recipe search we call the Alien Sweep (the project's name for its in-the-loop recipe search), Spark proposes per-layer rank allocations (recipes) for compressing a fine-tune's patch under a hard byte budget, training-free."
> "Third, Muse Spark is the claim checker."

While one Spark role is judging claims, two other runtime roles are present: Llama 3.2 1B loaded as a base model in the factored runtime `Y = (X U) V^T`, and Spark generating per-layer rank recipes inside the Alien Sweep search that are applied at runtime. This is not only dev-tooling.

### 2. JUDGE-LEVEL BLOCKERS

**Blocker 1 - (c) Contradicted hot-swap timing claim:**

README claims:
> "live hot-swap (0.104 s and 0.087 s, file-load times on the demo machine, in the recorded demo)"

Demo video stand-in (the actual on-screen text the judge will see) shows:
> "and the swap line `>>> SWAP: ... loaded live in 0.49s` boxed in amber."

Production notes admit two recordings:
> "Swap wording is now 'well under a second' everywhere (true for both the 0.104s transcript of record and the 0.49s contended recording; 'about a tenth of a second' removed)."

The headline "tenth of a second" speed is contradicted by the 0.49s presented in the demo highlight.

**Blocker 2 - (d) Reproducibility / distrust - missing dependency:**

Repo file listing contains no `requirements.txt`:
> ".gitignore, BUILD_PLAN.md, LICENSE, NOTICE.md, README.md, docs/demo_script.md..."

README "Do it yourself" gives no install step:
> "You need two models: a base model and a fine-tuned version of that same base, in safetensors format."

The coordinator fact that the hot-swap demo imports `tokenizers` means the quickstart as written fails with `ModuleNotFoundError` on a bare follow-the-README run, undermining the "Do it yourself" and "can be rerun" claims.

No other provenance blockers found beyond these - prior work is explicitly disclosed:
> "This repository contains only work built during the Meta Global AI Developer Hackathon... Pre-existing work (not part of this submission): Fraction Compressor v0.1 to v0.3"

## Scores, quickstart, credibility (tokens this call: 19979)

### Cold Judge Scoring - Fraction Compressor v0.4

**Impact: 58/100**
Storage win is real and measured: 19,434,496B vs 987,922,432B = 51x on Qwen2.5-0.5B headline, ~79x on 1.5B, with live swap timed 0.104s / 0.087s file-load in `results/hotswap_demo_transcript.txt`. But own disclosure caps impact: gap-closed 23.2% on 96 fresh questions, first-token accuracy 0.010 vs base 0.031, knowledge bucket 3.7% vs uniform 7.8%, NuExtract real skill 1/10 clean vs full fine-tune 9/10, and matched-byte LoRA at 18,696,192B closes 136% avg vs patch 23.2% and ties full accuracy. Position is honestly narrowed to "where training cannot happen and degraded accuracy acceptable" - rigorous but small niche.

**Use of Meta AI Tooling: 84/100**
Passes Stage One gate. Llama 3.2 1B base+Instruct is the third pair with weaker recovery reported -14.201 vs base -13.718. Spark is not a wrapper: it's the in-loop recipe designer for the Alien Sweep proposing per-layer rank allocations under hard byte budget, and the claim-checker requiring file citations. Logs in `results/api_usage_log.jsonl`, plus Spark Open via Baseten/Fireworks and Glimmer wording audit. Deduction: probe file `heldout96_probes_spark.json` - same model generates the evaluation questions it then judges, disclosed in submission draft but circular.

**Demo: 81/100**
Video stand-in script shows real `asciinema` captures, not mocks: Base strict JSON -> rambles `parseable=False` boxed red, swap line `loaded live in 0.49s` amber, patched same prompt `parseable=True` green, plus Tokyo fix. Numbers block opens with Llama weak result first, then headline Qwen. Speaks measure correctly as log-prob, not task solve, and voices the two hardest disclosures: "first-word accuracy stays below base's own" and "plain one-bit closes more at sixty-two megabytes." Under 3 min at 178.627s, single AAC, -16 LUFS spec met. Deduction: relies on cloned voice with small-print disclosure "Vinay's voice, cloned locally with Chatterbox" - may distract.

**Technical Depth and Execution: 86/100**
Substantial execution: `src/factored.py` factored runtime Y=(XU)V^T never rebuilds full matrix, `tests/test_factored.py`, per-layer budget search across four open models up to 1.5B, 96 held-out questions unseen by search, two honest rivals - BitDelta at floor 61,745,828B closing 43.6% vs factored 38.5% at 61,258,816B, and distilled LoRA baseline 18.7MB beating patch. Verification is standout: Spark judging pass with file citations, Gemini arithmetic recompute `results/gemini_validation_day2.md`, Glimmer reference check for wording rules, IBM Quantum fixture `fixtures/qrng_fixture.json` powering 41/41 audit `results/quantum_audit.json`. Deduction: core 1-bit delta idea from BitDelta/Delta-CoMe/LittleBit, repo admits "superiority over other training-free low-rank formats was not established" and CPU-only home bound.

**Weighted Total: 75.9**
0.30*58 + 0.25*84 + 0.25*81 + 0.20*86 = 17.4 + 21.0 + 20.25 + 17.2 = **75.85**

---
### QUICKSTART TRIP POINTS - paper walk

README `# Do it yourself` block:

1. **No dependency install.** README never mentions `pip install`, no `requirements.txt` in file listing, no `pyproject.toml`. Judge on bare python hits `ModuleNotFoundError`. Coordinator fact: `examples/hotswap_demo.py` imports `tokenizers` which README never mentions. `examples/make_patch.py` will need `torch`, `safetensors`, `numpy`. `examples/quickstart.py` says "needs only numpy" but install step still missing.

2. **No model acquisition.** Args `<base-model-dir>` / `<finetuned-model-dir>` are placeholders. No HF repo IDs, no `git lfs` / `huggingface-cli download` command for Qwen2.5-0.5B base/Instruct, SmolLM2-360M, Llama 3.2 1B pairs used in `results/`. Judge cannot run step 1.

3. **`--recipe` unexplained.** Line "or pass a per-layer recipe file with `--recipe`" - no format, no example file path, no schema. `docs/` doesn't list a recipe spec.

4. **Clone step missing.** Instructs "Clone the repo" in video narration but README quickstart starts at `python examples/make_patch.py` without `git clone https://github.com/...` and `cd`.

5. **Verification dead end.** Step 2 `python examples/make_patch.py --verify patch.npz ...` - what does verify output? No expected output described, no exit code contract.

6. **Use step vague.** Step 3 "as in `examples/hotswap_demo.py`" - that demo needs base model loaded and patch path - again no arg docs. `results/make_patch_demo.txt` referenced but not linked as runnable log.

### CREDIBILITY READ

**Reads as rigorous**, not undermining in intent. Disclosure is systematic: every negative number is file-cited `results/*.json`, separate `results/skill_limit_consultation.md`, BitDelta baseline at own floor price, LoRA out-of-style control still 62.0% vs 23.2%. Quantum audit and Glimmer rule-set are rare at hackathon.

**Strongest point a judge would name:** The verification harness - file-cited Spark claim judging + Glimmer wording rules + Gemini independent recompute + quantum-random 41/41 audit, with Llama 3.2 1B weak result published even though it hurts headline.

**Weakest point a judge would name:** Own table proves trained alternative dominates at same bytes - distilled LoRA 18.7MB = 136% gap closed vs patch 23.2% with base-beating first-token accuracy, and patch's own first-token accuracy 0.010 < base 0.031, plus first-token-gated skill 1/10 vs full 9/10. Forces project into "weights-only, many variants, no training allowed" niche where partial probability recovery is acceptable.

TOTAL JUDGE TOKENS muse-spark-1.1: 43410
