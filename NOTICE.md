# NOTICE: prior art, attribution, and originality

## This project's own work

All code, documentation, evaluation items, and results in this repository
are original work by Vinay K Ganji Krishna, the sole participant and
author of record, produced with AI assistance: Ember, an AI agent
powered by Muse Spark, carried out implementation, benchmarking, and
documentation under his direction, and Muse Spark also generated the
compression recipes and the fresh evaluation questions used in the
benchmarks. Written during the Meta Global AI Developer Hackathon
(October 26 to November 4, 2026) and released under the MIT License
(see LICENSE). No third-party code is included in this repository, and
no code was copied from any of the projects cited below.

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
- **D-QRELO** (Li et al., April 2026, arXiv:2604.16940): training-free
  and data-free delta compression in two steps, a 1-bit sign-times-scale
  pass followed by a truncated SVD of the error that pass leaves behind.
  The closest published relative of our format: a sign part plus a
  low-rank part.
- **DeltaDQ** (Jiang et al., October 2024, arXiv:2410.08666): sparsifies
  the delta in groups, then quantizes what survives, reaching 16x to
  512x compression on fine-tuned models.
- **LittleBit** (Lee et al., NeurIPS 2025, arXiv:2506.13771): extreme low-bit
  quantization using a factored, dual residual form. Prior work from
  the author's earlier Fraction Compressor versions (v0.1 to v0.3, in
  the original repository) explored this direction; the factored form
  in `src/factored.py` is this event's own implementation.
- **LittleBit-2** (Lee and Kim, February 2026, arXiv:2603.00042,
  ICML 2026): follow-up to LittleBit. It explains why factored binary
  weights underperformed and fixes it by rotating the factors before
  quantizing them. It compresses whole models with training, not
  post-hoc deltas, so it does not compete with this project directly.

## What is ours

Naming a published method and reporting its published results for
comparison is standard research practice. The contributions claimed by
this repository are not the 1-bit delta format itself. They are:

- the in-loop recipe search and judging, in a specific narrow form:
  Muse Spark proposes the per-layer rank allocation (the recipe) for a
  post-hoc fine-tune delta under a hard byte budget, with no training,
  and later judges the results, with every verdict required to cite the
  exact result file it rests on;
- the forced-multiply runtime in `src/factored.py`, which applies the
  delta as two small multiplies and never rebuilds the full matrix, so
  patches swap in and out of a running base model live;
- the first-token gate diagnosis, scoped to what was tested: one gated
  skill (NuExtract JSON extraction) on the Qwen2.5-0.5B pair transferred
  weakly through small patches at ranks 32, 64, and 128 and through one
  Muse Spark recipe, together with its force-start control test, which
  separates "the skill is missing" from "the start decision is
  missing";
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
(Llama 3.2 Community License), Qwen/Qwen2.5-1.5B and
Qwen2.5-1.5B-Instruct (Apache 2.0), numind/NuExtract-1.5-tiny (MIT).
