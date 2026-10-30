# Demo video script: Fraction Compressor v0.4 (v7)

Under 3 minutes (target 178 to 179.5 seconds; the rules say exactly 3
minutes and v2 ran 0.07s over). One idea on screen at a time. Narration is
the text under each NARRATION heading, nothing else is spoken.
Total narration: 480 words. Final v7 cut: 178.63 seconds (v6: 178.63,
v5: 178.85, v4: 178.87).

V5 change vs v4 (one edit, decided Oct 28): the BitDelta honesty line
in the numbers block speaks the size again: "Honestly: plain one-bit
closes more at sixty-two megabytes." Spark's v4 recheck had ruled the
de-numbered v4 line NOT landed (vague without a spoken size); a panel
of three outside AIs (Gemini, GPT-OSS, Glimmer) voted 3-0 for
restoring the spoken size, adopting Glimmer's wording. Full record:
results/video_review_v5_panel.md. Only block 6 was re-recorded
(cloned voice, same method); it was paced to the exact v4 block-6
span and spliced into the v4 track inside the inter-block silences,
so every other block and the picture are unchanged from v4. Final
file: 178.85s, one AAC stream, -16.0 LUFS, true peak -1.9 dBFS.
Narration text of record: video/narration_v5.txt.

V6 changes vs v5 (built Oct 29, after Vinay's listening notes on
v5; standing cut): Vinay heard quiet places and too much space
around the quantum block. Measurements showed no block far off
(loudness spread 0.86 LU); the quiet was momentary dips, and the
quantum space was assembly, the two longest pauses in the video
sat around that block (1.68s and 1.79s) on a track paced at
atempo 0.886. Fixes, no words cut anywhere: per-block gain matching
plus a gentle 2:1 compressor (spread down to 0.40 LU); inter-block
pauses shortened to about 1.3s and internal pauses over 0.34s
capped at 0.34s; block 1 re-recorded with the naming clarification
spoken after the swaps-live line (funded entirely by the pause
tightening). Candidate: 178.33s. The outside panel then reviewed
v6 (results/video_review_v6_panel.md): ADOPT WITH CHANGES, 4 to 1
with none against, and two changes were applied for the final:
(1) the clarification added in print on the title card, in small
print under the swaps-live lines; (2) about 0.3s of beat restored
at the "Honestly:" pivot in the numbers block (the pause after
"sixty-two megabytes.", cut from 0.676s to 0.34s by the cap, now
0.633s). Final file: video/rough_cut_v6_final.mp4, 178.63s, one
AAC stream, -16.03 LUFS integrated, true peak -1.84 dB measured on
the encoded file. Full build record: video/v6_notes.md. Narration
text of record: video/narration_v6.txt.

V7 changes vs v6 (built Oct 30, at Vinay's go, following Muse
Wonder's review of the video): two changes only. (1) In the numbers
block, the spoken sentence "Same pattern on SmolLM2." is replaced
by: "Honestly, the patch's first-word accuracy stays below the base
model's own: this is probability recovery, not solved tasks." Only
block 6 was re-recorded (cloned voice, same method) and spliced in
at the pause boundaries, so every pause and every other block is
unchanged. (2) The numbers slide gains one printed line:
"First-token accuracy: patch 0.010 vs base 0.031". Internal review
(results/video_review_v7_panel.md): SHIP unanimously, Glimmer,
Spark, Gemini, and Wonder. Final file: video/rough_cut_v7_final.mp4,
178.627s, one AAC stream, -16.02 LUFS integrated, true peak -1.80 dB
measured on the encoded file. Full build record: video/v7_notes.md.
Narration text of record: video/narration_v7.txt. Vinay adopted v7
as the submission cut on Oct 30, 2026.

FINAL CUT change (DONE in v6, Oct 29; originally planned for the
Nov 2-3 final cut, decided by Vinay Oct 29): the naming
clarification is in block 0, spoken right after "It plugs into the
base and swaps behavior live, well under a second." Line: "To be
clear: it does not compress the model. Only the fine-tune's change
gets small. The base stays full size, loaded once." Reason: the
name "Fraction Compressor" makes readers think the whole model is
compressed; only the fine-tune's difference is. It is also printed
on the title card (panel change, see the V6 paragraph above). The
roughly 9 to 10 seconds it costs were funded by pause tightening
across the track, not by trims or faster pacing of the words.

V4 changes vs v3 (three edits, all approved by Vinay on Oct 28):
1. The numbers block now opens with the Llama pair (Vinay's ordering:
   Llama first, then the Qwen headline, SmolLM2, and the 1.5B test).
   The Llama 3.2 1B result is spoken again (it fell out of v3 in the
   word-budget trims): weaker factored recovery there, and the uniform
   recipe scored below the base. The numbers slide follows the same
   order, and its bar visual is labeled as the Qwen2.5-0.5B pair.
   Funded inside the block by dropping the spoken winner's parent
   clause and the spoken "three times bigger" (both stay in print).
2. The closing slide adds a small-print credit: "Narration: Vinay's
   voice, cloned locally with Chatterbox."
3. The BitDelta baseline byte figure (62 MB) is no longer spoken
   (Spark's v3 partial: spoken numbers too dense). It stays in the
   numbers slide's small print; the spoken line is now "Honestly:
   plain one-bit closes more at its size."
Only the numbers block was re-recorded (cloned voice, same method);
the other seven blocks reuse the v3 takes. Pacing recomputed:
atempo 0.886, inter-block pauses 1.38s. Narration text of record:
video/narration_v4.txt; changed slides in video/slides_v4/.

V3 changes vs v2: opens with Vinay's personal introduction in his own
cloned voice (name shown as "Vinay Ganji"); one line credits Ember
(Muse Spark). Swap wording is now "well under a second" everywhere
(true for both the 0.104s transcript of record and the 0.49s contended
recording; "about a tenth of a second" removed). Numbers block rebuilt
around one visual. Demo frames zoomed with the parseable lines boxed.
Do-it-yourself is a real terminal capture, not a slide. Two plain
sentences added: what the first-token gate is, and what Muse Spark
concretely did. Glimmer audit fix (Oct 28): the SmolLM2 result and the
Qwen2.5-1.5B scale result are separate sentences in the numbers block;
SmolLM2-360M is the smaller second pair, "three times bigger" belongs
to the 1.5B test only.

## 0:00-0:31 Introduction and the product

ON SCREEN: Title card: FRACTION COMPRESSOR v0.4, by Vinay Ganji. Under
it, one line: a fine-tune squeezed into a patch file, about 19 MB
instead of about 1 GB. Under the plugs-in and swaps-live lines, the
clarification in small print: "To be clear: this does not compress
the model. Only the fine-tune's change gets small. The base stays
full size, loaded once." Then the use cases: many fine-tunes on one base,
no full copies stored; send a fine-tune as a small file; switch behavior
instantly; run on small machines. Small line at the bottom: Built with
Ember, powered by Muse Spark.

NARRATION:
Hi, I'm Vinay Ganji. This week, for the Meta hackathon, I built
Fraction Compressor. I built it with Ember, my AI agent, powered by
Muse Spark. It turns a fine-tuned model into one patch file: about
nineteen megabytes instead of about a gigabyte. It plugs into the base
and swaps behavior live, well under a second. To be clear: it does not
compress the model. Only the fine-tune's change gets small. The base
stays full size, loaded once. One base carries many
fine-tunes, no full copies stored. Send a fine-tune as a small file.
Switch behavior instantly. Run on small machines.

## 0:31-0:55 Building on an existing idea: what is old, what is new

ON SCREEN: Two short lists. Published before: 1-bit delta compression,
BitDelta and Delta-CoMe; our earlier compressor work. Built this week:
factored runtime; Muse Spark recipes and claim judging; first-token
gate finding (with its plain-words line: a fine-tune's behavior is set
by its first generated token); verification harness. Repo address at
the bottom: github.com/ganjikrishna/fraction-compressor-v0.4.

NARRATION:
Honesty first: one-bit delta compression is published, BitDelta and
Delta-CoMe, and our work predates this week. Built fresh this week: the
factored runtime, Spark recipes designed in the loop, the first-token
gate, and the verification harness. The gate, plainly: behavior is set
by the first generated token; if it does not change, the skill never
starts.

## 0:55-1:09 The problem: a fine-tune is almost a second model

ON SCREEN: Two file sizes side by side: the base model, and the full
difference file at 987,922,432 bytes. This tool: about 0.3 bits per
weight, all in.

NARRATION:
A fine-tune is a base model plus a patch: their difference. That
difference: nine hundred eighty-eight million bytes. It keeps a
fraction: nought point three bits per weight, all in. Ten fine-tunes,
ten near-full models.

## 1:09-1:25 Do it yourself: a real run

ON SCREEN: a real asciinema terminal capture (recorded on Flash) of:
1. `python3 examples/quickstart.py` and its printed size and error lines.
2. `python3 examples/make_patch.py --base <base> --finetuned <finetuned> --out patch.npz --rank 32`
   on the real Qwen2.5-0.5B pair, printing the PATCH SUMMARY: patch byte
   price 19,434,496 B (the uniform rank-32 patch), full delta
   987,922,432 B, 50.8x smaller. Successive genuine terminal states,
   dead time cut. No text altered.

NARRATION:
Do it yourself: you need a base and its fine-tune. Clone the repo. Run
the quickstart: it squeezes a sample patch, printing size and error.
Run the patch maker: it subtracts the fine-tune from its base and
writes one file, about nineteen million bytes.

## 1:25-1:48 The demo moment: swap a file, change the behavior

ON SCREEN: zoomed/cropped frames from the REAL asciinema recording of
`python3 examples/hotswap_demo.py` (hotswap_v2.cast), same terminal
text throughout, wrapped wider for a larger font:
1. Base answers the strict JSON prompt, rambles after the object;
   the line `JSON SCORE: parseable=False ...` is boxed in red.
2. The PATCH SIZES block (full delta 987,922,432 B; uniform rank-32
   patch 19,434,496 B; mlp_behemoth_lite patch 19,358,176 B, both
   patches labeled) and the swap line `>>> SWAP: ... loaded live in
   0.49s` boxed in amber.
3. The lite patch answers the same prompt: exactly the object;
   `JSON SCORE: parseable=True ...` boxed in green.
4. Capital of Japan: the base's Lauderdale loop boxed in red; the
   patched one-line answer "The capital of Japan is Tokyo." boxed in
   green.

NARRATION:
One base model, loaded once. I ask for strict JSON. The base writes the
right object, then rambles, failing the format check. Watch: the patch
swaps in live, well under a second. Same question again: exactly the
object, check passed. Same patch, new question: the capital of Japan.
Base repeats a wrong city; the patch, one clean line.

## 1:48-2:33 The numbers: smaller file, tested on fresh questions

ON SCREEN (same order as the narration): A line for the Llama pair:
"First, Meta's Llama 3.2 1B: weaker recovery there; the uniform recipe
scored below the base." Then the big visual, labeled as the
Qwen2.5-0.5B pair: two bars, full difference 988 MB vs patch 19 MB,
"51x smaller". One plain sentence: on 96 fresh questions, Spark's
recipe kept 23.2% of the fine-tune's improvement; the hand recipe
kept 2.1%. A line naming SmolLM2-360M. Small print only: winner
patch (mlp_behemoth_lite) 19,358,176 bytes; uniform rank-32 patch
19,434,496 bytes (the one made above); Qwen2.5-1.5B scale test, Spark
recipe 38,623,232 bytes inside the 39,046,144 byte budget, +0.134
nats, about 80x smaller; honest baseline: at 61,745,828 bytes a plain
1-bit patch closes 43.6% vs our 38.5%; at 19 MB no plain 1-bit patch
fits at all.

NARRATION:
First, Meta's Llama 3.2 1B: recovery ran weaker; uniform recipe scored
below the base. The headline pair, Qwen2.5-0.5B: nineteen million
bytes against nine hundred eighty-eight million, fifty-one times
smaller. The measure: how strongly the model backs the answer. On
ninety-six questions, Spark's recipe at the human budget closes
twenty-three point two percent of the gap; the human recipe, two
point one. Winner: mlp_behemoth_lite. Same pattern on SmolLM2. On
Qwen2.5-1.5B, Spark's recipe won by nought point one three four nats,
inside budget. Honestly: plain one-bit closes more at sixty-two megabytes. Our
win is reach: at nineteen million, no one-bit patch fits, ours does.

## 2:33-2:46 Checked, not just claimed

ON SCREEN: Two short lines, one at a time: the Muse Spark judging record
citing its result files; then the audit line, 41 of 41 checks passed.

NARRATION:
Then we checked ourselves. Muse Spark proposed the per-layer recipes,
generated the fresh test questions, and judged every claim against its
result file. Quantum random numbers picked the audit sample: all
forty-one checks passed.

## 2:46-2:59 Close: a chip, not a note

ON SCREEN: The base model with the small patch file next to it. End card:
repo address, with a small-print line under it: "Narration: Vinay's
voice, cloned locally with Chatterbox." 

NARRATION:
This is not a memory file. A memory file is a note the model reads;
this is a chip swapped inside the machine, changing the model's math.
Fine-tunes to carry and swap: one base, many behaviors.

---

## Production notes

- Narration: Vinay's own cloned voice (Chatterbox on Flash,
  ~/voice-clone/narrate.py, reference vinay-voice-ref.wav), recorded
  per paragraph, mixed over the picture with ffmpeg. Exactly one audio
  stream (narration only), AAC, loudness about -16 LUFS, true peak
  under -1 dB. No burned-in subtitles. V4: blocks 1-5, 7, 8 are the
  v3 takes; block 6 re-recorded from video/narration_v4.txt; whole
  track re-paced at atempo 0.886 with 1.38s inter-block pauses
  (final file: 178.87s, -15.9 LUFS integrated, true peak -1.9 dBFS).
  V5: block 6 re-recorded from video/narration_v5.txt (the honesty
  line's spoken size restored; panel record in
  results/video_review_v5_panel.md), paced to the v4 block-6 span and
  spliced into the v4 track (final file: 178.85s, -16.0 LUFS
  integrated, true peak -1.9 dBFS). V6: block 1 re-recorded from
  video/narration_v6.txt (the clarification line); the whole track
  pause-tightened and level-matched, then the panel's two fixes
  (printed clarification on the title card, 0.3s of beat restored at
  the honesty pivot) applied in video/rough_cut_v6_final.mp4
  (178.63s, -16.03 LUFS integrated, true peak -1.84 dB measured on
  the encoded file). Build record: video/v6_notes.md.
- Timings above are targets; the final cut follows the recorded
  paragraph lengths and must land between 178 and 179.5 seconds total.
- The demo frames come from the genuine hotswap_v2.cast recording;
  only cropping, wrapping and highlight boxes are presentation.
  The transcript of record is results/hotswap_demo_transcript.txt.
- The full caveats (score is not task solving, first-token accuracy
  stays low, the knowledge-bucket result, the second pair's percentage
  warning) live in the README's Benchmark results section; the video
  states the measure honestly in the numbers block and does not claim
  accuracy gains.
