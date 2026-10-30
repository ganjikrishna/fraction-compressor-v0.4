# Demo video v7 internal review panel (2026-10-30)

Scope: the v7 change only. V7 = v6 final plus the two changes Muse
Wonder recommended in results/wonder_video_review.md, approved by
Vinay 2026-10-30 ("1 done, review internally after done"; Wonder added
to the panel at his 3:45 PM ET instruction). Nothing else in the video
changed. Full build record: video/v7_notes.md. Review brief given to
all four reviewers: video/v7_work/panel_brief.md (Wonder additionally
received the full narration_v7.txt as its text package).

## The change under review

1. Spoken, numbers block: "Same pattern on SmolLM2." replaced by
   "Honestly, the patch's first-word accuracy stays below the base
   model's own: this is probability recovery, not solved tasks."
   Block re-recorded with the v6 voice-clone method and spliced into
   the v6 master at the block boundaries.
2. Print, numbers slide: added line
   "First-token accuracy: patch 0.010 vs base 0.031".

Verification supplied to the panel (measured on the shipped file):
duration 178.627 s; one H.264 + one AAC, no subtitles; -16.02 LUFS,
true peak -1.80 dB; block loudness -15.94 / -16.01 (new block) /
-16.07 LUFS; pivot pause 0.636 s; inter-block pauses byte-identical;
Whisper spot-check of the new sentence word-for-word; frame
differencing shows only the numbers slide changed.

## Verdicts

### Glimmer (first reviewer): SHIP
Requested nvidia/meta/muse-glimmer-30b via Flash OmniRoute, served
model confirmed meta/muse-glimmer-30b, temperature 0.3.
"1. Accuracy: Yes. The new narration correctly states first-token
accuracy is below base (patch 0.010 vs base 0.031) and frames the
result as probability recovery, not solved tasks. The printed slide
line 'Same pattern on SmolLM2-360M.' remains as a print-only summary
of a verified separate result and is not asserted in narration. No
overclaim or misleading implication. 2. Splice consistency: Yes.
Duration 178.627 s vs v6 178.633 s... Block 6 is -16.01 LUFS,
gain-matched... tempo-fit 1.0157 to the exact 42.780 s span.
Inter-block pauses byte-identical to v6; honesty-pivot pause 0.636 s
vs 0.633 s. Whisper spot-check confirms word-for-word transcription
and exact numbers. Picture change limited to numbers-slide frames
only. 3. No reason not to ship. The change implements the Muse
Wonder recommendation exactly as approved by Vinay, preserves v6
master integrity, and meets technical specs."

### Muse Spark 1.3 (Meta Model API): SHIP
"1. Accurate, no overclaim: patch 0.010 < base 0.031 first-token
accuracy, metric of record is nats-gap recovery 23.2%, not solved
tasks. Printed SmolLM2 line stays but is a real separate result.
2. Splice is transparent: duration 178.627s vs 178.633s, loudness
-16.02 vs -16.03 LUFS, block 6 -16.01 vs neighbors -15.94/-16.07,
-0.07dB gain, 1.0157x tempo, pauses byte-identical, pivot pause
0.636s vs 0.633s. Whisper transcribes new sentence + all numbers
exactly. 3. No blocker: under 3:00, 1x H.264 1080p30 + 1x AAC,
picture change confined to numbers slide, print insurance 'patch
0.010 vs base 0.031' matches facts."
Logged in results/api_usage_log.jsonl, purpose "v7 video review"
(995 in / 1784 out).

### Gemini 3.5 Flash Lite: SHIP
"VERDICT: SHIP. 1. The spoken statement strictly aligns with the
verified metrics (patch 0.010 vs. base 0.031) and accurately frames
the project around its true metric of record (nats gap recovery)
without overclaiming task success. The added print line on the
numbers slide correctly reinforces this. 2. The splice meets
professional engineering standards. The new block's integrated
loudness (-16.01 LUFS) and tempo adjustment (1.0157x) seamlessly
match the surrounding track and preserve the pre-existing timing and
inter-block pauses. 3. The change precisely implements the Muse
Wonder / Vinay recommendation without unauthorized scope creep,
re-editing the rest of the video, or violating the 3-minute limit
(178.627 s)."
Logged in results/api_usage_log.jsonl, purpose "v7 video review"
(1121 in / 243 out).

### Muse Wonder 1.0 (Meta Model API, text package): SHIP
Wonder authored the original recommendation and judged whether the
fix landed, from the brief + full narration_v7.txt (it cannot watch
the mp4 via the API).
"SHIP. Spoken fix landed exactly: v7 narration contains verbatim
'Honestly, the patch's first-word accuracy stays below the base
model's own: this is probability recovery, not solved tasks.' and
'Same pattern on SmolLM2.' is gone. Whisper confirms word-for-word.
Accurate, no overclaim: 0.010 patch vs 0.031 base is indeed below
base; metric of record is probability recovery, not solved tasks.
Print insurance correct: 'First-token accuracy: patch 0.010 vs base
0.031', right numbers, right labels. No side effects shown: duration
178.627s (<180s), loudness -16.02 LUFS / block 6 -16.01 LUFS vs
neighbours -15.94/-16.07, tempo-fit to the exact replaced span,
pauses byte-identical (pivot pause 0.636s vs 0.633s), and frame
differencing shows only the numbers slide changed. No reason not to
replace v6 with v7."
Logged in results/api_usage_log.jsonl, purpose "v7 video review"
(1832 in / 2070 out).

## Panel outcome

Unanimous SHIP (4 of 4, no conditions, no flags). The panel finds
the new sentence accurate, the splice consistent with the rest of
the track by every supplied measurement, and no reason not to ship
v7 as the submission cut in place of v6. Adoption is Vinay's call;
demo_script.md still describes v6 until he adopts v7. Local only,
nothing pushed, nothing uploaded.
