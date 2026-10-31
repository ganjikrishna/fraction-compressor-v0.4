# Fifth pair (Qwen2.5-7B): yardstick fix and regularization test

Date: October 29, 2026. Local results only (no publication, no repo edits beyond this results folder).

Scope: two follow-up questions on the fifth pair (Qwen2.5-7B base vs Qwen2.5-7B-Instruct full fine-tune, and the 86 MB down_king patch). Part A re-measures the held-out 96 battery after removing the chat-template artifact proven in `fifth_pair_template_diagnostic.json`, and adds a 12-prompt generation sanity eval. Part B tests Gemini's regularization hypothesis (`gemini_validation_7b.md`) against scaled full deltas (alpha 0.25 and 0.5), with the interpretation panel's added checks folded in (echo rate, per-item KL, helped/hurt buckets, scaling curve with agreement). Every number below was recomputed independently from per-item rows by `validation_helpers/y7_analyze.py`: 37 of 37 checks pass.

## Plain-words summary

**Question 1: is the yardstick fixed, and what recovery can honestly be claimed at 7B?**

Partly fixed. The corrected battery (raw completion for knowledge and instruction, chat format kept for math) removes the template artifact: the prompt-restart echo rate for every delta config drops from 8.3% on the chat battery to 0.0%, and the full fine-tune's huge knowledge and instruction deficits shrink from -15.6 and -11.0 points (versus base, chat battery) to -1.0 and -0.2. But the full fine-tune still does not beat the base model on mean target log-probability on any subset, on either battery. So no gap-closed recovery percentage can honestly be claimed at 7B on this metric; anyone quoting one would be quoting a number whose denominator (full minus base) is negative everywhere.

What can be claimed, per subset, from the other two measurements:

- Math: the fine-tune's gain is real and large in behavior. First-token accuracy goes from 0.03 (base) to 0.75 (full), and down_king keeps all of it (0.75) at 86 MB. Mean logprob still favors base (-4.61 vs -5.20 for full) because scoring is against one fixed answer wording.
- Instruction: first-token accuracy doubles (0.13 base, 0.25 full, 0.19 down_king). In generation, full passes 11 of 12 sanity prompts to down_king's 9 and base's 7 (script heuristics; Spark judging: 11, 8, 9).
- Knowledge: no config shows a gain. First-token accuracy under raw completion is 0.00 for every config (a format floor: the authored answers start with tokens no raw completion leads with), and logprob favors base in both formats. The two batteries bracket the size of the deficit (-15.6 chat, -1.0 raw); they agree on the sign.

The honest one-liner: at 7B, the logprob yardstick can only say the patch and the fine-tune sit at or below base against fixed target wordings; the behavioral measures (first-token choice, free generation) show the fine-tune clearly ahead and down_king keeping most of that lead, math fully, instruction partly, knowledge not measurably.

**Question 2: regularization (shrinkage) or movement toward the fine-tune?**

The evidence supports Gemini's regularization hypothesis as the explanation for why down_king beats the full delta, and the "movement" claim narrows to a weaker statement. Turning the full delta down to 25% strength reproduces and exceeds down_king's profile on both batteries: better overall score than the patch (corrected -7.10 vs -7.56; chat -6.36 vs -8.69), better on math (-2.17 vs -3.16), the same helped/hurt shape (it wins by avoiding the items the fine-tune hurt, even more strongly than the patch does), and equal or better agreement with the fine-tune. Neither patch beats the scaling curve at matched agreement, so the panel's strong denoiser signature is absent; down_king actually sits slightly below the curve (its corrected overall score is below both the 0.25 and 0.5 scaling points, a correction Spark caught and we accept). What survives of "movement": down_king's output distribution is much closer to the fine-tune than to base exactly where the fine-tune moved most (math: KL 0.17 to full vs 1.62 to base), its per-item logprob correlation with the fine-tune (0.93) matches the 0.5 scaling, and it does this as an 86 MB artifact, while a scaled delta is only a diagnostic (building one requires keeping the full 15 GB delta). Movement describes where the patch's outputs sit; shrinkage explains why it outscores the full fine-tune.

## Part A: the corrected battery

Protocol: same 96 held-out items as `fifth_pair_heldout96.json`. Corrected battery scores knowledge and instruction items as raw completions (no chat template) and keeps the chat format for math (the diagnostic showed raw math is poor for both models). Six configs: base, full delta, uniform rank-32 (86,499,328 B), down_king (86,401,024 B), full delta scaled by 0.25 and by 0.5 (Part B diagnostics). Mean target log-probability (higher is better):

Corrected battery:

| config | knowledge | instruction | math | overall |
|---|---|---|---|---|
| base | -12.154 | -7.370 | -4.606 | -8.043 |
| full delta | -13.176 | -7.527 | -5.200 | -8.634 |
| uniform rank-32 | -12.485 | -6.753 | -3.260 | -7.499 |
| down_king | -12.586 | -6.924 | -3.160 | -7.556 |
| full x0.25 | -12.341 | -6.782 | -2.166 | -7.096 |
| full x0.50 | -12.567 | -6.679 | -3.010 | -7.419 |

Original chat battery (re-run; reproduces the published numbers exactly, see Validation):

| config | knowledge | instruction | math | overall |
|---|---|---|---|---|
| base | -3.977 | -12.164 | -4.606 | -6.916 |
| full delta | -19.539 | -23.182 | -5.200 | -15.974 |
| uniform rank-32 | -10.327 | -25.888 | -3.260 | -13.158 |
| down_king | -9.117 | -13.804 | -3.160 | -8.694 |
| full x0.25 | -5.848 | -11.066 | -2.166 | -6.360 |
| full x0.50 | -9.301 | -12.936 | -3.010 | -8.416 |

First-token accuracy, corrected battery (chat battery in parentheses for overall):

| config | knowledge | instruction | math | overall |
|---|---|---|---|---|
| base | 0.000 | 0.125 | 0.031 | 0.052 (0.073) |
| full delta | 0.000 | 0.250 | 0.750 | 0.333 (0.312) |
| uniform rank-32 | 0.000 | 0.188 | 0.750 | 0.313 (0.323) |
| down_king | 0.000 | 0.188 | 0.750 | 0.313 (0.344) |
| full x0.25 | 0.000 | 0.188 | 0.750 | 0.313 |
| full x0.50 | 0.000 | 0.219 | 0.750 | 0.323 |

Readings:

- Full minus base per subset, corrected: knowledge -1.02, instruction -0.16, math -0.59. The same gaps on the chat battery: -15.56, -11.02, -0.59 (math identical by construction; the recompute verifies math rows match across batteries to 1.8e-05). Most of the chat-battery deficit was template artifact, but the sign never flips, so gap_closed is null for every config on both batteries.
- Echo (panel check 1): restart-echo rate (the model's top first token restarts the raw user prompt and is not the target). Corrected: 0.000 for full, uniform, down_king, x0.25, x0.50; base 0.052 (all five cases are math items, which keep the chat format). Chat battery: 0.083 for every delta config, 0.208 for base. On the chat battery the full fine-tune's echo items average -18.34 against -15.76 for its non-echo items; the artifact is real, it is concentrated in the delta configs' chat scores, and the corrected battery removes it. The softer any-echo rate (top token appears anywhere in the prompt) is 0.07 to 0.09 corrected for all configs, base included, so it does not separate configs.
- Knowledge bracket: the 96 items were authored as chat questions with full-sentence answers, so raw completion is also a mismatched format for them, in the opposite direction (base knowledge: -3.98 chat vs -12.15 raw). Neither battery is a neutral knowledge measure; both put full below base.
- Generation sanity: 12 fresh prompts (disjointness from the Signet 24, held-out 96, LoRA distill prompts, and the demo scan asserted in the script), chat format, greedy, up to 40 tokens, through the same streamed runtime. Script heuristics vs Muse Spark judging (independent, `fifth_pair_yardstick_spark_gen_judging.json`):

| config | heuristic pass | Spark pass |
|---|---|---|
| base | 7/12 | 9/12 |
| full delta | 11/12 | 11/12 |
| down_king | 9/12 | 8/12 |

  Both judges fail the reversed-word prompt for every config, and both pass full on everything else. Base fails format-constrained instruction prompts and (heuristics) two math prompts; Spark was more lenient on base's math wording. down_king's generations carry the right content (Canberra, carbon dioxide, 6, Austen, 28, 37, 42, 5) but often trail junk tokens after the answer ("6_Pods", a stray ".UrlParser", non-English fragments), the same tail corruption Gemini flagged in the stream demo; Spark failed it on three format prompts for exactly that, heuristics on two. down_king also needed the full 40-token cap to stop (base did too; full stopped in 9 steps).

## Part B: scaled deltas vs the patch

Scaling curve on the corrected battery, with agreement reported beside every score (panel check 3):

| alpha | config | overall | knowledge | instruction | math | agreement with full | corr with full |
|---|---|---|---|---|---|---|---|
| 0.00 | base | -8.043 | -12.154 | -7.370 | -4.606 | 0.510 | 0.634 |
| 0.25 | full x0.25 | -7.096 | -12.341 | -6.782 | -2.166 | 0.865 | 0.842 |
| 0.50 | full x0.50 | -7.419 | -12.567 | -6.679 | -3.010 | 0.906 | 0.929 |
| 1.00 | full delta | -8.634 | -13.176 | -7.527 | -5.200 | 1.000 | 1.000 |
| patch | down_king | -7.556 | -12.586 | -6.924 | -3.160 | 0.854 | 0.928 |
| patch | uniform rank-32 | -7.499 | -12.485 | -6.753 | -3.260 | 0.865 | 0.925 |

- Scores: the score peak sits at alpha 0.25, above both endpoints (base and full). down_king and uniform rank-32 also beat both endpoints on instruction and math, but both score below the 0.25 point overall and below both scaling points overall (down_king); neither patch beats the curve (`patch_vs_curve` false on both batteries). On the chat battery the same ordering holds (x0.25 -6.36 is the best overall score of any config, ahead of base -6.92).
- Agreement/correlation: down_king's agreement with the full fine-tune (0.854) is essentially the 0.25 scaling's (0.865) and below the 0.5 scaling's (0.906); its correlation (0.928) matches the 0.5 scaling (0.929) and beats the 0.25 (0.842). It does not track the fine-tune distinctly better than every shrinkage; on correlation it matches one.
- KL (panel check 2), corrected battery, mean per-item KL over scored answer positions (full's own distance to base is 0.829 for scale):

| config | KL to full | KL to base | items closer to full |
|---|---|---|---|
| down_king | 0.281 | 0.643 | 0.40 |
| uniform rank-32 | 0.356 | 0.778 | 0.53 |
| full x0.25 | 0.625 | 0.493 | 0.24 |
| full x0.50 | 0.166 | 0.630 | 0.56 |

  Per bucket, down_king is far closer to full on math (0.166 vs 1.617 to base) and closer to base on knowledge (0.057 to full vs 0.013 to base) and instruction (0.621 vs 0.298). The mean is carried by math, where the fine-tune actually moved; on most items the patch still sits nearer base. First-token KL shows the same pattern (math 0.31 to full vs 3.40 to base).
- Helped/hurt (Opus check 1), corrected battery; helped = items where full beats base per item (46), hurt = full below base (50):

| config | agreement, helped | agreement, hurt | score minus full, helped | score minus full, hurt |
|---|---|---|---|---|
| down_king | 0.848 | 0.860 | -0.37 | +2.41 |
| uniform rank-32 | 0.870 | 0.860 | -0.39 | +2.54 |
| full x0.25 | 0.870 | 0.860 | -0.57 | +3.48 |
| full x0.50 | 0.891 | 0.920 | -0.28 | +2.59 |

  Agreement is flat across buckets for every config, not concentrated where the fine-tune helped. Every config wins over full almost entirely by losing less in the hurt bucket, and the plain 0.25 shrinkage does it most. On the chat battery the shape is the same and larger (down_king +11.52 in the hurt bucket; x0.25 +15.29). This is the filtering signature, and it is not specific to the patch.
- Denoiser criterion (panel check 3): as alpha rises 0.25 to 0.5 to 1.0, agreement with full rises (0.865, 0.906, 1.0) and score falls (-7.10, -7.42, -8.63). A denoiser would sit above that curve (patch-level agreement with a better score than any curve point at that agreement); down_king sits slightly below it. Signature absent.
- Proposed, not run (Opus check 2): projecting the full delta into down_king's kept subspace versus its complement and scoring each half. This did not fit the queued compute honestly: it needs a new build of two projected delta sets (about 15 GB) applied through a stored-delta runtime path this study has not validated, plus a kept + complement = full identity check, plus about five more gated eval passes. Recorded here as the decisive follow-up if the mechanism question is reopened; the design gate is that the two halves must sum back to the full delta within tolerance before any scoring counts.

Decision, per the pre-registered logic: a scaled full delta reproduces down_king's profile (beats full on math, same subset pattern, similar agreement), so the regularization/shrinkage explanation gains real support and the "moves toward the fine-tune" claim narrows to the distributional statement in B3. It is a mixed result only in that weaker sense; on the mechanism question itself the evidence is one-directional.

## Validation

- Independent recomputation: `y7_analyze.py` recomputes every number from the per-item rows and log-probability sidecars in `fifth_pair_yardstick_eval_{battery}_{config}.json` (+ `.logp.npz`). 37 of 37 checks pass, including aggregate recompute for all 12 eval files, sidecar consistency (258 scored positions per corrected file, 96 per chat file), math-row identity across batteries, and KL(full||full) = 0.
- Continuity: the chat re-run matches the published `fifth_pair_heldout96.json` overall means exactly for all six configs (for example base -6.915776, full -15.974108, down_king -8.693891) and per item to 0.00e+00 for uniform_rank32 and down_king (the two configs with published per-item rows).
- Muse Spark judging (Meta Model API, muse-spark-1.3; `fifth_pair_yardstick_spark_interpretation.md`): 12 interpretation claims, 9 supported, 3 partly supported, 0 unsupported. Headline: "Battery numbers internally cohere and support shrinkage over strong-denoiser account, aside from limited per-item continuity evidence and B2 between-scalings misstatement."
- Disagreements and corrections, recorded plainly:
  - Spark caught a real error in draft claim B2: down_king's corrected overall score (-7.556) is below both scaling points (-7.096 and -7.419), not between them. Accepted; this report uses the corrected wording, and the correction strengthens the Part B conclusion.
  - A1 partly supported: per-item exactness is evidenced for the two patch configs (the ones with published per-item rows); the other four configs' continuity is aggregate-level. Accepted as scoped.
  - A4 partly supported: the accuracy/logprob reversal is measured, but "the logprob deficit is a phrasing-match penalty" is an interpretation of that pattern, not a separately measured quantity; and the knowledge floor (0.000 for all configs) caps any gain claim there. The summary above is worded accordingly.
  - Generation judging disagreements: Spark passes base on two math prompts the heuristic fails (wording leniency) and fails down_king on the three-animals prompt the heuristic passes (junk suffix after the third item). Both counts are reported side by side in Part A; neither was averaged away.
- API usage for this investigation: 2 Muse Spark calls, 13,328 tokens total (5,402 generation judging + 7,926 interpretation judging), logged in `api_usage_log.jsonl` with purpose "7B yardstick fix". No other paid API calls.

## Files

- `fifth_pair_yardstick_eval_{corrected,chat}_{base,full_delta,uniform_rank32,down_king,full_a025,full_a05}.json` and matching `.logp.npz` sidecars: per-item rows and scored-position log-probabilities.
- `fifth_pair_yardstick_gen.json`: 36 generations (12 prompts x 3 configs) with programmatic expectations.
- `fifth_pair_yardstick_recompute.json`: independent recomputation, all sections cited above.
- `fifth_pair_yardstick_spark_gen_judging.json`, `fifth_pair_yardstick_spark_interpretation.json` / `.md`: Spark judging records.
- Scripts: `results/validation_helpers/y7_eval.py`, `y7_gen.py`, `y7_analyze.py`, `y7_spark_judging.py`, `run_all_v2.sh`.

## Run notes

Flash compute ran under a gate that kept it clear of the LoRA baseline job (two consecutive clear checks before each job). All 12 eval jobs finished with rc=0 (about 4 to 8 minutes each). The generation job is the slow one in this runtime (full-sequence re-streaming per token, no KV cache): base 40 steps in 2,889 s, full 9 steps in 966 s, down_king 40 steps in 3,518 s. It was interrupted once at 06:11 ET (about 36 steps into the base config, no output written) to let the chat battery proceed, after a per-config checkpoint patch to `y7_gen.py`; the rerun completed from checkpoints with no config repeated. One duplicate generation process was started by mistake during the relaunch and was killed within minutes; the surviving process's checkpoints are the ones in the results file, and its base and full configs match the checkpoint file the duplicate had loaded (resume log records the skip), so no generation was double-counted.
