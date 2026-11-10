---
name: run-milestone
description: This skill should be used to work through the active milestone's ready issues unattended — implementing, reviewing and merging them in parallel sessions — until the next project meeting is due. Trigger phrases include "run the milestone", "work through the issues", "keep going until the next meeting", "continue the run", or whenever the user wants the issue loop to run without them. Claude Code desktop app and Codex desktop with chat tools; not CLI or IDE. Never creates issues, edits specs, closes milestones or resolves findings.
---

# Run Milestone

Coordinates; never implements, reviews or fixes anything itself. Every issue runs in its own session, which uses the existing skills in non-interactive mode and records its outcome on GitHub labels.

Rules used here: `../_shared/next-action.md` (issue states, pending findings, meeting due), `../_shared/conventions.md` (base branch, committing to it, non-interactive mode and its `RESULT:` line), and `../_shared/runtime-adapters.md` § Units of work (starting, messaging and stopping sessions) — all relative to this skill's directory.

**Codex desktop only:** before any action, read [references/codex-desktop.md](references/codex-desktop.md). Its Codex-specific rules replace the corresponding session, permission, recovery and merge details below. Claude Code skips this reference and follows the steps below unchanged.

## 1. Preconditions

- Host: only where § Units of work names a mapping. Otherwise say this skill is unsupported here and stop.
- Active milestone per `next-action.md`; none → stop and name `project-status`.
- Started sessions inherit this session's permission mode. If it asks before `git` or `gh` commands, sessions will wait on prompts and the run stalls — say so and let the user change it before starting.
- Normal checkout on the base branch, clean apart from untracked files; `git pull --ff-only`. Otherwise stop and report.
- Labels exist: `gh label create <name> --force` for `needs-decision`, `in-progress`, `verified`.

## 2. Run policy

Read `.project/RUN-POLICY.md`. Missing — write it with the user, confirming each value, then commit it per the base-branch rule:

```markdown
parallel: 2                    # concurrent sessions, 1–3
merge-into-default-branch: no  # yes allows autonomous merges when the base branch is the repository default
```

A run never changes the policy.

## 3. Loop

Repeat until Step 4 applies; re-evaluate after every session result and every merge. Feedback means unresolved review threads — plain PR comments are not seen by the run.

1. **File parked questions** — each `needs-decision:` issue comment not yet filed: write it to `.project/Inbox/findings-<slug>.md` and commit it per the base-branch rule.
2. **Stop check** — meeting due per `next-action.md` → Step 4. Running sessions finish; nothing new starts and nothing more is merged.
3. **Feedback** — an open `issue/*` PR with unresolved review threads whose issue is neither `needs-decision` nor `in-progress`: remove `verified`, label the issue `in-progress`, start a session (as in step 5) with the brief `Run the check-pr-comments skill for PR #<n> with mode: non-interactive. End with its RESULT line.`
4. **Merge** each open `issue/*` PR that passes every gate:
   - labelled `verified`, and its issue is neither `needs-decision` nor `in-progress`;
   - no unresolved review threads;
   - targets the base branch; if that is the repository default branch, the policy allows it;
   - no pending finding the PR adds says it must not merge as is.

   Run `merge-pr` for it. If `merge-pr` stops on a blocker (conflict, protection, failing checks): remove `verified`, record the blocker in `.project/Inbox/findings-<slug>-merge.md`, commit it, and leave the PR for the meeting. After a merge: `git pull --ff-only` and run the project's full build and tests on the base branch. A failure is a critical finding: write it to `.project/Inbox/findings-run-<YYYY-MM-DD>-broken-build.md`, commit it, go to Step 4.
5. **Start** — while fewer sessions run than `parallel`: take the ready issues, lowest number first, run `estimate-issue` on each, and pick one whose expected files overlap neither a running session's nor an open PR's (`gh pr diff <n> --name-only`). Label it `in-progress`, then start the session per § Units of work, with the tier's model and effort from § Model selection:
   - brief: `Run the implement-issue skill for issue #<n> with mode: non-interactive. End with its RESULT line.`
   - background: the repository, the base branch, that this is one issue of an unattended `run-milestone` run, and that the final `RESULT:` line is the only report read.

   If the host refuses to start a session, start no more; go to Step 4 once nothing runs, with that as the reason.
6. **Wait** for the next session to end its turn, then handle its result:

   | Result | Action |
   |---|---|
   | `pr=<n> …` | Confirm the PR exists and its body has `Closes #<issue>`; otherwise treat as `failed`. With `unresolved=high` or `critical` the PR stays unmerged — the session filed the finding. |
   | `parked` | Nothing — step 1 files the question. |
   | `skipped` | Park the issue: `needs-decision` label and a `needs-decision:` comment with the reason. |
   | `failed`, or no `RESULT:` line | First time: send that session one message to continue in non-interactive mode and end with its `RESULT:` line. Second time: stop the session and park the issue with a comment describing both attempts. |

   Whatever the result, make sure the issue no longer carries `in-progress` unless a retry is running.
7. Nothing running and nothing left to file, merge or start → Step 4.

If the app stops continuing this session before Step 4, re-running this skill resumes from GitHub and `.project/`; sessions that finished meanwhile have already recorded their outcomes. An issue still labelled `in-progress` belongs to a session from an earlier run that is still working or died: leave it and list it in the report; the user removes the label to retry it.

## 4. Stop and report

- Wait until no started session is still working, handling each result as in step 6 but without retries, then file parked questions (step 1).
- Write `.project/Reports/run-<YYYY-MM-DD>-<n>.md` (`<n>` counts that day's runs): PRs merged, issues parked with their questions, findings raised, issues left `in-progress`, sessions that ran below their tier's model, and why the run stopped. Commit it per the base-branch rule.
- Notify the user where the host can, one line: why it stopped and what waits on them.
- Name the next step: `project-meeting` when a meeting is due or issues are parked; otherwise the first match of the order in `next-action.md`.
