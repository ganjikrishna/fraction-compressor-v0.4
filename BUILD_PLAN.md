# Build plan, Meta Global AI Developer Hackathon (Oct 26 to Nov 4, 2026)

Submission rules honored here:
- This repo holds only work done during the event. Prior work (v0.1 to v0.3, Signet) stays in github.com/ganjikrishna/fraction-compressor and is cited, not copied.
- The 3-minute demo video opens with one line stating what was pre-existing and what was built this week.
- Deadline: Wed Nov 4, 9:00 PM ET, via the Cerebral Valley submission portal.

## Scope

1. Factored-multiply runtime for 1-bit compressed deltas: Y = (X U) V^T, never materialize W. Memory read per token is the headline metric.
2. End-to-end task-accuracy benchmark on the Signet probe sets (knowledge, instruction, math): base vs base + full delta vs base + sign/factored delta, so the compressed path is scored on task answers, not only weight error.
3. Meta model in the loop: Muse Spark (Meta Model API) runs the same probe sets as a hosted reference, and Muse Spark Open is the planned open-weight candidate if time allows.
4. Stretch, only if 1 to 3 are done: System Instruction Hot-Swap Test (base vs full delta vs sign delta on strict JSON-format prompts, scored by parseability).
5. Alien Sweep: a wide, automated search over compression recipes that a human would not normally pick, filtered in two stages and verified by rerun (full protocol in its own section below). This replaces the planned human rank sweep; it does not add a separate build.
6. Nov 4 reserved for the 3-minute demo video and the submission writeup.

## Demo video plan (approved by Vinay, Oct 26)

- Recorded on Muse's VM: a screen recording of the real demo running (terminal/browser capture). No camera, no laptop needed from Vinay.
- Script first, timed to what is on screen. Voice added after: AI-generated narration mixed over the recording with ffmpeg (the same pipeline as the folk-tale factory, minus generated scenes).
- Exactly 3 minutes. Opens with the required line stating what was pre-existing and what was built this week. Shape: 0:00 opening + problem; 0:30 the hot-swap moment; 1:30 benchmark numbers, including one Alien Sweep line (recipes tried, winner, held out result); 2:15 Muse Spark judging + quantum audit, one line each; 2:45 close.
- Rough cut early (as soon as the hot-swap demo runs) for Vinay to watch and react; final cut Nov 2-3 once the real numbers are in; Nov 4 reserved for submission only. Vinay approves the final cut before anything is posted.

## Working notes

- Muse Spark reasons before answering and reasoning tokens count against max_tokens; use generous caps in benchmark calls.
- Log every real Muse Spark call the benchmark makes (prompt, token counts, verdict) into results/ as it happens, so the Meta tooling use is evidenced in the repo, not just planned. (Muse Spark's own suggestion in its Oct 26 repo review. Soft budget from Vinay: keep Meta API use under the $100 alert level of the $150 credits where possible.)
- Validation rule (Vinay, Oct 26): key results are cross-validated by Muse Spark AND Gemini, on top of the script reruns that produce them. If the two disagree, the disagreement is reported and investigated, never averaged away.
- Model scope (settled Oct 26 night, Vinay: do what is best): Spark family only. Spark 1.3 via the Meta Model API, Spark Open via Baseten, Glimmer as the Flash reference. The other Meta models (Wonder, Image, Voice Transcribe, SAM 3.1) do not fit a compression tool, so they will not be forced in just to name more models. Depth of Spark use is the tooling story.
- Credit order and tracking (Vinay, Oct 26, 10:23 PM): the Baseten credits may not be available after the hackathon, so Baseten carries the heavy lifting first while it lasts: bulk benchmark runs, sweeps, and repeated evaluations on Muse Spark Open. The Meta Model API is used as needed for task generation, judging, and validation. Every Baseten and Meta call is tracked in results/ with provider, model, time, purpose, and token counts, so the usage totals can be shared with the organizers in the submission and checked against the credit balances.
- Models and weights are never committed (see .gitignore); data/ holds local downloads only.

## Expanded scope (Vinay, Oct 26: push the limits, not just another version)

1. Live hot-swap demo as the centerpiece: one base model, tiny 1-bit delta files swapped in live, behavior changes on the spot, file sizes shown side by side. This is the moment the demo video is built around.
2. Muse Spark inside the product loop: Spark (Meta Model API) generates fresh probe tasks, runs the compressed vs full comparison, and writes the verdicts. The benchmark is agentic, not a static script output.
3. Meta open weights in the comparison: Muse Spark Open (hosted via Baseten) joins the benchmark table, which also puts the project in contention for the Best Build on Meta Open Weight Models bonus.
4. Reproducibility as a feature: every number in the README and demo is produced by a script in this repo that anyone can rerun.
5. Submission craft: review the submission form in the first days, script the 3-minute demo from the start, post the demo on X at submission for the Most Viral bonus, and open the video with the required line separating pre-existing work from this week's build.
6. Alien Sweep as the search story: Spark proposes recipes, the sweep tests them, and the demo reports how many recipes were tried and what the winner was. If the human recipe wins, that is the reported result, with the full search map published either way.

## Alien Sweep (approved by Vinay, Oct 26)

Vinay's condition (Oct 26): use it only if it makes sense once the build starts. If the recipe space outruns what the runtime can run and verify by Nov 4, fall back to the human rank sweep and report that plainly in the results.

What it is, in plain words: instead of a person choosing a few sensible compression settings and testing those, an agent proposes many settings, including odd ones a person would skip, a script tests all of them, and only the ones that pass a fresh rerun count. The name comes from the October 2026 OpenAI math release, where mathematicians called the AI proofs alien math because the winning moves came from directions humans had not tried.

How it runs:
- Recipe generation: Muse Spark proposes recipes as per-layer rank maps under a fixed total size budget (uneven budgets across layers included). Recipes are strict JSON, layer name to integer rank only; anything needing a new code path (ternary deltas, variable bit width) is out of bounds for the sweep. Every proposed recipe is logged with its reason, so the search count in the demo is a real count from a file, not a claim.
- Stage 1, cheap filter: the fast matrix level benchmark scores every recipe on reconstruction error at exact accounted size. Only the top 5 recipes advance.
- Stage 2, hard check: the top 5 run the end to end task benchmark (knowledge, instruction, math probes) on Flash. A recipe only counts if the benchmark script reruns it and it passes on task score, not only weight error.
- Held out guard: Spark generates fresh probe tasks the search never saw. The winner must also pass those, so the sweep cannot win by memorizing the old 24 probe items.
- Honest outcome rule: if no alien recipe beats the human rank 32 recipe, the result is reported that way and the search map is still published. No winner is named in the demo script until Stage 2 and the held out check are both done.

Where it fits the schedule: the rank sweep was already an early experiment in this plan. The Alien Sweep widens that same slot. Stage 1 is cheap CPU work on the VM; Stage 2 is only 5 recipes on Flash. Nov 4 stays reserved.

### Gemini debate on Alien Sweep (Oct 26, via the Gemini API)

- Verdict: GO, but only inside a strict boundary. A recipe is a per-layer rank distribution under a fixed total size budget, which needs zero new runtime code (the same SVD and packing path, different rank integers per layer). The moment a recipe needs a new code path, it is out.
- Technique adopted: precompute the SVD once per matrix up to the max rank, then Stage 1 scores each recipe by slicing the precomputed factors. Hundreds of recipes then cost seconds, not one SVD per recipe.
- Failure modes Gemini raised, all accepted: low matrix error does not guarantee task success (that is why Stage 2 exists); Spark can emit invalid layer names or out-of-range ranks (strict JSON schema check before anything runs); Stage 2 CPU time per config is the real budget risk; the winner may be the boring uniform recipe (covered by the honest outcome rule).
- Day 2 go/no-go checks. Any failure means fall back to the human rank sweep and report it: (1) Spark produces 5 schema-valid recipe JSONs quickly, layer-to-rank maps only; (2) the one-time SVD precompute for the target model finishes in under 10 minutes; (3) Stage 1 scores the full recipe set in minutes via slicing; (4) one Stage 2 config completes the task benchmark inside the agreed time budget without memory thrash on Flash.

## Resources we will use

- AI compute (Vinay, Oct 26): use all of it. Meta Model API credits fund Muse Spark as task generator, judge, AND independent validator of results; Gemini covers design debate and repo review; Flash local models run the heavy benchmarks. The free credits exist to be spent on this build. Order of use (Vinay, Oct 26 night): Baseten first for the heavy lifting, because its credits may end with the hackathon; the Meta Model API fills in as needed. Real-money charges beyond the credits still need Vinay's tap.

- Flash (Vinay's Ubuntu box): local small models for the factored-runtime experiments, plus Muse Glimmer 30B through NVIDIA NIM, which is already working there. Quality-critical orchestration stays on the Muse VM, which holds the Meta Model API connection.
- Other AIs for design pressure-testing: the standing Gemini design-debate chat (Vinay's permission), used the same way as during prep, with anything adopted logged in NOTES.
- Quantum component (honest and bounded): the benchmark's verification pass audits a subset of results, and that subset is chosen with true quantum random numbers generated on IBM Quantum hardware (free plan, ibm_fez). The backend, job, and seed are logged with the results. It is an audit-sampling method, not a speed claim.
- Feedback for Meta: the submission includes a short section on what we learned about the Muse models themselves (for example, Muse Spark spends output budget on reasoning before answering), since the organizers say they want to learn where the tools need to improve.

## Crediting

Vinay K Ganji Krishna is the sole participant and author of record. The README credits Ember (Muse Spark) as the AI agent used for implementation, benchmarking, and documentation, the same way the event itself promotes building with the Muse Code agent. Ember is not listed as a team member.

## Design input from the Gemini debate chat (Oct 26)

- Rank tuning beats bit-unpacking kernels. Kernels are a rabbit hole for a 10-day solo build; plain numpy unpacking is enough. Rank calibration is existential: too low and the delta is powerless, too high and the file-size story dies. A rank sweep is an early experiment.
- Quarantine the quantum dependency: pull one large batch of quantum random numbers from IBM hardware at the start, log backend and seed, freeze it as a static fixture. No live quantum calls during crunch or demo.
- The demo contrast must be stark: same prompt, base model fails it, the tiny delta file (size on screen) swaps in, same prompt now succeeds. The strict-JSON instruction prompt is the natural centerpiece.
- Probe sets: sharp archetypes carry the demo; the full Signet sets still carry the benchmark table, because reproducible numbers are the credibility.
