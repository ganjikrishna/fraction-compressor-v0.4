# Why it matters

A fine-tuned model is a base model plus a patch: everything training changed, and normally that patch is nearly as big as the model itself. This tool squeezes an existing fine-tune's patch into a file of about 19 MB instead of 1 GB, at 1 bit per weight. One base can then carry many behaviors, one small file each.

## Three uses

- **Many behaviors, one model.** Fifty fine-tunes the normal way means fifty full models; as patches, fifty small files on one base.
- **Live switching.** A patch swaps in or out in a tenth of a second while the base keeps running, changing behavior mid-conversation.
- **Cheap to move.** A 19 MB file can be sent, downloaded on a slow link, or carried on a small device. A 1 GB model often cannot be.

## How it differs from a download or a repo

Downloading a fine-tune gives you the whole model, full size. Small adapters like LoRA exist, but an adapter is a new add-on trained for one task. This tool starts from a fine-tune that exists and converts it, with no retraining: point the script at a base and its fine-tune, and it writes the patch and measures how much behavior the patch carries.

Two honest costs: making a patch needs both full models once, and running one needs the base in memory. The saving is in storing and moving behaviors.

## What bound it breaks, and what it does not

The usual assumption is that at 1 bit per weight, nothing useful survives. Done the plain way, that holds: on Llama 3.2 1B, spreading the budget evenly scored below the base model itself, worse than no patch. Spending the same bytes where they matter kept a real share: 15.9% of the gap closed there, 23.2% on the Qwen pair. So one bound breaks: useful behavior survives smart squeezing.

The other bound stands: a tiny patch is not the full fine-tune. Most of the gap stays behind. Patches are for cheap switching and sharing, not replacements.

## The known limit

One kind of skill transfers weakly: skills decided by the first token, like "start the JSON or stop." On a JSON-extraction fine-tune, the full fine-tune starts on 9 of 10 prompts, the base on 0, the patch on 1. Measured at the first token, the patch moves the model halfway toward starting (base -6.33, patch -1.29, full fine-tune +4.60) but usually does not cross. On the one prompt where it does start, the extraction is fully correct.

The author's intuition: the knowledge is there, it just needs to know to start. The control test has now been run, and it mostly backs him: force the fine-tune's first token and the plain base completes 7 of 10 cleanly (8 of 10 counting a partial), so most of the extraction skill was already in the base, and what the fine-tune mainly installs is the decision to start. The patch under the same forced start completes 8 of 10 cleanly and 1 partly, matching the fine-tune's own unforced score: a small real edge beyond the trigger, but the gate is the main story. Full records: `results/skill_demo_forced.json`; the earlier debate is in `results/why_debate.md`.
