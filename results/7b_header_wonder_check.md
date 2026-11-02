# 7B supplementary header guardrail check — Muse Wonder (substitute validator)

- Date: 2026-10-31 (UTC 18:51)
- Why: the Glimmer guardrail chunk on this header returned empty content, leaving no Glimmer guardrail verdict. Per Vinay's instruction (Oct 31, 2026), Wonder substitutes for Glimmer when Glimmer is not working.
- Validator: muse-wonder-1.0 via Meta Model API, reasoning_effort low, max_tokens 8192.
- Checked file: results/fifth_pair_supplementary/index.md, against the panel guardrails in results/7b_push_panel.md.
- Usage: 1,445 prompt + 1,698 completion (1,213 reasoning) = 3,143 tokens. Logged in results/api_usage_log.jsonl, purpose "7B header guardrail check wonder substitute".

## Verbatim verdict

1. PASS — "Supplementary exploratory material, published for transparency. This folder is not part of the submission claim set, and no four-pair result depends on anything in it."
2. PASS — "On the held-out 96-question battery, the full fine-tune delta scores below the base model on mean target logprob (full delta -15.974, base -6.916), and it stays below base on the corrected battery as well (full delta -8.634, base -8.043). With the reference inverted, gap_closed is null at 7B: no fraction figure is defined for this pair, and none is claimed for any 7B configuration."
3. PASS — "A plain copy of the full delta turned down to 25% strength reproduces and exceeds the selected factored configuration's (down_king) profile on both batteries (corrected battery: scaled copy -7.096 vs down_king -7.556; original battery: -6.360 vs -8.694)." / "On Oct 29 an eval fix removed a chat-template echo artifact from this pair's battery (the prompt-restart echo was eliminated)."
4. PASS — "As a score-and-size fact in the same comparison: the factored down_king patch file is 86,401,024 bytes and scores -8.694 on the original battery, where the plain 1-bit baseline file is 951,911,192 bytes and scores -11.378."
5. PASS — "on the math subset, base 0.031, full delta 0.750, down_king 0.750, and down_king's generations carry the right content but trail junk tokens."
6. PASS — "First-token accuracy on the corrected battery, with base and full delta beside the patch: overall, base 0.052, full delta 0.333, down_king 0.313; on the math subset, base 0.031, full delta 0.750, down_king 0.750, and down_king's generations carry the right content but trail junk tokens."
7. PASS — "With the reference inverted, gap_closed is null at 7B: no fraction figure is defined for this pair, and none is claimed for any 7B configuration."
OVERALL: PASS
