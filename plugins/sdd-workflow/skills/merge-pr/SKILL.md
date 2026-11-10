---
name: merge-pr
description: This skill should be used to merge an open, reviewed pull request back into its base branch, identified by its issue number or PR number. Trigger phrases include "merge PR 12", "merge this PR", "merge issue 12", "land this branch", or whenever an approved implementation is ready to merge.
---

# Merge PR

Merges an approved PR into its base branch and cleans up the branch — does not review or implement anything.

GitHub operations: `../_shared/github.md` — the `gh` commands below are the reference form.

The base branch is whatever the PR targets: `develop` where the project has one, otherwise the default branch (typically `main`). Read it off the PR (`gh pr view <number> --json baseRefName`) rather than assuming.

## 1. Identify the PR

- Accept an issue number or a PR number. If genuinely unclear, ask.
- PR number: `gh pr view <number>` directly. Issue number: find the PR whose head branch is `issue/<issue-number>-*` (`gh pr list --search "head:issue/<issue-number>-"`).

## 2. Verify it's ready

- Confirm the PR is open, targets the expected base branch, has no unresolved review threads, and has no failing required checks (`gh pr checks <number>`).
- If blocked — failing CI, unresolved comments, merge conflicts — stop and report the blocker instead of force-merging.

## 3. Merge and delete the branch

- Check whether the current directory is a linked git worktree, not the main checkout: `git rev-parse --git-common-dir --git-dir` — if the two paths differ, it's a worktree. (Also visible via `git worktree list`.)
- **Normal branch (not a worktree):** `gh pr merge <number> --squash --delete-branch`. Always use the squash merge method. Confirm the remote branch was deleted; if `--delete-branch` didn't remove it, delete it explicitly.
- If the merge is rejected by branch protection (missing approvals, required checks), stop and report what protection requires. Never bypass it with `--admin`.
- **Linked worktree, or the head branch checked out in another worktree** (`git worktree list`): the local branch belongs to that worktree and its session — do not delete it and do not switch it. Merge without `--delete-branch` (`gh pr merge <number> --squash`), then delete only the remote branch (`git push origin --delete <branch>`). Leave the local branch and worktree alone.

## 4. Clean up locally

Only for a normal branch (skip entirely for a linked worktree — no switch, no branch deletion, no pull there; when the head branch is checked out in another worktree, skip only the `git branch -d`):

```bash
git switch <base>
git branch -d <head-branch>   # from gh pr view <number> --json headRefName
git pull --ff-only
```

## 5. Report

Confirm the merge and remote branch deletion. For a normal branch, also confirm the local branch was deleted and the base branch is up to date; for a linked worktree, note that the local branch was left in place. Note the issue this closed and, if it was the last open issue in its milestone (`gh issue view <issue-number> --json milestone`, then `gh issue list --milestone "<title>" --state open` — treat the just-merged issue as closed even if it still shows open), say so. Never close the milestone here — that is `project-meeting`'s job.

## 6. Check the Inbox and suggest the next step

Use the rules in `../_shared/next-action.md` (relative to this skill's directory), counting the just-merged PR and its issue as closed.

- Meeting due → recommend `project-meeting`, naming the critical finding(s) or the count. Keep it to a brief hint at the end of the report; do not open, triage, or act on the findings — that is the project meeting's job.
- Otherwise suggest the first match of its next-action order.
