# Fresh perspectives: three models never used in this project

Date: 2026-10-28. The identical brief below was sent, one call each (plus one
retry where a call returned no final answer), to three models that have never
been used anywhere in this project, all via the Fireworks API. Every call is
logged in results/api_usage_log.jsonl with purpose "fresh_perspective".

Outcome up front: only one of the three produced a reply. DeepSeek V4.1 Flash
and Kimi K3 each spent the entire 8,000-token completion budget on hidden
reasoning and were cut off (finish_reason "length") with an empty final
answer, on the first attempt and on the retry. Their sections below record
that failure honestly; nothing they drafted internally is presented as a
reply. GPT-OSS 120B answered fully (2,493 completion tokens, finish_reason
"stop") and its reply is reproduced verbatim.

## The brief (sent identically to all three models)

You are a fresh outside reviewer who has never seen this project. Read the summary, then answer the five questions directly and specifically. We want a genuinely new perspective: disagreements, blind spots, and judge-style attacks are more valuable than praise.

PROJECT SUMMARY: Fraction Compressor v0.4 (a hackathon project)

The tool compresses the difference ("delta") between a base AI model and its fine-tuned version into a tiny patch file. The delta is stored as a factored 1-bit representation (sign bits plus low-rank factors, with a per-layer rank allocation called a "recipe"), at roughly 1 bit per weight. On a Qwen2.5-0.5B base/Instruct pair, the full delta is about 988 MB in fp16; the patch is about 19 MB, roughly 50x smaller. A script converts an existing fine-tune into a patch automatically, with no retraining. Once loaded, patches can be swapped in and out of the running base model live, in about 0.1 seconds per swap.

Muse Spark (via the Meta Model API) sits inside the product loop in two roles: it designs the per-layer rank recipes, and it judges benchmark results, with every verdict required to cite the exact result file it rests on.

Headline results. On three base/fine-tune pairs, byte-fair recipes designed by Spark beat the human "uniform" recipe (same rank everywhere) at the same byte budget, on 96 fresh held-out questions scored by mean target logprob (gap closed = how much of the base-to-full score gap the patch recovers):
- Qwen2.5-0.5B: Spark recipe 23.2% of the gap closed vs uniform 2.1%.
- SmolLM2-360M: Spark recipe wins on raw logprob (gap-closed exceeded 100% for both, because patched models outscored the full delta itself, so the ratio is not a recovery fraction on this pair).
- Llama 3.2 1B: Spark recipe 15.9% vs uniform -7.6%. The uniform recipe scored below the base model itself; the AI-designed allocation stayed positive.

The weak case. A real skill test used NuExtract-1.5-tiny, a JSON-extraction fine-tune of the same Qwen base (10 prompts, judged on whether the output parses with correct keys and values). Unforced: the full fine-tune passes 9/10, the plain base 0/10, the rank-32 patch 1/10. The failure is concentrated at the first generated token: the skill is "gated" by whether generation starts at all (start the JSON vs emit end-of-text). First-token margins (logprob of the fine-tune's actual first token minus logprob of end-of-text): base -6.33, patch -1.29, full fine-tune +4.60. Making the patch bigger barely helped (rank 64 and rank 128 each passed 2/10), and a Spark recipe that spent the same bytes mostly on the embedding and attention output did worse (0/10).

The control test. We then forced the fine-tune's own first token and let each model continue. Forced base: 7/10 clean (8 counting a partial). Forced patch: 8/10 clean plus 1 partial, exactly matching the full fine-tune's unforced score. Interpretation we now ship: most of the extraction skill was already latent in the base; what fine-tuning mainly installs, for this skill, is the decision to start; the patch moves the start decision about halfway (-6.33 to -1.29 toward +4.60) but usually does not cross it. This finding was re-checked by script recomputation and by five AI validators (Muse Spark, Muse Glimmer, Gemini, and Muse Spark Open via two providers); all numbers held, and the validators required us to hedge the claim that the patch has a "real edge" beyond the trigger, because at 10 prompts the lead is within sampling noise.

Quantum component. The audit sample of benchmark items was selected using random bytes produced by a real IBM quantum computer (one 32-qubit job, 2,048 shots, on ibm_fez). The audit recomputed the reported numbers from the per-item records: 41 of 41 checks passed.

Context. This is an entry in the Meta Global AI Developer Hackathon, theme "Push the Frontier", indie developer track, solo participant. Judging weights: Impact 30%, Use of Meta AI Tooling 25%, Demo 25%, Technical Depth and Execution 20%. Demo is a 3-minute video centered on the live hot-swap: same prompt, base model fails, a 19 MB file swaps in, same prompt succeeds.

QUESTIONS:
1. Your fresh perspective: what is genuinely new here, if anything? And what are we missing, or fooling ourselves about?
2. Attack this as a judge in this hackathon: what are the weakest points under each criterion (Impact, Use of Meta AI Tooling, Demo, Technical Depth)?
3. Is the first-token gate story a real phenomenon, or an artifact of this one 10-prompt test? What would settle it?
4. Name one concrete experiment you would run next to push the frontier further. Be specific enough that we could run it.
5. Where could Meta's own models (Muse Spark via API, Muse Spark Open, Muse Glimmer) be pushed harder inside this project?

---

## DeepSeek (accounts/fireworks/models/deepseek-v4p1-flash)

NO REPLY. Two calls were made (prompt 1,192 tokens each; 8,000 completion
tokens each). Both returned an empty final answer: all 8,000 completion
tokens were consumed by reasoning_content and the responses ended with
finish_reason "length" before any answer text was emitted. Per the task
rules (one retry at the same settings, then record the failure honestly),
no further attempt was made. Nothing from the reasoning drafts is quoted
here as a perspective; one checkable lead found in those drafts is handled,
labeled as such, in the synthesis at the end of this file.

---

## Kimi (accounts/fireworks/models/kimi-k3, Moonshot)

NO REPLY. Two calls were made (prompt 1,180 tokens each; 8,000 completion
tokens each). Same failure shape as DeepSeek: empty final answer on both
attempts, all completion tokens consumed by reasoning_content,
finish_reason "length" each time. No further attempt was made.

---

## GPT-OSS 120B (accounts/fireworks/models/gpt-oss-120b, OpenAI open weights)

Reply received in full (prompt 1,220 tokens, completion 2,493 tokens,
finish_reason "stop"). Verbatim:

**1. What is genuinely new, and what are we fool‑ing ourselves about?**  

| What‑is‑new | Why it‑might matter | What we’re probably overstating |
|-------------|--------------------|--------------------------------|
| **A 1‑bit factored delta format** that can turn a ~1 GB fp16 fine‑tune into a ~19 MB patch (≈50× compression) **without retraining**. | The “no‑re‑train” claim is rare – most low‑rank adapters require a second‑stage fine‑tune on the low‑rank factors. If the math truly preserves the full‑delta’s expressive power at that size, it opens a new class of “plug‑and‑play” model upgrades for edge devices. | The compression ratio is reported only for a single 0.5 B model pair. The storage savings may evaporate on larger models (rank allocation grows super‑linearly) and on real‑world pipelines that need versioning, integrity checks, and meta‑data. |
| **Automated per‑layer “recipe” generation** via Muse Spark that outperforms a naïve uniform rank allocation on the same byte budget. | Demonstrates that a language model can meaningfully allocate a tiny budget across layers, hinting at meta‑learning of model‑update strategies. | The improvement (23 % vs 2 % gap‑closed) is measured on a *single* held‑out question set (96 items) using **mean target log‑prob** – a proxy that does not correlate strongly with downstream task success. The “recipe” may simply be over‑fitting the benchmark distribution. |
| **Live hot‑swap of a 19 MB patch** in ≈0.1 s. | Nice for demos, but the engineering cost (reload, re‑allocate GPU memory, re‑wire kernels) is not disclosed. In production a 0.1 s pause is a *service‑level* impact; we don’t know if the swap is safe under multi‑threaded serving or distributed inference. | The demo shows a single prompt; we never see stability across batches, back‑to‑back swaps, or failure handling. It’s more a visual trick than a production‑ready capability. |
| **Quantum‑derived random seed** for benchmark selection. | A clever story‑teller’s flourish, but adds zero scientific value. | It distracts from the core reproducibility concerns (tiny test sets, cherry‑picked prompts). The “audit” of 41/41 passes is a tautology because the same seed produced the same items. |

**Bottom line:** The compression format and recipe automation are the only plausible novelties; everything else (demo, quantum seed, impact claims) is veneer. The biggest blind spot is the *scale* and *robustness* of the approach – a 0.5 B model is not representative of the 10–100 B models that most Meta products run, and the evaluation methodology is far too narrow to claim “real edge”.  

---

**2. Judge‑style attack: weakest points per hackathon criterion**  

| Criterion | Weakness #1 (most fatal) | Weakness #2 (secondary) |
|-----------|--------------------------|--------------------------|
| **Impact (30 %)** | *Limited real‑world impact*: 19 MB patches are only useful if you need to ship upgrades to *tiny* edge devices; Meta’s core workloads are on multi‑hundred‑GB models where a 1 bit delta would still be tens of GB. | *Task relevance*: Gap‑closed on a synthetic log‑prob benchmark does not translate to downstream performance (e.g., code generation, retrieval). |
| **Use of Meta AI Tooling (25 %)** | *Tooling is a black‑box*: The project calls Muse Spark to design recipes and judge results, but provides no insight into prompts, temperature, or prompt‑engineering that made Spark succeed. This makes the contribution non‑reproducible and essentially “we outsourced the hard part”. | *Over‑reliance on APIs*: The pipeline is tethered to proprietary endpoints (Meta Model API). If those services change, the whole recipe generation breaks. |
| **Demo (25 %)** | *Demo is a gimmick*: A 3‑minute video of a single prompt swapping a patch is impressive visually but tells nothing about latency under load, memory fragmentation, or failure modes. Judges cannot verify the claim without running the code. | *No quantitative metrics*: No latency histogram, no throughput comparison, no memory footprint before/after swap. |
| **Technical Depth & Execution (20 %)** | *Sparse experimental rigor*: Only three model pairs, one 10‑prompt skill test, and a single random‑byte selection method. No ablation (e.g., varying rank budgets, alternative compression schemes) and no baseline against existing adapters (LoRA, IA³). | *Engineering opacity*: The 0.1 s hot‑swap claim lacks profiling data, GPU utilization, or code snippets. Also, the “1‑bit factored representation” is not formally described (no entropy analysis, no error‑bounds). |

The *deal‑breaker* for the hackathon is the **lack of robust, reproducible evaluation**; judges will see a flashy demo but no evidence that the technique scales or truly solves a pressing problem for Meta.

---

**3. Is the first‑token gate story real or a 10‑prompt artifact?**  

*Probability*: **High chance it is an artifact**. The test set is only 10 JSON‑extraction prompts, all sharing the same “gate” (first token must be “{”). The base model’s first‑token log‑prob is uniformly low (‑6.33), the patch lifts it to ‑1.29, but the variance is huge relative to the gap to the fine‑tuned (+4.60). With n = 10, a single outlier can swing the pass rate from 0/10 to 2/10.

**What would settle it?**  

1. **Scale up the probing set**: generate ≥ 500 diverse JSON‑style prompts (different key sets, nesting depths, varied prefixes) and evaluate first‑token log‑prob distributions for base, patch (multiple rank budgets), and full fine‑tune.  
2. **Statistical test**: perform a paired bootstrap (or permutation) test on the first‑token margin to see if the patch improvement is significantly different from zero at α = 0.01.  
3. **Control for randomness**: run each model with multiple seeds (temperature = 0, deterministic) to isolate the effect of the weight delta from sampling noise.  
4. **Ablation on “gate” location**: shift the decision point deeper (e.g., second or third token) by designing prompts where the start token is not a punctuation symbol but a word; see whether the patch still moves the margin.  

If after these steps the patch consistently moves the first‑token probability across the decision boundary on a statistically significant fraction of prompts, the gate phenomenon is real. Otherwise it’s a cherry‑picked anecdote.

---

**4. Concrete next experiment (runnable now)**  

**Goal**: Test whether the 1‑bit factored delta can *exactly* reproduce a full fine‑tune when given enough bits, and to map the *bit‑efficiency curve*.

**Steps**  

1. **Select a mid‑sized model** (e.g., Llama‑2‑7B) and a publicly available fine‑tune (e.g., Alpaca‑LoRA).  
2. **Compute the full delta** (fp16) between base and fine‑tune.  
3. **Create a series of patches** with increasing per‑layer rank budgets:  
   - Budget 1 % of total weights (≈ 0.5 % bits).  
   - 2 %, 5 %, 10 %, 20 % … up to 100 % (i.e., storing the full fp16 delta).  
   - For each budget, run the *recipe optimizer* (Muse Spark) and also a *uniform* baseline.  
4. **Evaluation**:  
   - On a standard benchmark (e.g., MT‑bench or TruthfulQA), compute **Δlog‑prob** relative to the base and to the full fine‑tune.  
   - Plot **gap‑closed vs bits per weight** for both Spark‑generated and uniform recipes.  
   - Additionally, measure **inference latency & memory overhead** for each patch size.  
5. **Success metric**: Identify the *knee point* where adding more bits yields diminishing returns (e.g., < 1 % extra gap‑closed per additional 0.1 bit/weight).  

**Why this matters**: It directly addresses the open question of *scalability* and *efficiency*: does the 1‑bit factorization truly capture the fine‑tune’s information, or is the 23 % gap‑closed on Qwen a fluke of a tiny model? The curve will also give judges a tangible “technical depth” artifact to inspect.  

---

**5. Where Meta’s own models could be pushed harder**  

| Component | Current use | Aggressive upgrade |
|-----------|-------------|--------------------|
| **Muse Spark (recipe design)** | Prompted to allocate per‑layer ranks; no feedback loop. | Turn Spark into a *reinforcement‑learning* optimiser: give it a reward function that directly maximizes *gap‑closed* on a held‑out validation set, let it iteratively propose new recipes, and incorporate *policy gradients* to converge on a globally optimal allocation. |
| **Muse Spark Open (validation)** | Used only to re‑cite numbers after the fact. | Deploy it as an *online auditor* that runs the patch on a *stream* of random user queries (e.g., from Meta’s public datasets) and flags any divergence > ε in output distribution. This would surface systematic failures (like the first‑token gate) early. |
| **Muse Glimmer (debugger / interpretability)** | Not used at all. | Apply Glimmer to visualise *gradient sensitivity* of the low‑rank factors versus the original weights. Use its attention‑map outputs to identify layers where the 1‑bit compression is throwing away critical information, then feed that insight back into Spark’s recipe search. |
| **Meta Model API (serving)** | Only for demo hot‑swap. | Integrate the patch loader into Meta’s *TensorRT‑style* inference runtime, measuring real‑world throughput, memory fragmentation, and fail‑over latency. Show that the hot‑swap can happen while the model is serving a batch of requests, not just in a controlled script. |
| **Quantum random seed** | Single IBM‑fez job for benchmark selection. | Replace the toy quantum‑seed with a *quantum‑generated distribution* for *hyper‑parameter search*: e.g., let a quantum circuit sample candidate rank budgets, then evaluate on the Spark‑feedback loop. This would actually leverage quantum randomness for a non‑trivial optimisation. |

By moving these components from *passive* utilities to *active* optimisation, validation, and serving elements, the project would demonstrate a deeper integration with Meta’s AI stack and would address the current critique that the “Meta tooling” contribution is superficial.

---

## Synthesis (by Ember, after checking every checkable claim against the repo and the literature)

### What is genuinely NEW in this round

1. **Named prior art for the core format: BitDelta and Delta-CoMe (both NeurIPS 2024).**
   This lead surfaced in the discarded reasoning drafts of both no-reply models
   (named here only as the source of the lead, not as a reply) and is consistent
   with GPT-OSS's novelty skepticism. I verified both papers independently:
   - BitDelta (Liu et al., arXiv 2402.10193) already does post-fine-tuning
     1-bit quantization of the delta, with the same "one high-precision base
     plus many small 1-bit deltas" multi-tenant pitch, validated on models up
     to 70B with minimal degradation.
   - Delta-CoMe (Ping et al., arXiv 2406.08903) already does training-free
     delta compression via SVD with per-component mixed precision, and
     explicitly warns that low-rank and low-bit compression can significantly
     harm task-specific fine-tunes.
   Spark, Gemini, and Glimmer never named either paper; their prior-art
   pressure stopped at LoRA in general terms (results/why_debate.md). The
   consequence is real: the 1-bit factored delta format itself is not the
   defensible novelty. What remains defensible is (a) a Meta LLM designing
   per-layer rank recipes inside the product loop and judging with file
   citations, (b) the first-token gate diagnosis with a force-start control,
   and (c) the recomputation/audit harness. A knowledgeable judge can be
   expected to raise BitDelta by name.

2. **The scale axis, pressed as an experiment rather than a caveat (GPT-OSS).**
   All project evidence is sub-1B models. Earlier reviewers flagged limited
   generality ("3 pairs", "ANY is too strong") as a wording problem. GPT-OSS
   turns it into the central technical question and proposes a runnable
   answer: a bit-efficiency (gap-closed vs bits-per-weight) curve on a 7B
   pair, Spark recipe vs uniform, to find the knee. Nobody earlier proposed
   the rate-distortion curve as the missing artifact.

3. **No empirical baseline against existing delta codecs (GPT-OSS).**
   Earlier reviewers raised LoRA only as fairness wording for the
   download/install contrast. GPT-OSS raises the experimental version: there
   is no head-to-head against LoRA, IA3, or (by extension of point 1) a
   BitDelta-style sign-plus-scale baseline at the same bytes. That is the
   comparison a Technical Depth judge will ask for first.

4. **Swap safety under real serving (GPT-OSS), sharper than the earlier memory caveat.**
   Gemini noted the base must stay resident and concurrent serving changes
   the memory math. GPT-OSS adds what nobody raised: no evidence the 0.1 s
   swap is safe under batched/multi-threaded serving, and no latency,
   throughput, or memory profiling of the swap at all.

5. **A concrete settling protocol for the gate (GPT-OSS Q3).**
   Earlier consensus was "one 10-prompt test does not prove a general wall"
   (Spark) plus the force-start control, which settled the mechanism for this
   test. GPT-OSS adds testable extensions nobody proposed: 500+ diverse gated
   prompts, paired bootstrap on the margin, and moving the decision point
   deeper than token 1 (non-punctuation gates) to see whether the effect
   follows the decision point or the token position.

### What repeats earlier criticism (already on record, not new)

- Gap-closed is a logprob proxy, not downstream task success; 23.2% closed
  means most of the gap is not recovered; the patch is for switching and
  distribution, not replacement. (Spark, why-debate Q1 and Q3.)
- Generality wording: three pairs and ten prompts do not support "any
  fine-tune" claims. (Spark, why-debate Q2.)
- The base model must stay loaded; serving memory caveats. (Gemini Q1,
  Spark Q1.)
- The quantum component contributes selection randomness, not evidence;
  the audit establishes arithmetic consistency of reported numbers. (In line
  with the hedging the five validators already required.)

### Disputes from this round, checked before crediting

- GPT-OSS: "the compression ratio is reported only for a single 0.5B pair."
  NOT CREDITED as stated. results/second_pair_stage2.json and
  results/third_pair_stage2.json record real-shape patch byte counts for the
  SmolLM2-360M and Llama 3.2 1B pairs too. Credited only in weaker form: the
  ~50x headline and the demo are Qwen-pair specific.
- GPT-OSS: "the 41/41 audit is a tautology because the same seed produced
  the same items." NOT CREDITED. results/quantum_audit.json shows the
  quantum bytes selected WHICH held-out items to recheck; the 41 checks then
  recomputed the reported aggregates from the per-item records in
  results/alien_sweep_heldout.json. Selection and recomputation are
  different steps. The fair residue (a self-audit proves consistency, not
  that the original runs were correct) is already how the project presents
  it after validator hedging.
- GPT-OSS: "Muse Glimmer: not used at all." NOT CREDITED. Glimmer was used
  as a referee and validator (results/glimmer_reference.md,
  results/glimmer_reference_addendum.md, results/glimmer_validation_forced.md),
  and the brief itself listed Glimmer among the five validators of the gate
  finding. Its Q5 interpretability suggestion is still usable, but it rests
  on a false premise about current use.
- The BitDelta / Delta-CoMe prior-art lead (from the two reasoning drafts):
  CREDITED after independent verification, as recorded in point 1 above.

### Process finding

Two of the three fresh models could not return any final answer to this
brief inside an 8,000-token completion budget, spending all of it on hidden
reasoning, twice each. Anyone building an "ask several models" step into a
product loop should budget reasoning-heavy models far above 8,000 tokens,
or constrain reasoning explicitly, or they will silently get nothing.

### Bottom line

The fresh round's real yield is a correction, not a compliment: the format
has named, published prior art (BitDelta, Delta-CoMe), so the submission's
novelty claim has to rest on the in-loop LLM recipe design and judging, the
gate diagnosis, and the verification harness, and the two attacks most
likely to land in judging are the missing baseline comparison and the
missing scale evidence. GPT-OSS's bit-efficiency curve on a 7B pair would
answer the second; a same-bytes BitDelta-style baseline would answer the
first.
