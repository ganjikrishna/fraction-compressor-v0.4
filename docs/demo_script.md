# Demo video script: Fraction Compressor v0.4

Exactly 3 minutes. One idea on screen at a time. Narration is the text under
each NARRATION heading, nothing else is spoken. Total narration: 440 words,
about 147 words per minute.

## 0:00-0:25 The product: a fine-tune as a tiny patch file

ON SCREEN: Title card: FRACTION COMPRESSOR v0.4. Under it, one line: a
fine-tune squeezed into a patch file, about 19 MB instead of about 1 GB.
Then the use cases, one at a time: many fine-tunes on one base, no full
copies stored; send a fine-tune as a small file; switch behavior
instantly; run on small machines.

NARRATION:
This is Fraction Compressor. It turns a fine-tuned model into one patch
file: about nineteen megabytes instead of about a gigabyte. It plugs into
the base model and swaps behavior live, in about a tenth of a second.
One base carries many fine-tunes, no full copies stored. Send a fine-tune
as a small file. Switch behavior instantly. Run on small machines.

## 0:25-0:44 Building on an existing idea: what is old, what is new

ON SCREEN: Two short lists. Published before: 1-bit delta compression,
BitDelta and Delta-CoMe; our earlier compressor work. Built this week:
factored runtime; Muse Spark recipes and claim judging; first-token gate
finding; verification harness. Repo address at the bottom:
github.com/ganjikrishna/fraction-compressor-v0.4.

NARRATION:
Honesty: one-bit delta compression is a published idea, BitDelta and
Delta-CoMe, and our earlier compressor work predates this week. Built
fresh this week: the factored runtime, Muse Spark designing recipes in
the loop and judging claims against the files, the first-token gate
finding, and the verification harness.

## 0:44-1:02 The problem: a fine-tune is almost a second model

ON SCREEN: Two file sizes side by side: the base model, and the full
difference file at 987,922,432 bytes.

NARRATION:
A fine-tune is a base model plus a patch: the difference between them.
That difference alone: nine hundred eighty-eight million bytes, almost
the model itself. It keeps a fraction: about nought point three bits per
weight, all in. Ten fine-tunes, ten near-full models.

## 1:02-1:21 Do it yourself: clone, quickstart, make a patch

ON SCREEN, in real steps, typed in a terminal:
1. `git clone https://github.com/ganjikrishna/fraction-compressor-v0.4`
2. `python3 examples/quickstart.py` and its printed size and error lines.
3. `python3 examples/make_patch.py --base <base-model-dir> --finetuned <finetuned-model-dir> --out patch.npz --rank 32`
   and its printed sizes: patch 19,434,496 bytes, full difference
   987,922,432 bytes.

NARRATION:
You can do this yourself. You need two models: a base and its fine-tune.
Clone the repo. Run the quickstart: it squeezes a sample patch, printing
size and error. Run the patch maker: it subtracts the fine-tune from its
base and writes one file, about nineteen million bytes.

## 1:21-1:48 The demo moment: swap a file, change the behavior

ON SCREEN: `python3 examples/hotswap_demo.py` running. First the base model
answers the strict JSON prompt (the "Return ONLY a JSON object" prompt for
Arrival, 2016, Denis Villeneuve): the right object, then extra rambling
text, then the line `JSON SCORE: parseable=False`. Then the swap line:
patch loaded live in 0.09s. Then the same prompt again: exactly the object,
and `JSON SCORE: parseable=True`. Then the capital of Japan answers:
base loops on a wrong city, patched answers one clean line.

NARRATION:
One base model, loaded once. I ask for strict JSON, a format programs
can read. The base writes the right object, then rambles on, failing the
format check. Watch: the patch swaps in, about a tenth of a second.
Same question again: exactly the object, check passed. Same patch, new
question: the capital of Japan. Base repeats a wrong city; the patch,
one clean line.

## 1:48-2:31 The numbers: smaller file, tested on fresh questions

ON SCREEN: The size table from the demo (full delta 987,922,432 bytes;
patches about 19.4 million bytes, 51x smaller), then the benchmark result
lines: 96 fresh questions, gap closed 23.2% vs 2.1%, and the second model
pair name, SmolLM2-360M. Then the scale test lines: Qwen2.5-1.5B, Spark
recipe 38,623,232 bytes inside the 39,046,144 byte human budget, margin
0.134 nats on 96 fresh questions, patch about 39 MB vs 3,087,138,816 byte
full difference, about 80x smaller. Then the baseline lines: at the plain
1-bit floor price of 61,745,828 bytes, plain BitDelta-style init gap
closed 43.6% vs factored rank-108 gap closed 38.5% at 61,258,816 bytes;
at 19,434,496 bytes no plain 1-bit delta fits, only the factored patch.

NARRATION:
The patch is fifty-one times smaller: nineteen million bytes against
nine hundred eighty-eight million. The measure: how strongly the model
backs the answer. On ninety-six questions, Spark's recipe at the human
budget closes twenty-three point two percent of the gap; the human
recipe, two point one. Winner: mlp_behemoth_lite; its parent overspent
and does not count. Same pattern on SmolLM2; on a model three times
bigger, Spark's recipe won by nought point one three four nats, inside
budget. Honestly: at sixty-two million bytes a one-bit patch closes more
gap. Our win is reach: at nineteen million bytes, where no plain one-bit
patch fits, ours works.

## 2:31-2:44 Checked, not just claimed

ON SCREEN: Two short lines, one at a time: the Muse Spark judging record
citing its result files; then the audit line, 41 of 41 checks passed.

NARRATION:
Then we checked ourselves. Muse Spark judged every headline claim and
had to cite the file behind each one. A quantum computer's random
numbers picked the audit sample: all forty-one audit checks passed.

## 2:44-3:00 Close: a chip, not a note

ON SCREEN: The base model with the small patch file next to it. End card:
repo address.

NARRATION:
This is not a memory file. A memory file is a note the model reads; this
patch is a chip swapped inside the machine, numbers that change the
model's math. Fine-tunes to carry and swap: one base, many behaviors.

---

## Production notes

- Screen recording on the Muse VM of the real runs, in this order:
  repo page, terminal clone and quickstart, make_patch run, then the
  hotswap_demo run. Use the actual output; the transcript of record is
  results/hotswap_demo_transcript.txt.
- Narration recorded after the picture cut, with an AI voice, mixed over
  the recording with ffmpeg. Exactly one audio stream (narration only).
- No burned-in subtitles. Titles and file sizes appear as part of the
  terminal output itself, not as overlays.
- Cut to exactly 3:00. If a block runs long, trim screen pauses, not
  narration words.
- The full caveats (score is not task solving, first-token accuracy stays
  low, the knowledge-bucket result, the second pair's percentage warning)
  live in the README's Benchmark results section; the video states the
  measure honestly in the numbers block and does not claim accuracy gains.
