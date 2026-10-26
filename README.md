# Fraction Compressor v0.4

**Factored 1-bit delta runtime with end-to-end task-accuracy benchmarks.**

Fraction Compressor stores the difference between a base model and its fine-tuned version (the delta) at about 1 bit per weight, so one base model can serve many fine-tunes from tiny add-on files. Version 0.4 adds the factored runtime: the compressed delta is applied as two small matrix multiplies, Y = (X U) V^T, without ever rebuilding the full weight matrix, and it is measured end to end on real tasks, not just reconstruction error.

## Built during the hackathon

This repository contains only work built during the Meta Global AI Developer Hackathon, October 26 to November 4, 2026 (Indie Developer track, Push the Frontier).

Pre-existing work (not part of this submission): Fraction Compressor v0.1 to v0.3 and the Signet delta-transfer experiments live in the original repository, [github.com/ganjikrishna/fraction-compressor](https://github.com/ganjikrishna/fraction-compressor). The compression and Signet methods were designed and validated there before the event. What is new in this repo is the factored runtime, the end-to-end task benchmark, and the Meta model comparison.

## What is in this repo

- Factored-multiply runtime for compressed deltas (never materializes the full weight matrix)
- End-to-end task-accuracy benchmark: base model vs base + full delta vs base + 1-bit compressed delta
- A Meta model (Muse Spark, via the Meta Model API) folded into the same benchmark as a reference point
- Results, notes, and the demo script for the submission

## Author and credits

Built by **Vinay K Ganji Krishna**, solo participant (Indie Developer track) and author of record.

Implementation, benchmarking, and documentation were carried out with **Ember**, an AI agent powered by Muse Spark, working under the author's direction, the same way this event encourages building with Meta's Muse Code agent. Design pressure-testing also drew on a Gemini design-debate chat. Every result in this repository is produced by scripts in this repository and can be rerun.

## License

MIT, (c) 2026 Vinay K Ganji Krishna. Methods are clean-room implementations from published papers; see the original repository's NOTICE for citations.
