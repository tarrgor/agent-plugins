---
name: implement-issue
description: This skill should be used to implement a single GitHub issue from a fresh, unimplemented state. Trigger phrases include "implement issue 12", "work on this ticket", "fix issue X", "resolve this issue", or whenever the user wants the full issue-to-PR workflow. If the issue already has a branch/PR, use check-pr-comments instead.
---

# Implement Issue

Follow this workflow end to end. Keep the user informed at important transitions, but continue autonomously unless a blocking question or unsafe repository state requires their input. When the brief says `mode: non-interactive`, apply the non-interactive rules from the conventions wherever this skill would stop for the user, and end with their result line.

Branch/slug format, base-branch rule, `Depends on #N` format, the Knowledge discipline, written-deliverable sizing, and the delegation rule are defined in `../_shared/conventions.md` (relative to this skill's directory).

Read `../_shared/runtime-adapters.md` before branch setup or subagent invocation. Preserve the Claude Code path described there; use the Codex path only when running under Codex.

GitHub operations: `../_shared/github.md` — the `gh` commands below are the reference form.

## 1. Identify the issue and check for an existing implementation

- Identify the GitHub issue by number. If genuinely unclear, ask.
- Search for a PR whose head branch is `issue/<issue-number>-*` (`gh pr list --search "head:issue/<issue-number>-"`).
- **Found one** — this issue is already implemented. Stop and tell the user to use the `check-pr-comments` skill instead; do not refresh the base branch, create a branch, or touch the existing one.
- **Found nothing** — check for blockers: if the issue body contains `Depends on #<number>` lines, check each blocker's state (`gh issue view <n> --json state`). Any still open — stop, list the open blockers, and offer to implement one of them instead. All closed (or none listed) — continue to Step 2 as a fresh implementation.

## 2. Determine the checkout mode and refresh the base

- `git fetch` first. Check `git status`, current branch, remotes, and whether this is a linked worktree (per `runtime-adapters.md`). Never discard, stash, or sweep in unrelated user changes without explicit permission — if uncommitted changes make branch setup unsafe, stop and ask.
- The base branch follows the shared convention: `develop` if it exists, else the repository's default branch. Single-branch projects are supported — don't create `develop` yourself.
- In a normal checkout, update it with a fast-forward-only pull:
  ```bash
  git switch <base>
  git pull --ff-only
  ```
- In an existing linked worktree, do not switch another checkout or create a nested worktree. Fetch and verify the intended base ref. A detached `HEAD` is expected in a Codex-created worktree.

## 3. Review the issue

- Read any project instruction file (`CLAUDE.md`, `AGENTS.md`) and the relevant code/tests before acting.
- Fetch the issue's title, body, labels, linked context, and all comments (`gh issue view <number> --comments`).
- If the issue touches UI, styling, or any brand-facing output, also read `.project/Branding/BRAND.md` and `.project/Branding/Assets/`, if present, and implement against them (palette, typography, voice, logo/asset usage) — don't invent brand decisions the guide already made.
- Consult `.project/Knowledge/`, if present, per the conventions discipline: read only name-relevant entries; what you read is binding unless a checkable claim is contradicted by your own investigation — then trust what you observe and correct the entry in Step 6.
- Restate the acceptance criteria internally; do not implement from the title alone.
- If something genuinely blocks a correct implementation (not resolvable from the codebase or convention), post one concise comment on the issue explaining the ambiguity, then stop and wait. Resume once answered. Non-interactive: park instead.

## 4. Create the branch

- In a normal checkout, branch from the freshly updated base branch:
  ```bash
  git switch -c issue/<slug>
  ```
  `<slug>` is `<issue-number>-<kebab-title>` (per conventions).
- In an existing linked worktree, keep the worktree and create the issue branch there. If detached, create it directly from the verified remote/base ref (for example `git switch -c issue/<slug> origin/<base>`). If already on the intended issue branch, continue; if on another branch or dirty in a way that makes the correct base ambiguous, stop and ask.
- Don't reset or overwrite an existing branch of that name — Step 1 already handles the case where one exists.

## 5. Implement and verify

- Inspect the affected architecture, nearby implementations, and existing tests before editing.
- Implement the smallest complete change that satisfies the issue and its acceptance criteria — no unrelated refactors.
- Add or update tests for every behavioral change. If a change has no meaningful layer for a test category, explain why in the final report instead of adding a vacuous test.
- Determine this project's build/test commands from its manifests, scripts, or instruction file, and run them after each coherent change. Fix failures before proceeding — do not publish with known relevant failures.
- **Code-free change** — if the diff touches no executable code (documentation, prose, generated assets and similar), skip the build/test runs and the independent review in Step 9, and state the skip and its reason in the report. Any edit to source, scripts, build files, or configuration the code reads is not code-free; when in doubt, run them.
- Review the final diff and `git status`: implementation matches the issue, tests cover the behavior, no unrelated files included.

## 6. Capture findings and knowledge

- A Knowledge entry whose claim your own work disproved — correct it in place, per the conventions governance rule: fix the wrong claim, leave the rest of the entry alone, and record the correction in the report (Step 8). Only raise it as a finding instead when the correct value isn't unambiguous, or when fixing it would mean rewriting or deleting the entry.
- Anything else found during implementation that needs the project owner's attention (scope gaps, follow-up work, potential new issues, risks, a Knowledge contradiction you couldn't settle) — write `.project/Inbox/findings-<slug>.md` describing it, for review at the next project meeting.
- Anything learned worth keeping for future implementations (a gotcha, a convention, an architectural decision, a reusable pattern) — write it into `.project/Knowledge/`, in a subdirectory grouped by general topic (e.g. `architecture/`, `testing/`, `tooling/`); create a new subdirectory when nothing existing fits.

## 7. Publish

- Commit only the issue-related changes, with a message referencing the issue.
- Push the branch and open a non-draft PR targeting the base branch from Step 2 (`gh pr create --base <base>`), with a summary and the verification commands that passed.
- **The PR body must include `Closes #<number>` on its own line** so GitHub auto-closes the issue on merge. Verify this line is present in the created PR before reporting completion — do not rely on a generic PR template to add it.

## 8. Report completion

Write `.project/Reports/<slug>.md` — a short report of what was implemented and how it was verified. `project-meeting` and `project-status` read these reports; issue-level dedup lives in the GitHub milestone, not here.

## 9. Independent review

Skip this step and Step 10 for a code-free change (Step 5) and go straight to Step 11.

- Launch the `verify-implementation` agent as a subagent so it reviews with its own fresh context. Give it the issue number and PR number. Under Claude Code, use the Agent tool with `subagent_type: sdd-workflow:verify-implementation`. Under Codex, spawn the installed `verify-implementation` custom agent using the mapping in `runtime-adapters.md`.
- Wait for it to finish — do not proceed, merge, or report done while it is running. It returns its findings directly in its final message; it does not post to the PR.

## 10. Address the review findings

This is the filter stage: the review reports for coverage, so expect low-severity and low-confidence findings among the real ones. Filtering here is the point — do not act on everything returned.

- Findings returned: judge each one against the issue's acceptance criteria — valid and actionable, or not. Rank by the reported severity and confidence. For anything not actionable, note why in one line instead of acting on it. Never dismiss a high or critical finding on your own judgment: fix it, or leave it open for Step 11.
- For each valid finding, make the fix, then re-run the project's build/test commands; fix failures before proceeding.
- Stale knowledge findings aren't code fixes: confirm the reviewer's claim against the code yourself, then correct the entry in place as in Step 6. If you can't confirm it, or the right value is ambiguous, add it to this issue's `.project/Inbox/findings-<slug>.md` instead.
- Commit and push the fixes to the existing branch.
- **Re-review** when this round fixed a high or critical finding: return to Step 9 for a fresh review, telling the reviewer which high or critical findings the previous round raised so it confirms they are gone. At most two fix rounds (three reviews). If a review reports the approach itself as wrong, end the loop — that is the user's decision (Step 11).
- Otherwise — no findings, or only low or medium ones — say so; do not re-run the review.

## 11. Suggest the next step

End by naming the next step: all findings addressed, none returned, or the review skipped as code-free → suggest `merge-pr`; anything unresolved or disputed, or an approach the reviewer reports as wrong → suggest the user review it and run `check-pr-comments` afterwards.

Non-interactive: write every high or critical finding still open after the last round, and a reported wrong approach, to `.project/Inbox/findings-<slug>.md`, then commit and push; a wrong approach also parks the issue. The result line reports the last review's verdict, not your own assessment.

## Failure handling

- If auth, permissions, network, or CI blocks progress, preserve completed work and report the exact blocker.
- If requirements conflict with repository rules or constraints, comment on the issue (or tell the user) rather than guessing.
