---
name: estimate-issue
description: This skill should be used to estimate a GitHub issue's implementation complexity and recommend the model to implement it with, before any code is written. Trigger phrases include "estimate issue 12", "how complex is this issue", "which model should implement this", "abschätzen", or whenever an issue's difficulty needs judging up front. Read-only — recommends, changes nothing. Run by the user, or by `run-milestone` for each ready issue; no other skill runs it.
---

# Estimate Issue

Judges one issue's implementation complexity and names the model to implement it with. Read-only: no file writes, no `gh` mutations, no branch or code changes.

The host's model names per tier are defined in `../_shared/runtime-adapters.md` (relative to this skill's directory); the Knowledge consultation discipline in `../_shared/conventions.md`.

GitHub operations: `../_shared/github.md` — the `gh` commands below are the reference form.

## 1. Read the issue

- Identify the issue by number. If genuinely unclear, ask.
- `gh issue view <number> --comments` — title, body, labels, acceptance criteria, and the discussion.
- Skim the code the issue names or implies: the affected modules, their tests, and any obviously adjacent code. Skim only — this step must stay cheap relative to the implementation it precedes.
- Consult name-relevant `.project/Knowledge/` entries per the conventions discipline; a recorded gotcha in the affected area raises the estimate.

## 2. Score the complexity

Weigh these signals. Any single strong signal can carry the estimate — this is a judgement, not a points total.

- **Spread**: files and modules touched; one function, one module, or a cross-cutting change.
- **Design freedom**: an obvious local edit, or new abstractions, interfaces, or data structures that have to be invented.
- **Risk**: concurrency, persistence and migrations, auth and security, money, external APIs, protocol or format compatibility.
- **Reversibility**: a change that is cheap to correct later, or one that later work will build on.
- **Testability**: an existing test to extend, or a test harness that has to be built first.
- **Clarity**: acceptance criteria that decide every open question, or gaps the implementer has to fill.
- **Familiarity**: patterns already present in this codebase, or a library, protocol, or domain new to it.

Assign one tier:

| Tier | Looks like |
|---|---|
| **Low** | A local, well-specified change in a familiar pattern; an existing test extends to cover it. |
| **Medium** | Several files or a small new abstraction; some judgement calls, no serious risk. |
| **High** | Cross-cutting change, new design decisions, or a risk area (concurrency, migrations, security, external contracts). |
| **Exceptional** | Rare. Deep reasoning over an unfamiliar or intricate system, or a decision that later work is hard to unwind — an architecture rewrite, a hand-rolled algorithm or protocol, a subtle correctness proof. |

Estimate the *implementation*, not the wording of the issue: a one-line issue over an intricate subsystem is not a Low.

## 3. Report and hand over

Report in a few lines, no file written:

- the tier, and the two or three signals that decided it — name the actual files, risks, or gaps;
- the files the implementation will most likely change, as paths (`run-milestone` uses them to keep parallel sessions apart);
- the recommended model for this host, per `runtime-adapters.md`;
- anything the implementer should know up front: an ambiguity worth clarifying on the issue first, an open `Depends on #N` blocker, or a Knowledge entry that applies.

Recommend the model; switching the session model is the user's action.

End by naming the next step — set the model if it differs from the current one, then run `implement-issue <number>`.
