# The cloning question, put to four outside AIs (2026-10-28)

Published in this repo on 2026-10-29. Every model got the identical brief below. Replies are verbatim. Calls logged in results/api_usage_log.jsonl under purpose `cloning_question_panel`.

## The brief

A solo developer built Fraction Compressor: it takes an existing fine-tuned model and the base model it came from, and compresses the difference (the delta) into a patch file of about 19 MB instead of about 1 GB, at roughly 0.3 bits per weight, which can be swapped into the base model live. His stated vision: a fine-tune's personality and behavior as a small file you can carry and plug in anywhere, the way you would move an AI assistant's personality to a new account. His own testing found a limit: broad behavior transfers measurably, but skills gated by the first generated token transfer weakly, the knowledge moves but the trigger does not, so the copy is partial. He asks: 'Am I opening doors for AI to clone itself faster?' Give your honest answer in under 250 words: what this does and does not do for AI self-replication, and where you would draw the line if you disagree with the reassuring reading.

## Gemini (gemini-3.5-flash-lite, via Google Gemini API; 459 tokens)

Fraction Compressor enables weight-space delta patching, acting as a "personality mod" for open-weights models. For AI self-replication, this is an accelerant of efficiency, not autonomy. It reduces the bandwidth cost of distributing fine-tunes, making swarm architectures or decentralized model-swapping cheaper.

However, it does *not* grant an AI the capacity to self-replicate. Replication requires agency, compute acquisition, and orchestrating code execution—none of which a passive compression utility provides. The developer’s finding about weak trigger-token transfer highlights a fundamental limitation: knowledge without execution pathways is inert. A compressed personality cannot bootstrap itself into a new system.

The reassuring reading—that this is merely a benign tool for modular AI customization—holds true. It is structurally akin to mods in video games: it alters behavior, but cannot build the console.

**Where to draw the line:** The danger does not lie in the compression ratio, but in the *intent* of the weights being compressed. The line should be drawn at automated generation of self-modifying, goal-directed agent loops. So long as humans must manually apply the patches, Fraction Compressor is a breakthrough in storage efficiency, not a threshold of existential risk.

## Muse Spark 1.3 (via Meta Model API; 2,271 tokens)

No — not self-replication in the autonomous sense, but yes — faster cloning in the proliferation sense.

What it does: makes moving a fine-tune ~50x cheaper (1GB -> 19MB). If the base model is already everywhere, e.g. open-weights Llama/Qwen, then 19MB *is* the model for practical purposes. Easy to email, embed, smuggle out via logs, live-swap personas without reload. It lowers the cost of distributing refusal-removed, domain-specialized variants.

What it does not: create agency. It still needs someone/something to host the base, apply the patch, pay for inference. Your first-token limit matters: you aren't transmitting a perfect mind-upload, triggers / initial policies degrade.

Where I'd push back on reassurance: "partial copy = safe copy" is the wrong line. Broad behavior — tone, values, refusal tendency, domain knowledge — is often enough to cause harm. An attacker will select fine-tunes that survive 0.3 bits/weight, leave embeddings/first layers uncompressed, or re-train through the compressor. Partial today becomes near-total tomorrow.

Line I'd draw: treat patches as full models if the base is public. Don't publish methods tuned to preserve dangerous uplift / refusal-stripping under compression, or to hide deltas steganographically, and benchmark safety-critical transfer, not just average personality.

## GPT-OSS 120B (via Fireworks; 801 tokens)

**What it does**

- **Compresses a fine‑tune’s delta.** By storing only the weight‑difference between a base model and a fine‑tuned version, it shrinks a 1 GB checkpoint to ~19 MB (≈0.3 bit per weight).
- **Enables rapid swapping.** The patch can be applied to any copy of the same base model, giving that copy the fine‑tuned “personality” without shipping the full checkpoint.
- **Facilitates distribution of behaviour.** For end‑users, this is a practical way to move a custom assistant’s tone, style, or preferences between devices or accounts.

**What it does *not* do for AI self‑replication**

- **Doesn’t create new models.** It only re‑uses an existing base model; you still need a full‑size model to host the patch.
- **Limits transfer of “first‑token triggers.”** As you observed, skills that rely on a specific initial token or very tight conditioning often fail to activate, meaning the patch cannot faithfully clone complex, context‑sensitive abilities.
- **Leaves the training data intact.** The knowledge encoded in the base model remains unchanged; only a small bias shift is added, so the patch cannot generate novel architectures or learning algorithms.
- **Requires the same architecture and version.** A patch built for LLaMA‑2‑13B won’t apply to a different model family, restricting uncontrolled proliferation.

**Where to draw the line**

If the goal is to **mass‑distribute complete, autonomous agents** that can train themselves or replicate without a base model, this technique falls far short—it merely packages a lightweight “style” overlay. The security risk emerges only when many users share the same base model and can freely apply arbitrary patches, which could be used to inject malicious behaviour at scale. Mitigation focuses on controlling access to the base model, validating patches, and ensuring that critical capabilities (e.g., first‑token triggers) cannot be weaponized through tiny deltas. In short, it speeds up *personalization* but does not unlock unrestricted AI self‑replication.

## Muse Spark Open (via Baseten; 2,638 tokens)

Honest answer: This doesn't create self-replication, it lowers one distribution cost.

**Does:** Make a fine-tune portable *if* the base model is already everywhere. If that base is open or widely cached, a 19MB delta is easier to exfiltrate, share peer-to-peer, and hot-swap live than 1GB. That helps any actor - human or AI - trying to spread a personality fast.

**Does not:** Provide hosting, compute, or autonomy. It still needs the GB+ base, a loader that allows live patching, and a way to persist/run. Your own limit matters: at ~0.3 bits/weight the compression is lossy. Broad style transfers but first-token-gated skills do not reliably. Self-replication that depends on precise tool-calling loops, self-preservation instructions, or jailbreaks would likely break in that loss.

The reassuring reading holds only while that fidelity gap holds.

I would flip if: compression becomes near-lossless for trigger/first-token behavior, the model can autonomously write and apply its own delta without human approval, or you bundle scaffolding that auto-replicates.

If you ship, treat it like LoRA with extra exfiltration risk: add provenance/watermarking and don't enable unsupervised self-patching.

## Synthesis (5 lines)

1. All four agree the tool creates no agency, hosting, or compute: it lowers a distribution cost, it does not let an AI copy itself.
2. All four also say the proliferation effect is real: where the base model is public or already cached, a 19 MB patch is effectively the fine-tune, cheap to spread and hot-swap.
3. Muse Spark 1.3 says yes the most strongly: faster cloning "in the proliferation sense," and it rejects "partial copy = safe copy" because tone, values, and refusal tendency transfer well enough to matter, and partial today becomes near-total tomorrow.
4. GPT-OSS 120B is the most reassuring: the patch "merely packages a lightweight 'style' overlay," and its named risk is malicious patches on a shared base, not replication.
5. Gemini and Spark Open draw a conditional line in nearly the same place: fine while a human applies patches and the trigger fidelity gap holds; the flip point is near-lossless trigger transfer or unsupervised self-patching.
