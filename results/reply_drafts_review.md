# Panel review: the two public reply drafts (internal, local only)

Provenance: Vinay asked Thu Oct 29, 2026 for the two replies to be drafted, checked with the other AIs, and returned to him for the posting decision. Nothing posted, nothing pushed. Final drafts: results/reply_drafts_final.md. Order and routes: Muse Spark 1.3 first via the Meta Model API (1,865 prompt, 3,818 completion, 5,683 total tokens, logged in results/api_usage_log.jsonl, purpose "reply drafts review"); Gemini gemini-3.5-flash-lite via the connector helper (2,069 prompt, 264 completion, 2,333 total, also logged); Nemotron, Glimmer, Grok, and Claude via Flash OmniRoute (Flash-local calls, not in the API log; served models confirmed: nvidia/nemotron-3-ultra-550b-a55b, meta/muse-glimmer-30b, grok-4.7, claude-opus-4-6-thinking on the antigravity route, with tool_choice none). GPT-OSS was not retried in this round; it has been provider shut down (HTTP 410 model_shutdown) since Oct 28 evening in every panel. Every panelist got the same pack: both drafts plus the verified fact list. One call each, no retries needed; all six answered.

## Verdicts

### Muse Spark 1.3
Reply A: overstates the evidence. "Garbled" presents an indicative Whisper re-transcription as direct TTS fact, but Whisper adds its own errors; "plain sentences read fine" is unsupported. Proposed a hedged rewrite naming the Whisper caveat, the 27.55 s sample, and the 172 vs 149 wpm pacing. Reply B: no factual error or overstatement; bytes, logprobs, gap definition, first-token range, costs, validation lines, and the panel wording rules all match the facts. Ship as is.

### Gemini (gemini-3.5-flash-lite)
Reply A: no errors, no changes. Reply B: one softening. "The adapter wins, and it scores above the full fine-tune" overstates the narrative; replace with "the adapter yields a higher mean logprob than the full fine-tune it was distilled from." All panel guidelines otherwise followed.

### Nemotron 3 Ultra (asked the original LoRA question)
Reply A: "checkpoint license" to "model license"; "before deciding" to "before choosing a narrator." Reply B: drop "the obvious question" editorializing and restate the question neutrally; drop "standard" before LoRA; state the dedup rule exactly ("exact matches and items with token-set Jaccard ≥ 0.7 were rejected"); drop "only" before "ties"; add the dense vs hooked agreement (7.1e-06 per item) to the validation line.

### Glimmer
Reply A: same two flags as Spark (Whisper caveat; "plain sentences read fine" unverified). Proposed a rewrite keeping the concrete mishearings (Vinay Ganji as Vinik Ganjai, Meta as Mita, Muse Spark as MuSpart, patch file as catch file). Reply B: no factual errors; wording stays within the panel constraints; no changes required.

### Grok (grok-4.7)
Reply A: "before deciding" leaks a narration choice the reply was meant to omit; "plain sentences read fine" unsupported; "garbled" treats an indicative Whisper pass as proof. Proposed a rewrite adding the license's attribution term and the note that organizers count MMS as a usable Meta voice. Reply B: numbers and the consistent-with wording match; fixes: the logprob std (0.085) is missing from the table; "report the mean" is false for first-token accuracy, which is a range across seeds; "base scores bit for bit" is wider than the verified claim (per-item logprobs); add the dense vs hooked check; drop the Spark judging sentence because Spark also authored the prompts, so it is not independent support.

### Claude (claude-opus-4-6-thinking, antigravity route)
Both drafts publishable as written; no changes recommended. Verified Reply B numbers, rounding, the panel wording discipline, and the no-dash rule (clean pass). Noted only that Reply A could name the garbled terms if more precision were wanted.

## Fixes applied to the final drafts

Reply A:
1. Whisper caveat added (Spark, Glimmer, Grok): the mishearings are now attributed to an indicative Whisper re-transcription, not stated as a direct TTS measurement.
2. "Plain sentences read fine" dropped (Spark, Glimmer, Grok).
3. "Before deciding" dropped (Grok; Nemotron's milder replacement not taken, Grok's full drop is cleaner and leaks nothing).
4. "Checkpoint license" changed to "model license" (Nemotron), with the attribution term added (Grok).
5. One line added noting organizers count MMS as a Meta model usable as voice (Grok), so the license note does not read as "not usable here."

Reply B:
1. Opening restated neutrally, no "obvious question" (Nemotron); "standard LoRA" shortened to "LoRA" (Nemotron).
2. Dedup rule stated exactly: exact matches and token-set Jaccard of 0.7 or higher rejected (Nemotron).
3. "Scores above the full fine-tune" reframed: the adapter beats both factored patches on mean logprob and posts a higher mean logprob than the full fine-tune (Gemini).
4. Seed reporting corrected: headline numbers are the mean over seeds, first-token accuracy is the range across seeds (Grok); logprob std 0.085 added to the table (Grok).
5. Validation line completed: zero adapter reproduces the base per-item logprobs bit for bit, and dense vs hooked forwards agree to within 7.1e-06 per item (Grok, Nemotron).
6. Temperature 1 added to the distillation description (Grok).

Not applied, with reasons:
- Grok's "drop the Spark judging sentence": kept. The sentence claims only that Spark judged 7 of 7 factual claims supported, which is true and is part of the validation record this document is required to carry; it does not claim independence.
- Nemotron's "drop 'only' before 'ties'": kept. The earlier five-model panel's wording rule for this result specifies "first-token accuracy only ties," and Grok used the same phrasing; the word carries the confidence-vs-capability scope, it does not weaken the fact.

Dash check on the final drafts: no em dashes or en dashes (mechanical scan, zero U+2014 and zero U+2013).
