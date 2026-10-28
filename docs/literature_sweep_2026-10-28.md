# Literature sweep, 2026-10-28

A fresh check of the published work that touches this project's claims.
Every paper below was verified on its arXiv page (or the venue's own
listing) before being included. Nothing here edits NOTICE.md or the
README; the last section lists recommended changes only.

Short version: the core format gained one close new relative (D-QRELO),
"skills as compressed delta files" is now a named, published research
area (SkillPacks), and an LLM choosing compression settings per layer
now exists in print for vision models (APQF). Our novelty wording needs
narrowing in two places, detailed at the end. The first-token gate
finding gained outside support. Nothing found weakens the gate, the
verification harness, or the live hot-swap.

## 1. One-bit and low-bit delta compression

**D-QRELO: Training- and Data-Free Delta Compression for Large Language
Models via Quantization and Residual Low-Rank Approximation**
Junlin Li et al., April 2026, arXiv:2604.16940.
Compresses a fine-tune delta in two steps: a 1-bit sign-times-scale
pass, then a truncated SVD of whatever error is left over. Training-free
and data-free, and it reports design rules for where compression hurts
(by task difficulty, architecture, and layer position).
For us: the closest published relative of our format. Sign part plus a
low-rank part is the same family as our sign-plus-factored form, so a
judge may see them as siblings. Must-cite; it is not in NOTICE.md yet.

**DeltaDQ: Ultra-High Delta Compression for Fine-Tuned LLMs via
Group-wise Dropout and Separate Quantization**
Yanfeng Jiang et al., October 2024, arXiv:2410.08666.
Sparsifies the delta in groups, then quantizes the survivors, reaching
16x to 512x compression on WizardMath and WizardCoder models.
For us: older prior art in the same space that NOTICE.md does not name.
No impact on our claims; worth one citation line for completeness.

**Seeing Delta Parameters as JPEG Images: Data-Free Delta Compression
with Discrete Cosine Transform (Delta-DCT)**
Chenyu Huang et al. (Shanghai AI Lab / Fudan), March 2025,
arXiv:2503.06676.
Treats each layer's delta like an image: patches it, gives important
patches more bits, and compresses in the DCT (JPEG) domain at about
1-bit equivalent, with no data and no training.
For us: another data-free delta codec with per-patch bit allocation.
Supports our "where the bytes go matters" framing; different mechanism,
no conflict. Optional cite.

**LittleBit-2: Maximizing the Spectral Energy Gain in Sub-1-Bit LLMs
via Latent Geometry Alignment**
Banseok Lee and Youngmin Kim (Samsung), February 2026,
arXiv:2603.00042 (presented at ICML 2026).
Follow-up to LittleBit: explains why factored binary weights
underperformed (the latent factors point the wrong way for binarizing),
then fixes it by rotating the factors before quantization. State of the
art below 1 bit per weight on Llama-2 and Llama-3.
For us: NOTICE.md cites LittleBit (now confirmed as a NeurIPS 2025
paper) but not this successor. LittleBit-2 compresses whole models with
training, not post-hoc deltas, so it does not compete directly.
Must-cite as a follow-up line.

## 2. Factored formats and who chooses the allocation

**APQF: Agentic Profiling-Guided Structured Pruning and Mixed-Precision
Quantization with Adaptive Fine-Tuning**
Sadegh Jafari et al. (Iowa State), August 2026, arXiv:2608.05499.
A team of LLM agents profiles a vision model, and LLM planners then
choose the per-layer pruning ratios and per-layer bit-widths; every
proposed strategy is validated against the real model before it runs,
and fine-tuning recovers accuracy afterwards.
For us: this weakens the broad claim "a model chooses the allocation."
That idea now exists in print. It differs from ours in every other
respect: vision models, whole-model pruning plus quantization, and a
training-aware pipeline, where ours is training-free rank allocation
for a post-hoc delta under a hard byte budget. The claim must be
narrowed, not dropped (see Position changes).

**GA-SVD: Generation-aware Singular Value Decomposition for LLM
Compression**
Shengkun Tang et al., October 2026, arXiv:2610.15398.
Low-rank compression of whole LLMs where an evolutionary search (not
heuristics, not an LLM) finds the global per-layer rank allocation, up
to 70B models.
For us: shows searched per-layer rank allocation is an active,
competitive direction. Our difference stands: the searcher is a
language model reasoning about the layers, and the object is a delta,
not the whole model. No impact beyond context.

## 3. Layer streaming and offloaded inference

**Prima.cpp: Fast 30-70B LLM Inference on Heterogeneous and
Low-Resource Home Clusters**
Zonghang Li et al., April 2025, arXiv:2504.08791 (v3 July 2026).
Runs 30B to 70B models across a few home devices by memory-mapping the
weights and streaming them from disk, with a scheduler that assigns
layers to devices and prefetches to hide disk time.
For us: the streaming field is alive and moving, but we found no
academic successor to AirLLM itself and nothing that streams a
compressed delta patch instead of the model. Our 7B test streams our
own factored patch through a NumPy forward pass; that combination
(patch format plus streaming) is still unoccupied in print. Claim the
combination only, never streaming itself.

## 4. Skill and behavior transfer under compression

**Knowledge Fusion of Large Language Models Via Modular SkillPacks
(GraftLLM)**
Guodong Du et al., May 2025, arXiv:2505.18502 (ICLR 2026).
Stores a model's capability as a "SkillPack": the parameter update,
compressed with a different operator per module type (pruning for
embeddings, SVD for attention, conservative compression for MLPs).
SkillPacks are merged into other models for fusion and continual
learning.
For us: "a skill as a small compressed delta file" is published,
named, and at a top venue. Competes with the casual version of that
framing, not with our post-hoc, no-retraining conversion of an
arbitrary existing fine-tune. Must-cite if the submission uses the
word skillpack or leans on skills-as-files.

**Skill Weaving: Efficient LLM Improvement via Modular Skillpacks**
Zhuo Li et al., May 2026, arXiv:2605.22205 (Findings of ACL 2026).
Builds skillpacks by self-training, then compresses them with SkillZip,
which stores each delta in factored low-bit form, literally computed as
Y = X A B with quantized factors and scales, the same multiply shape as
our factored runtime. A 9B model built this way beats a 32B monolith on
their benchmarks.
For us: the closest published match to "factored delta as a skill
file," including the factored multiply. Two honest differences remain:
their skillpacks are created by training for that purpose, ours are
converted from an existing fine-tune after the fact with no training;
and they do not swap patches live in a running base. Must-cite.

**ACE-Compression: An Ability-Centric Evaluation of Compressed Large
Language Models**
Jiahui Ning et al., October 2026, arXiv:2610.27913.
Tests 35+ compressed checkpoints for which abilities survive:
surface-level skills persist, while fine-grained, long-tail, and
persona abilities quietly collapse even when task scores hold up.
For us: independent support for our core caution. Aggregate scores
(logprob included) can look fine while specific behaviors are gone,
which is exactly why we ran a task-level skill test and found the gate.
Supports; a good citation for the skill-test section.

**Quantization Undoes Alignment: Bias Emergence in Compressed LLMs
Across Models and Precision Levels**
Plawan Kumar Rath and Rahul Maliakkal, May 2026, arXiv:2605.15208.
At 3-bit, 6 to 21 percent of previously unbiased answers develop new
stereotyped behavior while perplexity barely moves (under 11 percent in
the worst case, under 0.5 percent at 8-bit).
For us: same lesson from the safety side: headline metrics stay calm
while behavior changes underneath. Supports our decision to report the
skill failure instead of only the gap-closed number. No impact on the
format claims.

**Steering Externalities: Benign Activation Steering Unintentionally
Increases Jailbreak Risk for Large Language Models**
Chen Xiong et al., February 2026, arXiv:2602.04896.
Shows that small steering interventions flip behavior by moving the
first few generated tokens: the model's refusal or compliance mode is
decided in a short prefix window (the "refusal gate"), and everything
after follows from that start.
For us: the strongest outside support for the first-token gate being a
real mechanism rather than an artifact of our 10-prompt test. Published
work in a different area (steering, safety) finds the same structure:
behavior is decided at the start of generation. Supports the gate
diagnosis; worth citing next to it.

## 5. Verification of claims (one comparable item)

**VeriFin: A Neurosymbolic Framework for Verifying LLM-Generated
Financial Claims**
Bethel Hall, Sachi Shome, William Eiers, August 2026,
arXiv:2608.10213.
An LLM's numerical answers are checked by first establishing the
correct calculation independently from the source filings, then letting
a solver (Z3) accept, reject, or abstain. It accepts far more correct
answers than an LLM judge while making zero false accepts.
For us: the same design pattern as our harness, published in another
domain: never let the model's word settle a number; recompute from the
source records and check. It validates the approach and costs us no
novelty, since our evidence is benchmark result files and our checker
set includes script recomputation plus model judging. No action needed.

## Position changes (recommendations only)

1. **NOTICE.md: add D-QRELO (arXiv:2604.16940).** It is the closest
   published relative of our format (1-bit sign pass plus low-rank
   remainder) and it is currently missing. Adding it before a judge
   raises it costs nothing and protects the honest-prior-art stance.
   In the same edit, add one line each for DeltaDQ (arXiv:2410.08666)
   and LittleBit-2 (arXiv:2603.00042), and note LittleBit itself is
   NeurIPS 2025.

2. **README Prior art section: add the SkillPack papers.**
   GraftLLM (arXiv:2505.18502) and Skill Weaving / SkillZip
   (arXiv:2605.22205) publish "skills as compressed delta modules,"
   and SkillZip even uses our factored multiply shape. One or two
   lines keep the section complete and pre-empt the judge's version
   of the question.

3. **Submission novelty framing: narrow the recipe claim.** Do not
   write or imply "first to have a model choose the compression
   allocation" (APQF, arXiv:2608.05499, did LLM-planned per-layer
   bit-widths for vision models in August 2026). The defensible
   wording: a Meta LLM allocates ranks for a post-hoc fine-tune delta
   under a hard byte budget, training-free, and the same loop judges
   the results against the files. Every qualifier in that sentence is
   doing work; keep them all.

4. **Submission novelty framing: retire "skills as files" as a novelty
   claim.** After GraftLLM and Skill Weaving it is a research area,
   not our invention. Our angle is conversion: any existing fine-tune
   becomes a patch with no retraining, patches swap live, and we
   measured where the transfer breaks (the gate). That framing is
   stronger anyway because it is the part nobody else published.

5. **Gate section: cite the support.** Steering Externalities
   (arXiv:2602.04896) for the start-of-generation gate mechanism, and
   ACE-Compression (arXiv:2610.27913) for "scores hold while behaviors
   collapse." These turn our 10-prompt finding from a lone observation
   into a result that agrees with two independent 2026 papers.

6. **No change needed:** the format's honest-baseline story versus
   BitDelta, the verification harness (VeriFin confirms the pattern
   rather than pre-empting it), and the streaming plan (claim the
   patch-plus-streaming combination only).
