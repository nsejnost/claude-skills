# Operations — Claude Code web mechanics

How a run actually moves: git protocol, session scheduling, GitHub operations,
and the human-mode procedures (preflight, launch, stop). Everything here assumes
Claude Code web sessions — ephemeral containers, fresh clone per session, no
`gh` CLI, no terminal on the human's side.

## Coordination-branch git protocol

The branch `auto/<arc-slug>` carries `docs/auto/**` and nothing else of its own —
it is cut from main at charter time and never merges back (except the FINISH
archive PR, which cherry-picks the archive directory onto a fresh docs branch).

Every run session:

```
git fetch origin auto/<arc>            # plus origin/main
git checkout auto/<arc>
# 1) CLAIM: edit state.md → claim + sessions_used, commit "claim: session <id>", push
#    push rejected → someone else is live → exit quietly (do not retry the claim)
#    claim present and younger than max_session_minutes → exit quietly
#    claim present but stale → adopt: note the takeover in session-log, re-claim
# 2) ...do the session's one unit of work...
# 3) WRITE-BACK: state.md + session-log.md + tickets touched, clear claim,
#    commit "wave N: <one line>", push
#    push rejected → fetch, rebase, push again (state files are line-append or
#    whole-file-owned, so rebases are clean; a genuine conflict means the claim
#    protocol was violated → HALT with both versions preserved in the report)
```

Ticket branches `auto/<arc>/tNN` are cut from `origin/main` at dispatch, live
only until their squash-merge, and are deleted after. `--force-with-lease` is
permitted on these branches only.

## Session scheduling (the runner)

Two Routines per arc, both created at launch, ids stored in state.md:

- **The chain**: each run session, as its final act *after* a successful state
  push and only when `status: RUNNING`, creates a **one-shot** Routine
  (run-once, fresh-session-per-fire, this environment) 2–5 minutes out, with
  prompt `/autopilot run`. One next session, never more. A crashed session
  simply breaks the chain — by design.
- **The babysitter**: an **hourly cron** Routine, same prompt, same environment,
  created once at launch. It catches broken chains: a babysitter-fired session
  runs the identical protocol (claim, budgets, one unit, reschedule the chain).
  Terminal status → it reports and exits; the terminal session should already
  have disabled both Routines, and any session seeing terminal status verifies
  that and disables them if not.

**Notifications**: create the chain and babysitter with push notifications
enabled so completed sessions that end with something noteworthy (HALT, DONE,
PAUSED, a blocked ticket) reach the human's phone. Write session summaries so
the noteworthy cases are unmistakable one-liners.

**Guards** (all live in the run session, not the Routine):
- Schedule only when the just-pushed state says `RUNNING`.
- `sessions_used` at cap, `max_hours` exceeded, or `no_progress_sessions`
  consecutive sessions without a state change (compare `last_session`) → HALT
  instead of scheduling.
- If the scheduling tools are unavailable in a session (MCP hiccup), skip the
  chain link and rely on the babysitter — note it in session-log. If they're
  unavailable at a terminal state, the halt/completion report must tell the
  human to disable the Routines from their Claude interface.

**Stopping the chain** is therefore: set a terminal status, push, disable both
Routines. All three, in that order.

## GitHub operations (MCP first)

Web sessions use the GitHub MCP tools; map operations as follows (if a `gh` CLI
exists — non-web environments — the equivalent commands are fine):

| Operation | How |
| --- | --- |
| Open PR | create_pull_request (head `auto/<arc>/tNN`, base main, body per formats.md) |
| Check CI on a PR | pull_request_read / get_check_run — poll with a deadline of `ci_wait_minutes`; never wait unbounded |
| Fetch failure logs | get_job_logs (failed jobs only) |
| Re-run suspected flake | actions_run_trigger / rerun failed — at most `flake_reruns` per attempt |
| Squash-merge | merge_pull_request with squash; delete the branch after |
| Dashboard | issue_write to create at launch; issue_write body-update each wave |
| Archive PR (FINISH) | create_pull_request from a `auto/<arc>-archive` docs branch |

Rules: CI red that also reproduces on `origin/main` is pre-existing breakage —
record it, apply the charter's stance (the interview captured the baseline), and
never burn attempts on it. Merge conflicts with main never happen at the PR
stage because integration rebases first — if GitHub still reports one, state
drifted: re-fetch and re-run integration for that ticket.

## Preflight (human present; run in the same environment runs will use)

Work through this checklist **in-session** — the point is proving the run's own
environment, not the human's machine. Report each line pass/fail; any fail
blocks launch with a specific fix.

1. Charter: VALIDATE-gate checks pass (sentinel gone, Done-when lines execute
   here and now, budgets/priorities well-formed).
2. Git: coordination branch exists and pushes from this session (push a
   trivial state edit and confirm).
3. GitHub: MCP tools reachable; repo writable; a PR can be created and closed
   (use a throwaway branch + immediately-closed draft PR as the probe, or verify
   permissions read-only if the human prefers); squash merging allowed; branch
   protection on main has **no required human reviews** (required status checks
   are fine — merges then use auto-merge-on-green).
4. CI: workflows detected (or the charter's no-CI stance confirmed); baseline
   suite runs green **in this container** — catching env vars/secrets that exist
   only on the human's machine, the classic overnight killer.
5. Scheduling: Routine tools available; create + immediately delete a dummy
   one-shot to prove it.
6. Budgets sanity: ticket-count guess from recon vs `max_sessions`.
7. Browser present? (only if the charter opted into UI prototypes).

Offer `launch` on full pass.

## Launch (human present)

1. Confirm with the human (one click): arc name, target repo/branch, budgets,
   merge policy line ("per-ticket squash-merged PRs, auto-merged on green").
2. Create the dashboard issue; store its number in state.md.
3. Create the babysitter cron + the first one-shot chain link (push
   notifications on); store ids.
4. Set `status: RUNNING` (from READY / a repaired HALT / PAUSED-SPEC-REVIEW),
   push, and tell the human what to expect on their phone.

Launch is also the re-arm path after a Repair interview or a spec-review pause —
same steps, minus creating things that already exist.

## Stop (human present, any device)

1. Set `status: HALTED-BY-USER`, write a mini halt-report (what was in flight,
   what is safely merged), push.
2. Disable both Routines.
3. Update the dashboard title/body.
4. Tell the human what state things stopped in and that `/autopilot` will offer
   Repair → launch whenever they want to resume. In-flight worker branches are
   left in place (unpushed worktrees die with their session; pushed ticket
   branches are listed in the report).

## Environment requirements (document for the human at charter time)

- The repo authorized to Claude Code web (GitHub app) with write access; runs
  happen in an environment for that repo.
- Environment network policy must allow the project's package registries and
  test dependencies.
- Repo settings: squash merge enabled; auto-merge enabled if branch protection
  requires status checks; no required human PR reviews on main.
- Subscription note: usage caps can pause overnight progress — the babysitter
  simply resumes when sessions can run again; "safely paused" is the guarantee,
  "done by morning" is not.
