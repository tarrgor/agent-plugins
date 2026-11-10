# Next action

Shared decision rules for `project-status`, `merge-pr` and `run-milestone`. Milestone naming, the `Status:` lifecycle and the `Depends on #N` format are in `conventions.md` beside this file.

## Issue states

For an open issue in the active milestone:

- **Parked** — labelled `needs-decision`: waiting for a decision in the next meeting.
- **In progress** — labelled `in-progress`: a `run-milestone` session is working on it.
- **Blocked** — a `Depends on #<number>` blocker is still open.
- **In review** — a PR from `issue/<number>-*` is open.
- **Ready** — none of the above.

## Pending findings

The union, by filename, of:

- `.project/Inbox/findings-*.md` on the base branch, and
- `.project/Inbox/` files each open PR adds or changes (`gh pr diff <number> --name-only`), and
- `needs-decision:` comments on parked issues not yet filed as an Inbox file.

Counting beyond the base branch matters: issue work writes its findings on the issue branch, so they reach the base branch only on merge.

## Meeting due

Either:

- a pending finding is critical — needs immediate attention: a security risk, data loss, a broken build, or a blocker for other work; or
- three or more findings are pending.

## The next action

First match wins:

1. Meeting due → `project-meeting`.
2. An open issue PR with unresolved feedback or failing checks → `check-pr-comments` for that PR.
3. An open issue PR that is clean → `merge-pr` for that PR.
4. A ready issue → `implement-issue #<n>` (lowest such number).
5. No ready issue, but a parked one → `project-meeting`, to make the decisions they wait on.
6. A `Planned` spec with no issues yet → `create-spec-issues`.
7. All milestone issues closed but the milestone still open (on GitHub or spec not `Done`) → `project-meeting`, to decide with the user whether to close it.
8. Milestone closed (or no active spec) → `kick-off` the next milestone.
