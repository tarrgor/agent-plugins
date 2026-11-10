---
name: create-spec-issues
description: This skill should be used after a kick-off interview has produced a confirmed spec (`.project/SPEC.md` for a new project, or a new `.project/SPEC-milestone-NNN-SLUG.md` for a milestone) and that spec's work needs to be broken into actionable issues. Trigger phrases include "create issues from this spec", "break this spec into tickets", "turn the spec into issues", "spec this out into work items", or whenever a freshly confirmed spec needs to be decomposed into implementable units of work.
---

# Create Spec Issues

Runs after kick-off produces a confirmed spec. Decomposes it into one issue per unit of work, grouped under a GitHub milestone — does not implement anything.

Milestone naming, the `Status:` lifecycle, the `Depends on #N` format, and the Knowledge discipline are defined in `../_shared/conventions.md` (relative to this skill's directory).

GitHub operations: `../_shared/github.md` — the `gh` commands below are the reference form.

## 1. Find the spec

Use the highest-numbered `.project/SPEC-milestone-<###>-*.md` if any exist, else `.project/SPEC.md`. Check its `Status:` header (lifecycle per conventions):

- `Done` — this spec is finished; refuse and suggest `kick-off` for the next milestone.
- `Active` — a re-run; issues already exist, so expect Step 6 to skip most units.
- `Planned` (or no header on a legacy spec — apply the conventions fallback) — fresh decomposition.

Read the spec thoroughly — if a milestone spec is in play, also skim `.project/SPEC.md` for project vision and constraints not repeated in the milestone spec.

## 2. Require GitHub

Run `gh repo view` (requires a GitHub remote and a working `gh auth status`). Issues live on GitHub — there is no offline fallback.

- No GitHub repo yet: tell the user, and offer to create one (`gh repo create`) — ask for name and visibility, and only run it once they confirm.
- `gh` missing or unauthenticated: say exactly what's missing and stop.

## 3. Decompose into units of work

Identify every discrete unit of work in the spec — each feature, component, workflow step, or task it describes. Favor finer granularity over bundling: every action called for in the spec must map to its own issue.

## 4. Check document currency

Issues are prompts an agent will execute later — a stale claim baked in now misleads that run.

- Consult `.project/Knowledge/`, if present, per the conventions discipline for the areas the units touch.
- Spot-check the spec's checkable claims about the current state of the codebase (e.g. "X doesn't exist yet", "Y works this way") against the code itself.
- Any contradiction — spec vs. code, Knowledge vs. code, spec vs. Knowledge — present it to the user and get a ruling **before** creating issues. Never bake a claim you've seen contradicted into an issue body.

## 5. Order by dependency

Order the units so any unit needing another's output comes after it. This is both the creation order and the suggested implementation order.

## 6. Create the milestone and issues

- Derive the milestone title from the spec filename (per conventions). Reuse it if it already exists; otherwise create it: `gh api repos/{owner}/{repo}/milestones -f title="<title>"` — there is no `gh milestone` subcommand.
- Idempotency: fetch the milestone's existing issues (`gh issue list --milestone "<title>" --state all --json number,title,state`) and skip any unit already represented — match by meaning, not exact title text, since a re-run may word titles differently. When genuinely unsure whether an existing issue covers a unit, ask the user rather than creating a duplicate.
- Each new issue is a detailed, specific implementation prompt an AI coding agent could execute directly — not a summary. Include: what to build, the relevant context/constraints from the spec, and a bullet list of clear, checkable acceptance criteria.
- Create in Step 5 order with `gh issue create --title "..." --body "..." --milestone "<title>"`. Where a unit depends on earlier-created issues, append one `Depends on #<number>` line per blocker to the body (format per conventions).
- Set the spec's `Status:` header to `Active`.

## 7. Verify completeness

Re-check against the units from Step 3 — every one must map to exactly one issue in the milestone (newly created or pre-existing). Report the final list in suggested implementation order, noting any skipped as already present. End with the next step: `implement-issue #<first issue with no open blockers>`.
