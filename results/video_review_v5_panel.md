# Demo video v5: BitDelta honesty line, outside panel decision

Date: 2026-10-28. Question carried over from the v4 recheck
(results/video_review_v4.md, item (c)): in the spoken numbers block,
the BitDelta honesty line. Vinay's instruction: "do whats best
discuss with other ai's if needed."

## The decision

Facts (verified, results/bitdelta_baseline.json and the sweep files):
the plain 1-bit baseline (BitDelta-style init, sign times mean-abs,
no training) is 61,745,828 bytes and closes 43.6% of the gap; the
factored patch at a matched 61 MB budget closes 38.5%; the headline
factored patch is about 19 MB, a size where a plain 1-bit delta
cannot exist at all.

- Option A: keep the v4 line, "Honestly: plain one-bit closes more
  at its size." (spoken size dropped in v4; figure stays in slide
  small print)
- Option B: restore a short spoken size in the line.

Spark has argued both sides: v3 round, the spoken numbers were too
dense (partial on the numbers block); v4 round, the de-numbered line
was ruled NOT landed: vague without a spoken size, softens the
honesty, small print does not cure audio-only vagueness.

## Panel (identical brief to all three)

Brief: the facts above, both Spark positions, options A and B, and
the constraint that the video is audio-first for many viewers
(small print does not reach listeners). Each was asked: A or B,
exact wording if B (about 14 words max), one-line reason.

### Gemini (gemini-3.5-flash-lite, Google Gemini API)

- VOTE: B
- WORDING: "Honestly, plain one-bit at sixty-two megabytes closes more."
- REASON: "Without a spoken size, 'its size' is too vague for audio-only listeners."
- Call logged in results/api_usage_log.jsonl (purpose
  video_review_v5_panel_gemini, 613 tokens). Flash-local panelists
  below are not in the API log, per convention.

### GPT-OSS 120B (Flash-local, OmniRoute to NVIDIA NIM)

- VOTE: B
- WORDING: "Honestly, the plain one-bit delta at 62 MB closes more than our patch."
- REASON: "Provides the missing size, making the honesty claim clear for audio-only listeners."
- Route note: the nvidia/openai/gpt-oss-120b route returned HTTP
  410 and cfp/openai/gpt-oss-120b returned 502; the vote came from
  antigravity/gpt-oss-120b-medium on the same Flash OmniRoute.
  Flash-local call, not in the API log.

### Glimmer (meta/muse-glimmer-30b, Flash-local OmniRoute to NVIDIA NIM)

- VOTE: B
- WORDING: "Honestly: plain one-bit closes more at sixty-two megabytes."
- REASON: "Audio-first viewers need a spoken size to make the honesty claim concrete and not vague."
- Flash-local call, not in the API log.

## Decision

**B wins, 3-0.** All three panelists independently landed on the
same fix Spark's v4 round demanded: a spoken size makes the honesty
claim concrete for listeners; the v3 density concern is answered by
restoring exactly one figure, not the full set.

Adopted wording: Glimmer's, "Honestly: plain one-bit closes more at
sixty-two megabytes." It changes the v4 line least (only "its size"
becomes the concrete figure), keeps the script's spoken-number style
(words, not digits), and avoids GPT-OSS's "than our patch", which a
listener could mishear as a comparison against the 19 MB headline
patch rather than the matched-budget patch. Gemini's wording is
equivalent in content.

## Build outcome

B won, so v5 was built: video/rough_cut_v5.mp4 (new file; v4
untouched). Only block 6 was re-recorded in Vinay's cloned voice
(Chatterbox on Flash, ~/voice-clone/v5/narr_p6.wav, reference
vinay-voice-ref.wav) with the adopted wording; a text diff against
the v4 block confirms the honesty line is the only change. The new
take was paced (atempo) to the exact v4 block-6 speech span and
spliced into the v4 narration track inside the inter-block silences,
so blocks 1-5, 7, 8 and the picture are byte-identical to v4.
Narration stays 444 words; text of record video/narration_v5.txt;
script updated in docs/demo_script.md.

Verified on the final file:
- Duration 178.85s (under 180; v4 was 178.87s)
- 1920x1080 H.264, exactly ONE audio stream (AAC, 48 kHz stereo),
  zero subtitle streams
- Loudness -16.0 LUFS integrated, true peak -1.9 dBFS (ebur128)
- faster-whisper transcript of the new block confirms the line was
  voiced as written: "Honestly, plain 1-bit closes more at 62
  megabytes."

## Spark confirmation (Muse Spark 1.3, Meta Model API)

Sent the final spoken numbers block and asked whether the honesty
line is now concrete and accurate. Verbatim:

1. "Yes — now concrete: size is spoken as sixty-two megabytes."
2. "Yes — accurate: 61,745,828 B ≈62 MB, 43.6% > 38.5% matched."
3. "No — size insertion alone, no new problem introduced."

Call logged in results/api_usage_log.jsonl (purpose
video_review_v5_spark_confirm, 2,013 tokens).

Decision closed: the honesty line is settled with the spoken size
in. The remaining v4 flags (Llama-first ordering, spoken-number
density elsewhere) were not reopened by this panel and stay as
Vinay's final-cut calls.
