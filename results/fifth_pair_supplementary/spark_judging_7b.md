# Muse Spark 1.3 judging: fifth pair (Qwen2.5-7B)

Date: 2026-10-28. Judge usage: {'completion_tokens': 12889, 'prompt_tokens': 1559, 'total_tokens': 14448, 'completion_tokens_details': {'reasoning_tokens': 12142}, 'prompt_tokens_details': {'cached_tokens': 0}}. Wall: 66.2 s.

- Claim A: **SUPPORTED** — 28*7+2=198 matrices, vocab shapes match tie_word_embeddings=false, and 15230566400/2=7615283200 params matches ~7.6B scale.
- Claim B: **SUPPORTED** — 15230566400/86499328=176.1x, and winner 86401024 is 98304 bytes under the 86499328 budget.
- Claim C: **SUPPORTED** — Reports 351.14s <1800s PASS with 7501.6MB peak; no arithmetic or ordering violation.
- Claim D: **SUPPORTED** — 5.82e-11 and 5.40e-11 are fp-rounding level, and product-gate with 1.85e-09 factor rotation from clustered singular values is coherent.
- Claim E: **SUPPORTED** — -9.5837 > -9.629 > -11.2036 > -13.7784 > -14.4748 > -14.9005 so down_king wins byte-fair, accuracy 0.333=8/24 beats full 0.292=7/24.
- Claim F: **SUPPORTED** — Full -17.7691 < base -7.2632 so gap denominator negative and null is honest; ln(1.93e-08)=-17.76 matches full mean and raw-completion reversal supports template-artifact explanation.
- Claim G: **SUPPORTED** — -8.6939-(-13.1583)=4.464 nats and 86499328-86401024=98304 bytes correct, and full -15.9741 < base -6.9158 so null gap is honest.
- Claim H: **SUPPORTED** — 951911192/86499328=11.01x ~11.0x, and -11.3776 < -8.6939 with 0.312 < 0.344 so worse than down_king.
- Claim I: **SUPPORTED** — 2.2-2.35GB and 8349.5MB peaks are <11GB, and 7.6B*4~30GB supports never-held-whole claim.
- Claim J: **SUPPORTED** — 78/78 recomputation pass claim has no internal arithmetic contradiction.
- Claim K: **SUPPORTED** — CUDA assertion after sharding supports CPU-only incompatibility conclusion with clear NumPy-runtime attribution.
- Claim L: **SUPPORTED** — Transcript is reported without success overclaim, with timing/RSS and degenerate patched strings disclosed as-is.

Headline answer: At 7B down_king beats uniform rank-32 by ~4.5 nats within budget but still trails base on mean logprob with full delta inverted by chat-template mismatch, so gap_closed is undefined.

Concerns: none
