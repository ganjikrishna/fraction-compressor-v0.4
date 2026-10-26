# Fraction Compressor v0.4

**One base model. Many tiny patch files. Swap a file, swap the behavior.**

![How Fraction Compressor v0.4 works](docs/how-it-works.svg)

## In plain words

A fine-tuned model differs from its base model by a patch (the delta). A normal patch is almost as big as the model itself. Fraction Compressor stores that patch in a factored form whose structure is kept as 1-bit signs, priced byte for byte by the code: 0.28 bits per weight for one large layer at rank 32 (the exact price depends on layer size and rank). v0.4 runs it through a factored runtime: two small multiplies, Y = (X U) V^T, without ever rebuilding the full weight matrix. One layer stored the normal way takes 8.4 MB; our rank-32 file takes 144 KB, and swapping patches is just loading a different small file. Compressing a patch is offline work done once with the full delta; the saving is in storage and at run time.

## Built during the hackathon

This repository contains only work built during the Meta Global AI Developer Hackathon, October 26 to November 4, 2026 (Indie Developer track, Push the Frontier).

Pre-existing work (not part of this submission): Fraction Compressor v0.1 to v0.3 and the Signet delta-transfer experiments live in the original repository, [github.com/ganjikrishna/fraction-compressor](https://github.com/ganjikrishna/fraction-compressor). The compression and Signet methods were designed and validated there before the event. What is new in this repo is the factored runtime, the end-to-end task benchmark, and the Meta model comparison.

## What is in this repo

- `src/factored.py`: the factored runtime (quantize a delta, price its storage, apply it factored). Tested, see `tests/test_factored.py`.
- `examples/quickstart.py`: a 1-minute smoke run on a dummy delta (needs only numpy): prints the storage cost, bits per weight, and the factored error next to the best any factored form could do at the same rank.
- `fixtures/`: the quantum random fixture for the benchmark's audit sampling (IBM Quantum hardware, backend and job logged in the file).
- In progress: the end-to-end task benchmark (base vs full delta vs compressed delta), Muse Spark in the loop as task generator and judge, and the live hot-swap demo.

## Author and credits

Built by **Vinay K Ganji Krishna**, solo participant (Indie Developer track) and author of record.

Implementation, benchmarking, and documentation were carried out with **Ember**, an AI agent powered by Muse Spark, working under the author's direction, the same way this event encourages building with Meta's Muse Code agent. Design pressure-testing also drew on a Gemini design-debate chat. Every result in this repository is produced by scripts in this repository and can be rerun.

## License

MIT, (c) 2026 Vinay K Ganji Krishna. Methods are clean-room implementations from published papers; see the original repository's NOTICE for citations.
