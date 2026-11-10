# GitHub access

Skills write GitHub operations as `gh` commands — the reference form. Pick the access mode once per run, then perform each operation in that mode.

## Mode

1. **`gh`** — `gh repo view --json nameWithOwner` succeeds: run the commands as written.
2. **MCP** — otherwise (`gh` missing, unauthenticated, or GraphQL refused, as in Claude Code cloud sessions where `gh pr`/`gh issue` return HTTP 403), if the host's GitHub MCP tools are available (Claude Code: `mcp__github__*`; if only listed as deferred, load them with ToolSearch first): use the table below. Take `owner` and `repo` from `git remote get-url origin` (last two path segments, `.git` stripped).
3. **None** — neither works: stop and tell the user GitHub access is required (`gh auth login`, or connect the GitHub integration). There is no offline fallback.

Rows marked **REST** have no MCP tool: use `gh api` (REST still works where only GraphQL is refused). If that fails too, tell the user the exact manual step on github.com (e.g. "create milestone `001-auth-flow`") and continue once they confirm; in non-interactive mode, stop with `RESULT: failed`.

## Operations without `gh`

| Operation | `gh` reference form | MCP mode |
|---|---|---|
| Repo exists | `gh repo view` | `git remote get-url origin` names a GitHub repo and `list_branches` succeeds |
| Default branch | `gh repo view --json defaultBranchRef` | `git ls-remote --symref origin HEAD` |
| Create repo | `gh repo create` | Not available — ask the user to create it on github.com |
| Read issue, comments | `gh issue view <n> [--comments]` | `issue_read` `get` (+ `get_comments`) |
| Create issue | `gh issue create --milestone "<title>"` | `issue_write` `create`; `milestone` takes the milestone **number** |
| Edit issue/PR milestone, labels, state | `gh issue edit`, `gh pr edit` | `issue_write` `update` (PRs are issues). `labels` replaces the set — read current labels and send the full new list |
| Comment on issue/PR | `gh issue comment`, `gh pr comment` | `add_issue_comment` |
| Issues in a milestone | `gh issue list --milestone "<title>"` | **REST**: milestone number from `gh api "repos/{owner}/{repo}/milestones?state=all"`, then `gh api "repos/{owner}/{repo}/issues?milestone=<number>&state=all&per_page=100"`; drop items with a `pull_request` key |
| Create/close milestone | `gh api …/milestones` | **REST**: same `gh api` calls as in `conventions.md` |
| Create label | `gh label create <name> --force` | **REST**: `gh api repos/{owner}/{repo}/labels -f name=<name>` (HTTP 422 = exists) |
| Find PR by head branch | `gh pr list --search "head:issue/<n>-"` | `list_pull_requests` `state: all`; match `head.ref` starting with `issue/<n>-` |
| List open PRs | `gh pr list` | `list_pull_requests` `state: open` |
| PR details (base, head, state) | `gh pr view <n> --json …` | `pull_request_read` `get` |
| PR diff, changed files | `gh pr diff <n> [--name-only]` | `pull_request_read` `get_diff` / `get_files` |
| PR comments, review threads | `gh pr view <n> --comments`, `reviewThreads` | `pull_request_read` `get_comments` + `get_review_comments` |
| PR checks | `gh pr checks <n>` | `pull_request_read` `get_check_runs` (+ `get_status`) |
| Create PR | `gh pr create --base <base> [--fill]` | Push the branch, then `create_pull_request`; for `--fill`, title and body from the branch's commits |
| Reply to review comment | `gh api …/comments/<id>/replies` | `add_reply_to_pull_request_comment` |
| Resolve review thread | `resolveReviewThread` via `gh api graphql` | `resolve_review_thread` |
| Squash merge | `gh pr merge <n> --squash` | `merge_pull_request` `merge_method: squash` |
| Delete remote branch | `--delete-branch`, `git push origin --delete <b>` | `gh api -X DELETE repos/{owner}/{repo}/git/refs/heads/<b>`; if refused (cloud sessions block branch deletion), report the branch as left for the user |

MCP tools take issue and PR bodies as parameters — no body file needed.

## Subagents

A subagent may lack the MCP tools (the `verify-implementation` agent has only `Read`, `Grep`, `Glob`, `Bash`, `Write`). It uses `gh api` REST instead: `repos/{owner}/{repo}/issues/<n>`, `…/issues/<n>/comments`, `…/pulls/<n>`, `…/pulls/<n>/files`. Diff without `gh`: `git fetch origin <base> <head>`, then `git diff origin/<base>...origin/<head>`.
