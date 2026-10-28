#!/usr/bin/env python3
"""Real-skill transfer demo for Fraction Compressor v0.4.

The Alien Sweep showed score transfer on probe sets. This demo shows a
SKILL moving: a model fine-tuned for one concrete job, its behaviour
rebuilt inside the plain base model by swapping in a small compressed
patch file, live, with nothing else changed.

The skill pair:
  base:       Qwen/Qwen2.5-0.5B (the plain base model)
  fine-tune:  numind/NuExtract-1.5-tiny (MIT license), a full fine-tune
              of that exact base for structured information extraction:
              give it a text and a JSON template, it answers with the
              template filled in, as JSON and nothing else.

The fine-tune uses a raw completion format (no chat template):

    <|input|>
    ### Template:
    {the JSON template, indent 4}
    ### Text:
    {the text}

    <|output|>
    {the filled JSON}

Three configs run the SAME 10 screening prompts, greedy, max 64 new
tokens, judged by the skill's own rule:

  1. base model, no patch
  2. base + full delta (the fine-tune's own weights; identical to the
     base plus the uncompressed difference)
  3. base + compressed patch (uniform rank 32, built by
     examples/make_patch.py; the factored path (X @ U) @ V.T, the dense
     delta is never formed)

Per-prompt transfer verdict for every config:
  clean   the answer parses as JSON, its keys match the template, and
          every expected value is present
  partial the answer parses as JSON but a key or a value is off
  failed  the answer does not parse as JSON (rambling, empty, or cut
          off at the token cap all count as failed)

Screening note (Step 2 of the search, run before any compression): on
these prompts the plain base model answers with an immediate
end-of-text on all 10 (empty output), while the full fine-tune fills
9 of 10 templates correctly inside the token cap (the "event" answer
is cut mid-JSON at 64 tokens). The compressed patch is then judged
against what the full fine-tune itself achieves.

Run on Flash (NumPy forward from the verified Stage 2 machinery):
  ~/qwen-test/.venv/bin/python examples/skill_demo.py \
      --out-json results/skill_demo.json
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
import factored  # noqa: E402
import hotswap_demo as hs  # noqa: E402  (KV-cached step with factored adapters)
from tokenizers import Tokenizer  # noqa: E402

EOS = {151643}  # <|endoftext|>, the fine-tune's generation_config eos
MAX_NEW_TOKENS = 64

# (id, text, template, expected-value substrings judged on the answer)
CASES = [
    ("person",
     "Maria Chen, a 34-year-old software engineer from Seattle, works at Northwind Labs where she leads the payments team.",
     {"Name": "", "Age": "", "City": "", "Employer": "", "Role": ""},
     ["maria chen", "34", "seattle", "northwind labs", "engineer"]),
    ("product",
     "The AeroPress Go travel coffee maker costs $49.95 and weighs 323 grams. It is made by AeroPress Inc. and brews espresso-style coffee in about 2 minutes.",
     {"Product": "", "Price": "", "Weight": "", "Maker": ""},
     ["aeropress go", "49.95", "323", "aeropress inc"]),
    ("event",
     "The Riverbend Music Festival will take place on August 14, 2027, in Austin, Texas. Headliners include The Wild Reeds and June Harbor. Tickets start at $89.",
     {"Event": "", "Date": "", "City": "", "Performers": [], "Ticket price": ""},
     ["riverbend", "2027", "austin", "wild reeds", "june harbor", "89"]),
    ("company",
     "On March 3, 2026, Helix Robotics announced it had raised $12 million in a Series A round led by Vertex Ventures. The startup, founded in 2021 in Denver, builds warehouse robots.",
     {"Company": "", "Amount raised": "", "Round": "", "Lead investor": "", "Founded": "", "Headquarters": ""},
     ["helix robotics", "12", "series a", "vertex ventures", "2021", "denver"]),
    ("book",
     "'The Clockwork Garden' is a 2023 fantasy novel by Priya Raman. The 384-page book was published by Alder House Press and won the 2024 Locus Award.",
     {"Title": "", "Author": "", "Year": "", "Pages": "", "Publisher": ""},
     ["clockwork garden", "priya raman", "2023", "384", "alder house"]),
    ("sports",
     "In Sunday's final, Spain defeated Argentina 2 to 1 to win the Davis Cup. The deciding match lasted 3 hours and 12 minutes and was played in Madrid.",
     {"Winner": "", "Loser": "", "Score": "", "Tournament": "", "City": ""},
     ["spain", "argentina", "davis cup", "madrid"]),
    ("recipe",
     "To make the sauce, melt 40 grams of butter, add 2 cloves of garlic and 200 milliliters of cream, then simmer for 5 minutes.",
     {"Ingredients": [], "Simmer time": ""},
     ["butter", "garlic", "cream"]),
    ("weather",
     "Tomorrow in Chicago, expect a high of 57 degrees Fahrenheit with winds of 18 miles per hour from the northwest and a 40 percent chance of rain.",
     {"City": "", "High temperature": "", "Wind speed": "", "Rain chance": ""},
     ["chicago", "57", "18", "40"]),
    ("job",
     "Brightline Health is hiring a data analyst in Boston. The role pays between $85,000 and $95,000 per year and requires 3 years of experience with SQL.",
     {"Company": "", "Role": "", "Location": "", "Salary range": "", "Experience": ""},
     ["brightline", "data analyst", "boston", "sql"]),
    ("model",
     "Today we release Falcon-Lite 3B, a 3-billion-parameter language model built by the TII team in Abu Dhabi. It uses grouped-query attention and is released under the Apache 2.0 license.",
     {"Model": {"Name": "", "Number of parameters": "", "Architecture": []}, "License": ""},
     ["falcon-lite", "apache", "grouped"]),
]


def make_prompt(text, template):
    """The fine-tune's documented raw prompt format."""
    return (f"<|input|>\n### Template:\n{json.dumps(template, indent=4)}\n"
            f"### Text:\n{text}\n\n<|output|>")


def generate_raw(sd, tok, prompt, adapters):
    ids = tok.encode(prompt).ids
    caches = [[[], []] for _ in range(s2.LAYERS)]
    logits = None
    t0 = time.perf_counter()
    for pos, token in enumerate(ids):
        logits = hs.step(sd, token, pos, caches, adapters)
    out, pos = [], len(ids)
    for _ in range(MAX_NEW_TOKENS):
        nxt = int(np.argmax(logits))
        if nxt in EOS:
            break
        out.append(nxt)
        if len(out) == MAX_NEW_TOKENS:
            break
        logits = hs.step(sd, nxt, pos, caches, adapters)
        pos += 1
    return tok.decode(out, skip_special_tokens=True), len(out), time.perf_counter() - t0


def keys_match(parsed, template):
    if not isinstance(parsed, dict) or not isinstance(template, dict):
        return False
    if set(parsed.keys()) != set(template.keys()):
        return False
    return all(keys_match(parsed[k], template[k])
               for k in template if isinstance(template[k], dict))


def judge(answer, template, checks):
    parsed = None
    try:
        obj = json.loads(answer.strip())
        if isinstance(obj, dict):
            parsed = obj
    except Exception:
        pass
    if parsed is None:
        return {"parseable": False, "keys_match": False,
                "value_hits": 0, "value_total": len(checks), "verdict": "failed"}
    low = json.dumps(parsed, ensure_ascii=False).lower()
    hits = sum(1 for c in checks if c in low)
    km = keys_match(parsed, template)
    verdict = "clean" if (km and hits == len(checks)) else "partial"
    return {"parseable": True, "keys_match": km,
            "value_hits": hits, "value_total": len(checks), "verdict": verdict}


def load_patch_adapters(patch_path):
    """Rebuild factored adapters from a make_patch.py .npz file."""
    z = np.load(patch_path)
    header = json.loads(z["header_json"].item())
    adapters = {}
    for meta in header["matrices"]:
        if meta["rank"] == 0:
            continue
        sk = meta["store_key"]
        rows, _ = meta["shape"]
        signs = z[f"{sk}_signs"]
        scales = z[f"{sk}_scales"].astype(np.float32)
        V = z[f"{sk}_V"].astype(np.float32)
        U = factored.unpack_signs(signs, (rows, meta["rank"])) * scales[:, None]
        adapters[sk] = (np.ascontiguousarray(U, dtype=np.float32), V)
    z.close()
    return adapters, header


def run_config(label, sd, tok, adapters, results):
    print(f"\n{'=' * 72}\nCONFIG: {label}\n{'=' * 72}")
    per_prompt = {}
    counts = {"clean": 0, "partial": 0, "failed": 0}
    for cid, text, template, checks in CASES:
        prompt = make_prompt(text, template)
        answer, ntok, secs = generate_raw(sd, tok, prompt, adapters)
        j = judge(answer, template, checks)
        counts[j["verdict"]] += 1
        per_prompt[cid] = {
            "prompt": prompt, "answer": answer, "generated_tokens": ntok,
            "seconds": round(secs, 3), **j,
        }
        print(f"\n[{cid}] PROMPT:\n{prompt}")
        print(f"ANSWER ({ntok} tokens, {secs:.1f}s):\n{answer}")
        print(f"VERDICT: {j['verdict']} (parseable={j['parseable']}, "
              f"keys_match={j['keys_match']}, values {j['value_hits']}/{j['value_total']})")
    print(f"\n{label}: clean {counts['clean']}, partial {counts['partial']}, "
          f"failed {counts['failed']} of {len(CASES)}")
    results[label] = {"per_prompt": per_prompt, "counts": counts}
    return counts


def main():
    ap = argparse.ArgumentParser()
    home = Path.home()
    ap.add_argument("--base", default=str(home / "qwen-test/data/qwen2.5-0.5b.safetensors"))
    ap.add_argument("--finetuned", default=str(home / "fc-v04-skill/data/nuextract/model.safetensors"))
    ap.add_argument("--tokenizer", default=str(home / "fc-v04-skill/data/nuextract/tokenizer.json"))
    ap.add_argument("--patch", default=str(home / "fc-v04-skill/skill_patch_r32.npz"))
    ap.add_argument("--out-json", default="skill_demo.json")
    args = ap.parse_args()

    print("FRACTION COMPRESSOR v0.4 - REAL-SKILL TRANSFER DEMO")
    print("Skill: structured information extraction (text + JSON template -> filled JSON)")
    print("Base: Qwen2.5-0.5B. Fine-tune: numind/NuExtract-1.5-tiny (MIT).")
    print(f"Decoding: greedy, max {MAX_NEW_TOKENS} new tokens. No API calls.")
    tok = Tokenizer.from_file(args.tokenizer)

    adapters, header = load_patch_adapters(args.patch)
    disk_bytes = Path(args.patch).stat().st_size
    print(f"\nPATCH (built by examples/make_patch.py, {header['rank_mode']}):")
    print(f"  factored-format price: {header['storage_bytes_total']:,} B")
    print(f"  patch file on disk:    {disk_bytes:,} B (.npz container)")
    print(f"  full delta at fp16:    {header['full_delta_fp16_bytes']:,} B "
          f"({header['full_delta_fp16_bytes'] / header['storage_bytes_total']:.1f}x larger)")
    print(f"  matrices with rank > 0: {len(adapters)}")

    results = {}
    t0 = time.perf_counter()
    sd = s2.load_all_fp32(args.base)
    print(f"\nBase model loaded in {time.perf_counter() - t0:.1f}s "
          f"(RSS {s2.peak_rss_mb():.0f} MB)")
    run_config("base (no patch)", sd, tok, None, results)
    run_config("base + compressed patch (uniform rank 32)", sd, tok, adapters, results)
    del sd, adapters
    gc.collect()

    sd = s2.load_all_fp32(args.finetuned)
    print(f"\nFine-tune weights loaded (RSS {s2.peak_rss_mb():.0f} MB)")
    run_config("base + full delta (fine-tune weights)", sd, tok, None, results)
    del sd
    gc.collect()

    print(f"\n{'=' * 72}\nSCOREBOARD (of {len(CASES)} prompts)\n{'=' * 72}")
    for label, r in results.items():
        c = r["counts"]
        print(f"{label}: clean {c['clean']}, partial {c['partial']}, failed {c['failed']}")
    out = {
        "demo": "real-skill transfer: structured information extraction",
        "base_model": "Qwen/Qwen2.5-0.5B",
        "finetuned_model": "numind/NuExtract-1.5-tiny (MIT), full fine-tune of the base",
        "skill_rule": "answer parses as JSON, keys match the template, every expected value present",
        "decoding": f"greedy, max {MAX_NEW_TOKENS} new tokens, raw NuExtract prompt format",
        "patch": {
            "built_by": "examples/make_patch.py",
            "rank_mode": header["rank_mode"],
            "storage_bytes": header["storage_bytes_total"],
            "file_bytes_on_disk": disk_bytes,
            "full_delta_fp16_bytes": header["full_delta_fp16_bytes"],
        },
        "configs": results,
        "peak_rss_mb": round(s2.peak_rss_mb(), 1),
        "api_calls": [],
    }
    Path(args.out_json).write_text(json.dumps(out, indent=2))
    print(f"\nPeak RSS: {s2.peak_rss_mb():.0f} MB")
    print(f"Wrote {args.out_json}")


if __name__ == "__main__":
    main()
