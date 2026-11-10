---
name: migrate-project
description: This skill should be used to bring an existing project that doesn't follow this workflow into it — migrating its planning documents, learnings, and GitHub issues into the `.project/` structure and a milestone. Trigger phrases include "migrate this project", "onboard this project into the workflow", "adopt the workflow here", "make this project compliant", "convert this project to the spec workflow". Re-runnable on partially-migrated projects — it migrates only what's missing.
---

# Migrate Project

Brings an existing, non-compliant project into this workflow: inventories what exists, maps it to workflow artifacts, and migrates with the user's confirmation. Does not implement anything and does not decompose new work into issues — that stays with `create-spec-issues`.

Slug/branch format, base branch, milestone commands, the `Status:` lifecycle, the `.project/` layout, the Knowledge rules, written-deliverable sizing, and the delegation rule are defined in `../_shared/conventions.md` (relative to this skill's directory).

GitHub operations: `../_shared/github.md` — the `gh` commands below are the reference form.

## 1. Survey the current state

Everything discoverable is a **fact** — never ask the user for it.

- Read the README, manifests, and source layout. Hunt for planning/progress documents anywhere in the repo: `TODO.md`, `PLAN.md`, `ROADMAP.md`, `NOTES.md`, `SPEC*`, `docs/`, notes folders, an existing partial `.project/`.
- Read any existing `CLAUDE.md`/`AGENTS.md` — they may predate this workflow; never assume the template.
- GitHub state: `gh repo view`; existing issues (open and closed), milestones, open PRs, and the branch-naming pattern in use.
- Diagnose compliance against this workflow: which `.project/` dirs and files exist, `Status:` headers present, Knowledge layout, milestone linkage. Sort everything into three buckets: **compliant** (skip), **missing**, **non-compliant**.
- On a re-run, read any previous `.project/Archive/MIGRATION-*.md` record first — already-migrated material is not re-proposed.

## 2. Require GitHub

Run `gh repo view` (requires a GitHub remote and a working `gh auth status`). The workflow runs on GitHub — there is no offline fallback.

- No GitHub repo yet: tell the user, and offer to create one (`gh repo create`) — ask for name and visibility, and only run it once they confirm.
- `gh` missing or unauthenticated: say exactly what's missing and stop.

## 3. Propose the migration map

For every discovered artifact from the missing/non-compliant buckets, propose a destination — present it as a compact source → destination table, with gaps marked:

- Vision, goals, architecture material → `.project/SPEC.md`.
- Current or in-flight work plans → `.project/SPEC-milestone-<###>-<slug>.md` (numbering per conventions; `Status: Active` if matching issues or work exist, else `Planned`).
- Reusable learnings, gotchas, decisions → `.project/Knowledge/<topic>/`.
- Open questions, ideas, risks, still-live TODOs → `.project/Inbox/findings-migration-<topic>.md`.
- Brand material (logos, palettes, style notes) → `.project/Branding/`.
- Notes about completed work and obsolete docs → `.project/Archive/`.
- Existing open GitHub issues → attach to the milestone. Never rewrite issue bodies; an issue lacking acceptance criteria becomes an Inbox finding, not an edit.
- Branches or PRs with foreign naming → note only; never rename branches or touch open PRs.
- Material too thin for a real spec (no clear vision, no milestone scope): mark the gap explicitly — it becomes a `kick-off` recommendation in Step 7, not an inline interview.

## 4. Interview one question at a time

Only about decisions the survey can't settle: an ambiguous doc mapping, which TODOs are still live, where the current milestone ends and backlog begins. One question per turn, with a recommended answer and short rationale — same discipline as kick-off. Never ask about facts.

## 5. Confirm before migrating

Summarize the full migration plan, including every file that will move to `.project/Archive/`. Write nothing until the user explicitly confirms.

## 6. Execute the migration

Migrate only the missing/non-compliant items from Step 1's diagnosis:

- Scaffold missing `.project/` dirs and root `CLAUDE.md`/`AGENTS.md` per kick-off's Step 1 rules (template copy, never overwrite). If a foreign `CLAUDE.md` exists, offer to append the `.project/` legend section from kick-off's template — with confirmation, never replacing existing content.
- Write or update `.project/SPEC.md` with the distilled vision; mark unresolved areas "TBD — run kick-off".
- Write the milestone spec(s) with the correct `Status:` header.
- Learnings → new Knowledge entries (grouping and governance per conventions).
- Open items → Inbox findings files.
- GitHub adoption: create the milestone per conventions if missing (`gh api` — there is no `gh milestone` subcommand), then attach the confirmed open issues: `gh issue edit <n> --milestone "<title>"`.
- `git mv` each migrated source doc to `.project/Archive/` (names preserved), and write `.project/Archive/MIGRATION-<YYYY-MM-DD>.md`: the source → destination map, adopted issues, and remaining gaps. This record is the re-run marker.
- Commit on the base branch (per conventions), staging only the migrated and moved files — never unrelated working-tree changes; if a feature branch is checked out and switching is unsafe, stop and ask — then push. If the push is rejected because the base branch is protected, fall back to the branch-and-PR flow in `../_shared/conventions.md` (branch `chore/migrate-project`) and report that PR instead. Note that `git mv` renames are part of the commit, so the PR carries the archive moves too.

## 7. Report and suggest the next step

Summarize compliance: what was migrated, what was already compliant, what gaps remain. If `.project/.obsidian/` does not exist, add a one-line hint that the user can run `/sdd-workflow:create-obsidian-vault` to browse the migrated docs in Obsidian — never run it yourself, it is user-invoked only. Then name the next step, first match wins: vision or milestone-scope gaps → `kick-off`; a `Planned` spec → `create-spec-issues`; otherwise → `project-status`.
