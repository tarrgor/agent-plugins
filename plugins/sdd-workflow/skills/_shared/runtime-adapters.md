# Runtime adapters

Use the current host's native capabilities. These mappings change invocation and command syntax only; they do not change the workflow's approval, safety, or output requirements.

## Subagents

- **Claude Code:** use the `Agent` tool with the requested `subagent_type`, which carries the plugin prefix (`sdd-workflow:<agent>`). Subagents run in the background and notify the caller when they finish; wait for that result before any step that depends on it, exactly as the calling skill specifies.
- **Codex:** spawn the matching custom agent with the collaboration/subagent capability, explicitly tell it to use the corresponding `$verify-implementation` or `$research-topic` skill, pass the complete brief, and wait for its final result before continuing. The Codex custom agents are named `verify-implementation` and `research-topic` — the same names Claude Code uses; their source files live in `agents/codex/`.
- **Codex plugin without custom agents:** the plugin bundles skills, not registered custom-agent TOMLs. If the named agent is unavailable, spawn a fresh generic subagent using the host's collaboration capability, with the role brief below and an explicit instruction to load the installed matching skill. Pass the skill's resolved location or full instructions if skill discovery is unavailable to the child. Wait for its complete result. Do not write agent files into the user's configuration. An installed named agent remains preferred.
  - Review brief: identify the child as the independent `verify-implementation` reviewer; provide the issue and PR; review only, never edit files, implement fixes, push, merge, or post comments; return all findings with location, impact, severity, confidence, and the criteria checked. The child follows Step 1 onward of the review skill without delegating again.
  - Research brief: identify the child as a `research-topic` worker; provide one subtopic, decision, boundaries, and established knowledge as text; use external research tools only, never read local project data, execute shell commands, edit files, or delegate further; return findings and dated sources to the caller. Supply the source discipline from the skill directly so loading it does not require local reads. The child does not write Knowledge entries.
  - Use host-enforced read-only or tool restrictions when available. These briefs alone are behavioral restrictions, not a sandbox or a web-only tool allowlist. If strict prevention of local reads is required for research, require an externally isolated service.
- If Codex has no subagent capability, stop an independent review and report that a separate review context is required; never review implementation in the context that wrote it. Research may use the calling skill's direct-research fallback and must report that context isolation was unavailable. For other hosts, follow the calling skill's fallback. Never claim independent review or isolated context when the work ran in the caller.

## Model selection

A skill may recommend a model per complexity tier; it never changes the model of the session it runs in — that stays the user's choice (`/model`, or the host's model picker). A model can be set only on work a skill starts itself (a subagent, or a new session where the host can start one), and this workflow does not implement issues in subagents.

The table names model families, not versions: use the newest release of the named family that the host offers.

| Tier | Claude Code | Codex |
|---|---|---|
| Low | Sonnet | Terra |
| Medium | Opus | Sol |
| High | Opus | Sol |
| Exceptional | Fable | Astra |

Astra and Fable are reserved for genuinely exceptional work; Sol carries ordinary coding issues up to and including the High tier. If the host offers a reasoning-effort setting, raise it with the tier rather than reaching for a larger model.

Name the recommendation and let the user act on it.

## Units of work

`run-milestone` starts each issue as a unit of work: isolated in its own worktree, with its own model, reporting back when done.

- **Claude Code desktop app:** the session-start tool (`start_session`) with `initiation: "user_asked"`, `context: "fresh"`, `use_worktree: true`, `source_branch: <base>`, a `model` and `effort` per tier, and a brief plus `background`. The app continues the coordinator when a started session ends its turn. A session can't run on a larger model or a higher effort than the coordinator's own; a tier above it runs at the coordinator's level. Started sessions inherit the coordinator's permission mode. A follow-up goes to the same session by its id (`SendMessage`); a session is stopped with the session-stop tool.
- **Codex desktop with chat tools:** use the Codex-only adapter in `skills/run-milestone/references/codex-desktop.md` (resolve from the installed `run-milestone` skill). It maps units to explicitly requested, user-visible chats in separate worktrees using `create_thread`, `wait_threads`, `read_thread` and `send_message_to_thread`. Read it only for a Codex `run-milestone` run; it does not change standalone skills or Claude Code sessions.

- **Any other host:** unsupported — `run-milestone` says so and stops.

## Shell and filesystem

- Prefer the host's file-search and file-editing tools over shell-specific pipelines.
- Recursive file listing: use `rg --files` when available. PowerShell fallback: `Get-ChildItem -Recurse -File`. POSIX fallback: `find <path> -type f`.
- Local ISO date: use runtime date context when available. PowerShell fallback: `Get-Date -Format yyyy-MM-dd`. POSIX fallback: `date +%F`.
- Python 3 (for bundled scripts): `python3` on POSIX; `python` or `py -3` on Windows.
- Create directories with the host-native operation. PowerShell: `New-Item -ItemType Directory -Force`. POSIX: `mkdir -p`.
- Treat repository-relative paths as platform-neutral. Quote native filesystem paths, especially when they contain spaces.
- For multiline GitHub issue or PR bodies, prefer a temporary body file and `gh ... --body-file <path>` over shell-dependent quoting.

## Git worktrees

Determine whether the current checkout is linked by comparing `git rev-parse --git-common-dir` with `git rev-parse --git-dir` and consulting `git worktree list --porcelain` when needed.

- **Normal checkout:** the workflow may switch to and fast-forward the base branch before creating the issue branch.
- **Existing linked worktree:** never create a nested worktree and never switch another checkout. Fetch the remote, verify the intended base ref, and create the issue branch directly from that ref if the current worktree is detached. Preserve any existing branch and stop on unrelated changes that make the operation ambiguous.
- A Codex-created worktree may start at detached `HEAD`. This is expected, not an error.
- A branch checked out in another worktree can't be switched to. Work on it detached (`git switch --detach origin/<branch>` after a fetch) and push with `git push origin HEAD:<branch>`; never delete or move it.

## Skill invocation labels

- Claude Code exposes the plugin's skills as `/sdd-workflow:<skill>`.
- Codex CLI and IDE support `$skill-name`; the ChatGPT desktop app exposes installed skills in its Skills UI.
- In user-facing guidance, name the skill itself unless the host-specific invocation syntax is known.
