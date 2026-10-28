#!/usr/bin/env python3
"""Force-start control test for the real-skill transfer demo.

examples/skill_demo.py showed a first-token gate: on the NuExtract
extraction prompts the plain base starts on 0 of 10 (it emits
end-of-text immediately), the full fine-tune on 9 of 10, and the
rank-32 compressed patch on only 1 of 10, even though the patch moves
the first-token start-vs-stop margin most of the way (base -6.33,
patch -1.29, full fine-tune +4.60). That leaves one question open:

  If the start is FORCED, what happens next?

This control test answers it. For each of the same 10 prompts, the
fine-tune's own first generated token is forced as the first token,
and generation then continues greedily under the usual rules (max 64
new tokens including the forced one), for two configs:

  1. base model, forced start
  2. base + compressed patch (uniform rank 32), forced start

Reading the result:
  - If the forced BASE completes nearly as well as the forced patch,
    the extraction skill was already in the base and the patch mainly
    moves the trigger.
  - If the forced PATCH completes much better than the forced base,
    the patch carries real skill beyond the trigger.
  - Anything in between is reported as in between.

The forced token per prompt is re-derived here with the fine-tune's
own weights (greedy argmax after the prompt) and cross-checked
against the recorded full-delta answers in results/skill_demo.json:
the forced token's text must be a prefix of the recorded answer.

Judging is the identical judge from examples/skill_demo.py (clean =
parses as JSON, keys match the template, every expected value
present; partial = parses with something off; failed = does not
parse, empty counts as failed).

Run on Flash (NumPy forward from the verified Stage 2 machinery):
  ~/qwen-test/.venv/bin/python examples/skill_demo_forced.py \
      --reference ~/fc-v04-skill/skill_demo.json \
      --out-json ~/fc-v04-skill/skill_demo_forced.json \
      --out-transcript ~/fc-v04-skill/skill_demo_forced_transcript.txt
"""

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "src"))

import alien_sweep_stage2 as s2  # noqa: E402  (verified Stage 2 forward machinery)
import hotswap_demo as hs  # noqa: E402  (KV-cached step with factored adapters)
import skill_demo as demo  # noqa: E402  (CASES, make_prompt, judge, patch loader)
from tokenizers import Tokenizer  # noqa: E402

EOS = demo.EOS
MAX_NEW_TOKENS = demo.MAX_NEW_TOKENS


class Tee:
    """Write to both stdout and the transcript file."""

    def __init__(self, path):
        self.f = open(path, "w")

    def write(self, s):
        sys.__stdout__.write(s)
        self.f.write(s)

    def flush(self):
        sys.__stdout__.flush()
        self.f.flush()


def prompt_pass(sd, tok, prompt, adapters):
    """Run the prompt through the model; return (ids, caches, logits)."""
    ids = tok.encode(prompt).ids
    caches = [[[], []] for _ in range(s2.LAYERS)]
    logits = None
    for pos, token in enumerate(ids):
        logits = hs.step(sd, token, pos, caches, adapters)
    return ids, caches, logits


def generate_forced(sd, tok, prompt, adapters, forced_token):
    """Force forced_token as the first generated token, then greedy.

    Same stopping rules as skill_demo.generate_raw: stop before an
    EOS token, stop at MAX_NEW_TOKENS generated tokens in total
    (the forced token counts toward the cap).
    """
    ids, caches, logits = prompt_pass(sd, tok, prompt, adapters)
    t0 = time.perf_counter()
    out = [forced_token]
    pos = len(ids)
    if len(out) < MAX_NEW_TOKENS:
        logits = hs.step(sd, forced_token, pos, caches, adapters)
        pos += 1
        while len(out) < MAX_NEW_TOKENS:
            nxt = int(np.argmax(logits))
            if nxt in EOS:
                break
            out.append(nxt)
            if len(out) == MAX_NEW_TOKENS:
                break
            logits = hs.step(sd, nxt, pos, caches, adapters)
            pos += 1
    return tok.decode(out, skip_special_tokens=True), out, time.perf_counter() - t0


def main():
    ap = argparse.ArgumentParser()
    home = Path.home()
    ap.add_argument("--base", default=str(home / "qwen-test/data/qwen2.5-0.5b.safetensors"))
    ap.add_argument("--finetuned", default=str(home / "fc-v04-skill/data/nuextract/model.safetensors"))
    ap.add_argument("--tokenizer", default=str(home / "fc-v04-skill/data/nuextract/tokenizer.json"))
    ap.add_argument("--patch", default=str(home / "fc-v04-skill/skill_patch_r32.npz"))
    ap.add_argument("--reference", default=str(home / "fc-v04-skill/skill_demo.json"),
                    help="recorded unforced results (results/skill_demo.json copy)")
    ap.add_argument("--out-json", default="skill_demo_forced.json")
    ap.add_argument("--out-transcript", default="skill_demo_forced_transcript.txt")
    args = ap.parse_args()

    tee = Tee(args.out_transcript)
    sys.stdout = tee

    print("FRACTION COMPRESSOR v0.4 - FORCE-START CONTROL TEST")
    print("Skill: structured information extraction (text + JSON template -> filled JSON)")
    print("Base: Qwen2.5-0.5B. Fine-tune: numind/NuExtract-1.5-tiny (MIT).")
    print(f"Decoding: the fine-tune's own first token is forced, then greedy, "
          f"max {MAX_NEW_TOKENS} new tokens including the forced one. No API calls.")

    ref = json.loads(Path(args.reference).read_text())
    ref_ft = ref["configs"]["base + full delta (fine-tune weights)"]["per_prompt"]
    unforced_reference = {
        label: ref["configs"][label]["counts"] for label in ref["configs"]
    }
    print("\nUNFORCED REFERENCE (results/skill_demo.json):")
    for label, c in unforced_reference.items():
        print(f"  {label}: clean {c['clean']}, partial {c['partial']}, failed {c['failed']}")

    tok = Tokenizer.from_file(args.tokenizer)

    # Phase 1: the fine-tune's actual first generated token per prompt.
    sd_ft = s2.load_all_fp32(args.finetuned)
    print(f"\nFine-tune weights loaded (RSS {s2.peak_rss_mb():.0f} MB)")
    forced = {}
    print("\nFORCED FIRST TOKENS (fine-tune greedy argmax after each prompt):")
    for cid, text, template, checks in demo.CASES:
        prompt = demo.make_prompt(text, template)
        ids, caches, logits = prompt_pass(sd_ft, tok, prompt, None)
        first = int(np.argmax(logits))
        first_text = tok.decode([first])
        recorded = ref_ft[cid]["answer"]
        prefix_ok = recorded.startswith(first_text)
        forced[cid] = {"token_id": first, "token_text": first_text,
                       "matches_recorded_answer_prefix": prefix_ok}
        print(f"  [{cid}] token {first} {first_text!r} "
              f"(prefix of recorded full-delta answer: {prefix_ok})")
        if not prefix_ok:
            print(f"  ERROR: forced token does not match the recorded answer for {cid}")
            sys.exit(1)
        if first in EOS:
            print(f"  ERROR: forced token for {cid} is EOS; nothing to force")
            sys.exit(1)
    del sd_ft
    gc.collect()

    # Phase 2: forced runs on base and base + patch.
    adapters, header = demo.load_patch_adapters(args.patch)
    print(f"\nPATCH: uniform rank 32, factored price {header['storage_bytes_total']:,} B, "
          f"{len(adapters)} matrices with rank > 0")
    sd = s2.load_all_fp32(args.base)
    print(f"Base model loaded (RSS {s2.peak_rss_mb():.0f} MB)")

    results = {}
    for label, ad in (("base, forced start", None),
                      ("base + compressed patch (uniform rank 32), forced start", adapters)):
        print(f"\n{'=' * 72}\nCONFIG: {label}\n{'=' * 72}")
        per_prompt = {}
        counts = {"clean": 0, "partial": 0, "failed": 0}
        for cid, text, template, checks in demo.CASES:
            prompt = demo.make_prompt(text, template)
            answer, out_ids, secs = generate_forced(
                sd, tok, prompt, ad, forced[cid]["token_id"])
            j = demo.judge(answer, template, checks)
            counts[j["verdict"]] += 1
            per_prompt[cid] = {
                "prompt": prompt,
                "forced_token_id": forced[cid]["token_id"],
                "forced_token_text": forced[cid]["token_text"],
                "answer": answer, "generated_tokens": len(out_ids),
                "seconds": round(secs, 3), **j,
            }
            print(f"\n[{cid}] FORCED TOKEN: {forced[cid]['token_id']} "
                  f"{forced[cid]['token_text']!r}")
            print(f"ANSWER ({len(out_ids)} tokens, {secs:.1f}s):\n{answer}")
            print(f"VERDICT: {j['verdict']} (parseable={j['parseable']}, "
                  f"keys_match={j['keys_match']}, values {j['value_hits']}/{j['value_total']})")
        print(f"\n{label}: clean {counts['clean']}, partial {counts['partial']}, "
              f"failed {counts['failed']} of {len(demo.CASES)}")
        results[label] = {"per_prompt": per_prompt, "counts": counts}

    print(f"\n{'=' * 72}\nSCOREBOARD (of {len(demo.CASES)} prompts)\n{'=' * 72}")
    for label, c in unforced_reference.items():
        print(f"unforced  {label}: clean {c['clean']}, partial {c['partial']}, failed {c['failed']}")
    for label, r in results.items():
        c = r["counts"]
        print(f"forced    {label}: clean {c['clean']}, partial {c['partial']}, failed {c['failed']}")

    out = {
        "demo": "force-start control test for the NuExtract skill pair",
        "question": ("the patch rarely flips the first-token gate (1 of 10 unforced). "
                     "If the start is forced, does the plain base complete the extraction "
                     "(skill already in the base; the patch mainly moves the trigger), or "
                     "does the patch complete much better (the patch carries skill beyond "
                     "the trigger)?"),
        "base_model": "Qwen/Qwen2.5-0.5B",
        "finetuned_model": "numind/NuExtract-1.5-tiny (MIT), full fine-tune of the base",
        "skill_rule": "answer parses as JSON, keys match the template, every expected value present",
        "decoding": (f"fine-tune's own first generated token forced, then greedy, "
                     f"max {MAX_NEW_TOKENS} new tokens including the forced one, "
                     f"raw NuExtract prompt format"),
        "forced_token_source": ("greedy argmax of the fine-tune's own weights after each "
                                "prompt, cross-checked as a prefix of the recorded "
                                "full-delta answer in results/skill_demo.json"),
        "forced_tokens": forced,
        "unforced_reference": unforced_reference,
        "configs": results,
        "peak_rss_mb": round(s2.peak_rss_mb(), 1),
        "api_calls": [],
    }
    Path(args.out_json).write_text(json.dumps(out, indent=2))
    print(f"\nPeak RSS: {s2.peak_rss_mb():.0f} MB")
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_transcript}")
    tee.f.close()


if __name__ == "__main__":
    main()
