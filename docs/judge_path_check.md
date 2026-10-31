# Judge path check (verified Fri 2026-10-30)

Glimmer claim check (Oct 30, served model meta/muse-glimmer-30b): the .env.example endpoint, model, and no-key-needed claims are CLEAN, and the proposed README line below was supported as written. Two narrow flags, both resolved as omissions in the fact sheet given to Glimmer rather than errors in the draft: the dev.meta.ai key source (documented in the project's Meta Model API connector record) and the optional Baseten/Fireworks keys (Spark Open cross-checks documented in the submission draft section 7 and the README). No text change required. Separately, a voluntary precision edit was applied to both .env.example and the proposed README line: they state plainly that the Spark loop ran through external tooling during the event, not through an in-repo script. Full record: results/submission_pack_glimmer_check.md.

Question: can a judge clone the public repo and run the project from the
README alone, including how to supply a Meta Model API key?

## What was verified

- Clone source: https://github.com/ganjikrishna/fraction-compressor-v0.4 (the submission repo, created Oct 26, 2026).
- README "Do it yourself" path: `python examples/make_patch.py --base <base> --finetuned <finetuned> --rank 32 --out patch.npz`, then `--verify`, then load the patch with the base as in examples/hotswap_demo.py.
- `python3 examples/quickstart.py` was run during this check (Fri Oct 30) and completed clean: it prints the storage cost, bits per weight, factored error next to the best any factored form could do at the same rank, and ends with "OK: the factored path runs and never builds the full matrix at apply time." It needs only numpy, as its docstring states.
- make_patch.py reads safetensors files with its own byte-level parser, so it genuinely needs only numpy plus src/factored.py, matching its docstring. A judge does not need the safetensors package for the patch maker.
- The hot-swap demo additionally imports the `tokenizers` package (pip). See gap 2.
- Recorded sample runs exist in the repo (results/make_patch_demo.txt, results/hotswap_demo_transcript.txt), so a judge can compare expected output before running anything heavy.

## The Meta Model API key question

- No script in this repo calls the Meta Model API. The recipe search and claim-checking consumed recipes and verdicts produced with Muse Spark during the event; the recipes, probes, and judging records are committed under results/, and every benchmark reruns from those files with no key.
- So a judge needs NO key for the compressor, the quickstart, the patch maker, the hot-swap demo, or the benchmark reruns.
- A judge who wants to re-run the Spark loop itself needs their own Meta Model API key (endpoint https://api.meta.ai/v1, model muse-spark-1.3, keys from https://dev.meta.ai). Organizer guidance (Josh, Oct 30) confirms judges test on their own keys if needed, and API access is not lost on Nov 4.
- `.env.example` was MISSING and has now been CREATED at the repo root (this check, Oct 30): template only, placeholder value, no real credential. It states plainly that nothing else in the repo needs a key, names the endpoint and model, and optionally names the Baseten and Fireworks keys used for the Spark Open cross-checks.
- README line that should reference it (for the README batch owner to add; README.md was not edited by this check). Suggested placement, end of the "Do it yourself" section, exact text (voluntary precision wording, Oct 30: the Spark loop ran through external tooling during the event, not an in-repo script, so the line does not promise it can be re-run from the repo):
  "No API key is needed for anything above. The Muse Spark recipe design and claim-checking during the event used the Meta Model API; to call it the same way with your own key, copy .env.example to .env and fill in your key. The recipes and judging records it produced are already in results/."
- Companion .gitignore line the same batch should add: `.env` (the current .gitignore lists .venv/, data/, __pycache__/, *.log, and not .env, so a filled-in key file would not be ignored by default).

## Gaps found

1. FIXED in this check: no .env.example existed. Created, template only. The README reference line above is still owed by the batch that owns README.md; until it lands, a judge finds the file at the repo root but no pointer to it.
2. OPEN (minor): no dependency install step anywhere. There is no requirements.txt, and the README never says to install numpy (needed by everything) or tokenizers (needed only by examples/hotswap_demo.py). A judge on a bare Python will hit ModuleNotFoundError on the first run. Nothing in the README contradicts running; the step is simply absent. Suggested one-line fix for the README batch, at the top of "Do it yourself": "Needs Python 3 with numpy (pip install numpy); the hot-swap demo also needs the tokenizers package (pip install tokenizers)."
3. OPEN (minor): the README's "Do it yourself" section never mentions examples/quickstart.py, the fastest smoke run (numpy only, no model downloads, under a minute). The video's narration points at it ("Clone the repo. Run the quickstart"), and the repo map section lists it, but the step-by-step a judge follows does not. Suggested fix for the README batch: make the quickstart step 0 of "Do it yourself".
4. No gap stops the core path: with numpy installed, the quickstart runs as verified, and make_patch plus verify run on any base/fine-tune safetensors pair. Gaps 2 and 3 cost a judge minutes, not the run.

## Bottom line

The judge path works. One gap (the missing .env.example) is fixed here; two minor README gaps are recorded above with exact suggested lines for the pre-submission README batch. Nothing found would stop a judge running the quickstart or making a patch.
