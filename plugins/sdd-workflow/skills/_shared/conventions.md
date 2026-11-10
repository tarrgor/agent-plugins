# Workflow conventions

Shared rules for all skills in this workflow. Skills reference this file as `../_shared/conventions.md` relative to their own directory.

Host-specific subagent, shell, and worktree mappings are defined in `runtime-adapters.md` beside this file. Read that file when the current step delegates work, gives an OS-specific command, or runs inside a linked worktree.

GitHub operations are written as `gh` commands. Before the first one in a run, pick the access mode in `github.md` beside this file; without a working `gh`, perform each operation as mapped there.

## Branches and slugs

- `<slug>` = `<issue-number>-<kebab-title>` (e.g. `12-add-login`).
- Feature branch: `issue/<slug>`.
- Find an issue's PR: `gh pr list --search "head:issue/<issue-number>-"`.

## Base branch

`develop` if it exists locally or on the remote; otherwise the repository's default branch (`gh repo view --json defaultBranchRef`), typically `main`. Never create `develop` yourself.

## Committing to the base branch

The base branch is usually protected against direct pushes — never assume a commit can land there. Commit it, then `git push`; if the push is rejected (protected branch, required reviews, required checks), move the commit to a branch and open a PR instead:

```bash
git reset --soft HEAD~1
git switch -c <type>/<short-slug>
git commit -m "<message>"
git push -u origin <type>/<short-slug>
gh pr create --base <base> --fill
```

Then `git switch <base>` again, so later work doesn't land on the side branch. Report the follow-up PR number rather than claiming the change landed on the base branch. Never bypass protection (no `--admin`, no force-push). In a linked worktree, skip the commit entirely and report the change as pending.

## GitHub milestones

- Milestone title = the spec filename minus `SPEC-milestone-` and `.md` (`SPEC-milestone-001-auth-flow.md` → `001-auth-flow`). A legacy project with only `SPEC.md` uses `001-initial`.
- There is **no `gh milestone` subcommand** — create and close via the API. Create: `gh api repos/{owner}/{repo}/milestones -f title="<title>"`. Close: look up the number (`gh api repos/{owner}/{repo}/milestones --jq '.[] | select(.title=="<title>") | .number'`), then `gh api -X PATCH repos/{owner}/{repo}/milestones/<number> -f state=closed`.
- `gh issue create --milestone "<title>"` and `gh issue list --milestone "<title>"` accept the title directly.

## Spec `Status:` lifecycle

Every milestone spec's first line is `Status: <value>`: `Planned` (spec written, no issues yet) → `Active` (issues created) → `Done` (milestone closed). Legacy spec without the header: treat as `Active` if a matching GitHub milestone or issues exist, else `Planned`.

## Issue dependencies

A dependency on another issue is one line in the issue body: `Depends on #<number>` — exact prefix, own line, one line per blocker — so skills can parse it reliably.

## `.project/` layout

`Inbox/`, `Archive/`, `Knowledge/`, `Reports/`, `Branding/Assets/`.

Any skill writing into `.project/` creates that whole set if missing, not just the one directory it needs — the layout is then identical whichever skill reaches the project first, and later skills find what they expect. Use the host-native directory operation from `runtime-adapters.md`. Spec files are never pre-created as empty placeholders; the `Status:` lifecycle reads them. Root `CLAUDE.md` and `AGENTS.md` are `kick-off`'s alone — no other skill creates them.

## Knowledge

- **Consultation**: list `.project/Knowledge/` subdirectory and file names with the current host's native file-search capability (see `runtime-adapters.md`) and read only entries whose names plausibly relate to the task's area. Never read the tree wholesale; if nothing matches, skip it. Anything read (a convention, a gotcha, a past decision) is binding — unless it asserts a specific, checkable state of the code or an issue (e.g. "bug X is unfixed") that your own investigation contradicts; then trust what you observe and flag the entry as stale.
- **Researched entries**: an entry with `type: research` frontmatter (written by `research-topic`) records external sources, not observed project fact. It carries a `researched:` date and a `confidence:` level — weigh it accordingly, and treat a low-confidence or long-stale entry as a starting point to re-check rather than as binding.
- **Governance**: any skill may add a **new** entry under `.project/Knowledge/<topic>/`. It may also correct a claim in an **existing** entry in place, without asking, when its own investigation disproves that claim and the correct value is unambiguous — fix the wrong claim, leave the rest of the entry untouched, and note the correction in the report or findings file it is already writing. Everything else — deleting an entry, rewriting or restructuring it, or a contradiction you cannot settle by observation — goes through `.project/Inbox/` findings for `project-meeting` to resolve.

## Written deliverables

Every file these skills write — `.project/Reports/`, `Inbox/findings-*`, `Knowledge/`, `SPEC*`, `Archive/`, `Branding/BRAND.md` — is sized to its substance. Cover what the file is for, then stop: no filler sections, no restating the same point in a summary, no boilerplate heading over an empty section. A file with nothing to say isn't written at all.

## Delegation

`verify-implementation` and `research-topic` are the only subagents this workflow calls for — the first for reviewer independence, the second because deep web research reads far more text than its conclusions are worth. Do the rest directly — exploring the codebase, reading issues, running builds and tests, and checking your own work are all faster as direct tool calls than as delegated agents.

Invoke them using the current host mapping in `runtime-adapters.md`. Under Claude Code they ship in the `sdd-workflow` plugin and carry its prefix: `sdd-workflow:verify-implementation`, `sdd-workflow:research-topic`. Codex's research agent uses a read-only sandbox and a behavioral no-local-read rule; unlike the Claude manifest's web-only tool allowlist, this is not a technical local-read boundary. Never describe the two isolation levels as equivalent.

## Non-interactive mode

A skill runs non-interactively only when the brief that invoked it says `mode: non-interactive` (the `run-milestone` coordinator does). In that mode it never waits for the user:

- **A question only the user can answer** — park: add the `needs-decision` label to the issue and record the question with its options as a finding. If the issue has an open PR, write it to `.project/Inbox/findings-<slug>.md` on its branch; otherwise post it as an issue comment starting with `needs-decision:`, for the caller to file. Then stop.
- **Unsafe repository state** — stop and report it; don't ask.
- **A precondition not met** (an open blocker, an existing PR, a missing issue) — stop without changing anything.
- Before stopping, commit and push to the issue branch every file this run wrote that is still uncommitted, so nothing stays behind in the worktree.
- Last, record the outcome on GitHub, so it survives the caller being interrupted: remove the `in-progress` label from the issue, and for `RESULT: pr=<n> unresolved=none` add the `verified` label to the PR. Labels are created by the caller.

End the final message with exactly one result line, last:

- `RESULT: pr=<number> unresolved=<critical|high|none> — <summary>` — a PR is ready; `unresolved` is the highest severity the last review left open (`none` when nothing high or critical remains, or the review was skipped as code-free).
- `RESULT: parked — <question>` — stopped on a decision, as above.
- `RESULT: skipped — <reason>` — a precondition was not met; nothing changed.
- `RESULT: failed — <reason>` — anything else that ended without a usable PR.
