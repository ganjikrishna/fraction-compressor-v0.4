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
- Simplicity rule (Vinay, Oct 27): keep the video as simple as possible. Plain words, no jargon without a one-line explanation, one idea at a time on screen. A newcomer watching once should understand what the tool does AND be able to pick it up and use it: the video shows the actual quickstart path (clone, run the quickstart, swap a patch file) in real steps, not just results.
- One script line near the close answers the question people will ask (Vinay, Oct 27): how is this different from a memory or personality file and other tools on the market? Plain version: a memory file is words the model reads; our patch is numbers that change the model's math. The README carries the fuller comparison (memory/prompts, adapters, whole-model shrinking).
- Do-it-yourself requirement (Vinay, Oct 27, after Agents 101): the video and the README must explain how the patch works AND how a viewer can do it themselves, as plain steps: take a base model and a fine-tuned version of it, run the compressor on the difference to get a small patch file, then load the patch with the base model to get the fine-tuned behavior. If the repo lacks a single clean script for that path, build one (examples/make_patch.py style) so the steps shown are the steps that actually run.

## Working notes

- Muse Spark reasons before answering and reasoning tokens count against max_tokens; use generous caps in benchmark calls.
- Log every real Muse Spark call the benchmark makes (prompt, token counts, verdict) into results/ as it happens, so the Meta tooling use is evidenced in the repo, not just planned. (Muse Spark's own suggestion in its Oct 26 repo review. Soft budget from Vinay: keep Meta API use under the $100 alert level of the $150 credits where possible.)
- Agents 101 takeaways applied (Oct 27, Vinay: use what is needed): (1) Verification leads the submission and demo story: Meta's own session framed agent output as unverified until defensive checks confirm it, "as important as building the agentic loop", so our rerun + Spark + Gemini cross-checks are presented as a headline feature, not a footnote. (2) Spark judging verdicts cite the exact result files they are based on (grounding advice from the session). (3) In the submission's Meta-products field, describe the benchmark harness honestly in the session's terms: a harness loop (plan, run tools, check results) with Muse Spark inside it.
- Validation rule (Vinay, Oct 26): key results are cross-validated by Muse Spark AND Gemini, on top of the script reruns that produce them. If the two disagree, the disagreement is reported and investigated, never averaged away.
- Model scope (settled Oct 26 night, Vinay: do what is best): Spark family only. Spark 1.3 via the Meta Model API, Spark Open via Baseten, Glimmer as the Flash reference. The other Meta models (Wonder, Image, Voice Transcribe, SAM 3.1) do not fit a compression tool, so they will not be forced in just to name more models. Depth of Spark use is the tooling story.
- Credit order and tracking (Vinay, Oct 26, 10:23 PM): the Baseten credits may not be available after the hackathon, so Baseten carries the heavy lifting first while it lasts: bulk benchmark runs, sweeps, and repeated evaluations on Muse Spark Open. The Meta Model API is used as needed for task generation, judging, and validation. Every Baseten and Meta call is tracked in results/ with provider, model, time, purpose, and token counts, so the usage totals can be shared with the organizers in the submission and checked against the credit balances.
- Models and weights are never committed (see .gitignore); data/ holds local downloads only.
- Glimmer's new wording limit (Oct 27, after the strengthening results): when the compressed versions outscore the full patch itself (as on the SmolLM2 pair), the gap-closed percentage passes 100% and must not be presented as a fraction of the fine-tune recovered. Prose about that pair must state plainly that the percentage is not a recovery fraction there and that the raw score margin is the honest measure. Record: results/glimmer_reference_addendum.md.
- Fresh-question test size (Vinay, Oct 27): the fresh held-out test stays at 96 questions. Expanding it further was considered and declined; 96 is the validated set the headline numbers rest on.
- Skill-transfer limit disclosure (Vinay, Oct 27): the NuExtract gated-skill limit is disclosed upfront, not buried: a "Known limit" note opens the README's Benchmark results section. Vinay's direction was to check with Spark and Glimmer and do what is best; both validators independently recommended (c) disclose upfront AND test larger patches (rank 64/128). The size test ran the same day: 1/10 clean at rank 32, 2/10 at rank 64 and rank 128, so size barely moves this boundary. Records: results/skill_limit_consultation.md, results/skill_demo.json, results/skill_demo_ranks.json.
- Force-start control test (Oct 28, Vinay's go-ahead): settles the question Muse Spark raised in the why-it-matters debate. Forcing the fine-tune's own first token on the same 10 NuExtract prompts takes the plain base from 0/10 to 7 clean + 1 partial, so most of the extraction skill was already in the base and the fine-tune's main work is the decision to start. The rank-32 patch under the same forced start scores 8 clean + 1 partial, matching the full fine-tune's own unforced score: a small real edge beyond the trigger (it cleans the two prompts the forced base still fails, and loses one the forced base cleans), but the gate is the dominant term. Limit wording in README and docs/why-it-matters.md updated to the settled version. Records: results/skill_demo_forced.json, results/skill_demo_forced_transcript.txt, examples/skill_demo_forced.py.
- Llama Phase 3 (Oct 27): the third pair (Meta's own Llama 3.2 1B base and Instruct, unblocked when the Hugging Face license approval landed) ran the full contest. The byte-fair variant no_embed_mlp_spread_balanced (24,515,584 B) beats uniform_rank32 on the combined 96 fresh questions, gap closed 15.9% vs -7.6% (uniform scores below the base model itself), and wins both halves; the Stage 2 winner no_embed_mlp_spread is byte-unfair at +38.0% over the 25,143,296 B budget and is named only as such. Recovery on this pair is weaker than on the other two pairs, and no factored config outscored the full delta, so gap_closed stays a recovery fraction here. Validation (Oct 27): script recomputation matched 60 of 60 gap_closed values exactly; Gemini recomputed every headline value, confirmed claims 1 to 5, and ruled the summary sentence fair; the Muse Spark judging addendum supported claims A to D and marked E not supported on scope only (the pair-1 comparison was outside the numbers it was shown; the in-pair facts were confirmed, and the 23.2% figure rests on the pair-1 records and the earlier addendum's supported claim A). Records: results/third_pair_stage2.json, results/third_pair_heldout96.json, results/gemini_validation_llama.md, results/spark_judging_llama.md.

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
- Headline ruling (Oct 27, three-way validation; Vinay sided with Glimmer over Gemini and Spark): the headline recipe in our own prose (README, demo, submission) is mlp_behemoth_lite, the byte-fair leader: it beat the human uniform recipe on the fresh held-out tasks while using fewer bytes (gap closed 9.5% vs 1.6%). mlp_behemoth itself is named only as the byte-unfair parent (11.8% more bytes than uniform) whenever it appears. The validators' own records in results/ keep their original words; this ruling governs our wording, not their records.
- Strengthening tests (approved by Vinay Oct 27, running): (1) the fresh-question held-out test expands from 24 to 96 items (72 new Spark-generated, novelty-checked), lite vs uniform rerun on the Qwen pair; (2) the full contest repeated on a second pair, SmolLM2-360M base/Instruct; (3) the same contest on Meta's own open weights, Llama 3.2 1B base/Instruct, queued after (2) and subject to the HF license gate.

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
