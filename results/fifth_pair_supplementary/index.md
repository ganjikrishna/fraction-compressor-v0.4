# Fifth pair (Qwen2.5-7B): supplementary scale probe

Supplementary exploratory material, published for transparency. This folder is not part of the submission claim set, and no four-pair result depends on anything in it.

**The reference inverts on this pair.** On the held-out 96-question battery, the full fine-tune delta scores below the base model on mean target logprob (full delta -15.974, base -6.916), and it stays below base on the corrected battery as well (full delta -8.634, base -8.043). With the reference inverted, gap_closed is null at 7B: no fraction figure is defined for this pair, and none is claimed for any 7B configuration.

**A shrinkage control explains the patch's profile.** A plain copy of the full delta turned down to 25% strength reproduces and exceeds the selected factored configuration's (down_king) profile on both batteries (corrected battery: scaled copy -7.096 vs down_king -7.556; original battery: -6.360 vs -8.694). The apparent 7B skill of the factored patch is therefore explained as mostly a regularization effect of shrinking the delta, not as the factored format reproducing fine-tune behavior. As a score-and-size fact in the same comparison: the factored down_king patch file is 86,401,024 bytes and scores -8.694 on the original battery, where the plain 1-bit baseline file is 951,911,192 bytes and scores -11.378.

**Yardstick note, with the same prominence.** On Oct 29 an eval fix removed a chat-template echo artifact from this pair's battery (the prompt-restart echo was eliminated). Under the corrected battery the full delta's deficits shrank, and the inversion stated above remained: the full delta still does not score above the base on mean target logprob on any subset, on either battery.

**Behavioral numbers only.** First-token accuracy on the corrected battery, with base and full delta beside the patch: overall, base 0.052, full delta 0.333, down_king 0.313; on the math subset, base 0.031, full delta 0.750, down_king 0.750, and down_king's generations carry the right content but trail junk tokens. On the knowledge subset no configuration shows a gain on either battery.

**The run.** Oct 28-29, 2026: the project's factored 1-bit patch format on Qwen2.5-7B base vs Qwen2.5-7B-Instruct, executed with layer-by-layer streaming in the project's own NumPy runtime on a CPU-only machine with 11 GB of RAM, the 7B model never held whole in memory. down_king is the configuration carried forward from the Stage 2 selection (selection score -9.584). The uniform rank-32 configuration at a near-identical size (86,499,328 bytes) scored -13.158 on the original battery. The per-item logprob arrays (.logp.npz) behind the JSON files are not included in this folder.

## Contents

- `fifth_pair_yardstick_and_regularization.md` — the follow-up report: corrected battery, scaled-delta controls, generation sanity eval, validation.
- `fifth_pair_heldout96.json` — the original held-out 96 eval (chat format), all configurations, per item.
- `fifth_pair_stage2.json` — the Stage 2 selection run that carried down_king forward.
- `fifth_pair_recompute.json` — independent recomputation record for the held-out 96 eval.
- `fifth_pair_yardstick_eval_chat_*.json` — per-configuration evals, original battery.
- `fifth_pair_yardstick_eval_corrected_*.json` — per-configuration evals, corrected battery.
- `fifth_pair_yardstick_gen.json` — the generation sanity eval rows.
- `fifth_pair_yardstick_recompute.json` — recomputation record for the yardstick numbers.
- `spark_judging_7b.json`, `spark_judging_7b.md` — Muse Spark claim judging of the original 7B run.
- `fifth_pair_yardstick_spark_gen_judging.json` — Muse Spark judging of the generation sanity eval.
- `fifth_pair_yardstick_spark_interpretation.json`, `fifth_pair_yardstick_spark_interpretation.md` — Muse Spark's interpretation record for the yardstick and regularization results.
