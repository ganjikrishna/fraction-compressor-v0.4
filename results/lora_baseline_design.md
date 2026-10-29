# Matched-byte LoRA / adapter-distillation baseline: design

Date: Wed Oct 28, 2026. Status: design frozen before any training; local only, nothing pushed.
Origin: results/nemotron_review.md (NVIDIA Nemotron 3 Ultra) flagged that the project has
"no comparison to LoRA or adapter distillation at matched bytes". Vinay approved running it
("lets do if we have time"). Design pressure-tested with Gemini and Muse Spark before
building (Vinay's standing builds rule); both calls logged in results/api_usage_log.jsonl
(purposes lora_baseline_design_consult_spark / lora_baseline_design_consult_gemini).

## The question

On the Qwen2.5-0.5B base/Instruct pair, at the same byte budget as the headline factored
patches (uniform rank-32: 19,434,496 B; searched lite recipe: 19,358,176 B), how much of the
base-to-full gap does a LoRA adapter close on the same combined 96 held-out questions with
the same scoring? Reference scores (results/alien_sweep_heldout96.json): base mean target
logprob -11.150, full fine-tune -8.542; uniform factored -11.096 (2.1% gap closed), lite
-10.545 (23.2% gap closed). The original Instruct training data is unavailable, so the
adapter is obtained by distillation from the full fine-tuned model itself (the teacher).

## Consult verdicts (summary)

Both consultants, independently:
- Placement option 1 (all seven block linears, uniform rank, no embedding) is the canonical
  "LoRA at this budget" baseline; options 2 (MLP-only) and 3 (topped-up ranks) read as
  tuned. Spark additionally noted option 3 (19,421,184 B) exceeds the lite budget anyway.
- The objective should be soft KL divergence, temperature 1.0, forward KL (teacher||student)
  on answer positions. Hard cross-entropy on teacher greedy generations trains to the
  teacher's mode and mismatches a benchmark scored by log-probability; it would read as a
  strawman baseline.
- The fixed 360-prompt / 3-epoch sketch is starved: more prompts, train toward a plateau
  with early stopping on a held-out distillation validation KL, never on the eval probes.
- The information asymmetry must be disclosed (wording adopted below).
Spark further demanded: multiple seeds with spread reported; price fp16 AND score the
fp16-cast values, with the cast sensitivity shown; a blocks-only vs blocks-only comparison
(the factored rows keep a cheap rank-32 embedding patch the LoRA cannot afford); a manual
audit on top of the Jaccard novelty filter. Gemini's numbers were smaller (720 prompts,
5 epochs); Spark's larger (2k-5k prompts, 5-10 epochs). The frozen design below sits
between them, sized by Flash CPU wall-clock (see budget note).

## Frozen design

Adapter:
- Standard LoRA, delta_W = B @ A on all seven block linears (attn q/k/v/o_proj, mlp
  gate/up/down_proj) in all 24 blocks, uniform rank 17, no embedding adapter.
- Byte price (fp16, 2 bytes/param, no other storage terms): one rank across all blocks
  costs 1,099,776 B, so rank 17 = 9,348,096 params = 18,696,192 B. That is under both
  factored budgets (by 738,304 B vs uniform, 661,984 B vs lite); rank 18 (19,795,968 B)
  would exceed both. The unspent remainder is disclosed as a small handicap against the
  adapter, not hidden.
- Training parameterization: delta_W = (alpha/r) * B @ A with alpha = 32, B zero-init,
  A ~ N(0, 0.02^2); the scale is folded into B at export, so the shipped adapter is a
  plain B @ A. Scoring uses the fp16-rounded A/B (rounded to fp16, upcast to fp32 for the
  NumPy forward): the file that is priced is the file that is scored. An fp32-unrounded
  scoring pass is run as a sensitivity check.

Distillation data:
- 1,500 fresh prompts written by Muse Spark (500 per bucket: knowledge, instruction,
  math), same shapes as the eval probes (knowledge = short factual sentence fragment;
  instruction = short command / format-constrained request; math = short word problem
  ending "Answer with just the number."). Prompts only; all supervision comes from the
  teacher.
- Hygiene: every prompt novelty-checked against all 96 eval prompts AND the 24 Signet
  prompts (exact normalized match, or token-set Jaccard >= 0.7, rejected; one logged
  regeneration retry per batch, house pattern). A manual audit of a random 10% sample is
  recorded. Accepted prompts also exclude each other (no near-duplicates inside the set).
- Split (fixed seed shuffle): 1,350 train (450/bucket), 150 validation (50/bucket). The
  validation split is used ONLY for early stopping on distillation KL. The 96 eval probes
  are never used for training, stopping, or selection of anything.
- Teacher answers: greedy generations from the Instruct weights (max 48 tokens, stop at
  <|im_end|>), produced by the PyTorch forward port after that port is validated against
  the NumPy scorer (below). Loss positions are the teacher-answer tokens of
  (chat-formatted prompt + teacher answer).

Objective and training:
- Soft KL, forward KL teacher||student, temperature 1.0, at answer positions only,
  teacher run online (teacher-forced on its own generations).
- PyTorch on Flash (voice-clone venv, torch 2.6.0), base weights frozen in fp32. AdamW
  (betas 0.9/0.999, weight decay 0), lr 2e-4 with cosine decay, batch 8, up to 6 epochs,
  validation KL every 100 steps, early stop with patience 2 checks, best-val checkpoint
  kept. Dropout 0.
- Three seeds (20261028, 20261029, 20261030). Headline adapter score is the mean over
  seeds; per-seed scores and the standard deviation are reported. Hyperparameters are
  fixed here, in advance; no eval-guided selection.

Forward-port validation (before any training):
- The PyTorch port of the Qwen2.5 forward must reproduce the NumPy scorer: base-weights
  per-item logprobs on 12 held-out eval items compared against the stored eval_base.json
  values (numerical equivalence check only, the same kind the pipeline's own assemble
  step runs against its references; no training signal flows from it).

Scoring (identical machinery to every other row):
- The house NumPy forward and metrics (mean target logprob, first-token accuracy,
  per-bucket), combined 96, via alien_sweep_stage2.score_items.
- Primary application is the factored apply: (X @ A.T) @ B.T added at each targeted
  linear, in a hooked copy of the forward. Verification passes:
  (a) dense reference: weights + B@A through the UNMODIFIED stage-2 forward, all 96
      items, seed 1; per-item logprobs must match the hooked path.
  (b) zero adapter through the hooked forward must reproduce the stored base per-item
      logprobs on all 96 items.
- Supplementary rows answering the embedding asymmetry head-on: the uniform and lite
  factored configs re-scored with their embedding delta dropped (blocks-only), priced
  blocks-only (uniform 19,434,496 - 1,272,832 = 18,161,664 B; lite priced from its own
  rank map). And a precision sensitivity: uniform and lite re-scored with their V factors
  rounded through fp16, the same cast the adapter is scored under.

## Disclosure wording (adopted from the Spark consult, adapted)

Parity here is storage-only, not compute or data. The compressor reads the full white-box
delta weights with zero gradient steps and zero queries, deterministically. The adapter
never sees the delta weights; it is trained by gradient descent on the teacher's output
distributions over 1,500 fresh prompts. Neither method sees the original Instruct training
data, and neither sees the eval prompts or their reference answers. The comparison reads:
"at about 19.4 MB, post-hoc factored conversion of the delta vs query-distilled LoRA."

## Budget note (why not Spark's full prescription)

Spark's 2k-5k prompts x 5-10 epochs x 3 seeds with an online teacher prices out at
roughly 8-14 hours of Flash CPU; the frozen design (1,500 prompts, up to 6 epochs with
early stop, 3 seeds, ~10 scoring passes at ~5 min each) prices at roughly 4-6 hours,
inside the one-day wall-clock box Vinay's approval carries. The starvation failure mode
Spark and Gemini both flagged is addressed by training to a validation plateau instead
of a fixed 135 steps.

## Files

- Prompts: examples/lora_baseline_gen.py -> data/distill_prompts.json (gitignored data/),
  generation record at /tmp/lora_distill_gen_record.json (copied into the results JSON).
- Flash pipeline: examples/lora_baseline.py (prep / train / eval subcommands), workdir
  ~/fc-v04-sweep/lora_baseline on Flash.
- Results: results/lora_baseline.json, judging in results/lora_baseline_judging.md/.json.
