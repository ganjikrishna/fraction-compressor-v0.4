# YouTube upload pack: Fraction Compressor demo (DRAFT, do not upload yet)

Header: prepared Fri 2026-10-30 for the Mon Nov 2 submission. Glimmer claim check (Oct 30, served model meta/muse-glimmer-30b): the title and description are CLEAN, every number matched the repo (19,358,176 B, 987,922,432 B, 51x, 0.31 bpw, 23.2% vs 2.1%, first-token 0.010 vs 0.031, 0.104 s / 0.087 s, BitDelta 62 MB floor, LoRA framing, prior-work separation). No changes needed in this file. Full record: results/submission_pack_glimmer_check.md.

## Which file to upload

- If v7 is approved: video/rough_cut_v7_final.mp4
- Otherwise the standing cut: video/rough_cut_v6_final.mp4, 178.633 s, one video stream and one audio stream, no subtitles.
- Upload as a NEW public video (do not reuse an earlier upload).

## Title (74 of 100 chars)

Fraction Compressor: a 19 MB patch file swaps a fine-tune's behavior, live

## Visibility

Public. Post, copy the watch URL, and confirm the link resolves in a signed-out check before it goes anywhere else.

## Description (paste as-is)

Fraction Compressor turns a fine-tune into one small patch file. A fine-tuned model is a base model plus a patch, the weight difference between the two, and that difference is normally almost as big as the model itself. On the pair in this demo, Qwen2.5-0.5B base and Instruct, the full difference is 987,922,432 bytes; our patch is 19,358,176 bytes, about 51x smaller, at about 0.31 bits per weight all in.

To be clear about the name: this tool does not compress the model. The base model stays full size and is loaded once. Only the fine-tune's change gets small. Patches swap in and out of the one running base model live (the two recorded swaps took 0.104 s and 0.087 s, file-load time on the demo machine).

What the video shows: the idea and what is new, the problem with full-size fine-tunes, a real run of the quickstart and patch maker, the live hot-swap demo (the base model rambles past a strict JSON answer; with the patch swapped in it returns exactly the object), the benchmark numbers on 96 fresh questions, and how the numbers were checked.

The honest limits, stated in the video and in the repo: the patch is lossy. On the headline pair it closes 23.2% of the score gap to the full fine-tune, against 2.1% for a plain uniform recipe, and its first-token accuracy (0.010) sits below the base model's own (0.031). A plain 1-bit delta (BitDelta) closes more at its own floor price of about 62 MB; our format is the one that fits at 19 MB. Where training is available, a distilled LoRA adapter at matched bytes beats the patch; the patch is for cases where training cannot happen. Skills gated by the first generated token transfer weakly through this format.

What was here before, and what was built this week: 1-bit delta compression is published work (BitDelta, Delta-CoMe), and Fraction Compressor v0.1 to v0.3 predates this week and lives in a separate repository. Built fresh this week for the Meta Global AI Developer Hackathon: the factored runtime, the recipe search with Muse Spark designing per-layer recipes in the loop, the first-token gate finding with its force-start control, and the verification harness.

Code and full results: https://github.com/ganjikrishna/fraction-compressor-v0.4

Built by Vinay K Ganji Krishna, solo participant (Indie Developer track, Push the Frontier), with Ember, an AI agent powered by Muse Spark, under his direction.

Narration: Vinay's voice, cloned locally with Chatterbox. The voice is the author's own, cloned with an open-source tool on his own machine, as disclosed on the video's closing slide. The product itself uses no text-to-speech at runtime.

## Chapters (from the narration blocks; same timings for v6 final and v7)

0:00 Introduction and the product
0:31 Building on an existing idea: what is old, what is new
0:55 The problem: a fine-tune is almost a second model
1:09 Do it yourself: a real run
1:25 The demo moment: swap a file, change the behavior
1:48 The numbers: smaller file, tested on fresh questions
2:33 Checked, not just claimed
2:46 Close: a chip, not a note

Note for v7: the only narration change is inside the numbers block, where the SmolLM2 pattern line is replaced by the first-token accuracy caveat. Chapter boundaries do not move.

## After upload

- Paste the watch URL into docs/submission_draft.md section 6 (3-Minute Demo Video), replacing the placeholder.
- Add the video file itself to the repo in the submission-day batch (per Vinay's Oct 28 instruction), and note the YouTube URL in the repo in that same batch.
- The same URL is used in the X post (see docs/x_post_pack.md).
