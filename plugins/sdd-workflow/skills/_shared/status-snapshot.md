# Local project status contract

`project-status` does a full reconciliation. `status-report` renders without gathering. Workflow mutations update only the affected parts of the existing snapshot after confirmation, without running either skill or automatically regenerating HTML. Keep these generated files out of commits: `/.project/status.json`, `/.project/status.json.lock`, `/STATUS.html`. The helper adds missing entries to the root `.gitignore`. Never stage generated files, including if the repo already tracks them.

Run from any directory, with the project work-tree root and the bundled script addressed explicitly. See [runtime adapters](runtime-adapters.md) for Python on each host:

```
python3 <scripts/status-snapshot.py> <root> revision
python3 <scripts/status-snapshot.py> <root> replace <full.json> --expect <revision>
python3 <scripts/status-snapshot.py> <root> patch <delta.json> --expect <revision>
```

Read the revision before gathering facts for any write. Inputs are UTF-8 files outside the repo or stdin (`-`); never put JSON or user-written titles in a shell word. On contention, read the new revision and re-confirm only the affected facts (full gather for `replace`). If missing or invalid, skip incremental writes; tell the user to run `project-status` next time they need the report. Do not fail or retry the original GitHub mutation because a local status update failed. Discard a delta if its supposed facts have been overtaken. The store is per work tree; for workflows in child work trees, the coordinator updates its own snapshot from verified outcomes, not by copying a worker's snapshot.

## Full input

- `project`: `name`, `repo` (owner/name), `base` (branch).
- `milestone`: null or `{"title":"M001 – Name","needs_close":true}`; true when the active spec is not Done or GitHub's milestone is still open. `planned`: titles of Planned specs with no issues yet.
- `issues`: all active milestone issues as `{"number":12,"title":"…","closed":false,"labels":[],"depends_on":[5]}`. Record all blocker numbers from the issue bodies, even currently closed ones. `external_blockers` maps blocker numbers outside this milestone (string keys) to true for open, false for closed. Don't invent a state; an absent blocker is treated as open until confirmed.
- `prs`: all open issue PRs as `{"number":30,"title":"…","branch":"issue/12-slug","checks":"pending","unresolved":0}`. Check states: passing, failing, pending, none. None means verified no check runs, not an unavailable read.
- `finding_items`: map of distinct pending items per [next-action.md](next-action.md), keyed by Inbox filename or a stable GitHub comment ID for an unfiled question. Values are null for ordinary items or a short summary for critical items. The helper derives the count and critical list. `last_meeting`: ISO date or null. Optional `flags`: short additional warnings. Keep empty arrays/objects, not omitted fields.

The helper computes `generated`, issue `state`/`blocked_by`, milestone `closed`/`total` and `next` (`action`, `skill`, `command`, or null) for the existing HTML renderer. It maintains `_status` with format version, revision, UTC last full refresh and last change, and a flag when part of the view needs manual reconciliation. Caller-supplied renderer-only reports may use the original display fields without a stored revision.

## Incremental input

Send only the affected facts in one JSON delta for the confirmed operation:

| Event | Delta |
| --- | --- |
| Issue PR opened or feedback/checks changed | Upsert a confirmed open PR by number in `prs` with the current review/check facts. For new checks still running, use `pending`. |
| Issue PR merged or closed | Remove its number in `remove_prs`. If GitHub also confirms an issue closure, upsert the closed issue when in scope, or record false in `external_blockers` for a tracked external dependency. Don't infer closure from PR text. |
| Issue labels, issue reopened or new issue in current milestone | Upsert the affected issue(s) by number in `issues`. Apply only to the snapshot's active milestone. For external dependency changes patch only `external_blockers`. |
| Spec created as Planned; milestone activated or closed | Update `planned` as applicable. Activation or closure sends `milestone`, its complete scoped `issues` and `external_blockers` together, using empty collections for no milestone. Include new issues at activation. Don't reuse the previous milestone's issue list. |
| Published/discarded Inbox finding, parked question, changed finding source or archived meeting | Update affected keys with `finding_upserts` (same map shape) and `remove_findings` (array of keys). Remove a key only when no source still contributes it, and remove the unfiled-comment key when its question is filed. Update `last_meeting` from the archive. For uncertain source coverage or criticality, preserve the corresponding items and set `"refresh_needed":true`. |

For any change that invalidates free-form `flags`, recompute the affected flags or clear them and set `refresh_needed`; omit unrelated fields. Use the affected resource only, not a whole-project rescan. No Spaces integration or publication in this workflow.
