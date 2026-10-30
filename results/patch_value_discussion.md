# Panel discussion: is the patch useful in the real world? (internal, local only)

Provenance: Vinay asked on Thu Oct 29, 2026, after the recovery tuning pilot landed: the patch start gave no advantage in recovery tuning (patch-init 1.136 vs random-init 1.348, one seed), so if the patch does not even help as a training starting point, how is the patch useful in the real world? Ember's answer (the positioning under test, quoted verbatim in the Round 1 pack below) was put to the panel. Two rounds: Round 1 independent positions, Round 2 a digest with two corrections (one arithmetic, one sign) and a merged wording put to a sign-off. Order and routes: Muse Spark 1.3 first via the Meta Model API; Gemini gemini-3.5-flash-lite via the connector helper; Nemotron, Glimmer, Grok, and Claude via Flash's local OmniRoute gateway (http://localhost:20128/v1, temperature 0.3, max_tokens 8000). Claude was called ONLY on the verified antigravity/claude-opus-4-6-thinking route and answered both rounds this time. GPT-OSS was skipped per standing instruction (provider 410 model_shutdown since Oct 28). Nothing pushed, nothing posted.

## Plain-words summary

**Consensus (all six panelists):** Ember's core separation is right. The patch is not a cheaper way to learn, and after the recovery pilot it is not a warm start either: patch-init trailed random-init. The trained adapter wins wherever training is available, and the project's own numbers say so.

**The one real fight was over the slogan.** Five of six panelists (Spark, Gemini, Nemotron, Glimmer, Grok) say DROP the phrase "ship what was already learned": at gap closed 0.232 with first-token accuracy 0.010, below the base model's 0.031, the phrase claims a fidelity the artifact does not have. Claude alone says QUALIFY it instead of dropping it ("ship a lossy approximation of what was already learned"). Either way, the panel is unanimous that public wording must put the word "lossy" and the first-token regression next to the size claim, not in a footnote.

**Claude's extra point, tested in Round 2:** the recovery runs show the factored FORMAT can carry trained quality at identical bytes, so the bottleneck is the training-free conversion, not the format. Round 2 verdict, unanimous including Claude: that is a value of the format, not of the shipped patch artifact, and it must not be credited to the patch in project wording. Grok adds the sharpest caveat: the recovery numbers do not even show the patch carrying trained quality; they show trained factors re-quantized, starting from an init that lost.

**Sign-off on the merged wording (Round 2):** Spark and Nemotron sign as written. Gemini, Glimmer, and Claude sign with amendments that all point the same way: state 23.2% (0.605 nats) explicitly and name the degraded first-token accuracy inside the acceptability clause. Grok does not sign and offers a stricter version that demotes hot-swap and determinism ("real but not unique and do not offset the fidelity loss") and narrows the niche to weights-only deltas with no data trail and no teacher bill.

**Recommended final wording (merged text plus the convergent amendments; Grok's stricter demotion noted as dissent):**

> "The patch is a lossy, training-free distribution format for a fine-tune delta: at 19,358,176 B it closes 23.2% of the gap (0.605 of 2.607 nats), with first-token accuracy 0.010 (below base 0.031), and it is not a training aid (patch-init trailed random-init by 0.213, one seed). It is useful only where training cannot happen and ~23% gap closure with degraded first-token accuracy is acceptable: weights-only fine-tunes, many variants against one base, ~0.1 s hot-swap, deterministic checkable bytes, no data trail or teacher bill. Where training is available, a matched-byte distilled LoRA wins (gap closed 1.362 ± 0.033, first-token 0.167-0.177)."

**Final one-line verdicts:**
- Spark: "Ember's learn/ship split is right but the slogan overclaims — it's a niche zero-data lossy distributor, not general learned-quality shipping."
- Gemini: the patch "is a lossy distribution format for static fine-tunes, useful strictly where zero data trail outweighs its heavy fidelity penalty."
- Nemotron: "Ember correctly separates deployment from training but understates the artifact's regression vs. base model."
- Glimmer: "Ember's positioning is correct as a niche, lossy, training-free distribution format with no learning benefit and a first-token regression."
- Grok: "Ember is right that the patch is not learning and not a warm start, and wrong to imply it faithfully ships the fine-tune."
- Claude: "Structurally correct on learn-vs-ship separation; overstated on fidelity and verifiability salience; the patch is a niche deployment format, not a capability showcase."

**Sharpest dissenting lines:**
- Nemotron: "This is not 'shipping the learned behavior'; it is shipping the *skeleton* of the behavior."
- Grok: "when training cannot happen, the patch still does not carry the learned behavior, and on first-token it is worse than shipping the base unchanged."
- Spark: verifiability is "true and vacuous at 0.232 and 0.010. Verifiably close in weights is not close in behavior."

## Record notes and failures

- ARITHMETIC INCIDENT: four Round 1 answers (Nemotron, Glimmer, Grok, Claude) wrote "0.232 of the 2.607 gap = 8.9%." That double-divides: gap closed 0.232 is already the fraction (the patch's mean logprob is -10.545, i.e. 0.605 of 2.607 nats = 23.2%). The correction was put to the panel in Round 2 and accepted by every panelist. Any Round 1 percentage built on 8.9% or "~10%" (including Nemotron's "map that gets you 10% of the way") should be read as 23.2%.
- Gemini's Round 2 amendment repeats the same error in the other artifact: it renders the LoRA result as "gap closed 52.2% ± 1.3%." That is 1.362 divided by 2.607 again. The correct form is the merged wording's: gap closed 1.362 ± 0.033 (136.2% of the gap). Do not use Gemini's percentage form.
- Claude's Round 1 Q1 paragraph flipped the recovery sign, calling the 0.213 "a modest advantage" for patch-init; its own Q2 stated the result correctly. The sign correction was put to it in Round 2 and its Round 2 answers use the correct sign.
- Nemotron's first Round 1 call completed (usage 804 prompt / 2,056 completion / 2,860 total) but its answer file was lost when Flash's /tmp was wiped mid-run (the same wipe recorded during the out-of-style run). Nemotron was re-called once from a home-directory workdir; the second answer (804 / 2,481 / 3,285) is the Round 1 answer of record below.
- Glimmer's first Round 1 attempt failed with the same /tmp wipe (no output file, exit 1). The retry from ~/patch_value_panel/ succeeded and is the answer of record.
- Two SSH attempts for the Grok and Claude Round 2 calls failed with a proxy broken pipe (tunnel outage); no API calls were made on those attempts. The third attempt succeeded.
- The push agent was still running in parallel at the end of this run, so the four hosted API entries for this discussion were NOT appended to results/api_usage_log.jsonl (to avoid racing its copy of that file). They are recorded in the Compute section below and should be appended after the push lands.

## Round 1 question pack (sent verbatim to all panelists)

You are one panelist in an internal discussion panel for the Fraction Compressor project. This is a debate, not a verdict form. Answer against the exact numbers below, not in generalities. Structure your reply as Q1 / Q2 / Q3 and keep it to about 700 words.

THE QUESTION FROM VINAY: The patch start gave no advantage in recovery tuning (patch-init 1.136 vs random-init 1.348, one seed). If the patch does not even help as a training starting point, how is the patch useful in the real world?

EMBER'S POSITION, THE CLAIM UNDER TEST (verbatim): "The patch is not a cheaper way to learn; it is a cheaper way to ship what was already learned. It earns its place where training cannot happen: fine-tunes shared as weights only with no training data available; many variants stored and shipped against one base (19 MB vs ~1 GB each); live hot-swapping of behavior (~0.1 s); exact verifiability, since the patch is a deterministic function of the two models; and no data trail or teacher bill. Where quality matters most and training is available, a trained adapter wins, and our own numbers say so."

EVIDENCE PACK (exact numbers):
- Qwen2.5-0.5B pair, combined 96: base -11.150, full delta -8.543 (987,922,432 B fp16). Factored lite patch 19,358,176 B: gap closed 0.232, first-token acc 0.010 (base 0.031, full 0.167).
- LoRA distilled adapter 18,696,192 B: gap closed 1.362 ± 0.033 (3 seeds), first-token acc 0.167-0.177. Cost: 1,500 Spark teacher generations (680,896 hosted tokens) + ~8 h training on a CPU-only home machine. Out-of-style control (Gemini-authored prompts, different style): gap closed 0.620, first-token acc 0.042; style match more than doubles the score.
- Recovery pilot (one seed, 101 steps, in-style data): untouched patch 0.232; patch-init trained then re-quantized to identical bytes 1.136; random-init control 1.348. Patch advantage -0.213. Panel's own earlier predictions were 0.18-0.38 (cluster) and 0.45-0.65 (Gemini); both runs beat every prediction.
- Skill limit: on a first-token-gated extraction skill, the rank-32 patch transfers 1/10 clean vs the full fine-tune's 8/1/1; force-start control shows most of the skill is latent in the base.
- Hot-swap transcript: patches swap live in 0.104 s and 0.087 s with the base loaded once.

Q1. Is Ember's positioning right, overstated, or missing something? Answer against the numbers.
Q2. Name the strongest real-world case FOR the patch and the strongest case AGAINST it, each in one or two sentences.
Q3. Anything the project should change in how it describes the patch's value (README/submission wording) as a result? Give exact replacement wording if you propose a change.

## Round 1 answer: Muse Spark 1.3 (Meta Model API)

(served model muse-spark-1.3; usage {'completion_tokens': 4720, 'prompt_tokens': 697, 'total_tokens': 5417, 'completion_tokens_details': {'reasoning_tokens': 3557}, 'prompt_tokens_details': {'cached_tokens': 0}})

**Q1. Is Ember right? Mostly right on the pivot, overstated on the payoff.**

Vinay's hit is fatal to one story and not to the other, and Ember is right to separate them. Recovery pilot, one seed, 101 steps in-style: untouched patch 0.232, patch-init then re-quantized to identical bytes 1.136, random-init 1.348. Patch advantage -0.213. Both trained runs beat every panel prediction - cluster 0.18-0.38 and Gemini 0.45-0.65. The patch is not a better starting point. It is a worse starting point than random at same bytes.

That does not logically kill a frozen, zero-training artifact. Initialization tests trainability; deployment tests frozen utility when you cannot train. Ember is right to concede: "not a cheaper way to learn."

Where Ember overstates is "a cheaper way to ship what was already learned." The numbers say shipped very lossily:

19,358,176 B vs 987,922,432 B fp16 is real - ~51x smaller. Base -11.150 to full -8.543, patch closes 0.232. Same-byte LoRA 18,696,192 B closes 1.362 +/- 0.033 over 3 seeds, 5.9x more gap per byte. More damning for "ship": first-token acc patch 0.010 is *below* base 0.031, while full is 0.167 and LoRA is 0.167-0.177. You improved mean log-prob while regressing the most user-visible token.

Skill test says the same: rank-32 patch 1/10 clean vs full 8/1/1, and force-start shows most of that skill was already latent in base. Deterministic function of the two models does not mean behaviorally faithful.

Run down Ember's five:

1. Weights-only, no data: strongest leg, but narrowed by our own control. Out-of-style LoRA on Gemini-authored prompts, different style, still closes 0.620 with acc 0.042 - 2.7x the patch's 0.232. So "training cannot happen" must mean literally zero compute / legal / data access, not just mismatched data. 1,500 Spark generations, 680,896 hosted tokens + ~8h on CPU-only home machine is a low bar to beat you.

2. Many variants 19 MB vs ~1 GB: true storage arithmetic, byte-parity with LoRA, but quality-per-byte loses badly.

3. Hot-swap 0.104s and 0.087s base-loaded-once: transcript proves mechanism, but not unique - LoRA adapters swap too. Advantage is no architecture change, not speed.

4. Exact verifiability: true and vacuous at 0.232 and 0.010. Verifiably close in weights is not close in behavior.

5. No data trail / teacher bill: true, you save 680k tokens + 8h, but you buy 0.232 instead of 1.362, or 0.620 even with wrong data.

Missing: state the first-token regression and that training is shockingly cheap-effective here.

**Q2. Strongest cases.**

FOR: A Hugging Face zoo of 100s of weights-only fine-tunes with no data, no retrain budget and no permission to distill, where you must keep one base and ship 19 MB deterministic deltas that hot-swap in ~0.1s and recover 0.232 where 988 MB each is impossible - better-than-nothing archiving.

AGAINST: Anywhere you can afford 1,500 teacher calls and 8h CPU, same-size 18.7 MB LoRA gives 1.362 vs 0.232 and restores first-token to 0.167-0.177 vs 0.010, and even wrong-style training gives 0.620 - so shipping the patch trades away user-visible quality for zero byte saving.

**Q3. Change the wording - stop saying "ship what was learned."**

That phrase implies fidelity the 0.010 and 1/10 vs 8/1/1 disprove, and invites Vinay's objection. Replace with zero-training snapshot language that quotes the loss.

Proposed exact replacement for README / submission claim:

> "The lite patch is not a cheaper way to learn - patch-init 1.136 vs random-init 1.348 (-0.213 advantage, 101 steps, one seed) - and not a substitute where training is possible: at ~19 MB it closes 0.232 of the -11.150 to -8.543 gap with first-token 0.010 (base 0.031, full 0.167), vs same-size LoRA 1.362 +/- 0.033 with first-token 0.167-0.177 at a cost of 1,500 teacher generations / 680,896 tokens + ~8h CPU, 0.620 even out-of-style. Its value is zero-training deployment only: deterministic 19,358,176 B function of the two models vs 987,922,432 B full delta (~51x), no data / teacher needed, hot-swappable in ~0.1s (0.104s, 0.087s observed), verifiable byte-exact - a lossy snapshot for weights-only, many-variant, no-retrain settings."


## Round 1 answer: Gemini (gemini-3.5-flash-lite)

(served model gemini-3.5-flash-lite; usage {'prompt_tokens': 797, 'completion_tokens': 831, 'total_tokens': 1628})

**Q1. Is Ember's positioning right, overstated, or missing something? Answer against the numbers.**

Ember’s positioning is largely correct, but slightly understated regarding the severity of the performance penalty, and misses a crucial deployment constraint. Ember claims the patch is for shipping, not learning. The recovery pilot numbers strongly back this up: starting from the untouched patch yields a gap-closed score of 0.232, whereas training *from* the patch (patch-init) hits 1.136, and random-init hits 1.348. Ember is right that the patch is a terrible training starting point—the negative patch advantage of -0.213 proves that initializing training with the patch actually underperforms a randomized baseline when optimization is allowed to run. 

However, Ember understates the absolute performance gap of the shipped artifact. Look at the hard numbers: the LoRA distilled adapter achieves a gap-closed of 1.362 and matches full fine-tune first-token accuracy at 0.167–0.177. The factored lite patch achieves a gap-closed of only 0.232 and a first-token accuracy of 0.010. Ember admits "a trained adapter wins," but calling it a mere quality trade-off hides the fact that a 0.010 accuracy is practically inert on first-token-gated skills (transferring only 1/10 clean vs. the full fine-tune's 8/1/1). 

Finally, Ember misses the data-privacy reality check. The LoRA adapter required 1,500 Spark teacher generations and 680,896 hosted tokens. Ember mentions "no teacher bill," but fails to emphasize that avoiding this data trail is the *only* reason to tolerate a patch that performs at 1/7th the level of a LoRA adapter. 

***

**Q2. Name the strongest real-world case FOR the patch and the strongest case AGAINST it, each in one or two sentences.**

**Case FOR:** The strongest case for the patch is its unbeatable deployment profile: it enables live hot-swapping of behavior in ~0.1 seconds and slashes storage requirements from ~1 GB (full model variants) down to 19 MB, all without requiring any training data, teacher queries, or compute infrastructure.

**Case AGAINST:** The strongest case against the patch is its catastrophic performance degradation on precision tasks, reducing first-token accuracy from 0.167 (full fine-tune/LoRA) down to 0.010, rendering it functionally useless for precision-gated extraction skills.

***

**Q3. Anything the project should change in how it describes the patch's value (README/submission wording) as a result? Give exact replacement wording if you propose a change.**

Yes. The README currently leans too close to framing the patch as a generalized alternative. We must explicitly trade away high-precision task execution for zero-data, zero-compute deployment convenience. 

**Existing problematic wording (implied):** Positioned as an efficient parameter-saving alternative for model adaptation.

**Exact replacement wording for the README/submission:**
> "The Fraction Compressor patch is not a training method or a precision fine-tune replacement—where training data and compute are available, a LoRA adapter decisively wins (achieving 1.362 gap-closed vs. the patch's 0.232). Instead, the patch is a zero-data, zero-compute distribution format designed strictly for environments where training cannot happen. It trades high-precision task execution (dropping first-token accuracy from ~0.17 to 0.01) for radical operational efficiency: 19 MB variant storage versus ~1 GB, live hot-swapping in ~0.1 seconds, and exact determinism with zero teacher bills or data trails."

## Round 1 answer: NVIDIA Nemotron 3 Ultra (via Flash OmniRoute)

(served model nvidia/nemotron-3-ultra-550b-a55b; usage {'prompt_tokens': 804, 'completion_tokens': 2481, 'total_tokens': 3285})

**Q1. Positioning Assessment: Strategically Right, Tactically Overstated on "Containment"**

Ember’s framing—"cheaper way to *ship*, not *learn*"—is the only honest reading of the numbers, but the submission wording currently lets "ship what was *learned*" do too much heavy lifting. The patch closes **0.232 / 2.607 = 8.9%** of the loss gap and achieves **0.010 / 0.167 = 6%** of the full fine-tune’s first-token accuracy. On the extraction skill, it transfers **1/10** clean successes versus the full delta’s **8/10**. This is not "shipping the learned behavior"; it is shipping the *skeleton* of the behavior—the rank-32 subspace—while leaving 90%+ of the capability (magnitude, nonlinear interactions, token-level precision) on the cutting-room floor.

The recovery pilot is the smoking gun against the "good initialization" intuition. **Patch-init trained to 1.136 gap closed; random-init hit 1.348.** The patch *hurts* convergence (-0.213 advantage). The panel’s own predictions (0.18–0.65) were crushed by *both* runs, proving the subspace is learnable fast, but the patch’s specific vector orientation is actively misleading for SGD. Ember’s claim of "exact verifiability, since the patch is a deterministic function of the two models" is technically true but practically vacuous: you can perfectly verify a map that gets you 10% of the way to the destination.

The LoRA distillation control is the real benchmark for the 19 MB form factor: **1.362 ± 0.033 gap closed (52% of full delta), 0.167–0.177 first-token acc (100% of full delta)** for 8 CPU-hours and 1,500 teacher calls. If the recipient *has* 8 hours and a CPU, the patch is strictly dominated. The patch’s niche is strictly **zero-compute, zero-data, zero-teacher** environments. Ember’s positioning is right on the *existence* of that niche, but overstated on the *fidelity* of the payload.

**Q2. Strongest Cases**

*   **FOR:** The patch is the *only* artifact that lets a recipient with **only base weights, zero GPU hours, zero training data, and zero teacher access** instantiate a verified structural delta in **19 MB / 0.1 s hot-swap**—enabling fleet-wide variant management (19 MB vs 1 GB) where any training loop is organizationally impossible.
*   **AGAINST:** The patch captures **<10% of the target skill** (0.232 gap, 1/10 extraction) and **actively degrades subsequent fine-tuning** (-0.213 vs random init), making it a **dead-end artifact** the moment the recipient gains 8 CPU-hours and teacher access—at which point a distilled LoRA in the *exact same footprint* delivers 6x the gap closure and full token accuracy.

**Q3. README / Submission Wording Changes**

**Current Implied Claim:** *"The patch is a cheaper way to ship what was already learned... exact verifiability, since the patch is a deterministic function of the two models."*

**Proposed Replacement (Value Proposition Section):**

> **What the Patch Actually Ships**
> The factored patch transmits the **rank-32 principal subspace** of the full fine-tune delta (19 MB vs 988 MB fp16). It is a *structural* artifact, not a *functional* one.
>
> *   **Fidelity:** Recovers **0.232 / 2.607 (8.9%)** of the loss gap and **0.010 / 0.167 (6%)** of first-token accuracy. On compositional skills (first-token gated extraction), it transfers **~10%** of clean successes (1/10 vs 8/10).
> *   **Verifiability:** You can cryptographically verify the patch equals `factorize(full_delta, rank=32)`. You *cannot* verify it reproduces the fine-tune’s behavior—it provably does not.
> *   **Recovery Tuning:** **Do not use as a training initialization.** In a controlled 101-step recovery, patch-init converged to **1.136** gap closed vs **1.348** for random init (**-0.213 disadvantage**). The patch constrains optimization into a suboptimal basin. If you have *any* compute/data (8 CPU-hours + 1.5k teacher tokens), **distill a LoRA instead** (1.362 gap closed, 100% token acc, same 19 MB).
>
> **Use the patch only when:** (1) The recipient has **zero training compute, zero data, zero teacher API**; (2) You need **live hot-swap of variants** (0.1 s) against a single loaded base; (3) You need **deterministic provenance** of the *directional change* without transmitting the full 1 GB delta.

## Round 1 answer: Glimmer (meta/muse-glimmer-30b, via Flash OmniRoute)

(served model meta/muse-glimmer-30b; usage {'prompt_tokens': 745, 'completion_tokens': 3520, 'total_tokens': 4265, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}})

Q1. Ember is right on the learning vs shipping distinction and overstated on how much shipping is worth.

The numbers support the learning claim. A LoRA distilled adapter at 18,696,192 B closes gap 1.362 ± 0.033 with first-token acc 0.167-0.177 vs base 0.031 and full 0.167. The factored lite patch at 19,358,176 B closes gap 0.232 and first-token acc 0.010. Where quality matters and training is available, the trained adapter wins, and the cost is modest: 1,500 Spark teacher generations, 680,896 hosted tokens, ~8 h CPU-only training. Out-of-style control shows the adapter is style sensitive, gap closed 0.620 and first-token acc 0.042 vs in-style 1.362, so style match more than doubles the score, but even out-of-style it beats the patch.

The shipping claim is numerically true but weak. Compression is real: full delta 987,922,432 B fp16 vs patch 19,358,176 B, ~19 MB vs ~1 GB each, and hot-swap is 0.104 s and 0.087 s with base loaded once. Exact verifiability and no data trail or teacher bill also hold.

The problem is fidelity. Gap closed 0.232 on a total gap of base -11.150 to full -8.543 = 2.607 is ~8.9% recovery. First-token accuracy falls from base 0.031 to patch 0.010. On a first-token-gated extraction skill the rank-32 patch transfers 1/10 clean vs full fine-tune 8/1/1, and force-start shows most skill is latent in base. That is not shipping what was learned, it is shipping a low-fidelity approximation.

Vinay’s point is reinforced by recovery. With 101 steps in-style, untouched patch 0.232, patch-init trained then re-quantized to identical bytes 1.136, random-init control 1.348. Patch advantage -0.213. The patch is not even a good initialization. Both runs beat panel predictions 0.18-0.38 cluster and 0.45-0.65 Gemini, but patch-init underperforms random-init. So the patch does not help learn and does not help start learning.

Ember is missing the magnitude of the loss. Verifiability and 0.1 s swaps are only valuable if the shipped artifact is usable. Here it is barely above base and actively harmful on first-token metrics.

Q2. Strongest case FOR the patch: When training data and teacher access are unavailable but you must ship many variants against one base, a 19 MB deterministic patch vs ~1 GB full delta with ~0.1 s hot-swap and no data trail is a cheap archival/distribution format for low-stakes variants.

Strongest case AGAINST the patch: Quality is poor and sometimes negative: gap closed 0.232 vs LoRA 1.362, first-token acc 0.010 vs base 0.031 and full 0.167, skill transfer 1/10 clean, and patch-init recovery 1.136 < random-init 1.348, so you are shipping mostly noise and a bad prior.

Q3. The README/submission wording should be qualified from a shipping benefit to a lossy shipping limitation.

Proposed replacement for the Ember claim:

"The patch is a lossy, training-free shipping format for model deltas, not a learning aid. On Qwen2.5-0.5B combined 96 it compresses a 987,922,432 B fp16 delta to 19,358,176 B but closes only 0.232 of the 2.607 gap and reduces first-token accuracy from base 0.031 to 0.010 vs full 0.167. Patch-init recovery is 1.136 vs random-init 1.348 on 101 steps in-style, i.e. -0.213 advantage. Use only where training is impossible and quality loss is acceptable; where training is available a distilled LoRA adapter wins, gap closed 1.362 ±0.033, first-token acc 0.167-0.177."

That keeps the 19 MB vs ~1 GB, 0.104 s/0.087 s hot-swap and verifiability claims, but ties them to the measured fidelity and the negative initialization result.

## Round 1 answer: Grok (grok-4.7, via Flash OmniRoute)

(served model grok-4.7; usage {'prompt_tokens': 1937, 'completion_tokens': 4739, 'total_tokens': 6676, 'prompt_tokens_details': {'cached_tokens': 1152}, 'completion_tokens_details': {'reasoning_tokens': 3769}})

Q1. Ember is right about the constraint and overstated about what the patch ships.

The no-training half matches the table. The lite patch is 19,358,176 B against a full fp16 delta of 987,922,432 B, and it does not spend the LoRA’s 1,500 Spark generations (680,896 hosted tokens) or ~8 h of CPU training. Live swap is measured, not asserted: 0.104 s and 0.087 s with the base loaded once. Recovery agrees with the retreat from “cheaper way to learn.” After 101 in-style steps and re-quantization to the same byte budget, patch-init closed 1.136 and random-init closed 1.348, advantage −0.213 on one seed. Both runs also beat this panel’s earlier bands (0.18–0.38 and 0.45–0.65), so the jump past 0.232 is the trainer, not structure stored in the patch. “Exact verifiability” is a property of a deterministic map between two weight sets; these numbers do not show that the patched model matches the fine-tune.

“Ship what was already learned” does not. Base −11.150 to full −8.543 is a learned gap of 2.607. The patch closes 0.232 of it, about 9%, and first-token accuracy moves the wrong way: base 0.031, patch 0.010, full 0.167. On the first-token-gated skill the rank-32 patch is 1/10 clean against the full fine-tune’s 8/1/1, and the force-start control says most of that skill is already latent in the base. A LoRA at 18,696,192 B — same shipping class — closes 1.362 ± 0.033 and lands first-token at 0.167–0.177. Style is doing real work for that adapter (out-of-style gap closed 0.620, first-token 0.042, and style match more than doubles the score), but even the degraded LoRA still beats the in-style patch on gap closed (0.620 vs 0.232). Ember is correct that a trained adapter wins when training exists. The missing clause is that when training cannot happen, the patch still does not carry the learned behavior, and on first-token it is worse than shipping the base unchanged.

Q2. For: weights in hand, no data and no teacher, many variants against one resident base — 19 MB instead of ~988 MB each — swapped in ~0.1 s, with bytes that are a deterministic function of the two models and can be checked as bytes.

Against: the behavior actually delivered is a thin and partly negative edit — 0.232 of a 2.607 gap, first-token 0.010 versus the base’s 0.031, skill 1/10 versus 8/1/1 — while a same-size trained adapter closes 1.362 and matches the full fine-tune’s first-token rate, and a style-mismatched adapter (0.620) still outruns the patch.

Q3. Drop any wording that calls the patch compressed learning or a stand-in for the fine-tune. Use this:

“The lite patch is a data-free, deterministic factoring of an existing weight delta, not a training method and not a quality-preserving copy of a fine-tune. On the Qwen2.5-0.5B pair the full fp16 delta is 987,922,432 B and moves the score from −11.150 to −8.543 (gap 2.607). The 19,358,176 B patch closes 0.232 of that gap and drops first-token accuracy from 0.031 (base) to 0.010, versus 0.167 for the full fine-tune. A distilled LoRA at 18,696,192 B, which requires teacher generations and training, closes 1.362 ± 0.033 and matches that first-token rate. Use a patch only when you already have both weight sets, cannot run a teacher, and need small, swappable, checkable bytes (~0.1 s hot-swap; many variants against one base), accepting a small fraction of the behavior change, including regressions versus the base. Where quality matters and training is possible, train the adapter. In a one-seed recovery pilot, patch initialization was worse than random initialization under the same budget (1.136 vs 1.348).”

## Round 1 answer: Claude (antigravity/claude-opus-4-6-thinking, via Flash OmniRoute)

(served model claude-opus-4-6-thinking; usage {'prompt_tokens': 875, 'completion_tokens': 1204, 'total_tokens': 2079})

# Panel Response — Antigravity

## Q1. Is Ember's positioning right, overstated, or missing something?

Ember's positioning is structurally correct and honestly framed, but it undersells one weakness and oversells one strength.

**What's right.** The core claim — "the patch is not a cheaper way to learn; it is a cheaper way to ship what was already learned" — is the only defensible reading of the numbers. A gap-closed of 0.232 versus the LoRA adapter's 1.362 ± 0.033 is not a rounding error; the patch recovers roughly 17% of what the trained adapter recovers at comparable byte budget (19.4 MB vs 18.7 MB). Nobody should position the patch as a quality competitor to training. Ember doesn't, and that's honest. The hot-swap numbers (0.104 s, 0.087 s) are real and verified, and the deterministic-verifiability argument is logically sound — a patch is a pure function of two weight sets, so it carries no data provenance risk. The "many variants against one base" storage argument is arithmetically clean: 19 MB vs ~1 GB per variant is a ~50× compression ratio on the delta.

**What's undersold.** The recovery pilot result actually *helps* the patch story more than Ember acknowledges. Patch-init reached 1.136 versus random-init 1.348 in only 101 steps on one seed — a modest advantage of 0.213, yes, but both runs crushed every prior prediction (the panel predicted 0.18–0.38; Gemini predicted 0.45–0.65). The fact that the patch-init didn't dominate random-init is Vinay's point, and it's fair. But the fact that *re-quantizing* a trained adapter back to the patch's identical byte format still yields 1.136 gap-closed means the patch format is not a bottleneck on quality — the bottleneck is the absence of training. That's a subtle but important distinction Ember should make explicit: the format can carry trained quality; it just can't generate it.

**What's overstated.** "Exact verifiability" is listed as a standalone value prop, but in practice this matters only in regulated or adversarial deployment contexts (model supply-chain auditing, compliance). For most users it's invisible. Listing it alongside hot-swap and storage savings inflates the apparent breadth of the value proposition. It should be mentioned but flagged as niche.

The first-token accuracy numbers are brutal and Ember doesn't flinch from them: patch 0.010 vs full fine-tune 0.167. That's effectively zero skill transfer on the hardest metric. The skill-limit result (1/10 clean extractions vs 8/10 for the full fine-tune) confirms this. Ember's framing absorbs this honestly, but the project should not let "gap closed 0.232" do rhetorical work without the first-token number right beside it.

## Q2. Strongest case FOR and AGAINST

**FOR:** Multi-variant deployment where you ship one 1 GB base and N patches at 19 MB each, with live hot-swap in ~0.1 s and zero training infrastructure at the edge. At N ≥ 5 you're already saving more than 80% of naive storage, and the swap latency makes A/B testing or persona switching practical in real time — no other artifact in the project achieves this.

**AGAINST:** At matched parameter budget the patch recovers 0.232 gap-closed versus the adapter's 1.362, and on the metric that most directly measures learned skill (first-token accuracy) the patch scores 0.010 — statistically indistinguishable from the base's 0.031 and nowhere near the fine-tune's 0.167. Any user who cares about output quality and has access to even modest training resources (8 hours on a CPU, 1,500 teacher samples) should use the adapter; the patch offers no quality advantage even as a warm start (patch-init 1.136 vs random-init 1.348, Δ = 0.213, one seed).

## Q3. Proposed wording changes

**Current implicit framing (README/submission):** The patch is presented alongside the adapter as a peer artifact.

**Proposed replacement (exact wording):**

> **Fraction Patch (19.4 MB, no training required):** A deterministic, factored compression of the full weight delta. Recovers 0.232 of 2.607 log-perplexity gap (9%) with near-zero first-token skill transfer (0.010 vs 0.167). Its value is operational, not qualitative: store many variants against one base at ~50× compression, hot-swap personalities in ~0.1 s, and ship fine-tune deltas without exposing training data or requiring training infrastructure. Where output quality matters, use the trained LoRA adapter (gap closed 1.362 ± 0.033 at comparable size, ~8 h CPU training).

This puts the quality number and the operational number in the same breath, which is the only honest way to present them.

## Round 2 question pack (sent verbatim to all panelists)

ROUND 2 of the Fraction Compressor patch-value panel. You answered Round 1; here is a digest of the panel's Round 1 positions, two corrections to check, and three short questions. Keep your whole reply under about 450 words.

ROUND 1 DIGEST:
- Unanimous: Ember's learn-vs-ship separation is correct; the patch is not a learning aid and not a warm start (recovery pilot: patch-init 1.136 vs random-init 1.348, one seed).
- Spark, Nemotron, Glimmer, Grok: "ship what was already learned" overstates fidelity. The patch is a lossy snapshot / low-fidelity approximation; verifiability is true but worth little at this fidelity; hot-swap is real but not unique (adapters swap too); even a wrong-style LoRA (0.620) beats the patch (0.232). All four propose replacing "ship what was learned" with lossy-format wording that quotes the first-token regression (patch 0.010, below base 0.031).
- Gemini: positioning largely right but understates the penalty; the no-data-trail point is the only reason to tolerate the fidelity loss; wording must trade precision explicitly for zero-data deployment.
- Claude: positioning structurally correct, verifiability is niche rather than a headline benefit; distinct extra claim: the recovery runs show the factored FORMAT can carry trained quality (re-quantized trained factors scored 1.136 / 1.348 at identical bytes), so the bottleneck is the absence of training, not the format.

CORRECTION 1 (arithmetic, check it): several Round 1 answers wrote "0.232 of the 2.607 gap = 8.9%." Gap closed is DEFINED as the fraction of the gap: the patch's mean logprob is -10.545, base -11.150, full -8.543, so the patch recovered 0.605 of 2.607 nats = 23.2% of the gap. The 8.9% figure double-counts the fraction.

CORRECTION 2 (sign, for Claude especially): patch advantage in the recovery pilot is -0.213, meaning patch-init TRAILED random-init. One Round 1 answer described the 0.213 as an advantage for patch-init.

QUESTIONS:
R2-Q1. With correction 1 applied (23.2%, not 8.9%), does your verdict on the phrase "ship what was already learned" change? Answer: drop it, qualify it, or keep it, one or two sentences why.
R2-Q2. Claude's format point: is "the format can carry trained quality; only the conversion is weak" a real addition to the patch's real-world value, a value of the format but not of the shipped patch artifact, or not a value at all? One or two sentences.
R2-Q3. Final verdict on Ember's positioning in ONE line, then say whether you sign this merged wording, and if not give your exact amendment:
"The patch is a lossy, training-free distribution format for a fine-tune delta: at 19,358,176 B it closes 0.232 of the gap, with first-token accuracy 0.010 (below base 0.031), and it is not a training aid (patch-init trailed random-init by 0.213, one seed). It is useful only where training cannot happen and partial behavior transfer is acceptable: weights-only fine-tunes, many variants against one base, ~0.1 s hot-swap, deterministic checkable bytes, no data trail or teacher bill. Where training is available, a matched-byte distilled LoRA wins (gap closed 1.362 ± 0.033, first-token 0.167-0.177)."

## Round 2 answer: Muse Spark 1.3 (Meta Model API)

(served model muse-spark-1.3; usage {'completion_tokens': 4353, 'prompt_tokens': 801, 'total_tokens': 5154, 'completion_tokens_details': {'reasoning_tokens': 4155}, 'prompt_tokens_details': {'cached_tokens': 0}})

Corrections checked: 0.605/2.607 = 0.232 = 23.2%, 8.9% double-divides; -0.213 means trailed.

R2-Q1. Drop it. 23.2% is better than 8.9% but still leaves ~77% unshipped with first-token 0.010 below base 0.031, so "what was learned" still implies fidelity not achieved.

R2-Q2. Value of the format but not of the shipped patch artifact. It proves the bottleneck is the training-free conversion, not bytes/layout, but doesn't rescue today's 0.232 patch — it only motivates future training directly into factors.

R2-Q3 verdict: Ember's learn/ship split is right but the slogan overclaims — it's a niche zero-data lossy distributor, not general learned-quality shipping.
I sign the merged wording as-is.


## Round 2 answer: Gemini (gemini-3.5-flash-lite)

(served model gemini-3.5-flash-lite; usage {'prompt_tokens': 896, 'completion_tokens': 362, 'total_tokens': 1258})

**R2-Q1:** Drop it. Closing 23.2% of the gap still leaves the artifact as a lossy, low-fidelity approximation of a fine-tune rather than a faithful shipping container for what was learned.

**R2-Q2:** It is a value of the *format* (proving the architecture can represent the capability), but not of the shipped patch artifact, since the conversion fails to preserve the quality.

**R2-Q3:**
Ember's positioning: The Fraction Compressor patch is a lossy distribution format for static fine-tunes, useful strictly where zero data trail outweighs its heavy fidelity penalty.

**Signed** with one minor metric amendment for precision: 
"The patch is a lossy, training-free distribution format for a fine-tune delta: at 19,358,176 B it recovers 23.2% of the gap (patch -10.545 vs base -11.150 and full -8.543), with first-token accuracy 0.010 (below base 0.031), and it is not a training aid (patch-init trailed random-init by 0.213, one seed). It is useful only where training cannot happen and partial behavior transfer is acceptable: weights-only fine-tunes, many variants against one base, ~0.1 s hot-swap, deterministic checkable bytes, no data trail or teacher bill. Where training is available, a matched-byte distilled LoRA wins (gap closed 52.2% ± 1.3%, first-token 0.167-0.177)."

## Round 2 answer: NVIDIA Nemotron 3 Ultra (via Flash OmniRoute)

(served model nvidia/nemotron-3-ultra-550b-a55b; usage {'prompt_tokens': 891, 'completion_tokens': 1097, 'total_tokens': 1988})

**Correction 1 confirmed:** 0.605/2.607 = 23.2% gap closed. The 8.9% figure was erroneous.  
**Correction 2 confirmed:** Patch-init trailed random-init by 0.213 nats; it was a disadvantage, not an advantage.

**R2-Q1:** **Drop it.** 23.2% gap closed with first-token accuracy *below base* (0.010 vs 0.031) constitutes a lossy snapshot, not a shipment of learned behavior. The phrase implies fidelity the artifact does not possess.

**R2-Q3:** **Verdict:** Ember correctly separates deployment from training but understates the artifact’s regression vs. base model.  
**Sign-off:** I sign the merged wording as written. It accurately reflects the corrected arithmetic (0.232 gap, −0.213 init penalty), the first-token regression, the strict no-training-aid finding, and the decisive LoRA superiority, while fairly scoping the niche utility (zero-data, hot-swap, verifiable bytes).

## Round 2 answer: Glimmer (meta/muse-glimmer-30b, via Flash OmniRoute)

(served model meta/muse-glimmer-30b; usage {'prompt_tokens': 849, 'completion_tokens': 1815, 'total_tokens': 2664, 'prompt_tokens_details': {'audio_tokens': None, 'cached_tokens': 0}})

R2-Q1. Drop it / qualify it. 23.2% gap closed is better than 8.9% but still lossy, and first-token accuracy is 0.010 vs base 0.031. “Ship what was already learned” still overstates fidelity.

R2-Q2. Value of the format but not of the shipped patch artifact. The re-quantized trained factors show the factored representation can carry quality at the same byte budget, but the shipped patch is training-free and untrained; the real-world value is the current lossy artifact, not the format’s potential.

R2-Q3. Final verdict: Ember’s positioning is correct as a niche, lossy, training-free distribution format with no learning benefit and a first-token regression.

I do not sign verbatim. Amendment:
“The patch is a lossy, training-free distribution format for a fine-tune delta: at 19,358,176 B it closes 23.2% of the gap, 0.605 nats, with first-token accuracy 0.010 (below base 0.031), and it is not a training aid (patch-init trailed random-init by 0.213, one seed). It is useful only where training cannot happen and partial behavior transfer is acceptable: weights-only fine-tunes, many variants against one base, ~0.1 s hot-swap, deterministic checkable bytes, no data trail or teacher bill. Where training is available, a matched-byte distilled LoRA wins (gap closed 1.362 ± 0.033, first-token 0.167-0.177).”

## Round 2 answer: Grok (grok-4.7, via Flash OmniRoute)

(served model grok-4.7; usage {'prompt_tokens': 2052, 'completion_tokens': 4944, 'total_tokens': 6996, 'prompt_tokens_details': {'cached_tokens': 1152}, 'completion_tokens_details': {'reasoning_tokens': 4521}})

R2-Q1. Drop it. The corrected figure is 23.2% (0.605 of 2.607 nats; fraction 0.232, not 8.9%), but that is still a minority of the gap, and first-token accuracy 0.010 is below base 0.031. A larger share of the gap does not make “ship what was already learned” accurate.

R2-Q2. That is a possible value of the format, not of the shipped patch. The 1.136 vs 1.348 figures are the recovery pilot in which patch-init trailed random-init by 0.213; they do not show this training-free artifact carrying trained quality. Format capacity, even if later shown with actually trained factors, must not be credited to the patch Ember is positioning.

R2-Q3. Ember is right that the patch is not learning and not a warm start, and wrong to imply it faithfully ships the fine-tune.

I do not sign the merged wording. Amendment:

“The patch is a lossy, training-free snapshot of a fine-tune delta, not a learning aid and not a warm start: at 19,358,176 B it closes 23.2% of the gap (0.605 of 2.607 nats; fraction 0.232 — do not divide that fraction by 2.607), with first-token accuracy 0.010 (below base 0.031). Patch-init trailed random-init by 0.213 (one seed). Use it only when training cannot be run and a partial, sometimes regressive transfer is acceptable — chiefly a weights-only delta with no data trail and no teacher bill. Hot-swap (~0.1 s) and deterministic bytes are real but not unique and do not offset the fidelity loss. Where training is available, a matched-byte distilled LoRA wins (gap fraction 1.362 ± 0.033, first-token 0.167–0.177).”

## Round 2 answer: Claude (antigravity/claude-opus-4-6-thinking, via Flash OmniRoute)

(served model claude-opus-4-6-thinking; usage {'prompt_tokens': 990, 'completion_tokens': 648, 'total_tokens': 1638})

**R2-Q1.** With the corrected 23.2%, "ship what was already learned" is still too generous but the case for *qualifying* rather than *dropping* is slightly stronger than at 8.9%. I'd **qualify it**: "ship a lossy approximation of what was already learned (~23% of the gap, with first-token accuracy below base)." 23.2% is non-trivial transfer of *something*, but the first-token regression proves the shipped artifact distorts the learned distribution enough that "what was learned" without a qualifier is misleading.

**R2-Q2.** Claude's format point — "the factored format can carry trained quality; only the conversion is weak" — is **a value of the format, not of the shipped patch artifact**. It tells you the compression scheme isn't inherently lossy at this level; a better conversion pipeline (e.g., factor-aware fine-tuning or iterative re-fitting) could close more gap at the same byte budget. That's genuinely useful information for R&D roadmap decisions, but it adds zero real-world value to the artifact a user downloads today. The patch-as-shipped is still the 23.2%-gap, below-base-first-token object. Potential ≠ delivered value.

**R2-Q3.**

**Verdict on Ember's positioning:** Structurally correct on learn-vs-ship separation; overstated on fidelity and verifiability salience; the patch is a niche deployment format, not a capability showcase.

**On the merged wording:** I **sign it with one amendment.** The phrase "partial behavior transfer" is vague enough to let a reader imagine 50%+. I'd replace it:

> "…and partial behavior transfer is acceptable"

with:

> "…and ~23% gap closure with degraded first-token accuracy is acceptable"

Full amended version:

> "The patch is a lossy, training-free distribution format for a fine-tune delta: at 19,358,176 B it closes 0.232 of the gap, with first-token accuracy 0.010 (below base 0.031), and it is not a training aid (patch-init trailed random-init by 0.213, one seed). It is useful only where training cannot happen and ~23% gap closure with degraded first-token accuracy is acceptable: weights-only fine-tunes, many variants against one base, ~0.1 s hot-swap, deterministic checkable bytes, no data trail or teacher bill. Where training is available, a matched-byte distilled LoRA wins (gap closed 1.362 ± 0.033, first-token 0.167–0.177)."

Everything else — the niche list, the LoRA comparison, the recovery-pilot sign — I endorse as stated.

## Compute

Hosted API calls (purpose "patch value discussion"; NOT appended to results/api_usage_log.jsonl this run because the push agent was still running in parallel and holds that file in its batch; append these four rows after the push lands):
- {"provider": "meta-model-api", "model": "muse-spark-1.3", "time": "2026-10-29T19:56Z (approx)", "purpose": "patch value discussion", "prompt_tokens": 697, "completion_tokens": 4720, "total_tokens": 5417}
- {"provider": "google-gemini", "model": "gemini-3.5-flash-lite", "time": "2026-10-29T19:57Z (approx)", "purpose": "patch value discussion", "prompt_tokens": 797, "completion_tokens": 831, "total_tokens": 1628}
- {"provider": "meta-model-api", "model": "muse-spark-1.3", "time": "2026-10-29T20:02Z (approx)", "purpose": "patch value discussion", "prompt_tokens": 801, "completion_tokens": 4353, "total_tokens": 5154}
- {"provider": "google-gemini", "model": "gemini-3.5-flash-lite", "time": "2026-10-29T20:03Z (approx)", "purpose": "patch value discussion", "prompt_tokens": 896, "completion_tokens": 362, "total_tokens": 1258}
Hosted totals: Spark 10,571 tokens; Gemini 2,886 tokens; 13,457 total.

Flash-local OmniRoute calls (not logged in api_usage_log.jsonl, per the standing convention for Flash-local panel calls; this file is their record):
- Nemotron (nvidia/nemotron-3-ultra-550b-a55b): Round 1 first call 804 / 2,056 / 2,860 (answer file lost in the Flash /tmp wipe); Round 1 answer of record 804 / 2,481 / 3,285; Round 2 891 / 1,097 / 1,988.
- Glimmer (meta/muse-glimmer-30b): Round 1 first attempt failed (no output, /tmp wipe); Round 1 answer of record 745 / 3,520 / 4,265; Round 2 849 / 1,815 / 2,664.
- Grok (grok-4.7): Round 1 1,937 / 4,739 / 6,676; Round 2 2,052 / 4,944 / 6,996.
- Claude (claude-opus-4-6-thinking, served via antigravity/claude-opus-4-6-thinking): Round 1 875 / 1,204 / 2,079; Round 2 990 / 648 / 1,638.
- GPT-OSS: not called (skipped per instruction; provider 410 model_shutdown since Oct 28).
