# Glimmer reference addendum: strengthening results (2026-10-27)

Follow-up reference check with Muse Glimmer 30B on the strengthening results,
after the 96-item expansion (pair 1) and the second-pair confirmation
(SmolLM2-360M). Same judge and same questions format as the first reference
(results/glimmer_reference.md), whose stricter ruling the project adopted:
the headline recipe is mlp_behemoth_lite, the byte-fair leader, and
mlp_behemoth is named only as the byte-unfair parent.

- Route: Flash-local call, identical to the first reference. Pi's model config
  on Flash (~/.pi/agent/models.json) routes `nvidia/meta/muse-glimmer-30b`
  through the local OmniRoute provider (http://localhost:20128/v1,
  OpenAI-compatible) to NVIDIA NIM; in the first reference the NIM response's
  served-model field confirmed `meta/muse-glimmer-30b`. This run's Pi event
  stream names the route id `nvidia/meta/muse-glimmer-30b` on every assistant
  message (the harness does not expose a separate served-model field).
- Tokens: Pi reported input 83,932, output 868, total 84,800. The input count
  is the Pi agent harness's full context (system prompt, tool schemas, session
  framing); the question prompt itself is about 1,050 tokens. The first
  reference's direct-call count (2,579 prompt / 1,823 completion) is not
  comparable for that reason.
- This was a Flash-local NIM call through Vinay's own Pi/OmniRoute setup, not
  a Meta Model API or Baseten call, so it is not logged in
  results/api_usage_log.jsonl; this file is the record (same convention as
  the first reference).
- Sources given to Glimmer: results/alien_sweep_heldout96.json,
  results/second_pair_stage2.json, results/second_pair_heldout96.json
  (headline numbers and caveats only, composed into the prompt below).

## Prompt used (verbatim)

You are giving an independent reference verdict on a compression benchmark's headline wording. You did not run these experiments; judge only whether the wording is honest given the numbers and caveats below. Answer directly in text; do not use any tools.

Earlier today you gave a reference verdict on this same project (Fraction Compressor v0.4: the weight delta between a base model and its fine-tuned Instruct version stored as a 1-bit factored patch, per-matrix SVD rank map; recipes proposed by Muse Spark against a human uniform rank-32 baseline; metric is mean target logprob of the correct answer tokens, gap_closed = (factored - base) / (full delta - base); first-token accuracy ~0 for factored configs). Your verdict then was NO to the proposed headline "mlp_behemoth is a conditionally validated leading recipe," because the byte-fair comparison is its lite variant, and you added one wording limit: never name mlp_behemoth alone as the headline; any mention must pair it with the byte-fair variant and an explicit "byte-unfair" label. The project adopted your stricter ruling: the headline recipe in its prose is mlp_behemoth_lite, the byte-fair leader, and mlp_behemoth is named only as the byte-unfair parent.

New evidence since your verdict (all numbers independently recomputed and confirmed by script reruns and by Google Gemini):

Pair 1 (Qwen2.5-0.5B base/Instruct), expanded fresh probe set: the held-out guard grew from 24 to 96 fresh items (the original 24 plus 72 new, all generated after the sweep, never seen during search or ranking; 32 per bucket):
- mlp_behemoth_lite (19,358,176 bytes, FEWER than uniform's 19,434,496): gap closed 23.2% on the combined 96, vs uniform rank-32 at 2.1%.
- Subsets independently: on the original 24, lite 9.5% vs uniform 1.6%; on the new 72, lite 30.4% vs uniform 2.3%. The shrinkage you flagged (Stage 2 45.7% down to 10.8% on the first fresh items) did not continue; the byte-fair variant's combined fresh figure (23.2%) is higher than its first-24 figure (9.5%).
- mlp_behemoth itself (byte-unfair, 21,719,776 bytes): 26.6% combined, for reference only.
- Per-bucket on the combined 96, lite beats uniform overall but not in every bucket (knowledge gap closed: lite 3.7% vs uniform 7.8%; instruction: lite 35.0% vs uniform 16.6%; math: lite 26.2% vs uniform -8.2%). Metric is still logprob, not task accuracy. One model pair so far for this recipe family.

Pair 2 (SmolLM2-360M base/Instruct, a different model pair, 225 delta matrices): the same procedure was repeated. Stage 2 winner "o-down supercharge" (gap closed 82.4% on the 24 ranking items) is byte-unfair at 27,660,288 bytes vs the uniform budget of 19,705,856 bytes. Its byte-matched variant "o-down-rebalanced" (19,683,328 bytes, inside budget) was confirmed on the same 96 fresh items: it beats uniform by 0.293 nats of raw mean logprob (-8.073 vs -8.366).
- Pair-2 anomaly: on this pair EVERY factored config outscores the full fp16 delta itself (full delta mean logprob -8.432; uniform -8.366; rebalanced -8.073; supercharge -8.040), so gap_closed exceeds 1.0 for all of them (1.015 to 1.088) and cannot be read as a fraction of the fine-tune recovered. In one subset's math bucket the full delta scores below base, and those gap values are recorded as null.
- First-token accuracy remains low (~0.08-0.09 for factored configs on pair 2, ~0.01-0.02 on pair 1).

Questions:
1. Does your earlier stricter ruling change? Specifically: is "mlp_behemoth_lite, byte-fair leader" now adequately supported as the pair-1 headline? Answer yes or no, then explain in at most 5 short bullet points.
2. Does the pair-2 result (factored configs outscoring the full delta itself, gap_closed above 1.0) raise any NEW wording limit the authors have not already adopted? (Already adopted: headline names the byte-fair variant; byte-unfair parents always labeled; metric stated as logprob; per-bucket losses stated; shrinkage history stated.) If yes, state the one limit in one sentence. If no, say so.
Keep the whole reply under 300 words.

## Glimmer's reply (verbatim)

1. Yes.

* Fresh 96-item hold-out sustains and improves the byte-fair lead: mlp_behemoth_lite 23.2% vs uniform rank-32 2.1% combined, 9.5%→30.4% on the new 72 items, no continuation of Stage-2 shrinkage.
* Byte-fair holds: lite is 19,358,176 bytes < uniform 19,434,496 bytes; mlp_behemoth parent remains byte-unfair and is only named as parent.
* The prior naming rule is satisfied; headline can be mlp_behemoth_lite, byte-fair leader for Pair 1.
* Caveats still apply: per-bucket loss remains e.g. knowledge 3.7% vs 7.8% uniform; metric is mean target logprob, first-token accuracy ~0; evidence is one model pair only.
* No change to the stricter naming ruling is required.

2. Yes. New wording limit: when factored configs outscore the full fp16 delta, gap_closed >1.0 must not be presented as a fraction of fine-tune recovered; state that gap_closed is no longer a recovery fraction and the metric is inverted/extrapolated for that pair.

