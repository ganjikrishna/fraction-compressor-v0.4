# Glimmer reference check (2026-10-27)

Independent reference verdict on the Alien Sweep headline wording, from Muse Glimmer 30B, a Meta open-weight model the project had not used for any prior validation.

- Route: Flash-local call. Pi's model config on Flash (~/.pi/agent/models.json) routes `nvidia/meta/muse-glimmer-30b` through the local OmniRoute provider (http://localhost:20128/v1, OpenAI-compatible) to NVIDIA NIM. The API response's served-model field confirmed `meta/muse-glimmer-30b`.
- Tokens: prompt 2,579, completion 1,823, total 4,402 (NIM usage as reported by the route; reasoning was returned separately and is not reproduced here).
- This was a Flash-local NIM call through Vinay's own Pi/OmniRoute setup, not a Meta Model API or Baseten call, so it is not logged in results/api_usage_log.jsonl; this file is the record.
- Sources given to Glimmer: results/alien_sweep_stage2.json, results/alien_sweep_heldout.json, results/hotswap_demo.json (headline numbers and caveats only, composed into the prompt below).

## Prompt used (verbatim)

You are giving an independent reference verdict on a compression benchmark's headline wording. You did not run these experiments; judge only whether the headline is honest given the numbers and caveats below.

Context: Fraction Compressor v0.4 stores the weight difference (delta) between a base model (Qwen2.5-0.5B) and its fine-tuned Instruct version as a 1-bit factored patch (per-matrix SVD rank map, 169 matrices). An "Alien Sweep" had Muse Spark propose 5 per-layer rank recipes; a human baseline used uniform rank 32 on every layer. Scoring metric: mean target logprob of the correct answer tokens on 24 short probe questions (knowledge / instruction / math, 8 each). "Gap closed" = (factored - base) / (full delta - base) on that mean logprob; 1.0 would mean the patch fully matches the fine-tune. First-token accuracy was ~0 for all factored configs; the metric is logprob, not task accuracy.

Stage 2 results (24 pre-existing hand-written probe items, the same items the recipes were ranked on):
- mlp_behemoth (Spark recipe): gap closed 45.7%
- uniform rank-32 (human baseline): gap closed 13.3%
- The other 4 Spark recipes ranged from -16.5% to +19.0%.
- Byte caveat: priced on the real model shapes, mlp_behemoth is 21,719,776 bytes, which is 11.8% MORE than uniform rank-32's 19,434,496 bytes. Its Stage 2 win was not byte-fair.

Held-out guard (24 fresh probe items written by Muse Spark after the sweep, never seen during search or ranking):
- mlp_behemoth: gap closed 10.8% (the effect shrank from 45.7% to 10.8% on fresh items)
- mlp_behemoth_lite (a byte-matched variant of the winner, mlp.down trimmed 50 to 40): 19,358,176 bytes, inside the uniform budget, gap closed 9.5%
- uniform rank-32: gap closed 1.6%
- Per-bucket on held-out: uniform actually beat both behemoth variants on knowledge (27.2% vs 26.7% / 25.5% gap closed); on instruction, NO factored config recovered anything (all negative, -17% to -20%); held-out math gap_closed is a ratio artifact because base and full delta differ by only 0.08 nats on math there.
- n = 24 items in each set (8 per bucket). One model pair, one run of experiments.

Live hot-swap demo (same patch format, qualitative): with either factored patch applied to the base model, a strict-JSON prompt went from unparseable rambling (base) to exactly the requested JSON object; a "capital of Japan" prompt went from a repetition loop to one clean sentence; a percent question went from junk text around the right number to a clean "15% of 200 = 30." Patch files ~19.4 MB vs 987,922,432 bytes for the full delta in fp16 (about 51x smaller); swaps took about 0.1 s.

Two independent checks (a script recomputation and Google Gemini) already confirmed the arithmetic exactly and ruled that calling this a "confirmed winner" is too strong.

Proposed headline wording: "mlp_behemoth is a conditionally validated leading recipe."

Questions:
1. Is "conditionally validated leading recipe" an honest headline for these results? Answer yes or no, then explain in at most 5 short bullet points.
2. What ONE wording limit would you add that the authors have not already adopted? (Already adopted: always quote the 45.7% to 10.8% shrinkage next to any Stage 2 figure; always state the byte-fair comparison is the lite variant; never claim task-solving or per-bucket dominance; state the metric is logprob, n = 24 per set, one model pair.)
Keep the whole reply under 300 words.

## Glimmer's reply (verbatim)

No.

* Held-out mean lead is thin and fragile: 10.8% for mlp_behemoth vs 9.5% for byte-matched mlp_behemoth_lite vs 1.6% uniform.
* mlp_behemoth is byte-unfair: 21,719,776 B is 11.8% larger than uniform 19,434,496 B; the fair comparison is the lite variant.
* Stage 2 → held-out shrinkage is severe: 45.7% → 10.8% on fresh items, indicating overfit to the 24 ranking items.
* No per-bucket dominance: uniform beats both behemoth variants on knowledge 27.2% vs 26.7%/25.5%; instruction is negative for all configs -17% to -20%; math gap closed is a ratio artifact.
* n = 24 per set, one model pair, one run, metric is mean target logprob not task accuracy; first-token accuracy ~0 for all factored configs.

One additional wording limit: Never name mlp_behemoth alone as the headline result. Any mention of the recipe must be paired in the same sentence/heading with the byte-fair variant and an explicit “byte-unfair” label, e.g., “mlp_behemoth is byte-unfair; the byte-fair leader is mlp_behemoth_lite”.
