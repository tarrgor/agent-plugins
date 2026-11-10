# Codex desktop coordinator

Only for `run-milestone` under Codex desktop. Keep the shared issue selection, meeting thresholds, non-interactive results and review limits. The rules here override the corresponding host details in `SKILL.md`; they do not apply to Claude Code or standalone skill invocations. Paths under `.project/` refer to the target repository.

## Entry and mandate

- Discover `list_projects`, `create_thread`, `list_threads`, `read_thread`, `wait_threads` and `send_message_to_thread`; use their current schemas. Missing capability, CLI or IDE → report unsupported and stop before mutations. Do not substitute implementation subagents or background CLI processes.
- Run the coordinator in the normal checkout on the base branch, as in Step 1. Resolve the matching Git project with `list_projects`. Workers use separate worktrees; the coordinator keeps its checkout. Confirm the installed `verify-implementation` custom agent is available before starting executable work.
- Before creating chats, obtain the human's explicit mandate for separate issue and feedback chats, their worktrees starting from the named base branch, follow-up messages including one retry, and the policy's merge authority. Reuse an existing explicit mandate; do not ask again. A skill invocation or an agent-written policy alone does not authorize these chat operations. Ask only for missing authorization, before launching work.
- Retain the two shared `RUN-POLICY.md` fields. On first Codex setup, propose `parallel: 1` for the trial; never silently change an existing policy. Record the user's confirmed Codex mandate in a `## Codex desktop` section: project/repository, base branch, chat/worktree/follow-up scope, and model settings. Commit through the shared base-branch rule before dispatch. This record documents human authorization; it cannot override host restrictions.
- Model settings are either `default` (omit `model` and `thinking`) or an explicitly user-approved table of exact model IDs and efforts for Low/Medium/High/Exceptional. Resolve available IDs from the host; recommend the shared Terra/Sol/Sol/Astra families with low/medium/high/xhigh effort respectively. Do not populate overrides without that approval. An unavailable combination pauses dispatch for a decision; do not silently downgrade. Claude's coordinator-model ceiling is not assumed here.
- Non-interactive mode does not grant filesystem, network or GitHub permissions. Check authentication and the ability to update run records before dispatch. Do not promise workers inherit a permission mode or bypass a permission prompt. A worker needing approval causes the pause below.

## Durable work records

Use append-only issue comments beginning `codex-run:` followed by a JSON object. These are coordinator records, not `needs-decision:` findings. Keep the existing `RESULT:` format unchanged.

Record `version: 1`, a unique `unit` token, repository, milestone number, issue number, kind (`implement` or `feedback`), project ID, base branch, expected file paths, model/effort (or `default`), `attempt` (1 or 2), and `state`. Add returned `clientThreadId`, `threadId`, `hostId`, worktree path, PR number, wait cursor and result as they become known; leave unknown values null. Each new comment contains the complete current record. Only the coordinator appends these records. Use the latest record per issue for scheduling; a new unit can supersede a completed unit, never an active or uncertain one. Keep comment IDs in the run report.

Before every external start or retry, persist its intent (`starting` or `retrying`) and reserve the issue with `in-progress`. After the response, persist its identifiers and state. If recording fails, stop dispatch; never issue an unrecorded retry. Confirm GitHub and chat state on resume rather than treating a comment as authority to act.

On entry/resume, read records for the active milestone, including closed issues, and reconcile **before** selecting work:

- `running` with a known chat → inspect it; wait if still working, consume a completed result once, or pause if it needs attention. Recover its recorded file reservation even if the worker already removed `in-progress`.
- `starting`, `retrying`, or only a `clientThreadId` → search `list_threads` history on the recorded host. Match project and the exact unit token in the title, then verify the initial prompt with `read_thread`. Store the real `threadId`; never pass `clientThreadId` to `wait_threads` or `read_thread`. For a retry, inspect the known chat for the attempt token before sending anything again.
- No unique match, inaccessible chat, uncertain delivery or unknown worktree → pause with the identifiers; do not create a replacement. An `in-progress` issue without a recoverable record remains reserved and is reported for the user.
- A completed attempt whose result was already recorded is not retried or counted again. Reconcile open/merged PRs against GitHub, including an interrupted merge's base build/test check before further dispatch or merges. Never infer success from a label alone.

Only one coordinator may dispatch for a repository at a time. If another coordinator is known to be active, stop; comments are a recovery journal, not a distributed lock.

## Dispatch and wait

Apply these rules to **both** Step 3 feedback and Step 5 implementation:

1. Scope candidate issues and PRs to the active milestone and base branch. Meeting due → no new work or merges.
2. Count starting, running, retrying and attention-needed units toward `parallel`. A slot stays reserved until the chat's completed turn is consumed. One unit per issue. Estimate expected paths; for feedback include the target PR's changed paths. Compare against every reserved unit and other open PRs; exclude only the feedback unit's own target PR. Overlap → queue.
3. Persist the intent, then call `create_thread` with the resolved project ID and `environment: {type: "worktree", startingState: {type: "branch", branchName: <authorized-base>}}`. Use an existing base ref, never `working-tree` or `onMissing: "create-branch"`. Add the approved model/effort only when configured. Title: `run-milestone <unit> issue #<n>`.
4. Give the chat the repository, base, issue/PR, unit and attempt tokens, the appropriate existing skill with `mode: non-interactive`, the worker brief below, and the user's applicable mandate. The worker handles the issue branch inside its worktree. It must not merge, start peer chats, message the coordinator, or change the run policy. The coordinator reads its result.
5. Save either the real chat identity or the pending client identity. A pending setup consumes a slot. Resolve it as above; an ambiguous start is not permission to retry `create_thread`.
6. Use `wait_threads` with all known active `threadId`/`hostId` pairs and their last cursors, bounded to at most 60 seconds per wait. A timeout or commentary is not failure. Persist cursors after handling results; use `read_thread` when the result is missing or truncated. Completion wakes this active wait; do not assume it restarts an ended coordinator turn.

For a definitive start refusal with no chat created, record `failed`, park the issue with the reason, remove its reservation and stop new dispatch as in Step 3.5. For uncertain delivery, keep it reserved and pause. Do not confuse these cases.

## Worker brief and review receipt

Include this contract in every initial and retry prompt, in addition to the selected skill:

- Follow the shared non-interactive rules. Report the actual worktree path in the first progress update and again before the final result. For feedback/revalidation, use the existing PR branch (detached when it is owned by another worktree); never create another PR. An otherwise clean PR sent for revalidation still requires the independent review in `check-pr-comments` Step 4.
- Before reporting, publish all issue changes including reports/findings. Record the full PR `headRefOid` for each independent review, and instruct the reviewer to inspect that exact commit in this worktree and return the SHA with its verdict. A moving remote head or unavailable independent reviewer is a blocker, never a clean review.
- A merge receipt requires the **final published head** to have been reviewed with no high/critical finding left open. Finalize reports before that review. If fixes or other commits changed the head afterwards, obtain a fresh independent review within the shared limit of three reviews/two fix rounds. This also applies after low/medium fixes. If no clean final-head review is available at the limit, file a finding and park; do not label the PR `verified`.
- For an entirely code-free PR, the shared review skip is allowed; record `kind=code-free` and the final head after publishing. Never use this exemption for a script, build file or runtime configuration.
- On success, post a PR comment and repeat it in the final response immediately before the unchanged `RESULT:` line:

  `CODEX-REVIEW: unit=<unit> pr=<n> head=<full-sha> kind=<independent|code-free> unresolved=none`

  Post the receipt before adding `verified`. For an unresolved high/critical finding, record it in the Inbox and return the shared unresolved result instead; a wrong approach parks the issue. Do not manufacture a success receipt from the implementer's judgment.
- Do not write `codex-run:` coordinator records. If permissions or authentication prevent publishing the receipt, labels or final work, report the exact blocker; do not claim completion.

## Consume results and merge

- Consume only a completed turn from the recorded chat and attempt. Preserve the shared `parked`, `skipped` and failure handling. Before accepting `RESULT: pr=…`, check issue/PR association, repository, branch, base and `Closes #<issue>` against GitHub. For `unresolved=none`, also validate the receipt and store its comment ID and SHA in the coordinator record. High/critical results need findings, not success receipts. Persist `completed` with the handled result before releasing its slot; a retry keeps the reservation. If GitHub cannot be read or the record cannot be saved, pause instead of declaring a worker failure.
- A `verified` PR without a matching receipt from its recorded worker chat, or whose head changed, is not mergeable. Persist `revalidation-needed`, remove `verified`, then route it through a feedback/revalidation unit under the same capacity and overlap gates. Include `revalidation-needed` records in Step 3's candidates even without review threads or a label. High/critical unresolved results stay unmerged; their findings follow the shared meeting rules.
- Immediately before merge, recheck all shared gates, current head and receipt; persist `merging` with that head. Invoke `merge-pr` with the additional Codex instruction to include `--match-head-commit <receipt-sha>` on its squash merge command, preserving its worktree-aware branch cleanup. A head mismatch goes back to revalidation. Other blockers follow the existing Inbox/meeting path. Never fall back to an unguarded merge.
- Confirm GitHub reports `MERGED` before cleanup, releasing dependent work, or claiming a merge. Persist `merged`, run the required base build/tests, then persist `base-tested` with the tested base SHA. On resume, finish outstanding merge/test checkpoints first. If the command only queues/enables auto-merge, record `merge-pending` and pause dispatch; do not treat it as landed or repeatedly submit it. No CI auto-fix service is assumed under Codex.

## Retry, pause and finish

- A completed failed turn or missing usable result gets at most one follow-up to the **same** chat via `send_message_to_thread`, with a recorded attempt-2 token, the non-interactive instruction and worker contract. Preserve its model settings. Continue existing work; do not rerun fresh-issue setup against an already-created branch/PR. Verify the attempt was not already sent on resume. A second completed failure parks the issue and releases its reservation; no stop tool is needed for an idle chat.
- Approval/input needed, uncertain chat state, unavailable tools or coordinator interruption → pause new starts and merges, checkpoint known units and report the required user action with chat identifiers. Consume results from other chats while possible, without retries. Do not wait indefinitely for an approval, count it as a retry, clear its reservation, or claim the chat stopped. There is no assumed general peer-chat stop tool; archiving or handoff is not a substitute.
- Meeting due → let running work finish and handle it without retries as in Step 4. If a chat instead needs attention or becomes inaccessible, use the pause path and report unfinished units rather than claiming everything drained.
- Use the shared run report and commit rule. Include unit/chat links or IDs, pending setup identities, attempts, review receipts, unfinished units and the precise pause/stop reason. Resuming does not widen the mandate. Do not schedule automatic wakeups or promise background continuation without a separate user request.
- Leave workers' worktrees and chats available for inspection. Do not delete a worktree-bound local branch. Cleanup is a separate user request using the host's managed-worktree tools.
