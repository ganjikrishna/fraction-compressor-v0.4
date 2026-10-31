# Submission day runbook: Monday Nov 2, 2026 (LOCAL DRAFT, nothing here is executed yet)

Planned submission day is Monday Nov 2 (Vinay's decision, Oct 29). Hard deadline is Wed Nov 4, 9:00 PM ET, with a 6-hour grace period as backstop only. Fallback if Nov 2 fails: Tue Nov 3 evening, after the Newton sale.

Two facts shape the whole day (verified Oct 29 from the live form): the form has NO draft saving, and there is NO statement that a submission can be edited, updated, or resubmitted after submitting. Treat the Nov 2 submission as FINAL. Everything below happens before the Submit button, in order.

Form: https://cerebralvalley.ai/e/meta-ai-developer-hackathon/hackathon/submit
Source text: docs/submission_draft.md (one section per form field, in form order).

## Runbook

### (a) Final text check of the draft

- [ ] Read docs/submission_draft.md end to end once, as a judge would. Every number against the README and the result files it cites; the honesty rules hold (patch is lossy, 23.2% gap closed on the main pair, first-token accuracy below base, LoRA wins where training is available, gap closed above 1.0 never called a recovery fraction).
- [ ] Only two placeholders should remain at this point: section 6 (YouTube link) and section 11 (X post link). Both get filled in steps (c) and (d).
- [ ] Confirm the approved video cut: v7 if Vinay approved it after the internal review, otherwise v6 final (video/rough_cut_v6_final.mp4, 178.633 s).

### (b) Pre-submission push batch (Vinay preview, Glimmer check, his tap, then push)

Batch contents, local changes waiting as of Oct 30:

- [ ] README.md: the panel-wording paragraph (lossy patch statement next to the 19 MB claim, applied Oct 29), PLUS the judge-path lines recorded in docs/judge_path_check.md (the .env.example pointer, the numpy/tokenizers install line, quickstart as step 0) and the `.env` line for .gitignore.
- [ ] .env.example (new, created Oct 30 in the judge-path check; template only, no credential).
- [ ] docs/demo_script.md (current v6 state; update to v7 if v7 is the approved cut).
- [ ] docs/youtube_upload_pack.md, docs/x_post_pack.md, docs/judge_path_check.md, docs/submission_day_checklist.md (this pack; new Oct 30).
- [ ] results/narration_vote.md (REQUIRED: the submission draft's narration note points judges to it).
- [ ] results/wonder_review.md, results/wonder_video_review.md, results/wonder_review_panel.md.
- [ ] results/patch_value_discussion.md, results/lora_recovery_push_glimmer_check.md, results/panel_wording_review.md.
- [ ] results/video_review_v6_panel.md and video/v6_notes.md (plus the v7 review record and notes if v7 is approved).
- [ ] results/api_usage_log.jsonl, including the still-owed appends from the patch-value discussion's Compute section.
- [ ] Provenance file mapping event files to the older repo's dated commits, IF Vinay approved the provenance draft (his tap pending as of Oct 30).
- [ ] The approved demo video file itself, added to the repo (Vinay's Oct 28 instruction).
- [ ] Push procedure as always: verify remote head first, NUL-delimited manifest outside the source dir, push, verify new head, append the sync record only on confirmed success.

NOT in this batch unless Vinay separately decides: all fifth-pair / 7B material, results/updates_question_panel.md, results/alien_math_panel.md, results/7b_interpretation_panel.md and _claude.md (his "Skip 4" ruling stands).

### (c) YouTube upload

- [ ] Upload the approved cut using docs/youtube_upload_pack.md (title, description, chapters as written there).
- [ ] Visibility: Public.
- [ ] Open the watch URL signed-out and confirm it resolves and plays.
- [ ] Paste the URL into docs/submission_draft.md section 6, replacing the placeholder.

### (d) X post

- [ ] Post the primary text from docs/x_post_pack.md with the real YouTube and repo links in place (alternates A and B are in the pack if the primary reads wrong on the day).
- [ ] Open the post URL signed-out and confirm it resolves.
- [ ] Paste the URL into docs/submission_draft.md section 11, replacing the placeholder.

### (e) Fill the form, field by field, from the draft

- [ ] Field 1 Team Name: "Fraction Compressor" (draft section 1).
- [ ] Team Members: pre-filled (Vinay Ganji / vinuhi5online); confirm it still shows correctly.
- [ ] Track radio: Indie Developer Track (draft section 2).
- [ ] Problem statement radio: Push the Frontier (draft section 3).
- [ ] Field 5 Most Viral: the X post URL from step (d).
- [ ] Field 6 Project Description: draft section 4, pasted whole (it opens with the pre-existing vs built-this-week separation; there is no separate field for it).
- [ ] Field 7 Public GitHub Repository: https://github.com/ganjikrishna/fraction-compressor-v0.4 (draft section 5). Confirm it resolves signed-out and shows the pushed batch from step (b).
- [ ] Field 8 3-Minute Demo Video: the YouTube URL from step (c) (draft section 6, including the narration note under it).
- [ ] Field 9 Use of Meta products: draft section 7.
- [ ] Field 10 Why Meta's models matter: draft section 8.
- [ ] Field 11 Meta product feedback (optional): draft section 9.
- [ ] Field 12 Partner tech feedback (optional): draft section 10.
- [ ] Read every pasted field once on the form itself before the checkbox; pasted text, not the draft, is what gets judged.

### (f) Permission, tap, submit

- [ ] Permission checkbox: grants Meta and Cerebral Valley use of the submitted materials (the project was always meant to be public; Vinay acknowledged the rules Oct 26).
- [ ] Vinay's final tap. Nothing submits without it.
- [ ] Click Submit once.

### (g) Save the confirmation

- [ ] Screenshot or save the confirmation screen and any confirmation text into ~/workspace/goals/fraction-compressor/hidden_files/ with the date and time.
- [ ] Note the submitted YouTube and X URLs next to it.
- [ ] Report to Vinay in the main chat: submitted, with the confirmation saved.

## If Nov 2 breaks

- Deadline Nov 4, 9:00 PM ET; grace to about 3:00 AM ET Nov 5 is a backstop, never the plan.
- Fallback slot: Tue Nov 3 evening after the Newton sale, same runbook, same order.
- Judging runs Nov 5 to 8 on the video and the repo; organizers test on their own keys if needed, and API access is not lost on Nov 4 (Josh, Oct 30). Baseten credits expire Nov 9; nothing in this runbook depends on them.
