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
