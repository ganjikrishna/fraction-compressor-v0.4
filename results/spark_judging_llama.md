# Muse Spark judging addendum: Llama Phase 3 (third model pair)

Date: 2026-10-27. Judge: Muse Spark 1.3 via the Meta Model API (4267 tokens: 1028 prompt, 3239 completion incl. 2614 reasoning). Spark judged the headline claims for the Llama 3.2 1B pair against the numbers copied at full precision from results/third_pair_stage2.json and results/third_pair_heldout96.json, and had to cite its source file for every verdict.

## Verdicts

### Claim A: SUPPORTED

On the combined 96 fresh items, the byte-fair variant no_embed_mlp_spread_balanced (24,515,584 B, under the 25,143,296 B budget) beats uniform_rank32: gap_closed 0.159 (15.9%) vs -0.076 (-7.6%), factored mean logprob -12.714 vs -14.201.

- Cited file: results/third_pair_heldout96.json
- Values relied on: balanced 24515584 bytes, gap_closed 0.15852079567397595, mean -12.714218663974016 vs uniform_rank32 25143296 bytes, gap_closed -0.07636110027783072, mean -14.20128408199294; budget 25143296
- Note: Balanced is under budget and higher on both gap_closed and mean logprob than uniform_rank32.

### Claim B: SUPPORTED

The byte-fair variant wins on both halves of the fresh set: heldout24 gap_closed 0.200 vs uniform -0.017; heldout72_new 0.148 vs uniform -0.091.

- Cited file: results/third_pair_heldout96.json
- Values relied on: heldout24: balanced gap_closed 0.200373434383912 vs uniform -0.016714667787171608; heldout72_new: balanced 0.14817956351361586 vs uniform -0.09109894297869517
- Note: Balanced gap_closed exceeds uniform on both fresh subsets.

### Claim C: SUPPORTED

uniform_rank32's combined-96 factored mean logprob (-14.201) is below the base model's own score (-13.718): on this pair the human recipe makes fresh-item scores worse than no patch at all.

- Cited file: results/third_pair_heldout96.json
- Values relied on: uniform_rank32 mean -14.20128408199294 vs base mean -13.717832809408115; higher logprob is better
- Note: Uniform_rank32 mean is more negative than base, so worse than no patch.

### Claim D: SUPPORTED

The Stage 2 winner no_embed_mlp_spread (gap_closed 0.403 on the 24 probe questions) is byte-unfair: 34,690,048 bytes is +38.0% over the 25,143,296-byte budget; uniform's Stage 2 gap_closed is 0.088.

- Cited file: results/third_pair_stage2.json
- Values relied on: no_embed_mlp_spread gap_closed 0.4029778971569745, 34690048 bytes vs budget 25143296 bytes (+38.0%); uniform_rank32 gap_closed 0.08834323479864378, 25143296 bytes
- Note: Stage 2 winner exceeds the byte budget by ~38% while uniform gap is 0.088.

### Claim E: NOT SUPPORTED

No factored config on the 96 outscores the full delta (best factored -12.123 vs full -7.387), every factored gap_closed on this pair is below 1.0, and first-token accuracy stays low for every factored config (best 3.1% vs full delta 21.9%); so gap_closed remains a true recovery fraction on this pair, and overall recovery here (byte-fair 15.9%) is weaker than on pair 1 (Qwen byte-fair 23.2% on the same 96).

- Cited file: results/third_pair_heldout96.json
- Values relied on: best factored mean -12.12275284734357 vs full -7.386713026876891; gaps 0.15852079567397595, -0.07636110027783072, 0.25194278687724053; accuracies best 0.03125 vs full 0.21875
- Note: In-pair recovery facts match, but the pair-1 Qwen 23.2% comparison has no numbers provided to judge against.
- Resolution: Investigated the same day: the NOT SUPPORTED is a scope limit, not a factual dispute. Spark confirmed every in-pair fact in claim E (best factored -12.123 vs full -7.387, all gap_closed below 1.0, best factored accuracy 3.1% vs full 21.9%) and objected only that the pair-1 Qwen 23.2% figure was not in the numbers it was shown. That figure stands on its own records: results/alien_sweep_heldout96.json (gap_closed 0.231923) and the earlier Spark judging addendum, claim A, which that same judge marked SUPPORTED. The README wording therefore keeps the in-pair facts and the cross-pair comparison, each resting on its own pair's records.

## Spark's summary (verbatim)

Claims A-D are fully supported by the cited files, while E fails because its cross-pair Qwen comparison is outside the provided numbers.

## Prompt sent (verbatim)

You are an independent judge for a model-compression benchmark. Judge each claim ONLY against the numbers given below, which are copied at full precision from the cited result files. For each claim, reply with a verdict (SUPPORTED or NOT SUPPORTED), the source file the claim rests on, the exact values you relied on, and a one-sentence note. Do not soften caveats. gap_closed = (factored - base) / (full - base) on mean target logprob; higher logprob is better. The byte budget is the human uniform rank-32 recipe's real-shape price.

Pair 3: Meta Llama 3.2 1B base vs Instruct. Budget (uniform_rank32 real bytes): 25,143,296.

From results/third_pair_heldout96.json (96 fresh questions):
- base overall: mean target logprob -13.717832809408115, first-token accuracy 0.010416666666666666
- full delta overall: mean target logprob -7.386713026876891, first-token accuracy 0.21875
- no_embed_mlp_spread_balanced (byte-fair variant): 24,515,584 bytes; combined96 factored mean logprob -12.714218663974016, gap_closed 0.15852079567397595, accuracy 0.020833333333333332; heldout24 subset gap_closed 0.200373434383912; heldout72_new subset gap_closed 0.14817956351361586
- uniform_rank32: 25,143,296 bytes; combined96 factored mean logprob -14.20128408199294, gap_closed -0.07636110027783072, accuracy 0.0; heldout24 subset gap_closed -0.016714667787171608; heldout72_new subset gap_closed -0.09109894297869517
- no_embed_mlp_spread (Stage 2 winner, byte-unfair): 34,690,048 bytes; combined96 factored mean logprob -12.12275284734357, gap_closed 0.25194278687724053, accuracy 0.03125
- full delta at fp16: 2,471,493,632 bytes

From results/third_pair_stage2.json (24 pre-existing probe questions):
- base overall mean logprob -13.88544512286745; full delta -7.3985802620448835
- no_embed_mlp_spread: factored mean logprob -11.271381962111702, gap_closed 0.4029778971569745, 34,690,048 bytes
- uniform_rank32: factored mean logprob -13.31237449736073, gap_closed 0.08834323479864378, 25,143,296 bytes

CLAIMS:
A. On the combined 96 fresh items, the byte-fair variant no_embed_mlp_spread_balanced (24,515,584 B, under the 25,143,296 B budget) beats uniform_rank32: gap_closed 0.159 (15.9%) vs -0.076 (-7.6%), factored mean logprob -12.714 vs -14.201.
B. The byte-fair variant wins on both halves of the fresh set: heldout24 gap_closed 0.200 vs uniform -0.017; heldout72_new 0.148 vs uniform -0.091.
C. uniform_rank32's combined-96 factored mean logprob (-14.201) is below the base model's own score (-13.718): on this pair the human recipe makes fresh-item scores worse than no patch at all.
D. The Stage 2 winner no_embed_mlp_spread (gap_closed 0.403 on the 24 probe questions) is byte-unfair: 34,690,048 bytes is +38.0% over the 25,143,296-byte budget; uniform's Stage 2 gap_closed is 0.088.
E. No factored config on the 96 outscores the full delta (best factored -12.123 vs full -7.387), every factored gap_closed on this pair is below 1.0, and first-token accuracy stays low for every factored config (best 3.1% vs full delta 21.9%); so gap_closed remains a true recovery fraction on this pair, and overall recovery here (byte-fair 15.9%) is weaker than on pair 1 (Qwen byte-fair 23.2% on the same 96).

Reply in exactly this JSON shape, no markdown fences:
{"verdicts": [{"claim_id": "A", "verdict": "SUPPORTED", "cited_file": "results/...", "values_relied_on": "...", "note": "..."}], "summary": "one or two sentences"}

## Raw reply (verbatim)

{"verdicts": [{"claim_id": "A", "verdict": "SUPPORTED", "cited_file": "results/third_pair_heldout96.json", "values_relied_on": "balanced 24515584 bytes, gap_closed 0.15852079567397595, mean -12.714218663974016 vs uniform_rank32 25143296 bytes, gap_closed -0.07636110027783072, mean -14.20128408199294; budget 25143296", "note": "Balanced is under budget and higher on both gap_closed and mean logprob than uniform_rank32."}, {"claim_id": "B", "verdict": "SUPPORTED", "cited_file": "results/third_pair_heldout96.json", "values_relied_on": "heldout24: balanced gap_closed 0.200373434383912 vs uniform -0.016714667787171608; heldout72_new: balanced 0.14817956351361586 vs uniform -0.09109894297869517", "note": "Balanced gap_closed exceeds uniform on both fresh subsets."}, {"claim_id": "C", "verdict": "SUPPORTED", "cited_file": "results/third_pair_heldout96.json", "values_relied_on": "uniform_rank32 mean -14.20128408199294 vs base mean -13.717832809408115; higher logprob is better", "note": "Uniform_rank32 mean is more negative than base, so worse than no patch."}, {"claim_id": "D", "verdict": "SUPPORTED", "cited_file": "results/third_pair_stage2.json", "values_relied_on": "no_embed_mlp_spread gap_closed 0.4029778971569745, 34690048 bytes vs budget 25143296 bytes (+38.0%); uniform_rank32 gap_closed 0.08834323479864378, 25143296 bytes", "note": "Stage 2 winner exceeds the byte budget by ~38% while uniform gap is 0.088."}, {"claim_id": "E", "verdict": "NOT SUPPORTED", "cited_file": "results/third_pair_heldout96.json", "values_relied_on": "best factored mean -12.12275284734357 vs full -7.386713026876891; gaps 0.15852079567397595, -0.07636110027783072, 0.25194278687724053; accuracies best 0.03125 vs full 0.21875", "note": "In-pair recovery facts match, but the pair-1 Qwen 23.2% comparison has no numbers provided to judge against."}], "summary": "Claims A-D are fully supported by the cited files, while E fails because its cross-pair Qwen comparison is outside the provided numbers."}
