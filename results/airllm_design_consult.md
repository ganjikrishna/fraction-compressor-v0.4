# AirLLM streaming design consult: Gemini pressure-test

Date: 2026-10-28. One call to gemini-3.5-flash-lite via the Google
Gemini API connector, logged in results/api_usage_log.jsonl with
purpose "airllm_design_consult" (prompt 1,175 tokens, completion
2,116 tokens). The design under review: run the Qwen2.5-7B base /
Instruct pair in the project's NumPy stack on Flash (11 GB RAM,
CPU only) using AirLLM-style layer-by-layer streaming (concept from
lyogavin/airllm, Apache 2.0; implementation ours): streamed RSVD
precompute, Gram-matrix exact SVD factor build, block-by-block eval
forward carrying all probe items' hidden states, per-item lm_head
logits at answer positions only, then a streamed greedy-generation
demo with the winning patch applied as each block loads.

## The prompt (verbatim)

You are pressure-testing an engineering design for a benchmark experiment. Be specific and adversarial; name failure modes, numbers, and what you would change. Short paragraphs, no flattery.

CONTEXT. "Fraction Compressor" compresses the difference between a base model and its fine-tune into a factored 1-bit patch (per-matrix: signs of a low-rank factor plus least-squares refit; storage priced as sign bits + fp32 row scales + fp16 second factor). An AI model (Muse Spark Open) proposes per-layer-type rank "recipes" under the byte budget of a human uniform rank-32 recipe; recipes are scored by mean target logprob on probe questions; gap_closed = (patched - base) / (full delta - base). On Qwen2.5-0.5B the byte-fair Spark recipe closed 23.2% vs uniform 2.1% (96 fresh questions); on Qwen2.5-1.5B the margin narrowed to 0.134 nats. A judge asked: does any of this survive at 7B?

THE 7B RUN (what you are reviewing). Pair: Qwen2.5-7B base / Instruct (28 blocks, hidden 3584, inter 18944, vocab 151936, embeddings NOT tied, so embed and lm_head are separate delta matrices; 198 delta matrices total; full delta is 15.2 GB in bf16). Machine: a CPU-only Ubuntu box with 11 GB RAM and 12 threads; everything is NumPy. The 7B model can never be held whole in fp32 (30 GB) or even bf16 alongside working state, so the design borrows the AirLLM concept (Apache 2.0): layer-by-layer streaming.

DESIGN.
1. Precompute: randomized SVD of each delta matrix, streamed per matrix from the sharded safetensors via memmap-style reads (read base tensor, read instruct tensor, form delta in place, RSVD, store singular values, release). Embedding/lm_head deltas are 151936x3584 (2.2 GB fp32 each).
2. Factor build: exact SVD per matrix via the smaller Gram matrix in fp64 (e.g. for mlp.gate 18944x3584, G = D^T D is 3584x3584) instead of dense LAPACK SVD, to bound memory and time; construction cross-validated against the reference quantize function on sampled matrices.
3. Eval forward, streamed: all probe items' hidden states are carried through the model block by block (batch = all items through block 0, then block 1, ...). Per block: load that block's base weights (bf16 file, upcast to fp32, about 0.93 GB), apply the config (nothing for base; instruct weights instead for full-delta; U@V.T added chunk-wise for factored), run every item's sequence through the block, release. Embedding is gathered row-wise (only tokens present). lm_head logits are computed at the end per item (151936x3584 fp32 = 2.2 GB loaded once per config), with the factored head delta applied chunk-wise. Peak RAM target under 9 GB.
4. Eval order: forward validation on 24 items (base vs full delta must gap positive in every bucket; graft check; quantize cross-check), then Stage 2 (5 Spark recipes + uniform, 24 items), then the byte-fair winner (or a byte-matched lite variant) vs uniform on 96 fresh items, then a plain 1-bit baseline (sign x per-matrix mean-abs scale, BitDelta-style init, no training) priced on real shapes and scored on the 96.
5. Stream demo after scoring: greedy generation on 3-5 prompts, base streamed plain vs base streamed with the winning patch applied block by block as each block loads (weights re-streamed per generated token, AirLLM-style), per-token wall time reported.

QUESTIONS.
Q1. RAM: where does this design blow the 11 GB budget? Consider fp64 Gram SVDs of the big matrices, the RSVD power iterations on the 151936x3584 deltas, 96 items' hidden states plus attention matrices, and the lm_head phase. Give peak estimates per phase if you can.
Q2. Eval order: is validation -> Stage 2 (24) -> confirmation (96) -> baseline the right order of spend if a wall is hit halfway? What should be cut or reordered?
Q3. Credibility: what would make the 7B scale claim believable to a skeptical judge, and what in this design most undermines it (e.g. Gram-matrix SVD numerics in fp64 vs dense SVD, bf16-to-fp32 upcasting, logprob-only scoring, subset sizes)?
Q4. Demo: is per-token re-streaming the honest way to show "the patch updates a model that is never whole in memory", or is there a cleaner demonstration? What timing numbers must be stated for it not to mislead?

## Gemini reply (verbatim)

### Q1. RAM Blowouts (The 11 GB Budget)

The 11 GB RAM limit is a hard wall that this design violates in at least three places during Precompute and the lm_head phase. NumPy does not garbage-collect C-allocated arrays deterministically; fragmentation will compound these footprints.

*   **Embedding & `lm_head` RSVD (Phase 1):** The deltas for `embed_tokens` and `lm_head` are $151936 \times 3584$ in fp32. That is $2.16\text{ GB}$ per matrix. Randomized SVD on a matrix of this shape requires storing multiple randomized projection matrices and working spaces of shape $(3584, k)$ and $(151936, k)$. For $k=64$, this is manageable, but if the power iterations accumulate dense intermediate matrices without strict in-place allocation, NumPy will allocate multiple $2.16\text{ GB}$ fp32 copies. Peak: **14–16 GB**.
*   **Gram Matrix SVD (Phase 2):** For `mlp.gate` and `mlp.up`, the shape is $18944 \times 3584$. Forming $G = D^T D$ yields a $3584 \times 3584$ fp64 matrix ($\approx 102.8\text{ MB}$), which is safe. However, computing its SVD via `np.linalg.eigh` or `svd` requires allocating eigenvectors and workspace arrays in fp64. The real danger is memory leaks when looping over all 198 matrices sequentially without calling `gc.collect()` and explicitly deleting view references. Doing so risks memory creep. Peak: **7–9 GB** (survivable only if strictly disciplined).
*   **Inference Forward Pass (Phase 3):** Qwen2.5-7B hidden dimension is 3584. Passing 96 probe items (assume sequence length $L = 512$) means the hidden state tensor is $96 \times 512 \times 3584$ in fp32 ($\approx 670\text{ MB}$). This is fine. **The trap is attention.** Storing attention maps or intermediate activations for 96 sequences across 28 layers will instantly OOM if attention is not fused or sliced. Furthermore, loading the base block (bf16, $0.93\text{ GB}$) and upcasting it to fp32 doubles it to $1.86\text{ GB}$. If the factored patch is applied via chunk-wise $U @ V^T$ additions in fp32 without in-place mutation, you hold base weights, instruct weights (if comparing), and deltas simultaneously. Peak: **9.5–10.5 GB** (dangerously close to the 11 GB cliff).
*   **The `lm_head` Logit Phase:** The final `lm_head` weight matrix is $151936 \times 3584$ fp32 ($2.16\text{ GB}$). Computing logits for 96 items of length 512 yields a tensor of shape $96 \times 512 \times 151936$ in fp32, which is **$75.5\text{ GB}$**. You *cannot* materialize this. You must compute logprobs chunk-wise over the vocabulary or sequence dimension on the fly. If the design materializes the full logits matrix, it crashes instantly.

---

### Q2. Evaluation Order & Resource Triage

The current order (Validation 24 $\rightarrow$ Stage 2 Spark 24 $\rightarrow$ Confirmation 96 $\rightarrow$ Baseline) is **suicidal** if a RAM wall or negative gap is hit halfway, because the most expensive and informative phase (the 96-item confirmation and BitDelta baseline) happens at the very end. 

**Reorder to fail fast:**
1.  **Micro-Sanity (1 item, 1 layer):** Verify the entire pipeline (delta subtraction, SVD, 1-bit quantization, block patching, logprob math) runs end-to-end without crashing or producing `NaN`. Cost: 2 minutes.
2.  **The 96-Item Fresh Confirmation (Base vs. Full Delta):** Run this *first* on the full uncompressed delta. If the full delta does not yield a substantial positive gap ($>50\%$ closed) on your 96 fresh items, your probe set is broken, your task is too noisy, or Qwen2.5-Instruct does not differ meaningfully from Base on these prompts. Do not waste compute on Spark recipes if the upper bound fails.
3.  **Baseline (BitDelta-style 1-bit):** Run the naive 1-bit baseline on the 96 items. This establishes your floor. If your complex Spark recipes cannot beat a uniform 1-bit baseline, the architecture is over-engineered.
4.  **Stage 2 (5 Spark Recipes on 24 items) $\rightarrow$ Winner on 96:** Run the search and final confirmation last. 

**What to cut if hitting a wall:** Cut Stage 2 from 5 recipes down to 2 (Uniform-32 and the top Spark recipe). Drop the validation block-by-block graft check from 24 items to 4; numerical correctness of the weight patching should be proven via unit tests on a single matrix, not validated via inference loops.

---

### Q3. Credibility & Skeptical Judge Demolitions

A skeptical judge will dismiss this 7B scale claim as a toy artifact unless you address three fatal vulnerabilities:

1.  **Gram Matrix SVD Numerics ($D^T D$):** Squaring the matrix conditions the singular values: $\sigma_i(D^T D) = \sigma_i(D)^2$. For Qwen2.5-7B layers, the condition number of $D$ can exceed $10^5$. Squaring it pushes the condition number past $10^{10}$, driving small singular values below machine epsilon in fp32 and degrading them even in fp64. **Fix:** Drop the Gram trick. Use randomized SVD (RSVD) directly on $D$, or use pivoted QR / truncated Arnoldi iterations. If you must use Gram, explicitly state the residual reconstruction error $\|D - U S V^T\|_F / \|D_F\|$; if it exceeds $1e-3$, your compression is introducing more noise than the delta contains.
2.  **The bf16-to-fp32 Upcast Mirage:** Upcasting 7B weights from bf16 to fp32 during streaming hides the fact that the underlying base model was trained and operates in bf16. More critically, applying a fp32 low-rank patch to a bf16 base model during inference introduces mixed-precision rounding errors that do not exist when the model is run natively. 
3.  **Logprob-Only Scoring on 96 Items:** Logprobs on 96 probe questions are statistically insignificant for a 7B model. A model can achieve a better mean logprob via calibration shifts or token-frequency biases while suffering catastrophic degradation in reasoning or generation coherence. Furthermore, 96 items provide wide confidence intervals; a margin of 0.1 nats is likely within the noise floor.
4.  **Embedding and `lm_head` Scale Mismatch:** The embedding and `lm_head` matrices account for over $4.3\text{ GB}$ of the delta parameters alone. Treating them with the same low-rank recipes as hidden layers will corrupt token representations. Did the Spark recipe optimize these, or were they left uniform/uncompressed? If uncompressed, state the exact byte budget consumed by the vocab matrices versus hidden layers.

---

### Q4. The Streaming Demo: Honesty vs. Theater

Per-token re-streaming on a CPU-only box (12 threads, NumPy) to demonstrate AirLLM-style patching is **performance theater**, not an engineering proof.

*   **The Timing Reality:** To generate a single token with Qwen2.5-7B streamed layer-by-layer from disk (even via fast NVMe memmap), the system must read $\sim 15\text{ GB}$ of weights across 28 layers for *every single token generated*. At a generous disk read speed of $3\text{ GB/s}$, raw sequential IIO takes $\sim 5\text{ seconds per token}$. With NumPy overhead, upcasting, and CPU matrix multiplication for 3584-dimensional hidden states, generation speed will be **$\approx 0.05$ tokens per second** (one token every 20 seconds). 
*   **What Must Be Stated:** You must explicitly report:
    1. Time-to-first-token (loading the first block + prompt processing across all layers).
    2. Inter-token latency (seconds per generated token).
    3. The exact I/O throughput of the storage medium (SSD vs. HDD) during the demo.
*   **The Cleaner Demonstration:** Do not run greedy generation token-by-token. It tests your I/O loop and Python overhead, not the quality of the Fraction Compressor. Instead, run a **batched prefill perplexity evaluation** on a held-out text file (e.g., 1KB of WikiText). Stream the blocks *once* per sequence, apply the patches, compute the total cross-entropy loss, and report wall-clock time for the full evaluation pass. That proves the model runs under memory constraints without turning your evaluation into a benchmarking of Python's disk-reading latency.
