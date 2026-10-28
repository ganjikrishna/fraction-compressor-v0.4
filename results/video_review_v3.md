# Demo video rough cut v3: outside AI recheck

Date: 2026-10-28. Video: video/rough_cut_v3.mp4 (179.07s, 1920x1080, one
AAC stream, -16.0 LUFS integrated, true peak -2.0 dBFS, no subtitles).
Narration: Vinay's own cloned voice (Chatterbox on Flash), 439 words,
opening with his personal introduction and the Ember credit.
Method: same three reviewers and same brief format as v2, plus the v2
fix list; each reviewer was asked to verdict each fix, then answer the
v2 questions again and re-score the Demo criterion.

Scores: Gemini 9.5/10 (v2: 7). Muse Spark 8/10 (v2: 5). GPT-OSS 8/10
(v2: 6).

Fix verdicts: Gemini 9 of 9 LANDED. GPT-OSS 9 of 9 LANDED. Muse Spark
8 LANDED, 1 PARTIAL (fix 3, numbers block: the visual is simplified as
required, but Spark judges the spoken numbers still dense).

All calls logged in results/api_usage_log.jsonl (purposes
video_review_v3_gemini 3,387 tokens; video_review_v3_spark 9,623;
video_review_v3_gptoss 3,784).

---

## Review 1: Gemini (gemini-3.5-flash-lite)

Here is the review of "Fraction Compressor v0.4" V3 based on the facts and rules provided.

### (a) Verdict on the 9 Fix Items
1. **Swap-time honesty:** LANDED (Narration says "well under a second"; 0.49s/0.104s on screen aligns cleanly).
2. **Length:** LANDED (Exactly 179.07 seconds, safely under the 180-second cap).
3. **Numbers block simplified:** LANDED (One big visual comparison, one plain sentence, heavy byte counts relegated to small print).
4. **SmolLM2-360M labeled:** LANDED (Explicitly printed on the numbers slide).
5. **Patch sizes labeled:** LANDED (Both `mlp_behemoth_lite` at 19,358,176 B and the uniform rank-32 at 19,434,496 B are clearly noted).
6. **Demo segment enhanced:** LANDED (Cropped real frames, larger font, clear red/amber/green visual boxing).
7. **Do-it-yourself real terminal:** LANDED (Replaced the typeset slide with genuine executing CLI scripts and clear bounding boxes).
8. **Plain sentences added:** LANDED (First-token gate mechanic and Muse Spark's explicit role are both stated plainly).
9. **Personal intro & attribution:** LANDED (Natural first-person opening by Vinay Ganji with Muse Spark attribution on slide 1).

---

### (b) Clarity Verdict for a Smart Newcomer in One Pass
**Clear and compelling.** A technical newcomer will immediately grasp the core value proposition (slashing a gigabyte fine-tune down to ~19MB without retraining, hot-swapping it live in under a second), understand what was built this week versus pre-existing foundations, and follow the live demo and benchmarks without getting bogged down in raw numbers.

---

### (c) Remaining Rule-Compliance Risk
* **Zero risk on time limit:** At 179.07s, it respects the exact 3-minute cap with a comfortable 0.93-second buffer.
* **Rule adherence:** The strict separation of pre-existing work (BitDelta/Delta-CoMe foundation) versus hackathon-built features (runtime, Spark loop, verification harness) is cleanly stated both in narration and on-screen, fully satisfying hackathon judging criteria.

---

### (d) The Three Weakest Remaining Moments, with Concrete Fixes
1. **The Numbers Slide Density (1:49–2:33):** Despite the simplification, this slide still contains a lot of dense comparative data (SmolLM2, Qwen2.5-1.5B, baseline metrics, nats) read in rapid succession.
   * *Fix:* Have the voiceover completely omit the specific "nats" score for Qwen2.5 and leave it purely as text on the screen, letting the narrator focus solely on the primary win factor ("Spark's recipe won inside budget").
2. **First-Token Gate Explanation (0:40–0:56):** The narration handles this well, but the text on the "Building on an Existing Idea" slide is visually crowded alongside the pre-existing vs. built-fresh split.
   * *Fix:* Give the first-token gate its own dedicated half-second micro-card or bullet point with larger typography so the eye isn't forced to parse a dense paragraph.
3. **Quantum Audit Mention (2:33–2:46):** "Quantum random numbers picked the audit sample" sounds slightly like a sci-fi buzzword unless you are deeply familiar with cryptographic or scientific sampling tooling.
   * *Fix:* Change the line slightly to "True random sampling picked the audit sample: all forty-one checks passed," removing any potential skepticism about quantum gimmickry.

---

### (e) Demo Score out of 10
* **Score:** **9.5 / 10**
* **Reasoning:** Exceptionally polished execution that fixes every prior critique: tight timing, crystal-clear visual signifiers (red/green boxes), authentic terminal captures, and a strong, honest narration style that builds immediate trust with judges.

---

## Review 2: Muse Spark 1.3 (Meta Model API)

(a) Verdict on each of the 9 fixes:

1. Swap-time honesty - LANDED: "well under a second" said twice and on slide, covers both 0.104s clean and 0.49s on-screen, "a tenth" gone.
2. Length - LANDED: 179.07s verified <180.00s, fixes v2 180.07s overage.
3. Numbers block simplified - PARTIAL: visual is simplified to 988MB vs 19MB bars + 51x + one plain 23.2% vs 2.1% sentence, but audio still carries 5 extra claims in 44s - winner name, parent overspent, SmolLM2, Qwen-1.5B 0.134 nats, 62MB baseline spoken.
4. SmolLM2-360M printed - LANDED: now on-screen as "Same pattern on SmolLM2-360M."
5. Both patch sizes labeled - LANDED: 19,358,176 winner mlp_behemoth_lite vs 19,434,496 uniform rank-32 labeled in DEMO PATCH SIZES block and NUMBERS small print, DIY shows 19,434,496 as made-above file.
6. Demo legibility - LANDED: real asciinema frames, zoomed/large font, red False / amber 0.49s SWAP / green True / red vs green Japan contrast as specified.
7. DIY real capture - LANDED: typeset replaced by real quickstart.py + make_patch.py runs with real PATCH SUMMARY 169 matrices, 19,434,496 B, 50.8x.
8. Two plain sentences - LANDED: gate sentence verbatim + Muse Spark proposed recipes / generated questions / judged claims verbatim, plus plain line on idea slide.
9. Personal intro + attribution - LANDED: "Hi, I'm Vinay Ganji..." opens, slide 1 has name + "Built with Ember, powered by Muse Spark."

(b) Clarity for smart newcomer in one pass:

CLEAR ENOUGH ON STORY, STILL HEAVY ON NUMBERS: problem > DIY > live swap proof > 51x + 23% win > self-check lands, but gate mechanism and numbers avalanche need second viewing.

(c) Remaining rule-compliance risk:

No disqualifier, but 3 risks: 1) "exactly 3 minutes" - 179.07s is safe if <=180s, fails if literally =180.00s - confirm tolerance; 2) "only functionality built during event" - you disclose pre-existing vs fresh, but base-model ramble/Lauderdale loop is pre-existing behavior shown for contrast - add on-screen "pre-existing base shown for contrast only"; 3) Biggest scoring risk, not legal: Impact 30 / Meta Tooling 25 - video names zero Meta tooling, says "powered by Muse Spark," demos on Qwen2.5-0.5B + SmolLM2-360M + Qwen2.5-1.5B, no Llama/Meta mention. Expect near-zero on Use of Meta AI Tooling unless you add explicit Meta-tool line. Also cloned Chatterbox own-voice not disclosed in-video - add credit to avoid authenticity flag.

(d) Three weakest remaining moments:

1. 1:49-2:33 numbers avalanche: mlp_behemoth_lite / parent overspent / 0.134 nats in voiceover overload. Fix: keep voice to 51x + 96-Q 23.2% vs 2.1% + 1 honest line "plain 1-bit wins at 62MB, we win at 19MB where it can't fit"; demote SmolLM2 + 1.5B detail to visual small-print only with 0.5s pause.
2. 1:10-1:26 scale whiplash: 36,864 bytes 14.2x then 19,434,496 bytes 50.8x looks contradictory. Fix: voice/label overlay "tiny sample test first" -> "now full model" and keep green boxes.
3. 1:26-1:49 Japan + gate no context: why Lauderdale loop? What fine-tune is patch? Gate abstract. Fix: header label "Patch = JSON + Tokyo-facts fine-tune", and 3-sec diagram on idea slide: Token-1 switch -> skill starts / never starts.

(e) Demo score:

8/10 - real live swap with boxed False/0.49s/True/Japan proof and real DIY run carries it, docked 2 for numbers density and unexplained sample scale.

---

## Review 3: GPT-OSS 120B (Fireworks)

**(a) Fix‑by‑fix verdict**

1. **Swap‑time honesty** – **LANDED**
2. **Length under 180 s** – **LANDED**
3. **Numbers block simplified** – **LANDED**
4. **“SmolLM2‑360M” label** – **LANDED**
5. **Patch‑size labels everywhere** – **LANDED**
6. **Demo segment boxed/high‑lighted** – **LANDED**
7. **DIY terminal capture** – **LANDED**
8. **Two plain sentences added** – **LANDED**
9. **Personal intro & slide header** – **LANDED**

---

**(b) Clarity verdict (one‑pass)**
The video delivers a crisp, end‑to‑end story: it introduces the author, states the problem, explains the novel runtime/first‑token gate, shows a reproducible DIY flow, demonstrates live hotswapping with clear visual cues, and finishes with quantitative results—easily understandable for a technically‑savvy newcomer.

---

**(c) Remaining rule‑compliance risk**
*Potential risk*: The quickstart/patch‑maker commands are displayed as “built fresh this week.” If those scripts existed in the repo prior to the hackathon, the video could be interpreted as showing pre‑existing functionality, which would violate the “only functionality built during the event may be shown” rule. A brief on‑screen note clarifying that the **factored runtime** and **patch‑maker modifications** are the newly‑added parts would mitigate this risk.

---

**(d) Three weakest moments & concrete fixes**

1. **Swap‑time ambiguity** – The narration says “well under a second” while the overlay only shows “0.49 s”.
   *Fix*: Add an on‑screen caption reading “Swap completed in 0.49 s (well under 1 s)” the moment the amber‑boxed swap line appears.

2. **Small‑print numbers slide** – Patch‑size and baseline numbers are in tiny text at the bottom, hard to read on a 1080p screen.
   *Fix*: Increase the font size of the small‑print block and/or provide a brief spoken “The baseline 1‑bit delta is 62 MB; our compressed patch is 19 MB” while the slide is shown.

3. **Demo‑step pacing** – The “JSON SCORE: parseable=False/True” boxes flash quickly, giving viewers little time to register the significance.
   *Fix*: Insert a 1‑second pause after each boxed result, accompanied by a voice‑over cue (“Base model fails JSON validation” / “Patched model passes JSON validation”).

---

**(e) Demo score (out of 10)**
**8 / 10** – The demo is technically solid, shows live swapping, quantifies impact, and leverages Meta’s Muse Spark tooling, but the impact narrative could be tighter and a few visual details (swap time, numbers readability) still need polishing.

---

## Synthesis (Ember, from the three rechecks above)

### Fix verification

- 26 of 27 fix verdicts are LANDED. The single PARTIAL is Spark on
  fix 3: the numbers VISUAL is exactly as specified, but the spoken
  numbers block still carries five claims (winner name, parent
  overspent, SmolLM2 sentence, the 1.5B nats sentence, the honest
  baseline). Gemini and GPT-OSS both call the same block LANDED;
  Gemini still lists its density as the weakest remaining moment.
  Net: the block is compliant and much clearer, and it remains the
  densest 44 seconds of the video by design (the claims are the
  submission's evidence, each one validator-checked).
- Scores moved from 7/5/6 (v2) to 9.5/8/8 (v3). Every reviewer credits
  the same things: the honesty wording, the boxed real demo, the real
  DIY run, and the personal opening.

### New flags, with our read

1. **Meta tooling visibility (Spark, its strongest point).** Spark says
   the video "names zero Meta tooling" because the demos run on Qwen
   and SmolLM2 pairs and Llama is never mentioned. Partly a misread:
   Muse Spark is Meta's model, is named in the intro, the idea block,
   the numbers block and the checked block, and the Ember credit is on
   slide 1. But the Llama 3.2 pair (Meta's own open weights, pair 3 of
   the benchmark) genuinely is absent from the v3 narration after the
   word-budget trims. If a v4 happens, one short clause restores it;
   the submission form's Meta-products field carries the full story
   regardless.
2. **Voice-clone disclosure (Spark).** The narration is Vinay's own
   voice, cloned with Chatterbox from his own sample, by his choice.
   Spark suggests an in-video credit to pre-empt an authenticity flag.
   Cheap to add to the closing slide or the submission text.
3. **Old/new demarcation inside the demo segments (GPT-OSS, echoing
   its v2 point).** It worries the quickstart and patch-maker could be
   read as pre-existing code. They are event-week code in the fresh
   v0.4 repo; the video's idea block already separates old from new.
   A perception risk only; the submission text can state it outright.
4. **"Exactly 3 minutes" tolerance (Spark).** 179.07s is under the cap
   every reviewer accepts; Spark alone wonders whether the rule means
   exactly 180.00. The v2 overage was the real risk and it is fixed.
5. **Smaller polish notes:** the quickstart's 36,864-byte sample next
   to the 19 MB full-model patch can read as a contradiction without a
   "sample vs full model" label (Spark); the small print is small by
   design (GPT-OSS); the quantum line could be softened (Gemini) —
   it is factual (a real IBM Quantum random fixture picked the audit
   sample), so it stays.

### Bottom line

V3 lands the full v2 fix list plus Vinay's three opening additions
(personal intro as "Vinay Ganji", the Ember/Muse Spark credit, and
the Glimmer-audit sentence split that keeps SmolLM2-360M and the
Qwen2.5-1.5B scale test un-confusable). Remaining notes are polish and
submission-text items, not blockers.
