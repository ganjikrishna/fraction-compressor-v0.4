# Skill-limit consultation (2026-10-27)

Vinay directed: consult Muse Spark and Muse Glimmer on the NuExtract skill-transfer limit, do what is best, and tell the limit upfront. Both were given the SAME question (below, verbatim, including the finding). Both independently recommended option (c): disclose upfront AND test larger patches (rank 64, rank 128). The rank test was run the same day; its results are in results/skill_demo_ranks.json.

## Question put to both (verbatim)

You are advising on how to present a benchmark result honestly in a submission. Judge only the presentation question; the numbers below are already verified.

Context: Fraction Compressor v0.4 stores the weight difference (delta) between a base model (Qwen2.5-0.5B) and a fine-tuned version of it as a small 1-bit factored patch file, so one base model can swap behaviors by swapping a small file.

The finding: a JSON-extraction fine-tune (NuExtract-1.5-tiny, MIT) scores 9/10 clean extractions itself; the plain base scores 0/10 (it emits end-of-text on the format); our rank-32 compressed patch (19,434,496 bytes) transfers the skill cleanly on only 1/10, because the skill is gated by the first generated token (start JSON vs stop). Broad behavior transfers much better: the Instruct pair closes 23.2% of the score gap on 96 fresh questions and shows clean generation wins.

Question: We found this limit. Options: (a) disclose it upfront as a documented boundary in the README and submission; (b) also test larger patches (rank 64, rank 128) on this gated skill to see whether the boundary moves with size; (c) both. What do you recommend, and what exact one or two sentences should the upfront limit statement say?

Keep the whole reply under 250 words.

## Muse Spark (muse-spark-1.3, Meta Model API) reply (verbatim)

Recommend **(c) both.**

Disclosing upfront is required for honesty — a 1/10 transfer can't be buried. Testing rank-64/128 is required for completeness — it shows if this is a capacity threshold or a hard limit.

Use this verbatim in README and submission:

> Rank-32 1-bit patches (~19.4 MB) transfer broad behavior — 23.2% gap closure on 96 instruct questions — but do not reliably transfer single-token-gated format skills: NuExtract JSON transfer scored 1/10 clean vs 9/10 for the full fine-tune (base 0/10).

Call record: results/api_usage_log.jsonl, purpose skill_limit_consultation_spark, 1,597 total tokens (308 prompt / 1,289 completion, of which 1,151 reasoning).

## Muse Glimmer (meta/muse-glimmer-30b) reply (verbatim)

Recommend (c) both.

Disclose the boundary now — honest reporting is non-negotiable for a submission — and characterize it with larger ranks so reviewers can see where the limit moves rather than assuming it's universal.

Upfront limit statement, e.g.:

*“Fraction Compressor v0.4 does not reliably transfer skills gated by the first generated token. On NuExtract-1.5-tiny JSON extraction, the rank-32 patch moves the base model from 0/10 to 1/10 clean extractions versus 9/10 for the full fine-tune, because the skill is controlled by start-JSON vs stop.”*

*“Broad instruction behavior transfers much better under the same patch — 23.2% score-gap closure on 96 fresh questions with clean generation wins — indicating the limitation is format-gated, not general.”*

Testing rank-64/128 on this gated skill is worthwhile editorially: if the boundary moves with size you can quantify the cost to overcome it; if it does not, you have stronger evidence the limit is architectural, which is also a valuable, honest result.

Route record: Flash-local call via Pi (default model nvidia/meta/muse-glimmer-30b through the local OmniRoute provider to NVIDIA NIM, the same route documented in results/glimmer_reference.md; the events confirm provider omniroute and model nvidia/meta/muse-glimmer-30b). Pi reported 7,738 total tokens (7,301 input / 437 output); as with the earlier Glimmer runs, the input count is the Pi harness's full context, not the ~200-token question. Flash-local NIM call, not a Meta Model API or Baseten call, so it is not logged in results/api_usage_log.jsonl; this file is the record.
