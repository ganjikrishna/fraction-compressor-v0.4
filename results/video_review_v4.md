# Demo video rough cut v4: Muse Spark recheck

Date: 2026-10-28. Video: video/rough_cut_v4.mp4 (178.87s, 1920x1080,
one AAC stream, no subtitles, -15.9 LUFS integrated, true peak
-1.9 dBFS). Narration: Vinay's cloned voice (Chatterbox on Flash),
444 words. Method: per Vinay's Oct 28 rule, the recheck went to Muse
Spark via the Meta Model API first (those credits expire after the
hackathon); Gemini and GPT-OSS were not re-run this round because
Spark flagged no accuracy problem. Call logged in
results/api_usage_log.jsonl (purpose video_review_v4_spark, 5,844
tokens).

V4 applies exactly three edits to v3 (all approved by Vinay):
1. Llama back in the numbers narration, ordered Llama first (Vinay's
   ordering direction), then the Qwen headline, SmolLM2, and the 1.5B
   test; the numbers slide follows the same order and its bars are
   labeled as the Qwen2.5-0.5B pair.
2. Voice disclosure credit on the closing slide.
3. The 62 MB BitDelta figure dropped from the spoken narration
   (stays in slide small print).

Build facts: only the numbers block was re-recorded; the other seven
blocks reuse the v3 takes. Whole track re-paced (atempo 0.886,
1.38s inter-block pauses). A faster-whisper transcript of the new
block confirms the new words were voiced as written and that
"sixty-two million" no longer appears in speech.

---

## Review: Muse Spark 1.3 (Meta Model API)

(a) Edit 1: LANDED factually, MIS-ORDERED rhetorically.
Accurate: 15.9% vs 23.2% = "ran weaker" true; uniform rank-32 negative gap closed = "scored below the base" true.
Order hurts: opening the numbers block with the weakest pair anchors on failure. Headline Qwen2.5-0.5B should lead, Llama as honestly/limits follow.
Label fix good: "Qwen2.5-0.5B pair" on 988MB vs 19MB / 51x prevents misattributing that win to Llama.
Funding trims: no accuracy lie. Dropping "its parent overspent" and "a model three times bigger" is clean for words, but costs context - winner why-it-matters and 1.5B scale anchor lost.

(b) Edit 2: LANDED.
Small-print "Narration: Vinay's voice, cloned locally with Chatterbox" resolves the v3 in-video non-disclosure flag - own-voice + tool + local. Minimal but sufficient. Still easy to miss vs spoken, but compliant.

(c) Edit 3: NOT LANDED.
"Honestly: plain one-bit closes more at its size" is vague without spoken size. Listener loses that its size = ~62M, ~61,745,828 bytes, ~3x factored, and that at matched budget plain wins 43.6% vs factored 38.5%. Small-print retention does not cure audio-only vagueness. Next line "at nineteen million, no one-bit patch fits" implies bigger, but doesn't quantify. Softens honesty while trying to fix density.

(d) NEW problems introduced:
Double de-numbering in speech: 62M gone + 3x bigger gone = no spoken comparator scale left to ground "Our win is reach." Slide-dependent auditability, fails with no subtitles / mobile / audio-only. Llama-first + vague BitDelta together dull hook and honesty in speech.

Verified clean: 178.87s <180, 444 words, Whisper confirms new Llama voiced and "sixty-two million" gone, -15.9 LUFS / -1.9 dBFS fine, one AAC.

(e) Updated Demo score: 8.5/10 - completeness and disclosure fixed from v3 8/10, but Llama-first opening and de-numbered baseline cost clarity/honesty in speech.

---

## Synthesis (Ember)

- **Accuracy: clean.** Spark confirms both halves of the Llama
  clause against the result files ("ran weaker" = 15.9% vs 23.2%;
  "scored below the base" = uniform's negative gap closed on that
  pair), calls the Qwen labeling on the bars correct, and finds no
  accuracy lie in the two funding trims.
- **Edit 2 fully landed** by Spark's ruling, closing its own v3
  flag.
- **Edit 3 is a genuine reviewer disagreement, recorded as-is.**
  The edit was applied exactly as Vinay directed (figure out of
  speech, kept in small print) to fix Spark's own v3 partial about
  spoken-number density; Spark now rules from the other side, that
  the spoken line is too vague without the figure. Both positions
  are defensible; the file records the tension rather than resolving
  it. The figure itself remains on screen for the whole numbers
  block (about 45 seconds).
- **Llama-first stays, per Vinay's rule for this build.** Vinay
  directed the order and set the test: keep it if it stays accurate
  and inside the word and duration budget (it does: clause verified
  accurate, 444 words, 178.87s), revert only if it measurably hurts
  clarity or accuracy. Spark's objection is rhetorical (it would
  lead with the headline pair), not an accuracy or comprehension
  failure, and Spark itself notes the slide labeling prevents the
  one real confusion risk. Vinay can overrule either way at final
  cut; swapping the two opening sentences back is a one-block
  re-record if he wants it.
- Score movement from this reviewer: 5 (v2) to 8 (v3) to 8.5 (v4).
