# Provenance live check and wording review (2026-10-31)

Local record only. Review requested by Vinay, 2026-10-31.

## Evidence (verified by Ember in the main chat, 2026-10-31)

Both live GitHub repos were cloned and every file SHA-256 hashed.

- v0.4 repo (github.com/ganjikrishna/fraction-compressor-v0.4), live head 2ce00363b97fbb278b133cea17852542aee0743d: 147 files.
- Older repo (github.com/ganjikrishna/fraction-compressor), live head c2bf28d1f52c4905d0b13a78fd93467328ea958f: 32 files.
- Exactly ONE byte-identical file across the two repos: .gitignore (generic, 4 lines: .venv/, data/, __pycache__/ and one more generic line).
- Same-path files: 4 total. .gitignore identical. README.md, NOTICE.md, LICENSE all DIFFERENT content in the two repos. The LICENSE difference: the older repo carries a shortened MIT variant; v0.4 carries the full standard MIT text. Both are MIT licenses.
- No code, benchmark, result, or script file matches by hash. No git history was carried over (v0.4 was created fresh Oct 26, 2026).

## Draft wording reviewed (revised draft)

"Provenance: this repository (github.com/ganjikrishna/fraction-compressor-v0.4) was created on Oct 26, 2026 for the Meta Global AI Developer Hackathon and contains only work from Oct 26 to Nov 4, 2026. It was verified against the live older repository (github.com/ganjikrishna/fraction-compressor, head c2bf28d) on Oct 31, 2026: of 147 files here and 32 files there, exactly one file is byte-identical in both, a generic four-line .gitignore. README.md and NOTICE.md exist in both repositories but are different texts (rewrites, not copies). Both repositories use the MIT license, but the license texts are not identical. No code, benchmark, result, or script file was copied, and no git history was carried over. Prior work (Fraction Compressor v0.1 to v0.3 and the Signet experiments) lives in the older repository and is disclosed in the README; its methods are cited as prior art, not included as files."

This wording replaced an earlier draft that wrongly called the LICENSE a shared identical file; the live check corrected that.

## Reviewer 1: Glimmer (meta/muse-glimmer-30b, Flash OmniRoute, served-model field confirmed)

Route note: first call (max_tokens 1500) returned no content, finish_reason "length" (2,124 tokens, reasoning consumed the cap). One retry at max_tokens 4000 returned the verdict below (4,280 tokens, finish "stop").

Verdict: FLAG

Verbatim:

1. No. The wording adds purpose / date-range claims and interpretive claims that are not in the evidence.

2. Overclaims / unsupported:
* “Provenance: this repository (github.com/ganjikrishna/fraction-compressor-v0.4) was created on Oct 26, 2026 for the Meta Global AI Developer Hackathon and contains only work from Oct 26 to Nov 4, 2026.”
  Created on Oct 26, 2026 is supported; “for the Meta Global AI Developer Hackathon” and “contains only work from Oct 26 to Nov 4, 2026” are not supported by the evidence.
* “README.md and NOTICE.md exist in both repositories but are different texts (rewrites, not copies).”
  Different content is supported; “rewrites, not copies” is an interpretation not supported.
* “No code, benchmark, result, or script file was copied, and no git history was carried over.”
  No git history was carried over is supported; “was copied” is stronger than the evidence which only shows no file is byte-identical / no hash match.
* “Prior work (Fraction Compressor v0.1 to v0.3 and the Signet experiments) lives in the older repository and is disclosed in the README; its methods are cited as prior art, not included as files.”
  No evidence is provided for v0.1-v0.3, Signet experiments, README disclosure or citation.

3. Verdict: FLAG

Evidence-conforming replacement:

Provenance: this repository github.com/ganjikrishna/fraction-compressor-v0.4 was created on Oct 26, 2026. It was verified against the live older repository github.com/ganjikrishna/fraction-compressor, head c2bf28d1f52c4905d0b13a78fd93467328ea958f on Oct 31, 2026: of 147 files here and 32 files there, exactly one file is byte-identical in both, a generic four-line .gitignore. README.md, NOTICE.md and LICENSE exist in both repositories but have different content. Both repositories use the MIT license, but the license texts are not identical. No code, benchmark, result, or script file is byte-identical, and no git history was carried over.

## Reviewer 2: Muse Spark 1.3 (Meta Model API)

Usage: prompt 576, completion 6,400, total 6,976 tokens. Logged in results/api_usage_log.jsonl, purpose "provenance live check review".

Verdict: FLAG

Verbatim:

1. No. It adds purpose, a future window, specific prior-work names/disclosure/citation, and absolute "copied/rewrites" conclusions not established by the Oct 31 SHA-256 comparison alone.

2. Overclaims:
- "Provenance: this repository (github.com/ganjikrishna/fraction-compressor-v0.4) was created on Oct 26, 2026 for the Meta Global AI Developer Hackathon and contains only work from Oct 26 to Nov 4, 2026." - verified Oct 31 cannot cover to Nov 4; purpose not in file-hash evidence.
- "No code, benchmark, result, or script file was copied, and no git history was carried over." - evidence is only no SHA-256 match, not proof of no copying with edits.
- "Prior work (Fraction Compressor v0.1 to v0.3 and the Signet experiments) lives in the older repository and is disclosed in the README; its methods are cited as prior art, not included as files." - v0.1-v0.3/Signet names, README disclosure and citation not in evidence.

3. FLAG. Replace with evidence-only language, e.g.:

Replace sentence 1 with: "Provenance: this repository (github.com/ganjikrishna/fraction-compressor-v0.4) was created fresh Oct 26, 2026 with no git history carried over, as verified Oct 31, 2026."

Replace "No code...was copied" with: "No code, benchmark, result, or script file is byte-identical to a file in the older repository (no SHA-256 match)."

Delete last sentence - README disclosure/citation was not part of the hash verification.

## Agreement between the reviewers

Both FLAG, on the same three points:

1. The Oct 26 to Nov 4 window and the hackathon-purpose phrase in sentence 1 are not established by an Oct 31 hash check (a check on Oct 31 cannot cover files added through Nov 4).
2. "Was copied" overclaims: the evidence shows no byte-identical file / no SHA-256 match, not the absence of copying with edits. Both propose byte-identical language.
3. The final sentence (v0.1 to v0.3, Signet, README disclosure, prior-art citation) is outside the hash evidence; both say delete it from this statement or support it from other records.

Glimmer alone also flags "(rewrites, not copies)" as an unsupported interpretation (evidence supports "different texts" only) and supplies a complete evidence-conforming replacement paragraph (above).

Scope note: both reviewers were instructed to judge the wording against the hash evidence pack only. The flagged purpose, date-range, and prior-work statements are project-history facts (repo created fresh Oct 26, 2026 for the hackathon; prior work disclosed in the README) that are simply not part of what the hash comparison itself proves. Whether the published PROVENANCE.md adopts the evidence-only wording or keeps those statements on the strength of the project record is Vinay's call.

## Agreed wording fix (if evidence-only wording is adopted)

Use Glimmer's replacement paragraph verbatim; it satisfies every Spark fix as well (byte-identical language, no future window, no unsupported prior-work sentence).
