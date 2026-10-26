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
5. Nov 4 reserved for the 3-minute demo video and the submission writeup.

## Working notes

- Muse Spark reasons before answering and reasoning tokens count against max_tokens; use generous caps in benchmark calls.
- Models and weights are never committed (see .gitignore); data/ holds local downloads only.

## Expanded scope (Vinay, Oct 26: push the limits, not just another version)

1. Live hot-swap demo as the centerpiece: one base model, tiny 1-bit delta files swapped in live, behavior changes on the spot, file sizes shown side by side. This is the moment the demo video is built around.
2. Muse Spark inside the product loop: Spark (Meta Model API) generates fresh probe tasks, runs the compressed vs full comparison, and writes the verdicts. The benchmark is agentic, not a static script output.
3. Meta open weights in the comparison: Muse Spark Open (hosted via Baseten) joins the benchmark table, which also puts the project in contention for the Best Build on Meta Open Weight Models bonus.
4. Reproducibility as a feature: every number in the README and demo is produced by a script in this repo that anyone can rerun.
5. Submission craft: review the submission form in the first days, script the 3-minute demo from the start, post the demo on X at submission for the Most Viral bonus, and open the video with the required line separating pre-existing work from this week's build.

## Resources we will use

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
