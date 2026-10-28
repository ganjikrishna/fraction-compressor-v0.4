# Grok outside review

Outside review by Grok (free account), pasted into the main chat by Vinay on Wed Oct 28, 2026. Grok had only the public repo (github.com/ganjikrishna/fraction-compressor-v0.4). Text below is verbatim.

---

Summary of Fraction Compressor v0.4
This is a research-style tool that turns an existing fine-tuned model into a very small "patch" file that can be loaded on top of the original base model.
Core idea
A fine-tune is treated as base model + delta (patch). Instead of storing the full high-precision delta (often nearly as big as the model itself), the tool:
• Factors the delta into a low-rank form.
• Keeps the structure as 1-bit signs.
• Stores the factors and scales.
• Runs the patch at inference time with two small matrix multiplies (Y = (X U) Vᵀ) without ever materializing the full weight matrix.
Result on the main benchmark pair (Qwen2.5-0.5B base → Instruct):
• Full delta ≈ 988 MB
• Rank-32 compressed patch ≈ 19.4 MB (~51× smaller)
• Effective cost around 0.28–0.31 bits per weight depending on layer.
You can hot-swap different patches on a single running base model in a fraction of a second.
How you use it
1 Point the script at a base model and its fine-tuned version (safetensors).
2 It computes the delta layer-by-layer and compresses it (uniform rank or a per-layer "recipe").
3 Verify the patch, then load it with the base for inference or live swapping.
Benchmarks (main results)
They compare three conditions on the same questions:
• Base only
• Base + full (uncompressed) patch
• Base + compressed patch
Metric is a log-score of how strongly the model prefers the correct answer. "Gap closed" = how much of the base→full improvement the compressed version recovers.
Key findings across four model pairs (Qwen 0.5B, SmolLM2-360M, Llama 3.2 1B, Qwen 1.5B):
• Smart per-layer rank allocation (found by an LLM search they call "Muse Spark") consistently beats a simple uniform rank-32 recipe.
• Best results recover ~15–23% of the score gap on fresh questions (sometimes more, sometimes the compressed version even slightly outperforms the full patch on the metric).
• Compression ratios stay high (roughly 50–80×) even at 1.5B scale.
• Important limitation: skills that are decided by the first token (e.g., "start outputting JSON or refuse") transfer poorly. A JSON-extraction fine-tune that works 9/10 times only works ~1/10 times under the compressed patch. Forcing the first token largely restores the behavior, showing the knowledge is mostly already in the base; the fine-tune mainly installs the "start" decision.
Positioning vs related work
Builds on ideas from BitDelta, Delta-CoMe, LittleBit, GraftLLM / SkillZip, etc., but claims originality in:
• Post-hoc conversion of existing fine-tunes (no retraining into the compressed form).
• LLM-driven search for per-layer rank recipes under a hard byte budget.
• Forced-multiply runtime that never rebuilds full matrices.
• Careful diagnosis of the first-token failure mode.
Strengths
• Extremely practical storage and switching story ("one base, many tiny behavior files").
• Honest about limits and failure modes.
• Thorough ablation and verification harness.
• Clean separation: offline compression once, cheap runtime use.
Weaknesses / open questions
• Recovered behavior is still only a fraction of the full fine-tune (most of the gap remains).
• First-token / gate-style skills are a real weak point.
• Relies on having both the base and the full fine-tune available to create the patch.
• Evaluation is mostly on log-score / preference strength rather than end-task accuracy or generation quality.
• The "Muse Spark" recipe search is interesting but still a bit opaque and not fully automated for arbitrary new pairs.
Overall feedback
This is a sharp, well-scoped research prototype that attacks a real pain point: the storage and distribution cost of many fine-tunes. The combination of 1-bit structure + factored low-rank + never-materializing runtime is elegant, and the honesty about the first-token limitation is refreshing.
It feels closest to a practical "skill packaging" layer rather than a general compression method. If the goal is "carry dozens of specialized behaviors on one base model with tiny, swappable files," it already looks useful. If the goal is "recover nearly the full fine-tune quality," it is not there yet (and the authors don't claim it is).
Most promising next steps would be:
• Better handling of first-token / decision-boundary skills.
• Scaling the recipe search and making it more automatic.
• Measuring actual generation quality and task accuracy more broadly.
• Seeing how well it works when the fine-tune is far from the base (heavy domain shift, long training, etc.).
Solid, focused work with clear experiments and good documentation. Worth watching.

---

## Notes on accuracy

- Its numbers match the repo's records: 988 MB to 19.4 MB (~51×), ~15–23% of the score gap recovered on fresh questions, and the 9/10 vs ~1/10 JSON-extraction contrast.
- One gloss: "consistently beats uniform" omits the byte-fair caveat, which the README states. The headline recipe is the byte-fair lite variant; its parent recipe was over budget.
- Its weakness list matches the project's own published limits: first-token gate skills, log-score rather than end-task accuracy, recipe search not fully automated, and reliance on having both the base and the full fine-tune.
