---
name: kick-off
description: This skill should be used when starting a brand new project (empty or near-empty project directory) or when kicking off a new milestone in an existing codebase. Trigger phrases include "kick off this project", "let's start this project", "kickoff", "new milestone", "spec this out", "interview me about this idea", or whenever the user has a rough idea or plan they want turned into a formal, mutually-confirmed spec before any code is written.
---

# Kick-off

Runs on an empty/near-empty project directory (new project) or to scope a new milestone in an existing codebase. Turns a rough idea into a confirmed spec — does not implement anything.

The `.project/` layout, written-deliverable sizing, and the delegation rule are defined in `../_shared/conventions.md` (relative to this skill's directory).

GitHub operations: `../_shared/github.md` — the `gh` commands below are the reference form.

## 1. Set up project files

- Create the `.project/` directories if missing, per the layout in `../_shared/conventions.md`.
- Create if missing: root `CLAUDE.md`, copied verbatim from this skill's `references/CLAUDE.md.template`; and root `AGENTS.md` containing just `Read CLAUDE.md.`. Never overwrite either if it already exists.
- If a codebase exists, read the README, manifests, source layout, `.project/SPEC.md`, and any `.project/SPEC-milestone-*.md` first. Anything discoverable this way is a **fact** — never ask the user for it.

## 2. Require GitHub

The whole workflow runs on GitHub issues and PRs — there is no offline fallback.

- Verify with `gh repo view` (needs a GitHub remote and a working `gh auth status`).
- Fails because the project has no GitHub repo: tell the user, and offer to create one (`gh repo create`) — ask for visibility and name, and only run it once they confirm.
- Fails because `gh` isn't installed or authenticated: tell the user exactly what's missing and stop; don't work around it.

## 3. Map the decision tree

Sketch the decision branches this plan touches — problem/goal, target users, scope (in/out), core workflows, data model, architecture/stack, integrations, non-functional requirements, milestone plan, risks — scoped to what's actually relevant, expanding into sub-branches as answers reveal dependencies.

## 4. Interview one question at a time

- One question per turn; wait for the answer before asking the next.
- Propose a recommended answer with a short rationale for every question.
- Ask only about **decisions**. Never ask about **facts** obtainable from the codebase — look those up instead.
- Resolve branches in dependency order — don't ask about something whose answer depends on an unresolved earlier decision.
- Keep going until every relevant branch is resolved, not just until "enough."

## 5. Confirm before writing

Summarize the full plan. Do not write anything until the user explicitly confirms it's correct and complete.

## 6. Write the spec

- `.project/SPEC.md` holds only the project vision: problem/goal, target users, architecture/stack, non-functional requirements, long-term roadmap. It changes rarely — later changes are amendments, not rewrites.
- `.project/SPEC-milestone-<###>-<slug>.md` holds one milestone's concrete detail: scope (in/out), workflows, data model, acceptance-level detail. Number sequentially, zero-padded to 3 digits (`001`, `002`, ...) — find the highest existing `SPEC-milestone-<###>-*.md` directly under `.project/` and use `+1`, starting at `001`.
- Every milestone spec's first line is `Status: Planned` (lifecycle per `../_shared/conventions.md`, relative to this skill's directory); `.project/SPEC.md` itself carries no status.
- New project: write both `.project/SPEC.md` and the first milestone spec (`SPEC-milestone-001-<slug>.md`).
- New milestone in an existing codebase: write only the next milestone spec; leave `.project/SPEC.md` untouched unless the vision itself changed, in which case amend it rather than rewriting it.
- Documentation only — do not implement the plan.

## 7. Suggest the next step

End by suggesting `create-spec-issues` to break the confirmed spec into issues.

If `.project/.obsidian/` does not exist, add a one-line hint that the user can run `/sdd-workflow:create-obsidian-vault` to browse `.project/` in Obsidian. Never run it yourself — it is user-invoked only.
