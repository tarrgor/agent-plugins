---
name: project-status
description: Fully refresh the local project status and report the single next workflow action. Use for "project status", "where do we stand", "what's next", or to reconcile a missing, stale or invalid status snapshot.
---

# Project Status

Read GitHub without mutating it. Resolve the project root (Git work tree root, otherwise current directory), then take a revision with the shared helper **before** gathering. Follow [status-snapshot.md](../_shared/status-snapshot.md), [conventions.md](../_shared/conventions.md), [next-action.md](../_shared/next-action.md) and [github.md](../_shared/github.md).

- Identify the active spec by `Status:` (including the legacy fallback), and record planned specs without issues. Get the milestone's GitHub state and **all** its issues with numbers, titles, state, labels and bodies. Include closed issues and resolve external dependencies. Use a sufficiently large limit or paginate; a truncated response is not a complete refresh.
- Read all open `issue/*` PRs, their check states and unresolved threads. Record pending findings per the shared rules and the most recent `.project/Archive/MEETING-<YYYY-MM-DD>.md` by filename. Distinguish empty data from read failures.
- On a complete read, write a full JSON input and run the helper's `replace` with the initial revision. If another writer changed the snapshot, re-gather from the new revision once; never overwrite intervening changes with old facts. For any remaining failure, explain it and leave the prior JSON and HTML intact.
- Read the normalized snapshot for one compact chat summary and exactly one next action when present. Highlight unusual conditions without inventing data. For backwards compatibility render `STATUS.html` through [status-report](../status-report/SKILL.md), using its saved-snapshot path. A rendering failure doesn't invalidate the saved snapshot or chat summary; report it separately. End with the page path on success.
