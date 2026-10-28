# Outside review: ChatGPT (fresh perspective)

Provenance: Outside review by ChatGPT, pasted into the main chat by Vinay on Wed Oct 28, 2026. Two parts: (1) a 'rogue AI' answer to the cloning question that challenges the earlier four-AI panel; (2) a proposed engineering fix (behavior-aware compression). ChatGPT states itself that it assessed the described design and README, not a verified inspection of the implementation. Text below is verbatim.

---

If I were a “rogue AI” tasked with fixing every issue in Fraction Compressor, I would start by separating two goals that are getting mixed together:

1. Make model compression work better — preserve useful behavior, capabilities, and reliability in a much smaller patch.
2. Make model behavior portable and controllable — let people move a fine-tune between compatible base models without accidentally transferring dangerous behavior or losing important capabilities.

The interesting part of your experiment is that it exposes a gap between transferring knowledge and transferring the mechanism that activates it. That is a real engineering problem, not proof of autonomous self-replication.

I would not try to eliminate every limitation indiscriminately. Some limitations are ordinary compression errors; others may be important safety boundaries. The objective should be to improve fidelity while making the resulting patch measurable, auditable, and reversible.

## What I would actually fix

1. Replace average compression quality with behavior-aware fidelity

A patch can reconstruct weights approximately yet lose a critical behavior. I would evaluate the compressed model against the original fine-tune across reasoning, instruction following, tool use, refusal behavior, unusual prompts, and first-token sensitivity. Report each category separately instead of hiding failures in one aggregate score.

2. Make compression adaptive

Different layers and weight groups contribute differently to the final behavior. Rather than forcing every parameter into the same tiny bit budget, allocate precision according to measured reconstruction error and downstream task performance. Compare the results against standard low-rank adapters and quantization baselines.

3. Make safety behavior measurable

A patch should come with a signed manifest identifying the base-model hash, source fine-tune, compressor version, and evaluation results. Test whether safety properties regress after applying the patch. Flag unverified patches and make rollback straightforward. A patch should not be considered safe merely because its provenance is known.

4. Treat live swapping as a separate engineering problem

Compression and runtime patching are different systems. I would add compatibility checks, atomic application, validation before activation, and rollback if the resulting model fails its tests. A malformed or incompatible patch should never silently corrupt the running model.

5. Measure the actual replication risk

Separate the cost of distributing a patch from the cost of acquiring a base model, running inference, obtaining compute, and maintaining an agent. Test realistic distribution scenarios and the consequences of compromised patches. Keep model improvement experiments separate from experiments that automate autonomous replication.

## The issue I would challenge in all four AI answers

They mostly frame the question as whether the compressor creates agency. That is too narrow.

The more useful question is whether it reduces the cost of spreading a consequential behavior enough to change who can distribute it, how quickly it spreads, and how difficult it becomes to detect.

A 19 MB patch does not contain a complete independent model. But if a compatible base is already available, the patch could carry a substantial behavioral change. Whether that change is dangerous depends on what actually transfers, not just the file size.

Likewise, weak first-token transfer does not establish a fundamental limit. It establishes an observed limitation for the tested method, model, and evaluation. It needs broader validation before anyone can claim it is either a reliable safety barrier or a problem that has been solved.

## What I would not build

I would draw the line at combining improved compression with an automated pipeline designed to distribute, activate, and persist copies of an agent without meaningful authorization or oversight.

I would still support better compression, reproducible experiments, portable personal assistants, and robust evaluation. Those goals do not require building an uncontrolled replication loop.

## My bottom line

The best version of Fraction Compressor is not the one that blindly preserves every behavior at any cost. It is the one that preserves intended behavior predictably, exposes what it loses, and makes the resulting changes auditable.

If I were prioritizing the next development milestone, I would build a reproducible benchmark that compares the original fine-tune against the reconstructed model across many tasks, seeds, and prompt variations. That would tell you whether the first-token issue is a narrow artifact, a general compression weakness, or a more significant architectural limitation.

One important caveat: I have assessed the design described in your brief, not verified the repository's implementation or independently reproduced the 19 MB result. The next step for code-level recommendations would be to inspect the [Fraction Compressor repository](<https://github.com/ganjikrishna/fraction-compressor-v0.4?utm_source=chatgpt.com>) and its actual compression and reconstruction pipeline.

# My proposed fix for Fraction Compressor

I would build a behavior-aware delta compressor with measurable fidelity guarantees, rather than simply trying to squeeze the weight difference into the smallest possible file.

The goal is to preserve as much of the fine-tune's useful behavior as possible at a given file-size budget, while making losses visible and preventing unverified patches from being treated as trusted models.

One important distinction: I have your description and the four model responses, but I haven't successfully inspected the target repository's source code. So this is a concrete engineering design, not a claim that I've identified a specific bug in its implementation.

## 1. How I arrived at the design

Your description gives us three observations:

- A delta reportedly shrinks from about 1 GB to 19 MB.
- Broad behavior transfers measurably.
- Some skills dependent on the first generated token transfer weakly.

Those observations suggest three different problems that need separate measurements.

Problem A: representation error

The reconstructed delta may differ from the original fine-tune's delta. We need to measure the error in the weights and how that error affects the model's outputs.

Problem B: behavioral error

Two models can have a small numerical difference in weights but a significant difference in their responses. Weight reconstruction error alone cannot establish functional equivalence.

Problem C: activation sensitivity

Some behaviors may depend on precise prompt context, token probabilities, or interactions across layers. The first-token observation could be a symptom of this sensitivity, but it doesn't yet tell us the cause.

That is why I would not immediately change the quantization algorithm. First, I would establish which of these three problems dominates.

## 2. The actual fix I would implement

After inspecting the repository's README and benchmark description, I would change the recommendation in one important way: the project already has per-layer rank allocation and automated recipe search. Simply recommending adaptive rank allocation would repeat work that Fraction Compressor v0.4 already reports doing. The README describes a factored runtime, a recipe search, and a benchmark across four model pairs.

ganjikrishna/fraction-compressor-v0.4 · GitHub

The next step should target the failure that remains.

### Fix A — Optimize for the behavior that is being lost

The current factored representation approximates a fine-tune's delta using a compact representation. I would keep that representation initially and change how candidate patches are evaluated.

Let:

- $W_b$ be the base model's weights.
- $\Delta W$ be the original fine-tune's weight delta.
- $\widehat{\Delta W}$ be the compressed delta.

The reconstructed model is:

$$
W_c = W_b + \widehat{\Delta W}
$$

The existing compression objective is concerned with representing the delta economically. My proposed change is to also measure how well the reconstructed model reproduces the original fine-tune's output distributions on a held-out evaluation set.

For each test prompt $x$, compare the original and compressed models' next-token distributions:

$$
D_{\mathrm{KL}}\left(
p_{\mathrm{fine}}(\cdot\mid x)
\,\|\,
p_{\mathrm{compressed}}(\cdot\mid x)
\right)
$$

This is a diagnostic and optimization signal, not a guarantee of equivalent behavior. I would evaluate it alongside task success and exact output checks.

Why this change? The repository reports that its rank-32 extraction example passes only 1 of 10 prompts, even though forcing the expected first token lets the compressed model complete most of the task. Increasing rank to 64 or 128 barely improves that result.

ganjikrishna/fraction-compressor-v0.4 · GitHub

That suggests a useful experiment: measure the output-distribution error at the point where the models diverge, rather than assuming that adding more overall rank will fix it.

### Fix B — Separate the decision to begin from the ability to complete a task

The repository's NuExtract experiment is particularly informative:

- The original fine-tune passes 9 of 10 prompts.
- The base model passes 0 of 10 because it stops instead of producing the expected output.
- The compressed patch passes 1 of 10.
- When the expected first token is forced, the base completes 7 of 10, and the patched model completes 8 of 10 cleanly.
  ganjikrishna/fraction-compressor-v0.4 · GitHub

This suggests that the fine-tune's main contribution in this particular experiment is not teaching the base an entirely new extraction skill. It is changing the model's decision about whether to start answering.

I would implement two separate evaluation tracks:

1. Continuation fidelity: Given the same starting token, how closely does the compressed model reproduce the original fine-tune's subsequent behavior?
2. Decision fidelity: Without forcing a starting token, does the compressed model make the same initial decision as the original fine-tune?

The first measures whether the downstream skill survived. The second measures whether the behavior that activates the skill survived.

This distinction prevents a misleading result where a model gets credit for knowing how to complete a task even though it never starts it.

### Fix C — Add a behavior-aware objective under a fixed byte budget

I would next test whether a candidate patch can be selected using both numerical reconstruction and output fidelity.

A conceptual objective would be:

$$
\begin{aligned}
\min_{\widehat{\Delta W}}\quad
& \lambda_w E_{\mathrm{weight}}
+ \lambda_p E_{\mathrm{output}}\\
&+\lambda_t E_{\mathrm{task}}\\
\text{subject to}\quad
& \operatorname{bytes}(\widehat{\Delta W})\le B
\end{aligned}
$$

Where:

- $E_{\mathrm{weight}}$ measures reconstruction error.
- $E_{\mathrm{output}}$ measures differences between original and compressed model outputs.
- $E_{\mathrm{task}}$ measures performance loss on a predefined evaluation suite.
- $B$ is the hard patch-size budget.
- The $\lambda$ values determine the relative importance of each metric.

I would not assume the task-error term can be reduced to a single universal score. It should be reported by task category, and safety-critical regressions should not be hidden by improvements elsewhere.

The practical experiment would compare three candidates at the same byte budget:

- The existing uniform-rank patch.
- The repository's best existing recipe.
- A candidate chosen using the combined evaluation objective.

The important part is not that the third candidate must win. It is that this experiment establishes whether behavior-aware selection actually improves results on unseen prompts.

## 3. How I would implement and validate it

I would make these changes in this order.

1. Reproduce the baseline. Run the repository's existing scripts and record the original fine-tune, base model, uniform-rank patch, and best recipe results. Preserve the exact model revisions and byte budgets.
2. Expand the evaluation set. The reported 10-prompt skill test is too small to support a strong general conclusion. Use more prompts, paraphrases, and multiple runs, with a held-out set that is not used to choose the patch.
3. Instrument the first-token decision. Record the original and compressed models' next-token logits, top predictions, and the probability margin between continuing and stopping where applicable. Determine whether the failure is a change in the preferred token or a more general distribution shift.
4. Run a controlled comparison. Test the current method against output-aware recipe selection while holding patch size and evaluation conditions constant.
5. Add regression gates. Reject a candidate that exceeds the byte budget or fails predefined quality and safety thresholds. Report failures rather than silently trading away important behavior.
6. Validate independently. Rerun the winning candidate on unseen prompts and a second compatible model pair before calling the approach an improvement.

## 4. What I would change in the codebase

The first places I would inspect are the existing factored representation, benchmark, and recipe-search implementations identified by the repository:

- `src/factored.py` — the representation and application of the compressed delta.
- `src/bench.py` — the existing evaluation pipeline.
- `results/skill_demo.json` and `results/skill_demo_forced.json` — the reported skill and forced-start experiments.
- `results/skill_demo_recipe.json` — the alternative allocation experiment.

These files are identified in the [repository documentation](<https://github.com/ganjikrishna/fraction-compressor-v0.4?utm_source=chatgpt.com>).

ganjikrishna/fraction-compressor-v0.4 · GitHub

I would start by extending the benchmark before modifying the compressor. That gives us a reliable way to tell whether any algorithmic change works.

## 5. What success would look like

| Metric | Desired result |
| --- | --- |
| Patch size | Within the same fixed byte budget |
| Broad behavior | Better or equal held-out performance |
| First-token decisions | Measurably closer to the original fine-tune |
| Continuation ability | Maintained when given the same starting context |
| Safety regressions | Explicitly measured, with unacceptable regressions blocking release |
| Reproducibility | Independent reruns produce consistent findings |

I would not promise that this approach will solve the first-token problem. The results could show that output-aware selection helps, that the current representation is the limiting factor, or that the apparent failure is partly due to evaluation noise.

My central reasoning is this: the repository already demonstrates that changing how a delta is represented and allocating the storage budget differently can improve some benchmark results. Its own experiments also show that better aggregate scores do not necessarily mean better first-token accuracy. The next meaningful fix is therefore to optimize and validate the behavior that is actually failing, not merely increase compression rank.

That gives you a falsifiable research plan: a defined hypothesis, a controlled experiment, a measurable success criterion, and a clear way to discover if the proposed fix does not work.

---

## Notes on accuracy

- The numbers ChatGPT cites match the project records: on the NuExtract gated skill, the full fine-tune passes 9/10, the base 0/10, the rank-32 patch 1/10, ranks 64 and 128 reach 2/10 each, and the force-start control gives 7/10 for the forced base and 8/10 clean for the forced patch.
- Its sharpest new point on the cloning question: the earlier four-AI panel mostly framed the question as whether the tool creates agency. ChatGPT argues the operative question is distribution cost and detectability (who can spread a consequential behavior, how fast, and how hard it is to detect), and that weak first-token transfer is an observed limitation of the tested method, model, and evaluation, not a proven general safety barrier.
- Part of its proposed fix overlaps work already in flight: the controlled comparison against adapters at a matched byte budget is the LoRA baseline experiment started Oct 28 (prompted by Nemotron's review). Its adaptive-allocation suggestion also restates the recipe search the project already runs, which ChatGPT itself acknowledges in section 2.
- Genuinely new proposals not yet in the project: reporting decision fidelity and continuation fidelity as two named evaluation tracks; a KL output-distribution fidelity metric between the fine-tune and the reconstructed model; and expanding the gated-skill evaluation beyond the current 10 prompts before drawing general conclusions about the gate.
