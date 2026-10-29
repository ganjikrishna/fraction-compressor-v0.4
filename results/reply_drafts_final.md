# Public reply drafts, final (panel-reviewed, pending Vinay's posting decision)

Status: drafted and panel-reviewed Thu Oct 29, 2026. Nothing posted, nothing pushed. Local only.
Review record: results/reply_drafts_review.md.

---

## Reply A: Discord #office-hours, MMS-TTS thread

Tested facebook/mms-tts-eng on a real script. Two things worth knowing: the model license is CC-BY-NC 4.0 (attribution, non-commercial use only), even though organizers count MMS as a Meta model usable as voice, and the quality is rough on names and technical terms. A Whisper re-transcription of our sample, indicative only since Whisper adds errors of its own, misheard the speaker's name and several key terms. It also runs fast and flat, about 172 words a minute in our test, with sentences running together, so budget time for pacing if you use it.

---

## Reply B: repo results document answering the LoRA question (saved for a later push decision)

# We ran the matched-byte LoRA baseline

In its review of this repo, Nemotron asked why we compress a finished fine-tune's delta at all, instead of training a LoRA adapter at the same byte budget. Fair question. We ran it.

## Design

The adapter is LoRA, rank 17, on all seven block linears in all 24 blocks of the Qwen2.5-0.5B pair, no embedding adapter, exported in fp16 at 18,696,192 bytes. That is under both factored patch budgets (uniform 19,434,496 B, lite 19,358,176 B). The original Instruct training data is not available, so the adapter was distilled from the full fine-tune itself: soft forward-KL training (temperature 1) on the teacher's own answers to 1,500 fresh prompts written by Muse Spark in the same three styles as the 96 eval questions (knowledge, instruction, math). Every training prompt was checked against the eval set; exact matches and items with token-set Jaccard of 0.7 or higher were rejected, so no eval item was trained on. We trained three seeds; headline numbers are the mean over seeds, and first-token accuracy is reported as the range across seeds.

## Results (same 96 questions, same scoring as every other result here)

| Config | Bytes | Mean logprob | Gap closed | First-token acc |
|---|---|---|---|---|
| base | 0 | -11.150 | 0.000 | 0.031 |
| full fine-tune | 987,922,432 | -8.543 | 1.000 | 0.167 |
| uniform factored patch | 19,434,496 | -11.096 | 0.021 | 0.010 |
| lite factored patch | 19,358,176 | -10.545 | 0.232 | 0.010 |
| distilled LoRA adapter | 18,696,192 | -7.599 ± 0.085 | 1.362 ± 0.033 | 0.167 to 0.177 |

Gap closed is the share of the base-to-full gap a config recovers; 1.000 is the full fine-tune by definition.

## What we think it means

On this probe set, the adapter beats both factored patches on mean logprob, and it posts a higher mean logprob than the full fine-tune it was distilled from. That overshoot is consistent with style specialization, and we do not claim it as anything stronger: the training prompts and the eval questions share an author and the same three styles, even though no item overlaps. The win is also a win in confidence across the whole answer, not in first picks: first-token accuracy only ties the full fine-tune, and both factored patches sit below the base model on that metric. The byte budgets match; the costs do not. The adapter needed 1,500 teacher generations and about 8 hours of training on a home CPU. The factored patch is a deterministic conversion of weights we already hold: no queries, no training, done in minutes. We make no claim beyond this probe distribution.

An out-of-style control, a fresh adapter distilled on differently styled prompts written by a different model, is running now; its result will be added here when it lands.

Validation: every stored row recomputes from the per-item data exactly; a zero adapter reproduces the base per-item logprobs bit for bit; dense and hooked forward passes agree to within 7.1e-06 per item; and Muse Spark judged 7 of 7 factual claims in the results file supported.
