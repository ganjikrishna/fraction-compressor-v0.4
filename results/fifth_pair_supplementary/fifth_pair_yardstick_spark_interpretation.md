# Spark interpretation judging: 7B yardstick fix + regularization test

Date: 2026-10-29T13:16:57Z. Judge: Muse Spark 1.3 via Meta Model API. Usage: {'completion_tokens': 6175, 'prompt_tokens': 1751, 'total_tokens': 7926, 'completion_tokens_details': {'reasoning_tokens': 5247}, 'prompt_tokens_details': {'cached_tokens': 0}}. Wall: 21.86 s.

Headline: Battery numbers internally cohere and support shrinkage over strong-denoiser account, aside from limited per-item continuity evidence and B2 between-scalings misstatement.

Disagreements: B2 says down_king scores between 0.25 (-7.096) and 0.5 (-7.419) scalings but -7.556 is worse than both, so it is below that interval not between; A1 claims exact reproduction for all six on means alone while per-item 0.0 is given only for two configs.

- Claim A1: **partly_supported** — Means match to 6 decimals for all six and 37/37 checks incl KL=0 support continuity, but per-item 0.0 is cited only for uniform_rank32 and down_king, so exactness for all six exceeds item-level evidence shown.
- Claim A2: **supported** — 0.000 corrected vs 0.083 chat for delta configs and 0.052 vs 0.208 for base shows removal, and -18.34 echo vs -15.76 non-echo shows echo penalty.
- Claim A3: **supported** — Math gap -0.59 in both supports identical protocol; knowledge -15.56 to -1.02 and instruction -11.02 to -0.16 shrink but stay negative, justifying null gap_closed.
- Claim A4: **partly_supported** — Reversal holds: 0.333 vs 0.052 overall and math 0.75 vs 0.031 opposite logprob, but knowledge 0.000 for every config limits gain claim and phrasing-penalty is interpretation not measured.
- Claim A5: **supported** — 7/12 vs 11/12 vs 9/12 counts cohere with 1-miss for full_delta and described base failures on format and math prompts.
- Claim A6: **supported** — Base -3.977 chat vs -12.154 raw brackets format effect, and -15.56 vs -1.02 agree on sign below base while disagreeing on size as claimed.
- Claim B1: **supported** — -7.096>-7.556 and -6.36>-8.694 plus math -2.166>-3.16 show full_a025 beats down_king on both, consistent with neither patch beating best below-full point.
- Claim B2: **partly_supported** — Agreement 0.854<0.865<0.906 and correlation 0.928~0.929 vs 0.842 support tracking claim, but -7.556 is worse than both -7.096 and -7.419 so not between 0.25-0.5 scalings.
- Claim B3: **supported** — 0.281<0.643 supports closer to full on average, math 0.166 vs 1.617 explains driver, 0.40 items closer allows skew, and 0.166 shows full_a05 closer.
- Claim B4: **supported** — 46+50=96, agreement 0.848 vs 0.860 shows no helped concentration, and -0.369 helped vs +2.409 hurt with same shape for full_a025 supports filtering reading.
- Claim B5: **supported** — Agreement 0.865,0.906,1.0 rising while scores -7.096,-7.419,-8.634 falling plus down_king 0.854,-7.556 below curve supports absent strong signature.
- Claim B6: **supported** — 25-50% beats patch on scores, matches helped/hurt shape and meets/exceeds agreement, while distributional closeness on math preserves weak movement sense as claimed.
