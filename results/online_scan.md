# Online scan of the live repo (Sat Oct 31, 2026)

Ordered by Vinay: since the pre-submission batch is on GitHub, scan what is LIVE. Judges: muse-spark-1.2 and muse-spark-1.1, opening the live repo cold on the deterministic results below plus the live README and file listing.

## Step 1, deterministic verification

- Fresh shallow clone of https://github.com/ganjikrishna/fraction-compressor-v0.4; head confirmed: fd075f6cef933f6a08f70d7c09b461f99c1c8e92.
- Live repo: 183 files. SHA-256 comparison of the 40 pushed files against the reviewed local tree:

| File | Result |
|---|---|
| PROVENANCE.md | IDENTICAL |
| .env.example | IDENTICAL |
| requirements.txt | IDENTICAL |
| results/fresh_hard_check.md | IDENTICAL |
| results/fresh_check_fixes.md | IDENTICAL |
| results/provenance_live_check.md | IDENTICAL |
| docs/youtube_upload_pack.md | IDENTICAL |
| docs/x_post_pack.md | IDENTICAL |
| docs/judge_path_check.md | IDENTICAL |
| docs/submission_day_checklist.md | IDENTICAL |
| results/7b_push_panel.md | IDENTICAL |
| results/7b_simple_push_record.md | IDENTICAL |
| results/api_usage_log.jsonl | DIFFER (explained below) |
| README.md | IDENTICAL |
| docs/demo_script.md | IDENTICAL |
| results/skill_limit_consultation.md | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_heldout96.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_recompute.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_stage2.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_and_regularization.md | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_chat_base.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_chat_down_king.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_chat_full_a025.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_chat_full_a05.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_chat_full_delta.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_chat_uniform_rank32.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_corrected_base.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_corrected_down_king.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_corrected_full_a025.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_corrected_full_a05.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_corrected_full_delta.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_eval_corrected_uniform_rank32.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_gen.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_recompute.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_spark_gen_judging.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_spark_interpretation.json | IDENTICAL |
| results/fifth_pair_supplementary/fifth_pair_yardstick_spark_interpretation.md | IDENTICAL |
| results/fifth_pair_supplementary/index.md | IDENTICAL |
| results/fifth_pair_supplementary/spark_judging_7b.json | IDENTICAL |
| results/fifth_pair_supplementary/spark_judging_7b.md | IDENTICAL |

39 of 40 byte-identical. The one difference, results/api_usage_log.jsonl: the live file is an exact byte-prefix of the local file; exactly one line (74,384 live bytes vs 74,605 local) was appended locally after the push, the Wonder substitute-validator log entry, which rides the Nov 2 link push. No pushed content differs.

Exclusions, all confirmed ABSENT from live: docs/submission_draft.md (local by design); results/updates_question_panel.md; results/alien_math_panel.md; results/7b_interpretation_panel.md; results/7b_interpretation_claude.md; any .npz file (none in the whole live tree); video/rough_cut_v7_final.mp4 (owner's decision, YouTube link replaces it Nov 2); fifth_pair originals in results/ root (only the fifth_pair_supplementary folder exists).

## Step 2, judge verdicts (verbatim)

### muse-spark-1.2 (total tokens 12901: prompt 7979, completion 4922)

**Verdict: PASS** - Live clone is byte-identical to reviewed tree on all claims. No drift, no hidden 7B claim, no broken references.

### 1. README vs Reviewed Claims - NO DRIFT

Deterministic provenance proves no drift:
> `39 of the 40 pushed files are BYTE-IDENTICAL live vs the reviewed local files... The 40th, results/api_usage_log.jsonl: the live file is an exact prefix of the local file; exactly ONE line was appended locally after the push`

Live `README.md` reproduces every `KNOWN-GOOD` headline exactly:

* **Lossy stated up-front, two places:**
> `That smaller file is lossy: its first-token accuracy is 0.010, below the base model's own 0.031 (full figures in the next paragraph).`
> `The patch is a lossy, training-free distribution format for a fine-tune delta: at 19,358,176 bytes it closes 23.2% of the gap (0.605 of 2.607 nats), with first-token accuracy 0.010 (below base 0.031)`

Matches Known-Good: `19,358,176 bytes, 23.2%, 0.010 vs 0.031`

* **Full delta size:**
> `rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference`

Matches Known-Good: `987,922,432 bytes`

* **Hot-swap qualified as file-load:**
> `live hot-swap (0.104 s and 0.087 s, file-load times on the demo machine, in the recorded demo)`

Matches Known-Good: `0.104 s / 0.087 s are file-load times`

* **LoRA matched-byte correctly as ratio, not recovery fraction:**
> `Where training is available, a distilled LoRA at 18,696,192 bytes, just under the patch's size, closes far more of the gap on these tests (1.362 against 0.232).`

Matches Known-Good: `1.362 (a ratio, never a recovery fraction)` - presented as `1.362 vs 0.232`

* **Second/Fourth pair >100% handled correctly - no recovery fraction claimed:**
> `so the gap-closed percentage goes above 100% here. That means the percentage is NOT a share of the fine-tune recovered for this pair. For this pair, the raw score margin (0.293 points) is the honest measure.`
> `so the gap-closed figure goes above 1.0 (1.307 against 1.279) and is NOT a share of the fine-tune recovered on this pair; the raw score margin (about 0.13 points) is the honest measure.`

* **Four-pair story only in README, no 7B headline:** Sections are `First pair: Qwen2.5-0.5B`, `Second pair: SmolLM2-360M`, `Third pair: Llama 3.2 1B`, `Fourth pair: Qwen2.5-1.5B` + `Baseline: plain 1-bit delta`. No 7B numbers in main benchmark.

**No number contradicts Known-Good. No new claim added.**

### 2. Submission Story & 7B Supplementary - NO CONTRADICTION

* **Submission story = four pairs, lossy + training-free** is preserved live. Supplementary material is isolated as designed:

Live listing `183 files` shows `results/fifth_pair_supplementary/` contains 24 files and **zero** `results/fifth_pair_*.json` outside it - as proven `ABSENT from live: any fifth_pair originals in results/ root outside the supplementary folder.`

* **Supplementary `results/fifth_pair_supplementary/index.md` reads as supplementary with inversion at same prominence, verbatim:**

> `Supplementary exploratory material, published for transparency. This folder is not part of the submission claim set, and no four-pair result depends on anything in it.`
> `The reference inverts on this pair. On the held-out 96-question battery, the full fine-tune delta scores below the base model on mean target logprob (full delta -15.974, base -6.916), and it stays below base on the corrected battery as well (full delta -8.634, base -8.043). With the reference inverted, gap_closed is null at 7B: no fraction figure is defined for this pair, and none is claimed for any 7B configuration.`
> `A shrinkage control explains the patch's profile. A plain copy of the full delta turned down to 25% strength reproduces and exceeds the selected factored configuration's (down_king) profile`

Matches Known-Good: `reference inversion (full delta scores below base), no recovery fraction claimed; the 7B material exists ONLY as a clearly labelled supplementary results folder.`

No 7B recovery fraction, no 7B headline, no confusion with four-pair claims.

### 3. Judge Trip Hazards (live-only view) - NONE

All references in live `README.md` and `index.md` resolve live:

* `docs/how-it-works.svg`, `docs/why-it-matters.md`, `docs/intent.md`, `NOTICE.md`, `results/make_patch_demo.txt`, `examples/hotswap_demo.py`, `examples/quickstart.py`, `src/factored.py`, `fixtures/qrng_fixture.json` - all present in `LIVE REPO FILE LISTING`
* Every file named in `fifth_pair_supplementary/index.md` (`fifth_pair_yardstick_and_regularization.md`, `fifth_pair_heldout96.json`, `fifth_pair_stage2.json`, `fifth_pair_yardstick_eval_chat_*.json`, `fifth_pair_yardstick_eval_corrected_*.json`, `spark_judging_7b.md` etc.) - present
* Expected absences are not trips: `docs/submission_draft.md (local by design)`, `video/rough_cut_v7_final.mp4 (excluded by the owner's decision; a YouTube link replaces it on Nov 2)`, any `.npz` - confirmed absent by provenance check. `video/narration_v7.txt` + `video/v7_notes.md` remain as text replacement.
* Layout is not confusing: 7B is in a single `fifth_pair_supplementary/` folder with `index.md` disclaimer, not mixed into `results/` root or `README` benchmark table.

**No broken links, no missing cited file, no layout confusion requiring local review to understand.**

**PASS**

### muse-spark-1.1 (total tokens 11499: prompt 7979, completion 3520)

Live clone at fd075f6 matches reviewed tree. Verdict: **PASS**

**1. README vs known-good facts – no drift**

Quoted live README lines:

> `What shrinks to a fraction is the fine-tune's change: from about 1 GB to about 19 MB on the Qwen2.5-0.5B pair used in these tests. That smaller file is lossy: its first-token accuracy is 0.010, below the base model's own 0.031`

> `The patch is a lossy, training-free distribution format for a fine-tune delta: at 19,358,176 bytes it closes 23.2% of the gap (0.605 of 2.607 nats), with first-token accuracy 0.010 (below base 0.031), and it is not a training aid.`

> `live hot-swap (0.104 s and 0.087 s, file-load times on the demo machine, in the recorded demo)`

> `rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller.`

> `a distilled LoRA at 18,696,192 bytes, just under the patch's size, closes far more of the gap on these tests (1.362 against 0.232).`

Matches known-good:
* 19,358,176 bytes / 23.2% / 0.010 vs 0.031 – exact
* full delta fp16 987,922,432 bytes – exact
* hot-swap times labeled as file-load times – exact
* LoRA 1.362 is presented as raw margin vs 0.232, not as recovery fraction
* No other numbers contradict. Lossy stated up front in paragraph 2.

**2. Submission story / 7B supplementary**

* README benchmarks only four pairs: First / Second / Third / Fourth. No 7B headline claim.
* File listing shows no `results/fifth_pair*` in root; all 7B material is ONLY under `results/fifth_pair_supplementary/` – as required.
* Supplementary index carries inversion with correct prominence:

> `Supplementary exploratory material, published for transparency. This folder is not part of the submission claim set, and no four-pair result depends on anything in it.`

> `**The reference inverts on this pair.** On the held-out 96-question battery, the full fine-tune delta scores below the base model on mean target logprob (full delta -15.974, base -6.916), and it stays below base on the corrected battery as well (full delta -8.634, base -8.043). With the reference inverted, gap_closed is null at 7B: no fraction figure is defined for this pair, and none is claimed for any 7B configuration.`

No recovery fraction claimed for 7B. Shrinkage control also disclosed.

**3. Judge-trip hazards – none**

* All paths referenced in README exist live: `docs/how-it-works.svg`, `docs/why-it-matters.md`, `docs/intent.md`, `examples/hotswap_demo.py`, `examples/quickstart.py`, `results/make_patch_demo.txt`, `results/skill_demo.json` etc – present in 183-file live listing.
* Byte-identical verification stated: 39/40 files identical, 40th (`results/api_usage_log.jsonl`) is exact prefix with one local-only appended line – expected.
* Confirmed absent live as designed: `docs/submission_draft.md`, skipped panels, any `.npz`, `video/rough_cut_v7_final.mp4`, any fifth_pair files outside supplementary – matches listing.
* No broken links, no hidden 7B claim in root.

**Final: PASS – live repo matches reviewed claims exactly, lossy disclosed up front, four-pair story intact, 7B clearly supplementary with inversion and null gap_closed.**
