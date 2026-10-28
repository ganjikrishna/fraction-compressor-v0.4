# Muse Spark judging: demo video script claims

Date: 2026-10-28. Judge: Muse Spark 1.3 via the Meta Model API (7,454 tokens: 2,398 prompt, 5,056 completion, of which 3,844 reasoning). Target: docs/demo_script.md read fresh at the start of the pass (the refreshed script, with the 1.5B scale test and the honest baseline in the numbers block and the v2 product-first opening). Method, per the Agents 102 working rules adopted today: every factual claim in the narration and the on-screen figures was extracted (22 claims), the values relied on were pulled from the result files by script and embedded in the judging prompt (Spark never reads our files), and each claim got one verdict: SUPPORTED, NOT SUPPORTED, or ESCALATED, with at most 3 cited files.

Result: **19 SUPPORTED, 3 NOT SUPPORTED, 0 ESCALATED.** The script was NOT edited in this pass; the three problem claims are listed first with the file-supported correction for the fix and re-render.

## Not supported (fix before the final render)

### D3: NOT SUPPORTED
Script (narration, problem block): "This tool keeps a fraction: about one bit per weight."
- Cited files: results/bitdelta_baseline.json, results/alien_sweep_heldout96.json
- Values relied on: priced total 19,434,496 B over 493,961,216 patched weights = 0.315 bits per weight effective
- Note: Recorded effective rate is 0.315 bits per weight, not about one.
- Correction: the format stores 1-bit signs plus fp16 factors and scales; the all-in priced rate on this pair is about 0.3 bits per weight. Honest wording: "about a third of a bit per weight, all in" (or state the sign/factor split plainly).

### D16: NOT SUPPORTED
Script (on screen, numbers block): "patch about 39 MB vs 3,087,138,816 byte full difference, about 79x smaller."
- Cited files: results/fourth_pair_stage2.json, results/fourth_pair_heldout96.json
- Values relied on: full difference 3,087,138,816 B; patch 38,623,232 B; ratio = 79.93
- Note: Ratio 79.93 rounds to 80x, not 79x.
- Correction: "about 80x smaller."

### D22: NOT SUPPORTED
Script (header, production metadata only): "Total narration: 440 words."
- Cited file: docs/demo_script.md
- Values relied on: script whitespace count over the NARRATION blocks = 441 words
- Note: Count is 441 words, not 440 words.
- Correction: 441 by that count; the count will move again whenever the narration text changes, so recompute it at each script edit.

## Supported

- **D1** Patch about 19 MB vs full difference about 1 GB (19,434,496 B vs 987,922,432 B). Cited: results/make_patch_demo.txt, results/hotswap_demo.json.
- **D2** Swap is live in about a tenth of a second (recorded 0.104 s and 0.087 s; transcript 0.09s). Cited: results/hotswap_demo.json, results/hotswap_demo_transcript.txt.
- **D4** Full difference is exactly 987,922,432 bytes. Cited: results/hotswap_demo.json.
- **D5** make_patch printed 19,434,496 B patch, 987,922,432 B full difference, VERIFY: PASS. Cited: results/make_patch_demo.txt.
- **D6** Base returns the right JSON object then rambles; parseable=False. Cited: results/hotswap_demo.json, results/hotswap_demo_transcript.txt.
- **D7** After the swap, the same prompt returns exactly the object; parseable=True. Cited: results/hotswap_demo.json, results/hotswap_demo_transcript.txt.
- **D8** Capital of Japan: base loops the wrong city (Lauderdale) after naming Tokyo once; both patches answer one clean line. Cited: results/hotswap_demo.json, results/hotswap_demo_transcript.txt.
- **D9** Patch is 51x smaller (ratio 50.83). Cited: results/hotswap_demo.json.
- **D10** 96 fresh questions: byte-fair Spark recipe closes 23.2% of the gap, human uniform 2.1% (0.2319 vs 0.0208). Cited: results/alien_sweep_heldout96.json.
- **D11** Winner is mlp_behemoth_lite; the parent mlp_behemoth was byte-unfair (21,719,776 B) and is reference only. Cited: results/alien_sweep_heldout96.json.
- **D12** Same pattern on SmolLM2-360M: byte-fair Spark variant beats uniform on the combined 96 (1.0808 vs 1.0148). Cited: results/second_pair_heldout96.json.
- **D13** Scale test model is three times bigger (Qwen2.5-1.5B vs 0.5B). Cited: results/fourth_pair_stage2.json, results/fourth_pair_heldout96.json.
- **D14** Down Dominator 38,623,232 B is inside the 39,046,144 B uniform budget. Cited: results/fourth_pair_heldout96.json.
- **D15** Scale test margin is 0.134 nats on 96 fresh questions (-6.3437 vs -6.4781). Cited: results/fourth_pair_heldout96.json.
- **D17** At the plain 1-bit floor (61,745,828 B), plain init closes 43.6% vs factored rank-108 at 38.5% (61,258,816 B). Cited: results/bitdelta_baseline.json.
- **D18** At about 19 MB no plain 1-bit delta fits; its floor price is 61,745,828 B. Cited: results/bitdelta_baseline.json.
- **D19** Muse Spark judged every headline claim with a cited file (original pass 10 of 10 SUPPORTED; later passes same format). Cited: results/spark_judging.json.
- **D20** Quantum fixture (IBM ibm_fez job) picked the audit sample; 41 of 41 audit checks passed. Cited: results/quantum_audit.json.
- **D21** BitDelta and Delta-CoMe are published prior art (NeurIPS 2024), credited in NOTICE.md. Cited: NOTICE.md.
