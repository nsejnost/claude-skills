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

Ticket branches `auto/<arc>-tNN` are cut from `origin/main` at dispatch, live
only until their squash-merge, and are deleted after. `--force-with-lease` is
permitted on these branches only.

## Session scheduling (the runner) — two lanes, canary decides

There are two ways to keep the run alive; **launch verifies which one this
account can actually use** (see the canary below) and records the lane in
state.md `notes`.

**Lane A — self-bind chain (default; platform-verified on this account).**
The launch session itself becomes the **runner conversation**. Each wake: run
one unit per the session protocol, push state, then — only when the pushed
state says `RUNNING` — call `send_later` (2–5 minutes out, message
`/autopilot run`) and END THE TURN so the fire can wake the conversation.
Store each pending trigger id in state.md. The babysitter is an **hourly fresh-session cron the HUMAN creates once in
the claude.ai Routines dashboard at launch** — launch prints the exact prompt
and settings to paste. UI-created fresh-session Routines provision correctly
even where MCP-created ones fail (verified 2026-07-28: commit 1fc5d2e pushed
by a UI-fired session), an out-of-band fresh session can recover even a
wedged runner conversation (which a self-bind cron cannot), and fresh-session
Routines carry push notifications. If the human skips the UI step, fall back
to a self-bind hourly cron bound to the runner conversation. Either way the
claim protocol makes overlapping wakes and sessions exit quietly. Context accrues across wakes; that is acceptable because the disk is
the program — every wake re-reads charter/state/tickets from origin and never
relies on conversation memory (platform auto-compaction handles the rest).
**Runner takeover** (corrupted or lost runner conversation): from any new
session, delete the old chain + cron triggers listed in state.md, adopt the
stale claim per protocol, re-arm a new self-bind chain from the new
conversation, and note the rotation in session-log.

**Lane B — fresh-session chain (preferred isolation; use only after the
canary passes).** As lane A, but each link is a one-shot Routine with
`create_new_session_on_fire: true`, an explicit verified `environment_id`,
and **`connectors: ["github"]`** (as held by the creating session) — fired
sessions inherit NO MCP connectors by default, and web sessions have no gh
CLI, so an unconnected fired session cannot open or merge PRs at all.
KNOWN UPSTREAM DEFECT: fresh-session provisioning silently fails on some
accounts — the trigger is marked `run_once_fired` while the cloud container
never initializes (anthropics/claude-code#54260, **closed as not planned**;
13/13 reproduction on this skill's home account — see
docs/research/2026-07-28-routine-fresh-session-materialization.md). The
failure is specific to **MCP-created** triggers: an identical routine created
by hand in the claude.ai Routines dashboard provisions and executes
(verified; create_trigger cannot attach a repository, which likely leaves
MCP-fired containers hanging at clone). So lane B *automation* — sessions
scheduling sessions — is what's blocked; human/UI-created fresh-session
Routines work. Treat automated lane B as unavailable unless a canary passes
today; never plan around a fix.

**The canary (run at launch, and at preflight):** create one one-shot
fresh-session Routine (~2 minutes out, explicit environment_id,
connectors ["github"]) whose prompt creates and pushes a marker commit to a
**`claude/`-prefixed scratch branch** (`claude/autopilot-canary-<arc>`) —
Routine-fired sessions may be push-restricted to `claude/*`, so a canary
targeting the coordination branch could fail forever on permissions and mask
a healthy platform. Marker appears within ~6 minutes → lane B provisions; the
canary prompt then ALSO attempts a push to the `auto/<arc>` prefix and
records which prefixes are writable — that second result decides whether
lane B uses the standard branch layout or the arc's branches must live under
`claude/`. No marker → lane A. Delete the canary Routine and scratch branch
either way.

**Notifications.** Completion push notifications only exist for
fresh-session Routines — the server rejects the parameter for self-bind. On
lane A, phone alerts ride GitHub instead: at HALT / DONE / PAUSED, update the
dashboard issue title AND post one comment @-mentioning the repo owner —
GitHub's mobile app notifies on mentions. (Launch reminds the human to have
GitHub notifications on.) On lane B, also enable Routine push notifications.

**Guards** (all live in the run session/wake, not the Routine):
- Schedule only when the just-pushed state says `RUNNING`; one next wake,
  never more.
- `sessions_used` at cap, `max_hours` exceeded, or `no_progress_sessions`
  consecutive wakes without a state change (compare `last_session`) → HALT
  instead of scheduling.
- Scheduling tools unavailable (MCP hiccup): skip the link, rely on the
  babysitter, note it in session-log. Unavailable at a terminal state: the
  halt/completion report tells the human to delete the Routines from the
  claude.ai Routines panel.

**Stopping the chain** is therefore: set a terminal status, push, delete the
pending chain trigger(s) and the babysitter cron (ids in state.md). All in
that order.

**Skill-version skew.** Skills are provisioned per container from the skills
repo's main — so any wake or babysitter session whose container was recreated
mid-arc runs the CURRENT skill against state written by an older one. The
`schema:`/`skill_version:` stamps in state.md are the guard (unknown schema →
HALT, never guess). Doctrine for the human: avoid merging breaking autopilot
changes to the skills repo while an arc is RUNNING; stop or pause the arc
first, or keep mid-arc edits schema-compatible.

## GitHub operations (MCP first)

Web sessions use the GitHub MCP tools; map operations as follows (if a `gh` CLI
exists — non-web environments — the equivalent commands are fine):

| Operation | How |
| --- | --- |
| Open PR | create_pull_request (head `auto/<arc>-tNN`, base main, body per formats.md) |
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

0. Skills provenance: `cat ~/.claude/skills-provenance.txt` — confirm this
   container's skills were provisioned from the skills repo's current main
   (stale snapshot → tell the human to bump the setup-script version and
   retry in a fresh session before trusting anything below).
1. Charter: VALIDATE-gate checks pass (sentinel gone; every Done-when line
   RUNS with a determinate result — unmet at arc start is expected;
   budgets/priorities well-formed).
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
5. Scheduling: Routine tools available; run the **canary** (see the runner
   section) to determine which lane this account supports; report the lane.
6. Budgets sanity: ticket-count guess from recon vs `max_sessions`.
7. Browser present? (only if the charter opted into UI prototypes).

Offer `launch` on full pass.

## Launch (human present)

1. Confirm with the human (one click): arc name, target repo/branch, budgets,
   merge policy line ("per-ticket squash-merged PRs, auto-merged on green").
2. Create the dashboard issue; store its number in state.md.
3. Re-run the canary if preflight's result is stale, then arm the chosen
   lane. Lane A: create the first `send_later` wake — this conversation
   becomes the runner, so end the turn after step 4 and remind the human to
   keep GitHub mobile notifications on (mentions on the dashboard issue are
   the alert channel) — and print this canonical babysitter prompt for the
   human to paste into the claude.ai Routines dashboard (hourly cron, fresh
   session, this repo, push notifications on):

   > Run "/autopilot run" for the arc on branch auto/<arc-slug>. If
   > "/autopilot" does not resolve as a skill, read
   > ~/.claude/skills/autopilot/SKILL.md and follow it as if "/autopilot run"
   > had been invoked. If that file is missing too, skill provisioning failed
   > in this container: report exactly that and end — the next hourly fire
   > retries with a fresh container.

   The fallback lines make the babysitter immune to a transient provisioning
   failure (the account's setup script installs skills per container; a
   failed clone would otherwise turn the babysitter into a silent no-op).
   Lane B: create the fresh-session babysitter cron + first one-shot link
   with push notifications on, same prompt. Store all trigger ids in
   state.md either way.
4. Set `status: RUNNING` (from READY / a repaired HALT / PAUSED-SPEC-REVIEW),
   push, and tell the human what to expect on their phone.

Launch is also the re-arm path after a Repair interview or a spec-review pause —
same steps, minus creating things that already exist.

## Stop (human present, any device)

1. Set `status: HALTED-BY-USER`, write a mini halt-report (what was in flight,
   what is safely merged), push.
2. Delete the arc's pending Routines — chain wake(s) and babysitter cron, ids
   in state.md.
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
