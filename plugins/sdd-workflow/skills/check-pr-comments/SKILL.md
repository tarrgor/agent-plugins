---
name: check-pr-comments
description: This skill should be used to triage and address review feedback on an issue that already has an open PR. Trigger phrases include "check the PR comments", "address the review feedback", "handle the comments on PR 12", "respond to review comments", or whenever an already-implemented issue has feedback waiting. Run by the user or by `run-milestone` — never triggered automatically by implement-issue, which handles its own verify-implementation findings directly. Use this for feedback already sitting on a PR from other sources (e.g. a human reviewer).
---

# Check PR Comments

Addresses review feedback on an issue that's already implemented — does not re-implement or create a new branch/PR. When the brief says `mode: non-interactive`, apply the non-interactive rules from the conventions wherever this skill would stop for the user.

Branch/slug format, the Knowledge discipline, written-deliverable sizing, and the delegation rule are defined in `../_shared/conventions.md` (relative to this skill's directory).

GitHub operations: `../_shared/github.md` — the `gh` commands below are the reference form.

## 1. Identify the issue and its branch

- Accept an issue number or a PR number. If genuinely unclear, ask.
- PR number: `gh pr view <number>` directly. Issue number: find the PR whose head branch is `issue/<issue-number>-*` (`gh pr list --search "head:issue/<issue-number>-"`).
- `git switch` to that branch; do not create a new one. If it is checked out in another worktree, work on it detached per `../_shared/runtime-adapters.md`.

## 2. Gather context and feedback

- Read the original issue in full — its acceptance criteria are the triage checklist.
- Fetch the feedback: all PR comments and unresolved review threads (`gh pr view <number> --comments`).
- If the feedback concerns UI, styling, or any brand-facing output, also read `.project/Branding/BRAND.md`, if present, and fix against it — don't invent brand decisions the guide already made.
- Consult `.project/Knowledge/`, if present, per the conventions discipline: read only name-relevant entries. A comment that contradicts a captured convention is worth flagging in the reply rather than silently following; an entry asserting a checkable state your investigation contradicts is not binding — proceed on what you observe and correct it in Step 4.

## 3. Triage and fix

- Judge each comment: valid and actionable, or not. For anything not actionable, reply explaining why instead of ignoring it. Non-interactive: leave such a review thread unresolved, and park once Step 4 has published the other fixes — whether to act on it is the owner's call.
- For each valid comment, make the fix, then determine this project's build/test commands from its manifests, scripts, or instruction file and run them — fix failures before proceeding.

## 4. Publish and report

- A Knowledge entry whose claim your work disproved: correct it in place per the conventions governance rule, and note the correction in the report. Anything else needing the project owner's attention (including a contradiction you couldn't settle): write `.project/Inbox/findings-<slug>.md`. Anything worth keeping for future implementations: add a new entry to `.project/Knowledge/<topic>/`.
- Update `.project/Reports/<slug>.md` with the new verification results.
- Commit and push the fixes, together with those `.project/` files, to the existing branch.
- Reply to each addressed comment confirming the fix, and resolve each addressed review thread (`resolveReviewThread` mutation via `gh api graphql`; thread IDs from the PR's `reviewThreads`).
- Non-interactive: before the result line, run one independent review exactly as `implement-issue` Step 9 and report its verdict as `unresolved` — the fixes must not merge on this session's own judgment.
