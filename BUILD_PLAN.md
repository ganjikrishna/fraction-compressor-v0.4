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
