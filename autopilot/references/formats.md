# Formats

Exact shapes for every artifact a run writes. Machine-parseable on purpose:
sessions grep these; the scheduler and gates depend on them. Do not innovate on
formats mid-run. Schema version: **1** (`schema: 1` in state.md; a session that
reads a schema it doesn't know must HALT, not guess).

## state.md (rewritten at every session end; the program counter)

```
schema: 1
skill_version: 1.1
arc: table-export
status: RUNNING            # READY | RUNNING | PAUSED-SPEC-REVIEW | DONE |
                           # HALTED | HALTED-AWAITING-CHARTER | HALTED-BY-USER
phase: BUILD               # VALIDATE | MAP | DECIDE | SPEC | TICKETS | BUILD | FINISH
wave: 4
claim: -                   # "-" or "<session-id> <ISO timestamp>"; stale after max_session_minutes
active_tickets: #12 #14    # or "-"
ci_pending: #11=PR#38      # or "-"
sessions_used: 17/60
replans_used: 0/1
arch_checkpoint_at: 15     # merged-ticket count that triggers the next checkpoint
gate_failures: SPEC=0 TICKETS=1 INTEGRATE(#09)=1
merged: 9                  # tickets merged so far
triggers: chain=trig_abc123 cron=trig_def456
dashboard: #7              # the dashboard issue number
launched: 2026-07-28T02:10Z  # re-stamped at every launch/re-arm; max_hours measures from here
last_session: 2026-07-28T06:41Z | BUILD | wave 4 | #12 merged (PR #41), #14 attempt 2 failed | next: #14 solo
notes: <one line max — anything the next session must know that isn't elsewhere>
```

Rules: `claim` is written+pushed **before** work and cleared at write-back; a
rejected claim push means another session is live — exit. `sessions_used`
increments in the same commit as the claim (so crashed sessions still count).
Status transitions into READY/RUNNING happen only in human modes (charter,
launch); run mode only ever moves RUNNING → {RUNNING, PAUSED-SPEC-REVIEW, DONE,
HALTED*}. `gate_failures:` feeds the consecutive-same-gate HALT for **phase**
gates only; `INTEGRATE(#NN)` entries are per-ticket visibility — INTEGRATE
failures burn that ticket's `attempts`, never this HALT.

## Ticket file — docs/auto/tickets/NN-slug.md

```
# 12 — Add CSV export to the results table
type: build                # research | decision | prototype | task | build
status: open               # open | claimed | review | ci-pending | merged | blocked | split | icebox
blocked_by: 09, 10         # ticket numbers, or "-"
charter_refs: §Scope(export), §Priorities
seams: ResultsTable public props; exportCsv(rows) in src/export
touches: src/export/**, src/components/ResultsTable.*
attempts: 1/3
pr: #41                    # once opened
split_generation: 0        # 0 = original; incremented on TOO_BIG splits

## What to build
<the end-to-end behaviour this slice makes work, from the user's perspective —
a vertical tracer bullet, not a layer list>

## Acceptance (executable — every build ticket)
- run: npx vitest run src/export/exportCsv.test.ts   expect: passes, ≥4 assertions
- run: npm run typecheck                             expect: exit 0

## Work log
<appended by worker/reviewer/orchestrator: red-run evidence per TDD cycle
(test name + failing output snippet), review findings + resolutions,
D-entries made, attempt outcomes>
```

A build ticket without runnable `run:/expect:` lines fails the TICKETS gate.
"Looks right" is not checkable; a command with an expected result is.

## decisions.md entries (append-only)

Type 2 — one line:
```
D-0042 | 2026-07-28 | #12 | Column state persists per-table, not globally | charter §Silence-defaults(1): matches existing preferences-store convention
```

Type 1 — ADR block:
```
## D-0043 (ADR) — Export engine: stream rows, don't buffer
Ticket: #10   Date: 2026-07-28   Status: accepted
Context: <2–4 lines: the fork and why it is one-way>
Evidence: research notes/export-size.md; prototype notes/export-proto.md
Decision: <what was chosen>
Charter basis: §Priorities 1 > 3; §Tech constraints
Objections considered: <red-team's strongest case against + the answer, 2–4 lines>
Rollback: <what undoing this costs and the concrete path>
Supersedes: — | D-00NN (new evidence: <ref>)
```

## Gate checklists (Auditor runs these in a fresh-context subagent; record PASS/FAIL + reasons in state.md)

**VALIDATE**
- [ ] CHARTER.md exists; sentinel line absent
- [ ] Every Done-when line executed as written: the command RUNS and yields a
      determinate result. UNMET at arc start is EXPECTED — Done-when defines
      termination, not entry; record each line's met/unmet status as the arc
      baseline. Only a command that cannot execute at all (not found,
      malformed, hangs) fails this check
- [ ] Priorities strictly ranked (no ties); budgets numeric; no-touch zones listed
- [ ] Baselines recorded (test count, xfail/skip, ratchet commands run once)

**MAP**
- [ ] Every charter Scope-In item → a ticket or a cited icebox entry
- [ ] Every decision ticket lists its charter sections
- [ ] Edges form a DAG; every ticket sized to one session
- [ ] codingstandards.md exists or a task ticket creates it; test infra exists or a task ticket bootstraps it

**SPEC**
- [ ] Every requirement traces to charter, braindump, or a D-entry (else → icebox)
- [ ] TDD seams named explicitly, per requirement area
- [ ] Every requirement carries executable acceptance criteria
- [ ] Red-team pass ran; objections answered or the requirement was cut
- [ ] No no-touch zone implicated; scope now FROZEN

**TICKETS**
- [ ] Vertical tracer-bullet slices; each independently mergeable (flags where needed)
- [ ] Acceptance lines copied verbatim from the spec; Touches and seams present
- [ ] Blocking edges form a DAG; no ticket exceeds one session by the sizing heuristics
- [ ] Mergeability-skeptic pass ran on the independence claims

**INTEGRATE (mechanical, per ticket — any FAIL fails the attempt; bounded by
the ticket's attempts, not the consecutive-same-gate HALT)**
- [ ] Branch rebased onto current origin/main; gate ran on the rebased result
- [ ] All charter CI commands green locally
- [ ] Ratchets hold (see Ratchet rules below)
- [ ] Every acceptance `run:` line passes as written
- [ ] Diff clean of no-touch zones
- [ ] Final review cycle's findings addressed, or waived with an Auditor-countersigned
      D-entry (spec-faithfulness findings: never waivable)
- [ ] PR checks green (or no CI configured, noted) before merge

**DONE**
- [ ] Every charter Done-when line passes against main
- [ ] Full sweep green on main; completion report written; archive PR opened
- [ ] Routines disabled; dashboard finalized

**Ratchet rules**: test count never decreases and xfail/skip never increases —
except with a D-entry citing consolidation, countersigned by the Auditor. Plus
any arc-specific ratchets from the charter, measured by the exact commands the
charter records.

## PR body (per build ticket)

```
## Ticket
#12 — Add CSV export to the results table (docs/auto/tickets/12-add-csv-export.md, branch auto/<arc>)

## Delivers
<2–4 lines, user-perspective>

## Acceptance results
- `npx vitest run src/export/exportCsv.test.ts` → passed (6 assertions)
- `npm run typecheck` → exit 0

## Decisions
D-0042 (persistence scope) · none Type 1

## Review
Standards: 2 findings, fixed · Spec: clean · TDD evidence: 4 red→green cycles logged

---
Generated autonomously by the autopilot skill. Squash-merged on green by policy.
```

## Dashboard issue body (rewritten each wave; never comment-spam)

```
# 🤖 Autopilot — <arc> — RUNNING (wave 4)
Phase: BUILD · Sessions 17/60 · Merged 9 · Blocked 1 · Icebox 3
Updated: 2026-07-28T06:41Z

| Ticket | Status | PR |
| #09 pagination | merged | #37 |
| #12 csv export | merged | #41 |
| #14 xlsx export | attempt 2 failed (CI red: node 18 job) | #43 |
...

Halts/attention: none
Charter: docs/auto/CHARTER.md on branch auto/<arc>
```

Title prefix tracks status: `🤖 RUNNING` / `⏸️ PAUSED — spec review` /
`🛑 HALTED — needs you` / `✅ DONE`.

## halt-report.md

```
# HALT — <arc> — <ISO date>
Reason: <one line: which budget/gate/conflict/user-stop>
Phase & wave: <where it stopped>
Safely merged: <ticket list with PR links>
Blocked tickets: <#id — why — attempts>
Open decisions: <the exact questions a human should answer, phrased so the Repair
interview can ask them verbatim; each names the charter section its answer appends to>
Resume: run /autopilot in any session — it will offer the Repair interview, then launch.
```

## Completion report (FINISH)

```
# DONE — <arc> — <ISO date>
Shipped: <slice list: ticket → PR link>
Done-when results: <each command + observed result, run against main>
Decisions: <count> (Type 1 ADRs: <ids>)
Architecture findings for next arc: <count, in icebox>
Icebox: <count + one line each>
Blocked/descoped: <list or none>
Sessions used: <n>/<budget> · waves: <n> · attempts spent: <n>
```

## Interview transcript — docs/auto/charter-interview.md

```
# Charter interview — <arc> — <date> — mode: NEW|RENEWAL|REPAIR
## <section>
Q1: <question as asked>
  options: A <label> | B <label> (Recommended) | C <label>
A1: B [CLICKED]                        # or [TYPED] verbatim text
C1: <clarification question the human typed> → <answer gist> [CLARIFICATION]
R1: option D added after clarification [OPTION-REVISED]
P1: <recon proposal shown> → confirmed [FACT-CONFIRMED]
D1: <template default> → accepted [DEFAULT-ACCEPTED]
=> charter lines written: <the exact lines>

(repeat per section; end with)
## Full read-back
Confirmed by human: <ISO timestamp>
```

A `STATUS: PARTIAL` header at the top marks an interrupted interview; resuming
restarts at the last confirmed section.
