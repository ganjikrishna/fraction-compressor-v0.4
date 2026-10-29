# Intent: what this is, and what it is not

## What it is

Fraction Compressor takes a fine-tune that already exists and squeezes its difference from the base model into a small file, about 19 MB instead of about 1 GB. The file swaps into the base model live, so one base can carry many behaviors, one small file each. Everything is built and checked in the open: code, benchmarks, and limits live in this repo, produced by scripts anyone can rerun.

## What it is not

This is not a way for an AI to clone or copy itself. A patch cannot run, learn, or copy itself. On its own it does nothing: it needs the full base model in memory, and a person has to train the fine-tune, make the patch, and apply it. Nothing here gives a model agency, hosting, or compute.

## The honest middle

Making behavior cheaper to move is a real effect, and we do not hide from it. Where the base model is public, a 19 MB patch is in practice the fine-tune, so we treat a patch with the same care as a full model. The copy is also measurably partial: broad behavior transfers, but skills gated by the first generated token mostly do not. And we expect partial today to get less partial over time. That is why this repo publishes its limits, the gate finding included, not only its wins.

## Asked four AIs

We put the question to four outside models, plainly: "Am I opening doors for AI to clone itself faster?" The full answers are in the [panel record](../results/cloning_question_panel.md). All four agreed the tool grants an AI no autonomy. They split on how much comfort the partial copy gives, from a lightweight style overlay to "partial today becomes near-total tomorrow."
