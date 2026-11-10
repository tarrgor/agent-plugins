---
name: research-topic
description: This skill should be used to research a topic in depth against external sources and capture the result as a durable entry in `.project/Knowledge/`. Trigger phrases include "research TOPIC", "look into TOPIC for the project", "find out how X works", "gather knowledge about X", "what's the state of the art for X", or whenever a decision needs external knowledge the project doesn't have yet. User-invoked and on-demand — other skills may recommend it, but never run it on their own.
---

# Research Topic

Researches one topic against external sources and writes what was learned into `.project/Knowledge/<topic>/`. Does not touch code, issues, or specs.

The `.project/` layout, the Knowledge consultation and governance rules, the base-branch and committing rules, written-deliverable sizing, and the delegation rule are defined in `../_shared/conventions.md` (relative to this skill's directory).

Use `../_shared/runtime-adapters.md` for host-specific file listing, date, and subagent invocation.

## 1. Scope the research with the user

Research without a scope returns an encyclopedia. Before anything else, establish:

- **The decision it feeds** — what will this knowledge be used to decide or build? If the user hasn't said, ask.
- **Boundaries** — what's explicitly out of scope, and what depth is wanted (orientation vs. implementation-ready detail).
- **Subtopics** — break the topic into 1-5 independently researchable questions.

Ask one question at a time and propose a recommended answer for each. Skip anything the user has already specified.

## 2. Check what the project already knows

- Create the `.project/` directories if missing, per the layout in `../_shared/conventions.md` — research can precede `kick-off` on an empty project, and the layout must not depend on which skill ran first.
- List `.project/Knowledge` with the host-native operation from `runtime-adapters.md`. Pick the target topic directory: reuse an existing one whose name fits, create a new one only when nothing does.
- Read the entries in that directory plus any others whose names relate to the topic. Note both what's already established and when it was researched.
- Drop or narrow any subtopic already answered — research the gaps, not the basics. If everything in scope is already covered, say so and stop rather than producing a near-duplicate entry.

## 3. Confirm the brief

Present the final subtopic list, what's being skipped as already known, and the target path `.project/Knowledge/<topic>/<slug>.md`. Do not start researching until the user confirms.

## 4. Research each subtopic in a fresh context

Web research reads far more text than its conclusions are worth — keep it out of the main conversation.

- A matching research agent is installed: launch **one `research-topic` subagent per subtopic**, all together so they run in parallel, using the current host mapping in `runtime-adapters.md`. Under Claude Code, use `subagent_type: sdd-workflow:research-topic` and wait for every subagent's result before Step 5. Under Codex, use the installed `research-topic` custom agent, or the generic research subagent fallback in `runtime-adapters.md`, for each spawned research task. Give each one its subtopic, the decision it feeds, the boundaries, and what the project already knows so it doesn't re-derive it — **as text in the brief, never as a path**. Step 2 has already read those entries. Paste the established claims that bound this subtopic; leave out the sourcing and anything belonging to another subtopic, and summarise an entry too long to paste rather than naming it. What goes into a brief goes out to a fetched page's reach.
- Claude Code's `agents/research-topic.md` technically limits the agent to web/research tools. Codex's custom agent is read-only and instructed not to read local data, but its documented configuration does not provide the same per-agent web-only allowlist. Do not claim equivalent isolation; if strict local-read prevention is required, stop and require an externally isolated research service.
- No named agent: under Codex, first use the generic subagent fallback in `runtime-adapters.md`. If no subagent capability exists, do the research directly per the source discipline below and report that context isolation was unavailable. Other hosts may research directly when their named agent is not installed.
- Already running as that subagent: research the assigned subtopic per the source discipline below, return the findings in full, and stop — Steps 5-7 belong to the caller.

**Source discipline** (applies wherever the research runs):

- Library, framework, SDK, or CLI documentation: query a documentation MCP server (e.g. Context7) if one is available before falling back to web search — it reflects current releases.
- Prefer primary sources — official docs, specs, RFCs, source repositories, papers — over blog posts and aggregators. Use a content-extraction tool if the environment has one; plain page fetches otherwise.
- Corroborate every load-bearing claim against a second independent source. A claim resting on one source is reported as such, not smoothed over.
- Record the publication or last-updated date of each source. Fast-moving topics go stale; an undated source is weaker evidence.
- Note disagreement between sources explicitly instead of picking a winner silently.

## 5. Write the Knowledge entry

One new file, `.project/Knowledge/<topic>/<slug>.md`, named for the specific question answered — not the broad topic. Never edit or overwrite an existing entry (governance per conventions).

Frontmatter marks it as researched rather than observed, so later readers weigh it accordingly:

```markdown
---
type: research
researched: <YYYY-MM-DD>   # current local date from the runtime adapter, never guessed
confidence: high | medium | low
---
```

`confidence` reflects source agreement and quality, not how sure the writing sounds. Body: the findings organized by subtopic, the trade-offs, a recommendation for the decision from Step 1, open questions that research couldn't settle, and a **Sources** section listing every source with its URL and date. Claims that rest on a single source or on disagreeing sources are marked inline.

If a prior entry in the topic covers adjacent ground, link it and state what this one adds — supersede, don't repeat.

## 6. Route contradictions to the Inbox

Research that contradicts an existing Knowledge entry does not correct it here. Write `.project/Inbox/findings-<slug>.md` naming both entries and the conflict; `project-meeting` reconciles them. Same for research that contradicts the current spec.

## 7. Commit, if there is a repository

- Not a git work tree (`git rev-parse --git-dir` fails): skip this step and say the entry is on disk but uncommitted. Never run `git init` — creating the repository belongs to `kick-off`, with the user's confirmation.
- A work tree: `.project/` changes belong on the base branch (per conventions: `develop` if present, else the default). If a feature branch is checked out, say so and `git switch <base>` first — never discard, stash, or sweep in unrelated uncommitted changes; if switching is unsafe, stop and ask.
- Stage only the files this run wrote (the Knowledge entry, and any Inbox finding) — never unrelated changes sitting in the working tree. Commit per the base-branch rules in `../_shared/conventions.md`; if the push is rejected because the branch is protected, use the branch-and-PR fallback (branch `chore/research-<slug>`) and report that PR instead of claiming the entry landed on the base branch.
- No remote configured: commit and say the push was skipped.

## 8. Report

State the entry's path, the recommendation in a sentence or two, the confidence and why, any open question left unanswered, any Inbox finding written, and whether the entry was committed (and pushed) or left on disk. Recommend `project-meeting` if a contradiction was filed, or `kick-off` if the project has no spec yet — research done before a spec exists is there to inform the kick-off interview.
