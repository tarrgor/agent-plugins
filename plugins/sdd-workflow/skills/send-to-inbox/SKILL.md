---
name: send-to-inbox
description: This skill should be used to drop a requirement, idea, or observation into the `.project/Inbox/` of another workflow project, from whatever directory the session runs in. Trigger phrases include "put this in the inbox of PROJECT", "send this to PROJECT's inbox", "note this for PROJECT", "file this as a finding in PROJECT", "PROJECT needs to know that…". Writes one findings file into the target project; never touches the current project, code, issues, or specs.
---

# Send to Inbox

Turns a short note from the user into a self-contained finding and writes it to the target project's `.project/Inbox/`, where `project-meeting` triages it.

The `.project/` layout and written-deliverable sizing are defined in `../_shared/conventions.md` (relative to this skill's directory). Use `../_shared/runtime-adapters.md` for host-specific file listing, directory creation, and date.

## 1. Resolve the target project

- The user names the target as a path or a project name. A path is used as given (`~` expanded).
- A bare name: look for a directory of that name that contains `.project/` — first as a sibling of the current project root, then under the parent of that. Exactly one match → use it. Several or none → list what was found and ask for the path. Never guess.
- The target must contain `.project/`. If it doesn't, say so and stop — creating a project's workflow layout belongs to `kick-off` or `migrate-project`, not here.
- The target is the current project itself: proceed, but say so in the report.

## 2. Gather context

The finding is read later, in the target project, by someone who wasn't in this conversation. Collect what it needs to stand alone:

- **From the user's note and the current conversation**: what is needed, why, and what triggered it — e.g. a limitation hit while working in the source project, an interface the source project depends on, an idea that came up.
- **From the source** (the current working directory, if it is a different project): its name and the concrete detail that motivates the request — the API call, file, error, or behaviour involved. Read only what the note points at.
- **From the target**: the newest `.project/SPEC*.md` (by `Status: Active`, else newest milestone, else `SPEC.md`) — skim only enough to phrase the request in the target's own terms and to spot whether the spec already covers or contradicts it. List `.project/Inbox/findings-*.md`; if one already covers this, show it and ask whether to append to it or write a new file.

Missing a fact the finding can't be understood without (what exactly is needed, or why)? Ask — one question at a time, with a proposed answer.

## 3. Draft the finding

```markdown
# <Concise title stating the requirement>

- **Date**: <YYYY-MM-DD>   # current local date from the runtime adapter, never guessed
- **From**: <source project name or path, or "user" if no project context>
- **Type**: requirement | idea | bug | question

## Context
<What led to this, with the concrete source-side detail. Enough to understand it without the source project at hand.>

## Request
<What the target project should do or decide, as an outcome — not an implementation, unless the user specified one.>

## Notes
<Only if there is something: relation to the target's spec (already covered / contradicts section X), constraints, deadlines, open questions.>
```

Write it in the language the target's `.project/` documents use. Size it to its substance; drop `Notes` if empty.

## 4. Confirm, then write

- Show the draft and the target path `.project/Inbox/findings-<kebab-title>.md` (append `-2`, `-3` … if the name is taken). Write nothing until the user confirms; apply requested changes and show again.
- Create the target's `.project/` layout directories if any are missing, per conventions.
- Write the file. Do not commit — the target may have unrelated work in progress or another branch checked out; `project-meeting` commits the Inbox when it consumes the finding.

## 5. Report

State the written path and the title. Recommend `project-meeting` in the target project to triage it.
