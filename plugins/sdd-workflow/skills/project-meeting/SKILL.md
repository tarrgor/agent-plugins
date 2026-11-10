---
name: project-meeting
description: This skill should be used to run a recurring project status meeting. Trigger phrases include "let's have a project meeting", "run the status meeting", "meeting time", "review the inbox", "project standup", or whenever accumulated findings, reports, and knowledge need to be reviewed and turned into decisions.
---

# Project Meeting

Moderates a recurring project status meeting — does not touch code. Decisions that shape the project are made with the user, one at a time; obvious corrections are made without asking.

Written-deliverable sizing and the delegation rule are defined in `../_shared/conventions.md` (relative to this skill's directory).

GitHub operations: `../_shared/github.md` — the `gh` commands below are the reference form.

## What an issue is for

A GitHub issue means implementation work: a change to code, tests, or shipped configuration. Nothing else is ever an issue.

Editing a document is never implementation work. Any change confined to `.project/` documents, READMEs, or other prose — a spec amendment, a Knowledge correction, a reworded requirement, a new Knowledge entry — is made directly in this meeting, by editing the file. Do not open an issue for it, however large the edit or however many documents it touches. "This is a big doc change" is a reason to confirm the wording with the user, not a reason to file an issue.

The one exception: an issue may exist for documentation that ships as part of the product (user-facing docs, generated API reference) when writing it is real work sized like a feature.

## What to decide alone vs. ask about

Act immediately, without asking, and just report what was done:

- Corrections to `.project/` documents where the document is factually wrong or out of date and the right value is unambiguous — a stale path, a renamed file, a superseded link, a `Status:` that contradicts reality, a claim the code plainly disproves.
- Adding or rewording a line or a few lines in a spec, Knowledge entry, or meeting record to match what the project already does.
- Discarding an Inbox finding that is already resolved, duplicated, or was purely informational.
- Deleting or archiving a Knowledge entry that documents something no longer in the codebase.

Just do these — no issue, no confirmation.

Ask the user, one topic at a time, only for:

- Anything that changes project direction, scope, priority, or milestone boundaries.
- Closing a milestone (Step 6).
- Creating a GitHub issue (i.e. committing real implementation work).
- Substantive spec changes: new or removed requirements, changed acceptance criteria, reversed decisions. Confirmation is about the wording and the direction — once agreed, edit the document here.
- Findings with more than one defensible outcome, or where the correct fix isn't clear from the project's own material.

When unsure which side a change falls on: if a competent teammate would have just fixed it, fix it.

## How to present something the user must decide

The user did not write the implementation and cannot judge a decision phrased in terms of it. Present every decision so it can be answered without reading the code.

- Lead with what is at stake for the project — what breaks, what gets slower, what a user of the product would notice — not with the mechanism that causes it.
- Name files, functions, types, and identifiers only when the user needs them to answer; one is usually enough as a pointer, and never as the explanation itself.
- Expand any term the project itself invented, or that only someone who read the implementation would know, the first time it appears.
- Give the options as concrete consequences ("we accept slower startup" / "we spend an issue on it"), each with its cost, and state a recommendation.
- Keep it to a few sentences. Offer the technical detail as a follow-up the user can ask for, rather than including it up front.

## 1. Determine what's new since the last meeting

- Find the most recent `.project/Archive/MEETING-<YYYY-MM-DD>.md` (newest by date in filename). Everything after its date is "since last meeting"; if none exists, this is the first meeting and everything counts.
- Gather: `.project/Reports/*` newer than that date, `.project/Knowledge/**` entries newer than that date, and every file currently in `.project/Inbox/`.

## 2. Report on completed work and new knowledge

- Summarize issues implemented since the last meeting, from `.project/Reports/`.
- Summarize new knowledge captured, from `.project/Knowledge/`.
- Informational only — no decisions needed here, just present it.

## 3. Spot-check Knowledge currency

- List `.project/Knowledge/**`. Skip entries recording a pure convention or decision — nothing there to go stale. For entries asserting a specific, checkable state ("X is unfixed", "Y isn't supported yet"), re-verify against the current code or issue tracker.
- Entries with `type: research` frontmatter rest on external sources that decay on their own schedule, so they age rather than get contradicted. Flag one when its `researched:` date is more than roughly three months old, when its `confidence:` is `low`, or when the project has since committed to a decision it informed. Do not re-run the research here — that's a Step 4 outcome.
- Anything contradicted or flagged as aged: if the correction is unambiguous, apply it now and report it. Otherwise treat it as a finding in Step 4, alongside Inbox findings — propose update, archive, or supersede.
- This is a full sweep, not scoped to "since last meeting" — staleness accumulates precisely in entries nobody has touched recently.
- Also spot-check the `Active` milestone spec (`Status:` lifecycle per `../_shared/conventions.md`, relative to this skill's directory): re-verify its checkable claims about the codebase the same way. Fix contradictions that are plainly factual; substantive contradictions become Step 4 findings (outcome: spec amendment). Closing a finished milestone happens in Step 6, not here.

## 4. Triage findings, one at a time

- Process each file in `.project/Inbox/`, plus each stale Knowledge entry flagged in Step 3. Sort each against the rule above:
  - Obvious outcome → carry it out now. Collect these and report them together as a short list of what was handled, without interrupting the meeting for each one.
  - Decision needed → present it per "How to present something the user must decide", propose an outcome, and wait for the user before moving to the next such finding. Never batch these or decide more than one at a time.
- Available outcomes:
  - Inbox findings: new issue (only if the finding requires a code change), amendment to `.project/SPEC.md` or the active `.project/SPEC-milestone-*.md`, no action, or something else. A finding whose whole remedy is "write this down" or "correct this document" takes the amendment outcome, never the issue outcome.
  - Stale Knowledge entries: update the entry, archive/delete it, or leave as-is.
  - Aged research entries: leave as-is, archive it if the decision it fed is settled and it no longer informs anything, or agree to re-research it. Re-research is a recommendation to run `research-topic` after the meeting — never run it from here; it is user-invoked and needs its own scoping.
- Carry out exactly the chosen outcome — create the issue using the same conventions as `create-spec-issues`, amend the relevant spec, edit or remove the Knowledge entry, or discard — then move any consumed Inbox file to `.project/Archive/`.

## 5. Plan next steps

- Discuss upcoming work, new ideas, or changes — raised by either party — one topic at a time.
- These are direction decisions by nature: new issues, spec changes, and milestone changes always require explicit confirmation before being carried out.

## 6. Close the milestone if finished

- Only this skill closes milestones. Commands and the `Status:` lifecycle per `../_shared/conventions.md`.
- For the `Active` milestone: `gh issue list --milestone "<title>" --state open` — include any issues created in this meeting.
- If none remain open: propose closing it and wait for the user's confirmation — never close a milestone without asking. On yes, close the GitHub milestone via `gh api` and set the spec's `Status:` to `Done`; on no, leave both as is and record why. The same applies to any milestone whose issues are all closed but which is still open on GitHub or not marked `Done`.
- If issues remain open, leave the milestone as is.

## 7. Record the meeting

Write `.project/Archive/MEETING-<YYYY-MM-DD>.md`: date, each finding and its resolved outcome (including stale Knowledge entries corrected or removed, and the changes made without asking), work completed, knowledge gained, next steps agreed, and any milestone closed or kept open. This is the marker the next meeting's Step 1 reads from.

## 8. Commit and push

- `.project/` changes belong on the base branch (per conventions: `develop` if present, else the default). If a feature branch is checked out, say so and `git switch <base>` first — never discard, stash, or sweep in unrelated uncommitted changes; if switching is unsafe, stop and ask.
- Stage only `.project/` (moved Inbox files, spec amendments, a spec marked `Done`, the new meeting record) — never unrelated changes sitting in the working tree.
- Commit with a message summarizing the meeting (date, findings resolved, decisions made) per the base-branch rules in `../_shared/conventions.md` — the branch is usually protected, so the branch-and-PR fallback (branch `chore/project-meeting-<YYYY-MM-DD>`) applies if the push is rejected; report that PR instead of claiming the change landed on the base branch.

## 9. Suggest the next step

End by naming the next action that follows from the meeting's decisions — e.g. `implement-issue` for a newly created issue, `create-spec-issues` after a spec change, `research-topic` for an entry agreed to be re-researched or an open question the meeting couldn't settle, `kick-off` after closing a milestone, or nothing pending.
