# Glimmer repo audit sweep (2026-10-28)

Independent strict audit of the pushed Fraction Compressor v0.4 repository, requested by Vinay: have Glimmer check the existing repo for anything that needs correcting.

## Audit record

- Repository: `ganjikrishna/fraction-compressor-v0.4`
- Pushed head audited: `3933fae16f5e1673cac38a000533a35fb7b0ecda` (verified as the current `main` head through the GitHub connector before the audit).
- Material given to Glimmer: the exact pushed versions of `README.md`, `NOTICE.md`, `docs/why-it-matters.md`, `docs/demo_script.md`, and `BUILD_PLAN.md`, plus an evidence digest computed from pushed result files at the same head (`results/alien_sweep_heldout96.json`, `results/second_pair_heldout96.json`, `results/third_pair_heldout96.json`, `results/fourth_pair_heldout96.json`, `results/bitdelta_baseline.json`, `results/skill_demo.json`, `results/skill_demo_forced.json`, and the other spot-check files named in the prompts).
- Excluded as local-only and not part of the pushed state: the later literature-citation edits in `NOTICE.md`, `README.md`, and `docs/why-it-matters.md`; `docs/intent.md`; `docs/literature_sweep_2026-10-28.md`; `results/cloning_question_panel.md`; `results/video_review_v2.md`; the entire `video/` directory; and all fifth-pair result/example files.
- Route: Flash-local call over SSH. Pi's model config on Flash routes `nvidia/meta/muse-glimmer-30b` through the local OmniRoute provider to NVIDIA NIM. Every response's served-model field confirmed `meta/muse-glimmer-30b`. This was a Flash-local NIM call, not a Meta Model API or Baseten call, so it is not logged in `results/api_usage_log.jsonl`; this file is the record.
- Method note: the first combined call (Prompt 0) hit its completion cap inside the reasoning channel and returned no final content (finish reason `length`; usage: prompt 25,620, completion 12,000, total 37,620). It produced no findings and was not used. The audit was rerun as three document-scoped calls with `reasoning_effort: low`, followed by a final adjudication call that received a corrected evidence pack for fields the first-pass digest had omitted, plus candidate passages the first pass had not reached. Reasoning channels are not reproduced, following the convention of the earlier Glimmer records in this repo; every final-content reply is reproduced verbatim below.
- Call usage (served model `meta/muse-glimmer-30b` in all calls):
  - Part A, README: prompt 20,491, completion 4,544, total 25,035; finish `stop`.
  - Part B, NOTICE + why-it-matters: prompt 19,341, completion 3,209, total 22,550; finish `stop`.
  - Part C, demo script + BUILD_PLAN: prompt 23,546, completion 4,804, total 28,350; finish `stop`.
  - Final adjudication: prompt 8,933, completion 3,415, total 12,348; finish `stop`.
- No repository file was edited as part of this sweep. This record is local only and was not pushed.

## Final adjudicated reply (verbatim)

**WITHDRAWALS – first-pass findings contradicted by corrected evidence pack**

* README.md – layer size 8.4 MB arithmetic error. Withdrawn. Pushed `src/factored.py` storage_bytes gives 147,456 bytes for 2048×2048 rank-32. Full fp16 matrix is 8,388,608 bytes = 8.388608 decimal MB ≈ 8.4 MB SI, 8.0 MiB. README “8.4 MB; 144 KB” is consistent with SI rounding.
* README.md – 0.28 bits per weight unverifiable. Withdrawn. Same formula gives 147,456*8 / 4,194,304 = 0.28125 bpw for that one 2048×2048 layer. README “0.28 bits per weight for one large layer at rank 32” is derivable from pushed code.
* README.md – BitDelta baseline gap-closed percentages 43.6% vs 38.5% unverifiable. Withdrawn. `results/bitdelta_baseline.json` contains base_mean_target_logprob -11.149778062515304, full_delta_mean_target_logprob -8.542466235416498, bitdelta_init mean -10.012813627503721 gap_closed overall 0.43606768595711076 price 61,745,828, factored_uniform_rank108 mean -10.146044864550612 gap_closed overall 0.3849686054166987 price 61,258,816. Percentages are source-backed.
* docs/why-it-matters.md – BitDelta 43.6% / 38.5% outruns evidence. Withdrawn for same reason as above.
* docs/why-it-matters.md – first-token margins -6.33 / -1.29 / +4.60 unverifiable. Withdrawn. `results/skill_demo_recipe.json` mean_margin: base -6.332; rank32_uniform -1.2942; full_delta +4.6005; spark_recipe -4.1422. Gate counts base 0/10, rank32 1/10, full 10/10.
* docs/why-it-matters.md – missing `results/why_debate.md` and `*validation_forced*` files. Withdrawn. Snapshot sync shows `results/why_debate.md` pushed and validation_forced files: `results/glimmer_validation_forced.md`, `results/spark_validation_forced.json`, `results/spark_validation_forced.md`, `results/gemini_validation_forced.md`, `results/sparkopen_validation_forced.md`, `results/sparkopen_fireworks_validation_forced.md`.
* docs/why-it-matters.md – hot-swap “tenth of a second” unsupported. Withdrawn. `results/hotswap_demo.json` swaps seconds 0.104 and 0.087. “about a tenth of a second” is source-backed; reference excerpt `docs/demo_script.md` line 69 “patch loaded live in 0.09s” is consistent.
* docs/demo_script.md – audit claim “41 of 41 checks passed” unverifiable. Withdrawn. `results/quantum_audit.json` quantum_source fixture `fixtures/qrng_fixture.json`, backend ibm_fez, job_id dbfouq7pc3tc739nvkt0, 32 qubits, 2048 shots, 3 qpu_seconds, 8192 random bytes; selection 8 distinct indices [1,10,20,8,21,12,5,22] from 24 held-out items; summary n_checks 41, n_passed 41, all_pass true.
* docs/demo_script.md – BitDelta baseline gap-closed percentages unverifiable. Withdrawn for same reason as README BitDelta.

**RETAINED FIRST-PASS FINDINGS – restated once**

* HIGH – Submission rule / demo opening mismatch. File `BUILD_PLAN.md` Scope / Demo video plan approved Oct 26: “The 3-minute demo video opens with one line stating what was pre-existing and what was built this week.” File `docs/demo_script.md` 0:00-0:25 opens with product title card/narration “This is Fraction Compressor…”. Required pre-existing / built-this-week disclosure is at 0:25-0:44. Correction: move required disclosure to first on-screen/spoken slot 0:00-0:25 or formally amend BUILD_PLAN.
* HIGH – Approved timing shape vs script timing. `BUILD_PLAN.md` shape: 0:00 opening + problem; 0:30 hot-swap moment; 1:30 benchmark numbers; 2:15 Muse Spark judging + quantum audit. `docs/demo_script.md` hot-swap is 1:21-1:48, benchmark numbers 1:48-2:31. Correction: re-time script to approved anchors or amend approved plan.
* LOW – Rounding presentation. `docs/demo_script.md` 1:48-2:31 “The patch is fifty-one times smaller: nineteen million bytes against nine hundred eighty-eight million.” 987,922,432 / 19,434,496 = 50.833447. “51x” is rounded. No change required; optionally note “≈51×”.
* LOW – NOTICE.md future date unverifiable. `NOTICE.md` “written during the Meta Global AI Developer Hackathon (October 26 to November 4, 2026)…”. Date range is future relative to typical publication and cannot be verified from digest. Keep as attribution; no numeric correction needed.

**CANDIDATE PASSAGES AUDIT**

*CANDIDATES CLEARED*

* I. Demo word count. `docs/demo_script.md` header “Total narration: 440 words”. Independent whitespace and word-character counts of the eight NARRATION blocks give exactly 440. Clear.
* B. Fourth-pair ratio wording. README.md line 72 and BUILD_PLAN.md “about 79x smaller” for 3,087,138,816-byte full delta vs Down Dominator 38,623,232 = 79.9326 and vs uniform 39,046,144 = 79.0657. `docs/demo_script.md` on-screen “about 80x smaller” is acceptable rounding. No correction required.

*FINDINGS FROM CANDIDATE PASSAGES*

* MEDIUM – Misleading bits-per-weight shorthand. README.md line 5 “stored at about 1 bit per weight”; README.md line 11 “is kept as 1-bit signs” with priced example 0.28 bpw; docs/why-it-matters.md line 3 “at 1 bit per weight”. Evidence: all-in priced rate on Qwen pair is 0.314753 bpw uniform, 0.313517 bpw lite. U signs are 1-bit per stored sign entry, V is fp16 and scales fp32. “about 1 bit per weight” / “at 1 bit per weight” overstates the all-in price and conflates sign storage with total price. Correction: qualify as “U signs are stored as 1-bit signs; all-in priced rate is ≈0.31 bpw on the Qwen pair” or similar.
* HIGH – NOTICE.md Models section materially incomplete. `NOTICE.md` Models lists Qwen2.5-0.5B pair, SmolLM2-360M pair, Llama-3.2-1B pair. Pushed experiments also use Qwen/Qwen2.5-1.5B and Qwen2.5-1.5B-Instruct, `examples/fourth_pair_stage2.py` lines 1,24,896-897, Apache 2.0, subject of README fourth-pair section. Skill test uses numind/NuExtract-1.5-tiny, `examples/skill_demo.py` lines 10-11,230, MIT license, subject of README Known limit section. Correction: add Qwen2.5-1.5B / Qwen2.5-1.5B-Instruct Apache 2.0 and NuExtract-1.5-tiny MIT to Models section.
* MEDIUM – Originality/authorship inconsistency. `NOTICE.md` lines 5-9: “All code, documentation, evaluation items, and results in this repository are original work by Vinay K Ganji Krishna… No third-party code is included… and no code was copied…”. README credits “Implementation, benchmarking, and documentation were carried out with Ember, an AI agent powered by Muse Spark, working under the author's direction” and benchmark 96 fresh questions and recipes were generated by Muse Spark. Correction: qualify NOTICE originality statement to acknowledge AI-assisted generation and direction, or align README credit with NOTICE.
* HIGH – Universal gate wording outruns evidence. `NOTICE.md` lines 47-51: contribution is “the first-token gate diagnosis (skills whose first generated token decides success transfer weakly through any small patch)”. Evidence base is one gated skill NuExtract JSON extraction on one model pair, tested at ranks 32/64/128 and one Spark recipe; README Known limit scopes to “one kind of skill” and “in this test”. Correction: narrow to “in this test, one gated skill transfers weakly through small patches” or provide additional evidence.
* MEDIUM – BUILD_PLAN stale headline metric. `BUILD_PLAN.md` Scope item 1: “Memory read per token is the headline metric.” No supplied result file measures memory read per token; repo reports storage bytes, patch sizes, swap times 0.104/0.087 s, peak RSS. Correction: replace headline metric with reported metric or add measurement.
* MEDIUM – BUILD_PLAN benchmark mislabel. Scope item 2: “End-to-end task-accuracy benchmark… scored on task answers”. Delivered headline metric is mean target logprob; README warns first-token accuracy stays low and “these are score results, not proof the model solves the tasks”. Correction: change to mean target logprob / score benchmark.
* MEDIUM – BUILD_PLAN Scope item 3 stale/superseded. Scope item 3: “Muse Spark (Meta Model API) runs the same probe sets as a hosted reference, and Muse Spark Open is the planned open-weight candidate if time allows.” Pushed text and README show Spark generated fresh probes, proposed recipes, and judged claims; Spark Open via Baseten generated recipes and validated results. Spark did not run probe sets as hosted reference in benchmark table. Correction: update Scope item 3 to reflect actual roles.
* MEDIUM – BUILD_PLAN internal force-start contradiction left standing. Working note “Force-start control test (Oct 28)” describes patch as “a small real edge beyond the trigger”. Later working note “Force-start validation (Oct 28)” records Spark 1.3 and both Spark Open routes ruled “a small real edge” too strong; README and why-it-matters now read “one clean more than the forced base, which at 10 prompts is within sampling noise…”. Earlier note remains in same document. Correction: remove or strike-through superseded note.
* MEDIUM – Demo narration ambiguity. `docs/demo_script.md` numbers narration: “Same pattern on SmolLM2; on a model three times bigger, Spark's recipe won by nought point one three four nats, inside budget.” SmolLM2-360M is smaller than Qwen2.5-0.5B; “three times bigger” refers to separate Qwen2.5-1.5B scale test. On-screen notes list SmolLM2-360M and Qwen2.5-1.5B scale lines separately. Spoken sequence can misattach “three times bigger” to SmolLM2. Correction: rephrase narration to clearly separate SmolLM2 result from Qwen2.5-1.5B scale result.

**OVERALL VERDICT: NO**
The pushed repo at 3933fae is not clean to submit as-is; retained and newly identified findings remain.

---

## First-pass replies (verbatim)

### Part A reply: README

**FINDINGS – README.md only**

### 1. Factual arithmetic error – layer size example
* Severity: HIGH
* Category: arithmetic/factual error
* File + location: README.md – “In plain words” paragraph
* Quoted phrase: “One layer stored the normal way takes 8.4 MB; our rank-32 file takes 144 KB”
* Problem: Evidence digest independent arithmetic spot calculation uses 8,388,608 bytes / 147,456 bytes = 56.888889 for the one-layer example. 8,388,608 bytes = 8.0 MB, not 8.4 MB. 147,456 bytes = 144 KB is correct. The 8.4 MB figure is not supported by the pushed digest.
* Recommended correction: Replace “8.4 MB” with the digest-supported 8,388,608 bytes ≈ 8.0 MB, or state the exact byte values used in the repo, and keep the 144 KB rank-32 figure.

### 2. Claim outrunning evidence – BitDelta baseline gap-closed percentages
* Severity: HIGH
* Category: claims outrunning evidence / UNVERIFIABLE
* File + location: README.md – “Baseline: a plain 1-bit delta, priced honestly”
* Quoted phrase: “the BitDelta initialization … closes 43.6% of the gap on the same 96 questions, against 38.5% for our factored format at uniform rank 108 priced just under it (61,258,816 bytes).”
* Problem: Evidence digest provides BitDelta pricing: n_matrices 169, bitdelta_init_price_bytes 61745828, factored_matched_price_bytes 61258816, factored_rank_plus_one_price_bytes 61809136, and mean_target_logprob values for bitdelta_init -10.012813627503721 and factored_uniform_rank108 -10.146044864550612. No gap_closed percentages for these two configs are supplied in the digest. The 43.6% vs 38.5% numbers are therefore UNVERIFIABLE from the pushed result JSON at head 3933fae16f5e1673cac38a000533a35fb7b0ecda.
* Recommended correction: Either cite the exact result file and values that produce 43.6% / 38.5% and add them to the evidence digest, or downgrade the statement to UNVERIFIABLE and remove the specific percentages until they are verifiable from pushed results.

### 3. Unverifiable / inconsistent bits-per-weight claim
* Severity: MEDIUM
* Category: stale / unverifiable number
* File + location: README.md – “In plain words”
* Quoted phrase: “priced byte for byte by the code: 0.28 bits per weight for one large layer at rank 32 (the exact price depends on layer size and rank).”
* Problem: Evidence digest gives Qwen pair all-in effective bits/weight for uniform price = 0.314753 bpw; for lite = 0.313517 bpw. No pushed evidence supports a 0.28 bits/weight figure for “one large layer at rank 32”. The claim is UNVERIFIABLE from the digest and inconsistent with the repo-wide effective bits/weight numbers that are available.
* Recommended correction: Replace the 0.28 bits/weight example with a digest-supported figure, e.g., the repo-wide effective bits/weight ≈0.315 bpw for uniform rank-32 on the Qwen pair, or qualify the 0.28 figure with the exact layer dimensions and cite the specific pushed calculation.

---

Clean-area notes, max three:
* First-pair gap-closed and byte budgets for mlp_behemoth_lite vs uniform_rank32 match digest: lite 23.1923% vs uniform 2.0764%, bytes 19,358,176 vs 19,434,496, over_pct 11.8%.
* Second-pair raw score margin and >100% gap-closed warning are consistent with digest: o-down-rebalanced mean -8.072964749082066 vs uniform -8.366280457949834, gap_closed 108.0783% vs 101.4816%.
* Third-pair and fourth-pair byte-fair comparisons, first-token accuracies and subset wins/losses match the pushed heldout96 JSONs.

### Part B reply: NOTICE + why-it-matters

**FINDINGS**

* **CRITICAL – Claim outruns evidence / UNVERIFIABLE – docs/why-it-matters.md – “Against the simplest rival, a plain 1-bit delta (the BitDelta initialization), the honest picture is two budgets, not one: on the Qwen pair a plain 1-bit delta cannot be smaller than about 62 MB, so at our 19 MB size it does not exist, while at its own 62 MB floor it closes more of the gap than our format does at the same price (43.6% against 38.5%). Our format's win is reach: it works at sizes the plain format cannot reach. Full record: `results/bitdelta_baseline.json`.”**
Category: factual / evidence gap. Problem: Evidence digest supplies BitDelta pricing `bitdelta_init_price_bytes=61745828` and `factored_matched_price_bytes=61258816` and mean_target_logprob values `-10.012813627503721` vs `-10.146044864550612`. No gap-closed percentages 43.6% / 38.5% are present in the digest, nor the base/full delta logprobs needed to recompute them. The claim is therefore UNVERIFIABLE from supplied evidence and outruns the digest. Recommended correction: either cite the exact gap-closed numbers from `results/bitdelta_baseline.json` in the digest or rephrase to “gap closed values as reported in results/bitdelta_baseline.json” and ensure the digest contains those recomputed percentages.

* **HIGH – Claim outruns evidence / UNVERIFIABLE – docs/why-it-matters.md – “The known limit… Measured at the first token, the patch moves the model halfway toward starting (base -6.33, patch -1.29, full fine-tune +4.60) but usually does not cross.”**
Category: factual / evidence gap. Problem: The digest contains `results/skill_demo_recipe.json` first_token_margins definition and a margin for the Spark recipe `-4.14`, and `results/skill_demo_forced.json` counts, but no first-token logprob margins `-6.33 / -1.29 / +4.60` for base / uniform rank-32 patch / full fine-tune. The numbers are not supplied and cannot be recomputed from the digest. Recommended correction: remove the numeric margins or add the exact margin values to the evidence digest with source file and recomputation.

* **HIGH – Claim outruns evidence / UNVERIFIABLE – docs/why-it-matters.md – “Full records: `results/skill_demo_forced.json`; the earlier debate is in `results/why_debate.md`, and the five-way validation of this test (script recomputation, Muse Spark, Muse Glimmer, Gemini, and Muse Spark Open via Baseten and via Fireworks) is in the `results/` files with `validation_forced` in their names.”**
Category: judge/submission risk. Problem: Digest provides `results/skill_demo_forced.json` counts, but does not list `results/why_debate.md` nor any `*validation_forced*` files. Existence and content of those files cannot be verified from pushed result JSON. Recommended correction: limit the claim to files present in the digest or add digest entries for `why_debate.md` and the validation_forced files.

* **MEDIUM – Stale / imprecise wording – docs/why-it-matters.md – “One base can then carry many behaviors, one small file each.” / “A patch swaps in or out in a tenth of a second while the base keeps running”**
Category: consistency. Problem: Hot-swap evidence in digest is not provided; `results/hotswap_demo.json` keys are listed but no swap time is in the digest. The “tenth of a second” claim is supported by reference excerpt `docs/demo_script.md` line 69 “patch loaded live in 0.09s”, which is reference material, not primary evidence digest. Recommended correction: cite the hotswap_demo timing from the pushed result JSON in the digest or qualify as “≈0.09 s per demo transcript”.

* **MEDIUM – Rounding presentation – docs/why-it-matters.md – “15.9% of the gap closed there, 23.2% on the Qwen pair.”**
Category: arithmetic. Problem: Recomputed from digest: third pair contender gap closed `0.15852079567397595` = 15.85% → 15.9% OK; Qwen pair lite gap closed `0.2319228264458408` = 23.19% → 23.2% OK. No error, but note rounding is consistent.

* **LOW – NOTICE.md – “All code, documentation, evaluation items, and results in this repository are original work by Vinay K Ganji Krishna, written during the Meta Global AI Developer Hackathon (October 26 to November 4, 2026)…”**
Category: factual. Problem: Date range is in the future relative to typical publication; cannot be verified from digest. No contradiction found, but claim is UNVERIFIABLE from evidence. Recommended correction: keep as attribution statement; no numeric correction needed.

Clean-area bullets:
* Qwen pair headline gap closed 23.192% vs uniform 2.076% and byte-fair lite within uniform budget is supported by `results/alien_sweep_heldout96.json` verdict fields.
* Llama 3.2 1B uniform rank32 gap closed -7.636% vs byte-fair contender +15.852% is supported by `results/third_pair_heldout96.json`.
* Skill demo forced-start counts base 7 clean/1 partial/2 failed and base+patch 8 clean/1 partial/1 failed match `results/skill_demo_forced.json`.

### Part C reply: demo script + BUILD PLAN

**FINDINGS**

* **HIGH – Submission rule / demo opening mismatch**
  * File: `BUILD_PLAN.md` – Scope / Demo video plan (approved by Vinay, Oct 26)
  * Quote: “The 3-minute demo video opens with one line stating what was pre-existing and what was built this week.”
  * File: `docs/demo_script.md` – 0:00-0:25 The product: a fine-tune as a tiny patch file
  * Problem: The pushed demo script opens with a title card / narration about the product – “This is Fraction Compressor. It turns a fine-tuned model into one patch file: about nineteen megabytes instead of about a gigabyte…”. The required pre-existing / built-this-week disclosure is placed at 0:25-0:44 “Honesty: one-bit delta compression is a published idea… Built fresh this week: the factored runtime…”. The opening line required by the submission rules is therefore not the first on-screen / spoken line.
  * Recommended correction: Move the required pre-existing vs built-this-week line to the very first on-screen/narration slot 0:00-0:25 and keep the product intro after it, or update BUILD_PLAN to reflect the approved script ordering.

* **HIGH – Approved timing shape vs script timing**
  * File: `BUILD_PLAN.md` – Demo video plan (approved by Vinay, Oct 26)
  * Quote: “Shape: 0:00 opening + problem; 0:30 the hot-swap moment; 1:30 benchmark numbers, including one Alien Sweep line…; 2:15 Muse Spark judging + quantum audit, one line each”
  * File: `docs/demo_script.md` – 1:21-1:48 The demo moment: swap a file, change the behavior
  * Problem: The hot-swap demo is scripted at 1:21-1:48, not ~0:30 as per the approved shape. Benchmark numbers are scripted at 1:48-2:31, later than the 1:30 target. The plan’s timing anchors are not met by the pushed script.
  * Recommended correction: Re-time the script to place the hot-swap moment around 0:30 and benchmark numbers around 1:30, or formally amend the approved plan to the 1:21/1:48 timings used in the script.

* **MEDIUM – Unverifiable audit claim**
  * File: `docs/demo_script.md` – 2:31-2:44 Checked, not just claimed
  * Quote: “Muse Spark judged every headline claim and had to cite the file behind each one. A quantum computer's random numbers picked the audit sample: all forty-one audit checks passed.”
  * Problem: The evidence digest computed from pushed result JSON at head 3933fae16f5e1673cac38a000533a35fb7b0ecda contains no audit sample size, quantum backend/job/seed record, or “41 of 41 checks passed” record. The claim is therefore UNVERIFIABLE from the supplied pushed evidence.
  * Recommended correction: Either add the audit result file and quantum sampling log to the pushed repo and reference it, or change the script to a verifiable statement supported by the pushed results.

* **MEDIUM – Unverifiable BitDelta baseline gap-closed percentages**
  * File: `docs/demo_script.md` – 1:48-2:31 The numbers
  * Quote: “at sixty-two million bytes a one-bit patch closes more gap… plain BitDelta-style init gap closed 43.6% vs factored rank-108 gap closed 38.5% at 61,258,816 bytes”
  * Problem: The digest provides BitDelta init price 61,745,828 bytes and factored matched price 61,258,816 bytes and mean_target_logprob values for the two configs, but does not provide base/full-delta means for that pair nor the derived gap_closed percentages 43.6% / 38.5%. The percentages are UNVERIFIABLE from the pushed evidence digest.
  * Recommended correction: Cite the exact result file and values used for the 43.6% / 38.5% gap-closed computation, or remove the percentages from the script.

* **LOW – Rounding presentation**
  * File: `docs/demo_script.md` – 1:48-2:31 The numbers
  * Quote: “The patch is fifty-one times smaller: nineteen million bytes against nine hundred eighty-eight million.”
  * Problem: 987,922,432 / 19,434,496 = 50.833447 per independent arithmetic spot calculation. “51x” is a rounded presentation; acceptable but note rounding.
  * Recommended correction: No change required; optionally note “≈51×”.

Clean-area bullets
* The Qwen 0.5B held-out 96 numbers are consistent: lite gap_closed 0.2319228264458408 ≈23.2% vs uniform 0.020763686533300157 ≈2.1%, lite within uniform budget, beats uniform on combined96 and both subsets.
* The Qwen 1.5B fourth-pair numbers are consistent: Down Dominator 38,623,232 bytes inside 39,046,144 byte budget, mean -6.343687772752477 vs uniform -6.478079873557243, raw margin ≈0.134 nats, full delta 3,087,138,816 bytes, ratio ≈79.9×.
* The full-delta / patch byte sizes used in the script match the pushed results: full delta 987,922,432 bytes, uniform rank-32 19,434,496 bytes.

---

## Prompts (verbatim)

### Prompt 0: initial combined prompt (returned no final content; see method note)

```text
You are Muse Glimmer acting as the strictest possible independent auditor of a public hackathon repository. Audit ONLY the pushed repository state supplied below. Do not be diplomatic. Assume a technically sharp hackathon judge will try to catch every error.

Repository: ganjikrishna/fraction-compressor-v0.4
Pushed head supplied for audit: 3933fae16f5e1673cac38a000533a35fb7b0ecda

IMPORTANT SCOPE AND EXCLUSIONS
- The five documents below are the exact pushed versions at that head.
- The evidence digest after them was computed from pushed result JSON files at the same head. Treat it as the spot-check evidence available to you. If a document claim cannot be checked from the supplied evidence, say that explicitly rather than assuming it is true.
- Known local-only material was deliberately EXCLUDED and is not part of the pushed repo state: later literature-citation edits to NOTICE.md, README.md, and docs/why-it-matters.md; docs/intent.md; docs/literature_sweep_2026-10-28.md; results/cloning_question_panel.md; results/video_review_v2.md; the entire video/ directory; and all fifth-pair result/example files. Do not audit those excluded items as if they were pushed.
- BUILD_PLAN.md is a pushed document and is in scope, including internal inconsistencies and stale plan language. No fifth-pair result files are supplied, so do not invent fifth-pair results.

AUDIT FOR ALL OF THE FOLLOWING
1. Factual or arithmetic errors. Recompute ratios, percentages, margins, byte comparisons, word counts, times, and rates from the evidence whenever possible.
2. Stale or superseded numbers still presented as current, including earlier smaller-test results, old wording, or plan sections overtaken by later results in the same documents.
3. Inconsistencies between documents: README.md vs docs/why-it-matters.md vs docs/demo_script.md vs NOTICE.md vs BUILD_PLAN.md.
4. Claims that outrun their evidence, including universal wording based on one test, authorship/originality wording, model/license omissions, runtime or memory claims not actually measured, and submission-rule risks visible in the documents.
5. Anything a hackathon judge would catch that the authors may have missed.

OUTPUT FORMAT, STRICTLY
- Start with: OVERALL VERDICT: YES or NO, followed by one sentence answering whether the pushed repo is clean to submit as-is.
- Then list EVERY finding, most serious first. For each finding give:
  * Severity: CRITICAL, HIGH, MEDIUM, or LOW.
  * Category: arithmetic/factual, stale/superseded, cross-document inconsistency, evidence overreach, or judge/submission risk.
  * Exact location: file and heading or quoted phrase.
  * Problem: what is wrong, with the recomputed value or conflicting passage when applicable.
  * Recommended correction: the exact correction or replacement wording in substance.
- Do not repeat the same root problem as multiple findings unless the correction differs by document.
- End with a short CLEAN AREAS list naming important claims you checked and found supported, so silence is not mistaken for not checking.
- If there are no findings in a category, do not invent any.

The authors have previously accepted strict Glimmer wording limits. Apply the same strictness here. In particular, do not let rounded language hide a wrong ratio, do not treat gap_closed above 1.0 as a recovery fraction, and do not accept a headline based on a subset when the combined or later result says something narrower.


===== BEGIN PUSHED FILE: README.md =====
# Fraction Compressor v0.4

**One base model. Many tiny patch files. Swap a file, swap the behavior.**

What "fraction" means here: not math fractions. A fine-tuned AI model is a base model plus a patch (the weight difference between the two). This tool keeps only a fraction of that patch's information, stored at about 1 bit per weight, in a file small enough to swap in and out live.

![How Fraction Compressor v0.4 works](docs/how-it-works.svg)

## In plain words

A fine-tuned model differs from its base model by a patch (the delta). A normal patch is almost as big as the model itself. Fraction Compressor stores that patch in a factored form whose structure is kept as 1-bit signs, priced byte for byte by the code: 0.28 bits per weight for one large layer at rank 32 (the exact price depends on layer size and rank). v0.4 runs it through a factored runtime: two small multiplies, Y = (X U) V^T, without ever rebuilding the full weight matrix. One layer stored the normal way takes 8.4 MB; our rank-32 file takes 144 KB, and swapping patches is just loading a different small file. Compressing a patch is offline work done once with the full delta; the saving is in storage and at run time.

## Do it yourself

You need two models: a base model and a fine-tuned version of that same base, in safetensors format.

1. Make a patch from the pair (rank 32 everywhere, or pass a per-layer recipe file with `--recipe` instead of `--rank`):
   `python examples/make_patch.py --base <base-model-dir> --finetuned <finetuned-model-dir> --rank 32 --out patch.npz`
   The script subtracts the two models layer by layer, squeezes the difference into the factored format, and writes one patch file. It prints the patch's exact byte price next to the full difference at normal precision.
2. Check the patch any time:
   `python examples/make_patch.py --verify patch.npz --base <base-model-dir> --finetuned <finetuned-model-dir>`
3. Use it: load the patch together with the base model, as in `examples/hotswap_demo.py`, where patches swap in and out of one running base model live.

On the model pair used in this repo's benchmark (Qwen2.5-0.5B base and Instruct), rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller. The full run is saved at `results/make_patch_demo.txt`.

## How this is different

- **From memory files and system prompts** (the text files an AI agent reads, like a personality or memory file): those are words the model reads as instructions, they take up prompt space, and a later instruction can override them. A patch here is numbers applied to the model's own weights. The behavior changes in the math itself, uses no prompt space, and cannot be talked away.
- **From an adapter (like LoRA):** an adapter is a new add-on trained for one task, usually stored at normal precision. This tool takes a fine-tune that already exists and squeezes the difference between it and its base model into a 1-bit factored file, so an existing fine-tune becomes a small patch you can swap.
- **From shrinking a whole model (quantization):** that makes the one model smaller and slightly changes everything it does. This shrinks only the patch, so one base model stays exact and carries many behaviors, one small file each.

Why this matters, what bound it breaks, and where it stops working: [docs/why-it-matters.md](docs/why-it-matters.md).

## Prior art

Compressing a fine-tune's difference is an established research area, and this project builds on published methods, ideas only, no code: BitDelta (1-bit delta compression of fine-tuned models, NeurIPS 2024, arXiv:2402.10193), Delta-CoMe (SVD-based mixed-precision delta compression, NeurIPS 2024, arXiv:2406.08903), and LittleBit (arXiv:2506.13771). All code in this repo is original and was written during the event. What is ours is not the 1-bit format itself: it is the in-loop recipe search and judging by Muse Spark, the forced-multiply runtime, the first-token gate diagnosis with its force-start control, and the verification harness. Full credits: [NOTICE.md](NOTICE.md).

## Benchmark results

The benchmark compares three runs on the same questions: the base model alone, the base model with the full patch, and the base model with our compressed patch. The score is how strongly the model backs the correct answer (a log score; higher is better). "Gap closed" is the share of the base-to-full score gap that a compressed patch recovers. One limit applies everywhere below: the share of questions whose first answer token is exactly right stays low for every compressed version (about 1 to 2% on the first pair, about 8 to 9% on the second, 0 to about 3% on the third; the fourth pair is the exception, where the compressed versions reach 26 to 32% against the full patch's own 33.3%), so these are score results, not proof the model solves the tasks.

### Known limit: skills gated by the first token transfer weakly

Transfer depends on the skill, and one kind of skill is a weak case for this format. We tested a real one: NuExtract-1.5-tiny (MIT), a fine-tune of the same Qwen base that reads a text and a JSON template and answers with the template filled in. The fine-tune itself passes 9 of 10 test prompts (eight fully clean, one with a single reworded value); the plain base passes 0 of 10, because it stops immediately instead of answering. Our rank-32 patch passes only 1 of 10. The reason is narrow: this skill is decided by the first token the model emits, start the JSON or stop, and the compressed patch usually does not flip that one decision. On the one prompt where it does start, the extraction is fully correct. A control test settles why: force that first token and the plain base completes 7 of 10 cleanly, so in this test most of the skill was already in the base and the fine-tune's main work is the decision to start. The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own score: one clean more than the forced base, which at 10 prompts is within sampling noise, so the gate is the main story and any edge beyond the trigger is small at most. Making the patch bigger barely moves this boundary: a rank-64 patch (37,044,736 bytes) and a rank-128 patch (72,265,216 bytes) each pass 2 of 10. Spending the same bytes differently did worse, not better: a Muse Spark recipe that puts most of the rank-32 budget into the embedding and the attention output layer (19,434,400 bytes, the same budget) passes 0 of 10, and measured directly at the first token, its average start-vs-stop margin sits further from opening the gate than the uniform patch's. Broad behavior transfers much better under the same format: the Instruct patch below closes 23.2% of the score gap on 96 fresh questions, with wins you can see in the live hot-swap demo. So the limit is format-gated, not general. Full records: `results/skill_demo.json`, `results/skill_demo_forced.json`, `results/skill_demo_ranks.json`, `results/skill_demo_recipe.json`, and the consultation behind this wording in `results/skill_limit_consultation.md`.

### First pair: Qwen2.5-0.5B base and Instruct

Muse Spark proposed uneven per-layer compression recipes (the Alien Sweep). The search winner, mlp_behemoth, is byte-unfair: at 21,719,776 bytes it spends 11.8% more than the human recipe's budget, so it is named only as the parent. The headline recipe is its byte-fair variant, mlp_behemoth_lite: 19,358,176 bytes, fewer than the human uniform rank-32 recipe's 19,434,496 bytes.

The check that matters is fresh questions the search never saw. That set grew from 24 to 96 questions. On all 96, lite closes 23.2% of the gap, against 2.1% for the human recipe. Lite also wins on each half alone: 9.5% vs 1.6% on the original 24 questions, and 30.4% vs 2.3% on the 72 new ones. An early read from the first small fresh set was that the lead might shrink on fresh questions; on the bigger set the lead grew instead, so that worry did not survive. Lite does not win every kind of question: on knowledge questions the human recipe closes more of the gap (7.8% vs 3.7%); lite's lead comes from the instruction and math questions.

### Second pair: SmolLM2-360M base and Instruct

The same contest ran on a second, different model pair. The search winner there (o-down supercharge) was byte-unfair too, so the byte-fair winner is its byte-matched variant, o-down-rebalanced: 19,683,328 bytes, inside the human recipe's budget of 19,705,856 bytes. On the same 96 fresh questions it beats the human uniform recipe by 0.293 score points on average, and it wins on both halves of the set separately.

One warning that applies to this pair only: every compressed version scores better than the full patch itself, so the gap-closed percentage goes above 100% here. That means the percentage is NOT a share of the fine-tune recovered for this pair. For this pair, the raw score margin (0.293 points) is the honest measure.

### Third pair: Llama 3.2 1B base and Instruct

The same contest also ran on Meta's own open weights, Llama 3.2 1B base and Instruct. The search winner, no_embed_mlp_spread, was byte-unfair again: at 34,690,048 bytes it spends 38.0% more than the human recipe's budget of 25,143,296 bytes, so it is named only as the parent. The headline recipe is its byte-fair variant, no_embed_mlp_spread_balanced: 24,515,584 bytes, inside the budget.

On the same 96 fresh questions, the byte-fair variant scores -12.714 against the human uniform recipe's -14.201: it closes 15.9% of the gap, while the human recipe closes -7.6%, which is below the base model itself (-13.718), so on this pair the plain human recipe makes the score worse than using no patch at all. The byte-fair variant also wins on each half alone: 20.0% vs -1.7% on the original 24 questions, and 14.8% vs -9.1% on the 72 new ones.

Recovery on this pair is weaker than on the other two pairs (15.9% here against 23.2% on the Qwen pair), and first-token accuracy stays low for every compressed version: 2.1% for the byte-fair variant, against 21.9% for the full patch itself. No compressed version outscores the full patch on this pair, so the gap-closed percentage stays a true share of the fine-tune recovered here.

### Fourth pair: Qwen2.5-1.5B base and Instruct (the scale test)

A fresh-eyes review (GPT-OSS, see `results/fresh_perspective.md`) asked whether any of this survives above 1B parameters, so the same contest ran on a fourth pair, Qwen2.5-1.5B base and Instruct. This round the recipes were priced on the real shapes from the start, and all five of Muse Spark's recipes came in under the human recipe's budget of 39,046,144 bytes. The search winner, Down Dominator, is byte-fair itself at 38,623,232 bytes (it drops the MLP gate and up matrices entirely and spends the bytes on the down projection and the attention output), so it is its own byte-fair headline recipe, no variant needed.

On the same 96 fresh questions, Down Dominator scores -6.344 against the human uniform recipe's -6.478: it still wins, but by about 0.13 score points, far narrower than the first pair's win, and the win does not hold on both halves of the set (the human recipe wins the first 24 questions; Down Dominator wins the 72 newer ones). One pattern from the second pair repeats here: every compressed version outscores the full patch itself (full patch -7.810), so the gap-closed percentage goes above 100% (130.7% against 127.9%) and is NOT a share of the fine-tune recovered on this pair; the raw score margin (about 0.13 points) is the honest measure. The recipe's edge is also not an accuracy edge: the human recipe's first-token accuracy on the 96 is 32.3%, against Down Dominator's 26.0% and the full patch's own 33.3%.

So the scale answer is mixed and we state it that way: the format and the recipe contest both still work at 1.5B (a roughly 39 MB patch against a 3,087,138,816-byte full patch, about 79x smaller, scoring at the full patch's level on this metric), but the AI-designed recipe's advantage over the plain human recipe shrinks from decisive at 0.5B to narrow and subset-dependent at 1.5B.

### Baseline: a plain 1-bit delta, priced honestly

A fair question (raised by a fresh-eyes GPT-OSS review) is why not a plain 1-bit delta, the BitDelta idea: sign of each delta weight, one scale per matrix. The catch is price: a plain 1-bit delta cannot go below 1 bit per weight, which on the first pair's 169 matrices is 61,745,828 bytes. At our 19.4 MB budget it does not fit at all; the factored format is the only one of the two that exists there. At the plain format's own floor price, the comparison flips: the BitDelta initialization (sign times the per-matrix mean absolute value, exactly as published, with no scale distillation or any training) closes 43.6% of the gap on the same 96 questions, against 38.5% for our factored format at uniform rank 108 priced just under it (61,258,816 bytes). So the honest summary is a two-budget curve: below about 62 MB on this pair the factored format wins by reach, and at about 62 MB the plain initialization wins on quality. Full record: `results/bitdelta_baseline.json`, judged in `results/spark_judging_baseline.md`.

### How these numbers are checked

Every number above is produced by a script in this repo and can be rerun. Beyond the reruns, Gemini independently recomputed the arithmetic, a Muse Spark judging pass checked each headline claim against the exact result files it cites, and a Muse Glimmer reference check set the wording rules used here (which recipe may be called the leader, and how the second pair's percentage may be described). A subset of the results, picked using true quantum random numbers from IBM Quantum hardware, was re-audited end to end: 41 of 41 checks passed. The records live in `results/`.

## Built during the hackathon

This repository contains only work built during the Meta Global AI Developer Hackathon, October 26 to November 4, 2026 (Indie Developer track, Push the Frontier).

Pre-existing work (not part of this submission): Fraction Compressor v0.1 to v0.3 and the Signet delta-transfer experiments live in the original repository, [github.com/ganjikrishna/fraction-compressor](https://github.com/ganjikrishna/fraction-compressor). The compression and Signet methods were designed and validated there before the event. What is new in this repo is the factored runtime, the end-to-end task benchmark, and the Meta model comparison.

## What is in this repo

- `src/factored.py`: the factored runtime (quantize a delta, price its storage, apply it factored). Tested, see `tests/test_factored.py`.
- `examples/quickstart.py`: a 1-minute smoke run on a dummy delta (needs only numpy): prints the storage cost, bits per weight, and the factored error next to the best any factored form could do at the same rank.
- `fixtures/`: the quantum random fixture for the benchmark's audit sampling (IBM Quantum hardware, backend and job logged in the file).
- `src/bench.py` and `results/`: the end-to-end task benchmark (base vs full delta vs compressed delta) and the Alien Sweep, where Muse Spark proposed compression recipes that were scored, cross-validated (Gemini arithmetic checks, a Muse Spark judging pass, a Muse Glimmer reference check), and confirmed on 96 fresh held-out questions generated by Muse Spark, on four model pairs. See Benchmark results above.
- The live hot-swap demo: one base model loaded once, patch files swapped in live in about a tenth of a second (examples/hotswap_demo.py, transcript in results/).

## Author and credits

Built by **Vinay K Ganji Krishna**, solo participant (Indie Developer track) and author of record.

Implementation, benchmarking, and documentation were carried out with **Ember**, an AI agent powered by Muse Spark, working under the author's direction, the same way this event encourages building with Meta's Muse Code agent. Design pressure-testing also drew on a Gemini design-debate chat. Every result in this repository is produced by scripts in this repository and can be rerun.

## License

MIT, (c) 2026 Vinay K Ganji Krishna. Methods are clean-room implementations from published papers; see [NOTICE.md](NOTICE.md) for citations.

===== END PUSHED FILE: README.md =====

===== BEGIN PUSHED FILE: NOTICE.md =====
# NOTICE: prior art, attribution, and originality

## This project's own work

All code, documentation, evaluation items, and results in this repository
are original work by Vinay K Ganji Krishna, written during the Meta Global
AI Developer Hackathon (October 26 to November 4, 2026) and released under
the MIT License (see LICENSE). No third-party code is included in this
repository, and no code was copied from any of the projects cited below.

## Published methods this work builds on

Compressing the difference between a base model and its fine-tune is an
established research area. The methods below are published prior art. We
read the papers and take the ideas; the implementations here are ours,
written from scratch for this event.

- **BitDelta** (Liu et al., NeurIPS 2024, arXiv:2402.10193): 1-bit
  quantization of the fine-tuning delta, storing the sign of each delta
  weight with one high-precision scale per matrix. Our baseline in
  `examples/bitdelta_baseline.py` implements the paper's initialization
  exactly (sign times the per-matrix mean absolute value, no further
  training), and `results/bitdelta_baseline.json` reports how it scores
  next to our format.
- **Delta-CoMe** (Ping et al., NeurIPS 2024, arXiv:2406.08903):
  training-free delta compression that mixes precisions across singular
  vectors from an SVD of the delta, instead of treating every component
  the same. The lesson that where the bytes go matters more than how
  many there are is one this project builds on.
- **LittleBit** (Lee et al., arXiv:2506.13771): extreme low-bit
  quantization using a factored, dual residual form. Prior work from
  the author's earlier Fraction Compressor versions (v0.1 to v0.3, in
  the original repository) explored this direction; the factored form
  in `src/factored.py` is this event's own implementation.

## What is ours

Naming a published method and reporting its published results for
comparison is standard research practice. The contributions claimed by
this repository are not the 1-bit delta format itself. They are:

- the in-loop recipe search and judging: Muse Spark proposes the
  per-layer rank allocation (the recipe) and later judges the results,
  with every verdict required to cite the exact result file it rests on;
- the forced-multiply runtime in `src/factored.py`, which applies the
  delta as two small multiplies and never rebuilds the full matrix, so
  patches swap in and out of a running base model live;
- the first-token gate diagnosis (skills whose first generated token
  decides success transfer weakly through any small patch) together
  with its force-start control test, which separates "the skill is
  missing" from "the start decision is missing";
- the verification harness: every headline number is recomputed by
  scripts, cross-checked by independent models, and a sample picked
  with true quantum random numbers from IBM Quantum hardware was
  re-audited end to end.

## Models

This repository distributes no model weights and no tokenizer files.
Experiments download models separately from Hugging Face, under each
model's own license: Qwen/Qwen2.5-0.5B and Qwen2.5-0.5B-Instruct
(Apache 2.0), HuggingFaceTB/SmolLM2-360M and SmolLM2-360M-Instruct
(Apache 2.0), meta-llama/Llama-3.2-1B and Llama-3.2-1B-Instruct
(Llama 3.2 Community License).

===== END PUSHED FILE: NOTICE.md =====

===== BEGIN PUSHED FILE: docs/why-it-matters.md =====
# Why it matters

A fine-tuned model is a base model plus a patch: everything training changed, and normally that patch is nearly as big as the model itself. This tool squeezes an existing fine-tune's patch into a file of about 19 MB instead of 1 GB, at 1 bit per weight. One base can then carry many behaviors, one small file each.

## Three uses

- **Many behaviors, one model.** Fifty fine-tunes the normal way means fifty full models; as patches, fifty small files on one base.
- **Live switching.** A patch swaps in or out in a tenth of a second while the base keeps running, changing behavior mid-conversation.
- **Cheap to move.** A 19 MB file can be sent, downloaded on a slow link, or carried on a small device. A 1 GB model often cannot be.

## How it differs from a download or a repo

Downloading a fine-tune gives you the whole model, full size. Small adapters like LoRA exist, but an adapter is a new add-on trained for one task. This tool starts from a fine-tune that exists and converts it, with no retraining: point the script at a base and its fine-tune, and it writes the patch and measures how much behavior the patch carries.

Two honest costs: making a patch needs both full models once, and running one needs the base in memory. The saving is in storing and moving behaviors.

## What bound it breaks, and what it does not

The usual assumption is that at 1 bit per weight, nothing useful survives. Done the plain way, that holds: on Llama 3.2 1B, spreading the budget evenly scored below the base model itself, worse than no patch. Spending the same bytes where they matter kept a real share: 15.9% of the gap closed there, 23.2% on the Qwen pair. So one bound breaks: useful behavior survives smart squeezing.

The other bound stands: a tiny patch is not the full fine-tune. Most of the gap stays behind. Patches are for cheap switching and sharing, not replacements.

Against the simplest rival, a plain 1-bit delta (the BitDelta initialization), the honest picture is two budgets, not one: on the Qwen pair a plain 1-bit delta cannot be smaller than about 62 MB, so at our 19 MB size it does not exist, while at its own 62 MB floor it closes more of the gap than our format does at the same price (43.6% against 38.5%). Our format's win is reach: it works at sizes the plain format cannot reach. Full record: `results/bitdelta_baseline.json`.

## The known limit

One kind of skill transfers weakly: skills decided by the first token, like "start the JSON or stop." On a JSON-extraction fine-tune, the full fine-tune starts on 9 of 10 prompts, the base on 0, the patch on 1. Measured at the first token, the patch moves the model halfway toward starting (base -6.33, patch -1.29, full fine-tune +4.60) but usually does not cross. On the one prompt where it does start, the extraction is fully correct.

The author's intuition: the knowledge is there, it just needs to know to start. The control test has now been run, and it mostly backs him: force the fine-tune's first token and the plain base completes 7 of 10 cleanly (8 of 10 counting a partial), so in this test most of the extraction skill was already in the base, and what the fine-tune mainly installs is the decision to start. The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own unforced score. That is one clean more than the forced base, which at 10 prompts is within sampling noise, so the honest reading is: the gate is the main story, and any edge beyond the trigger is small at most. Full records: `results/skill_demo_forced.json`; the earlier debate is in `results/why_debate.md`, and the five-way validation of this test (script recomputation, Muse Spark, Muse Glimmer, Gemini, and Muse Spark Open via Baseten and via Fireworks) is in the `results/` files with `validation_forced` in their names.

===== END PUSHED FILE: docs/why-it-matters.md =====

===== BEGIN PUSHED FILE: docs/demo_script.md =====
# Demo video script: Fraction Compressor v0.4

Exactly 3 minutes. One idea on screen at a time. Narration is the text under
each NARRATION heading, nothing else is spoken. Total narration: 440 words,
about 147 words per minute.

## 0:00-0:25 The product: a fine-tune as a tiny patch file

ON SCREEN: Title card: FRACTION COMPRESSOR v0.4. Under it, one line: a
fine-tune squeezed into a patch file, about 19 MB instead of about 1 GB.
Then the use cases, one at a time: many fine-tunes on one base, no full
copies stored; send a fine-tune as a small file; switch behavior
instantly; run on small machines.

NARRATION:
This is Fraction Compressor. It turns a fine-tuned model into one patch
file: about nineteen megabytes instead of about a gigabyte. It plugs into
the base model and swaps behavior live, in about a tenth of a second.
One base carries many fine-tunes, no full copies stored. Send a fine-tune
as a small file. Switch behavior instantly. Run on small machines.

## 0:25-0:44 Building on an existing idea: what is old, what is new

ON SCREEN: Two short lists. Published before: 1-bit delta compression,
BitDelta and Delta-CoMe; our earlier compressor work. Built this week:
factored runtime; Muse Spark recipes and claim judging; first-token gate
finding; verification harness. Repo address at the bottom:
github.com/ganjikrishna/fraction-compressor-v0.4.

NARRATION:
Honesty: one-bit delta compression is a published idea, BitDelta and
Delta-CoMe, and our earlier compressor work predates this week. Built
fresh this week: the factored runtime, Muse Spark designing recipes in
the loop and judging claims against the files, the first-token gate
finding, and the verification harness.

## 0:44-1:02 The problem: a fine-tune is almost a second model

ON SCREEN: Two file sizes side by side: the base model, and the full
difference file at 987,922,432 bytes.

NARRATION:
A fine-tune is a base model plus a patch: the difference between them.
That difference alone: nine hundred eighty-eight million bytes, almost
the model itself. It keeps a fraction: about nought point three bits per
weight, all in. Ten fine-tunes, ten near-full models.

## 1:02-1:21 Do it yourself: clone, quickstart, make a patch

ON SCREEN, in real steps, typed in a terminal:
1. `git clone https://github.com/ganjikrishna/fraction-compressor-v0.4`
2. `python3 examples/quickstart.py` and its printed size and error lines.
3. `python3 examples/make_patch.py --base <base-model-dir> --finetuned <finetuned-model-dir> --out patch.npz --rank 32`
   and its printed sizes: patch 19,434,496 bytes, full difference
   987,922,432 bytes.

NARRATION:
You can do this yourself. You need two models: a base and its fine-tune.
Clone the repo. Run the quickstart: it squeezes a sample patch, printing
size and error. Run the patch maker: it subtracts the fine-tune from its
base and writes one file, about nineteen million bytes.

## 1:21-1:48 The demo moment: swap a file, change the behavior

ON SCREEN: `python3 examples/hotswap_demo.py` running. First the base model
answers the strict JSON prompt (the "Return ONLY a JSON object" prompt for
Arrival, 2016, Denis Villeneuve): the right object, then extra rambling
text, then the line `JSON SCORE: parseable=False`. Then the swap line:
patch loaded live in 0.09s. Then the same prompt again: exactly the object,
and `JSON SCORE: parseable=True`. Then the capital of Japan answers:
base loops on a wrong city, patched answers one clean line.

NARRATION:
One base model, loaded once. I ask for strict JSON, a format programs
can read. The base writes the right object, then rambles on, failing the
format check. Watch: the patch swaps in, about a tenth of a second.
Same question again: exactly the object, check passed. Same patch, new
question: the capital of Japan. Base repeats a wrong city; the patch,
one clean line.

## 1:48-2:31 The numbers: smaller file, tested on fresh questions

ON SCREEN: The size table from the demo (full delta 987,922,432 bytes;
patches about 19.4 million bytes, 51x smaller), then the benchmark result
lines: 96 fresh questions, gap closed 23.2% vs 2.1%, and the second model
pair name, SmolLM2-360M. Then the scale test lines: Qwen2.5-1.5B, Spark
recipe 38,623,232 bytes inside the 39,046,144 byte human budget, margin
0.134 nats on 96 fresh questions, patch about 39 MB vs 3,087,138,816 byte
full difference, about 80x smaller. Then the baseline lines: at the plain
1-bit floor price of 61,745,828 bytes, plain BitDelta-style init gap
closed 43.6% vs factored rank-108 gap closed 38.5% at 61,258,816 bytes;
at 19,434,496 bytes no plain 1-bit delta fits, only the factored patch.

NARRATION:
The patch is fifty-one times smaller: nineteen million bytes against
nine hundred eighty-eight million. The measure: how strongly the model
backs the answer. On ninety-six questions, Spark's recipe at the human
budget closes twenty-three point two percent of the gap; the human
recipe, two point one. Winner: mlp_behemoth_lite; its parent overspent
and does not count. Same pattern on SmolLM2; on a model three times
bigger, Spark's recipe won by nought point one three four nats, inside
budget. Honestly: at sixty-two million bytes a one-bit patch closes more
gap. Our win is reach: at nineteen million bytes, where no plain one-bit
patch fits, ours works.

## 2:31-2:44 Checked, not just claimed

ON SCREEN: Two short lines, one at a time: the Muse Spark judging record
citing its result files; then the audit line, 41 of 41 checks passed.

NARRATION:
Then we checked ourselves. Muse Spark judged every headline claim and
had to cite the file behind each one. A quantum computer's random
numbers picked the audit sample: all forty-one audit checks passed.

## 2:44-3:00 Close: a chip, not a note

ON SCREEN: The base model with the small patch file next to it. End card:
repo address.

NARRATION:
This is not a memory file. A memory file is a note the model reads; this
patch is a chip swapped inside the machine, numbers that change the
model's math. Fine-tunes to carry and swap: one base, many behaviors.

---

## Production notes

- Screen recording on the Muse VM of the real runs, in this order:
  repo page, terminal clone and quickstart, make_patch run, then the
  hotswap_demo run. Use the actual output; the transcript of record is
  results/hotswap_demo_transcript.txt.
- Narration recorded after the picture cut, with an AI voice, mixed over
  the recording with ffmpeg. Exactly one audio stream (narration only).
- No burned-in subtitles. Titles and file sizes appear as part of the
  terminal output itself, not as overlays.
- Cut to exactly 3:00. If a block runs long, trim screen pauses, not
  narration words.
- The full caveats (score is not task solving, first-token accuracy stays
  low, the knowledge-bucket result, the second pair's percentage warning)
  live in the README's Benchmark results section; the video states the
  measure honestly in the numbers block and does not claim accuracy gains.

===== END PUSHED FILE: docs/demo_script.md =====

===== BEGIN PUSHED FILE: BUILD_PLAN.md =====
# Build plan, Meta Global AI Developer Hackathon (Oct 26 to Nov 4, 2026)

Submission rules honored here:
- This repo holds only work done during the event. Prior work (v0.1 to v0.3, Signet) stays in github.com/ganjikrishna/fraction-compressor and is cited, not copied.
- The 3-minute demo video opens with one line stating what was pre-existing and what was built this week.
- Deadline: Wed Nov 4, 9:00 PM ET, via the Cerebral Valley submission portal.

## Scope

1. Factored-multiply runtime for 1-bit compressed deltas: Y = (X U) V^T, never materialize W. Memory read per token is the headline metric.
2. End-to-end task-accuracy benchmark on the Signet probe sets (knowledge, instruction, math): base vs base + full delta vs base + sign/factored delta, so the compressed path is scored on task answers, not only weight error.
3. Meta model in the loop: Muse Spark (Meta Model API) runs the same probe sets as a hosted reference, and Muse Spark Open is the planned open-weight candidate if time allows.
4. Stretch, only if 1 to 3 are done: System Instruction Hot-Swap Test (base vs full delta vs sign delta on strict JSON-format prompts, scored by parseability).
5. Alien Sweep: a wide, automated search over compression recipes that a human would not normally pick, filtered in two stages and verified by rerun (full protocol in its own section below). This replaces the planned human rank sweep; it does not add a separate build.
6. Nov 4 reserved for the 3-minute demo video and the submission writeup.
7. AirLLM-style streaming scale test (unparked by Vinay, Oct 28; active): the full Alien Sweep protocol on a fifth pair, Qwen2.5-7B base/Instruct, run on Flash with layer-by-layer streaming in our own NumPy runtime (the AirLLM concept, Apache 2.0; code ours), because a 7B model can never be held whole in Flash's 11 GB RAM. Includes a streamed generation demo: the winning byte-fair patch applied block by block as each block loads, updating a model that is never whole in memory. Vinay's Oct 28 decision: the run's scripts and results are saved locally; whether the 7B results enter the README and submission is decided after he reviews the outcome.

## Demo video plan (approved by Vinay, Oct 26)

- Recorded on Muse's VM: a screen recording of the real demo running (terminal/browser capture). No camera, no laptop needed from Vinay.
- Script first, timed to what is on screen. Voice added after: AI-generated narration mixed over the recording with ffmpeg (the same pipeline as the folk-tale factory, minus generated scenes).
- Exactly 3 minutes. Opens with the required line stating what was pre-existing and what was built this week. Shape: 0:00 opening + problem; 0:30 the hot-swap moment; 1:30 benchmark numbers, including one Alien Sweep line (recipes tried, winner, held out result); 2:15 Muse Spark judging + quantum audit, one line each; 2:45 close.
- Rough cut early (as soon as the hot-swap demo runs) for Vinay to watch and react; final cut Nov 2-3 once the real numbers are in; Nov 4 reserved for submission only. Vinay approves the final cut before anything is posted.
- Simplicity rule (Vinay, Oct 27): keep the video as simple as possible. Plain words, no jargon without a one-line explanation, one idea at a time on screen. A newcomer watching once should understand what the tool does AND be able to pick it up and use it: the video shows the actual quickstart path (clone, run the quickstart, swap a patch file) in real steps, not just results.
- One script line near the close answers the question people will ask (Vinay, Oct 27): how is this different from a memory or personality file and other tools on the market? Plain version: a memory file is words the model reads; our patch is numbers that change the model's math. The README carries the fuller comparison (memory/prompts, adapters, whole-model shrinking).
- Do-it-yourself requirement (Vinay, Oct 27, after Agents 101): the video and the README must explain how the patch works AND how a viewer can do it themselves, as plain steps: take a base model and a fine-tuned version of it, run the compressor on the difference to get a small patch file, then load the patch with the base model to get the fine-tuned behavior. If the repo lacks a single clean script for that path, build one (examples/make_patch.py style) so the steps shown are the steps that actually run.

## Working notes

- Muse Spark reasons before answering and reasoning tokens count against max_tokens; use generous caps in benchmark calls.
- Log every real Muse Spark call the benchmark makes (prompt, token counts, verdict) into results/ as it happens, so the Meta tooling use is evidenced in the repo, not just planned. (Muse Spark's own suggestion in its Oct 26 repo review. Soft budget from Vinay: keep Meta API use under the $100 alert level of the $150 credits where possible.)
- Agents 101 takeaways applied (Oct 27, Vinay: use what is needed): (1) Verification leads the submission and demo story: Meta's own session framed agent output as unverified until defensive checks confirm it, "as important as building the agentic loop", so our rerun + Spark + Gemini cross-checks are presented as a headline feature, not a footnote. (2) Spark judging verdicts cite the exact result files they are based on (grounding advice from the session). (3) In the submission's Meta-products field, describe the benchmark harness honestly in the session's terms: a harness loop (plan, run tools, check results) with Muse Spark inside it.
- Validation rule (Vinay, Oct 26): key results are cross-validated by Muse Spark AND Gemini, on top of the script reruns that produce them. If the two disagree, the disagreement is reported and investigated, never averaged away.
- Model scope (settled Oct 26 night, Vinay: do what is best): Spark family only. Spark 1.3 via the Meta Model API, Spark Open via Baseten, Glimmer as the Flash reference. The other Meta models (Wonder, Image, Voice Transcribe, SAM 3.1) do not fit a compression tool, so they will not be forced in just to name more models. Depth of Spark use is the tooling story.
- Credit order and tracking (Vinay, Oct 26, 10:23 PM): the Baseten credits may not be available after the hackathon, so Baseten carries the heavy lifting first while it lasts: bulk benchmark runs, sweeps, and repeated evaluations on Muse Spark Open. The Meta Model API is used as needed for task generation, judging, and validation. Every Baseten and Meta call is tracked in results/ with provider, model, time, purpose, and token counts, so the usage totals can be shared with the organizers in the submission and checked against the credit balances.
- Models and weights are never committed (see .gitignore); data/ holds local downloads only.
- Glimmer's new wording limit (Oct 27, after the strengthening results): when the compressed versions outscore the full patch itself (as on the SmolLM2 pair), the gap-closed percentage passes 100% and must not be presented as a fraction of the fine-tune recovered. Prose about that pair must state plainly that the percentage is not a recovery fraction there and that the raw score margin is the honest measure. Record: results/glimmer_reference_addendum.md.
- Fresh-question test size (Vinay, Oct 27): the fresh held-out test stays at 96 questions. Expanding it further was considered and declined; 96 is the validated set the headline numbers rest on.
- Skill-transfer limit disclosure (Vinay, Oct 27): the NuExtract gated-skill limit is disclosed upfront, not buried: a "Known limit" note opens the README's Benchmark results section. Vinay's direction was to check with Spark and Glimmer and do what is best; both validators independently recommended (c) disclose upfront AND test larger patches (rank 64/128). The size test ran the same day: 1/10 clean at rank 32, 2/10 at rank 64 and rank 128, so size barely moves this boundary. Records: results/skill_limit_consultation.md, results/skill_demo.json, results/skill_demo_ranks.json.
- Force-start control test (Oct 28, Vinay's go-ahead): settles the question Muse Spark raised in the why-it-matters debate. Forcing the fine-tune's own first token on the same 10 NuExtract prompts takes the plain base from 0/10 to 7 clean + 1 partial, so most of the extraction skill was already in the base and the fine-tune's main work is the decision to start. The rank-32 patch under the same forced start scores 8 clean + 1 partial, matching the full fine-tune's own unforced score: a small real edge beyond the trigger (it cleans the two prompts the forced base still fails, and loses one the forced base cleans), but the gate is the dominant term. Limit wording in README and docs/why-it-matters.md updated to the settled version. Records: results/skill_demo_forced.json, results/skill_demo_forced_transcript.txt, examples/skill_demo_forced.py.
- Scale test, fourth pair (Oct 28, Vinay: use the expiring compute): the full Alien Sweep protocol on Qwen2.5-1.5B base/Instruct (Apache 2.0, non-gated; 197 delta matrices, tied embeddings), answering the fresh-eyes GPT-OSS attack "does any of this survive above 1B?" (results/fresh_perspective.md). One change from Phases 1-3: recipes were generated against the real-shape budget directly (uniform rank 32 = 39,046,144 bytes), so all 5 Spark recipes priced byte-fair from the start and the Stage 2 winner, Down Dominator (38,623,232 bytes; mlp.gate/up dropped to 0, mlp.down 45, attn.o_proj 64), needed no byte-matched variant. Combined-96 result: Down Dominator -6.344 vs uniform -6.478 (raw margin about 0.134 nats; base -12.584, full delta -7.810), but the win is subset-mixed (uniform wins heldout24, Down Dominator wins heldout72_new) and uniform's first-token accuracy is higher (32.3% vs 26.0%). Every factored config outscores the full delta itself on this pair, so gap_closed exceeds 1.0 (1.307 vs 1.279) and is not a recovery fraction here (same pattern and wording rule as pair 2). Honest scale answer: the format and contest still work at 1.5B (about 79x smaller than the 3,087,138,816-byte full delta), but the recipe's edge over uniform narrows from decisive at 0.5B to narrow and subset-dependent at 1.5B. Validation: script recomputation 61/61 gap_closed values, zero mismatches; Muse Spark judging 5/5 SUPPORTED (results/spark_judging_scale.md, corrected pass: the first pass carried two hand-copied Stage 2 values off by ~4e-4, re-run with file-pulled values, no verdict changed); Gemini all recomputations MATCH, claims 1-6 CONFIRMED, README sentence FAIR (results/gemini_validation_scale.md). Records: results/fourth_pair_check1.json, results/fourth_pair_stage2.json, results/fourth_pair_heldout96.json; scripts examples/fourth_pair_precompute.py, examples/fourth_pair_stage2.py, examples/fourth_pair_heldout96.py; Flash workdir ~/fc-v04-sweep4. Compute: precompute 66.9 s; build peak RSS 7,042.6 MB; eval peaks up to 7,964.4 MB on Flash's 11 GB.
- Force-start validation (Oct 28, Vinay: "put others to use too"): five independent checks of the forced-start claims. Script recomputation recounted every count from the per-prompt records, verified all 10 forced-token prefixes, and matched the margins (base -6.332, patch -1.2942, full +4.6005); no mismatches. Muse Spark 1.3, Muse Spark Open via Baseten, and Muse Spark Open via Fireworks each recounted and ruled claims 1 to 3 SUPPORTED; Glimmer ruled the interpretation FAIR with the small-sample caveat; Gemini ruled all four claims supported and the interpretation fair. All five agree the missing-control objection is settled for this test. One wording correction survived: Spark 1.3 and both Spark Open routes ruled "a small real edge" too strong, because the forced patch's lead over the forced base is one clean prompt out of 10, inside sampling noise; README and why-it-matters.md now read "one clean more than the forced base, which at 10 prompts is within sampling noise, so the gate is the main story and any edge beyond the trigger is small at most," with the "most of the skill" sentence scoped to this test. Records: results/glimmer_validation_forced.md, results/spark_validation_forced.json/.md, results/gemini_validation_forced.md, results/sparkopen_validation_forced.md, results/sparkopen_fireworks_validation_forced.md.
- Prior-art credit and the missing baseline (Oct 28): NOTICE.md now credits the published methods this work builds on conceptually (BitDelta, Delta-CoMe, LittleBit; methods only, no code used), and the README carries a short Prior art section plus a baseline paragraph in Benchmark results. The baseline answers the GPT-OSS judge question (why not a plain 1-bit delta?): on the Qwen pair a plain 1-bit delta's floor is 61,745,828 bytes, so at 19.4 MB it cannot exist, while the factored format closes 23.2% there (lite). At the floor price the BitDelta initialization (published init only, no distillation or training) closes 43.6% on the combined 96, against 38.5% for factored uniform rank 108 at 61,258,816 bytes: at that budget the plain init wins. Honest conclusion, judged SUPPORTED 6 of 6 by Muse Spark with the headline sentence returned unchanged: the factored format's win is reach, not quality per byte at the plain format's floor. Records: results/bitdelta_baseline.json, results/spark_judging_baseline.md, examples/bitdelta_baseline.py.
- AirLLM streaming scale test, fifth pair (Oct 28, Vinay unparked it and clarified "we can use anything from AirLLM for ourselves, I mean the concept"): Qwen2.5-7B base/Instruct (Apache 2.0, non-gated; 28 blocks, hidden 3584, 28 Q heads / 4 KV heads, embeddings NOT tied, so embed and lm_head are separate delta matrices; 198 delta matrices; full delta 15.2 GB bf16) on Flash (11 GB RAM), streamed AirLLM-style in our own NumPy stack: per-matrix streamed RSVD precompute, Gram-matrix exact SVD factor build, block-by-block eval forward carrying all probe items' hidden states, per-item lm_head logits at answer positions only (never a materialized full logits tensor). Concept credited to lyogavin/airllm (Apache 2.0) in NOTICE.md; all code is ours. Gemini design consult first (results/airllm_design_consult.md): adopted in-place delta formation with explicit gc discipline, answer-position-only logits, and full timing disclosure in the stream demo (time to first token, per-token latency, storage medium, peak RAM); rebutted its 14-16 GB RSVD peak (thin projections keep it near the 2.2 GB delta plus ~0.4 GB of factors) and its demand to drop the Gram SVD (the quantize cross-check against dense-SVD construction is the guard, and its diffs are reported). Protocol mirrors pair 4 for comparability (validation, Stage 2 on 24, byte-fair winner on the combined 96, BitDelta-style baseline at its real price), plus the streamed generation demo Vinay asked for: base streamed plain vs base streamed with the winning patch, greedy, few prompts, per-token time stated honestly. Vinay's decision (Oct 28): results stay local-only until he reviews the report; no README section and no why-it-matters claims unless he approves after seeing the outcome.
- Llama Phase 3 (Oct 27): the third pair (Meta's own Llama 3.2 1B base and Instruct, unblocked when the Hugging Face license approval landed) ran the full contest. The byte-fair variant no_embed_mlp_spread_balanced (24,515,584 B) beats uniform_rank32 on the combined 96 fresh questions, gap closed 15.9% vs -7.6% (uniform scores below the base model itself), and wins both halves; the Stage 2 winner no_embed_mlp_spread is byte-unfair at +38.0% over the 25,143,296 B budget and is named only as such. Recovery on this pair is weaker than on the other two pairs, and no factored config outscored the full delta, so gap_closed stays a recovery fraction here. Validation (Oct 27): script recomputation matched 60 of 60 gap_closed values exactly; Gemini recomputed every headline value, confirmed claims 1 to 5, and ruled the summary sentence fair; the Muse Spark judging addendum supported claims A to D and marked E not supported on scope only (the pair-1 comparison was outside the numbers it was shown; the in-pair facts were confirmed, and the 23.2% figure rests on the pair-1 records and the earlier addendum's supported claim A). Records: results/third_pair_stage2.json, results/third_pair_heldout96.json, results/gemini_validation_llama.md, results/spark_judging_llama.md.

- Agents 102 handbook check (Oct 28, Vinay: use what is needed, follow any strict guidelines there): Meta's workshop repo (github.com/meta-models/legal-agent-workshop, the Agents 101/102 sessions) was read in full: HANDBOOK.md, VERIFICATION.md, ESCALATION_RULES.md, and the verification code. Judgment: it is a teaching pattern for a legal agent, not event rules, so none of it binds this submission. It is still Meta's own published standard for verifiable agents, so our harness was checked against it. Already matching: (1) two layers of checking, plain code first (script recomputation of every value, the quantum audit), then a model judging pass (one Muse Spark call per result set, like their claims check, which also runs only after the code rules pass); (2) no claim is published without a citation: their findings cite a document, page, and exact quote, and the case record refuses a quote that is not on the page; our judging verdicts cite the result file and the exact values relied on; (3) refusals come back as a problem list and the text is fixed, never silently rewritten (our headline ruling and the force-start wording correction both worked this way); (4) human sign-off at the end: their passing memo waits as awaiting_signoff until the attorney approves, ours waits for Vinay's approval before the submission and final video ship. Adopted now, as working rules: (a) judging values are pulled from the result files by script, never hand-copied (the scale test's first judging pass carried two hand-copied values off by about 4e-4; the corrected pass pulled them from the files, and that is now the standing rule, the same reason their kit checks quotes at write time); (b) each published claim carries at most 3 cited result files, the strongest ones (their cap is 3 citations per finding); (c) judging verdicts gain a third state, escalated, for claims the evidence shown cannot settle (scope limits, validators disagreeing); an escalated claim goes to Vinay instead of being reworded by the agent, and a claim refused by validators twice escalates rather than being reworded a third time (their version: a memo refused 3 times goes to a person); (d) held-out hygiene: the submission reports held-out results as aggregate numbers only and never describes the held-out items themselves (their feedback rule: point to what is missing, never quote or count the ground truth). Deliberately NOT adopted: their claims check fails open (an unreadable Spark judgment passes the memo); ours fails closed, a judging pass with missing evidence is rerun, as the scale test did. Format mapping, no code change: their finding is {item, status: proven / not_proven / escalated, one-sentence summary, citations [{document, page, quote}], max 3}; ours is {claim_id, claim, verdict: SUPPORTED / NOT SUPPORTED, cited_file, values_relied_on, note}. The shapes already match; the only deltas are the new escalated status and the 3-citation cap, which future judging passes follow. Their ground-truth checklist check (score kept from the agent, shown to the reviewer) maps to our held-out guard plus the judging claim list: the search never sees the fresh items, and the validators' records keep their own words.

## Expanded scope (Vinay, Oct 26: push the limits, not just another version)

1. Live hot-swap demo as the centerpiece: one base model, tiny 1-bit delta files swapped in live, behavior changes on the spot, file sizes shown side by side. This is the moment the demo video is built around.
2. Muse Spark inside the product loop: Spark (Meta Model API) generates fresh probe tasks, runs the compressed vs full comparison, and writes the verdicts. The benchmark is agentic, not a static script output.
3. Meta open weights in the comparison: Muse Spark Open (hosted via Baseten) joins the benchmark table, which also puts the project in contention for the Best Build on Meta Open Weight Models bonus.
4. Reproducibility as a feature: every number in the README and demo is produced by a script in this repo that anyone can rerun.
5. Submission craft: review the submission form in the first days, script the 3-minute demo from the start, post the demo on X at submission for the Most Viral bonus, and open the video with the required line separating pre-existing work from this week's build.
6. Alien Sweep as the search story: Spark proposes recipes, the sweep tests them, and the demo reports how many recipes were tried and what the winner was. If the human recipe wins, that is the reported result, with the full search map published either way.

## Alien Sweep (approved by Vinay, Oct 26)

Vinay's condition (Oct 26): use it only if it makes sense once the build starts. If the recipe space outruns what the runtime can run and verify by Nov 4, fall back to the human rank sweep and report that plainly in the results.

What it is, in plain words: instead of a person choosing a few sensible compression settings and testing those, an agent proposes many settings, including odd ones a person would skip, a script tests all of them, and only the ones that pass a fresh rerun count. The name comes from the October 2026 OpenAI math release, where mathematicians called the AI proofs alien math because the winning moves came from directions humans had not tried.

How it runs:
- Recipe generation: Muse Spark proposes recipes as per-layer rank maps under a fixed total size budget (uneven budgets across layers included). Recipes are strict JSON, layer name to integer rank only; anything needing a new code path (ternary deltas, variable bit width) is out of bounds for the sweep. Every proposed recipe is logged with its reason, so the search count in the demo is a real count from a file, not a claim.
- Stage 1, cheap filter: the fast matrix level benchmark scores every recipe on reconstruction error at exact accounted size. Only the top 5 recipes advance.
- Stage 2, hard check: the top 5 run the end to end task benchmark (knowledge, instruction, math probes) on Flash. A recipe only counts if the benchmark script reruns it and it passes on task score, not only weight error.
- Held out guard: Spark generates fresh probe tasks the search never saw. The winner must also pass those, so the sweep cannot win by memorizing the old 24 probe items.
- Honest outcome rule: if no alien recipe beats the human rank 32 recipe, the result is reported that way and the search map is still published. No winner is named in the demo script until Stage 2 and the held out check are both done.
- Headline ruling (Oct 27, three-way validation; Vinay sided with Glimmer over Gemini and Spark): the headline recipe in our own prose (README, demo, submission) is mlp_behemoth_lite, the byte-fair leader: it beat the human uniform recipe on the fresh held-out tasks while using fewer bytes (gap closed 9.5% vs 1.6%). mlp_behemoth itself is named only as the byte-unfair parent (11.8% more bytes than uniform) whenever it appears. The validators' own records in results/ keep their original words; this ruling governs our wording, not their records.
- Strengthening tests (approved by Vinay Oct 27, running): (1) the fresh-question held-out test expands from 24 to 96 items (72 new Spark-generated, novelty-checked), lite vs uniform rerun on the Qwen pair; (2) the full contest repeated on a second pair, SmolLM2-360M base/Instruct; (3) the same contest on Meta's own open weights, Llama 3.2 1B base/Instruct, queued after (2) and subject to the HF license gate.

Where it fits the schedule: the rank sweep was already an early experiment in this plan. The Alien Sweep widens that same slot. Stage 1 is cheap CPU work on the VM; Stage 2 is only 5 recipes on Flash. Nov 4 stays reserved.

### Gemini debate on Alien Sweep (Oct 26, via the Gemini API)

- Verdict: GO, but only inside a strict boundary. A recipe is a per-layer rank distribution under a fixed total size budget, which needs zero new runtime code (the same SVD and packing path, different rank integers per layer). The moment a recipe needs a new code path, it is out.
- Technique adopted: precompute the SVD once per matrix up to the max rank, then Stage 1 scores each recipe by slicing the precomputed factors. Hundreds of recipes then cost seconds, not one SVD per recipe.
- Failure modes Gemini raised, all accepted: low matrix error does not guarantee task success (that is why Stage 2 exists); Spark can emit invalid layer names or out-of-range ranks (strict JSON schema check before anything runs); Stage 2 CPU time per config is the real budget risk; the winner may be the boring uniform recipe (covered by the honest outcome rule).
- Day 2 go/no-go checks. Any failure means fall back to the human rank sweep and report it: (1) Spark produces 5 schema-valid recipe JSONs quickly, layer-to-rank maps only; (2) the one-time SVD precompute for the target model finishes in under 10 minutes; (3) Stage 1 scores the full recipe set in minutes via slicing; (4) one Stage 2 config completes the task benchmark inside the agreed time budget without memory thrash on Flash.

## Resources we will use

- AI compute (Vinay, Oct 26): use all of it. Meta Model API credits fund Muse Spark as task generator, judge, AND independent validator of results; Gemini covers design debate and repo review; Flash local models run the heavy benchmarks. The free credits exist to be spent on this build. Order of use (Vinay, Oct 26 night): Baseten first for the heavy lifting, because its credits may end with the hackathon; the Meta Model API fills in as needed. Real-money charges beyond the credits still need Vinay's tap.

- Flash (Vinay's Ubuntu box): local small models for the factored-runtime experiments, plus Muse Glimmer 30B through NVIDIA NIM, which is already working there. Quality-critical orchestration stays on the Muse VM, which holds the Meta Model API connection.
- Other AIs for design pressure-testing: the standing Gemini design-debate chat (Vinay's permission), used the same way as during prep, with anything adopted logged in NOTES.
- Quantum component (honest and bounded): the benchmark's verification pass audits a subset of results, and that subset is chosen with true quantum random numbers generated on IBM Quantum hardware (free plan, ibm_fez). The backend, job, and seed are logged with the results. It is an audit-sampling method, not a speed claim.
- Feedback for Meta: the submission includes a short section on what we learned about the Muse models themselves (for example, Muse Spark spends output budget on reasoning before answering), since the organizers say they want to learn where the tools need to improve.

## Crediting

Vinay K Ganji Krishna is the sole participant and author of record. The README credits Ember (Muse Spark) as the AI agent used for implementation, benchmarking, and documentation, the same way the event itself promotes building with the Muse Code agent. Ember is not listed as a team member.

## Design input from the Gemini debate chat (Oct 26)

- Rank tuning beats bit-unpacking kernels. Kernels are a rabbit hole for a 10-day solo build; plain numpy unpacking is enough. Rank calibration is existential: too low and the delta is powerless, too high and the file-size story dies. A rank sweep is an early experiment.
- Quarantine the quantum dependency: pull one large batch of quantum random numbers from IBM hardware at the start, log backend and seed, freeze it as a static fixture. No live quantum calls during crunch or demo.
- The demo contrast must be stark: same prompt, base model fails it, the tiny delta file (size on screen) swaps in, same prompt now succeeds. The strict-JSON instruction prompt is the natural centerpiece.
- Probe sets: sharp archetypes carry the demo; the full Signet sets still carry the benchmark table, because reproducible numbers are the credibility.

===== END PUSHED FILE: BUILD_PLAN.md =====

===== BEGIN EVIDENCE DIGEST FROM PUSHED RESULT FILES =====
# Evidence digest computed from the pushed result JSON files at commit 3933fae

## results/alien_sweep_heldout96.json
- base: mean_target_logprob=-11.1497780625, accuracy=0.031250
- full_delta: mean_target_logprob=-8.5424662354, accuracy=0.166667
- full_delta_fp16_bytes=987922432
- ranking: mlp_behemoth: mean=-10.45627380592698, gap_closed=0.2659843941106181 (26.5984%), accuracy=0.020833333333333332, bytes=21719776
- ranking: mlp_behemoth_lite: mean=-10.54508293414888, gap_closed=0.2319228264458408 (23.1923%), accuracy=0.010416666666666666, bytes=19358176
- ranking: uniform_rank32: mean=-11.095640657042859, gap_closed=0.020763686533300157 (2.0764%), accuracy=0.010416666666666666, bytes=19434496
- verdict.byte_fair_headline_question=does mlp_behemoth_lite still beat uniform_rank32 on the combined 96 fresh items?
- verdict.lite_beats_uniform_on_combined96=True
- verdict.lite_gap_closed_combined96=0.2319228264458408
- verdict.uniform_gap_closed_combined96=0.020763686533300157
- verdict.lite_within_uniform_budget=True
- verdict.subset_consistency.heldout24.lite_gap_closed=0.0947229129097021
- verdict.subset_consistency.heldout24.uniform_gap_closed=0.01564243038524459
- verdict.subset_consistency.heldout24.lite_beats_uniform=True
- verdict.subset_consistency.heldout72_new.lite_gap_closed=0.303801464368062
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=0.023446697818697487
- verdict.subset_consistency.heldout72_new.lite_beats_uniform=True
- verdict.mlp_behemoth_reference_only.note=mlp_behemoth is BYTE-UNFAIR (over the uniform budget) and is reported as a reference only, never as the headline.
- verdict.mlp_behemoth_reference_only.real_shape_bytes=21719776
- verdict.mlp_behemoth_reference_only.uniform_real_shape_bytes=19434496
- verdict.mlp_behemoth_reference_only.over_bytes=2285280
- verdict.mlp_behemoth_reference_only.over_pct=11.8
- verdict.mlp_behemoth_reference_only.combined96_gap_closed=0.2659843941106181
- verdict.mlp_behemoth_reference_only.combined96_factored_mean_target_logprob=-10.45627380592698

## results/second_pair_heldout96.json
- base: mean_target_logprob=-12.8785653857, accuracy=0.010417
- full_delta: mean_target_logprob=-8.4321585239, accuracy=0.093750
- full_delta_fp16_bytes=723517440
- ranking: o-down supercharge: mean=-8.03994579872309, gap_closed=1.0882089150651426 (108.8209%), accuracy=0.09375, bytes=27660288
- ranking: o-down-rebalanced: mean=-8.072964749082066, gap_closed=1.080782930132702 (108.0783%), accuracy=0.08333333333333333, bytes=19683328
- ranking: uniform_rank32: mean=-8.366280457949834, gap_closed=1.0148160229227625 (101.4816%), accuracy=0.08333333333333333, bytes=19705856
- verdict.stage2_winner=o-down supercharge
- verdict.byte_fair_contender=o-down-rebalanced
- verdict.byte_fair_headline_question=does o-down-rebalanced beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=1.080782930132702
- verdict.uniform_gap_closed_combined96=1.0148160229227625
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=27660288
- verdict.winner_byte_status.uniform_real_shape_bytes=19705856
- verdict.winner_byte_status.winner_byte_unfair=True
- verdict.winner_byte_status.winner_combined96_gap_closed=1.0882089150651426
- verdict.subset_consistency.heldout24.contender_gap_closed=1.037137028575536
- verdict.subset_consistency.heldout24.uniform_gap_closed=0.9703361598361151
- verdict.subset_consistency.heldout24.contender_beats_uniform=True
- verdict.subset_consistency.heldout72_new.contender_gap_closed=1.0979379349340161
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=1.0322988159821247
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## results/third_pair_heldout96.json
- base: mean_target_logprob=-13.7178328094, accuracy=0.010417
- full_delta: mean_target_logprob=-7.3867130269, accuracy=0.218750
- full_delta_fp16_bytes=2471493632
- ranking: no_embed_mlp_spread: mean=-12.12275284734357, gap_closed=0.25194278687724053 (25.1943%), accuracy=0.03125, bytes=34690048
- ranking: no_embed_mlp_spread_balanced: mean=-12.714218663974016, gap_closed=0.15852079567397595 (15.8521%), accuracy=0.020833333333333332, bytes=24515584
- ranking: uniform_rank32: mean=-14.20128408199294, gap_closed=-0.07636110027783072 (-7.6361%), accuracy=0.0, bytes=25143296
- verdict.stage2_winner=no_embed_mlp_spread
- verdict.byte_fair_contender=no_embed_mlp_spread_balanced
- verdict.byte_fair_headline_question=does no_embed_mlp_spread_balanced beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=0.15852079567397595
- verdict.uniform_gap_closed_combined96=-0.07636110027783072
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=34690048
- verdict.winner_byte_status.uniform_real_shape_bytes=25143296
- verdict.winner_byte_status.winner_byte_unfair=True
- verdict.winner_byte_status.winner_combined96_gap_closed=0.25194278687724053
- verdict.subset_consistency.heldout24.contender_gap_closed=0.200373434383912
- verdict.subset_consistency.heldout24.uniform_gap_closed=-0.016714667787171608
- verdict.subset_consistency.heldout24.contender_beats_uniform=True
- verdict.subset_consistency.heldout72_new.contender_gap_closed=0.14817956351361586
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=-0.09109894297869517
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## results/fourth_pair_heldout96.json
- base: mean_target_logprob=-12.5841302690, accuracy=0.010417
- full_delta: mean_target_logprob=-7.8097449276, accuracy=0.333333
- full_delta_fp16_bytes=3087138816
- ranking: Down Dominator: mean=-6.343687772752477, gap_closed=1.3070672034171866 (130.7067%), accuracy=0.2604166666666667, bytes=38623232
- ranking: uniform_rank32: mean=-6.478079873557243, gap_closed=1.2789186374354595 (127.8919%), accuracy=0.3229166666666667, bytes=39046144
- verdict.stage2_winner=Down Dominator
- verdict.byte_fair_contender=Down Dominator
- verdict.byte_fair_headline_question=does Down Dominator beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=1.3070672034171866
- verdict.uniform_gap_closed_combined96=1.2789186374354595
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=38623232
- verdict.winner_byte_status.uniform_real_shape_bytes=39046144
- verdict.winner_byte_status.winner_byte_unfair=False
- verdict.winner_byte_status.winner_combined96_gap_closed=1.3070672034171866
- verdict.subset_consistency.heldout24.contender_gap_closed=1.1242514732201125
- verdict.subset_consistency.heldout24.uniform_gap_closed=1.152286379770239
- verdict.subset_consistency.heldout24.contender_beats_uniform=False
- verdict.subset_consistency.heldout72_new.contender_gap_closed=1.3791549665115759
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=1.3288521753254294
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## Independent arithmetic spot calculations
- Qwen pair full/uniform ratio = 50.833447; full/lite ratio = 51.033859.
- Qwen 1.5B full/Down Dominator ratio = 79.929583; full/uniform ratio = 79.063859.
- One-layer ratio using 8,388,608 bytes / 147,456 bytes = 56.888889.
- Qwen pair all-in effective bits/weight for uniform price = 0.314753 bpw; for lite = 0.313517 bpw.
- BitDelta pricing: {'n_matrices': 169, 'n_weights_169_matrices': 493961216, 'bitdelta_init_price_bytes': 61745828, 'bitdelta_price_formula': 'ceil(total_weights / 8) + 4 bytes x n_matrices (one fp32 scale per matrix)', 'factored_matched_rank': 108, 'factored_matched_price_bytes': 61258816, 'factored_rank_plus_one_price_bytes': 61809136, 'factored_under_by_bytes': 487012}; configs: {'bitdelta_init': {'kind': 'published_baseline_initialization', 'definition': "BitDelta initialization (Liu et al., arXiv:2402.10193): per matrix, delta_hat = sign(delta) * mean(|delta|); one fp32 scale per matrix; NO scale distillation and NO training. The full BitDelta method distills the scales on data afterwards; that step is deliberately not run, and this config must be cited as the initialization, not as BitDelta's final reported quality.", 'mean_target_logprob': -10.012813627503721, 'accuracy_first_token': 0.0625, 'price_bytes': 61745828, 'wall_s': 285.21, 'peak_rss_mb': 3578.4}, 'factored_uniform_rank108': {'kind': 'ours_factored_matched_budget', 'definition': 'factored.quantize_delta at uniform rank 108 on all 169 matrices: the largest uniform rank whose factored.storage_bytes total fits under the plain 1-bit price.', 'mean_target_logprob': -10.146044864550612, 'accuracy_first_token': 0.03125, 'price_bytes': 61258816, 'wall_s': 287.5, 'peak_rss_mb': 3279.4}}.

## results/skill_demo.json
- patch={'built_by': 'examples/make_patch.py', 'rank_mode': 'uniform rank 32', 'storage_bytes': 19434496, 'file_bytes_on_disk': 19801674, 'full_delta_fp16_bytes': 987922432}
- base (no patch): counts={'clean': 0, 'partial': 0, 'failed': 10}
- base + compressed patch (uniform rank 32): counts={'clean': 1, 'partial': 0, 'failed': 9}
- base + full delta (fine-tune weights): counts={'clean': 8, 'partial': 1, 'failed': 1}

## results/skill_demo_forced.json
- unforced_reference={'base (no patch)': {'clean': 0, 'partial': 0, 'failed': 10}, 'base + compressed patch (uniform rank 32)': {'clean': 1, 'partial': 0, 'failed': 9}, 'base + full delta (fine-tune weights)': {'clean': 8, 'partial': 1, 'failed': 1}}
- base, forced start: counts={'clean': 7, 'partial': 1, 'failed': 2}
- base + compressed patch (uniform rank 32), forced start: counts={'clean': 8, 'partial': 1, 'failed': 1}

## results/skill_demo_ranks.json
- test=skill-transfer size test: does a larger uniform patch move the first-token gate?
- skill_pair=Qwen/Qwen2.5-0.5B base + numind/NuExtract-1.5-tiny (MIT) JSON extraction
- prompts=the same 10 screening prompts and the same judge as results/skill_demo.json (clean = parses as JSON, keys match template, every expected value present)
- decoding=greedy, max 64 new tokens, raw NuExtract prompt format
- reference_counts: {'note': 'both reruns (rank 64 and rank 128 runs) reproduced these two configs exactly: base 0/0/10, full delta 8 clean / 1 partial / 1 failed'}
- conclusion=Clean transfers: rank 32 = 1/10 at 19,434,496 B; rank 64 = 2/10 at 37,044,736 B; rank 128 = 2/10 at 72,265,216 B. Quadrupling the patch buys one extra prompt and then nothing: at these sizes the first-token gate barely moves with uniform size.
- verify=rank 64 and rank 128 patches both passed make_patch --verify (worst factored-vs-dense diff 4.3e-16 / 3.1e-16; file-vs-fresh rel diff 5.0e-04 / 3.3e-04, the designed fp16 V rounding). Build peaks: 4,754 MB both; verify peaks 4,917 / 5,067 MB.

## results/skill_demo_recipe.json
- test=allocation test: same bytes (19,434,496 B budget), smarter placement vs uniform rank 32
- skill_pair=Qwen/Qwen2.5-0.5B base + numind/NuExtract-1.5-tiny (MIT) JSON extraction
- recipe_generation: {'provider': 'baseten', 'model': 'meta-models/muse-spark-open-1026', 'max_tokens': 16000, 'budget_bytes': 19434496, 'prompt': 'You are proposing compression recipes for a factored 1-bit weight-delta format. A recipe assigns one integer rank to each layer TYPE; that rank is used for that layer type in all 24 transformer blocks (the embedding is a single matrix). The stored size of one matrix at rank r is priced exactly as:\n\n  bytes(matrix, r) = ceil(rows * r / 8) + 4 * rows + 2 * cols * r\n\nLayers (rows x cols of the delta matrix):\n  embed: delta matrix 151936 x 896, rank may be 0..896\n  attn.q_proj: delta matrix 896 x 896, rank may be 0..896\n  attn.k_proj: delta matrix 128 x 896, rank may be 0..128\n  attn.v_proj: delta matrix 128 x 896, rank may be 0..128\n  attn.o_proj: delta matrix 896 x 896, rank may be 0..896\n  mlp.gate: delta matrix 4864 x 896, rank may be 0..896\n  mlp.up: delta matrix 4864 x 896, rank may be 0..896\n  mlp.down: delta matrix 896 x 4864, rank may be 0..896\n\nThe total size of a recipe is bytes(embed) + 24 * (sum of bytes over the other 7 layer types), and it must be <= 19434496 bytes. That is exactly the cost of the uniform rank-32 recipe on this model; you have the same bytes, spend them differently.\n\nThe model pair is Qwen2.5-0.5B base and NuExtract-1.5-tiny, a fine-tune for structured JSON extraction (read a text and a JSON template, answer with the filled template). The finding you are designing against: this skill is gated by the FIRST generated token. The fine-tune starts the JSON; the plain base emits end-of-text immediately and answers nothing (0 of 10 test prompts). Our uniform rank-32 patch flips that gate on only 1 of 10 prompts (on the 9 others the patched model still stops immediately), even though the one extraction it does start is fully correct. Bigger uniform patches barely help (rank 64 and rank 128 each flip 2 of 10). So placement, not size, is the open question. Weigh protecting the embedding (it feeds every token position and, with tied weights, the output head) and the output-side layers (attn.o_proj, mlp.down) that shape the final logits, if you judge that is where the start-vs-stop decision lives.\n\nPropose exactly 5 recipes, ordered best-first: put the recipe you recommend most first. Make them genuinely different from each other and from uniform: uneven allocations are the point. Every recipe must include every layer name exactly once in its "ranks" object, with an integer rank (0 is allowed and means that layer type\'s delta is dropped).\n\nReply with ONLY a JSON object, no markdown fences, no commentary, in exactly this shape:\n{"recipes": [{"name": "<short name>", "reason": "<one sentence>", "ranks": {"embed": 0, "attn.q_proj": 0, "attn.k_proj": 0, "attn.v_proj": 0, "attn.o_proj": 0, "mlp.gate": 0, "mlp.up": 0, "mlp.down": 0}}]}\nReplace the zeros with your ranks. Check your arithmetic: each recipe\'s total (embed once + 24 blocks) must be <= 19434496 bytes.'}
- chosen_recipe: {'name': 'Gatekeeper Embed+O', 'reason': 'Maximizes the tied embed and cheap-to-expensive output ratio by pushing embed to 382 and o_proj to 64 with minimal down to flip the first-token EOS vs JSON gate.'}
- chosen_recipe_price_bytes=19434400
- patch_file_bytes_on_disk=18796330
- verify: {'result': 'PASS'}
- demo_run: {'config_label': 'base + compressed patch (recipe Gatekeeper Embed+O)'}
- first_token_margins: {'measure': 'first-token logprob margin', 'definition': "margin = logprob(fine-tune's actual first generated token) - logprob(end-of-text 151643) at the first generation position, natural log; positive means the gate is open (starting the JSON beats stopping)", 'peak_rss_mb': 2354.3}
- conclusion=Placement did not beat size at equal bytes; it did worse. The Spark recipe's radical reallocation (embed 382, mlp.gate/up dropped to 0) opened 0 of 10 gates and its mean first-token margin (-4.14) is far below uniform rank 32 (-1.29). The gate-open counts measured from margins (base 0, rank32 1, recipe 0, full delta 10) exactly match the generation outcomes. Neither bigger uniform patches (2/10 at rank 128) nor this reallocation opens the gate at these budgets; uniform rank 32 is closest per byte.

## results/alien_sweep_heldout.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'byte_matched_variant', 'method', 'shared_configs', 'configs', 'ranking_by_heldout_task_score', 'verdict', 'scripts']
- verdict={"stage2_winner": "mlp_behemoth", "heldout_task_score_metric": "overall mean target logprob of the factored config (Stage 2 convention)", "mlp_behemoth_beats_uniform_on_heldout": true, "mlp_behemoth_confirmed_sweep_winner": true, "byte_fair_comparison": {"variant": "mlp_behemoth_lite", "variant_real_shape_bytes": 19358176, "uniform_real_shape_bytes": 19434496, "variant_within_uniform_budget": true, "variant_beats_uniform_on_heldout": true, "variant_gap_closed_overall": 0.0947229129097021, "uniform_gap_closed_overall": 0.01564243038524459}, "mlp_behemoth_byte_caveat": {"mlp_behemoth_real_shape_bytes": 21719776, "uniform_real_shape_bytes": 19434496, "over_bytes": 2285280, "over_pct": 11.8, "note": "mlp_behemoth's Stage 2 win was not byte-fair; the byte-fair comparison is the variant's row."}}
- configs={"uniform_rank32": {"name": "uniform_rank32", "kind": "human_baseline", "ranks": {"embed": 32, "attn.q_proj": 32, "attn.k_proj": 32, "attn.v_proj": 32, "attn.o_proj": 32, "mlp.gate": 32, "mlp.up": 32, "mlp.down": 32}, "rank0_layer_names": [], "real_shape_bytes": 19434496, "configs": {"base": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.907639310877745}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -11.568273144098278}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -8.098655694460739}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -7.055989094074219}}}, "full_delta": {"overall": {"n": 24, "accuracy": 0.16666666666666666, "mean_target_logprob": -5.322192186566966}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.894272131668772}, "instruction": {"n": 8, "accuracy": 0.5, "mean_target_logprob": -2.096013926456496}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.976290501575629}}}, "factored_delta": {"overall": {"n": 24, "accuracy": 0.0, "mean_target_logprob": -8.851554203835738}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -10.297644800209842}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -9.299502159565801}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.957515651731569}}}}, "gap_closed": {"knowledge": 0.27185025003406543, "instruction": -0.20005299525050946, "math": 1.2355731670467298, "overall": 0.01564243038524459}, "per_item": [{"bucket": "knowledge", "logprob": -12.447284086602247, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -6.0896188013150265, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -15.854590412931671, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -8.147514544844567, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -11.862084444157764, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -7.865520628128349, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -9.294762646619539, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -10.819782837079575, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -9.532485010686338, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.933549728098443, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -11.326082756254166, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -4.2459042955269455, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -11.143121419135793, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -10.478749897546045, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.699891449809007, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -10.036232719469663, "first_token_correct": 0}, {"bucket": "math", "logprob": -5.077893818957592, "first_token_correct": 0}, {"bucket": "math", "logprob": -6.483583546908075, "first_token_correct": 0}, {"bucket": "math", "logprob": -7.500344703423812, "first_token_correct": 0}, {"bucket": "math", "logprob": -4.190430632303273, "first_token_correct": 0}, {"bucket": "math", "logprob": -7.556504310356592, "first_token_correct": 0}, {"bucket": "math", "logprob": -6.033214856384206, "first_token_correct": 0}, {"bucket": "math", "logprob": -8.703859851819542, "first_token_correct": 0}, {"bucket": "math", "logprob": -10.11429349369946, "first_token_correct": 0}], "wall_s": 71.67, "eval_wall_s": 68.15, "peak_rss_mb": 3192.2}, "mlp_behemoth": {"name": "mlp_behemoth", "kind": "spark_recipe_stage2_winner", "ranks": {"embed": 10, "attn.q_proj": 20, "attn.k_proj": 0, "attn.v_proj": 20, "attn.o_proj": 20, "mlp.gate": 45, "mlp.up": 45, "mlp.down": 50}, "rank0_layer_names": ["attn.k_proj"], "real_shape_bytes": 21719776, "configs": {"base": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.907639310877745}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -11.568273144098278}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -8.098655694460739}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -7.055989094074219}}}, "full_delta": {"overall": {"n": 24, "accuracy": 0.16666666666666666, "mean_target_logprob": -5.322192186566966}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.894272131668772}, "instruction": {"n": 8, "accuracy": 0.5, "mean_target_logprob": -2.096013926456496}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.976290501575629}}}, "factored_delta": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.519294854322665}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -10.322385879852932}, "instruction": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -9.11764732690944}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.117851356205622}}}}, "gap_closed": {"knowledge": 0.2665569093656965, "instruction": -0.1697571955534997, "math": 11.771070334588293, "overall": 0.10831130486402876}, "per_item": [{"bucket": "knowledge", "logprob": -11.869581919159009, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -5.260216545256683, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -13.640625505545405, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -11.094353136443697, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -12.667091050882842, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -7.917084875768683, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -9.902145731672057, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -10.22798827409509, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.970952865296688, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -9.583043071480885, "first_token_correct": 0

## results/alien_sweep_stage2.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'method', 'build_validation', 'forward_validation', 'full_delta_fp16_bytes_real_shapes', 'shared_configs', 'recipes', 'human_baseline', 'ablations', 'rank0_analysis', 'ranking_by_task_score', 'api_calls', 'scripts']

## results/fourth_pair_stage2.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'method', 'build_validation', 'forward_validation', 'forward_validation_verdict', 'gap_closed_note', 'full_delta_fp16_bytes_real_shapes', 'shared_configs', 'recipes', 'human_baseline', 'ranking_by_task_score', 'winner', 'api_calls', 'scripts']

## results/hotswap_demo.json (top-level keys and compact verdict/ranking fields)
- keys=['model', 'decoding', 'prompts', 'patch_sizes_bytes', 'swaps', 'configs', 'peak_rss_mb', 'api_calls']
- configs={"base (no patch)": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}\n Comey\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant", "generated_tokens": 48, "seconds": 14.868, "json": {"parseable": false, "exact_keys": false, "exact_values": false}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo. Lauderdale. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital", "generated_tokens": 48, "seconds": 9.24, "contains_expected": true}, "math_percent": {"answer": "Sure, 15 percent of 200 is 30.eousystem\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.\u9c95system\nYou are Qwen, created by Alibaba Cloud.", "generated_tokens": 48, "seconds": 8.784, "contains_expected": true}}, "base + uniform rank-32 factored patch": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}", "generated_tokens": 31, "seconds": 12.162, "json": {"parseable": true, "exact_keys": true, "exact_values": true}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo.", "generated_tokens": 7, "seconds": 4.922, "contains_expected": true}, "math_percent": {"answer": "To find 15% of 200, you can use the following formula:\n\n(15/100) * 200 = 30\n\nSo, 15% of 200", "generated_tokens": 48, "seconds": 9.36, "contains_expected": true}}, "base + mlp_behemoth_lite factored patch": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}", "generated_tokens": 31, "seconds": 12.046, "json": {"parseable": true, "exact_keys": true, "exact_values": true}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo.", "generated_tokens": 7, "seconds": 7.891, "contains_expected": true}, "math_percent": {"answer": "15% of 200 = 30.", "generated_tokens": 13, "seconds": 5.928, "contains_expected": true}}}

===== END EVIDENCE DIGEST =====

```

### Prompt A: README audit

```text
You are Muse Glimmer, strict independent auditor. Reason efficiently and report FINDINGS ONLY. Do not narrate a claim-by-claim review and do not list supported claims except a maximum of three clean-area bullets at the end.

Audit target: README.md only as the primary document
Repository state: ganjikrishna/fraction-compressor-v0.4 at pushed head 3933fae16f5e1673cac38a000533a35fb7b0ecda.
The PRIMARY documents are exact pushed versions. The evidence digest was computed from pushed result JSON at the same head. Reference excerpts are exact lines from other pushed documents, supplied only for cross-document consistency.
Excluded local-only material, not pushed and not to be treated as repo content: later literature-citation edits; docs/intent.md; docs/literature_sweep_2026-10-28.md; results/cloning_question_panel.md; results/video_review_v2.md; video/; all fifth-pair result/example files. BUILD_PLAN.md is pushed and in scope in its own audit part.

Check: arithmetic/factual errors; stale or superseded numbers; inconsistencies; claims outrunning evidence; judge/submission risks. Recompute from the digest. If evidence is not supplied, label the point UNVERIFIABLE rather than calling it false, unless the wording itself is internally inconsistent or universal beyond its stated test.

For every finding: severity (CRITICAL/HIGH/MEDIUM/LOW), category, exact file + heading or quoted phrase, problem with recomputed/conflicting values, recommended correction. Most serious first. No duplicate roots. Maximum 2600 words.


===== PRIMARY PUSHED FILE: README.md =====
# Fraction Compressor v0.4

**One base model. Many tiny patch files. Swap a file, swap the behavior.**

What "fraction" means here: not math fractions. A fine-tuned AI model is a base model plus a patch (the weight difference between the two). This tool keeps only a fraction of that patch's information, stored at about 1 bit per weight, in a file small enough to swap in and out live.

![How Fraction Compressor v0.4 works](docs/how-it-works.svg)

## In plain words

A fine-tuned model differs from its base model by a patch (the delta). A normal patch is almost as big as the model itself. Fraction Compressor stores that patch in a factored form whose structure is kept as 1-bit signs, priced byte for byte by the code: 0.28 bits per weight for one large layer at rank 32 (the exact price depends on layer size and rank). v0.4 runs it through a factored runtime: two small multiplies, Y = (X U) V^T, without ever rebuilding the full weight matrix. One layer stored the normal way takes 8.4 MB; our rank-32 file takes 144 KB, and swapping patches is just loading a different small file. Compressing a patch is offline work done once with the full delta; the saving is in storage and at run time.

## Do it yourself

You need two models: a base model and a fine-tuned version of that same base, in safetensors format.

1. Make a patch from the pair (rank 32 everywhere, or pass a per-layer recipe file with `--recipe` instead of `--rank`):
   `python examples/make_patch.py --base <base-model-dir> --finetuned <finetuned-model-dir> --rank 32 --out patch.npz`
   The script subtracts the two models layer by layer, squeezes the difference into the factored format, and writes one patch file. It prints the patch's exact byte price next to the full difference at normal precision.
2. Check the patch any time:
   `python examples/make_patch.py --verify patch.npz --base <base-model-dir> --finetuned <finetuned-model-dir>`
3. Use it: load the patch together with the base model, as in `examples/hotswap_demo.py`, where patches swap in and out of one running base model live.

On the model pair used in this repo's benchmark (Qwen2.5-0.5B base and Instruct), rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller. The full run is saved at `results/make_patch_demo.txt`.

## How this is different

- **From memory files and system prompts** (the text files an AI agent reads, like a personality or memory file): those are words the model reads as instructions, they take up prompt space, and a later instruction can override them. A patch here is numbers applied to the model's own weights. The behavior changes in the math itself, uses no prompt space, and cannot be talked away.
- **From an adapter (like LoRA):** an adapter is a new add-on trained for one task, usually stored at normal precision. This tool takes a fine-tune that already exists and squeezes the difference between it and its base model into a 1-bit factored file, so an existing fine-tune becomes a small patch you can swap.
- **From shrinking a whole model (quantization):** that makes the one model smaller and slightly changes everything it does. This shrinks only the patch, so one base model stays exact and carries many behaviors, one small file each.

Why this matters, what bound it breaks, and where it stops working: [docs/why-it-matters.md](docs/why-it-matters.md).

## Prior art

Compressing a fine-tune's difference is an established research area, and this project builds on published methods, ideas only, no code: BitDelta (1-bit delta compression of fine-tuned models, NeurIPS 2024, arXiv:2402.10193), Delta-CoMe (SVD-based mixed-precision delta compression, NeurIPS 2024, arXiv:2406.08903), and LittleBit (arXiv:2506.13771). All code in this repo is original and was written during the event. What is ours is not the 1-bit format itself: it is the in-loop recipe search and judging by Muse Spark, the forced-multiply runtime, the first-token gate diagnosis with its force-start control, and the verification harness. Full credits: [NOTICE.md](NOTICE.md).

## Benchmark results

The benchmark compares three runs on the same questions: the base model alone, the base model with the full patch, and the base model with our compressed patch. The score is how strongly the model backs the correct answer (a log score; higher is better). "Gap closed" is the share of the base-to-full score gap that a compressed patch recovers. One limit applies everywhere below: the share of questions whose first answer token is exactly right stays low for every compressed version (about 1 to 2% on the first pair, about 8 to 9% on the second, 0 to about 3% on the third; the fourth pair is the exception, where the compressed versions reach 26 to 32% against the full patch's own 33.3%), so these are score results, not proof the model solves the tasks.

### Known limit: skills gated by the first token transfer weakly

Transfer depends on the skill, and one kind of skill is a weak case for this format. We tested a real one: NuExtract-1.5-tiny (MIT), a fine-tune of the same Qwen base that reads a text and a JSON template and answers with the template filled in. The fine-tune itself passes 9 of 10 test prompts (eight fully clean, one with a single reworded value); the plain base passes 0 of 10, because it stops immediately instead of answering. Our rank-32 patch passes only 1 of 10. The reason is narrow: this skill is decided by the first token the model emits, start the JSON or stop, and the compressed patch usually does not flip that one decision. On the one prompt where it does start, the extraction is fully correct. A control test settles why: force that first token and the plain base completes 7 of 10 cleanly, so in this test most of the skill was already in the base and the fine-tune's main work is the decision to start. The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own score: one clean more than the forced base, which at 10 prompts is within sampling noise, so the gate is the main story and any edge beyond the trigger is small at most. Making the patch bigger barely moves this boundary: a rank-64 patch (37,044,736 bytes) and a rank-128 patch (72,265,216 bytes) each pass 2 of 10. Spending the same bytes differently did worse, not better: a Muse Spark recipe that puts most of the rank-32 budget into the embedding and the attention output layer (19,434,400 bytes, the same budget) passes 0 of 10, and measured directly at the first token, its average start-vs-stop margin sits further from opening the gate than the uniform patch's. Broad behavior transfers much better under the same format: the Instruct patch below closes 23.2% of the score gap on 96 fresh questions, with wins you can see in the live hot-swap demo. So the limit is format-gated, not general. Full records: `results/skill_demo.json`, `results/skill_demo_forced.json`, `results/skill_demo_ranks.json`, `results/skill_demo_recipe.json`, and the consultation behind this wording in `results/skill_limit_consultation.md`.

### First pair: Qwen2.5-0.5B base and Instruct

Muse Spark proposed uneven per-layer compression recipes (the Alien Sweep). The search winner, mlp_behemoth, is byte-unfair: at 21,719,776 bytes it spends 11.8% more than the human recipe's budget, so it is named only as the parent. The headline recipe is its byte-fair variant, mlp_behemoth_lite: 19,358,176 bytes, fewer than the human uniform rank-32 recipe's 19,434,496 bytes.

The check that matters is fresh questions the search never saw. That set grew from 24 to 96 questions. On all 96, lite closes 23.2% of the gap, against 2.1% for the human recipe. Lite also wins on each half alone: 9.5% vs 1.6% on the original 24 questions, and 30.4% vs 2.3% on the 72 new ones. An early read from the first small fresh set was that the lead might shrink on fresh questions; on the bigger set the lead grew instead, so that worry did not survive. Lite does not win every kind of question: on knowledge questions the human recipe closes more of the gap (7.8% vs 3.7%); lite's lead comes from the instruction and math questions.

### Second pair: SmolLM2-360M base and Instruct

The same contest ran on a second, different model pair. The search winner there (o-down supercharge) was byte-unfair too, so the byte-fair winner is its byte-matched variant, o-down-rebalanced: 19,683,328 bytes, inside the human recipe's budget of 19,705,856 bytes. On the same 96 fresh questions it beats the human uniform recipe by 0.293 score points on average, and it wins on both halves of the set separately.

One warning that applies to this pair only: every compressed version scores better than the full patch itself, so the gap-closed percentage goes above 100% here. That means the percentage is NOT a share of the fine-tune recovered for this pair. For this pair, the raw score margin (0.293 points) is the honest measure.

### Third pair: Llama 3.2 1B base and Instruct

The same contest also ran on Meta's own open weights, Llama 3.2 1B base and Instruct. The search winner, no_embed_mlp_spread, was byte-unfair again: at 34,690,048 bytes it spends 38.0% more than the human recipe's budget of 25,143,296 bytes, so it is named only as the parent. The headline recipe is its byte-fair variant, no_embed_mlp_spread_balanced: 24,515,584 bytes, inside the budget.

On the same 96 fresh questions, the byte-fair variant scores -12.714 against the human uniform recipe's -14.201: it closes 15.9% of the gap, while the human recipe closes -7.6%, which is below the base model itself (-13.718), so on this pair the plain human recipe makes the score worse than using no patch at all. The byte-fair variant also wins on each half alone: 20.0% vs -1.7% on the original 24 questions, and 14.8% vs -9.1% on the 72 new ones.

Recovery on this pair is weaker than on the other two pairs (15.9% here against 23.2% on the Qwen pair), and first-token accuracy stays low for every compressed version: 2.1% for the byte-fair variant, against 21.9% for the full patch itself. No compressed version outscores the full patch on this pair, so the gap-closed percentage stays a true share of the fine-tune recovered here.

### Fourth pair: Qwen2.5-1.5B base and Instruct (the scale test)

A fresh-eyes review (GPT-OSS, see `results/fresh_perspective.md`) asked whether any of this survives above 1B parameters, so the same contest ran on a fourth pair, Qwen2.5-1.5B base and Instruct. This round the recipes were priced on the real shapes from the start, and all five of Muse Spark's recipes came in under the human recipe's budget of 39,046,144 bytes. The search winner, Down Dominator, is byte-fair itself at 38,623,232 bytes (it drops the MLP gate and up matrices entirely and spends the bytes on the down projection and the attention output), so it is its own byte-fair headline recipe, no variant needed.

On the same 96 fresh questions, Down Dominator scores -6.344 against the human uniform recipe's -6.478: it still wins, but by about 0.13 score points, far narrower than the first pair's win, and the win does not hold on both halves of the set (the human recipe wins the first 24 questions; Down Dominator wins the 72 newer ones). One pattern from the second pair repeats here: every compressed version outscores the full patch itself (full patch -7.810), so the gap-closed percentage goes above 100% (130.7% against 127.9%) and is NOT a share of the fine-tune recovered on this pair; the raw score margin (about 0.13 points) is the honest measure. The recipe's edge is also not an accuracy edge: the human recipe's first-token accuracy on the 96 is 32.3%, against Down Dominator's 26.0% and the full patch's own 33.3%.

So the scale answer is mixed and we state it that way: the format and the recipe contest both still work at 1.5B (a roughly 39 MB patch against a 3,087,138,816-byte full patch, about 79x smaller, scoring at the full patch's level on this metric), but the AI-designed recipe's advantage over the plain human recipe shrinks from decisive at 0.5B to narrow and subset-dependent at 1.5B.

### Baseline: a plain 1-bit delta, priced honestly

A fair question (raised by a fresh-eyes GPT-OSS review) is why not a plain 1-bit delta, the BitDelta idea: sign of each delta weight, one scale per matrix. The catch is price: a plain 1-bit delta cannot go below 1 bit per weight, which on the first pair's 169 matrices is 61,745,828 bytes. At our 19.4 MB budget it does not fit at all; the factored format is the only one of the two that exists there. At the plain format's own floor price, the comparison flips: the BitDelta initialization (sign times the per-matrix mean absolute value, exactly as published, with no scale distillation or any training) closes 43.6% of the gap on the same 96 questions, against 38.5% for our factored format at uniform rank 108 priced just under it (61,258,816 bytes). So the honest summary is a two-budget curve: below about 62 MB on this pair the factored format wins by reach, and at about 62 MB the plain initialization wins on quality. Full record: `results/bitdelta_baseline.json`, judged in `results/spark_judging_baseline.md`.

### How these numbers are checked

Every number above is produced by a script in this repo and can be rerun. Beyond the reruns, Gemini independently recomputed the arithmetic, a Muse Spark judging pass checked each headline claim against the exact result files it cites, and a Muse Glimmer reference check set the wording rules used here (which recipe may be called the leader, and how the second pair's percentage may be described). A subset of the results, picked using true quantum random numbers from IBM Quantum hardware, was re-audited end to end: 41 of 41 checks passed. The records live in `results/`.

## Built during the hackathon

This repository contains only work built during the Meta Global AI Developer Hackathon, October 26 to November 4, 2026 (Indie Developer track, Push the Frontier).

Pre-existing work (not part of this submission): Fraction Compressor v0.1 to v0.3 and the Signet delta-transfer experiments live in the original repository, [github.com/ganjikrishna/fraction-compressor](https://github.com/ganjikrishna/fraction-compressor). The compression and Signet methods were designed and validated there before the event. What is new in this repo is the factored runtime, the end-to-end task benchmark, and the Meta model comparison.

## What is in this repo

- `src/factored.py`: the factored runtime (quantize a delta, price its storage, apply it factored). Tested, see `tests/test_factored.py`.
- `examples/quickstart.py`: a 1-minute smoke run on a dummy delta (needs only numpy): prints the storage cost, bits per weight, and the factored error next to the best any factored form could do at the same rank.
- `fixtures/`: the quantum random fixture for the benchmark's audit sampling (IBM Quantum hardware, backend and job logged in the file).
- `src/bench.py` and `results/`: the end-to-end task benchmark (base vs full delta vs compressed delta) and the Alien Sweep, where Muse Spark proposed compression recipes that were scored, cross-validated (Gemini arithmetic checks, a Muse Spark judging pass, a Muse Glimmer reference check), and confirmed on 96 fresh held-out questions generated by Muse Spark, on four model pairs. See Benchmark results above.
- The live hot-swap demo: one base model loaded once, patch files swapped in live in about a tenth of a second (examples/hotswap_demo.py, transcript in results/).

## Author and credits

Built by **Vinay K Ganji Krishna**, solo participant (Indie Developer track) and author of record.

Implementation, benchmarking, and documentation were carried out with **Ember**, an AI agent powered by Muse Spark, working under the author's direction, the same way this event encourages building with Meta's Muse Code agent. Design pressure-testing also drew on a Gemini design-debate chat. Every result in this repository is produced by scripts in this repository and can be rerun.

## License

MIT, (c) 2026 Vinay K Ganji Krishna. Methods are clean-room implementations from published papers; see [NOTICE.md](NOTICE.md) for citations.

===== END README.md =====

===== EVIDENCE DIGEST =====
# Evidence digest computed from the pushed result JSON files at commit 3933fae

## results/alien_sweep_heldout96.json
- base: mean_target_logprob=-11.1497780625, accuracy=0.031250
- full_delta: mean_target_logprob=-8.5424662354, accuracy=0.166667
- full_delta_fp16_bytes=987922432
- ranking: mlp_behemoth: mean=-10.45627380592698, gap_closed=0.2659843941106181 (26.5984%), accuracy=0.020833333333333332, bytes=21719776
- ranking: mlp_behemoth_lite: mean=-10.54508293414888, gap_closed=0.2319228264458408 (23.1923%), accuracy=0.010416666666666666, bytes=19358176
- ranking: uniform_rank32: mean=-11.095640657042859, gap_closed=0.020763686533300157 (2.0764%), accuracy=0.010416666666666666, bytes=19434496
- verdict.byte_fair_headline_question=does mlp_behemoth_lite still beat uniform_rank32 on the combined 96 fresh items?
- verdict.lite_beats_uniform_on_combined96=True
- verdict.lite_gap_closed_combined96=0.2319228264458408
- verdict.uniform_gap_closed_combined96=0.020763686533300157
- verdict.lite_within_uniform_budget=True
- verdict.subset_consistency.heldout24.lite_gap_closed=0.0947229129097021
- verdict.subset_consistency.heldout24.uniform_gap_closed=0.01564243038524459
- verdict.subset_consistency.heldout24.lite_beats_uniform=True
- verdict.subset_consistency.heldout72_new.lite_gap_closed=0.303801464368062
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=0.023446697818697487
- verdict.subset_consistency.heldout72_new.lite_beats_uniform=True
- verdict.mlp_behemoth_reference_only.note=mlp_behemoth is BYTE-UNFAIR (over the uniform budget) and is reported as a reference only, never as the headline.
- verdict.mlp_behemoth_reference_only.real_shape_bytes=21719776
- verdict.mlp_behemoth_reference_only.uniform_real_shape_bytes=19434496
- verdict.mlp_behemoth_reference_only.over_bytes=2285280
- verdict.mlp_behemoth_reference_only.over_pct=11.8
- verdict.mlp_behemoth_reference_only.combined96_gap_closed=0.2659843941106181
- verdict.mlp_behemoth_reference_only.combined96_factored_mean_target_logprob=-10.45627380592698

## results/second_pair_heldout96.json
- base: mean_target_logprob=-12.8785653857, accuracy=0.010417
- full_delta: mean_target_logprob=-8.4321585239, accuracy=0.093750
- full_delta_fp16_bytes=723517440
- ranking: o-down supercharge: mean=-8.03994579872309, gap_closed=1.0882089150651426 (108.8209%), accuracy=0.09375, bytes=27660288
- ranking: o-down-rebalanced: mean=-8.072964749082066, gap_closed=1.080782930132702 (108.0783%), accuracy=0.08333333333333333, bytes=19683328
- ranking: uniform_rank32: mean=-8.366280457949834, gap_closed=1.0148160229227625 (101.4816%), accuracy=0.08333333333333333, bytes=19705856
- verdict.stage2_winner=o-down supercharge
- verdict.byte_fair_contender=o-down-rebalanced
- verdict.byte_fair_headline_question=does o-down-rebalanced beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=1.080782930132702
- verdict.uniform_gap_closed_combined96=1.0148160229227625
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=27660288
- verdict.winner_byte_status.uniform_real_shape_bytes=19705856
- verdict.winner_byte_status.winner_byte_unfair=True
- verdict.winner_byte_status.winner_combined96_gap_closed=1.0882089150651426
- verdict.subset_consistency.heldout24.contender_gap_closed=1.037137028575536
- verdict.subset_consistency.heldout24.uniform_gap_closed=0.9703361598361151
- verdict.subset_consistency.heldout24.contender_beats_uniform=True
- verdict.subset_consistency.heldout72_new.contender_gap_closed=1.0979379349340161
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=1.0322988159821247
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## results/third_pair_heldout96.json
- base: mean_target_logprob=-13.7178328094, accuracy=0.010417
- full_delta: mean_target_logprob=-7.3867130269, accuracy=0.218750
- full_delta_fp16_bytes=2471493632
- ranking: no_embed_mlp_spread: mean=-12.12275284734357, gap_closed=0.25194278687724053 (25.1943%), accuracy=0.03125, bytes=34690048
- ranking: no_embed_mlp_spread_balanced: mean=-12.714218663974016, gap_closed=0.15852079567397595 (15.8521%), accuracy=0.020833333333333332, bytes=24515584
- ranking: uniform_rank32: mean=-14.20128408199294, gap_closed=-0.07636110027783072 (-7.6361%), accuracy=0.0, bytes=25143296
- verdict.stage2_winner=no_embed_mlp_spread
- verdict.byte_fair_contender=no_embed_mlp_spread_balanced
- verdict.byte_fair_headline_question=does no_embed_mlp_spread_balanced beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=0.15852079567397595
- verdict.uniform_gap_closed_combined96=-0.07636110027783072
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=34690048
- verdict.winner_byte_status.uniform_real_shape_bytes=25143296
- verdict.winner_byte_status.winner_byte_unfair=True
- verdict.winner_byte_status.winner_combined96_gap_closed=0.25194278687724053
- verdict.subset_consistency.heldout24.contender_gap_closed=0.200373434383912
- verdict.subset_consistency.heldout24.uniform_gap_closed=-0.016714667787171608
- verdict.subset_consistency.heldout24.contender_beats_uniform=True
- verdict.subset_consistency.heldout72_new.contender_gap_closed=0.14817956351361586
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=-0.09109894297869517
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## results/fourth_pair_heldout96.json
- base: mean_target_logprob=-12.5841302690, accuracy=0.010417
- full_delta: mean_target_logprob=-7.8097449276, accuracy=0.333333
- full_delta_fp16_bytes=3087138816
- ranking: Down Dominator: mean=-6.343687772752477, gap_closed=1.3070672034171866 (130.7067%), accuracy=0.2604166666666667, bytes=38623232
- ranking: uniform_rank32: mean=-6.478079873557243, gap_closed=1.2789186374354595 (127.8919%), accuracy=0.3229166666666667, bytes=39046144
- verdict.stage2_winner=Down Dominator
- verdict.byte_fair_contender=Down Dominator
- verdict.byte_fair_headline_question=does Down Dominator beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=1.3070672034171866
- verdict.uniform_gap_closed_combined96=1.2789186374354595
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=38623232
- verdict.winner_byte_status.uniform_real_shape_bytes=39046144
- verdict.winner_byte_status.winner_byte_unfair=False
- verdict.winner_byte_status.winner_combined96_gap_closed=1.3070672034171866
- verdict.subset_consistency.heldout24.contender_gap_closed=1.1242514732201125
- verdict.subset_consistency.heldout24.uniform_gap_closed=1.152286379770239
- verdict.subset_consistency.heldout24.contender_beats_uniform=False
- verdict.subset_consistency.heldout72_new.contender_gap_closed=1.3791549665115759
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=1.3288521753254294
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## Independent arithmetic spot calculations
- Qwen pair full/uniform ratio = 50.833447; full/lite ratio = 51.033859.
- Qwen 1.5B full/Down Dominator ratio = 79.929583; full/uniform ratio = 79.063859.
- One-layer ratio using 8,388,608 bytes / 147,456 bytes = 56.888889.
- Qwen pair all-in effective bits/weight for uniform price = 0.314753 bpw; for lite = 0.313517 bpw.
- BitDelta pricing: {'n_matrices': 169, 'n_weights_169_matrices': 493961216, 'bitdelta_init_price_bytes': 61745828, 'bitdelta_price_formula': 'ceil(total_weights / 8) + 4 bytes x n_matrices (one fp32 scale per matrix)', 'factored_matched_rank': 108, 'factored_matched_price_bytes': 61258816, 'factored_rank_plus_one_price_bytes': 61809136, 'factored_under_by_bytes': 487012}; configs: {'bitdelta_init': {'kind': 'published_baseline_initialization', 'definition': "BitDelta initialization (Liu et al., arXiv:2402.10193): per matrix, delta_hat = sign(delta) * mean(|delta|); one fp32 scale per matrix; NO scale distillation and NO training. The full BitDelta method distills the scales on data afterwards; that step is deliberately not run, and this config must be cited as the initialization, not as BitDelta's final reported quality.", 'mean_target_logprob': -10.012813627503721, 'accuracy_first_token': 0.0625, 'price_bytes': 61745828, 'wall_s': 285.21, 'peak_rss_mb': 3578.4}, 'factored_uniform_rank108': {'kind': 'ours_factored_matched_budget', 'definition': 'factored.quantize_delta at uniform rank 108 on all 169 matrices: the largest uniform rank whose factored.storage_bytes total fits under the plain 1-bit price.', 'mean_target_logprob': -10.146044864550612, 'accuracy_first_token': 0.03125, 'price_bytes': 61258816, 'wall_s': 287.5, 'peak_rss_mb': 3279.4}}.

## results/skill_demo.json
- patch={'built_by': 'examples/make_patch.py', 'rank_mode': 'uniform rank 32', 'storage_bytes': 19434496, 'file_bytes_on_disk': 19801674, 'full_delta_fp16_bytes': 987922432}
- base (no patch): counts={'clean': 0, 'partial': 0, 'failed': 10}
- base + compressed patch (uniform rank 32): counts={'clean': 1, 'partial': 0, 'failed': 9}
- base + full delta (fine-tune weights): counts={'clean': 8, 'partial': 1, 'failed': 1}

## results/skill_demo_forced.json
- unforced_reference={'base (no patch)': {'clean': 0, 'partial': 0, 'failed': 10}, 'base + compressed patch (uniform rank 32)': {'clean': 1, 'partial': 0, 'failed': 9}, 'base + full delta (fine-tune weights)': {'clean': 8, 'partial': 1, 'failed': 1}}
- base, forced start: counts={'clean': 7, 'partial': 1, 'failed': 2}
- base + compressed patch (uniform rank 32), forced start: counts={'clean': 8, 'partial': 1, 'failed': 1}

## results/skill_demo_ranks.json
- test=skill-transfer size test: does a larger uniform patch move the first-token gate?
- skill_pair=Qwen/Qwen2.5-0.5B base + numind/NuExtract-1.5-tiny (MIT) JSON extraction
- prompts=the same 10 screening prompts and the same judge as results/skill_demo.json (clean = parses as JSON, keys match template, every expected value present)
- decoding=greedy, max 64 new tokens, raw NuExtract prompt format
- reference_counts: {'note': 'both reruns (rank 64 and rank 128 runs) reproduced these two configs exactly: base 0/0/10, full delta 8 clean / 1 partial / 1 failed'}
- conclusion=Clean transfers: rank 32 = 1/10 at 19,434,496 B; rank 64 = 2/10 at 37,044,736 B; rank 128 = 2/10 at 72,265,216 B. Quadrupling the patch buys one extra prompt and then nothing: at these sizes the first-token gate barely moves with uniform size.
- verify=rank 64 and rank 128 patches both passed make_patch --verify (worst factored-vs-dense diff 4.3e-16 / 3.1e-16; file-vs-fresh rel diff 5.0e-04 / 3.3e-04, the designed fp16 V rounding). Build peaks: 4,754 MB both; verify peaks 4,917 / 5,067 MB.

## results/skill_demo_recipe.json
- test=allocation test: same bytes (19,434,496 B budget), smarter placement vs uniform rank 32
- skill_pair=Qwen/Qwen2.5-0.5B base + numind/NuExtract-1.5-tiny (MIT) JSON extraction
- recipe_generation: {'provider': 'baseten', 'model': 'meta-models/muse-spark-open-1026', 'max_tokens': 16000, 'budget_bytes': 19434496, 'prompt': 'You are proposing compression recipes for a factored 1-bit weight-delta format. A recipe assigns one integer rank to each layer TYPE; that rank is used for that layer type in all 24 transformer blocks (the embedding is a single matrix). The stored size of one matrix at rank r is priced exactly as:\n\n  bytes(matrix, r) = ceil(rows * r / 8) + 4 * rows + 2 * cols * r\n\nLayers (rows x cols of the delta matrix):\n  embed: delta matrix 151936 x 896, rank may be 0..896\n  attn.q_proj: delta matrix 896 x 896, rank may be 0..896\n  attn.k_proj: delta matrix 128 x 896, rank may be 0..128\n  attn.v_proj: delta matrix 128 x 896, rank may be 0..128\n  attn.o_proj: delta matrix 896 x 896, rank may be 0..896\n  mlp.gate: delta matrix 4864 x 896, rank may be 0..896\n  mlp.up: delta matrix 4864 x 896, rank may be 0..896\n  mlp.down: delta matrix 896 x 4864, rank may be 0..896\n\nThe total size of a recipe is bytes(embed) + 24 * (sum of bytes over the other 7 layer types), and it must be <= 19434496 bytes. That is exactly the cost of the uniform rank-32 recipe on this model; you have the same bytes, spend them differently.\n\nThe model pair is Qwen2.5-0.5B base and NuExtract-1.5-tiny, a fine-tune for structured JSON extraction (read a text and a JSON template, answer with the filled template). The finding you are designing against: this skill is gated by the FIRST generated token. The fine-tune starts the JSON; the plain base emits end-of-text immediately and answers nothing (0 of 10 test prompts). Our uniform rank-32 patch flips that gate on only 1 of 10 prompts (on the 9 others the patched model still stops immediately), even though the one extraction it does start is fully correct. Bigger uniform patches barely help (rank 64 and rank 128 each flip 2 of 10). So placement, not size, is the open question. Weigh protecting the embedding (it feeds every token position and, with tied weights, the output head) and the output-side layers (attn.o_proj, mlp.down) that shape the final logits, if you judge that is where the start-vs-stop decision lives.\n\nPropose exactly 5 recipes, ordered best-first: put the recipe you recommend most first. Make them genuinely different from each other and from uniform: uneven allocations are the point. Every recipe must include every layer name exactly once in its "ranks" object, with an integer rank (0 is allowed and means that layer type\'s delta is dropped).\n\nReply with ONLY a JSON object, no markdown fences, no commentary, in exactly this shape:\n{"recipes": [{"name": "<short name>", "reason": "<one sentence>", "ranks": {"embed": 0, "attn.q_proj": 0, "attn.k_proj": 0, "attn.v_proj": 0, "attn.o_proj": 0, "mlp.gate": 0, "mlp.up": 0, "mlp.down": 0}}]}\nReplace the zeros with your ranks. Check your arithmetic: each recipe\'s total (embed once + 24 blocks) must be <= 19434496 bytes.'}
- chosen_recipe: {'name': 'Gatekeeper Embed+O', 'reason': 'Maximizes the tied embed and cheap-to-expensive output ratio by pushing embed to 382 and o_proj to 64 with minimal down to flip the first-token EOS vs JSON gate.'}
- chosen_recipe_price_bytes=19434400
- patch_file_bytes_on_disk=18796330
- verify: {'result': 'PASS'}
- demo_run: {'config_label': 'base + compressed patch (recipe Gatekeeper Embed+O)'}
- first_token_margins: {'measure': 'first-token logprob margin', 'definition': "margin = logprob(fine-tune's actual first generated token) - logprob(end-of-text 151643) at the first generation position, natural log; positive means the gate is open (starting the JSON beats stopping)", 'peak_rss_mb': 2354.3}
- conclusion=Placement did not beat size at equal bytes; it did worse. The Spark recipe's radical reallocation (embed 382, mlp.gate/up dropped to 0) opened 0 of 10 gates and its mean first-token margin (-4.14) is far below uniform rank 32 (-1.29). The gate-open counts measured from margins (base 0, rank32 1, recipe 0, full delta 10) exactly match the generation outcomes. Neither bigger uniform patches (2/10 at rank 128) nor this reallocation opens the gate at these budgets; uniform rank 32 is closest per byte.

## results/alien_sweep_heldout.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'byte_matched_variant', 'method', 'shared_configs', 'configs', 'ranking_by_heldout_task_score', 'verdict', 'scripts']
- verdict={"stage2_winner": "mlp_behemoth", "heldout_task_score_metric": "overall mean target logprob of the factored config (Stage 2 convention)", "mlp_behemoth_beats_uniform_on_heldout": true, "mlp_behemoth_confirmed_sweep_winner": true, "byte_fair_comparison": {"variant": "mlp_behemoth_lite", "variant_real_shape_bytes": 19358176, "uniform_real_shape_bytes": 19434496, "variant_within_uniform_budget": true, "variant_beats_uniform_on_heldout": true, "variant_gap_closed_overall": 0.0947229129097021, "uniform_gap_closed_overall": 0.01564243038524459}, "mlp_behemoth_byte_caveat": {"mlp_behemoth_real_shape_bytes": 21719776, "uniform_real_shape_bytes": 19434496, "over_bytes": 2285280, "over_pct": 11.8, "note": "mlp_behemoth's Stage 2 win was not byte-fair; the byte-fair comparison is the variant's row."}}
- configs={"uniform_rank32": {"name": "uniform_rank32", "kind": "human_baseline", "ranks": {"embed": 32, "attn.q_proj": 32, "attn.k_proj": 32, "attn.v_proj": 32, "attn.o_proj": 32, "mlp.gate": 32, "mlp.up": 32, "mlp.down": 32}, "rank0_layer_names": [], "real_shape_bytes": 19434496, "configs": {"base": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.907639310877745}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -11.568273144098278}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -8.098655694460739}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -7.055989094074219}}}, "full_delta": {"overall": {"n": 24, "accuracy": 0.16666666666666666, "mean_target_logprob": -5.322192186566966}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.894272131668772}, "instruction": {"n": 8, "accuracy": 0.5, "mean_target_logprob": -2.096013926456496}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.976290501575629}}}, "factored_delta": {"overall": {"n": 24, "accuracy": 0.0, "mean_target_logprob": -8.851554203835738}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -10.297644800209842}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -9.299502159565801}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.957515651731569}}}}, "gap_closed": {"knowledge": 0.27185025003406543, "instruction": -0.20005299525050946, "math": 1.2355731670467298, "overall": 0.01564243038524459}, "per_item": [{"bucket": "knowledge", "logprob": -12.447284086602247, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -6.0896188013150265, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -15.854590412931671, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -8.147514544844567, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -11.862084444157764, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -7.865520628128349, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -9.294762646619539, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -10.819782837079575, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -9.532485010686338, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.933549728098443, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -11.326082756254166, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -4.2459042955269455, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -11.143121419135793, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -10.478749897546045, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.699891449809007, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -10.036232719469663, "first_token_correct": 0}, {"bucket": "math", "logprob": -5.077893818957592, "first_token_correct": 0}, {"bucket": "math", "logprob": -6.483583546908075, "first_token_correct": 0}, {"bucket": "math", "logprob": -7.500344703423812, "first_token_correct": 0}, {"bucket": "math", "logprob": -4.190430632303273, "first_token_correct": 0}, {"bucket": "math", "logprob": -7.556504310356592, "first_token_correct": 0}, {"bucket": "math", "logprob": -6.033214856384206, "first_token_correct": 0}, {"bucket": "math", "logprob": -8.703859851819542, "first_token_correct": 0}, {"bucket": "math", "logprob": -10.11429349369946, "first_token_correct": 0}], "wall_s": 71.67, "eval_wall_s": 68.15, "peak_rss_mb": 3192.2}, "mlp_behemoth": {"name": "mlp_behemoth", "kind": "spark_recipe_stage2_winner", "ranks": {"embed": 10, "attn.q_proj": 20, "attn.k_proj": 0, "attn.v_proj": 20, "attn.o_proj": 20, "mlp.gate": 45, "mlp.up": 45, "mlp.down": 50}, "rank0_layer_names": ["attn.k_proj"], "real_shape_bytes": 21719776, "configs": {"base": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.907639310877745}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -11.568273144098278}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -8.098655694460739}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -7.055989094074219}}}, "full_delta": {"overall": {"n": 24, "accuracy": 0.16666666666666666, "mean_target_logprob": -5.322192186566966}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.894272131668772}, "instruction": {"n": 8, "accuracy": 0.5, "mean_target_logprob": -2.096013926456496}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.976290501575629}}}, "factored_delta": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.519294854322665}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -10.322385879852932}, "instruction": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -9.11764732690944}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.117851356205622}}}}, "gap_closed": {"knowledge": 0.2665569093656965, "instruction": -0.1697571955534997, "math": 11.771070334588293, "overall": 0.10831130486402876}, "per_item": [{"bucket": "knowledge", "logprob": -11.869581919159009, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -5.260216545256683, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -13.640625505545405, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -11.094353136443697, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -12.667091050882842, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -7.917084875768683, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -9.902145731672057, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -10.22798827409509, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.970952865296688, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -9.583043071480885, "first_token_correct": 0

## results/alien_sweep_stage2.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'method', 'build_validation', 'forward_validation', 'full_delta_fp16_bytes_real_shapes', 'shared_configs', 'recipes', 'human_baseline', 'ablations', 'rank0_analysis', 'ranking_by_task_score', 'api_calls', 'scripts']

## results/fourth_pair_stage2.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'method', 'build_validation', 'forward_validation', 'forward_validation_verdict', 'gap_closed_note', 'full_delta_fp16_bytes_real_shapes', 'shared_configs', 'recipes', 'human_baseline', 'ranking_by_task_score', 'winner', 'api_calls', 'scripts']

## results/hotswap_demo.json (top-level keys and compact verdict/ranking fields)
- keys=['model', 'decoding', 'prompts', 'patch_sizes_bytes', 'swaps', 'configs', 'peak_rss_mb', 'api_calls']
- configs={"base (no patch)": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}\n Comey\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant", "generated_tokens": 48, "seconds": 14.868, "json": {"parseable": false, "exact_keys": false, "exact_values": false}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo. Lauderdale. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital", "generated_tokens": 48, "seconds": 9.24, "contains_expected": true}, "math_percent": {"answer": "Sure, 15 percent of 200 is 30.eousystem\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.\u9c95system\nYou are Qwen, created by Alibaba Cloud.", "generated_tokens": 48, "seconds": 8.784, "contains_expected": true}}, "base + uniform rank-32 factored patch": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}", "generated_tokens": 31, "seconds": 12.162, "json": {"parseable": true, "exact_keys": true, "exact_values": true}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo.", "generated_tokens": 7, "seconds": 4.922, "contains_expected": true}, "math_percent": {"answer": "To find 15% of 200, you can use the following formula:\n\n(15/100) * 200 = 30\n\nSo, 15% of 200", "generated_tokens": 48, "seconds": 9.36, "contains_expected": true}}, "base + mlp_behemoth_lite factored patch": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}", "generated_tokens": 31, "seconds": 12.046, "json": {"parseable": true, "exact_keys": true, "exact_values": true}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo.", "generated_tokens": 7, "seconds": 7.891, "contains_expected": true}, "math_percent": {"answer": "15% of 200 = 30.", "generated_tokens": 13, "seconds": 5.928, "contains_expected": true}}}

===== END EVIDENCE DIGEST =====

===== REFERENCE EXCERPTS FROM PUSHED FILE: docs/demo_script.md (line-numbered selected lines) =====
1: # Demo video script: Fraction Compressor v0.4
3: Exactly 3 minutes. One idea on screen at a time. Narration is the text under
4: each NARRATION heading, nothing else is spoken. Total narration: 440 words,
5: about 147 words per minute.
7: ## 0:00-0:25 The product: a fine-tune as a tiny patch file
9: ON SCREEN: Title card: FRACTION COMPRESSOR v0.4. Under it, one line: a
10: fine-tune squeezed into a patch file, about 19 MB instead of about 1 GB.
16: This is Fraction Compressor. It turns a fine-tuned model into one patch
18: the base model and swaps behavior live, in about a tenth of a second.
22: ## 0:25-0:44 Building on an existing idea: what is old, what is new
24: ON SCREEN: Two short lists. Published before: 1-bit delta compression,
25: BitDelta and Delta-CoMe; our earlier compressor work. Built this week:
26: factored runtime; Muse Spark recipes and claim judging; first-token gate
28: github.com/ganjikrishna/fraction-compressor-v0.4.
31: Honesty: one-bit delta compression is a published idea, BitDelta and
32: Delta-CoMe, and our earlier compressor work predates this week. Built
33: fresh this week: the factored runtime, Muse Spark designing recipes in
34: the loop and judging claims against the files, the first-token gate
37: ## 0:44-1:02 The problem: a fine-tune is almost a second model
39: ON SCREEN: Two file sizes side by side: the base model, and the full
40: difference file at 987,922,432 bytes.
43: A fine-tune is a base model plus a patch: the difference between them.
44: That difference alone: nine hundred eighty-eight million bytes, almost
45: the model itself. It keeps a fraction: about nought point three bits per
46: weight, all in. Ten fine-tunes, ten near-full models.
48: ## 1:02-1:21 Do it yourself: clone, quickstart, make a patch
51: 1. `git clone https://github.com/ganjikrishna/fraction-compressor-v0.4`
52: 2. `python3 examples/quickstart.py` and its printed size and error lines.
53: 3. `python3 examples/make_patch.py --base <base-model-dir> --finetuned <finetuned-model-dir> --out patch.npz --rank 32`
54:    and its printed sizes: patch 19,434,496 bytes, full difference
55:    987,922,432 bytes.
58: You can do this yourself. You need two models: a base and its fine-tune.
61: base and writes one file, about nineteen million bytes.
63: ## 1:21-1:48 The demo moment: swap a file, change the behavior
65: ON SCREEN: `python3 examples/hotswap_demo.py` running. First the base model
67: Arrival, 2016, Denis Villeneuve): the right object, then extra rambling
68: text, then the line `JSON SCORE: parseable=False`. Then the swap line:
69: patch loaded live in 0.09s. Then the same prompt again: exactly the object,
74: One base model, loaded once. I ask for strict JSON, a format programs
76: format check. Watch: the patch swaps in, about a tenth of a second.
81: ## 1:48-2:31 The numbers: smaller file, tested on fresh questions
83: ON SCREEN: The size table from the demo (full delta 987,922,432 bytes;
84: patches about 19.4 million bytes, 51x smaller), then the benchmark result
85: lines: 96 fresh questions, gap closed 23.2% vs 2.1%, and the second model
86: pair name, SmolLM2-360M. Then the scale test lines: Qwen2.5-1.5B, Spark
87: recipe 38,623,232 bytes inside the 39,046,144 byte human budget, margin
88: 0.134 nats on 96 fresh questions, patch about 39 MB vs 3,087,138,816 byte
89: full difference, about 80x smaller. Then the baseline lines: at the plain
90: 1-bit floor price of 61,745,828 bytes, plain BitDelta-style init gap
91: closed 43.6% vs factored rank-108 gap closed 38.5% at 61,258,816 bytes;
92: at 19,434,496 bytes no plain 1-bit delta fits, only the factored patch.
95: The patch is fifty-one times smaller: nineteen million bytes against
96: nine hundred eighty-eight million. The measure: how strongly the model
100: and does not count. Same pattern on SmolLM2; on a model three times
102: budget. Honestly: at sixty-two million bytes a one-bit patch closes more
103: gap. Our win is reach: at nineteen million bytes, where no plain one-bit
106: ## 2:31-2:44 Checked, not just claimed
108: ON SCREEN: Two short lines, one at a time: the Muse Spark judging record
109: citing its result files; then the audit line, 41 of 41 checks passed.
112: Then we checked ourselves. Muse Spark judged every headline claim and
113: had to cite the file behind each one. A quantum computer's random
116: ## 2:44-3:00 Close: a chip, not a note
118: ON SCREEN: The base model with the small patch file next to it. End card:
122: This is not a memory file. A memory file is a note the model reads; this
123: patch is a chip swapped inside the machine, numbers that change the
124: model's math. Fine-tunes to carry and swap: one base, many behaviors.
128: ## Production notes
132:   hotswap_demo run. Use the actual output; the transcript of record is
133:   results/hotswap_demo_transcript.txt.
138: - Cut to exactly 3:00. If a block runs long, trim screen pauses, not
140: - The full caveats (score is not task solving, first-token accuracy stays
141:   low, the knowledge-bucket result, the second pair's percentage warning)
===== END EXCERPTS docs/demo_script.md =====

===== REFERENCE EXCERPTS FROM PUSHED FILE: BUILD_PLAN.md (line-numbered selected lines) =====
1: # Build plan, Meta Global AI Developer Hackathon (Oct 26 to Nov 4, 2026)
4: - This repo holds only work done during the event. Prior work (v0.1 to v0.3, Signet) stays in github.com/ganjikrishna/fraction-compressor and is cited, not copied.
5: - The 3-minute demo video opens with one line stating what was pre-existing and what was built this week.
6: - Deadline: Wed Nov 4, 9:00 PM ET, via the Cerebral Valley submission portal.
8: ## Scope
10: 1. Factored-multiply runtime for 1-bit compressed deltas: Y = (X U) V^T, never materialize W. Memory read per token is the headline metric.
11: 2. End-to-end task-accuracy benchmark on the Signet probe sets (knowledge, instruction, math): base vs base + full delta vs base + sign/factored delta, so the compressed path is scored on task answers, not only weight error.
12: 3. Meta model in the loop: Muse Spark (Meta Model API) runs the same probe sets as a hosted reference, and Muse Spark Open is the planned open-weight candidate if time allows.
13: 4. Stretch, only if 1 to 3 are done: System Instruction Hot-Swap Test (base vs full delta vs sign delta on strict JSON-format prompts, scored by parseability).
14: 5. Alien Sweep: a wide, automated search over compression recipes that a human would not normally pick, filtered in two stages and verified by rerun (full protocol in its own section below). This replaces the planned human rank sweep; it does not add a separate build.
15: 6. Nov 4 reserved for the 3-minute demo video and the submission writeup.
16: 7. AirLLM-style streaming scale test (unparked by Vinay, Oct 28; active): the full Alien Sweep protocol on a fifth pair, Qwen2.5-7B base/Instruct, run on Flash with layer-by-layer streaming in our own NumPy runtime (the AirLLM concept, Apache 2.0; code ours), because a 7B model can never be held whole in Flash's 11 GB RAM. Includes a streamed generation demo: the winning byte-fair patch applied block by block as each block loads, updating a model that is never whole in memory. Vinay's Oct 28 decision: the run's scripts and results are saved locally; whether the 7B results enter the README and submission is decided after he reviews the outcome.
18: ## Demo video plan (approved by Vinay, Oct 26)
22: - Exactly 3 minutes. Opens with the required line stating what was pre-existing and what was built this week. Shape: 0:00 opening + problem; 0:30 the hot-swap moment; 1:30 benchmark numbers, including one Alien Sweep line (recipes tried, winner, held out result); 2:15 Muse Spark judging + quantum audit, one line each; 2:45 close.
23: - Rough cut early (as soon as the hot-swap demo runs) for Vinay to watch and react; final cut Nov 2-3 once the real numbers are in; Nov 4 reserved for submission only. Vinay approves the final cut before anything is posted.
24: - Simplicity rule (Vinay, Oct 27): keep the video as simple as possible. Plain words, no jargon without a one-line explanation, one idea at a time on screen. A newcomer watching once should understand what the tool does AND be able to pick it up and use it: the video shows the actual quickstart path (clone, run the quickstart, swap a patch file) in real steps, not just results.
25: - One script line near the close answers the question people will ask (Vinay, Oct 27): how is this different from a memory or personality file and other tools on the market? Plain version: a memory file is words the model reads; our patch is numbers that change the model's math. The README carries the fuller comparison (memory/prompts, adapters, whole-model shrinking).
26: - Do-it-yourself requirement (Vinay, Oct 27, after Agents 101): the video and the README must explain how the patch works AND how a viewer can do it themselves, as plain steps: take a base model and a fine-tuned version of it, run the compressor on the difference to get a small patch file, then load the patch with the base model to get the fine-tuned behavior. If the repo lacks a single clean script for that path, build one (examples/make_patch.py style) so the steps shown are the steps that actually run.
28: ## Working notes
30: - Muse Spark reasons before answering and reasoning tokens count against max_tokens; use generous caps in benchmark calls.
31: - Log every real Muse Spark call the benchmark makes (prompt, token counts, verdict) into results/ as it happens, so the Meta tooling use is evidenced in the repo, not just planned. (Muse Spark's own suggestion in its Oct 26 repo review. Soft budget from Vinay: keep Meta API use under the $100 alert level of the $150 credits where possible.)
32: - Agents 101 takeaways applied (Oct 27, Vinay: use what is needed): (1) Verification leads the submission and demo story: Meta's own session framed agent output as unverified until defensive checks confirm it, "as important as building the agentic loop", so our rerun + Spark + Gemini cross-checks are presented as a headline feature, not a footnote. (2) Spark judging verdicts cite the exact result files they are based on (grounding advice from the session). (3) In the submission's Meta-products field, describe the benchmark harness honestly in the session's terms: a harness loop (plan, run tools, check results) with Muse Spark inside it.
33: - Validation rule (Vinay, Oct 26): key results are cross-validated by Muse Spark AND Gemini, on top of the script reruns that produce them. If the two disagree, the disagreement is reported and investigated, never averaged away.
34: - Model scope (settled Oct 26 night, Vinay: do what is best): Spark family only. Spark 1.3 via the Meta Model API, Spark Open via Baseten, Glimmer as the Flash reference. The other Meta models (Wonder, Image, Voice Transcribe, SAM 3.1) do not fit a compression tool, so they will not be forced in just to name more models. Depth of Spark use is the tooling story.
35: - Credit order and tracking (Vinay, Oct 26, 10:23 PM): the Baseten credits may not be available after the hackathon, so Baseten carries the heavy lifting first while it lasts: bulk benchmark runs, sweeps, and repeated evaluations on Muse Spark Open. The Meta Model API is used as needed for task generation, judging, and validation. Every Baseten and Meta call is tracked in results/ with provider, model, time, purpose, and token counts, so the usage totals can be shared with the organizers in the submission and checked against the credit balances.
36: - Models and weights are never committed (see .gitignore); data/ holds local downloads only.
37: - Glimmer's new wording limit (Oct 27, after the strengthening results): when the compressed versions outscore the full patch itself (as on the SmolLM2 pair), the gap-closed percentage passes 100% and must not be presented as a fraction of the fine-tune recovered. Prose about that pair must state plainly that the percentage is not a recovery fraction there and that the raw score margin is the honest measure. Record: results/glimmer_reference_addendum.md.
38: - Fresh-question test size (Vinay, Oct 27): the fresh held-out test stays at 96 questions. Expanding it further was considered and declined; 96 is the validated set the headline numbers rest on.
39: - Skill-transfer limit disclosure (Vinay, Oct 27): the NuExtract gated-skill limit is disclosed upfront, not buried: a "Known limit" note opens the README's Benchmark results section. Vinay's direction was to check with Spark and Glimmer and do what is best; both validators independently recommended (c) disclose upfront AND test larger patches (rank 64/128). The size test ran the same day: 1/10 clean at rank 32, 2/10 at rank 64 and rank 128, so size barely moves this boundary. Records: results/skill_limit_consultation.md, results/skill_demo.json, results/skill_demo_ranks.json.
40: - Force-start control test (Oct 28, Vinay's go-ahead): settles the question Muse Spark raised in the why-it-matters debate. Forcing the fine-tune's own first token on the same 10 NuExtract prompts takes the plain base from 0/10 to 7 clean + 1 partial, so most of the extraction skill was already in the base and the fine-tune's main work is the decision to start. The rank-32 patch under the same forced start scores 8 clean + 1 partial, matching the full fine-tune's own unforced score: a small real edge beyond the trigger (it cleans the two prompts the forced base still fails, and loses one the forced base cleans), but the gate is the dominant term. Limit wording in README and docs/why-it-matters.md updated to the settled version. Records: results/skill_demo_forced.json, results/skill_demo_forced_transcript.txt, examples/skill_demo_forced.py.
41: - Scale test, fourth pair (Oct 28, Vinay: use the expiring compute): the full Alien Sweep protocol on Qwen2.5-1.5B base/Instruct (Apache 2.0, non-gated; 197 delta matrices, tied embeddings), answering the fresh-eyes GPT-OSS attack "does any of this survive above 1B?" (results/fresh_perspective.md). One change from Phases 1-3: recipes were generated against the real-shape budget directly (uniform rank 32 = 39,046,144 bytes), so all 5 Spark recipes priced byte-fair from the start and the Stage 2 winner, Down Dominator (38,623,232 bytes; mlp.gate/up dropped to 0, mlp.down 45, attn.o_proj 64), needed no byte-matched variant. Combined-96 result: Down Dominator -6.344 vs uniform -6.478 (raw margin about 0.134 nats; base -12.584, full delta -7.810), but the win is subset-mixed (uniform wins heldout24, Down Dominator wins heldout72_new) and uniform's first-token accuracy is higher (32.3% vs 26.0%). Every factored config outscores the full delta itself on this pair, so gap_closed exceeds 1.0 (1.307 vs 1.279) and is not a recovery fraction here (same pattern and wording rule as pair 2). Honest scale answer: the format and contest still work at 1.5B (about 79x smaller than the 3,087,138,816-byte full delta), but the recipe's edge over uniform narrows from decisive at 0.5B to narrow and subset-dependent at 1.5B. Validation: script recomputation 61/61 gap_closed values, zero mismatches; Muse Spark judging 5/5 SUPPORTED (
[EXCERPT TRUNCATED BY LENGTH]
===== END EXCERPTS BUILD_PLAN.md =====

===== REFERENCE EXCERPTS FROM PUSHED FILE: NOTICE.md (line-numbered selected lines) =====
1: # NOTICE: prior art, attribution, and originality
3: ## This project's own work
6: are original work by Vinay K Ganji Krishna, written during the Meta Global
7: AI Developer Hackathon (October 26 to November 4, 2026) and released under
8: the MIT License (see LICENSE). No third-party code is included in this
11: ## Published methods this work builds on
13: Compressing the difference between a base model and its fine-tune is an
18: - **BitDelta** (Liu et al., NeurIPS 2024, arXiv:2402.10193): 1-bit
21:   `examples/bitdelta_baseline.py` implements the paper's initialization
23:   training), and `results/bitdelta_baseline.json` reports how it scores
25: - **Delta-CoMe** (Ping et al., NeurIPS 2024, arXiv:2406.08903):
28:   the same. The lesson that where the bytes go matters more than how
30: - **LittleBit** (Lee et al., arXiv:2506.13771): extreme low-bit
32:   the author's earlier Fraction Compressor versions (v0.1 to v0.3, in
33:   the original repository) explored this direction; the factored form
36: ## What is ours
40: this repository are not the 1-bit delta format itself. They are:
42: - the in-loop recipe search and judging: Muse Spark proposes the
47:   patches swap in and out of a running base model live;
48: - the first-token gate diagnosis (skills whose first generated token
53:   scripts, cross-checked by independent models, and a sample picked
54:   with true quantum random numbers from IBM Quantum hardware was
57: ## Models
59: This repository distributes no model weights and no tokenizer files.
60: Experiments download models separately from Hugging Face, under each
61: model's own license: Qwen/Qwen2.5-0.5B and Qwen2.5-0.5B-Instruct
62: (Apache 2.0), HuggingFaceTB/SmolLM2-360M and SmolLM2-360M-Instruct
63: (Apache 2.0), meta-llama/Llama-3.2-1B and Llama-3.2-1B-Instruct
64: (Llama 3.2 Community License).
===== END EXCERPTS NOTICE.md =====

===== REFERENCE EXCERPTS FROM PUSHED FILE: docs/why-it-matters.md (line-numbered selected lines) =====
1: # Why it matters
3: A fine-tuned model is a base model plus a patch: everything training changed, and normally that patch is nearly as big as the model itself. This tool squeezes an existing fine-tune's patch into a file of about 19 MB instead of 1 GB, at 1 bit per weight. One base can then carry many behaviors, one small file each.
5: ## Three uses
7: - **Many behaviors, one model.** Fifty fine-tunes the normal way means fifty full models; as patches, fifty small files on one base.
8: - **Live switching.** A patch swaps in or out in a tenth of a second while the base keeps running, changing behavior mid-conversation.
9: - **Cheap to move.** A 19 MB file can be sent, downloaded on a slow link, or carried on a small device. A 1 GB model often cannot be.
11: ## How it differs from a download or a repo
13: Downloading a fine-tune gives you the whole model, full size. Small adapters like LoRA exist, but an adapter is a new add-on trained for one task. This tool starts from a fine-tune that exists and converts it, with no retraining: point the script at a base and its fine-tune, and it writes the patch and measures how much behavior the patch carries.
15: Two honest costs: making a patch needs both full models once, and running one needs the base in memory. The saving is in storing and moving behaviors.
17: ## What bound it breaks, and what it does not
19: The usual assumption is that at 1 bit per weight, nothing useful survives. Done the plain way, that holds: on Llama 3.2 1B, spreading the budget evenly scored below the base model itself, worse than no patch. Spending the same bytes where they matter kept a real share: 15.9% of the gap closed there, 23.2% on the Qwen pair. So one bound breaks: useful behavior survives smart squeezing.
23: Against the simplest rival, a plain 1-bit delta (the BitDelta initialization), the honest picture is two budgets, not one: on the Qwen pair a plain 1-bit delta cannot be smaller than about 62 MB, so at our 19 MB size it does not exist, while at its own 62 MB floor it closes more of the gap than our format does at the same price (43.6% against 38.5%). Our format's win is reach: it works at sizes the plain format cannot reach. Full record: `results/bitdelta_baseline.json`.
25: ## The known limit
27: One kind of skill transfers weakly: skills decided by the first token, like "start the JSON or stop." On a JSON-extraction fine-tune, the full fine-tune starts on 9 of 10 prompts, the base on 0, the patch on 1. Measured at the first token, the patch moves the model halfway toward starting (base -6.33, patch -1.29, full fine-tune +4.60) but usually does not cross. On the one prompt where it does start, the extraction is fully correct.
29: The author's intuition: the knowledge is there, it just needs to know to start. The control test has now been run, and it mostly backs him: force the fine-tune's first token and the plain base completes 7 of 10 cleanly (8 of 10 counting a partial), so in this test most of the extraction skill was already in the base, and what the fine-tune mainly installs is the decision to start. The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own unforced score. That is one clean more than the forced base, which at 10 prompts is within sampling noise, so the honest reading is: the gate is the main story, and any edge beyond the trigger is small at most. Full records: `results/skill_demo_forced.json`; the earlier debate is in `results/why_debate.md`, and the five-way validation of this test (script recomputation, Muse Spark, Muse Glimmer, Gemini, and Muse Spark Open via Baseten and via Fireworks) is in the `results/` files with `validation_forced` in their names.
===== END EXCERPTS docs/why-it-matters.md =====
```

### Prompt B: NOTICE + why-it-matters audit

```text
You are Muse Glimmer, strict independent auditor. Reason efficiently and report FINDINGS ONLY. Do not narrate a claim-by-claim review and do not list supported claims except a maximum of three clean-area bullets at the end.

Audit target: NOTICE.md and docs/why-it-matters.md as primary documents
Repository state: ganjikrishna/fraction-compressor-v0.4 at pushed head 3933fae16f5e1673cac38a000533a35fb7b0ecda.
The PRIMARY documents are exact pushed versions. The evidence digest was computed from pushed result JSON at the same head. Reference excerpts are exact lines from other pushed documents, supplied only for cross-document consistency.
Excluded local-only material, not pushed and not to be treated as repo content: later literature-citation edits; docs/intent.md; docs/literature_sweep_2026-10-28.md; results/cloning_question_panel.md; results/video_review_v2.md; video/; all fifth-pair result/example files. BUILD_PLAN.md is pushed and in scope in its own audit part.

Check: arithmetic/factual errors; stale or superseded numbers; inconsistencies; claims outrunning evidence; judge/submission risks. Recompute from the digest. If evidence is not supplied, label the point UNVERIFIABLE rather than calling it false, unless the wording itself is internally inconsistent or universal beyond its stated test.

For every finding: severity (CRITICAL/HIGH/MEDIUM/LOW), category, exact file + heading or quoted phrase, problem with recomputed/conflicting values, recommended correction. Most serious first. No duplicate roots. Maximum 2600 words.


===== PRIMARY PUSHED FILE: NOTICE.md =====
# NOTICE: prior art, attribution, and originality

## This project's own work

All code, documentation, evaluation items, and results in this repository
are original work by Vinay K Ganji Krishna, written during the Meta Global
AI Developer Hackathon (October 26 to November 4, 2026) and released under
the MIT License (see LICENSE). No third-party code is included in this
repository, and no code was copied from any of the projects cited below.

## Published methods this work builds on

Compressing the difference between a base model and its fine-tune is an
established research area. The methods below are published prior art. We
read the papers and take the ideas; the implementations here are ours,
written from scratch for this event.

- **BitDelta** (Liu et al., NeurIPS 2024, arXiv:2402.10193): 1-bit
  quantization of the fine-tuning delta, storing the sign of each delta
  weight with one high-precision scale per matrix. Our baseline in
  `examples/bitdelta_baseline.py` implements the paper's initialization
  exactly (sign times the per-matrix mean absolute value, no further
  training), and `results/bitdelta_baseline.json` reports how it scores
  next to our format.
- **Delta-CoMe** (Ping et al., NeurIPS 2024, arXiv:2406.08903):
  training-free delta compression that mixes precisions across singular
  vectors from an SVD of the delta, instead of treating every component
  the same. The lesson that where the bytes go matters more than how
  many there are is one this project builds on.
- **LittleBit** (Lee et al., arXiv:2506.13771): extreme low-bit
  quantization using a factored, dual residual form. Prior work from
  the author's earlier Fraction Compressor versions (v0.1 to v0.3, in
  the original repository) explored this direction; the factored form
  in `src/factored.py` is this event's own implementation.

## What is ours

Naming a published method and reporting its published results for
comparison is standard research practice. The contributions claimed by
this repository are not the 1-bit delta format itself. They are:

- the in-loop recipe search and judging: Muse Spark proposes the
  per-layer rank allocation (the recipe) and later judges the results,
  with every verdict required to cite the exact result file it rests on;
- the forced-multiply runtime in `src/factored.py`, which applies the
  delta as two small multiplies and never rebuilds the full matrix, so
  patches swap in and out of a running base model live;
- the first-token gate diagnosis (skills whose first generated token
  decides success transfer weakly through any small patch) together
  with its force-start control test, which separates "the skill is
  missing" from "the start decision is missing";
- the verification harness: every headline number is recomputed by
  scripts, cross-checked by independent models, and a sample picked
  with true quantum random numbers from IBM Quantum hardware was
  re-audited end to end.

## Models

This repository distributes no model weights and no tokenizer files.
Experiments download models separately from Hugging Face, under each
model's own license: Qwen/Qwen2.5-0.5B and Qwen2.5-0.5B-Instruct
(Apache 2.0), HuggingFaceTB/SmolLM2-360M and SmolLM2-360M-Instruct
(Apache 2.0), meta-llama/Llama-3.2-1B and Llama-3.2-1B-Instruct
(Llama 3.2 Community License).

===== END NOTICE.md =====

===== PRIMARY PUSHED FILE: docs/why-it-matters.md =====
# Why it matters

A fine-tuned model is a base model plus a patch: everything training changed, and normally that patch is nearly as big as the model itself. This tool squeezes an existing fine-tune's patch into a file of about 19 MB instead of 1 GB, at 1 bit per weight. One base can then carry many behaviors, one small file each.

## Three uses

- **Many behaviors, one model.** Fifty fine-tunes the normal way means fifty full models; as patches, fifty small files on one base.
- **Live switching.** A patch swaps in or out in a tenth of a second while the base keeps running, changing behavior mid-conversation.
- **Cheap to move.** A 19 MB file can be sent, downloaded on a slow link, or carried on a small device. A 1 GB model often cannot be.

## How it differs from a download or a repo

Downloading a fine-tune gives you the whole model, full size. Small adapters like LoRA exist, but an adapter is a new add-on trained for one task. This tool starts from a fine-tune that exists and converts it, with no retraining: point the script at a base and its fine-tune, and it writes the patch and measures how much behavior the patch carries.

Two honest costs: making a patch needs both full models once, and running one needs the base in memory. The saving is in storing and moving behaviors.

## What bound it breaks, and what it does not

The usual assumption is that at 1 bit per weight, nothing useful survives. Done the plain way, that holds: on Llama 3.2 1B, spreading the budget evenly scored below the base model itself, worse than no patch. Spending the same bytes where they matter kept a real share: 15.9% of the gap closed there, 23.2% on the Qwen pair. So one bound breaks: useful behavior survives smart squeezing.

The other bound stands: a tiny patch is not the full fine-tune. Most of the gap stays behind. Patches are for cheap switching and sharing, not replacements.

Against the simplest rival, a plain 1-bit delta (the BitDelta initialization), the honest picture is two budgets, not one: on the Qwen pair a plain 1-bit delta cannot be smaller than about 62 MB, so at our 19 MB size it does not exist, while at its own 62 MB floor it closes more of the gap than our format does at the same price (43.6% against 38.5%). Our format's win is reach: it works at sizes the plain format cannot reach. Full record: `results/bitdelta_baseline.json`.

## The known limit

One kind of skill transfers weakly: skills decided by the first token, like "start the JSON or stop." On a JSON-extraction fine-tune, the full fine-tune starts on 9 of 10 prompts, the base on 0, the patch on 1. Measured at the first token, the patch moves the model halfway toward starting (base -6.33, patch -1.29, full fine-tune +4.60) but usually does not cross. On the one prompt where it does start, the extraction is fully correct.

The author's intuition: the knowledge is there, it just needs to know to start. The control test has now been run, and it mostly backs him: force the fine-tune's first token and the plain base completes 7 of 10 cleanly (8 of 10 counting a partial), so in this test most of the extraction skill was already in the base, and what the fine-tune mainly installs is the decision to start. The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own unforced score. That is one clean more than the forced base, which at 10 prompts is within sampling noise, so the honest reading is: the gate is the main story, and any edge beyond the trigger is small at most. Full records: `results/skill_demo_forced.json`; the earlier debate is in `results/why_debate.md`, and the five-way validation of this test (script recomputation, Muse Spark, Muse Glimmer, Gemini, and Muse Spark Open via Baseten and via Fireworks) is in the `results/` files with `validation_forced` in their names.

===== END docs/why-it-matters.md =====

===== EVIDENCE DIGEST =====
# Evidence digest computed from the pushed result JSON files at commit 3933fae

## results/alien_sweep_heldout96.json
- base: mean_target_logprob=-11.1497780625, accuracy=0.031250
- full_delta: mean_target_logprob=-8.5424662354, accuracy=0.166667
- full_delta_fp16_bytes=987922432
- ranking: mlp_behemoth: mean=-10.45627380592698, gap_closed=0.2659843941106181 (26.5984%), accuracy=0.020833333333333332, bytes=21719776
- ranking: mlp_behemoth_lite: mean=-10.54508293414888, gap_closed=0.2319228264458408 (23.1923%), accuracy=0.010416666666666666, bytes=19358176
- ranking: uniform_rank32: mean=-11.095640657042859, gap_closed=0.020763686533300157 (2.0764%), accuracy=0.010416666666666666, bytes=19434496
- verdict.byte_fair_headline_question=does mlp_behemoth_lite still beat uniform_rank32 on the combined 96 fresh items?
- verdict.lite_beats_uniform_on_combined96=True
- verdict.lite_gap_closed_combined96=0.2319228264458408
- verdict.uniform_gap_closed_combined96=0.020763686533300157
- verdict.lite_within_uniform_budget=True
- verdict.subset_consistency.heldout24.lite_gap_closed=0.0947229129097021
- verdict.subset_consistency.heldout24.uniform_gap_closed=0.01564243038524459
- verdict.subset_consistency.heldout24.lite_beats_uniform=True
- verdict.subset_consistency.heldout72_new.lite_gap_closed=0.303801464368062
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=0.023446697818697487
- verdict.subset_consistency.heldout72_new.lite_beats_uniform=True
- verdict.mlp_behemoth_reference_only.note=mlp_behemoth is BYTE-UNFAIR (over the uniform budget) and is reported as a reference only, never as the headline.
- verdict.mlp_behemoth_reference_only.real_shape_bytes=21719776
- verdict.mlp_behemoth_reference_only.uniform_real_shape_bytes=19434496
- verdict.mlp_behemoth_reference_only.over_bytes=2285280
- verdict.mlp_behemoth_reference_only.over_pct=11.8
- verdict.mlp_behemoth_reference_only.combined96_gap_closed=0.2659843941106181
- verdict.mlp_behemoth_reference_only.combined96_factored_mean_target_logprob=-10.45627380592698

## results/second_pair_heldout96.json
- base: mean_target_logprob=-12.8785653857, accuracy=0.010417
- full_delta: mean_target_logprob=-8.4321585239, accuracy=0.093750
- full_delta_fp16_bytes=723517440
- ranking: o-down supercharge: mean=-8.03994579872309, gap_closed=1.0882089150651426 (108.8209%), accuracy=0.09375, bytes=27660288
- ranking: o-down-rebalanced: mean=-8.072964749082066, gap_closed=1.080782930132702 (108.0783%), accuracy=0.08333333333333333, bytes=19683328
- ranking: uniform_rank32: mean=-8.366280457949834, gap_closed=1.0148160229227625 (101.4816%), accuracy=0.08333333333333333, bytes=19705856
- verdict.stage2_winner=o-down supercharge
- verdict.byte_fair_contender=o-down-rebalanced
- verdict.byte_fair_headline_question=does o-down-rebalanced beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=1.080782930132702
- verdict.uniform_gap_closed_combined96=1.0148160229227625
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=27660288
- verdict.winner_byte_status.uniform_real_shape_bytes=19705856
- verdict.winner_byte_status.winner_byte_unfair=True
- verdict.winner_byte_status.winner_combined96_gap_closed=1.0882089150651426
- verdict.subset_consistency.heldout24.contender_gap_closed=1.037137028575536
- verdict.subset_consistency.heldout24.uniform_gap_closed=0.9703361598361151
- verdict.subset_consistency.heldout24.contender_beats_uniform=True
- verdict.subset_consistency.heldout72_new.contender_gap_closed=1.0979379349340161
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=1.0322988159821247
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## results/third_pair_heldout96.json
- base: mean_target_logprob=-13.7178328094, accuracy=0.010417
- full_delta: mean_target_logprob=-7.3867130269, accuracy=0.218750
- full_delta_fp16_bytes=2471493632
- ranking: no_embed_mlp_spread: mean=-12.12275284734357, gap_closed=0.25194278687724053 (25.1943%), accuracy=0.03125, bytes=34690048
- ranking: no_embed_mlp_spread_balanced: mean=-12.714218663974016, gap_closed=0.15852079567397595 (15.8521%), accuracy=0.020833333333333332, bytes=24515584
- ranking: uniform_rank32: mean=-14.20128408199294, gap_closed=-0.07636110027783072 (-7.6361%), accuracy=0.0, bytes=25143296
- verdict.stage2_winner=no_embed_mlp_spread
- verdict.byte_fair_contender=no_embed_mlp_spread_balanced
- verdict.byte_fair_headline_question=does no_embed_mlp_spread_balanced beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=0.15852079567397595
- verdict.uniform_gap_closed_combined96=-0.07636110027783072
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=34690048
- verdict.winner_byte_status.uniform_real_shape_bytes=25143296
- verdict.winner_byte_status.winner_byte_unfair=True
- verdict.winner_byte_status.winner_combined96_gap_closed=0.25194278687724053
- verdict.subset_consistency.heldout24.contender_gap_closed=0.200373434383912
- verdict.subset_consistency.heldout24.uniform_gap_closed=-0.016714667787171608
- verdict.subset_consistency.heldout24.contender_beats_uniform=True
- verdict.subset_consistency.heldout72_new.contender_gap_closed=0.14817956351361586
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=-0.09109894297869517
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## results/fourth_pair_heldout96.json
- base: mean_target_logprob=-12.5841302690, accuracy=0.010417
- full_delta: mean_target_logprob=-7.8097449276, accuracy=0.333333
- full_delta_fp16_bytes=3087138816
- ranking: Down Dominator: mean=-6.343687772752477, gap_closed=1.3070672034171866 (130.7067%), accuracy=0.2604166666666667, bytes=38623232
- ranking: uniform_rank32: mean=-6.478079873557243, gap_closed=1.2789186374354595 (127.8919%), accuracy=0.3229166666666667, bytes=39046144
- verdict.stage2_winner=Down Dominator
- verdict.byte_fair_contender=Down Dominator
- verdict.byte_fair_headline_question=does Down Dominator beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=1.3070672034171866
- verdict.uniform_gap_closed_combined96=1.2789186374354595
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=38623232
- verdict.winner_byte_status.uniform_real_shape_bytes=39046144
- verdict.winner_byte_status.winner_byte_unfair=False
- verdict.winner_byte_status.winner_combined96_gap_closed=1.3070672034171866
- verdict.subset_consistency.heldout24.contender_gap_closed=1.1242514732201125
- verdict.subset_consistency.heldout24.uniform_gap_closed=1.152286379770239
- verdict.subset_consistency.heldout24.contender_beats_uniform=False
- verdict.subset_consistency.heldout72_new.contender_gap_closed=1.3791549665115759
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=1.3288521753254294
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## Independent arithmetic spot calculations
- Qwen pair full/uniform ratio = 50.833447; full/lite ratio = 51.033859.
- Qwen 1.5B full/Down Dominator ratio = 79.929583; full/uniform ratio = 79.063859.
- One-layer ratio using 8,388,608 bytes / 147,456 bytes = 56.888889.
- Qwen pair all-in effective bits/weight for uniform price = 0.314753 bpw; for lite = 0.313517 bpw.
- BitDelta pricing: {'n_matrices': 169, 'n_weights_169_matrices': 493961216, 'bitdelta_init_price_bytes': 61745828, 'bitdelta_price_formula': 'ceil(total_weights / 8) + 4 bytes x n_matrices (one fp32 scale per matrix)', 'factored_matched_rank': 108, 'factored_matched_price_bytes': 61258816, 'factored_rank_plus_one_price_bytes': 61809136, 'factored_under_by_bytes': 487012}; configs: {'bitdelta_init': {'kind': 'published_baseline_initialization', 'definition': "BitDelta initialization (Liu et al., arXiv:2402.10193): per matrix, delta_hat = sign(delta) * mean(|delta|); one fp32 scale per matrix; NO scale distillation and NO training. The full BitDelta method distills the scales on data afterwards; that step is deliberately not run, and this config must be cited as the initialization, not as BitDelta's final reported quality.", 'mean_target_logprob': -10.012813627503721, 'accuracy_first_token': 0.0625, 'price_bytes': 61745828, 'wall_s': 285.21, 'peak_rss_mb': 3578.4}, 'factored_uniform_rank108': {'kind': 'ours_factored_matched_budget', 'definition': 'factored.quantize_delta at uniform rank 108 on all 169 matrices: the largest uniform rank whose factored.storage_bytes total fits under the plain 1-bit price.', 'mean_target_logprob': -10.146044864550612, 'accuracy_first_token': 0.03125, 'price_bytes': 61258816, 'wall_s': 287.5, 'peak_rss_mb': 3279.4}}.

## results/skill_demo.json
- patch={'built_by': 'examples/make_patch.py', 'rank_mode': 'uniform rank 32', 'storage_bytes': 19434496, 'file_bytes_on_disk': 19801674, 'full_delta_fp16_bytes': 987922432}
- base (no patch): counts={'clean': 0, 'partial': 0, 'failed': 10}
- base + compressed patch (uniform rank 32): counts={'clean': 1, 'partial': 0, 'failed': 9}
- base + full delta (fine-tune weights): counts={'clean': 8, 'partial': 1, 'failed': 1}

## results/skill_demo_forced.json
- unforced_reference={'base (no patch)': {'clean': 0, 'partial': 0, 'failed': 10}, 'base + compressed patch (uniform rank 32)': {'clean': 1, 'partial': 0, 'failed': 9}, 'base + full delta (fine-tune weights)': {'clean': 8, 'partial': 1, 'failed': 1}}
- base, forced start: counts={'clean': 7, 'partial': 1, 'failed': 2}
- base + compressed patch (uniform rank 32), forced start: counts={'clean': 8, 'partial': 1, 'failed': 1}

## results/skill_demo_ranks.json
- test=skill-transfer size test: does a larger uniform patch move the first-token gate?
- skill_pair=Qwen/Qwen2.5-0.5B base + numind/NuExtract-1.5-tiny (MIT) JSON extraction
- prompts=the same 10 screening prompts and the same judge as results/skill_demo.json (clean = parses as JSON, keys match template, every expected value present)
- decoding=greedy, max 64 new tokens, raw NuExtract prompt format
- reference_counts: {'note': 'both reruns (rank 64 and rank 128 runs) reproduced these two configs exactly: base 0/0/10, full delta 8 clean / 1 partial / 1 failed'}
- conclusion=Clean transfers: rank 32 = 1/10 at 19,434,496 B; rank 64 = 2/10 at 37,044,736 B; rank 128 = 2/10 at 72,265,216 B. Quadrupling the patch buys one extra prompt and then nothing: at these sizes the first-token gate barely moves with uniform size.
- verify=rank 64 and rank 128 patches both passed make_patch --verify (worst factored-vs-dense diff 4.3e-16 / 3.1e-16; file-vs-fresh rel diff 5.0e-04 / 3.3e-04, the designed fp16 V rounding). Build peaks: 4,754 MB both; verify peaks 4,917 / 5,067 MB.

## results/skill_demo_recipe.json
- test=allocation test: same bytes (19,434,496 B budget), smarter placement vs uniform rank 32
- skill_pair=Qwen/Qwen2.5-0.5B base + numind/NuExtract-1.5-tiny (MIT) JSON extraction
- recipe_generation: {'provider': 'baseten', 'model': 'meta-models/muse-spark-open-1026', 'max_tokens': 16000, 'budget_bytes': 19434496, 'prompt': 'You are proposing compression recipes for a factored 1-bit weight-delta format. A recipe assigns one integer rank to each layer TYPE; that rank is used for that layer type in all 24 transformer blocks (the embedding is a single matrix). The stored size of one matrix at rank r is priced exactly as:\n\n  bytes(matrix, r) = ceil(rows * r / 8) + 4 * rows + 2 * cols * r\n\nLayers (rows x cols of the delta matrix):\n  embed: delta matrix 151936 x 896, rank may be 0..896\n  attn.q_proj: delta matrix 896 x 896, rank may be 0..896\n  attn.k_proj: delta matrix 128 x 896, rank may be 0..128\n  attn.v_proj: delta matrix 128 x 896, rank may be 0..128\n  attn.o_proj: delta matrix 896 x 896, rank may be 0..896\n  mlp.gate: delta matrix 4864 x 896, rank may be 0..896\n  mlp.up: delta matrix 4864 x 896, rank may be 0..896\n  mlp.down: delta matrix 896 x 4864, rank may be 0..896\n\nThe total size of a recipe is bytes(embed) + 24 * (sum of bytes over the other 7 layer types), and it must be <= 19434496 bytes. That is exactly the cost of the uniform rank-32 recipe on this model; you have the same bytes, spend them differently.\n\nThe model pair is Qwen2.5-0.5B base and NuExtract-1.5-tiny, a fine-tune for structured JSON extraction (read a text and a JSON template, answer with the filled template). The finding you are designing against: this skill is gated by the FIRST generated token. The fine-tune starts the JSON; the plain base emits end-of-text immediately and answers nothing (0 of 10 test prompts). Our uniform rank-32 patch flips that gate on only 1 of 10 prompts (on the 9 others the patched model still stops immediately), even though the one extraction it does start is fully correct. Bigger uniform patches barely help (rank 64 and rank 128 each flip 2 of 10). So placement, not size, is the open question. Weigh protecting the embedding (it feeds every token position and, with tied weights, the output head) and the output-side layers (attn.o_proj, mlp.down) that shape the final logits, if you judge that is where the start-vs-stop decision lives.\n\nPropose exactly 5 recipes, ordered best-first: put the recipe you recommend most first. Make them genuinely different from each other and from uniform: uneven allocations are the point. Every recipe must include every layer name exactly once in its "ranks" object, with an integer rank (0 is allowed and means that layer type\'s delta is dropped).\n\nReply with ONLY a JSON object, no markdown fences, no commentary, in exactly this shape:\n{"recipes": [{"name": "<short name>", "reason": "<one sentence>", "ranks": {"embed": 0, "attn.q_proj": 0, "attn.k_proj": 0, "attn.v_proj": 0, "attn.o_proj": 0, "mlp.gate": 0, "mlp.up": 0, "mlp.down": 0}}]}\nReplace the zeros with your ranks. Check your arithmetic: each recipe\'s total (embed once + 24 blocks) must be <= 19434496 bytes.'}
- chosen_recipe: {'name': 'Gatekeeper Embed+O', 'reason': 'Maximizes the tied embed and cheap-to-expensive output ratio by pushing embed to 382 and o_proj to 64 with minimal down to flip the first-token EOS vs JSON gate.'}
- chosen_recipe_price_bytes=19434400
- patch_file_bytes_on_disk=18796330
- verify: {'result': 'PASS'}
- demo_run: {'config_label': 'base + compressed patch (recipe Gatekeeper Embed+O)'}
- first_token_margins: {'measure': 'first-token logprob margin', 'definition': "margin = logprob(fine-tune's actual first generated token) - logprob(end-of-text 151643) at the first generation position, natural log; positive means the gate is open (starting the JSON beats stopping)", 'peak_rss_mb': 2354.3}
- conclusion=Placement did not beat size at equal bytes; it did worse. The Spark recipe's radical reallocation (embed 382, mlp.gate/up dropped to 0) opened 0 of 10 gates and its mean first-token margin (-4.14) is far below uniform rank 32 (-1.29). The gate-open counts measured from margins (base 0, rank32 1, recipe 0, full delta 10) exactly match the generation outcomes. Neither bigger uniform patches (2/10 at rank 128) nor this reallocation opens the gate at these budgets; uniform rank 32 is closest per byte.

## results/alien_sweep_heldout.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'byte_matched_variant', 'method', 'shared_configs', 'configs', 'ranking_by_heldout_task_score', 'verdict', 'scripts']
- verdict={"stage2_winner": "mlp_behemoth", "heldout_task_score_metric": "overall mean target logprob of the factored config (Stage 2 convention)", "mlp_behemoth_beats_uniform_on_heldout": true, "mlp_behemoth_confirmed_sweep_winner": true, "byte_fair_comparison": {"variant": "mlp_behemoth_lite", "variant_real_shape_bytes": 19358176, "uniform_real_shape_bytes": 19434496, "variant_within_uniform_budget": true, "variant_beats_uniform_on_heldout": true, "variant_gap_closed_overall": 0.0947229129097021, "uniform_gap_closed_overall": 0.01564243038524459}, "mlp_behemoth_byte_caveat": {"mlp_behemoth_real_shape_bytes": 21719776, "uniform_real_shape_bytes": 19434496, "over_bytes": 2285280, "over_pct": 11.8, "note": "mlp_behemoth's Stage 2 win was not byte-fair; the byte-fair comparison is the variant's row."}}
- configs={"uniform_rank32": {"name": "uniform_rank32", "kind": "human_baseline", "ranks": {"embed": 32, "attn.q_proj": 32, "attn.k_proj": 32, "attn.v_proj": 32, "attn.o_proj": 32, "mlp.gate": 32, "mlp.up": 32, "mlp.down": 32}, "rank0_layer_names": [], "real_shape_bytes": 19434496, "configs": {"base": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.907639310877745}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -11.568273144098278}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -8.098655694460739}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -7.055989094074219}}}, "full_delta": {"overall": {"n": 24, "accuracy": 0.16666666666666666, "mean_target_logprob": -5.322192186566966}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.894272131668772}, "instruction": {"n": 8, "accuracy": 0.5, "mean_target_logprob": -2.096013926456496}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.976290501575629}}}, "factored_delta": {"overall": {"n": 24, "accuracy": 0.0, "mean_target_logprob": -8.851554203835738}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -10.297644800209842}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -9.299502159565801}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.957515651731569}}}}, "gap_closed": {"knowledge": 0.27185025003406543, "instruction": -0.20005299525050946, "math": 1.2355731670467298, "overall": 0.01564243038524459}, "per_item": [{"bucket": "knowledge", "logprob": -12.447284086602247, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -6.0896188013150265, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -15.854590412931671, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -8.147514544844567, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -11.862084444157764, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -7.865520628128349, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -9.294762646619539, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -10.819782837079575, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -9.532485010686338, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.933549728098443, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -11.326082756254166, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -4.2459042955269455, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -11.143121419135793, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -10.478749897546045, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.699891449809007, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -10.036232719469663, "first_token_correct": 0}, {"bucket": "math", "logprob": -5.077893818957592, "first_token_correct": 0}, {"bucket": "math", "logprob": -6.483583546908075, "first_token_correct": 0}, {"bucket": "math", "logprob": -7.500344703423812, "first_token_correct": 0}, {"bucket": "math", "logprob": -4.190430632303273, "first_token_correct": 0}, {"bucket": "math", "logprob": -7.556504310356592, "first_token_correct": 0}, {"bucket": "math", "logprob": -6.033214856384206, "first_token_correct": 0}, {"bucket": "math", "logprob": -8.703859851819542, "first_token_correct": 0}, {"bucket": "math", "logprob": -10.11429349369946, "first_token_correct": 0}], "wall_s": 71.67, "eval_wall_s": 68.15, "peak_rss_mb": 3192.2}, "mlp_behemoth": {"name": "mlp_behemoth", "kind": "spark_recipe_stage2_winner", "ranks": {"embed": 10, "attn.q_proj": 20, "attn.k_proj": 0, "attn.v_proj": 20, "attn.o_proj": 20, "mlp.gate": 45, "mlp.up": 45, "mlp.down": 50}, "rank0_layer_names": ["attn.k_proj"], "real_shape_bytes": 21719776, "configs": {"base": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.907639310877745}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -11.568273144098278}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -8.098655694460739}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -7.055989094074219}}}, "full_delta": {"overall": {"n": 24, "accuracy": 0.16666666666666666, "mean_target_logprob": -5.322192186566966}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.894272131668772}, "instruction": {"n": 8, "accuracy": 0.5, "mean_target_logprob": -2.096013926456496}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.976290501575629}}}, "factored_delta": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.519294854322665}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -10.322385879852932}, "instruction": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -9.11764732690944}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.117851356205622}}}}, "gap_closed": {"knowledge": 0.2665569093656965, "instruction": -0.1697571955534997, "math": 11.771070334588293, "overall": 0.10831130486402876}, "per_item": [{"bucket": "knowledge", "logprob": -11.869581919159009, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -5.260216545256683, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -13.640625505545405, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -11.094353136443697, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -12.667091050882842, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -7.917084875768683, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -9.902145731672057, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -10.22798827409509, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.970952865296688, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -9.583043071480885, "first_token_correct": 0

## results/alien_sweep_stage2.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'method', 'build_validation', 'forward_validation', 'full_delta_fp16_bytes_real_shapes', 'shared_configs', 'recipes', 'human_baseline', 'ablations', 'rank0_analysis', 'ranking_by_task_score', 'api_calls', 'scripts']

## results/fourth_pair_stage2.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'method', 'build_validation', 'forward_validation', 'forward_validation_verdict', 'gap_closed_note', 'full_delta_fp16_bytes_real_shapes', 'shared_configs', 'recipes', 'human_baseline', 'ranking_by_task_score', 'winner', 'api_calls', 'scripts']

## results/hotswap_demo.json (top-level keys and compact verdict/ranking fields)
- keys=['model', 'decoding', 'prompts', 'patch_sizes_bytes', 'swaps', 'configs', 'peak_rss_mb', 'api_calls']
- configs={"base (no patch)": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}\n Comey\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant", "generated_tokens": 48, "seconds": 14.868, "json": {"parseable": false, "exact_keys": false, "exact_values": false}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo. Lauderdale. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital", "generated_tokens": 48, "seconds": 9.24, "contains_expected": true}, "math_percent": {"answer": "Sure, 15 percent of 200 is 30.eousystem\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.\u9c95system\nYou are Qwen, created by Alibaba Cloud.", "generated_tokens": 48, "seconds": 8.784, "contains_expected": true}}, "base + uniform rank-32 factored patch": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}", "generated_tokens": 31, "seconds": 12.162, "json": {"parseable": true, "exact_keys": true, "exact_values": true}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo.", "generated_tokens": 7, "seconds": 4.922, "contains_expected": true}, "math_percent": {"answer": "To find 15% of 200, you can use the following formula:\n\n(15/100) * 200 = 30\n\nSo, 15% of 200", "generated_tokens": 48, "seconds": 9.36, "contains_expected": true}}, "base + mlp_behemoth_lite factored patch": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}", "generated_tokens": 31, "seconds": 12.046, "json": {"parseable": true, "exact_keys": true, "exact_values": true}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo.", "generated_tokens": 7, "seconds": 7.891, "contains_expected": true}, "math_percent": {"answer": "15% of 200 = 30.", "generated_tokens": 13, "seconds": 5.928, "contains_expected": true}}}

===== END EVIDENCE DIGEST =====

===== REFERENCE EXCERPTS FROM PUSHED FILE: README.md (line-numbered selected lines) =====
1: # Fraction Compressor v0.4
3: **One base model. Many tiny patch files. Swap a file, swap the behavior.**
5: What "fraction" means here: not math fractions. A fine-tuned AI model is a base model plus a patch (the weight difference between the two). This tool keeps only a fraction of that patch's information, stored at about 1 bit per weight, in a file small enough to swap in and out live.
7: ![How Fraction Compressor v0.4 works](docs/how-it-works.svg)
9: ## In plain words
11: A fine-tuned model differs from its base model by a patch (the delta). A normal patch is almost as big as the model itself. Fraction Compressor stores that patch in a factored form whose structure is kept as 1-bit signs, priced byte for byte by the code: 0.28 bits per weight for one large layer at rank 32 (the exact price depends on layer size and rank). v0.4 runs it through a factored runtime: two small multiplies, Y = (X U) V^T, without ever rebuilding the full weight matrix. One layer stored the normal way takes 8.4 MB; our rank-32 file takes 144 KB, and swapping patches is just loading a different small file. Compressing a patch is offline work done once with the full delta; the saving is in storage and at run time.
13: ## Do it yourself
15: You need two models: a base model and a fine-tuned version of that same base, in safetensors format.
17: 1. Make a patch from the pair (rank 32 everywhere, or pass a per-layer recipe file with `--recipe` instead of `--rank`):
18:    `python examples/make_patch.py --base <base-model-dir> --finetuned <finetuned-model-dir> --rank 32 --out patch.npz`
19:    The script subtracts the two models layer by layer, squeezes the difference into the factored format, and writes one patch file. It prints the patch's exact byte price next to the full difference at normal precision.
20: 2. Check the patch any time:
21:    `python examples/make_patch.py --verify patch.npz --base <base-model-dir> --finetuned <finetuned-model-dir>`
22: 3. Use it: load the patch together with the base model, as in `examples/hotswap_demo.py`, where patches swap in and out of one running base model live.
24: On the model pair used in this repo's benchmark (Qwen2.5-0.5B base and Instruct), rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller. The full run is saved at `results/make_patch_demo.txt`.
26: ## How this is different
28: - **From memory files and system prompts** (the text files an AI agent reads, like a personality or memory file): those are words the model reads as instructions, they take up prompt space, and a later instruction can override them. A patch here is numbers applied to the model's own weights. The behavior changes in the math itself, uses no prompt space, and cannot be talked away.
29: - **From an adapter (like LoRA):** an adapter is a new add-on trained for one task, usually stored at normal precision. This tool takes a fine-tune that already exists and squeezes the difference between it and its base model into a 1-bit factored file, so an existing fine-tune becomes a small patch you can swap.
30: - **From shrinking a whole model (quantization):** that makes the one model smaller and slightly changes everything it does. This shrinks only the patch, so one base model stays exact and carries many behaviors, one small file each.
34: ## Prior art
36: Compressing a fine-tune's difference is an established research area, and this project builds on published methods, ideas only, no code: BitDelta (1-bit delta compression of fine-tuned models, NeurIPS 2024, arXiv:2402.10193), Delta-CoMe (SVD-based mixed-precision delta compression, NeurIPS 2024, arXiv:2406.08903), and LittleBit (arXiv:2506.13771). All code in this repo is original and was written during the event. What is ours is not the 1-bit format itself: it is the in-loop recipe search and judging by Muse Spark, the forced-multiply runtime, the first-token gate diagnosis with its force-start control, and the verification harness. Full credits: [NOTICE.md](NOTICE.md).
38: ## Benchmark results
40: The benchmark compares three runs on the same questions: the base model alone, the base model with the full patch, and the base model with our compressed patch. The score is how strongly the model backs the correct answer (a log score; higher is better). "Gap closed" is the share of the base-to-full score gap that a compressed patch recovers. One limit applies everywhere below: the share of questions whose first answer token is exactly right stays low for every compressed version (about 1 to 2% on the first pair, about 8 to 9% on the second, 0 to about 3% on the third; the fourth pair is the exception, where the compressed versions reach 26 to 32% against the full patch's own 33.3%), so these are score results, not proof the model solves the tasks.
42: ### Known limit: skills gated by the first token transfer weakly
44: Transfer depends on the skill, and one kind of skill is a weak case for this format. We tested a real one: NuExtract-1.5-tiny (MIT), a fine-tune of the same Qwen base that reads a text and a JSON template and answers with the template filled in. The fine-tune itself passes 9 of 10 test prompts (eight fully clean, one with a single reworded value); the plain base passes 0 of 10, because it stops immediately instead of answering. Our rank-32 patch passes only 1 of 10. The reason is narrow: this skill is decided by the first token the model emits, start the JSON or stop, and the compressed patch usually does not flip that one decision. On the one prompt where it does start, the extraction is fully correct. A control test settles why: force that first token and the plain base completes 7 of 10 cleanly, so in this test most of the skill was already in the base and the fine-tune's main work is the decision to start. The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own score: one clean more than the forced base, which at 10 prompts is within sampling noise, so the gate is the main story and any edge beyond the trigger is small at most. Making the patch bigger barely moves this boundary: a rank-64 patch (37,044,736 bytes) and a rank-128 patch (72,265,216 bytes) each pass 2 of 10. Spending the same bytes differently did worse, not better: a Muse Spark recipe that puts most of the rank-32 budget into the embedding and the attention output layer (19,434,400 bytes, the same budget) passes 0 of 10, and measured directly at the first token, its average start-vs-stop margin sits further from opening the gate than the uniform patch's. Broad behavior transfers much better under the same format: the Instruct patch below closes 23.2% of the score gap on 96 fresh questions, with wins you can see in the live hot-swap demo. So the limit is format-gated, not general. Full records: `results/skill_demo.json`, `results/skill_demo_forced.json`, `results/skill_demo_ranks.json`, `results/skill_demo_recipe.json`, and the consultation behind this wording in `results/skill_limit_consultation.md`.
46: ### First pair: Qwen2.5-0.5B base and Instruct
48: Muse Spark proposed uneven per-layer compression recipes (the Alien Sweep). The search winner, mlp_behemoth, is byte-unfair: at 21,719,776 bytes it spends 11.8% more than the human recipe's budget, so it is named only as the parent. The headline recipe is its byte-fair variant, mlp_behemoth_lite: 19,358,176 bytes, fewer than the human uniform rank-32 recipe's 19,434,496 bytes.
50: The check that matters is fresh questions the search never saw. That set grew from 24 to 96 questions. On all 96, lite closes 23.2% of the gap, against 2.1% for the human recipe. Lite also wins on each half alone: 9.5% vs 1.6% on the original 24 questions, and 30.4% vs 2.3% on the 72 new ones. An early read from the first small fresh set was that the lead might shrink on fresh questions; on the bigger set the lead grew instead, so that worry did not survive. Lite does not win every kind of question: on knowledge questions the human recipe closes more of the gap (7.8% vs 3.7%); lite's lead comes from the instruction and math questions.
52: ### Second pair: SmolLM2-360M base and Instruct
54: The same contest ran on a second, different model pair. The search winner there (o-down supercharge) was byte-unfair too, so the byte-fair winner is its byte-matched variant, o-down-rebalanced: 19,683,328 bytes, inside the human recipe's budget of 19,705,856 bytes. On the same 96 fresh questions it beats the human uniform recipe by 0.293 score points on average, and it wins on both halves of the set separately.
56: One warning that applies to this pair only: every compressed version scores better than the full patch itself, so the gap-closed percentage goes above 100% here. That means the percentage is NOT a share of the fine-tune recovered for this pair. For this pair, the raw score margin (0.293 points) is the honest measure.
58: ### Third pair: Llama 3.2 1B base and Instruct
60: The same contest also ran on Meta's own open weights, Llama 3.2 1B base and Instruct. The search winner, no_embed_mlp_spread, was byte-unfair again: at 34,690,048 bytes it spends 38.0% more than the human recipe's budget of 25,143,296 bytes, so it is named only as the parent. The headline recipe is its byte-fair variant, no_embed_mlp_spread_balanced: 24,515,584 bytes, inside the budget.
62: On the same 96 fresh questions, the byte-fair variant scores -12.714 against the human uniform recipe's -14.201: it closes 15.9% of the gap, while the human recipe closes -7.6%, which is below the base model itself (-13.718), so on this pair the plain human recipe makes the score worse than using no patch at all. The byte-fair variant also wins on each half alone: 20.0% vs -1.7% on the original 24 questions, and 14.8% vs -9.1% on the 72 new ones.
64: Recovery on this pair is weaker than on the other two pairs (15.9% here against 23.2% on the Qwen pair), and first-token accuracy stays low for every co
[EXCERPT TRUNCATED BY LENGTH]
===== END EXCERPTS README.md =====

===== REFERENCE EXCERPTS FROM PUSHED FILE: docs/demo_script.md (line-numbered selected lines) =====
1: # Demo video script: Fraction Compressor v0.4
3: Exactly 3 minutes. One idea on screen at a time. Narration is the text under
4: each NARRATION heading, nothing else is spoken. Total narration: 440 words,
5: about 147 words per minute.
7: ## 0:00-0:25 The product: a fine-tune as a tiny patch file
9: ON SCREEN: Title card: FRACTION COMPRESSOR v0.4. Under it, one line: a
10: fine-tune squeezed into a patch file, about 19 MB instead of about 1 GB.
16: This is Fraction Compressor. It turns a fine-tuned model into one patch
18: the base model and swaps behavior live, in about a tenth of a second.
22: ## 0:25-0:44 Building on an existing idea: what is old, what is new
24: ON SCREEN: Two short lists. Published before: 1-bit delta compression,
25: BitDelta and Delta-CoMe; our earlier compressor work. Built this week:
26: factored runtime; Muse Spark recipes and claim judging; first-token gate
28: github.com/ganjikrishna/fraction-compressor-v0.4.
31: Honesty: one-bit delta compression is a published idea, BitDelta and
32: Delta-CoMe, and our earlier compressor work predates this week. Built
33: fresh this week: the factored runtime, Muse Spark designing recipes in
34: the loop and judging claims against the files, the first-token gate
37: ## 0:44-1:02 The problem: a fine-tune is almost a second model
39: ON SCREEN: Two file sizes side by side: the base model, and the full
40: difference file at 987,922,432 bytes.
43: A fine-tune is a base model plus a patch: the difference between them.
44: That difference alone: nine hundred eighty-eight million bytes, almost
45: the model itself. It keeps a fraction: about nought point three bits per
46: weight, all in. Ten fine-tunes, ten near-full models.
48: ## 1:02-1:21 Do it yourself: clone, quickstart, make a patch
51: 1. `git clone https://github.com/ganjikrishna/fraction-compressor-v0.4`
52: 2. `python3 examples/quickstart.py` and its printed size and error lines.
53: 3. `python3 examples/make_patch.py --base <base-model-dir> --finetuned <finetuned-model-dir> --out patch.npz --rank 32`
54:    and its printed sizes: patch 19,434,496 bytes, full difference
55:    987,922,432 bytes.
58: You can do this yourself. You need two models: a base and its fine-tune.
61: base and writes one file, about nineteen million bytes.
63: ## 1:21-1:48 The demo moment: swap a file, change the behavior
65: ON SCREEN: `python3 examples/hotswap_demo.py` running. First the base model
67: Arrival, 2016, Denis Villeneuve): the right object, then extra rambling
68: text, then the line `JSON SCORE: parseable=False`. Then the swap line:
69: patch loaded live in 0.09s. Then the same prompt again: exactly the object,
74: One base model, loaded once. I ask for strict JSON, a format programs
76: format check. Watch: the patch swaps in, about a tenth of a second.
81: ## 1:48-2:31 The numbers: smaller file, tested on fresh questions
83: ON SCREEN: The size table from the demo (full delta 987,922,432 bytes;
84: patches about 19.4 million bytes, 51x smaller), then the benchmark result
85: lines: 96 fresh questions, gap closed 23.2% vs 2.1%, and the second model
86: pair name, SmolLM2-360M. Then the scale test lines: Qwen2.5-1.5B, Spark
87: recipe 38,623,232 bytes inside the 39,046,144 byte human budget, margin
88: 0.134 nats on 96 fresh questions, patch about 39 MB vs 3,087,138,816 byte
89: full difference, about 80x smaller. Then the baseline lines: at the plain
90: 1-bit floor price of 61,745,828 bytes, plain BitDelta-style init gap
91: closed 43.6% vs factored rank-108 gap closed 38.5% at 61,258,816 bytes;
92: at 19,434,496 bytes no plain 1-bit delta fits, only the factored patch.
95: The patch is fifty-one times smaller: nineteen million bytes against
96: nine hundred eighty-eight million. The measure: how strongly the model
100: and does not count. Same pattern on SmolLM2; on a model three times
102: budget. Honestly: at sixty-two million bytes a one-bit patch closes more
103: gap. Our win is reach: at nineteen million bytes, where no plain one-bit
106: ## 2:31-2:44 Checked, not just claimed
108: ON SCREEN: Two short lines, one at a time: the Muse Spark judging record
109: citing its result files; then the audit line, 41 of 41 checks passed.
112: Then we checked ourselves. Muse Spark judged every headline claim and
113: had to cite the file behind each one. A quantum computer's random
116: ## 2:44-3:00 Close: a chip, not a note
118: ON SCREEN: The base model with the small patch file next to it. End card:
122: This is not a memory file. A memory file is a note the model reads; this
123: patch is a chip swapped inside the machine, numbers that change the
124: model's math. Fine-tunes to carry and swap: one base, many behaviors.
128: ## Production notes
132:   hotswap_demo run. Use the actual output; the transcript of record is
133:   results/hotswap_demo_transcript.txt.
138: - Cut to exactly 3:00. If a block runs long, trim screen pauses, not
140: - The full caveats (score is not task solving, first-token accuracy stays
141:   low, the knowledge-bucket result, the second pair's percentage warning)
===== END EXCERPTS docs/demo_script.md =====

===== REFERENCE EXCERPTS FROM PUSHED FILE: BUILD_PLAN.md (line-numbered selected lines) =====
1: # Build plan, Meta Global AI Developer Hackathon (Oct 26 to Nov 4, 2026)
4: - This repo holds only work done during the event. Prior work (v0.1 to v0.3, Signet) stays in github.com/ganjikrishna/fraction-compressor and is cited, not copied.
5: - The 3-minute demo video opens with one line stating what was pre-existing and what was built this week.
6: - Deadline: Wed Nov 4, 9:00 PM ET, via the Cerebral Valley submission portal.
8: ## Scope
10: 1. Factored-multiply runtime for 1-bit compressed deltas: Y = (X U) V^T, never materialize W. Memory read per token is the headline metric.
11: 2. End-to-end task-accuracy benchmark on the Signet probe sets (knowledge, instruction, math): base vs base + full delta vs base + sign/factored delta, so the compressed path is scored on task answers, not only weight error.
12: 3. Meta model in the loop: Muse Spark (Meta Model API) runs the same probe sets as a hosted reference, and Muse Spark Open is the planned open-weight candidate if time allows.
13: 4. Stretch, only if 1 to 3 are done: System Instruction Hot-Swap Test (base vs full delta vs sign delta on strict JSON-format prompts, scored by parseability).
14: 5. Alien Sweep: a wide, automated search over compression recipes that a human would not normally pick, filtered in two stages and verified by rerun (full protocol in its own section below). This replaces the planned human rank sweep; it does not add a separate build.
15: 6. Nov 4 reserved for the 3-minute demo video and the submission writeup.
16: 7. AirLLM-style streaming scale test (unparked by Vinay, Oct 28; active): the full Alien Sweep protocol on a fifth pair, Qwen2.5-7B base/Instruct, run on Flash with layer-by-layer streaming in our own NumPy runtime (the AirLLM concept, Apache 2.0; code ours), because a 7B model can never be held whole in Flash's 11 GB RAM. Includes a streamed generation demo: the winning byte-fair patch applied block by block as each block loads, updating a model that is never whole in memory. Vinay's Oct 28 decision: the run's scripts and results are saved locally; whether the 7B results enter the README and submission is decided after he reviews the outcome.
18: ## Demo video plan (approved by Vinay, Oct 26)
22: - Exactly 3 minutes. Opens with the required line stating what was pre-existing and what was built this week. Shape: 0:00 opening + problem; 0:30 the hot-swap moment; 1:30 benchmark numbers, including one Alien Sweep line (recipes tried, winner, held out result); 2:15 Muse Spark judging + quantum audit, one line each; 2:45 close.
23: - Rough cut early (as soon as the hot-swap demo runs) for Vinay to watch and react; final cut Nov 2-3 once the real numbers are in; Nov 4 reserved for submission only. Vinay approves the final cut before anything is posted.
24: - Simplicity rule (Vinay, Oct 27): keep the video as simple as possible. Plain words, no jargon without a one-line explanation, one idea at a time on screen. A newcomer watching once should understand what the tool does AND be able to pick it up and use it: the video shows the actual quickstart path (clone, run the quickstart, swap a patch file) in real steps, not just results.
25: - One script line near the close answers the question people will ask (Vinay, Oct 27): how is this different from a memory or personality file and other tools on the market? Plain version: a memory file is words the model reads; our patch is numbers that change the model's math. The README carries the fuller comparison (memory/prompts, adapters, whole-model shrinking).
26: - Do-it-yourself requirement (Vinay, Oct 27, after Agents 101): the video and the README must explain how the patch works AND how a viewer can do it themselves, as plain steps: take a base model and a fine-tuned version of it, run the compressor on the difference to get a small patch file, then load the patch with the base model to get the fine-tuned behavior. If the repo lacks a single clean script for that path, build one (examples/make_patch.py style) so the steps shown are the steps that actually run.
28: ## Working notes
30: - Muse Spark reasons before answering and reasoning tokens count against max_tokens; use generous caps in benchmark calls.
31: - Log every real Muse Spark call the benchmark makes (prompt, token counts, verdict) into results/ as it happens, so the Meta tooling use is evidenced in the repo, not just planned. (Muse Spark's own suggestion in its Oct 26 repo review. Soft budget from Vinay: keep Meta API use under the $100 alert level of the $150 credits where possible.)
32: - Agents 101 takeaways applied (Oct 27, Vinay: use what is needed): (1) Verification leads the submission and demo story: Meta's own session framed agent output as unverified until defensive checks confirm it, "as important as building the agentic loop", so our rerun + Spark + Gemini cross-checks are presented as a headline feature, not a footnote. (2) Spark judging verdicts cite the exact result files they are based on (grounding advice from the session). (3) In the submission's Meta-products field, describe the benchmark harness honestly in the session's terms: a harness loop (plan, run tools, check results) with Muse Spark inside it.
33: - Validation rule (Vinay, Oct 26): key results are cross-validated by Muse Spark AND Gemini, on top of the script reruns that produce them. If the two disagree, the disagreement is reported and investigated, never averaged away.
34: - Model scope (settled Oct 26 night, Vinay: do what is best): Spark family only. Spark 1.3 via the Meta Model API, Spark Open via Baseten, Glimmer as the Flash reference. The other Meta models (Wonder, Image, Voice Transcribe, SAM 3.1) do not fit a compression tool, so they will not be forced in just to name more models. Depth of Spark use is the tooling story.
35: - Credit order and tracking (Vinay, Oct 26, 10:23 PM): the Baseten credits may not be available after the hackathon, so Baseten carries the heavy lifting first while it lasts: bulk benchmark runs, sweeps, and repeated evaluations on Muse Spark Open. The Meta Model API is used as needed for task generation, judging, and validation. Every Baseten and Meta call is tracked in results/ with provider, model, time, purpose, and token counts, so the usage totals can be shared with the organizers in the submission and checked against the credit balances.
36: - Models and weights are never committed (see .gitignore); data/ holds local downloads only.
37: - Glimmer's new wording limit (Oct 27, after the strengthening results): when the compressed versions outscore the full patch itself (as on the SmolLM2 pair), the gap-closed percentage passes 100% and must not be presented as a fraction of the fine-tune recovered. Prose about that pair must state plainly that the percentage is not a recovery fraction there and that the raw score margin is the honest measure. Record: results/glimmer_reference_addendum.md.
38: - Fresh-question test size (Vinay, Oct 27): the fresh held-out test stays at 96 questions. Expanding it further was considered and declined; 96 is the validated set the headline numbers rest on.
39: - Skill-transfer limit disclosure (Vinay, Oct 27): the NuExtract gated-skill limit is disclosed upfront, not buried: a "Known limit" note opens the README's Benchmark results section. Vinay's direction was to check with Spark and Glimmer and do what is best; both validators independently recommended (c) disclose upfront AND test larger patches (rank 64/128). The size test ran the same day: 1/10 clean at rank 32, 2/10 at rank 64 and rank 128, so size barely moves this boundary. Records: results/skill_limit_consultation.md, results/skill_demo.json, results/skill_demo_ranks.json.
40: - Force-start control test (Oct 28, Vinay's go-ahead): settles the question Muse Spark raised in the why-it-matters debate. Forcing the fine-tune's own first token on the same 10 NuExtract prompts takes the plain base from 0/10 to 7 clean + 1 partial, so most of the extraction skill was already in the base and the fine-tune's main work is the decision to start. The rank-32 patch under the same forced start scores 8 clean + 1 partial, matching the full fine-tune's own unforced score: a small real edge beyond the trigger (it cleans the two prompts the forced base still fails, and loses one the forced base cleans), but the gate is the dominant term. Limit wording in README and docs/why-it-matters.md updated to the settled version. Records: results/skill_demo_forced.json, results/skill_demo_forced_transcript.txt, examples/skill_demo_forced.py.
41: - Scale test, fourth pair (Oct 28, Vinay: use the expiring compute): the full Alien Sweep protocol on Qwen2.5-1.5B base/Instruct (Apache 2.0, non-gated; 197 delta matrices, tied embeddings), answering the fresh-eyes GPT-OSS attack "does any of this survive above 1B?" (results/fresh_perspective.md). One change from Phases 1-3: recipes were generated against the real-shape budget directly (uniform rank 32 = 39,046,144 bytes), so all 5 Spark recipes priced byte-fair from the start and the Stage 2 winner, Down Dominator (38,623,232 bytes; mlp.gate/up dropped to 0, mlp.down 45, attn.o_proj 64), needed no byte-matched variant. Combined-96 result: Down Dominator -6.344 vs uniform -6.478 (raw margin about 0.134 nats; base -12.584, full delta -7.810), but the win is subset-mixed (uniform wins heldout24, Down Dominator wins heldout72_new) and uniform's first-token accuracy is higher (32.3% vs 26.0%). Every factored config outscores the full delta itself on this pair, so gap_closed exceeds 1.0 (1.307 vs 1.279) and is not a recovery fraction here (same pattern and wording rule as pair 2). Honest scale answer: the format and contest still work at 1.5B (about 79x smaller than the 3,087,138,816-byte full delta), but the recipe's edge over uniform narrows from decisive at 0.5B to narrow and subset-dependent at 1.5B. Validation: script recomputation 61/61 gap_closed values, zero mismatches; Muse Spark judging 5/5 SUPPORTED (
[EXCERPT TRUNCATED BY LENGTH]
===== END EXCERPTS BUILD_PLAN.md =====
```

### Prompt C: demo script + BUILD_PLAN audit

```text
You are Muse Glimmer, strict independent auditor. Reason efficiently and report FINDINGS ONLY. Do not narrate a claim-by-claim review and do not list supported claims except a maximum of three clean-area bullets at the end.

Audit target: docs/demo_script.md and BUILD_PLAN.md as primary documents
Repository state: ganjikrishna/fraction-compressor-v0.4 at pushed head 3933fae16f5e1673cac38a000533a35fb7b0ecda.
The PRIMARY documents are exact pushed versions. The evidence digest was computed from pushed result JSON at the same head. Reference excerpts are exact lines from other pushed documents, supplied only for cross-document consistency.
Excluded local-only material, not pushed and not to be treated as repo content: later literature-citation edits; docs/intent.md; docs/literature_sweep_2026-10-28.md; results/cloning_question_panel.md; results/video_review_v2.md; video/; all fifth-pair result/example files. BUILD_PLAN.md is pushed and in scope in its own audit part.

Check: arithmetic/factual errors; stale or superseded numbers; inconsistencies; claims outrunning evidence; judge/submission risks. Recompute from the digest. If evidence is not supplied, label the point UNVERIFIABLE rather than calling it false, unless the wording itself is internally inconsistent or universal beyond its stated test.

For every finding: severity (CRITICAL/HIGH/MEDIUM/LOW), category, exact file + heading or quoted phrase, problem with recomputed/conflicting values, recommended correction. Most serious first. No duplicate roots. Maximum 2600 words.


===== PRIMARY PUSHED FILE: docs/demo_script.md =====
# Demo video script: Fraction Compressor v0.4

Exactly 3 minutes. One idea on screen at a time. Narration is the text under
each NARRATION heading, nothing else is spoken. Total narration: 440 words,
about 147 words per minute.

## 0:00-0:25 The product: a fine-tune as a tiny patch file

ON SCREEN: Title card: FRACTION COMPRESSOR v0.4. Under it, one line: a
fine-tune squeezed into a patch file, about 19 MB instead of about 1 GB.
Then the use cases, one at a time: many fine-tunes on one base, no full
copies stored; send a fine-tune as a small file; switch behavior
instantly; run on small machines.

NARRATION:
This is Fraction Compressor. It turns a fine-tuned model into one patch
file: about nineteen megabytes instead of about a gigabyte. It plugs into
the base model and swaps behavior live, in about a tenth of a second.
One base carries many fine-tunes, no full copies stored. Send a fine-tune
as a small file. Switch behavior instantly. Run on small machines.

## 0:25-0:44 Building on an existing idea: what is old, what is new

ON SCREEN: Two short lists. Published before: 1-bit delta compression,
BitDelta and Delta-CoMe; our earlier compressor work. Built this week:
factored runtime; Muse Spark recipes and claim judging; first-token gate
finding; verification harness. Repo address at the bottom:
github.com/ganjikrishna/fraction-compressor-v0.4.

NARRATION:
Honesty: one-bit delta compression is a published idea, BitDelta and
Delta-CoMe, and our earlier compressor work predates this week. Built
fresh this week: the factored runtime, Muse Spark designing recipes in
the loop and judging claims against the files, the first-token gate
finding, and the verification harness.

## 0:44-1:02 The problem: a fine-tune is almost a second model

ON SCREEN: Two file sizes side by side: the base model, and the full
difference file at 987,922,432 bytes.

NARRATION:
A fine-tune is a base model plus a patch: the difference between them.
That difference alone: nine hundred eighty-eight million bytes, almost
the model itself. It keeps a fraction: about nought point three bits per
weight, all in. Ten fine-tunes, ten near-full models.

## 1:02-1:21 Do it yourself: clone, quickstart, make a patch

ON SCREEN, in real steps, typed in a terminal:
1. `git clone https://github.com/ganjikrishna/fraction-compressor-v0.4`
2. `python3 examples/quickstart.py` and its printed size and error lines.
3. `python3 examples/make_patch.py --base <base-model-dir> --finetuned <finetuned-model-dir> --out patch.npz --rank 32`
   and its printed sizes: patch 19,434,496 bytes, full difference
   987,922,432 bytes.

NARRATION:
You can do this yourself. You need two models: a base and its fine-tune.
Clone the repo. Run the quickstart: it squeezes a sample patch, printing
size and error. Run the patch maker: it subtracts the fine-tune from its
base and writes one file, about nineteen million bytes.

## 1:21-1:48 The demo moment: swap a file, change the behavior

ON SCREEN: `python3 examples/hotswap_demo.py` running. First the base model
answers the strict JSON prompt (the "Return ONLY a JSON object" prompt for
Arrival, 2016, Denis Villeneuve): the right object, then extra rambling
text, then the line `JSON SCORE: parseable=False`. Then the swap line:
patch loaded live in 0.09s. Then the same prompt again: exactly the object,
and `JSON SCORE: parseable=True`. Then the capital of Japan answers:
base loops on a wrong city, patched answers one clean line.

NARRATION:
One base model, loaded once. I ask for strict JSON, a format programs
can read. The base writes the right object, then rambles on, failing the
format check. Watch: the patch swaps in, about a tenth of a second.
Same question again: exactly the object, check passed. Same patch, new
question: the capital of Japan. Base repeats a wrong city; the patch,
one clean line.

## 1:48-2:31 The numbers: smaller file, tested on fresh questions

ON SCREEN: The size table from the demo (full delta 987,922,432 bytes;
patches about 19.4 million bytes, 51x smaller), then the benchmark result
lines: 96 fresh questions, gap closed 23.2% vs 2.1%, and the second model
pair name, SmolLM2-360M. Then the scale test lines: Qwen2.5-1.5B, Spark
recipe 38,623,232 bytes inside the 39,046,144 byte human budget, margin
0.134 nats on 96 fresh questions, patch about 39 MB vs 3,087,138,816 byte
full difference, about 80x smaller. Then the baseline lines: at the plain
1-bit floor price of 61,745,828 bytes, plain BitDelta-style init gap
closed 43.6% vs factored rank-108 gap closed 38.5% at 61,258,816 bytes;
at 19,434,496 bytes no plain 1-bit delta fits, only the factored patch.

NARRATION:
The patch is fifty-one times smaller: nineteen million bytes against
nine hundred eighty-eight million. The measure: how strongly the model
backs the answer. On ninety-six questions, Spark's recipe at the human
budget closes twenty-three point two percent of the gap; the human
recipe, two point one. Winner: mlp_behemoth_lite; its parent overspent
and does not count. Same pattern on SmolLM2; on a model three times
bigger, Spark's recipe won by nought point one three four nats, inside
budget. Honestly: at sixty-two million bytes a one-bit patch closes more
gap. Our win is reach: at nineteen million bytes, where no plain one-bit
patch fits, ours works.

## 2:31-2:44 Checked, not just claimed

ON SCREEN: Two short lines, one at a time: the Muse Spark judging record
citing its result files; then the audit line, 41 of 41 checks passed.

NARRATION:
Then we checked ourselves. Muse Spark judged every headline claim and
had to cite the file behind each one. A quantum computer's random
numbers picked the audit sample: all forty-one audit checks passed.

## 2:44-3:00 Close: a chip, not a note

ON SCREEN: The base model with the small patch file next to it. End card:
repo address.

NARRATION:
This is not a memory file. A memory file is a note the model reads; this
patch is a chip swapped inside the machine, numbers that change the
model's math. Fine-tunes to carry and swap: one base, many behaviors.

---

## Production notes

- Screen recording on the Muse VM of the real runs, in this order:
  repo page, terminal clone and quickstart, make_patch run, then the
  hotswap_demo run. Use the actual output; the transcript of record is
  results/hotswap_demo_transcript.txt.
- Narration recorded after the picture cut, with an AI voice, mixed over
  the recording with ffmpeg. Exactly one audio stream (narration only).
- No burned-in subtitles. Titles and file sizes appear as part of the
  terminal output itself, not as overlays.
- Cut to exactly 3:00. If a block runs long, trim screen pauses, not
  narration words.
- The full caveats (score is not task solving, first-token accuracy stays
  low, the knowledge-bucket result, the second pair's percentage warning)
  live in the README's Benchmark results section; the video states the
  measure honestly in the numbers block and does not claim accuracy gains.

===== END docs/demo_script.md =====

===== PRIMARY PUSHED FILE: BUILD_PLAN.md =====
# Build plan, Meta Global AI Developer Hackathon (Oct 26 to Nov 4, 2026)

Submission rules honored here:
- This repo holds only work done during the event. Prior work (v0.1 to v0.3, Signet) stays in github.com/ganjikrishna/fraction-compressor and is cited, not copied.
- The 3-minute demo video opens with one line stating what was pre-existing and what was built this week.
- Deadline: Wed Nov 4, 9:00 PM ET, via the Cerebral Valley submission portal.

## Scope

1. Factored-multiply runtime for 1-bit compressed deltas: Y = (X U) V^T, never materialize W. Memory read per token is the headline metric.
2. End-to-end task-accuracy benchmark on the Signet probe sets (knowledge, instruction, math): base vs base + full delta vs base + sign/factored delta, so the compressed path is scored on task answers, not only weight error.
3. Meta model in the loop: Muse Spark (Meta Model API) runs the same probe sets as a hosted reference, and Muse Spark Open is the planned open-weight candidate if time allows.
4. Stretch, only if 1 to 3 are done: System Instruction Hot-Swap Test (base vs full delta vs sign delta on strict JSON-format prompts, scored by parseability).
5. Alien Sweep: a wide, automated search over compression recipes that a human would not normally pick, filtered in two stages and verified by rerun (full protocol in its own section below). This replaces the planned human rank sweep; it does not add a separate build.
6. Nov 4 reserved for the 3-minute demo video and the submission writeup.
7. AirLLM-style streaming scale test (unparked by Vinay, Oct 28; active): the full Alien Sweep protocol on a fifth pair, Qwen2.5-7B base/Instruct, run on Flash with layer-by-layer streaming in our own NumPy runtime (the AirLLM concept, Apache 2.0; code ours), because a 7B model can never be held whole in Flash's 11 GB RAM. Includes a streamed generation demo: the winning byte-fair patch applied block by block as each block loads, updating a model that is never whole in memory. Vinay's Oct 28 decision: the run's scripts and results are saved locally; whether the 7B results enter the README and submission is decided after he reviews the outcome.

## Demo video plan (approved by Vinay, Oct 26)

- Recorded on Muse's VM: a screen recording of the real demo running (terminal/browser capture). No camera, no laptop needed from Vinay.
- Script first, timed to what is on screen. Voice added after: AI-generated narration mixed over the recording with ffmpeg (the same pipeline as the folk-tale factory, minus generated scenes).
- Exactly 3 minutes. Opens with the required line stating what was pre-existing and what was built this week. Shape: 0:00 opening + problem; 0:30 the hot-swap moment; 1:30 benchmark numbers, including one Alien Sweep line (recipes tried, winner, held out result); 2:15 Muse Spark judging + quantum audit, one line each; 2:45 close.
- Rough cut early (as soon as the hot-swap demo runs) for Vinay to watch and react; final cut Nov 2-3 once the real numbers are in; Nov 4 reserved for submission only. Vinay approves the final cut before anything is posted.
- Simplicity rule (Vinay, Oct 27): keep the video as simple as possible. Plain words, no jargon without a one-line explanation, one idea at a time on screen. A newcomer watching once should understand what the tool does AND be able to pick it up and use it: the video shows the actual quickstart path (clone, run the quickstart, swap a patch file) in real steps, not just results.
- One script line near the close answers the question people will ask (Vinay, Oct 27): how is this different from a memory or personality file and other tools on the market? Plain version: a memory file is words the model reads; our patch is numbers that change the model's math. The README carries the fuller comparison (memory/prompts, adapters, whole-model shrinking).
- Do-it-yourself requirement (Vinay, Oct 27, after Agents 101): the video and the README must explain how the patch works AND how a viewer can do it themselves, as plain steps: take a base model and a fine-tuned version of it, run the compressor on the difference to get a small patch file, then load the patch with the base model to get the fine-tuned behavior. If the repo lacks a single clean script for that path, build one (examples/make_patch.py style) so the steps shown are the steps that actually run.

## Working notes

- Muse Spark reasons before answering and reasoning tokens count against max_tokens; use generous caps in benchmark calls.
- Log every real Muse Spark call the benchmark makes (prompt, token counts, verdict) into results/ as it happens, so the Meta tooling use is evidenced in the repo, not just planned. (Muse Spark's own suggestion in its Oct 26 repo review. Soft budget from Vinay: keep Meta API use under the $100 alert level of the $150 credits where possible.)
- Agents 101 takeaways applied (Oct 27, Vinay: use what is needed): (1) Verification leads the submission and demo story: Meta's own session framed agent output as unverified until defensive checks confirm it, "as important as building the agentic loop", so our rerun + Spark + Gemini cross-checks are presented as a headline feature, not a footnote. (2) Spark judging verdicts cite the exact result files they are based on (grounding advice from the session). (3) In the submission's Meta-products field, describe the benchmark harness honestly in the session's terms: a harness loop (plan, run tools, check results) with Muse Spark inside it.
- Validation rule (Vinay, Oct 26): key results are cross-validated by Muse Spark AND Gemini, on top of the script reruns that produce them. If the two disagree, the disagreement is reported and investigated, never averaged away.
- Model scope (settled Oct 26 night, Vinay: do what is best): Spark family only. Spark 1.3 via the Meta Model API, Spark Open via Baseten, Glimmer as the Flash reference. The other Meta models (Wonder, Image, Voice Transcribe, SAM 3.1) do not fit a compression tool, so they will not be forced in just to name more models. Depth of Spark use is the tooling story.
- Credit order and tracking (Vinay, Oct 26, 10:23 PM): the Baseten credits may not be available after the hackathon, so Baseten carries the heavy lifting first while it lasts: bulk benchmark runs, sweeps, and repeated evaluations on Muse Spark Open. The Meta Model API is used as needed for task generation, judging, and validation. Every Baseten and Meta call is tracked in results/ with provider, model, time, purpose, and token counts, so the usage totals can be shared with the organizers in the submission and checked against the credit balances.
- Models and weights are never committed (see .gitignore); data/ holds local downloads only.
- Glimmer's new wording limit (Oct 27, after the strengthening results): when the compressed versions outscore the full patch itself (as on the SmolLM2 pair), the gap-closed percentage passes 100% and must not be presented as a fraction of the fine-tune recovered. Prose about that pair must state plainly that the percentage is not a recovery fraction there and that the raw score margin is the honest measure. Record: results/glimmer_reference_addendum.md.
- Fresh-question test size (Vinay, Oct 27): the fresh held-out test stays at 96 questions. Expanding it further was considered and declined; 96 is the validated set the headline numbers rest on.
- Skill-transfer limit disclosure (Vinay, Oct 27): the NuExtract gated-skill limit is disclosed upfront, not buried: a "Known limit" note opens the README's Benchmark results section. Vinay's direction was to check with Spark and Glimmer and do what is best; both validators independently recommended (c) disclose upfront AND test larger patches (rank 64/128). The size test ran the same day: 1/10 clean at rank 32, 2/10 at rank 64 and rank 128, so size barely moves this boundary. Records: results/skill_limit_consultation.md, results/skill_demo.json, results/skill_demo_ranks.json.
- Force-start control test (Oct 28, Vinay's go-ahead): settles the question Muse Spark raised in the why-it-matters debate. Forcing the fine-tune's own first token on the same 10 NuExtract prompts takes the plain base from 0/10 to 7 clean + 1 partial, so most of the extraction skill was already in the base and the fine-tune's main work is the decision to start. The rank-32 patch under the same forced start scores 8 clean + 1 partial, matching the full fine-tune's own unforced score: a small real edge beyond the trigger (it cleans the two prompts the forced base still fails, and loses one the forced base cleans), but the gate is the dominant term. Limit wording in README and docs/why-it-matters.md updated to the settled version. Records: results/skill_demo_forced.json, results/skill_demo_forced_transcript.txt, examples/skill_demo_forced.py.
- Scale test, fourth pair (Oct 28, Vinay: use the expiring compute): the full Alien Sweep protocol on Qwen2.5-1.5B base/Instruct (Apache 2.0, non-gated; 197 delta matrices, tied embeddings), answering the fresh-eyes GPT-OSS attack "does any of this survive above 1B?" (results/fresh_perspective.md). One change from Phases 1-3: recipes were generated against the real-shape budget directly (uniform rank 32 = 39,046,144 bytes), so all 5 Spark recipes priced byte-fair from the start and the Stage 2 winner, Down Dominator (38,623,232 bytes; mlp.gate/up dropped to 0, mlp.down 45, attn.o_proj 64), needed no byte-matched variant. Combined-96 result: Down Dominator -6.344 vs uniform -6.478 (raw margin about 0.134 nats; base -12.584, full delta -7.810), but the win is subset-mixed (uniform wins heldout24, Down Dominator wins heldout72_new) and uniform's first-token accuracy is higher (32.3% vs 26.0%). Every factored config outscores the full delta itself on this pair, so gap_closed exceeds 1.0 (1.307 vs 1.279) and is not a recovery fraction here (same pattern and wording rule as pair 2). Honest scale answer: the format and contest still work at 1.5B (about 79x smaller than the 3,087,138,816-byte full delta), but the recipe's edge over uniform narrows from decisive at 0.5B to narrow and subset-dependent at 1.5B. Validation: script recomputation 61/61 gap_closed values, zero mismatches; Muse Spark judging 5/5 SUPPORTED (results/spark_judging_scale.md, corrected pass: the first pass carried two hand-copied Stage 2 values off by ~4e-4, re-run with file-pulled values, no verdict changed); Gemini all recomputations MATCH, claims 1-6 CONFIRMED, README sentence FAIR (results/gemini_validation_scale.md). Records: results/fourth_pair_check1.json, results/fourth_pair_stage2.json, results/fourth_pair_heldout96.json; scripts examples/fourth_pair_precompute.py, examples/fourth_pair_stage2.py, examples/fourth_pair_heldout96.py; Flash workdir ~/fc-v04-sweep4. Compute: precompute 66.9 s; build peak RSS 7,042.6 MB; eval peaks up to 7,964.4 MB on Flash's 11 GB.
- Force-start validation (Oct 28, Vinay: "put others to use too"): five independent checks of the forced-start claims. Script recomputation recounted every count from the per-prompt records, verified all 10 forced-token prefixes, and matched the margins (base -6.332, patch -1.2942, full +4.6005); no mismatches. Muse Spark 1.3, Muse Spark Open via Baseten, and Muse Spark Open via Fireworks each recounted and ruled claims 1 to 3 SUPPORTED; Glimmer ruled the interpretation FAIR with the small-sample caveat; Gemini ruled all four claims supported and the interpretation fair. All five agree the missing-control objection is settled for this test. One wording correction survived: Spark 1.3 and both Spark Open routes ruled "a small real edge" too strong, because the forced patch's lead over the forced base is one clean prompt out of 10, inside sampling noise; README and why-it-matters.md now read "one clean more than the forced base, which at 10 prompts is within sampling noise, so the gate is the main story and any edge beyond the trigger is small at most," with the "most of the skill" sentence scoped to this test. Records: results/glimmer_validation_forced.md, results/spark_validation_forced.json/.md, results/gemini_validation_forced.md, results/sparkopen_validation_forced.md, results/sparkopen_fireworks_validation_forced.md.
- Prior-art credit and the missing baseline (Oct 28): NOTICE.md now credits the published methods this work builds on conceptually (BitDelta, Delta-CoMe, LittleBit; methods only, no code used), and the README carries a short Prior art section plus a baseline paragraph in Benchmark results. The baseline answers the GPT-OSS judge question (why not a plain 1-bit delta?): on the Qwen pair a plain 1-bit delta's floor is 61,745,828 bytes, so at 19.4 MB it cannot exist, while the factored format closes 23.2% there (lite). At the floor price the BitDelta initialization (published init only, no distillation or training) closes 43.6% on the combined 96, against 38.5% for factored uniform rank 108 at 61,258,816 bytes: at that budget the plain init wins. Honest conclusion, judged SUPPORTED 6 of 6 by Muse Spark with the headline sentence returned unchanged: the factored format's win is reach, not quality per byte at the plain format's floor. Records: results/bitdelta_baseline.json, results/spark_judging_baseline.md, examples/bitdelta_baseline.py.
- AirLLM streaming scale test, fifth pair (Oct 28, Vinay unparked it and clarified "we can use anything from AirLLM for ourselves, I mean the concept"): Qwen2.5-7B base/Instruct (Apache 2.0, non-gated; 28 blocks, hidden 3584, 28 Q heads / 4 KV heads, embeddings NOT tied, so embed and lm_head are separate delta matrices; 198 delta matrices; full delta 15.2 GB bf16) on Flash (11 GB RAM), streamed AirLLM-style in our own NumPy stack: per-matrix streamed RSVD precompute, Gram-matrix exact SVD factor build, block-by-block eval forward carrying all probe items' hidden states, per-item lm_head logits at answer positions only (never a materialized full logits tensor). Concept credited to lyogavin/airllm (Apache 2.0) in NOTICE.md; all code is ours. Gemini design consult first (results/airllm_design_consult.md): adopted in-place delta formation with explicit gc discipline, answer-position-only logits, and full timing disclosure in the stream demo (time to first token, per-token latency, storage medium, peak RAM); rebutted its 14-16 GB RSVD peak (thin projections keep it near the 2.2 GB delta plus ~0.4 GB of factors) and its demand to drop the Gram SVD (the quantize cross-check against dense-SVD construction is the guard, and its diffs are reported). Protocol mirrors pair 4 for comparability (validation, Stage 2 on 24, byte-fair winner on the combined 96, BitDelta-style baseline at its real price), plus the streamed generation demo Vinay asked for: base streamed plain vs base streamed with the winning patch, greedy, few prompts, per-token time stated honestly. Vinay's decision (Oct 28): results stay local-only until he reviews the report; no README section and no why-it-matters claims unless he approves after seeing the outcome.
- Llama Phase 3 (Oct 27): the third pair (Meta's own Llama 3.2 1B base and Instruct, unblocked when the Hugging Face license approval landed) ran the full contest. The byte-fair variant no_embed_mlp_spread_balanced (24,515,584 B) beats uniform_rank32 on the combined 96 fresh questions, gap closed 15.9% vs -7.6% (uniform scores below the base model itself), and wins both halves; the Stage 2 winner no_embed_mlp_spread is byte-unfair at +38.0% over the 25,143,296 B budget and is named only as such. Recovery on this pair is weaker than on the other two pairs, and no factored config outscored the full delta, so gap_closed stays a recovery fraction here. Validation (Oct 27): script recomputation matched 60 of 60 gap_closed values exactly; Gemini recomputed every headline value, confirmed claims 1 to 5, and ruled the summary sentence fair; the Muse Spark judging addendum supported claims A to D and marked E not supported on scope only (the pair-1 comparison was outside the numbers it was shown; the in-pair facts were confirmed, and the 23.2% figure rests on the pair-1 records and the earlier addendum's supported claim A). Records: results/third_pair_stage2.json, results/third_pair_heldout96.json, results/gemini_validation_llama.md, results/spark_judging_llama.md.

- Agents 102 handbook check (Oct 28, Vinay: use what is needed, follow any strict guidelines there): Meta's workshop repo (github.com/meta-models/legal-agent-workshop, the Agents 101/102 sessions) was read in full: HANDBOOK.md, VERIFICATION.md, ESCALATION_RULES.md, and the verification code. Judgment: it is a teaching pattern for a legal agent, not event rules, so none of it binds this submission. It is still Meta's own published standard for verifiable agents, so our harness was checked against it. Already matching: (1) two layers of checking, plain code first (script recomputation of every value, the quantum audit), then a model judging pass (one Muse Spark call per result set, like their claims check, which also runs only after the code rules pass); (2) no claim is published without a citation: their findings cite a document, page, and exact quote, and the case record refuses a quote that is not on the page; our judging verdicts cite the result file and the exact values relied on; (3) refusals come back as a problem list and the text is fixed, never silently rewritten (our headline ruling and the force-start wording correction both worked this way); (4) human sign-off at the end: their passing memo waits as awaiting_signoff until the attorney approves, ours waits for Vinay's approval before the submission and final video ship. Adopted now, as working rules: (a) judging values are pulled from the result files by script, never hand-copied (the scale test's first judging pass carried two hand-copied values off by about 4e-4; the corrected pass pulled them from the files, and that is now the standing rule, the same reason their kit checks quotes at write time); (b) each published claim carries at most 3 cited result files, the strongest ones (their cap is 3 citations per finding); (c) judging verdicts gain a third state, escalated, for claims the evidence shown cannot settle (scope limits, validators disagreeing); an escalated claim goes to Vinay instead of being reworded by the agent, and a claim refused by validators twice escalates rather than being reworded a third time (their version: a memo refused 3 times goes to a person); (d) held-out hygiene: the submission reports held-out results as aggregate numbers only and never describes the held-out items themselves (their feedback rule: point to what is missing, never quote or count the ground truth). Deliberately NOT adopted: their claims check fails open (an unreadable Spark judgment passes the memo); ours fails closed, a judging pass with missing evidence is rerun, as the scale test did. Format mapping, no code change: their finding is {item, status: proven / not_proven / escalated, one-sentence summary, citations [{document, page, quote}], max 3}; ours is {claim_id, claim, verdict: SUPPORTED / NOT SUPPORTED, cited_file, values_relied_on, note}. The shapes already match; the only deltas are the new escalated status and the 3-citation cap, which future judging passes follow. Their ground-truth checklist check (score kept from the agent, shown to the reviewer) maps to our held-out guard plus the judging claim list: the search never sees the fresh items, and the validators' records keep their own words.

## Expanded scope (Vinay, Oct 26: push the limits, not just another version)

1. Live hot-swap demo as the centerpiece: one base model, tiny 1-bit delta files swapped in live, behavior changes on the spot, file sizes shown side by side. This is the moment the demo video is built around.
2. Muse Spark inside the product loop: Spark (Meta Model API) generates fresh probe tasks, runs the compressed vs full comparison, and writes the verdicts. The benchmark is agentic, not a static script output.
3. Meta open weights in the comparison: Muse Spark Open (hosted via Baseten) joins the benchmark table, which also puts the project in contention for the Best Build on Meta Open Weight Models bonus.
4. Reproducibility as a feature: every number in the README and demo is produced by a script in this repo that anyone can rerun.
5. Submission craft: review the submission form in the first days, script the 3-minute demo from the start, post the demo on X at submission for the Most Viral bonus, and open the video with the required line separating pre-existing work from this week's build.
6. Alien Sweep as the search story: Spark proposes recipes, the sweep tests them, and the demo reports how many recipes were tried and what the winner was. If the human recipe wins, that is the reported result, with the full search map published either way.

## Alien Sweep (approved by Vinay, Oct 26)

Vinay's condition (Oct 26): use it only if it makes sense once the build starts. If the recipe space outruns what the runtime can run and verify by Nov 4, fall back to the human rank sweep and report that plainly in the results.

What it is, in plain words: instead of a person choosing a few sensible compression settings and testing those, an agent proposes many settings, including odd ones a person would skip, a script tests all of them, and only the ones that pass a fresh rerun count. The name comes from the October 2026 OpenAI math release, where mathematicians called the AI proofs alien math because the winning moves came from directions humans had not tried.

How it runs:
- Recipe generation: Muse Spark proposes recipes as per-layer rank maps under a fixed total size budget (uneven budgets across layers included). Recipes are strict JSON, layer name to integer rank only; anything needing a new code path (ternary deltas, variable bit width) is out of bounds for the sweep. Every proposed recipe is logged with its reason, so the search count in the demo is a real count from a file, not a claim.
- Stage 1, cheap filter: the fast matrix level benchmark scores every recipe on reconstruction error at exact accounted size. Only the top 5 recipes advance.
- Stage 2, hard check: the top 5 run the end to end task benchmark (knowledge, instruction, math probes) on Flash. A recipe only counts if the benchmark script reruns it and it passes on task score, not only weight error.
- Held out guard: Spark generates fresh probe tasks the search never saw. The winner must also pass those, so the sweep cannot win by memorizing the old 24 probe items.
- Honest outcome rule: if no alien recipe beats the human rank 32 recipe, the result is reported that way and the search map is still published. No winner is named in the demo script until Stage 2 and the held out check are both done.
- Headline ruling (Oct 27, three-way validation; Vinay sided with Glimmer over Gemini and Spark): the headline recipe in our own prose (README, demo, submission) is mlp_behemoth_lite, the byte-fair leader: it beat the human uniform recipe on the fresh held-out tasks while using fewer bytes (gap closed 9.5% vs 1.6%). mlp_behemoth itself is named only as the byte-unfair parent (11.8% more bytes than uniform) whenever it appears. The validators' own records in results/ keep their original words; this ruling governs our wording, not their records.
- Strengthening tests (approved by Vinay Oct 27, running): (1) the fresh-question held-out test expands from 24 to 96 items (72 new Spark-generated, novelty-checked), lite vs uniform rerun on the Qwen pair; (2) the full contest repeated on a second pair, SmolLM2-360M base/Instruct; (3) the same contest on Meta's own open weights, Llama 3.2 1B base/Instruct, queued after (2) and subject to the HF license gate.

Where it fits the schedule: the rank sweep was already an early experiment in this plan. The Alien Sweep widens that same slot. Stage 1 is cheap CPU work on the VM; Stage 2 is only 5 recipes on Flash. Nov 4 stays reserved.

### Gemini debate on Alien Sweep (Oct 26, via the Gemini API)

- Verdict: GO, but only inside a strict boundary. A recipe is a per-layer rank distribution under a fixed total size budget, which needs zero new runtime code (the same SVD and packing path, different rank integers per layer). The moment a recipe needs a new code path, it is out.
- Technique adopted: precompute the SVD once per matrix up to the max rank, then Stage 1 scores each recipe by slicing the precomputed factors. Hundreds of recipes then cost seconds, not one SVD per recipe.
- Failure modes Gemini raised, all accepted: low matrix error does not guarantee task success (that is why Stage 2 exists); Spark can emit invalid layer names or out-of-range ranks (strict JSON schema check before anything runs); Stage 2 CPU time per config is the real budget risk; the winner may be the boring uniform recipe (covered by the honest outcome rule).
- Day 2 go/no-go checks. Any failure means fall back to the human rank sweep and report it: (1) Spark produces 5 schema-valid recipe JSONs quickly, layer-to-rank maps only; (2) the one-time SVD precompute for the target model finishes in under 10 minutes; (3) Stage 1 scores the full recipe set in minutes via slicing; (4) one Stage 2 config completes the task benchmark inside the agreed time budget without memory thrash on Flash.

## Resources we will use

- AI compute (Vinay, Oct 26): use all of it. Meta Model API credits fund Muse Spark as task generator, judge, AND independent validator of results; Gemini covers design debate and repo review; Flash local models run the heavy benchmarks. The free credits exist to be spent on this build. Order of use (Vinay, Oct 26 night): Baseten first for the heavy lifting, because its credits may end with the hackathon; the Meta Model API fills in as needed. Real-money charges beyond the credits still need Vinay's tap.

- Flash (Vinay's Ubuntu box): local small models for the factored-runtime experiments, plus Muse Glimmer 30B through NVIDIA NIM, which is already working there. Quality-critical orchestration stays on the Muse VM, which holds the Meta Model API connection.
- Other AIs for design pressure-testing: the standing Gemini design-debate chat (Vinay's permission), used the same way as during prep, with anything adopted logged in NOTES.
- Quantum component (honest and bounded): the benchmark's verification pass audits a subset of results, and that subset is chosen with true quantum random numbers generated on IBM Quantum hardware (free plan, ibm_fez). The backend, job, and seed are logged with the results. It is an audit-sampling method, not a speed claim.
- Feedback for Meta: the submission includes a short section on what we learned about the Muse models themselves (for example, Muse Spark spends output budget on reasoning before answering), since the organizers say they want to learn where the tools need to improve.

## Crediting

Vinay K Ganji Krishna is the sole participant and author of record. The README credits Ember (Muse Spark) as the AI agent used for implementation, benchmarking, and documentation, the same way the event itself promotes building with the Muse Code agent. Ember is not listed as a team member.

## Design input from the Gemini debate chat (Oct 26)

- Rank tuning beats bit-unpacking kernels. Kernels are a rabbit hole for a 10-day solo build; plain numpy unpacking is enough. Rank calibration is existential: too low and the delta is powerless, too high and the file-size story dies. A rank sweep is an early experiment.
- Quarantine the quantum dependency: pull one large batch of quantum random numbers from IBM hardware at the start, log backend and seed, freeze it as a static fixture. No live quantum calls during crunch or demo.
- The demo contrast must be stark: same prompt, base model fails it, the tiny delta file (size on screen) swaps in, same prompt now succeeds. The strict-JSON instruction prompt is the natural centerpiece.
- Probe sets: sharp archetypes carry the demo; the full Signet sets still carry the benchmark table, because reproducible numbers are the credibility.

===== END BUILD_PLAN.md =====

===== EVIDENCE DIGEST =====
# Evidence digest computed from the pushed result JSON files at commit 3933fae

## results/alien_sweep_heldout96.json
- base: mean_target_logprob=-11.1497780625, accuracy=0.031250
- full_delta: mean_target_logprob=-8.5424662354, accuracy=0.166667
- full_delta_fp16_bytes=987922432
- ranking: mlp_behemoth: mean=-10.45627380592698, gap_closed=0.2659843941106181 (26.5984%), accuracy=0.020833333333333332, bytes=21719776
- ranking: mlp_behemoth_lite: mean=-10.54508293414888, gap_closed=0.2319228264458408 (23.1923%), accuracy=0.010416666666666666, bytes=19358176
- ranking: uniform_rank32: mean=-11.095640657042859, gap_closed=0.020763686533300157 (2.0764%), accuracy=0.010416666666666666, bytes=19434496
- verdict.byte_fair_headline_question=does mlp_behemoth_lite still beat uniform_rank32 on the combined 96 fresh items?
- verdict.lite_beats_uniform_on_combined96=True
- verdict.lite_gap_closed_combined96=0.2319228264458408
- verdict.uniform_gap_closed_combined96=0.020763686533300157
- verdict.lite_within_uniform_budget=True
- verdict.subset_consistency.heldout24.lite_gap_closed=0.0947229129097021
- verdict.subset_consistency.heldout24.uniform_gap_closed=0.01564243038524459
- verdict.subset_consistency.heldout24.lite_beats_uniform=True
- verdict.subset_consistency.heldout72_new.lite_gap_closed=0.303801464368062
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=0.023446697818697487
- verdict.subset_consistency.heldout72_new.lite_beats_uniform=True
- verdict.mlp_behemoth_reference_only.note=mlp_behemoth is BYTE-UNFAIR (over the uniform budget) and is reported as a reference only, never as the headline.
- verdict.mlp_behemoth_reference_only.real_shape_bytes=21719776
- verdict.mlp_behemoth_reference_only.uniform_real_shape_bytes=19434496
- verdict.mlp_behemoth_reference_only.over_bytes=2285280
- verdict.mlp_behemoth_reference_only.over_pct=11.8
- verdict.mlp_behemoth_reference_only.combined96_gap_closed=0.2659843941106181
- verdict.mlp_behemoth_reference_only.combined96_factored_mean_target_logprob=-10.45627380592698

## results/second_pair_heldout96.json
- base: mean_target_logprob=-12.8785653857, accuracy=0.010417
- full_delta: mean_target_logprob=-8.4321585239, accuracy=0.093750
- full_delta_fp16_bytes=723517440
- ranking: o-down supercharge: mean=-8.03994579872309, gap_closed=1.0882089150651426 (108.8209%), accuracy=0.09375, bytes=27660288
- ranking: o-down-rebalanced: mean=-8.072964749082066, gap_closed=1.080782930132702 (108.0783%), accuracy=0.08333333333333333, bytes=19683328
- ranking: uniform_rank32: mean=-8.366280457949834, gap_closed=1.0148160229227625 (101.4816%), accuracy=0.08333333333333333, bytes=19705856
- verdict.stage2_winner=o-down supercharge
- verdict.byte_fair_contender=o-down-rebalanced
- verdict.byte_fair_headline_question=does o-down-rebalanced beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=1.080782930132702
- verdict.uniform_gap_closed_combined96=1.0148160229227625
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=27660288
- verdict.winner_byte_status.uniform_real_shape_bytes=19705856
- verdict.winner_byte_status.winner_byte_unfair=True
- verdict.winner_byte_status.winner_combined96_gap_closed=1.0882089150651426
- verdict.subset_consistency.heldout24.contender_gap_closed=1.037137028575536
- verdict.subset_consistency.heldout24.uniform_gap_closed=0.9703361598361151
- verdict.subset_consistency.heldout24.contender_beats_uniform=True
- verdict.subset_consistency.heldout72_new.contender_gap_closed=1.0979379349340161
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=1.0322988159821247
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## results/third_pair_heldout96.json
- base: mean_target_logprob=-13.7178328094, accuracy=0.010417
- full_delta: mean_target_logprob=-7.3867130269, accuracy=0.218750
- full_delta_fp16_bytes=2471493632
- ranking: no_embed_mlp_spread: mean=-12.12275284734357, gap_closed=0.25194278687724053 (25.1943%), accuracy=0.03125, bytes=34690048
- ranking: no_embed_mlp_spread_balanced: mean=-12.714218663974016, gap_closed=0.15852079567397595 (15.8521%), accuracy=0.020833333333333332, bytes=24515584
- ranking: uniform_rank32: mean=-14.20128408199294, gap_closed=-0.07636110027783072 (-7.6361%), accuracy=0.0, bytes=25143296
- verdict.stage2_winner=no_embed_mlp_spread
- verdict.byte_fair_contender=no_embed_mlp_spread_balanced
- verdict.byte_fair_headline_question=does no_embed_mlp_spread_balanced beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=0.15852079567397595
- verdict.uniform_gap_closed_combined96=-0.07636110027783072
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=34690048
- verdict.winner_byte_status.uniform_real_shape_bytes=25143296
- verdict.winner_byte_status.winner_byte_unfair=True
- verdict.winner_byte_status.winner_combined96_gap_closed=0.25194278687724053
- verdict.subset_consistency.heldout24.contender_gap_closed=0.200373434383912
- verdict.subset_consistency.heldout24.uniform_gap_closed=-0.016714667787171608
- verdict.subset_consistency.heldout24.contender_beats_uniform=True
- verdict.subset_consistency.heldout72_new.contender_gap_closed=0.14817956351361586
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=-0.09109894297869517
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## results/fourth_pair_heldout96.json
- base: mean_target_logprob=-12.5841302690, accuracy=0.010417
- full_delta: mean_target_logprob=-7.8097449276, accuracy=0.333333
- full_delta_fp16_bytes=3087138816
- ranking: Down Dominator: mean=-6.343687772752477, gap_closed=1.3070672034171866 (130.7067%), accuracy=0.2604166666666667, bytes=38623232
- ranking: uniform_rank32: mean=-6.478079873557243, gap_closed=1.2789186374354595 (127.8919%), accuracy=0.3229166666666667, bytes=39046144
- verdict.stage2_winner=Down Dominator
- verdict.byte_fair_contender=Down Dominator
- verdict.byte_fair_headline_question=does Down Dominator beat uniform_rank32 on the combined 96 fresh items?
- verdict.contender_beats_uniform_on_combined96=True
- verdict.contender_gap_closed_combined96=1.3070672034171866
- verdict.uniform_gap_closed_combined96=1.2789186374354595
- verdict.contender_within_uniform_budget=True
- verdict.winner_byte_status.winner_real_shape_bytes=38623232
- verdict.winner_byte_status.uniform_real_shape_bytes=39046144
- verdict.winner_byte_status.winner_byte_unfair=False
- verdict.winner_byte_status.winner_combined96_gap_closed=1.3070672034171866
- verdict.subset_consistency.heldout24.contender_gap_closed=1.1242514732201125
- verdict.subset_consistency.heldout24.uniform_gap_closed=1.152286379770239
- verdict.subset_consistency.heldout24.contender_beats_uniform=False
- verdict.subset_consistency.heldout72_new.contender_gap_closed=1.3791549665115759
- verdict.subset_consistency.heldout72_new.uniform_gap_closed=1.3288521753254294
- verdict.subset_consistency.heldout72_new.contender_beats_uniform=True

## Independent arithmetic spot calculations
- Qwen pair full/uniform ratio = 50.833447; full/lite ratio = 51.033859.
- Qwen 1.5B full/Down Dominator ratio = 79.929583; full/uniform ratio = 79.063859.
- One-layer ratio using 8,388,608 bytes / 147,456 bytes = 56.888889.
- Qwen pair all-in effective bits/weight for uniform price = 0.314753 bpw; for lite = 0.313517 bpw.
- BitDelta pricing: {'n_matrices': 169, 'n_weights_169_matrices': 493961216, 'bitdelta_init_price_bytes': 61745828, 'bitdelta_price_formula': 'ceil(total_weights / 8) + 4 bytes x n_matrices (one fp32 scale per matrix)', 'factored_matched_rank': 108, 'factored_matched_price_bytes': 61258816, 'factored_rank_plus_one_price_bytes': 61809136, 'factored_under_by_bytes': 487012}; configs: {'bitdelta_init': {'kind': 'published_baseline_initialization', 'definition': "BitDelta initialization (Liu et al., arXiv:2402.10193): per matrix, delta_hat = sign(delta) * mean(|delta|); one fp32 scale per matrix; NO scale distillation and NO training. The full BitDelta method distills the scales on data afterwards; that step is deliberately not run, and this config must be cited as the initialization, not as BitDelta's final reported quality.", 'mean_target_logprob': -10.012813627503721, 'accuracy_first_token': 0.0625, 'price_bytes': 61745828, 'wall_s': 285.21, 'peak_rss_mb': 3578.4}, 'factored_uniform_rank108': {'kind': 'ours_factored_matched_budget', 'definition': 'factored.quantize_delta at uniform rank 108 on all 169 matrices: the largest uniform rank whose factored.storage_bytes total fits under the plain 1-bit price.', 'mean_target_logprob': -10.146044864550612, 'accuracy_first_token': 0.03125, 'price_bytes': 61258816, 'wall_s': 287.5, 'peak_rss_mb': 3279.4}}.

## results/skill_demo.json
- patch={'built_by': 'examples/make_patch.py', 'rank_mode': 'uniform rank 32', 'storage_bytes': 19434496, 'file_bytes_on_disk': 19801674, 'full_delta_fp16_bytes': 987922432}
- base (no patch): counts={'clean': 0, 'partial': 0, 'failed': 10}
- base + compressed patch (uniform rank 32): counts={'clean': 1, 'partial': 0, 'failed': 9}
- base + full delta (fine-tune weights): counts={'clean': 8, 'partial': 1, 'failed': 1}

## results/skill_demo_forced.json
- unforced_reference={'base (no patch)': {'clean': 0, 'partial': 0, 'failed': 10}, 'base + compressed patch (uniform rank 32)': {'clean': 1, 'partial': 0, 'failed': 9}, 'base + full delta (fine-tune weights)': {'clean': 8, 'partial': 1, 'failed': 1}}
- base, forced start: counts={'clean': 7, 'partial': 1, 'failed': 2}
- base + compressed patch (uniform rank 32), forced start: counts={'clean': 8, 'partial': 1, 'failed': 1}

## results/skill_demo_ranks.json
- test=skill-transfer size test: does a larger uniform patch move the first-token gate?
- skill_pair=Qwen/Qwen2.5-0.5B base + numind/NuExtract-1.5-tiny (MIT) JSON extraction
- prompts=the same 10 screening prompts and the same judge as results/skill_demo.json (clean = parses as JSON, keys match template, every expected value present)
- decoding=greedy, max 64 new tokens, raw NuExtract prompt format
- reference_counts: {'note': 'both reruns (rank 64 and rank 128 runs) reproduced these two configs exactly: base 0/0/10, full delta 8 clean / 1 partial / 1 failed'}
- conclusion=Clean transfers: rank 32 = 1/10 at 19,434,496 B; rank 64 = 2/10 at 37,044,736 B; rank 128 = 2/10 at 72,265,216 B. Quadrupling the patch buys one extra prompt and then nothing: at these sizes the first-token gate barely moves with uniform size.
- verify=rank 64 and rank 128 patches both passed make_patch --verify (worst factored-vs-dense diff 4.3e-16 / 3.1e-16; file-vs-fresh rel diff 5.0e-04 / 3.3e-04, the designed fp16 V rounding). Build peaks: 4,754 MB both; verify peaks 4,917 / 5,067 MB.

## results/skill_demo_recipe.json
- test=allocation test: same bytes (19,434,496 B budget), smarter placement vs uniform rank 32
- skill_pair=Qwen/Qwen2.5-0.5B base + numind/NuExtract-1.5-tiny (MIT) JSON extraction
- recipe_generation: {'provider': 'baseten', 'model': 'meta-models/muse-spark-open-1026', 'max_tokens': 16000, 'budget_bytes': 19434496, 'prompt': 'You are proposing compression recipes for a factored 1-bit weight-delta format. A recipe assigns one integer rank to each layer TYPE; that rank is used for that layer type in all 24 transformer blocks (the embedding is a single matrix). The stored size of one matrix at rank r is priced exactly as:\n\n  bytes(matrix, r) = ceil(rows * r / 8) + 4 * rows + 2 * cols * r\n\nLayers (rows x cols of the delta matrix):\n  embed: delta matrix 151936 x 896, rank may be 0..896\n  attn.q_proj: delta matrix 896 x 896, rank may be 0..896\n  attn.k_proj: delta matrix 128 x 896, rank may be 0..128\n  attn.v_proj: delta matrix 128 x 896, rank may be 0..128\n  attn.o_proj: delta matrix 896 x 896, rank may be 0..896\n  mlp.gate: delta matrix 4864 x 896, rank may be 0..896\n  mlp.up: delta matrix 4864 x 896, rank may be 0..896\n  mlp.down: delta matrix 896 x 4864, rank may be 0..896\n\nThe total size of a recipe is bytes(embed) + 24 * (sum of bytes over the other 7 layer types), and it must be <= 19434496 bytes. That is exactly the cost of the uniform rank-32 recipe on this model; you have the same bytes, spend them differently.\n\nThe model pair is Qwen2.5-0.5B base and NuExtract-1.5-tiny, a fine-tune for structured JSON extraction (read a text and a JSON template, answer with the filled template). The finding you are designing against: this skill is gated by the FIRST generated token. The fine-tune starts the JSON; the plain base emits end-of-text immediately and answers nothing (0 of 10 test prompts). Our uniform rank-32 patch flips that gate on only 1 of 10 prompts (on the 9 others the patched model still stops immediately), even though the one extraction it does start is fully correct. Bigger uniform patches barely help (rank 64 and rank 128 each flip 2 of 10). So placement, not size, is the open question. Weigh protecting the embedding (it feeds every token position and, with tied weights, the output head) and the output-side layers (attn.o_proj, mlp.down) that shape the final logits, if you judge that is where the start-vs-stop decision lives.\n\nPropose exactly 5 recipes, ordered best-first: put the recipe you recommend most first. Make them genuinely different from each other and from uniform: uneven allocations are the point. Every recipe must include every layer name exactly once in its "ranks" object, with an integer rank (0 is allowed and means that layer type\'s delta is dropped).\n\nReply with ONLY a JSON object, no markdown fences, no commentary, in exactly this shape:\n{"recipes": [{"name": "<short name>", "reason": "<one sentence>", "ranks": {"embed": 0, "attn.q_proj": 0, "attn.k_proj": 0, "attn.v_proj": 0, "attn.o_proj": 0, "mlp.gate": 0, "mlp.up": 0, "mlp.down": 0}}]}\nReplace the zeros with your ranks. Check your arithmetic: each recipe\'s total (embed once + 24 blocks) must be <= 19434496 bytes.'}
- chosen_recipe: {'name': 'Gatekeeper Embed+O', 'reason': 'Maximizes the tied embed and cheap-to-expensive output ratio by pushing embed to 382 and o_proj to 64 with minimal down to flip the first-token EOS vs JSON gate.'}
- chosen_recipe_price_bytes=19434400
- patch_file_bytes_on_disk=18796330
- verify: {'result': 'PASS'}
- demo_run: {'config_label': 'base + compressed patch (recipe Gatekeeper Embed+O)'}
- first_token_margins: {'measure': 'first-token logprob margin', 'definition': "margin = logprob(fine-tune's actual first generated token) - logprob(end-of-text 151643) at the first generation position, natural log; positive means the gate is open (starting the JSON beats stopping)", 'peak_rss_mb': 2354.3}
- conclusion=Placement did not beat size at equal bytes; it did worse. The Spark recipe's radical reallocation (embed 382, mlp.gate/up dropped to 0) opened 0 of 10 gates and its mean first-token margin (-4.14) is far below uniform rank 32 (-1.29). The gate-open counts measured from margins (base 0, rank32 1, recipe 0, full delta 10) exactly match the generation outcomes. Neither bigger uniform patches (2/10 at rank 128) nor this reallocation opens the gate at these budgets; uniform rank 32 is closest per byte.

## results/alien_sweep_heldout.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'byte_matched_variant', 'method', 'shared_configs', 'configs', 'ranking_by_heldout_task_score', 'verdict', 'scripts']
- verdict={"stage2_winner": "mlp_behemoth", "heldout_task_score_metric": "overall mean target logprob of the factored config (Stage 2 convention)", "mlp_behemoth_beats_uniform_on_heldout": true, "mlp_behemoth_confirmed_sweep_winner": true, "byte_fair_comparison": {"variant": "mlp_behemoth_lite", "variant_real_shape_bytes": 19358176, "uniform_real_shape_bytes": 19434496, "variant_within_uniform_budget": true, "variant_beats_uniform_on_heldout": true, "variant_gap_closed_overall": 0.0947229129097021, "uniform_gap_closed_overall": 0.01564243038524459}, "mlp_behemoth_byte_caveat": {"mlp_behemoth_real_shape_bytes": 21719776, "uniform_real_shape_bytes": 19434496, "over_bytes": 2285280, "over_pct": 11.8, "note": "mlp_behemoth's Stage 2 win was not byte-fair; the byte-fair comparison is the variant's row."}}
- configs={"uniform_rank32": {"name": "uniform_rank32", "kind": "human_baseline", "ranks": {"embed": 32, "attn.q_proj": 32, "attn.k_proj": 32, "attn.v_proj": 32, "attn.o_proj": 32, "mlp.gate": 32, "mlp.up": 32, "mlp.down": 32}, "rank0_layer_names": [], "real_shape_bytes": 19434496, "configs": {"base": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.907639310877745}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -11.568273144098278}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -8.098655694460739}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -7.055989094074219}}}, "full_delta": {"overall": {"n": 24, "accuracy": 0.16666666666666666, "mean_target_logprob": -5.322192186566966}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.894272131668772}, "instruction": {"n": 8, "accuracy": 0.5, "mean_target_logprob": -2.096013926456496}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.976290501575629}}}, "factored_delta": {"overall": {"n": 24, "accuracy": 0.0, "mean_target_logprob": -8.851554203835738}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -10.297644800209842}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -9.299502159565801}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.957515651731569}}}}, "gap_closed": {"knowledge": 0.27185025003406543, "instruction": -0.20005299525050946, "math": 1.2355731670467298, "overall": 0.01564243038524459}, "per_item": [{"bucket": "knowledge", "logprob": -12.447284086602247, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -6.0896188013150265, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -15.854590412931671, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -8.147514544844567, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -11.862084444157764, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -7.865520628128349, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -9.294762646619539, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -10.819782837079575, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -9.532485010686338, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.933549728098443, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -11.326082756254166, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -4.2459042955269455, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -11.143121419135793, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -10.478749897546045, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.699891449809007, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -10.036232719469663, "first_token_correct": 0}, {"bucket": "math", "logprob": -5.077893818957592, "first_token_correct": 0}, {"bucket": "math", "logprob": -6.483583546908075, "first_token_correct": 0}, {"bucket": "math", "logprob": -7.500344703423812, "first_token_correct": 0}, {"bucket": "math", "logprob": -4.190430632303273, "first_token_correct": 0}, {"bucket": "math", "logprob": -7.556504310356592, "first_token_correct": 0}, {"bucket": "math", "logprob": -6.033214856384206, "first_token_correct": 0}, {"bucket": "math", "logprob": -8.703859851819542, "first_token_correct": 0}, {"bucket": "math", "logprob": -10.11429349369946, "first_token_correct": 0}], "wall_s": 71.67, "eval_wall_s": 68.15, "peak_rss_mb": 3192.2}, "mlp_behemoth": {"name": "mlp_behemoth", "kind": "spark_recipe_stage2_winner", "ranks": {"embed": 10, "attn.q_proj": 20, "attn.k_proj": 0, "attn.v_proj": 20, "attn.o_proj": 20, "mlp.gate": 45, "mlp.up": 45, "mlp.down": 50}, "rank0_layer_names": ["attn.k_proj"], "real_shape_bytes": 21719776, "configs": {"base": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.907639310877745}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -11.568273144098278}, "instruction": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -8.098655694460739}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -7.055989094074219}}}, "full_delta": {"overall": {"n": 24, "accuracy": 0.16666666666666666, "mean_target_logprob": -5.322192186566966}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.894272131668772}, "instruction": {"n": 8, "accuracy": 0.5, "mean_target_logprob": -2.096013926456496}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.976290501575629}}}, "factored_delta": {"overall": {"n": 24, "accuracy": 0.041666666666666664, "mean_target_logprob": -8.519294854322665}, "per_bucket": {"knowledge": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -10.322385879852932}, "instruction": {"n": 8, "accuracy": 0.125, "mean_target_logprob": -9.11764732690944}, "math": {"n": 8, "accuracy": 0.0, "mean_target_logprob": -6.117851356205622}}}}, "gap_closed": {"knowledge": 0.2665569093656965, "instruction": -0.1697571955534997, "math": 11.771070334588293, "overall": 0.10831130486402876}, "per_item": [{"bucket": "knowledge", "logprob": -11.869581919159009, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -5.260216545256683, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -13.640625505545405, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -11.094353136443697, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -12.667091050882842, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -7.917084875768683, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -9.902145731672057, "first_token_correct": 0}, {"bucket": "knowledge", "logprob": -10.22798827409509, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -8.970952865296688, "first_token_correct": 0}, {"bucket": "instruction", "logprob": -9.583043071480885, "first_token_correct": 0

## results/alien_sweep_stage2.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'method', 'build_validation', 'forward_validation', 'full_delta_fp16_bytes_real_shapes', 'shared_configs', 'recipes', 'human_baseline', 'ablations', 'rank0_analysis', 'ranking_by_task_score', 'api_calls', 'scripts']

## results/fourth_pair_stage2.json (top-level keys and compact verdict/ranking fields)
- keys=['stage', 'date', 'machine', 'model_pair', 'probe_set', 'method', 'build_validation', 'forward_validation', 'forward_validation_verdict', 'gap_closed_note', 'full_delta_fp16_bytes_real_shapes', 'shared_configs', 'recipes', 'human_baseline', 'ranking_by_task_score', 'winner', 'api_calls', 'scripts']

## results/hotswap_demo.json (top-level keys and compact verdict/ranking fields)
- keys=['model', 'decoding', 'prompts', 'patch_sizes_bytes', 'swaps', 'configs', 'peak_rss_mb', 'api_calls']
- configs={"base (no patch)": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}\n Comey\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant", "generated_tokens": 48, "seconds": 14.868, "json": {"parseable": false, "exact_keys": false, "exact_values": false}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo. Lauderdale. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital of Japan. Lauderdale is the capital", "generated_tokens": 48, "seconds": 9.24, "contains_expected": true}, "math_percent": {"answer": "Sure, 15 percent of 200 is 30.eousystem\nYou are Qwen, created by Alibaba Cloud. You are a helpful assistant.\u9c95system\nYou are Qwen, created by Alibaba Cloud.", "generated_tokens": 48, "seconds": 8.784, "contains_expected": true}}, "base + uniform rank-32 factored patch": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}", "generated_tokens": 31, "seconds": 12.162, "json": {"parseable": true, "exact_keys": true, "exact_values": true}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo.", "generated_tokens": 7, "seconds": 4.922, "contains_expected": true}, "math_percent": {"answer": "To find 15% of 200, you can use the following formula:\n\n(15/100) * 200 = 30\n\nSo, 15% of 200", "generated_tokens": 48, "seconds": 9.36, "contains_expected": true}}, "base + mlp_behemoth_lite factored patch": {"json_transform": {"answer": "{\n  \"title\": \"Arrival\",\n  \"year\": 2016,\n  \"director\": \"Denis Villeneuve\"\n}", "generated_tokens": 31, "seconds": 12.046, "json": {"parseable": true, "exact_keys": true, "exact_values": true}}, "knowledge_capital": {"answer": "The capital of Japan is Tokyo.", "generated_tokens": 7, "seconds": 7.891, "contains_expected": true}, "math_percent": {"answer": "15% of 200 = 30.", "generated_tokens": 13, "seconds": 5.928, "contains_expected": true}}}

===== END EVIDENCE DIGEST =====

===== REFERENCE EXCERPTS FROM PUSHED FILE: README.md (line-numbered selected lines) =====
1: # Fraction Compressor v0.4
3: **One base model. Many tiny patch files. Swap a file, swap the behavior.**
5: What "fraction" means here: not math fractions. A fine-tuned AI model is a base model plus a patch (the weight difference between the two). This tool keeps only a fraction of that patch's information, stored at about 1 bit per weight, in a file small enough to swap in and out live.
7: ![How Fraction Compressor v0.4 works](docs/how-it-works.svg)
9: ## In plain words
11: A fine-tuned model differs from its base model by a patch (the delta). A normal patch is almost as big as the model itself. Fraction Compressor stores that patch in a factored form whose structure is kept as 1-bit signs, priced byte for byte by the code: 0.28 bits per weight for one large layer at rank 32 (the exact price depends on layer size and rank). v0.4 runs it through a factored runtime: two small multiplies, Y = (X U) V^T, without ever rebuilding the full weight matrix. One layer stored the normal way takes 8.4 MB; our rank-32 file takes 144 KB, and swapping patches is just loading a different small file. Compressing a patch is offline work done once with the full delta; the saving is in storage and at run time.
13: ## Do it yourself
15: You need two models: a base model and a fine-tuned version of that same base, in safetensors format.
17: 1. Make a patch from the pair (rank 32 everywhere, or pass a per-layer recipe file with `--recipe` instead of `--rank`):
18:    `python examples/make_patch.py --base <base-model-dir> --finetuned <finetuned-model-dir> --rank 32 --out patch.npz`
19:    The script subtracts the two models layer by layer, squeezes the difference into the factored format, and writes one patch file. It prints the patch's exact byte price next to the full difference at normal precision.
20: 2. Check the patch any time:
21:    `python examples/make_patch.py --verify patch.npz --base <base-model-dir> --finetuned <finetuned-model-dir>`
22: 3. Use it: load the patch together with the base model, as in `examples/hotswap_demo.py`, where patches swap in and out of one running base model live.
24: On the model pair used in this repo's benchmark (Qwen2.5-0.5B base and Instruct), rank 32 gives a patch priced at 19,434,496 bytes against 987,922,432 bytes for the full difference, about 51x smaller. The full run is saved at `results/make_patch_demo.txt`.
26: ## How this is different
28: - **From memory files and system prompts** (the text files an AI agent reads, like a personality or memory file): those are words the model reads as instructions, they take up prompt space, and a later instruction can override them. A patch here is numbers applied to the model's own weights. The behavior changes in the math itself, uses no prompt space, and cannot be talked away.
29: - **From an adapter (like LoRA):** an adapter is a new add-on trained for one task, usually stored at normal precision. This tool takes a fine-tune that already exists and squeezes the difference between it and its base model into a 1-bit factored file, so an existing fine-tune becomes a small patch you can swap.
30: - **From shrinking a whole model (quantization):** that makes the one model smaller and slightly changes everything it does. This shrinks only the patch, so one base model stays exact and carries many behaviors, one small file each.
34: ## Prior art
36: Compressing a fine-tune's difference is an established research area, and this project builds on published methods, ideas only, no code: BitDelta (1-bit delta compression of fine-tuned models, NeurIPS 2024, arXiv:2402.10193), Delta-CoMe (SVD-based mixed-precision delta compression, NeurIPS 2024, arXiv:2406.08903), and LittleBit (arXiv:2506.13771). All code in this repo is original and was written during the event. What is ours is not the 1-bit format itself: it is the in-loop recipe search and judging by Muse Spark, the forced-multiply runtime, the first-token gate diagnosis with its force-start control, and the verification harness. Full credits: [NOTICE.md](NOTICE.md).
38: ## Benchmark results
40: The benchmark compares three runs on the same questions: the base model alone, the base model with the full patch, and the base model with our compressed patch. The score is how strongly the model backs the correct answer (a log score; higher is better). "Gap closed" is the share of the base-to-full score gap that a compressed patch recovers. One limit applies everywhere below: the share of questions whose first answer token is exactly right stays low for every compressed version (about 1 to 2% on the first pair, about 8 to 9% on the second, 0 to about 3% on the third; the fourth pair is the exception, where the compressed versions reach 26 to 32% against the full patch's own 33.3%), so these are score results, not proof the model solves the tasks.
42: ### Known limit: skills gated by the first token transfer weakly
44: Transfer depends on the skill, and one kind of skill is a weak case for this format. We tested a real one: NuExtract-1.5-tiny (MIT), a fine-tune of the same Qwen base that reads a text and a JSON template and answers with the template filled in. The fine-tune itself passes 9 of 10 test prompts (eight fully clean, one with a single reworded value); the plain base passes 0 of 10, because it stops immediately instead of answering. Our rank-32 patch passes only 1 of 10. The reason is narrow: this skill is decided by the first token the model emits, start the JSON or stop, and the compressed patch usually does not flip that one decision. On the one prompt where it does start, the extraction is fully correct. A control test settles why: force that first token and the plain base completes 7 of 10 cleanly, so in this test most of the skill was already in the base and the fine-tune's main work is the decision to start. The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own score: one clean more than the forced base, which at 10 prompts is within sampling noise, so the gate is the main story and any edge beyond the trigger is small at most. Making the patch bigger barely moves this boundary: a rank-64 patch (37,044,736 bytes) and a rank-128 patch (72,265,216 bytes) each pass 2 of 10. Spending the same bytes differently did worse, not better: a Muse Spark recipe that puts most of the rank-32 budget into the embedding and the attention output layer (19,434,400 bytes, the same budget) passes 0 of 10, and measured directly at the first token, its average start-vs-stop margin sits further from opening the gate than the uniform patch's. Broad behavior transfers much better under the same format: the Instruct patch below closes 23.2% of the score gap on 96 fresh questions, with wins you can see in the live hot-swap demo. So the limit is format-gated, not general. Full records: `results/skill_demo.json`, `results/skill_demo_forced.json`, `results/skill_demo_ranks.json`, `results/skill_demo_recipe.json`, and the consultation behind this wording in `results/skill_limit_consultation.md`.
46: ### First pair: Qwen2.5-0.5B base and Instruct
48: Muse Spark proposed uneven per-layer compression recipes (the Alien Sweep). The search winner, mlp_behemoth, is byte-unfair: at 21,719,776 bytes it spends 11.8% more than the human recipe's budget, so it is named only as the parent. The headline recipe is its byte-fair variant, mlp_behemoth_lite: 19,358,176 bytes, fewer than the human uniform rank-32 recipe's 19,434,496 bytes.
50: The check that matters is fresh questions the search never saw. That set grew from 24 to 96 questions. On all 96, lite closes 23.2% of the gap, against 2.1% for the human recipe. Lite also wins on each half alone: 9.5% vs 1.6% on the original 24 questions, and 30.4% vs 2.3% on the 72 new ones. An early read from the first small fresh set was that the lead might shrink on fresh questions; on the bigger set the lead grew instead, so that worry did not survive. Lite does not win every kind of question: on knowledge questions the human recipe closes more of the gap (7.8% vs 3.7%); lite's lead comes from the instruction and math questions.
52: ### Second pair: SmolLM2-360M base and Instruct
54: The same contest ran on a second, different model pair. The search winner there (o-down supercharge) was byte-unfair too, so the byte-fair winner is its byte-matched variant, o-down-rebalanced: 19,683,328 bytes, inside the human recipe's budget of 19,705,856 bytes. On the same 96 fresh questions it beats the human uniform recipe by 0.293 score points on average, and it wins on both halves of the set separately.
56: One warning that applies to this pair only: every compressed version scores better than the full patch itself, so the gap-closed percentage goes above 100% here. That means the percentage is NOT a share of the fine-tune recovered for this pair. For this pair, the raw score margin (0.293 points) is the honest measure.
58: ### Third pair: Llama 3.2 1B base and Instruct
60: The same contest also ran on Meta's own open weights, Llama 3.2 1B base and Instruct. The search winner, no_embed_mlp_spread, was byte-unfair again: at 34,690,048 bytes it spends 38.0% more than the human recipe's budget of 25,143,296 bytes, so it is named only as the parent. The headline recipe is its byte-fair variant, no_embed_mlp_spread_balanced: 24,515,584 bytes, inside the budget.
62: On the same 96 fresh questions, the byte-fair variant scores -12.714 against the human uniform recipe's -14.201: it closes 15.9% of the gap, while the human recipe closes -7.6%, which is below the base model itself (-13.718), so on this pair the plain human recipe makes the score worse than using no patch at all. The byte-fair variant also wins on each half alone: 20.0% vs -1.7% on the original 24 questions, and 14.8% vs -9.1% on the 72 new ones.
64: Recovery on this pair is weaker than on the other two pairs (15.9% here against 23.2% on the Qwen pair), and first-token accuracy stays low for every co
[EXCERPT TRUNCATED BY LENGTH]
===== END EXCERPTS README.md =====

===== REFERENCE EXCERPTS FROM PUSHED FILE: NOTICE.md (line-numbered selected lines) =====
1: # NOTICE: prior art, attribution, and originality
3: ## This project's own work
6: are original work by Vinay K Ganji Krishna, written during the Meta Global
7: AI Developer Hackathon (October 26 to November 4, 2026) and released under
8: the MIT License (see LICENSE). No third-party code is included in this
11: ## Published methods this work builds on
13: Compressing the difference between a base model and its fine-tune is an
18: - **BitDelta** (Liu et al., NeurIPS 2024, arXiv:2402.10193): 1-bit
21:   `examples/bitdelta_baseline.py` implements the paper's initialization
23:   training), and `results/bitdelta_baseline.json` reports how it scores
25: - **Delta-CoMe** (Ping et al., NeurIPS 2024, arXiv:2406.08903):
28:   the same. The lesson that where the bytes go matters more than how
30: - **LittleBit** (Lee et al., arXiv:2506.13771): extreme low-bit
32:   the author's earlier Fraction Compressor versions (v0.1 to v0.3, in
33:   the original repository) explored this direction; the factored form
36: ## What is ours
40: this repository are not the 1-bit delta format itself. They are:
42: - the in-loop recipe search and judging: Muse Spark proposes the
47:   patches swap in and out of a running base model live;
48: - the first-token gate diagnosis (skills whose first generated token
53:   scripts, cross-checked by independent models, and a sample picked
54:   with true quantum random numbers from IBM Quantum hardware was
57: ## Models
59: This repository distributes no model weights and no tokenizer files.
60: Experiments download models separately from Hugging Face, under each
61: model's own license: Qwen/Qwen2.5-0.5B and Qwen2.5-0.5B-Instruct
62: (Apache 2.0), HuggingFaceTB/SmolLM2-360M and SmolLM2-360M-Instruct
63: (Apache 2.0), meta-llama/Llama-3.2-1B and Llama-3.2-1B-Instruct
64: (Llama 3.2 Community License).
===== END EXCERPTS NOTICE.md =====

===== REFERENCE EXCERPTS FROM PUSHED FILE: docs/why-it-matters.md (line-numbered selected lines) =====
1: # Why it matters
3: A fine-tuned model is a base model plus a patch: everything training changed, and normally that patch is nearly as big as the model itself. This tool squeezes an existing fine-tune's patch into a file of about 19 MB instead of 1 GB, at 1 bit per weight. One base can then carry many behaviors, one small file each.
5: ## Three uses
7: - **Many behaviors, one model.** Fifty fine-tunes the normal way means fifty full models; as patches, fifty small files on one base.
8: - **Live switching.** A patch swaps in or out in a tenth of a second while the base keeps running, changing behavior mid-conversation.
9: - **Cheap to move.** A 19 MB file can be sent, downloaded on a slow link, or carried on a small device. A 1 GB model often cannot be.
11: ## How it differs from a download or a repo
13: Downloading a fine-tune gives you the whole model, full size. Small adapters like LoRA exist, but an adapter is a new add-on trained for one task. This tool starts from a fine-tune that exists and converts it, with no retraining: point the script at a base and its fine-tune, and it writes the patch and measures how much behavior the patch carries.
15: Two honest costs: making a patch needs both full models once, and running one needs the base in memory. The saving is in storing and moving behaviors.
17: ## What bound it breaks, and what it does not
19: The usual assumption is that at 1 bit per weight, nothing useful survives. Done the plain way, that holds: on Llama 3.2 1B, spreading the budget evenly scored below the base model itself, worse than no patch. Spending the same bytes where they matter kept a real share: 15.9% of the gap closed there, 23.2% on the Qwen pair. So one bound breaks: useful behavior survives smart squeezing.
23: Against the simplest rival, a plain 1-bit delta (the BitDelta initialization), the honest picture is two budgets, not one: on the Qwen pair a plain 1-bit delta cannot be smaller than about 62 MB, so at our 19 MB size it does not exist, while at its own 62 MB floor it closes more of the gap than our format does at the same price (43.6% against 38.5%). Our format's win is reach: it works at sizes the plain format cannot reach. Full record: `results/bitdelta_baseline.json`.
25: ## The known limit
27: One kind of skill transfers weakly: skills decided by the first token, like "start the JSON or stop." On a JSON-extraction fine-tune, the full fine-tune starts on 9 of 10 prompts, the base on 0, the patch on 1. Measured at the first token, the patch moves the model halfway toward starting (base -6.33, patch -1.29, full fine-tune +4.60) but usually does not cross. On the one prompt where it does start, the extraction is fully correct.
29: The author's intuition: the knowledge is there, it just needs to know to start. The control test has now been run, and it mostly backs him: force the fine-tune's first token and the plain base completes 7 of 10 cleanly (8 of 10 counting a partial), so in this test most of the extraction skill was already in the base, and what the fine-tune mainly installs is the decision to start. The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own unforced score. That is one clean more than the forced base, which at 10 prompts is within sampling noise, so the honest reading is: the gate is the main story, and any edge beyond the trigger is small at most. Full records: `results/skill_demo_forced.json`; the earlier debate is in `results/why_debate.md`, and the five-way validation of this test (script recomputation, Muse Spark, Muse Glimmer, Gemini, and Muse Spark Open via Baseten and via Fireworks) is in the `results/` files with `validation_forced` in their names.
===== END EXCERPTS docs/why-it-matters.md =====
```

### Final prompt: adjudication and completion

```text
You are Muse Glimmer completing a strict repo audit sweep. Three first-pass audit replies are supplied below. Some were based on an evidence digest that omitted fields actually present in the pushed source files. A corrected evidence pack follows. Your job now is to ADJUDICATE and COMPLETE the sweep.

Rules:
- Withdraw any first-pass finding contradicted by the corrected evidence pack. Explicitly list withdrawals in one short section.
- Retain genuine first-pass findings, but restate each once only, with severity, category, exact location, problem, and correction.
- Audit the candidate passages in the corrected pack that the first pass did not reach. Add a finding only if the passage is genuinely wrong, stale, internally inconsistent, incomplete in a way a judge would catch, or outruns evidence. If a candidate is defensible, name it in the "candidates cleared" list, not as a finding.
- End with OVERALL VERDICT: YES or NO on whether the pushed repo at 3933fae is clean to submit as-is, in one sentence.
- Most serious first. Maximum 3000 words. Reason efficiently; do not narrate claim-by-claim.

===== FIRST-PASS REPLY A: README =====
**FINDINGS – README.md only**

### 1. Factual arithmetic error – layer size example
* Severity: HIGH
* Category: arithmetic/factual error
* File + location: README.md – “In plain words” paragraph
* Quoted phrase: “One layer stored the normal way takes 8.4 MB; our rank-32 file takes 144 KB”
* Problem: Evidence digest independent arithmetic spot calculation uses 8,388,608 bytes / 147,456 bytes = 56.888889 for the one-layer example. 8,388,608 bytes = 8.0 MB, not 8.4 MB. 147,456 bytes = 144 KB is correct. The 8.4 MB figure is not supported by the pushed digest.
* Recommended correction: Replace “8.4 MB” with the digest-supported 8,388,608 bytes ≈ 8.0 MB, or state the exact byte values used in the repo, and keep the 144 KB rank-32 figure.

### 2. Claim outrunning evidence – BitDelta baseline gap-closed percentages
* Severity: HIGH
* Category: claims outrunning evidence / UNVERIFIABLE
* File + location: README.md – “Baseline: a plain 1-bit delta, priced honestly”
* Quoted phrase: “the BitDelta initialization … closes 43.6% of the gap on the same 96 questions, against 38.5% for our factored format at uniform rank 108 priced just under it (61,258,816 bytes).”
* Problem: Evidence digest provides BitDelta pricing: n_matrices 169, bitdelta_init_price_bytes 61745828, factored_matched_price_bytes 61258816, factored_rank_plus_one_price_bytes 61809136, and mean_target_logprob values for bitdelta_init -10.012813627503721 and factored_uniform_rank108 -10.146044864550612. No gap_closed percentages for these two configs are supplied in the digest. The 43.6% vs 38.5% numbers are therefore UNVERIFIABLE from the pushed result JSON at head 3933fae16f5e1673cac38a000533a35fb7b0ecda.
* Recommended correction: Either cite the exact result file and values that produce 43.6% / 38.5% and add them to the evidence digest, or downgrade the statement to UNVERIFIABLE and remove the specific percentages until they are verifiable from pushed results.

### 3. Unverifiable / inconsistent bits-per-weight claim
* Severity: MEDIUM
* Category: stale / unverifiable number
* File + location: README.md – “In plain words”
* Quoted phrase: “priced byte for byte by the code: 0.28 bits per weight for one large layer at rank 32 (the exact price depends on layer size and rank).”
* Problem: Evidence digest gives Qwen pair all-in effective bits/weight for uniform price = 0.314753 bpw; for lite = 0.313517 bpw. No pushed evidence supports a 0.28 bits/weight figure for “one large layer at rank 32”. The claim is UNVERIFIABLE from the digest and inconsistent with the repo-wide effective bits/weight numbers that are available.
* Recommended correction: Replace the 0.28 bits/weight example with a digest-supported figure, e.g., the repo-wide effective bits/weight ≈0.315 bpw for uniform rank-32 on the Qwen pair, or qualify the 0.28 figure with the exact layer dimensions and cite the specific pushed calculation.

---

Clean-area notes, max three:
* First-pair gap-closed and byte budgets for mlp_behemoth_lite vs uniform_rank32 match digest: lite 23.1923% vs uniform 2.0764%, bytes 19,358,176 vs 19,434,496, over_pct 11.8%.
* Second-pair raw score margin and >100% gap-closed warning are consistent with digest: o-down-rebalanced mean -8.072964749082066 vs uniform -8.366280457949834, gap_closed 108.0783% vs 101.4816%.
* Third-pair and fourth-pair byte-fair comparisons, first-token accuracies and subset wins/losses match the pushed heldout96 JSONs.

===== FIRST-PASS REPLY B: NOTICE + WHY-IT-MATTERS =====
**FINDINGS**

* **CRITICAL – Claim outruns evidence / UNVERIFIABLE – docs/why-it-matters.md – “Against the simplest rival, a plain 1-bit delta (the BitDelta initialization), the honest picture is two budgets, not one: on the Qwen pair a plain 1-bit delta cannot be smaller than about 62 MB, so at our 19 MB size it does not exist, while at its own 62 MB floor it closes more of the gap than our format does at the same price (43.6% against 38.5%). Our format's win is reach: it works at sizes the plain format cannot reach. Full record: `results/bitdelta_baseline.json`.”**
Category: factual / evidence gap. Problem: Evidence digest supplies BitDelta pricing `bitdelta_init_price_bytes=61745828` and `factored_matched_price_bytes=61258816` and mean_target_logprob values `-10.012813627503721` vs `-10.146044864550612`. No gap-closed percentages 43.6% / 38.5% are present in the digest, nor the base/full delta logprobs needed to recompute them. The claim is therefore UNVERIFIABLE from supplied evidence and outruns the digest. Recommended correction: either cite the exact gap-closed numbers from `results/bitdelta_baseline.json` in the digest or rephrase to “gap closed values as reported in results/bitdelta_baseline.json” and ensure the digest contains those recomputed percentages.

* **HIGH – Claim outruns evidence / UNVERIFIABLE – docs/why-it-matters.md – “The known limit… Measured at the first token, the patch moves the model halfway toward starting (base -6.33, patch -1.29, full fine-tune +4.60) but usually does not cross.”**
Category: factual / evidence gap. Problem: The digest contains `results/skill_demo_recipe.json` first_token_margins definition and a margin for the Spark recipe `-4.14`, and `results/skill_demo_forced.json` counts, but no first-token logprob margins `-6.33 / -1.29 / +4.60` for base / uniform rank-32 patch / full fine-tune. The numbers are not supplied and cannot be recomputed from the digest. Recommended correction: remove the numeric margins or add the exact margin values to the evidence digest with source file and recomputation.

* **HIGH – Claim outruns evidence / UNVERIFIABLE – docs/why-it-matters.md – “Full records: `results/skill_demo_forced.json`; the earlier debate is in `results/why_debate.md`, and the five-way validation of this test (script recomputation, Muse Spark, Muse Glimmer, Gemini, and Muse Spark Open via Baseten and via Fireworks) is in the `results/` files with `validation_forced` in their names.”**
Category: judge/submission risk. Problem: Digest provides `results/skill_demo_forced.json` counts, but does not list `results/why_debate.md` nor any `*validation_forced*` files. Existence and content of those files cannot be verified from pushed result JSON. Recommended correction: limit the claim to files present in the digest or add digest entries for `why_debate.md` and the validation_forced files.

* **MEDIUM – Stale / imprecise wording – docs/why-it-matters.md – “One base can then carry many behaviors, one small file each.” / “A patch swaps in or out in a tenth of a second while the base keeps running”**
Category: consistency. Problem: Hot-swap evidence in digest is not provided; `results/hotswap_demo.json` keys are listed but no swap time is in the digest. The “tenth of a second” claim is supported by reference excerpt `docs/demo_script.md` line 69 “patch loaded live in 0.09s”, which is reference material, not primary evidence digest. Recommended correction: cite the hotswap_demo timing from the pushed result JSON in the digest or qualify as “≈0.09 s per demo transcript”.

* **MEDIUM – Rounding presentation – docs/why-it-matters.md – “15.9% of the gap closed there, 23.2% on the Qwen pair.”**
Category: arithmetic. Problem: Recomputed from digest: third pair contender gap closed `0.15852079567397595` = 15.85% → 15.9% OK; Qwen pair lite gap closed `0.2319228264458408` = 23.19% → 23.2% OK. No error, but note rounding is consistent.

* **LOW – NOTICE.md – “All code, documentation, evaluation items, and results in this repository are original work by Vinay K Ganji Krishna, written during the Meta Global AI Developer Hackathon (October 26 to November 4, 2026)…”**
Category: factual. Problem: Date range is in the future relative to typical publication; cannot be verified from digest. No contradiction found, but claim is UNVERIFIABLE from evidence. Recommended correction: keep as attribution statement; no numeric correction needed.

Clean-area bullets:
* Qwen pair headline gap closed 23.192% vs uniform 2.076% and byte-fair lite within uniform budget is supported by `results/alien_sweep_heldout96.json` verdict fields.
* Llama 3.2 1B uniform rank32 gap closed -7.636% vs byte-fair contender +15.852% is supported by `results/third_pair_heldout96.json`.
* Skill demo forced-start counts base 7 clean/1 partial/2 failed and base+patch 8 clean/1 partial/1 failed match `results/skill_demo_forced.json`.

===== FIRST-PASS REPLY C: DEMO SCRIPT + BUILD PLAN =====
**FINDINGS**

* **HIGH – Submission rule / demo opening mismatch**
  * File: `BUILD_PLAN.md` – Scope / Demo video plan (approved by Vinay, Oct 26)
  * Quote: “The 3-minute demo video opens with one line stating what was pre-existing and what was built this week.”
  * File: `docs/demo_script.md` – 0:00-0:25 The product: a fine-tune as a tiny patch file
  * Problem: The pushed demo script opens with a title card / narration about the product – “This is Fraction Compressor. It turns a fine-tuned model into one patch file: about nineteen megabytes instead of about a gigabyte…”. The required pre-existing / built-this-week disclosure is placed at 0:25-0:44 “Honesty: one-bit delta compression is a published idea… Built fresh this week: the factored runtime…”. The opening line required by the submission rules is therefore not the first on-screen / spoken line.
  * Recommended correction: Move the required pre-existing vs built-this-week line to the very first on-screen/narration slot 0:00-0:25 and keep the product intro after it, or update BUILD_PLAN to reflect the approved script ordering.

* **HIGH – Approved timing shape vs script timing**
  * File: `BUILD_PLAN.md` – Demo video plan (approved by Vinay, Oct 26)
  * Quote: “Shape: 0:00 opening + problem; 0:30 the hot-swap moment; 1:30 benchmark numbers, including one Alien Sweep line…; 2:15 Muse Spark judging + quantum audit, one line each”
  * File: `docs/demo_script.md` – 1:21-1:48 The demo moment: swap a file, change the behavior
  * Problem: The hot-swap demo is scripted at 1:21-1:48, not ~0:30 as per the approved shape. Benchmark numbers are scripted at 1:48-2:31, later than the 1:30 target. The plan’s timing anchors are not met by the pushed script.
  * Recommended correction: Re-time the script to place the hot-swap moment around 0:30 and benchmark numbers around 1:30, or formally amend the approved plan to the 1:21/1:48 timings used in the script.

* **MEDIUM – Unverifiable audit claim**
  * File: `docs/demo_script.md` – 2:31-2:44 Checked, not just claimed
  * Quote: “Muse Spark judged every headline claim and had to cite the file behind each one. A quantum computer's random numbers picked the audit sample: all forty-one audit checks passed.”
  * Problem: The evidence digest computed from pushed result JSON at head 3933fae16f5e1673cac38a000533a35fb7b0ecda contains no audit sample size, quantum backend/job/seed record, or “41 of 41 checks passed” record. The claim is therefore UNVERIFIABLE from the supplied pushed evidence.
  * Recommended correction: Either add the audit result file and quantum sampling log to the pushed repo and reference it, or change the script to a verifiable statement supported by the pushed results.

* **MEDIUM – Unverifiable BitDelta baseline gap-closed percentages**
  * File: `docs/demo_script.md` – 1:48-2:31 The numbers
  * Quote: “at sixty-two million bytes a one-bit patch closes more gap… plain BitDelta-style init gap closed 43.6% vs factored rank-108 gap closed 38.5% at 61,258,816 bytes”
  * Problem: The digest provides BitDelta init price 61,745,828 bytes and factored matched price 61,258,816 bytes and mean_target_logprob values for the two configs, but does not provide base/full-delta means for that pair nor the derived gap_closed percentages 43.6% / 38.5%. The percentages are UNVERIFIABLE from the pushed evidence digest.
  * Recommended correction: Cite the exact result file and values used for the 43.6% / 38.5% gap-closed computation, or remove the percentages from the script.

* **LOW – Rounding presentation**
  * File: `docs/demo_script.md` – 1:48-2:31 The numbers
  * Quote: “The patch is fifty-one times smaller: nineteen million bytes against nine hundred eighty-eight million.”
  * Problem: 987,922,432 / 19,434,496 = 50.833447 per independent arithmetic spot calculation. “51x” is a rounded presentation; acceptable but note rounding.
  * Recommended correction: No change required; optionally note “≈51×”.

Clean-area bullets
* The Qwen 0.5B held-out 96 numbers are consistent: lite gap_closed 0.2319228264458408 ≈23.2% vs uniform 0.020763686533300157 ≈2.1%, lite within uniform budget, beats uniform on combined96 and both subsets.
* The Qwen 1.5B fourth-pair numbers are consistent: Down Dominator 38,623,232 bytes inside 39,046,144 byte budget, mean -6.343687772752477 vs uniform -6.478079873557243, raw margin ≈0.134 nats, full delta 3,087,138,816 bytes, ratio ≈79.9×.
* The full-delta / patch byte sizes used in the script match the pushed results: full delta 987,922,432 bytes, uniform rank-32 19,434,496 bytes.

===== CORRECTED EVIDENCE PACK =====

1. BitDelta source values, from pushed results/bitdelta_baseline.json (these were omitted from the first-pass digest):
- references: base_mean_target_logprob -11.149778062515304; full_delta_mean_target_logprob -8.542466235416498.
- bitdelta_init: mean -10.012813627503721, gap_closed overall 0.43606768595711076, price 61,745,828.
- factored_uniform_rank108: mean -10.146044864550612, gap_closed overall 0.3849686054166987, price 61,258,816.
- two_budget_curve repeats exactly those gap_closed values. Therefore 43.6% and 38.5% ARE in the pushed source file.

2. First-token margins, from pushed results/skill_demo_recipe.json (omitted from first-pass digest):
- mean_margin: base -6.332; rank32_uniform -1.2942; full_delta +4.6005; spark_recipe -4.1422.
- gate_open_count_of_10: base 0; rank32 1; full 10; recipe 0. Therefore why-it-matters' -6.33 / -1.29 / +4.60 values are source-backed.

3. Quantum audit, from pushed results/quantum_audit.json (omitted from first-pass digest):
- quantum_source: fixture fixtures/qrng_fixture.json, backend ibm_fez, job_id dbfouq7pc3tc739nvkt0, 32 qubits, 2048 shots, 3 qpu_seconds, 8192 random bytes.
- selection: 8 distinct indices [1,10,20,8,21,12,5,22] from 24 held-out items.
- summary: n_checks 41, n_passed 41, all_pass true. Therefore "41 of 41" is source-backed.

4. Hot-swap timings, from pushed results/hotswap_demo.json:
- swaps seconds: 0.104 and 0.087. Therefore "about a tenth of a second" is source-backed.

5. Validation-file existence in the pushed repo (from the snapshot sync record of pushed paths):
- results/why_debate.md was pushed.
- Pushed validation_forced files: results/glimmer_validation_forced.md, results/spark_validation_forced.json, results/spark_validation_forced.md, results/gemini_validation_forced.md, results/sparkopen_validation_forced.md, results/sparkopen_fireworks_validation_forced.md. Therefore why-it-matters' five-way validation file claim is not based on missing files.

6. One-layer storage calculation, from pushed src/factored.py:
- storage_bytes(rank, shape): ceil(m*rank/8) + 4*m + 2*n*rank, where m=rows, n=cols.
- For shape 2048x2048, rank 32: 8192 + 8192 + 131072 = 147,456 bytes.
- A full fp16 2048x2048 matrix is 8,388,608 bytes. That is 8.388608 decimal MB (SI), or 8.0 MiB. README says "8.4 MB" and "144 KB" (147,456 bytes = 144 KiB exactly, or 147.456 decimal KB). Judge whether README's units are actually wrong or merely SI/rounded; do not call 8.4 decimal MB an arithmetic error if it is correct in SI units.
- The same formula gives 0.28125 bits per weight for that one 2048x2048 layer: 147,456*8 / 4,194,304 = 0.28125. Therefore README's "0.28 bits per weight for one large layer at rank 32" is derivable from pushed code, even though it was not in the digest.

7. First-pair per-bucket combined-96 values, from pushed results/alien_sweep_heldout96.json:
- Knowledge: base -9.691128, full -7.848184; uniform factored -9.546934 (gap closed 7.82%); lite factored -9.623622 (3.66%).
- Instruction: base -16.278045, full -14.238147; uniform -15.938609 (16.64%); lite -15.564867 (34.96%).
- Math: base -7.480161, full -3.541069; uniform -7.801378 (-8.16%); lite -6.446759 (26.23%).
Therefore README's statement that uniform closes more knowledge gap (7.8% vs 3.7%) and lite's lead comes from instruction and math is source-backed.

===== CANDIDATE PASSAGES NOT REACHED BY THE FIRST PASS =====

A. Effective bits-per-weight language:
- README.md line 5: the patch's information is "stored at about 1 bit per weight".
- README.md line 11: the structure "is kept as 1-bit signs" and the priced example is 0.28 bpw for one large layer.
- docs/why-it-matters.md line 3: the patch is squeezed "at 1 bit per weight".
- Evidence: the factored format's all-in priced rate on the Qwen pair is 0.314753 bpw (uniform) and 0.313517 bpw (lite), because low rank makes the total smaller than the plain 1-bit floor; only the U signs are 1 bit per stored sign entry, while V is fp16 and scales are fp32. Decide strictly whether "about 1 bit per weight" / "at 1 bit per weight" is a factual error, a misleading simplification, or defensible shorthand, and what correction if any.

B. Fourth-pair ratio wording:
- README.md line 72 and BUILD_PLAN.md scale-test note: "about 79x smaller" for the 1.5B patch vs 3,087,138,816-byte full delta.
- Exact ratios: full / Down Dominator 38,623,232 = 79.9326; full / uniform 39,046,144 = 79.0657.
- docs/demo_script.md on-screen text says "about 80x smaller".
Decide whether "about 79x" is an error needing correction in README/BUILD_PLAN, and severity.

C. NOTICE model/license list completeness:
- NOTICE.md "Models" section lists only: Qwen2.5-0.5B pair (Apache 2.0), SmolLM2-360M pair (Apache 2.0), Llama-3.2-1B pair (Llama 3.2 Community License).
- Pushed experiments also use Qwen/Qwen2.5-1.5B and Qwen2.5-1.5B-Instruct (examples/fourth_pair_stage2.py lines 1, 24, 896-897 identify them, Apache 2.0), the subject of README's fourth-pair section.
- Pushed skill test uses numind/NuExtract-1.5-tiny (examples/skill_demo.py lines 10-11 and 230 identify it, MIT license), the subject of README's Known limit section.
Decide whether NOTICE's Models section is materially incomplete.

D. Originality/authorship wording:
- NOTICE.md lines 5-9: "All code, documentation, evaluation items, and results in this repository are original work by Vinay K Ganji Krishna, written during the Meta Global AI Developer Hackathon... No third-party code is included... and no code was copied..."
- README.md credits: "Implementation, benchmarking, and documentation were carried out with Ember, an AI agent powered by Muse Spark, working under the author's direction" and the benchmark's 96 fresh questions and recipes were generated by Muse Spark (README Alien Sweep / held-out text; BUILD_PLAN).
Decide whether NOTICE's unqualified "original work by Vinay" is inconsistent or overbroad next to the README's own crediting, and what correction if any.

E. Universal gate wording:
- NOTICE.md lines 47-51: the contribution is "the first-token gate diagnosis (skills whose first generated token decides success transfer weakly through any small patch)".
- Evidence base: one gated skill (NuExtract JSON extraction) on one model pair, tested at ranks 32/64/128 and one Spark recipe; README's own Known limit section scopes it to "one kind of skill" and "in this test".
Decide whether "any small patch" outruns the evidence.

F. BUILD_PLAN stale scope items (pushed BUILD_PLAN.md):
- Scope item 1: factored runtime; "Memory read per token is the headline metric." No supplied result file measures memory read per token; the repo reports storage bytes, patch sizes, swap times (0.104/0.087 s), and peak RSS for runs. Decide whether the plan promises a headline metric the repo never reports.
- Scope item 2: "End-to-end task-accuracy benchmark... scored on task answers". The benchmark's headline metric is mean target logprob; README itself warns first-token accuracy stays low and "these are score results, not proof the model solves the tasks". Decide whether "task-accuracy" mislabels the delivered benchmark.
- Scope item 3: "Muse Spark (Meta Model API) runs the same probe sets as a hosted reference, and Muse Spark Open is the planned open-weight candidate if time allows." Later pushed text (Expanded scope item 2/3 and working notes) and README describe what actually happened: Spark generated fresh probes, proposed recipes, and judged claims; Spark Open via Baseten generated recipes and later validated results. Spark did not run the probe sets as a hosted reference model in the benchmark table. Decide whether Scope item 3 is stale/superseded inside the same pushed document.

G. BUILD_PLAN internal force-start contradiction:
- Working note "Force-start control test (Oct 28)": the patch result is described as "a small real edge beyond the trigger (it cleans the two prompts the forced base still fails, and loses one the forced base cleans), but the gate is the dominant term."
- Later working note "Force-start validation (Oct 28)": "One wording correction survived: Spark 1.3 and both Spark Open routes ruled 'a small real edge' too strong, because the forced patch's lead over the forced base is one clean prompt out of 10, inside sampling noise; README and why-it-matters.md now read 'one clean more than the forced base, which at 10 prompts is within sampling noise...'"
Decide whether the earlier note is a stale/superseded claim left standing in the same document.

H. Demo narration ambiguity:
- docs/demo_script.md numbers narration: "Same pattern on SmolLM2; on a model three times bigger, Spark's recipe won by nought point one three four nats, inside budget."
- Facts: SmolLM2-360M is smaller than Qwen2.5-0.5B; the "three times bigger" model is the separate Qwen2.5-1.5B scale test (1.5B vs 0.5B parameters). The on-screen notes list SmolLM2-360M and the Qwen2.5-1.5B scale lines as separate items.
Decide whether the spoken sequence misleadingly attaches "three times bigger" to SmolLM2.

I. Demo word count:
- docs/demo_script.md header: "Total narration: 440 words".
- Independent whitespace and word-character counts of the eight NARRATION blocks both give exactly 440.
Decide whether there is any issue. (Expected: clear it if the count is right.)

```

---

# Recheck of corrections (2026-10-28, later the same day)

## Recheck record

- Requested by Vinay ("Go") after the audit above returned an overall verdict of NO. The corrections were applied locally on top of the pushed head `3933fae` and on top of the earlier local literature-citation edits; nothing was pushed as part of this recheck.
- Material given to Glimmer: the full corrected `NOTICE.md`; the corrected `README.md` opening paragraphs plus its Prior art and Author and credits sections; the full current `docs/why-it-matters.md`; and corrected `BUILD_PLAN.md` excerpts (submission rules, Scope, demo video plan bullets, both force-start working notes).
- `docs/demo_script.md` was deliberately NOT edited in this correction pass (a video worker owns it), so the audit's demo-narration-ambiguity finding (finding 8 below) was declared out of scope for the recheck and marked deferred.
- Route: Flash-local call over SSH, same path as the audit (OmniRoute to NVIDIA NIM). Served model confirmed `meta/muse-glimmer-30b`. Usage: prompt 8,281, completion 1,803, total 10,084; finish `stop`; `reasoning_effort: low`. Flash-local NIM call, not logged in `results/api_usage_log.jsonl`; this section is the record.
- Numbering: findings 1 to 11 below follow the parent summary of the adjudicated audit (HIGH: 1 demo opening mismatch, 2 NOTICE Models incomplete, 3 universal gate wording, 4 demo timing shape; MEDIUM: 5 bits-per-weight shorthand, 6 Scope item 3 stale, 7 force-start contradiction, 8 demo narration ambiguity, 9 unmeasured headline metric, 10 benchmark mislabel, 11 originality wording).

## Corrections applied

- NOTICE.md: Models section gained Qwen/Qwen2.5-1.5B and Qwen2.5-1.5B-Instruct (Apache 2.0) and numind/NuExtract-1.5-tiny (MIT); the gate claim was narrowed to the tested scope (NuExtract on the Qwen2.5-0.5B pair, ranks 32/64/128, one Spark recipe); the originality statement now credits Ember (Muse Spark) with implementation, benchmarking, and documentation under Vinay's direction and Spark with the recipes and fresh evaluation questions.
- README.md and docs/why-it-matters.md: the "about 1 bit per weight" shorthand now separates the 1-bit sign storage from the all-in priced rate of about 0.31 bits per weight on the Qwen pair.
- BUILD_PLAN.md: the demo opening rule carries a dated Oct 28 amendment (product-first, disclosure at about 0:25); the demo timing shape was corrected to the script's actual timings; Scope item 3 was rewritten to the actual Spark and Spark Open roles; the force-start control-test note's "small real edge beyond the trigger" phrase is marked superseded, pointing at the validation note; Scope item 1's headline metric was replaced with the reported metrics (storage bytes, swap time, peak RSS) with the unmeasured metric explicitly disclaimed; Scope item 2 was relabeled as a score benchmark on mean target logprob with first-token accuracy alongside.

## Glimmer recheck reply (verbatim)

Finding 1: RESOLVED
BUILD_PLAN now states "Amended Oct 28: Vinay chose a product-first opening; the pre-existing vs built-this-week disclosure sits at about 0:25 in the script, and this plan is amended to match" and the demo plan lists "0:00 product opening; about 0:25 the line stating what was pre-existing and what was built this week".

Finding 2: RESOLVED
NOTICE Models section now lists "Qwen/Qwen2.5-1.5B and Qwen2.5-1.5B-Instruct (Apache 2.0), numind/NuExtract-1.5-tiny (MIT)" alongside the other models.

Finding 3: RESOLVED
NOTICE "What is ours" now reads "the first-token gate diagnosis, scoped to what was tested: one gated skill (NuExtract JSON extraction) on the Qwen2.5-0.5B pair transferred weakly through small patches at ranks 32, 64, and 128 and through one Muse Spark recipe, together with its force-start control test".

Finding 4: RESOLVED
BUILD_PLAN demo video plan is corrected: "Shape (corrected Oct 28 to the script's actual timings; the original anchors... are superseded): 0:00 product opening; about 0:25 the line stating what was pre-existing and what was built this week... 1:21 the hot-swap moment; 1:48 benchmark numbers".

Finding 5: RESOLVED
README intro now says "priced all in (signs, factors, and scales together) that comes to about 0.31 bits per weight on the Qwen pair" and docs/why-it-matters.md states "with the patch structure held as 1-bit signs, about 0.31 bits per weight all in on the Qwen pair".

Finding 6: RESOLVED
BUILD_PLAN Scope 3 now reads "Muse Spark (Meta Model API) generated the fresh held-out probe sets, proposed the per-layer compression recipes for the Alien Sweep, and judged the headline claims against the result files. Muse Spark Open (via Baseten, and later Fireworks) generated recipes on the later pairs and ran independent validation passes."

Finding 7: RESOLVED
BUILD_PLAN Force-start control test note now contains "[Wording superseded: the Force-start validation note below records that Muse Spark 1.3 and both Spark Open routes ruled 'a small real edge' too strong... the settled wording is in the README and docs/why-it-matters.md.]" and the validation note records the ruling.

Finding 8: NOT ADDRESSED (deferred)
docs/demo_script.md is owned by a video worker and was not edited in this pass per the recheck scope.

Finding 9: RESOLVED
BUILD_PLAN Scope 1 now states "Headline metrics actually reported: patch storage bytes, patch swap time, and peak memory (RSS) during runs. (An earlier draft named memory read per token as the headline metric; it was never measured and is not claimed.)"

Finding 10: RESOLVED
BUILD_PLAN Scope 2 now states "The headline score is mean target logprob (how strongly the model backs the correct answer), with first-token accuracy reported alongside; these are score results, not proof of task solving."

Finding 11: RESOLVED
NOTICE now states "All code... are original work by Vinay K Ganji Krishna, the sole participant and author of record, produced with AI assistance: Ember... carried out implementation, benchmarking, and documentation under his direction" and README Author and credits matches "Implementation, benchmarking, and documentation were carried out with Ember... working under the author's direction".

NEW ISSUES INTRODUCED BY THE EDITS
None

OVERALL RECHECK VERDICT: CLEAN
