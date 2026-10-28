# Demo video script: Fraction Compressor v0.4

Exactly 3 minutes. One idea on screen at a time. Narration is the text under
each NARRATION heading, nothing else is spoken. Total narration: 429 words,
about 140 words per minute.

## 0:00-0:19 Opening: what is old, what is new

ON SCREEN: The repo page, github.com/ganjikrishna/fraction-compressor-v0.4.
Nothing else.

NARRATION:
Quick note on what is old and what is new: the compressor idea and an
earlier version existed before this week. Everything you will see, the
runtime, the benchmark, the hot-swap demo, and the patch maker, was built
fresh this week, in this repo.

## 0:19-0:43 The problem: a fine-tune is almost a second model

ON SCREEN: Two file sizes side by side: the base model, and the full
difference file at 987,922,432 bytes.

NARRATION:
A fine-tuned model is a base model plus a patch: the difference between
the two, as numbers. A normal patch is almost as big as the model itself:
here, nine hundred eighty-eight million bytes. This tool keeps only a
fraction of that patch, at about one bit per weight. Ten fine-tunes, ten
near-full models to carry.

## 0:43-1:11 Do it yourself: clone, quickstart, make a patch

ON SCREEN, in real steps, typed in a terminal:
1. `git clone https://github.com/ganjikrishna/fraction-compressor-v0.4`
2. `python3 examples/quickstart.py` and its printed size and error lines.
3. `python3 examples/make_patch.py --base <base-model-dir> --finetuned <finetuned-model-dir> --out patch.npz --rank 32`
   and its printed sizes: patch 19,434,496 bytes, full difference
   987,922,432 bytes.

NARRATION:
You can do this yourself. It takes two models: a base, and a fine-tuned
version of that same base. Clone the repo. Run the quickstart: it squeezes
a sample patch and prints the size and the error. Then run the patch maker:
it subtracts the fine-tuned model from its base, squeezes the difference,
and writes one small file, about nineteen million bytes.

## 1:11-1:47 The demo moment: swap a file, change the behavior

ON SCREEN: `python3 examples/hotswap_demo.py` running. First the base model
answers the strict JSON prompt (the "Return ONLY a JSON object" prompt for
Arrival, 2016, Denis Villeneuve): the right object, then extra rambling
text, then the line `JSON SCORE: parseable=False`. Then the swap line:
patch loaded live in 0.09s. Then the same prompt again: exactly the object,
and `JSON SCORE: parseable=True`. Then the capital of Japan answers:
base loops on a wrong city, patched answers one clean line.

NARRATION:
Now the demo. One base model, loaded once. I ask for data in strict JSON:
a fixed format a program can read, nothing extra. The base model writes
the right object, then keeps talking, so the answer fails the format
check. Watch: the patch file swaps in, in about a tenth of a second.
Same question again: exactly the object, nothing else. The check passes.
Same patch, another question: asked the capital of Japan, the base model
repeats a wrong city; with the patch, one clean line.

## 1:47-2:27 The numbers: smaller file, tested on fresh questions

ON SCREEN: The size table from the demo (full delta 987,922,432 bytes;
patches about 19.4 million bytes, 51x smaller), then the benchmark result
lines: 96 fresh questions, gap closed 23.2% vs 2.1%, and the second model
pair name, SmolLM2-360M.

NARRATION:
The patch file is fifty-one times smaller: about nineteen million bytes
against nine hundred eighty-eight million. The measure is a score: how
strongly the model backs the right answer. On ninety-six fresh questions
Spark wrote for this, unseen by the search, Spark's winning recipe,
trimmed to the human recipe's byte budget, closes twenty-three point two
percent of the gap to the full patch. The human recipe closes two point
one. That winner is mlp_behemoth_lite. Its parent, mlp_behemoth, spent
more bytes than the budget allows, so it does not count. The same pattern
held on a second model pair, SmolLM2.

## 2:27-2:42 Checked, not just claimed

ON SCREEN: Two short lines, one at a time: the Muse Spark judging record
citing its result files; then the audit line, 41 of 41 checks passed.

NARRATION:
Then we checked ourselves. Muse Spark judged every headline claim and
had to cite the result file behind each one. And a quantum computer's
random numbers picked the audit sample: all forty-one audit checks
passed.

## 2:42-3:00 Close: a chip, not a note

ON SCREEN: The base model with the small patch file next to it. End card:
repo address.

NARRATION:
This is not a memory file. A memory file is a note the model reads; this
patch is a small chip swapped inside the machine, numbers that change the
model's math. Fine-tunes you can carry and swap like files: one base
model, many small behaviors.

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
