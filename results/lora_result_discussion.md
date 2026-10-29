# Panel discussion: the LoRA result, recovery tuning, and the value claim (internal, local only)

Provenance: Vinay asked on Thu Oct 29, 2026 (late morning ET) for a panel DISCUSSION on the matched-byte LoRA result and what follows from it, after working out the recovery tuning idea with Gemini earlier that day. Two rounds: Round 1 independent positions, Round 2 each panelist read the others' Round 1 answers and gave a final position. Order and routes: Muse Spark 1.3 first via the Meta Model API (logged in results/api_usage_log.jsonl, purpose "lora result discussion"; Round 1: 1,221 prompt, 3,684 completion, 4,905 total tokens; Round 2: 4,408 prompt, 2,231 completion, 6,639 total); Gemini gemini-3.5-flash-lite via the connector helper (also logged; Round 1: 1,324 prompt, 700 completion, 2,024 total; Round 2: 4,804 prompt, 396 completion, 5,200 total); Nemotron, Glimmer, Grok, and Claude via Flash's local OmniRoute gateway (http://localhost:20128/v1, temperature 0.3, max_tokens 8000), which are Flash-local calls and not logged in api_usage_log.jsonl; this file is their record. Claude was called ONLY on the verified antigravity/claude-opus-4-6-thinking route. Nothing pushed, nothing posted. The recovery tuning design under discussion is results/recovery_tuning_design.md (frozen Oct 29, 2026; run queued).

## Converged conclusion

The panel converged on this: the LoRA result stands as filed (the adapter wins quality at matched bytes on this probe distribution, the overshoot above the full fine-tune is consistent with style specialization and not proven as its cause, and the cost asymmetry is part of the result, not a footnote). Recovery tuning is a legitimate and well-frozen pilot of a narrow empirical question: whether a data-free 1-bit factored patch, used as the starting point for a brief distillation pass, retains any of that training gain after being forced back through its own quantizer at the identical byte count, beyond what the same brief training achieves from a random start. Patch as initialization is not a new method; every panelist who answered called it recovery fine-tuning or warm starting, known practice, and the only claimable novelty is the empirical survival question at 1 bit and identical bytes. The dollars claim is honest in mechanism and small in magnitude: the savings are real for distributors pushing many variants to many recipients on metered bandwidth (about 969 MB saved per transfer, on the order of $850 versus $15 per push at 10,000 recipients and $0.09 per GB egress) and trivial in storage (about $2.20 per month per 100 variants), they do not extend to anyone who can afford to train, and they carry a live liability the project must keep stating: the pure patch is worse than the base model on first-token accuracy (0.010 vs 0.031), so a recipient can experience the cheap artifact as a regression. Four of five panelists predict the re-quantized recovery headline lands between about 0.18 and 0.38 gap closed, i.e. little or no gain over the untouched patch's 0.232, with the trained fp16 diagnostic higher (about 0.35 to 0.8); Gemini alone predicts 0.45 to 0.65. Named mind-change thresholds: a re-quantized headline at or above roughly 0.55 to 0.6, or the patch initialization beating the matched control by 0.3 gap or more.

Agreed positioning (merged from the Grok and Glimmer drafts, amended by Spark, Nemotron, and Gemini in Round 2; every answering panelist's final Q3 is a variant of this): Fraction Compressor is a deterministic, zero-query, data-free coder that turns a full fine-tune delta into a 19 MB 1-bit factored patch recovering about a quarter of the fine-tune logprob gap. It is a distribution format with an explicit quality ceiling, not a substitute for distillation: at matched bytes a trained LoRA adapter is the quality winner whenever training is allowed. Whether the patch, used as initialization, retains training gain through its own quantizer beyond a matched-budget control is an open pilot, and no training-cost saving should be claimed until that control reports.

## Design changes demanded for the queued recovery run

MUST FIX BEFORE THE RUN (unanimous, 5 of 5 answering panelists by the end of Round 2): add a matched-budget control run. Random or zero initialization in the SAME U/V parameterization and rank map, same 101 steps, same learning rate 2e-5 and schedule, same 1,350 training prompts and data order, same re-quantizer, scored on the same 96 probes. Cost: one extra short training run, no new teacher generations. Without it, any gain is fully confounded between "the patch initialization held part of the answer" and "101 steps of KL training helps from anywhere," and the run cannot support the claim it exists to test. Spark adds: label the experiment a pilot (one seed) and make no cost-saving claim from it alone; also do not compare the 101-step factors against the 1,014-step LoRA adapter, since the parameterizations and fp16 prices differ (43 MB vs 18.7 MB).

RECOMMENDED, NOT AGREED (Grok, 1 of 5): re-quantize and score the intermediate checkpoints at the already-logged steps (0, 25, 50, 75, 101) as diagnostics only, headline unchanged. Grok's argument: validation KL is computed in fp32 and cannot distinguish a dead 1-bit update from a late peak, so the KL trajectory alone cannot interpret the headline. The other four held that the planned KL logging is enough and that intermediate scoring spends extra looks. Gemini separately suggested logging validation KL every 10 steps instead of every 25; nobody else took a position on the denser grid.

REJECTED BY THE PANEL: best-checkpoint selection replacing the frozen step-101 headline (5 of 5 against; it would spend the validation signal and break the fixed-budget claim). Quantization-aware training or a straight-through estimator, and promoting the fp16 diagnostic to the headline: demanded by Glimmer in Round 1, withdrawn by Glimmer in Round 2, and explicitly rejected by Spark and Grok on the ground that forcing the trained delta back through the shipped quantizer is the experiment; a null result through that quantizer is a result about the format the project actually ships.

## Sharpest disagreements

1. The prediction split. Gemini stands alone at 0.45 to 0.65, arguing that 101 gradient steps will smooth the initial factorization's quantization noise and that the 1-bit bottleneck will act as a regularizer rather than an eraser. The other four expect the quantizer to erase most of the gain. Nemotron moved during the discussion, from 0.35 to 0.55 in Round 1 down to 0.20 to 0.38 in Round 2, joining the pessimistic cluster and saying so. This disagreement is empirical and the run settles it; it is recorded here so the predictions cannot be retrofitted.
2. Grok versus the field on intermediate scoring (above): whether the validation KL trajectory can interpret a 1-bit headline at all. Unresolved; the moderator notes the frozen design already logs KL at five steps, and Grok's diagnostic scoring is cheap to add without touching the headline rule, but only Grok demanded it.
3. A rejected inference. Nemotron's Round 1 positioning draft implied the LoRA adapter's overshoot is evidence that the factored patch preserves the fine-tune direction better than random initialization. Grok rejected that outright in Round 2 (a LoRA overshoot says nothing about this U/V patch versus random init), and Nemotron abandoned the framing, adopting Glimmer's draft instead.

## Record notes

- Gemini's Round 1 answer arrived with its Q3 quote signed "Claude"; recorded as received.
- Glimmer's Round 2 answer restated its prediction as 0.20 to 0.35 (Round 1: 0.28 to 0.38) and its dollars text closely parallels Spark's figures; recorded as received.
- Grok's first Round 2 call returned a tool-call preamble only; the retry answered in full and is the answer of record.
- Claude (antigravity/claude-opus-4-6-thinking): NO ANSWER in either round. Round 1: two calls (initial plus the one permitted retry with tool_choice "none"), both finish reason "tool_calls" with only a preamble about checking its memory; served model confirmed. It was not sent a Round 2 pack it could not have answered; the failure is recorded once here for both rounds.
- GPT-OSS 120B (nvidia/openai/gpt-oss-120b): NO ANSWER. Round 1 initial call and the one permitted retry both returned upstream HTTP 410 model_shutdown, the same provider shutdown recorded in the Oct 28 and Oct 29 panels.

## Round 1 question pack (sent verbatim to all panelists)

You are one panelist in an internal DISCUSSION panel for the Fraction Compressor project (hackathon, submission due Nov 4, 2026). This is a debate round, not a verdict form: argue your position, name predictions, and say what evidence would change your mind. There will be a Round 2 where you see the other panelists' answers. Be direct. At most about 600 words total, structured as Q1 / Q2 / Q3. The panelists are Muse Spark, Gemini, Nemotron, Glimmer, Grok, and Claude.

ESTABLISHED RESULT (matched-byte LoRA baseline, Qwen2.5-0.5B base/Instruct pair, same 96 held-out probes and scoring as every project result; gap closed = (config minus base) / (full minus base) on mean target logprob):
- base: logprob -11.1498, gap closed 0.000, first-token accuracy 0.031
- full fine-tune (987,922,432 B fp16): -8.5425, 1.000 by definition, first-token 0.167
- lite factored patch, the project's headline (19,358,176 B): -10.5451, gap closed 0.232, first-token 0.010
- LoRA adapter distilled from the full fine-tune (rank 17, 18,696,192 B, smaller than the patch): mean logprob -7.5987 over 3 seeds, gap closed 1.362, first-token accuracy 0.167 to 0.177 (ties the full fine-tune, wins on confidence across the answer, not on first picks)
- Costs: the adapter took 1,500 teacher generations plus about 8 hours of CPU gradient training (3 seeds, 1,014 steps each). The factored patch is a deterministic, zero-query conversion of the delta weights: minutes, no training, no prompts, no teacher.
- The previous panel round ruled: the adapter overshooting the full fine-tune (gap closed above 1.0) is "consistent with" style specialization, not proven caused by it, because the 1,500 distillation prompts and the 96 eval probes share one author (Muse Spark) and the same three style buckets (knowledge, instruction, math), items disjoint and novelty-checked. One panelist added a competing mechanism: forward-KL distillation can change distribution shape (confidence) without changing first picks. An out-of-style control (fresh adapter, prompts by a different author in a deliberately different style, same 96 probes) is RUNNING now; its result is not in yet.

NEW PROPOSAL 1: RECOVERY TUNING (Vinay's idea, design frozen, run queued; it can still be amended if this panel demands changes). Initialize training from the shipped lite factored patch instead of from random: the patch's U and V factors (145 matrices) become trainable fp32 parameters starting exactly at the shipped values, base frozen. Train briefly on the SAME stored distillation set (1,350 train prompts, teacher answers already generated, no new teacher cost in this study): soft forward-KL, temperature 1, at teacher-answer positions, teacher run online. Budget: 101 optimizer steps at batch 8, which is 10 percent of the LoRA run's per-seed steps. One seed. Learning rate 2e-5 (inside the 1e-5 to 5e-5 band Gemini suggested for factor training; the LoRA run used 2e-4 from a random start). No checkpoint selection: the state after step 101 is the result, validation KL logged only. Then the trained delta is RE-QUANTIZED with the compressor's own 1-bit factored quantizer at the shipped per-matrix ranks, and the byte count must come out at exactly 19,358,176 B; only that re-quantized patch is the headline result. A secondary row keeps the trained factors in fp16 (43,422,720 B) labelled as a diagnostic only. Scoring: same pipeline, same 96 probes, and the eval path must first reproduce the stored untouched-lite rows. Interpretation rule frozen in advance: report whatever comes out, including if re-quantization kills the gain.

NEW PROPOSAL 2: THE VALUE CLAIM IN DOLLARS. Proven savings claimed today: (a) distribution: a 19 MB patch instead of a 988 MB full model per update, per recipient; (b) storage: one shared base plus many small patches instead of a full model copy per behavior; (c) zero conversion cost for the pure patch (minutes on a CPU, no GPU, no data). Conceded: at matched bytes, quality goes to training (the LoRA result above). The hope: if recovery tuning works, patch initialization cuts adapter training cost for practitioners, because training starts from a data-free artifact that already holds part of the answer instead of from random.

Q1. RECOVERY TUNING. Is the design sound? What do you predict the re-quantized headline row will show (give a number or range for gap closed), and what result would change your mind about the idea? Is "patch as initialization" a real contribution, or a restatement of known recovery fine-tuning / quantization-aware training practice? Name any design flaw that would make the result uninterpretable, and say whether it must be fixed before the run.

Q2. THE DOLLARS CLAIM. Is the framing honest and complete? Who concretely benefits, in dollars, and who does not? What is the strongest counterargument a skeptical judge or practitioner would make?

Q3. POSITIONING. Given the LoRA result, the pending out-of-style control, and the recovery test, state the project's contribution in one or two sentences you would sign your name to.

## Round 1 answer: Muse Spark 1.3 (Meta Model API)

(served model muse-spark-1.3; usage {'completion_tokens': 3684, 'prompt_tokens': 1221, 'total_tokens': 4905, 'completion_tokens_details': {'reasoning_tokens': 2792}, 'prompt_tokens_details': {'cached_tokens': 0}})

**Q1. RECOVERY TUNING**

Design is half-sound and currently uninterpretable for its own claim. Good parts: start exactly at shipped values, frozen interpretation including quant-kill, no checkpoint picking, must reproduce untouched-lite rows, headline is only the re-quantized 19,358,176 B artifact. That prevents moving the goalposts.

Prediction: re-quantized headline **gap closed 0.20-0.35, centered on 0.232** - i.e. no real gain. Unquantized fp16 diagnostic 0.5-0.8. Reason: 101 steps x batch 8 = 808 samples, ~0.6 epoch, at lr 2e-5 from an fp32 start, then forced through the project's own 1-bit per-matrix quantizer. Small updates don't survive 1-bit re-quantization. That is the classic QAT failure when you train full-precision then post-quantize without quant-aware steps.

What would change my mind: re-quantized >=0.6, or a clean separation where patch-init beats random-init by >=0.3 gap at identical budget and bytes. Anything <0.4 is noise / failed recovery.

Contribution: "patch as initialization" is not new. It's warm-start + recovery fine-tuning + QAT, known for decades. The only novel instantiation would be *showing it survives 1-bit factored delta quant at same bytes.* That would be minor but real.

Must-fix flaw before run: **no matched-budget control.** Without a random-init run with the *same* U/V architecture, same 101 steps, same lr, same 1,350 prompts, same re-quant, you cannot attribute anything to initialization. "101 steps helps from anywhere" vs "patch holds part of the answer" are fully confounded. That's cheap - no new teacher cost, same data - add it now. Secondary: one seed makes a 0.1-gap effect uninterpretable; call this a pilot, don't claim cost savings. Also don't compare 101-step factors to 1,014-step LoRA rank-17; architectures and fp16 sizes (43MB vs 18.7MB) differ.

**Q2. THE DOLLARS CLAIM**

Directionally honest, magnitudes omitted, and therefore misleading as a value claim.

Who benefits, concretely: a distributor pushing many behavior variants to many recipients on metered egress, or versioning many variants. Math: ~969 MB saved per transfer. At $0.09/GB egress that's ~$0.087/recipient/update, ~$870 per 10k pushes. Storage: 100 variants as full fp16 = ~99 GB; as base+19MB patches = ~2.9 GB; at $0.023/GB-mo that's ~$2.20/mo saved. Peanuts.

Who does not benefit: anyone optimizing quality-per-byte or total cost including accuracy. Conceded result: at matched ~19MB, distilled LoRA gap 1.36 beats patch gap 0.232, ties full fine-tune on first-token. Storage and bandwidth are cheap; wrong answers are expensive. Zero-conversion-cost is true and the only unique property, but you get what you pay for: 23% of the gap.

Strongest skeptic line: "You compare 19MB vs 988MB full fp16, not vs gzip delta, vs quantized base, vs the 18.7MB LoRA that beats you. LoRA also gives (a) and (b). Your (c) saves minutes of CPU to lose ~75% of achievable quality." Until recovery tuning preserves training gain through re-quant, there is no dollar case for quality-sensitive users.

**Q3. POSITIONING**

I would sign: "Fraction Compressor gives a deterministic, zero-data, zero-training 19MB 1-bit factored delta that recovers 23% of the full fine-tune logprob gap; at matched bytes, distillation training dominates, and whether patch-initialization can retain training gain through re-quantization is an open pilot, not a proven saving."

Pending out-of-style control decides whether the LoRA >1.0 overshoot is style overfitting or confidence reshaping - don't claim either until it lands.

## Round 1 answer: Gemini (gemini-3.5-flash-lite)

(served model gemini-3.5-flash-lite; usage {'prompt_tokens': 1324, 'completion_tokens': 700, 'total_tokens': 2024})

### Q1. Recovery Tuning

The design is conceptually sound but methodologically fragile. Initializing from the zero-query factored patch is clever, but stopping blindly at step 101 without checkpoint selection is a gamble. Forward-KL with a temperature of 1 at 2e-5 learning rate on top of a deterministic base risks destabilizing the carefully structured U and V factors, especially given that we are re-quantizing down to 1-bit post-training. 

I predict the re-quantized headline row will land at a gap closed of **0.45 to 0.65**. It will comfortably beat the original patch’s 0.232 because 101 steps of gradient descent will smooth out the quantization noise introduced by the initial decomposition. However, it will not reach the LoRA’s 1.362, because the 1-bit quantization bottleneck will act as a heavy regularizer, clipping the expressive gains of the soft-KL loss. 

"Patch as initialization" is a novel hybrid contribution, distinct from standard QAT (Quantization-Aware Training) because we are training factored delta weights on top of a frozen base rather than quantizing a natively trained dense model. 

**Fatal design flaw:** The most dangerous flaw is coupling the final headline metric strictly to "step 101" without a validation-based stopping criterion. If the training overfits the 1,350 distillation prompts by step 75 and degrades by step 101, forcing the final checkpoint will produce artificially suppressed numbers. It should *not* block the queue, but we must log step-by-step validation KL to avoid publishing a suboptimal snapshot. 

What changes my mind? If re-quantization completely nullifies the training gains—dropping gap closed back to or below the baseline 0.232—it proves that 1-bit factor constraints are too rigid to absorb gradient updates without breaking the underlying structural decomposition.

---

### Q2. The Dollars Claim

The framing is honest about technical mechanics, but overly aggressive on commercial impact. 

* **Who benefits:** Edge-deployment infrastructure providers and multi-tenant SaaS platforms pushing frequent, specialized behavioral updates to localized instances where bandwidth and storage per tenant dictate cloud bills. 
* **Who does not:** Enterprises running homogeneous model fleets or those whose primary bottleneck is inference latency rather than distribution footprint. 

**The strongest counterargument:** A skeptical practitioner will point out that if a developer has access to the teacher model, the distillation data, and a GPU for 101 training steps, the "zero-query, zero-training" purity of the original patch is already forfeit. At that point, why not just ship the LoRA adapter (which achieves 1.362 gap closed at a nearly identical 18.7 MB) and sidestep the complex 1-bit re-quantization pipeline entirely? The economic value of saving a few megabytes is dwarfed by the engineering overhead of maintaining a custom 1-bit factor compressor.

---

### Q3. Positioning

"The Fraction Compressor delivers zero-query, deterministic delta compression that shrinks full-model behavioral updates into sub-20MB patches, while recovery tuning proves that these patches can double as high-efficiency initialization states for downstream distillation." 
— *Claude*
## Round 1 answer: NVIDIA Nemotron 3 Ultra (via Flash OmniRoute)

(served model nvidia/nemotron-3-ultra-550b-a55b; usage {'prompt_tokens': 3796, 'completion_tokens': 2133, 'total_tokens': 5929})

**Q1. RECOVERY TUNING**  
Design is sound but high-variance. The patch initialization is quantization-aware training with a structured prior—known to work, but 101 steps (10% of LoRA budget) on a single seed is a needle-in-haystack search. The re-quantization step is the real test: if the trained fp32 factors move off the 1-bit manifold, the compressor's quantizer will project them back, likely destroying gains.  

**Prediction:** re-quantized headline gap closed **0.35–0.55** (vs. untouched patch 0.232, LoRA 1.362). If it lands ≥0.70, patch initialization is a real accelerator; if ≤0.25, it's noise.  

**Design flaw that makes result uninterpretable:** no checkpoint selection + single seed. A lucky/bad step 101 could swing ±0.15 gap closed. Must be fixed before run: log validation KL every 10 steps and report the *best* re-quantized checkpoint, not the last. The "report whatever comes out" rule is fine for the headline, but the panel needs the trajectory to interpret it.  

**Q2. THE DOLLARS CLAIM**  
Framing is honest but incomplete. The three savings are real *for the pure patch only*—which currently scores **worse than base on first-token accuracy (0.010 vs 0.031)**. Practitioners who need quality will use the LoRA adapter (18.7 MB, gap closed 1.362, beats full fine-tune). The patch only wins for: (a) air-gapped/edge devices with zero GPU and strict bandwidth, (b) model marketplaces shipping thousands of behaviors over a shared base. Everyone else pays the LoRA training cost (~8 CPU-hours) and gets 6× the quality at the same byte budget.  

**Strongest counterargument:** "You're selling a 19 MB artifact that degrades first-token accuracy below base. The LoRA adapter at the same size *improves* it. Your 'hope' that patch initialization cuts training cost is unproven—and even if it works, you're comparing against a random start, not against a standard LoRA warm-start from a public checkpoint."  

**Q3. POSITIONING**  
The Fraction Compressor demonstrates that a deterministic, zero-compute 1-bit factored quantization of a fine-tune delta retains ~23% of the quality gain at 2% of the size, and that this compressed artifact serves as a non-trivial initialization for recovery training. At matched bytes, the compressor's factorization preserves the fine-tune direction better than random initialization—evidenced by the distilled LoRA adapter exceeding the full fine-tune (gap closed 1.362) while the pure patch does not.
## Round 1 answer: Glimmer (meta/muse-glimmer-30b, via Flash OmniRoute)

(served model meta/muse-glimmer-30b; usage {'prompt_tokens': 3490, 'completion_tokens': 1433, 'total_tokens': 4923, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}})

**Q1. RECOVERY TUNING**

Design is sound as a test, but uninterpretable for the headline claim you want.

Prediction for the re-quantized headline row: gap closed 0.28 to 0.38, first-token ~0.02-0.04. The fp16 diagnostic will be better, maybe 0.55-0.80 gap closed, because 101 steps from a good warm start beats random for 101 steps. Re-quantization will kill most of that gain. The compressor is 1-bit signs + low-rank factors at fixed per-matrix ranks. Training in fp32 then projecting back through a non-differentiable quantizer is classic post-training quantization error. You are measuring initialization + 101 steps of KL, not initialization + quantization.

What would change my mind: re-quantized gap closed ≥0.60 with first-token ≥0.10, i.e., within striking distance of the LoRA adapter at matched bytes, or a clear monotonic improvement over a random-init control run with identical 101-step budget. 

Patch as initialization is not a new contribution. It is recovery fine-tuning / quantization-aware warm start. The novelty would be if a data-free compressed delta is a better initializer than random for a KL distillation objective. That is plausible but not proven here because you have no random-init baseline at 101 steps, no QAT, and you force a hard re-quantization with no checkpoint selection. 

Design flaw that makes result uninterpretable: the re-quantization step is confounded with training gain. You must either report pre-quant fp16 as primary, or do quantization-aware training / straight-through estimator during those 101 steps. As frozen, a null or negative re-quantized result tells us nothing about initialization value, only that your quantizer is lossy.

**Q2. THE DOLLARS CLAIM**

Framing is partially honest but incomplete.

Who benefits in dollars: distributors who push many variants to edge devices. 19 MB vs 988 MB per update is real bandwidth and storage savings, and zero conversion cost is real for the pure patch. A shared 0.5B base + many 19 MB patches is cheaper than many full copies.

Who does not benefit: practitioners who care about quality per byte. At matched bytes, a trained rank-17 LoRA distilled from the full fine-tune beats the patch 1.362 vs 0.232 gap closed, ties first-token accuracy, and costs only 1,500 teacher generations + 8h CPU. Once you add recovery tuning you lose the zero-cost story and still trail LoRA.

Strongest counterargument: you are selling distribution savings while conceding quality goes to training. A skeptical judge will ask why not just ship a 18.7 MB LoRA adapter at the same byte budget with strictly better quality, and if you need a warm start, why not train LoRA from random for 101 steps? The zero-conversion-cost advantage evaporates the moment you add any training.

**Q3. POSITIONING**

I would sign: Fraction Compressor is a data-free, deterministic compression of a full fine-tune delta into a 19 MB 1-bit factored patch that recovers ~23% of the fine-tune logprob gain with zero training cost. It is a cheap distribution and warm-start artifact, not a quality-competitive alternative to trained adapters at matched bytes.
## Round 1 answer: Grok (grok-4.7, via Flash OmniRoute)

(served model grok-4.7; usage {'prompt_tokens': 4506, 'completion_tokens': 3685, 'total_tokens': 8191, 'prompt_tokens_details': {'cached_tokens': 1152}, 'completion_tokens_details': {'reasoning_tokens': 2781}})

**Q1. Recovery tuning**

The design is only half sound. Freezing the base, starting at the shipped U/V, banning checkpoint shopping, forcing the compressor’s own 1-bit quantizer, and scoring only the re-quantized 19,358,176 B artifact are the right constraints. The budget is honest about being small.

I predict the headline re-quantized row lands at **gap closed 0.18–0.38** (point ~0.27), i.e. noise around today’s 0.232, not a new regime. The fp16 diagnostic can look better, roughly **0.35–0.65**, and re-quantization will eat most of that. 101 steps at 2e-5 barely moves 145 factors, and the 1-bit lattice is why the patch only held 0.232 in the first place. First-token accuracy stays near the floor (≤ ~0.05), not the full fine-tune’s 0.167.

What would change my mind: re-quantized gap closed **≥ 0.55**, or first-token accuracy back to ~0.15, after the same quantizer. That would mean the factored manifold can hold a distilled solution and we were only failing to find the point.

“Patch as initialization” is **not a new method**. It is recovery fine-tuning / warm-start of a structured factorization, adjacent to quantize-then-tune. The only claim worth making is empirical: this data-free point beats a matched init under this budget *after* re-quantization.

**Fix before the run:** there is no control in the *same* U/V parameterization, same 101 steps, same 2e-5, same re-quantizer, from random or zero factors. Without it, any gain is “short KL on the factors helped,” not “the patch init helped,” and the cost-cutting hope is uninterpretable. One seed is weak but can be labeled preliminary; the missing control cannot. Train-then-quantize (no straight-through) is acceptable only because the fp16 row is already demoted to a diagnostic.

**Q2. Dollars**

(a)–(c) are real mechanisms and incomplete as a value claim. Quality is the price, and at matched bytes it is a bad price.

Who is paid: someone who **already has** base and full fine-tune weights, has **no** prompt corpus and no teacher budget, and will ship a behavior that closes ~23% of the logprob gap while **hurting** first-token accuracy (0.010 vs base 0.031). Bandwidth is the cash. 988 MB → 19 MB is ~50×. At 10k recipients and ~$0.09/GB egress, one push is on the order of **~$850 vs ~$15**. That matters for frequent fleet updates; it is petty for a single lab checkpoint. Storage of one base plus many patches beats full copies the same way LoRA already does.

Who is not: anyone who can spend the 1,500 teacher generations and ~8 h. They get gap closed 1.36 at **fewer** bytes. Recovery tuning does not create a new customer: it spends the distillation set, so the zero-query advantage is gone, and you still needed the full fine-tune to build the patch. You saved optimizer steps, not the expensive part.

Strongest judge line: you are selling a nonstandard adapter that loses to PEFT LoRA wherever training is allowed, and that is worse than the base on the metric users notice, in the only regime where the compressor is uniquely cheap. Dollars saved on egress can be negative if recipients roll back a regression.

**Q3. Positioning**

I would sign this: Fraction Compressor is a deterministic, zero-query coder that turns a full delta into a 19 MB patch in minutes and recovers about a quarter of the fine-tune’s target-logprob gap — a distribution format under an explicit quality ceiling, not a substitute for distillation. Matched-byte LoRA remains the quality winner at higher data and time cost; until a same-budget init control and the out-of-style probe report, do not claim that patch initialization cuts training cost or that either artifact generalizes past this author’s style buckets.
## Round 1: Claude and GPT-OSS

Claude: no answer (see Record notes). GPT-OSS: no answer, HTTP 410 model_shutdown on both attempts (see Record notes).

## Round 2 briefing (summary of what was sent)

Each answering panelist received the five Round 1 answers verbatim, the prediction table (Spark 0.20 to 0.35, Gemini 0.45 to 0.65, Nemotron 0.35 to 0.55, Glimmer 0.28 to 0.38, Grok 0.18 to 0.38), and four required responses: (1) endorse Demand A (matched-budget random-init control in the same U/V parameterization) as a must-fix, yes or no; (2) on Demand B, pick one of logging the validation trajectory, scoring intermediate re-quantized checkpoints, or best-checkpoint selection, with a one-line reason; (3) state any change of mind or say "no change" explicitly; (4) a final Q3 positioning statement, adopting or amending another panelist's draft allowed. Word limit about 400.

## Round 2 answer: Muse Spark 1.3 (Meta Model API)

(served model muse-spark-1.3; usage {'completion_tokens': 2231, 'prompt_tokens': 4408, 'total_tokens': 6639, 'completion_tokens_details': {'reasoning_tokens': 1708}, 'prompt_tokens_details': {'cached_tokens': 0}})

CHANGED
One refinement, no core reversal: after the Grok/Glimmer exchange I now explicitly reject Glimmer's QAT / fp16-as-primary fix. Grok is right: train-then-quantize is interpretable *if* fp16 stays a labelled diagnostic and only the 19,358,176 B re-quantized row is headline.

FINAL Q1
(1) Demand A: **Yes** - must-fix before run. Matched-budget control in SAME U/V, same 101 steps, same lr 2e-5, same 1,350 prompts, same re-quantizer from random/zero. Without it "patch holds answer" vs "101 steps helps from anywhere" are confounded.
(2) Demand B: **Logging the validation trajectory is enough.** Best-checkpoint selection must not replace the frozen step-101 rule because it reintroduces checkpoint-shopping and moves the goalposts.
Prediction reaffirmed: re-quantized headline **0.20-0.35 centered on 0.232**, fp16 diagnostic 0.5-0.8, first-token stays low. 808 samples at 2e-5 then forced through the project's own 1-bit quantizer will not survive projection. What changes my mind: re-quantized >=0.6 or patch-init beats matched control by >=0.3 at identical bytes.

FINAL Q2
Directionally honest mechanisms, misleading as value. Who is paid: distributor pushing many variants over metered egress: ~969 MB saved ~$0.087/recipient/push, ~$870/10k pushes; one base + many 19MB patches beats full copies. Who is not: anyone buying quality-per-byte or total cost including errors. At matched ~19MB distilled LoRA 1.362 beats patch 0.232 and ties full fine-tune on first-token, for 1,500 teacher gens + ~8h CPU. Once you add recovery tuning you spend the distillation set and lose zero-query purity but still needed the full fine-tune to make the patch. No dollar case for quality-sensitive users until gain survives re-quant.

FINAL Q3
Amending Grok's draft, which I adopt: Fraction Compressor is a deterministic, zero-query coder turning a full delta into a 19MB 1-bit patch in minutes for ~23% of the logprob gap - a distribution format with an explicit quality ceiling, not a substitute for distillation at matched bytes.

## Round 2 answer: Gemini (gemini-3.5-flash-lite)

(served model gemini-3.5-flash-lite; usage {'prompt_tokens': 4804, 'completion_tokens': 396, 'total_tokens': 5200})

**CHANGED / FINAL Q1 / FINAL Q2 / FINAL Q3**

*   **CHANGED:** I have changed my mind on the urgency of Demand A. Across Round 1, Spark, Glimmer, and Grok all nailed the missing control: without a random-init baseline in the *exact same* U/V factorization, we cannot isolate whether 101 steps of short KL helped because the patch held structural info or simply because brief tuning on factors helps anything. That control must be added immediately.
*   **FINAL Q1:** Endorse Demand A? **Yes.** On Demand B: **log validation trajectory every 10 steps, do not checkpoint-select for the headline.** Why: We need intermediate visibility to interpret whether step 101 is an overfit cliff, but the frozen rule "step 101 is the final result" must stand to prevent p-hacking the headline against the post-quantizer.
*   **FINAL Q2:** The dollars value claim holds only for bulk fleet distributors shipping to bandwidth-metered endpoints where base+patch beats 100 full fp16 copies. For quality-sensitive users, it fails: once you spend CPU/data on recovery tuning, you have sacrificed the zero-query advantage, and a matched-byte distilled LoRA adapter (gap closed 1.36) leaves the patch behind. Bandwidth savings are real; quality regressions are too expensive to offset them.
*   **FINAL Q3:** "Fraction Compressor delivers a deterministic, zero-query, sub-20MB 1-bit factored delta patch that recovers ~23% of the fine-tune gap; recovery tuning is a pilot test of whether that patch can serve as a high-efficiency distillation init, but matched-byte LoRA remains the quality-per-byte winner whenever training budgets are allowed." (Amends Grok/Muse Spark drafts).
## Round 2 answer: NVIDIA Nemotron 3 Ultra (via Flash OmniRoute)

(served model nvidia/nemotron-3-ultra-550b-a55b; usage {'prompt_tokens': 7269, 'completion_tokens': 2381, 'total_tokens': 9650})

CHANGED / FINAL Q1 / FINAL Q2 / FINAL Q3

**Demand A: YES, must-fix before run.** Four of five panelists (Spark, Glimmer, Grok, Nemotron implicitly) converge: without a matched-budget random/zero-init control in the identical U/V parameterization, same 101 steps, same LR, same re-quantizer, any gain is confounded with "brief KL training helps from anywhere." This is a one-line script addition, no new teacher cost, and the only way to attribute improvement to the patch initialization itself.

**Demand B: Logging the validation trajectory is enough.** The frozen rule (step 101 = headline) protects against p-hacking; the pre-registered validation KL logs at steps 0/25/50/75/101 already give the trajectory needed to interpret the re-quantized result. Intermediate re-quantized scoring invites cherry-picking; best-checkpoint selection replaces the protocol. The fp16 diagnostic row exists precisely for the "what training could have yielded" view. *One line: Frozen headline + logged trajectory + fp16 diagnostic = interpretable without compromising the pre-registered rule.*

**Changed:** Shifted toward the pessimistic cluster (Spark/Glimmer/Grok) on Q1 — re-quantized gap closed likely 0.20–0.38, not 0.45+. Convinced Demand A is non-negotiable (was "strongly recommended"). On Demand B, Grok's argument that train-then-quantize is acceptable *because* fp16 is a labeled diagnostic flipped me from Nemotron's "report best checkpoint" to frozen-rule-plus-trajectory.

**FINAL Q3:** Adopting Glimmer's draft with one amendment: "Fraction Compressor is a data-free, deterministic compression of a full fine-tune delta into a 19 MB 1-bit factored patch that recovers ~23% of the fine-tune logprob gain with zero training cost. It is a cheap distribution and warm-start artifact, not a quality-competitive alternative to trained adapters at matched bytes; whether patch initialization retains training gain through re-quantization remains an open pilot pending the matched-budget control."
## Round 2 answer: Glimmer (meta/muse-glimmer-30b, via Flash OmniRoute)

(served model meta/muse-glimmer-30b; usage {'prompt_tokens': 6677, 'completion_tokens': 2211, 'total_tokens': 8888, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 6592}})

CHANGED
No change on core prediction and dollars framing. I now accept validation KL logging as sufficient diagnostic for Demand B rather than demanding QAT or best-checkpoint selection.

FINAL Q1
Demand A: yes, must-fix before run. A matched-budget control with random or zero init in the same U/V parameterization, same 101 steps, same lr, same 1,350 prompts and same re-quantizer is required. Without it “101 steps helps from anywhere” is fully confounded with “patch holds part of the answer”.

Prediction unchanged: re-quantized headline gap closed 0.20 to 0.35, centered on 0.232, i.e. no real gain. Unquantized fp16 diagnostic 0.5-0.8. 101 steps x batch 8 = 808 samples ~0.6 epoch at lr 2e-5 from an fp32 start, then forced through the project’s own 1-bit per-matrix quantizer. Small updates do not survive 1-bit post-quantization.

Demand B: logging the validation trajectory is enough. Headline stays frozen at step 101 with no checkpoint selection to avoid moving goalposts. The logged KL at steps 0,25,50,75,101 lets us interpret an overfit snapshot without cherry-picking the headline. Intermediate re-quantized scoring would change the frozen rule; best-checkpoint selection would do the same.

FINAL Q2
Directionally honest, magnitudes omitted and therefore misleading as a value claim. Who benefits concretely: a distributor pushing many behavior variants to many recipients on metered egress, or versioning many variants. ~969 MB saved per transfer ≈ $0.087/recipient/update at $0.09/GB, ~$870 per 10k pushes. Storage peanuts.

Who does not benefit: anyone optimizing quality-per-byte. At matched ~19 MB, distilled LoRA gap 1.362 beats patch gap 0.232, ties full fine-tune on first-token. Storage and bandwidth are cheap; wrong answers are expensive. Zero-conversion-cost is true and the only unique property, but you get what you pay for: ~23% of the gap.

FINAL Q3
Adopting Glimmer with amendment: Fraction Compressor is a data-free, deterministic compression of a full fine-tune delta into a 19 MB 1-bit factored patch that recovers ~23% of the fine-tune logprob gain with zero training cost. It is a cheap distribution and warm-start artifact, not a quality-competitive alternative to trained adapters at matched bytes, and whether patch-initialization retains training gain through re-quantization remains an open pilot pending the matched-budget control.
## Round 2 answer: Grok (grok-4.7, via Flash OmniRoute)

(served model grok-4.7; usage {'prompt_tokens': 7785, 'completion_tokens': 4141, 'total_tokens': 11926, 'prompt_tokens_details': {'cached_tokens': 7680}, 'completion_tokens_details': {'reasoning_tokens': 3444}})

CHANGED
One design point only. I still reject best-checkpoint selection, but Gemini and Nemotron are right that the logged validation KL cannot interpret a 1-bit headline: fp32 loss can fall while the quantizer projects the factors back onto the same lattice. Intermediate checkpoints at the already-logged steps must be re-quantized and scored as diagnostics. The headline stays step 101.

No change on the band (0.18–0.38, point ~0.27), on Demand A, on train-then-quantize, on “not a new method,” or on dollars. I do not drift toward Gemini’s 0.45–0.65; that assumes the gain is smoothed quantization noise, which an uncontrolled run cannot show. I reject Nemotron’s Q3: a LoRA that overshoots the full fine-tune is not evidence this U/V patch beats random init.

FINAL Q1
(1) Yes. Demand A is a must-fix before the run. Same U/V parameterization, random or zero init, 101 steps, same learning rate, same 1,350 prompts, same re-quantizer. A gain from both inits is “short KL helped.” Only a separation — I adopt Spark’s ≥0.3 gap — attributes anything to the shipped patch.

(2) Score intermediate re-quantized checkpoints; do not replace the frozen rule. Validation KL is not the artifact we ship, so it cannot tell a dead 1-bit update from a late peak; picking the best of those scores spends extra looks and breaks the pre-registered 10% budget.

Prediction unchanged: re-quantized gap closed 0.18–0.38. The fp16 row may print 0.35–0.65 and stays a labelled diagnostic. Mind changes only if the re-quantized row is ≥0.55, or first-token returns to ~0.15, and the matched control loses by a clear margin. Patch-as-init remains recovery fine-tuning. Glimmer’s QAT demand would change the product; a null through this quantizer is a result about the format we ship.

FINAL Q2
No change. The savings are real only for someone who already holds both models, has no teacher budget, and will ship a behavior that closes ~23% of the logprob gap while hurting first-token accuracy versus base. At ~$0.09/GB, 10k recipients is on the order of ~$850 versus ~$15 per push. Anyone who can spend 1,500 generations and ~8 h gets gap closed 1.36 at fewer bytes. Recovery tuning spends that corpus, so it creates no new customer and is not a dollar case for quality-sensitive users until a re-quantized gain survives Demand A.

FINAL Q3
Amending my Round 1 draft with Spark’s pilot clause: Fraction Compressor is a deterministic, zero-query coder that turns a full delta into a 19 MB patch and recovers about a quarter of the fine-tune’s target-logprob gap — a distribution format under an explicit quality ceiling, not a substitute for distillation. Whether that patch, as initialization, retains any gain through the same 1-bit quantizer beyond a matched-budget control is an open pilot; do not claim it cuts training cost until that control reports.