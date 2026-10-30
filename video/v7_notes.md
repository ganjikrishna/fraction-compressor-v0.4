# V7 demo build notes (2026-10-30)

V7 = v6 final plus exactly two changes, both from Muse Wonder's video
review (results/wonder_video_review.md), approved by Vinay 2026-10-30
("1 done, review internally after done"). Base file
rough_cut_v6_final.mp4 untouched; output is rough_cut_v7_final.mp4.
Narration text of record for this cut: narration_v7.txt (480 words,
one sentence swapped). docs/demo_script.md still describes the v6 cut;
it changes only when Vinay adopts v7.

## Change 1: numbers block narration

Old sentence: "Same pattern on SmolLM2."
New sentence: "Honestly, the patch's first-word accuracy stays below
the base model's own: this is probability recovery, not solved tasks."

Method (assemble_v7.py in v7_work/, mirroring v6 production):
- Only block 6 re-recorded: Chatterbox clone on Flash
  (~/voice-clone/narrate.py, reference vinay-voice-ref.wav, script
  v7_work/narr_p6_v7.txt = narration_v7.txt block 6). Raw take 43.31 s.
- Splice point: the v6 final's post-compressor track
  (v6_work/v6f_track_comp.wav, the one carrying the restored
  honesty-pivot beat), NOT the decoded AAC. Block 6 speech span there:
  109.140-151.920 s (42.780 s). Replacement window runs pause-midpoint
  to pause-midpoint (108.370-152.570 s), so the inter-block pauses
  before and after block 6 are byte-identical to v6 and the total
  duration is unchanged by construction.
- Take processing, same rules as assemble_v6.py: head/tail trim,
  internal pauses over 0.34 s cut to 0.34 s from the middle, speech
  RMS normalised to the track reference -18.2 dB (take measured
  -18.13 dB, so gain was -0.07 dB), atempo fit to the exact span
  (factor 1.0157), then the same gentle 2:1 acompressor as the v6
  track (threshold -20 dB, attack 20, release 250, makeup 1).
- Honesty-pivot pause: the new take's natural pause after
  "sixty-two megabytes." measured only 0.160 s at -45 dB, so it was
  set (silence inserted at its midpoint) to land at 0.633 s after the
  tempo fit, the value measured in the v6 final. In the finished v7
  track it measures 0.636 s at 147.075 s (silencedetect -40 dB).
- Loudnorm stage re-run on the whole spliced track exactly as
  restore_beat.py did for v6f (measure, then linear loudnorm
  I=-16, TP=-1.9, LRA=11).

## Change 2: numbers slide print

Added line: "First-token accuracy: patch 0.010 vs base 0.031"
(v7_work/render_seg6_v7.py, same renderer, fonts and colors as
render_slides_v4.py). The line sits in BODY 34 between the 23.2%/2.1%
lines and the SmolLM2 line; the lower block starts 20 px higher and
gaps are slightly tightened so the small print ends at y=1022 with a
clean bottom margin. Picture replaced frame-exactly: frames
3239-4585 of the v6 picture (t=107.967-152.867 s, cuts located by
frame differencing) swapped for the re-rendered slide; the rest of
the picture is the v6 picture re-encoded (libx264 crf 20). Mux as in
v6: video copy + AAC 192k.

## Verification (rough_cut_v7_final.mp4)

- Duration 178.627 s (v6: 178.633 s); limit 179 s. OK.
- Streams: exactly one H.264 1920x1080 30 fps + one AAC; no subtitle
  streams. OK.
- Integrated loudness -16.02 LUFS; true peak -1.80 dB (v6: -16.03,
  -1.84). OK.
- Per-block integrated loudness (final track, v6 method): block 5
  -15.94, block 6 (new) -16.01, block 7 -16.07 LUFS; v6 block 6 was
  -15.92. The new block sits in line with its neighbours. OK.
- Pivot pause 0.636 s (see above). OK.
- Frames: t=130 matches the new slide (mean abs diff 1.11 vs 4.16 for
  the old slide); frames at t=20, 60, 107.90 and 160 differ from v6
  by <=0.04 (untouched). OK.
- Whisper spot-check (faster-whisper small on Flash, block 6 of the
  shipped mp4): the new sentence transcribes word-for-word:
  "Honestly, the patch's first word accuracy stays below the base
  model's own. This is probability recovery, not solved tasks."
  All numbers in the block transcribe exactly (19 million, 988
  million, 51 times, 96, 23.2%, 2.1, 0.134, 62 megabytes). Residual
  ASR garbling is confined to model names (Llama/Qwen/Behemoth),
  the same class seen in the v6 spot-checks.

Internal review of this change: results/video_review_v7_panel.md.
Nothing pushed, nothing uploaded.
