# Muse Wonder review of the demo video (2026-10-30)

- Date: 2026-10-30
- Model: muse-wonder-1.0 (Meta Model API, chat completions)
- Requested by: Vinay, 2026-10-30

## What Wonder reviewed (exact)

Wonder cannot watch the mp4 through this endpoint. The review is of the
complete video package AS TEXT:

- The exact narration: video/narration_v6.txt (466 words), sent verbatim.
- The shot and slide plan: docs/demo_script.md in full (v6 state: final
  file video/rough_cut_v6_final.mp4, 178.633 s, title card carries the
  printed clarification line, narration disclosure in small print on the
  closing slide).
- A key-facts sheet supplied with the prompt: headline pair numbers
  (19,358,176 B patch vs 987,922,432 B full delta; gap closed 23.2%;
  first-token accuracy patch 0.010 vs base 0.031; hot-swap 0.104 s and
  0.087 s of record, 0.49 s shown in the demo recording), the BitDelta
  matched-budget figures, the Llama and 1.5B results, the 41/41 audit,
  and the first-token gate skill-test numbers.
- Judging context supplied: judges stop watching at exactly 3:00, Demo
  is 25% of the score, video must show only event-built work with the
  pre-existing vs built statement.

Wonder did NOT see the actual frames, motion, slide legibility, or the
cloned-voice audio. Its judgments are of the text package only, and it
says so itself where relevant.

## Collection note

Six calls total under purpose "wonder video review" (see
results/api_usage_log.jsonl). Two early attempts at the accuracy
question (one combined questions 4-6 call, one question 4 alone) spent
the entire 8192-token completion budget on reasoning and returned no
content (finish_reason "length"); the question was then split by
narration half and answered. The four content-bearing calls are
reproduced below verbatim, in question order.

---

## Questions 1-3 (verdict, first-30-seconds hook, pacing)

## 1. One-line verdict

> Credible and unusually honest, but it explains for 85 seconds before proving anything and then spends its longest block exposing that its headline recovery is only 23.2%.

## 2. Does the first 30 seconds hook a judge?

**It earns continued attention, but it does not fully hook.** The strongest material is there; the proof is not.

### What lands

- The size contrast is immediate and concrete: “about nineteen megabytes instead of about a gigabyte.”
- “It plugs into the base and swaps behavior live, well under a second” makes a testable promise the later demo actually pays off.
- “One base carries many fine-tunes, no full copies stored” gives the architecture in one understandable sentence.
- A named human presenter helps: “Hi, I'm Vinay Ganji.”

### What does not

- **No behavior is shown.** The first block is a title card and claims. The promised live swap does not arrive until **1:25**, nearly halfway through.
- The opening spends its second major beat on tooling credit: “I built it with Ember, my AI agent, powered by Muse Spark.” Interesting, but secondary to the problem and result.
- The naming correction consumes prime time: “To be clear: it does not compress the model. Only the fine-tune's change gets small. The base stays full size, loaded once.” Necessary, but the judge first hears what the product is *not*. It is also duplicated in small print on the same title card.
- The use-case tail becomes a spoken slide list: “Send a fine-tune as a small file. Switch behavior instantly. Run on small machines.” No user, workload, or concrete scenario makes those benefits vivid.
- The title card is overloaded for an alleged “one idea on screen at a time” design: product claim, clarification, four use cases, and agent credit.

**Judgment:** a technical judge stays because 19 MB versus 1 GB is a real hook. Attention begins leaking around the clarification and list, roughly the last third of the block. This assessment is from the script and slide plan; cloned-voice intelligibility and title-card legibility could make it better or worse.

## 3. Pacing, block by block

### 0:00–0:31 — Introduction

**Attention: decent start, late-block sag.**

The personal opening and size claim land quickly. Then the block keeps talking after the essential pitch is complete: agent credit, naming disclaimer, and four applications in 31 seconds. It promises a live swap but withholds it. This is an abstract product summary, not an opening demonstration.

### 0:31–0:55 — What is old versus new

**Attention: first sustained drop.**

The disclosure is ethically and competitively necessary, especially under the hackathon’s pre-existing-work rule. But 24 seconds of provenance this early is a tax: “one-bit delta compression is published, BitDelta and Delta-CoMe, and our work predates this week.” Judges who do not know those papers hear names, not stakes.

“The gate, plainly: behavior is set by the first generated token; if it does not change, the skill never starts” is intriguing, but nothing yet shows it. The block is an inventory—runtime, recipes, gate, harness—before the audience has seen a result worth auditing.

### 0:55–1:09 — The problem

**Attention: recovers.**

This is the tightest explanatory block. “Ten fine-tunes, ten near-full models” makes the storage problem obvious. It partially repeats the introduction’s 19 MB/1 GB contrast, and “nought point three bits per weight, all in” is jargon, but at 14 seconds it does not overstay.

### 1:09–1:25 — Do-it-yourself run

**Attention: credibility up, excitement down.**

A genuine terminal capture is better than a fake slide, and the commands make the project feel reproducible. But this is procedure before payoff: “Run the quickstart: it squeezes a sample patch, printing size and error.” A judge is asked to care about invocation details before seeing the dramatic behavior change. Terminal density and font size are also major unknowns from the text package.

### 1:25–1:48 — Live swap demo

**Attention: peak.**

This should have happened much earlier. The sequence is clear: base fails the format check, “the patch swaps in live, well under a second,” patched model produces “exactly the object, check passed,” then handles a new question. Red/amber/green boxing should make the before-and-after legible.

The drama is still modest. The base initially “writes the right object, then rambles,” so its failure is formatting discipline, not total incompetence. The capital-of-Japan example is memorable, but “Base repeats a wrong city” is so odd that a skeptical judge may wonder how representative the prompt is. Still, this is the first block that *shows* rather than asserts.

### 1:48–2:33 — Numbers

**Attention: the major cliff.**

At 45 seconds, this is almost twice the live demo and the densest passage in the video. It opens with a negative result: “First, Meta's Llama 3.2 1B: recovery ran weaker; uniform recipe scored below the base.” Honest, but it makes the judge process failure before the headline win.

Then the block stacks model names, budgets, percentages, codenames, and unfamiliar units:

- “closes twenty-three point two percent of the gap; the human recipe, two point one”
- “Winner: mlp_behemoth_lite”
- “Same pattern on SmolLM2”
- “won by nought point one three four nats”
- “plain one-bit closes more at sixty-two megabytes”

The central weakness is unavoidable: **23.2% sounds small in absolute terms**, however impressive the 11-fold improvement over 2.1% may be. “Winner: mlp_behemoth_lite” means nothing without a visual anchor. “Same pattern on SmolLM2” supplies no spoken number. “0.134 nats” will be meaningless to most judges. The BitDelta admission builds trust, but immediately reminds them that another method performs better at 62 MB; “Our win is reach” rescues the point, yet arrives after several opportunities to tune out.

The script carefully defines the measure as “how strongly the model backs the answer,” not task accuracy. That is honest wording, but hurried judges may still hear 23.2% “gap closed” as capability recovery. The omitted first-token-accuracy result—patch below base—will matter if judges inspect the fuller results.

### 2:33–2:46 — Verification

**Attention: brief rebound, with an eye-roll risk.**

Forty-one of forty-one checks passing is clean and memorable. The self-checking structure also answers the obvious “did you cherry-pick this?” concern.

But the credibility mechanism is partly circular in presentation: Muse Spark “proposed the per-layer recipes, generated the fresh test questions, and judged every claim.” The same named system is inventor, examiner, and grader, albeit against result files. “Quantum random numbers picked the audit sample” sounds like novelty garnish; judges may remember the gimmick more than the verification.

### 2:46–2:59 — Close

**Attention: solid landing.**

“This is not a memory file” is defensive against a comparison the video never established, but the next image works: “this is a chip swapped inside the machine, changing the model's math.” That is the clearest conceptual distinction in the script. “One base, many behaviors” is a good final compression of the pitch.

The final file’s **178.63 seconds** also leaves a safe 1.37-second margin before the judges’ 3:00 cutoff.

**Overall pacing problem:** provenance, problem, and instructions occupy the first 85 seconds; the proof gets 23 seconds; the audit of that proof gets 45. Invert the emphasis—show the swap inside the first half-minute, then explain why it is legitimate—and the same facts would retain substantially more attention.

---

## Question 4, first half (accuracy, narration 0:00-1:48)

## 4a. Accuracy — first half, 0:00–1:48

### Introduction

- **“This week, for the Meta hackathon, I built Fraction Compressor.”** — **Overshoot.** The project predates this week (v0.1–v0.3); the disclosure at 0:31 mitigates but does not erase the opening claim, which is exactly what hackathon judges police.
- **“It turns a fine-tuned model into one patch file: about nineteen megabytes instead of about a gigabyte.”** — **Misleading as stated.** The patch alone is not the fine-tuned model; it is useless without the full base. The 19 MB / 988 MB figures (19,358,176 vs 987,922,432 B, ~51x) are accurate only for the Qwen2.5-0.5B headline pair, unnamed here — the 1.5B patch is ~38 MB.
- **“It plugs into the base and swaps behavior live, well under a second.”** — **Half true.** Swap *loading* is supported (0.104s/0.087s of record; 0.49s in the shown recording). “Swaps behavior” is not established by load time, and key facts show transfer is weak.
- **“To be clear: it does not compress the model. Only the fine-tune's change gets small. The base stays full size, loaded once.”** — **Accurate.** Best line in the half; it corrects the product name.
- **“One base carries many fine-tunes, no full copies stored.”** — **Unproven in the video.** Only one patch is ever swapped in; multi-patch carrying is arithmetic, not demonstrated.
- **“Send a fine-tune as a small file. Switch behavior instantly.”** — **“Instantly” overshoots** the video’s own careful “well under a second,” and again asserts behavior change, not weight loading.
- **“Run on small machines.”** — **Unsupported and misleading.** The base stays full-size in memory; the saving is storage/transfer, not runtime footprint. No small machine is shown.

### What is old vs new

- **“Honesty first: one-bit delta compression is published, BitDelta and Delta-CoMe, and our work predates this week.”** — **Accurate** and satisfies the disclosure rule.
- **“Built fresh this week: the factored runtime, Spark recipes designed in the loop, the first-token gate, and the verification harness.”** — **Mostly unverifiable here, one category error:** the gate is a *finding*, not something “built,” and no evidence for any of the four appears in this half.
- **“The gate, plainly: behavior is set by the first generated token; if it does not change, the skill never starts.”** — **Overshoot.** A limited finding is stated as a universal law (“never”). Worse, the omitted key fact — skills transfer weakly through the patch (1/10 clean vs the full fine-tune’s 8/10) — directly undercuts the “swaps behavior” pitch, and a sharp judge will find that in the full record.

### The problem

- **“A fine-tune is a base model plus a patch: their difference.”** — **Terminology conflation.** The full difference is a delta, not “a patch”; calling it one blurs the very distinction the product sells.
- **“That difference: nine hundred eighty-eight million bytes.”** — **Accurate for the headline pair only**, presented as generic. It is Qwen2.5-0.5B-specific.
- **“It keeps a fraction: nought point three bits per weight, all in.”** — **Accurate** (0.315 bpw effective on the headline pair).
- **“Ten fine-tunes, ten near-full models.”** — **Assumes full-parameter fine-tunes stored wastefully.** LoRA/adapter fine-tunes — the common case — are already small files; the problem framing ignores the obvious incumbent.

### Do it yourself

- **“Run the quickstart: it squeezes a sample patch, printing size and error.”** — **Technically true, misleading noun.** That “error” is reconstruction error on a sample, not behavioral fidelity; nothing tells the judge the two differ enormously (23.2% gap closed).
- **“It subtracts the fine-tune from its base and writes one file, about nineteen million bytes.”** — **Two flags.** The subtraction is stated backwards (delta = fine-tuned − base), and “about nineteen million” holds only for the rank-32 patch (19,434,496 B) on this pair at this rank — neither condition is spoken.

### Live swap demo

- **“The base writes the right object, then rambles, failing the format check… exactly the object, check passed.”** — **Accurate** for the shown recording (`parseable=False` → `True`).
- **“Base repeats a wrong city; the patch, one clean line.”** — **Accurate as anecdote, misleading as evidence.** Two cherry-picked prompts imply the patch restores fine-tune behavior and fixes factual errors, while first-token accuracy of the patch is *below* base (0.010 vs 0.031).
- **Structural flaw a judge can press:** the demo compares base vs patched but **never shows the actual fine-tune’s output**, so it proves the patch *changes* output, not that it *reproduces the fine-tune*.

---

## Question 4, second half (accuracy, narration 1:48-2:59)

### 4b. Accuracy — second half (1:48–2:59)

**Numbers block**

- **“First, Meta's Llama 3.2 1B: recovery ran weaker; uniform recipe scored below the base.”** Accurate per KEY FACTS, and creditably disclosed. But “weaker” is soft: it never says how weak, or whether the factored recipes also approached/below base there.

- **“The headline pair, Qwen2.5-0.5B: nineteen million bytes against nine hundred eighty-eight million, fifty-one times smaller.”** Accurate: 19,358,176 vs 987,922,432 bytes ≈ 51×. No flag.

- **“The measure: how strongly the model backs the answer.”** Technically true but materially misleading. This is a log-probability/gap measure, not getting answers right — and the omitted fact is damning: first-token accuracy for the patch is **0.010 vs base 0.031**, i.e. *below the base it is meant to improve on*. A sharp judge will call “closes the gap” an accuracy claim in disguise.

- **“On ninety-six questions, Spark's recipe at the human budget closes twenty-three point two percent of the gap; the human recipe, two point one.”** Numbers match KEY FACTS (23.2%). But “the gap” is never defined in speech (gap between base and fine-tune, on that log-prob measure), and 96 questions is a small sample with no variance stated. Combined with the flag above, a listener hears “23% better answers”; nothing supports that.

- **“Winner: mlp_behemoth_lite.”** True as a label, content-free as spoken. Meaningless to a judge without the slide's byte figures; not inaccurate, just unverifiable from narration.

- **“Same pattern on SmolLM2.”** Unsupported as spoken. No numbers are given for SmolLM2 anywhere in the narration, and KEY FACTS supply none. “Same pattern” invites the judge to assume another 23%-style result that is never evidenced.

- **“On Qwen2.5-1.5B, Spark's recipe won by nought point one three four nats, inside budget.”** The 0.134-nat figure matches KEY FACTS. But “won” against what is unstated in speech (it beat *uniform*), “nats” is unexplained, and “inside budget” cites a budget never spoken. Precision theatre: an exact number with no comparator or scale a judge can evaluate.

- **“Honestly: plain one-bit closes more at sixty-two megabytes.”** True — 43.6% vs the factored format's 38.5% at ~62 MB — but the comparison is quietly switched: at 62 MB the factored number is 38.5%, while the headline 19 MB result is only 23.2%. Juxtaposed this way, a listener can easily over-credit the 19 MB patch with near-one-bit quality.

- **“Our win is reach: at nineteen million, no one-bit patch fits, ours does.”** Technically true and the most challengeable framing in the half. A 1-bit patch for this model is ~62 MB *by arithmetic*; “no one-bit patch fits at 19 MB” is a definitional truism, not an empirical result. Presented as a competitive “win,” it is a strawman baseline.

**Verification block**

- **“Muse Spark proposed the per-layer recipes, generated the fresh test questions, and judged every claim against its result file.”** Stated plainly, but this is a self-grading loop: the same system designed the recipes, authored the tests, and judged the claims. “Fresh” questions from the recipe-designer are not independent held-out evaluation, and “judged every claim” is exactly what a skeptical judge will discount.

- **“Quantum random numbers picked the audit sample: all forty-one checks passed.”** The 41/41 figure matches KEY FACTS. But *what* the 41 checks were, and out of how large a pool the sample was drawn, is never said — and quantum randomness adds zero evidentiary weight over ordinary randomness. It dresses a small, undefined audit in impressive-sounding machinery.

**Close**

- **“This is not a memory file… this is a chip swapped inside the machine, changing the model's math.”** Fair as metaphor; the patch does change the model's weights/math rather than being read as context. No accuracy flag.

- **“Fine-tunes to carry and swap: one base, many behaviors.”** Overshoot by implication. The demo shows essentially one working patch; KEY FACTS note the separate skill test transferred weakly (patch 1 clean vs full fine-tune 8 clean of 10) and first-token accuracy sits below base. “Many behaviors” is an aspiration stated as a delivered capability.

**Summary:** Every hard number spoken (51×, 23.2%, 2.1%, 0.134 nats, 62 MB, 41/41) checks out against KEY FACTS. The accuracy problem is not fabrication — it is omission and framing: a log-prob “gap closed” headline that hides below-base first-token accuracy, a definitional “no 1-bit fits” claim sold as a win, an undefined SmolLM2 “same pattern,” and a verification block where the system grades its own homework.

---

## Questions 5-6 (what is missing; changes before submission)

### 5. What is missing

- **No task-success metric.** “The measure: how strongly the model backs the answer” and “closes twenty-three point two percent of the gap” are log-probability claims. You never say first-token accuracy is **patch 0.010 vs base 0.031** — the patch is *below* base. A judge will find that in the results and treat the omission as cherry-picking.
- **The demo is two anecdotes, not evidence.** “exactly the object, check passed” and “the patch, one clean line” are single prompts. No base / patch / **full fine-tune** side-by-side, no success count. Especially damning because your own gate finding predicts weak transfer (your separate skill test: patch 1 clean vs fine-tune 8 clean — also unstated).
- **The headline use case is never shown.** “One base carries many fine-tunes” — the video swaps in exactly **one** patch, once. No library of patches, no A→B→A switching.
- **No small-machine proof.** “Run on small machines” is asserted. No device, no RAM footprint, no load/inference latency — only patch size and a swap time.
- **No “why not LoRA?” answer.** A ~19 MB natively-trained adapter is the obvious baseline. Never addressed.
- **The new code is barely visible.** DIY shows two terminal commands making a patch; the factored runtime, recipe loop, and gate — the claimed this-week builds — are listed, not demonstrated.
- Text-only caveat: I cannot judge frame legibility or cloned-voice intelligibility from this package.

### 6. Changes before submission

**Worth a re-cut (one block only):**
- Re-record the numbers block: swap out the content-free “Same pattern on SmolLM2.” for the accuracy caveat (“first-token accuracy stays below base; this is probability recovery, not solved tasks”). Net-zero length, so the 178.63s / −16 LUFS build survives. You have already done single-block cloned-voice splices twice (v4, v5) — this is a known, bounded cost, and it removes the single biggest credibility risk.
- Print-only, no re-record: put “patch 0.010 vs base 0.031 first-token accuracy” on the numbers slide, not just in the README. Cheap insurance if the spoken change slips.

**Only if time were free — do not attempt before Nov 2:**
- Filming a multi-patch swap and a quantified 10-prompt base/patch/fine-tune demo (new recordings + narration + re-verification; high risk, replaces your strongest visual moment).
- Small-device run, LoRA comparison, runtime code walkthrough.
- Spoken voice-clone disclosure — small print on the closing card is adequate; not worth a block re-record.

Leave the rest alone. The timing, honesty block, and BitDelta concession are already well-judged; a broader re-cut risks the verified final file for marginal gains.
