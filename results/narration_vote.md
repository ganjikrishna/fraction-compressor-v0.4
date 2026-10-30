# Narration vote: Chatterbox clone (A) vs MMS (B) for the final demo video

Provenance: Vinay ordered this vote on Wed Oct 28, 2026 (evening ET) after hearing the MMS sample against the current v5 Chatterbox-clone narration. Internal, local only, nothing pushed; the video is not rebuilt regardless of outcome, Vinay decides after the tally. One round, no debate. Every panelist got the identical brief (choice descriptions, sample facts, and the question verbatim). Order and routes: Muse Spark 1.3 first via the Meta Model API (logged in results/api_usage_log.jsonl, purpose "narration vote"; prompt 442, completion 1,880, total 2,322 tokens); Gemini gemini-3.5-flash-lite via the connector helper (also logged, 588 total tokens); Nemotron, Grok, Claude, Glimmer, and GPT-OSS via Flash's local OmniRoute gateway (http://localhost:20128/v1, temperature 0.3), which are Flash-local calls and not logged in api_usage_log.jsonl. Claude was called ONLY on the verified antigravity/claude-opus-4-6-thinking route; the served-model field confirmed claude-opus-4-6-thinking. Run completed 2026-10-29T01:06:45Z.

## Tally

- **A (Chatterbox clone): 4** — Gemini, Nemotron, Claude, Glimmer
- **B (MMS): 2** — Muse Spark, Grok
- **No answer: 1** — GPT-OSS

## Muse Spark 1.3 (Meta Model API): VOTE B

VOTE: B
Compliance decides it because organizers explicitly said third-party TTS not allowed and count MMS as an allowed Meta model, so A risks disqualification no matter how good it sounds. Deliberately not asking to avoid tightening the rules plus opening with cloned "Hi, I'm Vinay Ganji" looks deceptive if questioned live. B's flat 172 wpm and misheard terms ("Mita," "MuSpart") hurt first-time clarity, but can be partly fixed with slower per-block pacing, phonetic spelling, and on-screen text. B's CC-BY-NC attribution is easy to satisfy with a credit slide and keeping the submission unlisted/non-monetized, whereas A's rule risk wipes out the 25% Demo score entirely.

## Gemini (gemini-3.5-flash-lite): VOTE A

VOTE: A

Vinay's cloned voice ensures correct pronunciation of key terms like "Meta" and his own name, which the MMS model mangles into uncomprehending errors. For a hackathon where the demo video accounts for 25% of the score and is watched live, clarity and first impressions are paramount. MMS produces a rushed, flat delivery at 172 wpm with a restrictive non-commercial license, creating unnecessary compliance and quality friction. By contrast, Chatterbox delivers natural pacing and personal branding while maintaining honesty through a disclosure slide. Choosing A prioritizes judge comprehension and presentation quality over an overly strict interpretation of a gray-area rule.

## NVIDIA Nemotron 3 Ultra (nvidia/nemotron-3-ultra-550b-a55b, via Flash OmniRoute): VOTE A

VOTE: A

The "third-party TTS" restriction explicitly targets runtime models in the submission, not video-production tools; using a local MIT-licensed clone for the demo video is standard practice and the closing-slide disclosure demonstrates transparency. MMS's 172 wpm rush and systematic mispronunciation of "Vinay Ganji," "Muse Spark," and "patch file" would confuse judges hearing the project live for the first time, directly undermining the 25% demo score. The cc-by-nc-4.0 license also creates a needless legal cloud for a public YouTube video. Vinay's own voice at 149 wpm delivers correct terminology, personal authenticity, and natural pacing—exactly what a live judging session rewards. The organizer clarification was never meant to police how contestants record their own narration.

## Grok (grok-cli/grok-4.7, served grok-4.7, via Flash OmniRoute): VOTE B

VOTE: B

Organizers already said third-party TTS is not allowed, and declining to ask them does not make Chatterbox a safe choice — a flagged clone can wipe the entry, which outweighs a smoother take on the 25% demo score. MMS is the voice they count as a Meta model, so the submission stays inside the stated rule even though the speaker is generic. Its rushed, flat delivery and misheard names will hurt a judge hearing the project once, so use the feasible per-block re-pacing until “Vinay Ganji,” “Muse Spark,” and “patch file” are actually clear. cc-by-nc-4.0 still needs on-screen attribution, and the YouTube upload should stay unmonetized. A cloned voice is better theater, but it is the wrong bet while the downside is disqualification rather than a flatter narration.

## Claude (claude-opus-4-6-thinking, via Flash OmniRoute, antigravity route): VOTE A

VOTE: A

The demo video accounts for 25% of the score and is the first impression judges get—a voice that mispronounces the creator's own name, the sponsor's name, and the project's core terms (as confirmed by Whisper re-transcription) would actively undermine credibility and comprehension in a live judging session. Chatterbox is MIT-licensed, runs locally, and is not a third-party cloud TTS service injected into the product's runtime, so it falls squarely under production tooling (like using Premiere Pro or background music), and the closing slide's honest disclosure further neutralizes any compliance concern. The MMS option carries its own real compliance risk: cc-by-nc-4.0 is non-commercial, which is genuinely problematic for a public YouTube video tied to a competition with prizes, whereas MIT has no such restriction. A judge hearing "Vinik Ganjai built Mita's MuSpart using catch files" will be confused, not impressed, and no amount of re-pacing fixes a single-speaker model that simply cannot pronounce the relevant vocabulary. Vinay's own cloned voice speaking clearly at natural pace is the strongest, most honest, and lowest-risk choice for maximizing the demo score.

## Glimmer (meta/muse-glimmer-30b, via Flash OmniRoute): VOTE A

VOTE: A
Natural pacing, correct pronunciation of Vinay Ganji, Meta, Muse Spark and patch file, and a personal voice create a clear first impression that matters for a live-watched demo worth 25% of the score. Chatterbox is MIT licensed with honest on-screen disclosure, and the organizer clarification on third-party TTS appears aimed at runtime APIs, not a local open model, with the relevant office-hours posts never fully read. MMS is rushed and flat at ~172 wpm and demonstrably mishears core project vocabulary, which actively undermines comprehension on first hearing. Its cc-by-nc-4.0 license also introduces non-commercial attribution risk for a public YouTube video that could later be monetized.

## GPT-OSS 120B (nvidia/openai/gpt-oss-120b, via Flash OmniRoute): NO ANSWER

The single permitted try returned upstream HTTP 410 `model_shutdown`, the same provider shutdown first seen about 7:00 PM ET today and recorded in the earlier panels. No vote filed.

## Synthesis

The panel split on which risk is real. The four A votes (Gemini, Nemotron, Claude, Glimmer) all read the organizers' "third-party TTS" line as aimed at runtime models in the submitted product, not at how a contestant produces a video, and all four treated the MMS sample's mangled core vocabulary ("Vinik Ganjai", "Mita", "MuSpart", "catch file") as an active liability for a live-watched demo worth 25% of the score, with the cc-by-nc-4.0 license as a second, needless risk on a public video. The two B votes (Spark, Grok) took the clarification at face value: whatever the intended scope, a stated prohibition plus a deliberately un-asked question leaves A exposed to disqualification, a downside that dwarfs a flatter narration, and B's delivery problems are partly repairable with per-block re-pacing, phonetic respelling, and an unmonetized upload with attribution. The disagreement is not about which voice sounds better, every panelist conceded A does, but about whether the compliance wording is a gray area a disclosed production choice can stand on (A side) or a plain rule whose violation is not worth any demo gain (B side).
