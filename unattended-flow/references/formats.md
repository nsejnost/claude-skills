# Formats

Exact shapes for every artifact the run writes. Machine-parseable on purpose: the
outer runner greps `status:`, and future sessions grep the rest. Do not innovate on
these formats mid-run.

## state.md (rewritten at every session end; the program counter)

```
status: RUNNING            # RUNNING | DONE | HALTED | HALTED-AWAITING-CHARTER
phase: BUILD               # BOOTSTRAP | MAP | DECIDE | SPEC | TICKETS | BUILD | FINISH
active_ticket: #47         # or "-"
sessions_used: 23/60
replans_used: 0/1
gate_failures: SPEC=0 TICKETS=1 MERGE(#44)=1
last_session: 2026-07-15 | BUILD | #46 merged | next: #47
notes: <one line max — anything the next session must know that isn't elsewhere>
```

## decisions.md entries (append-only)

Type 2 (one line):
```
D-0042 | 2026-07-14 | #31 | Column state persists per-table, not global | charter §Silence-defaults(1): matches existing preferences-store convention
```

Type 1 (ADR block):
```
## D-0043 (ADR) — Table stack: TanStack headless
Ticket: #12   Date: 2026-07-14   Status: accepted
Context: <2–4 lines: the fork in the road and why it is one-way>
Evidence: research #9 (notes/table-stack.md), prototype #11 (screenshots on ticket)
Decision: <what was chosen>
Charter basis: §Priorities 2 > 4; §Tech constraints (dependency policy)
Rollback: <what undoing this costs and the concrete path>
Supersedes: — | D-00NN (with new evidence: <ref>)
```

## Ticket format (map and build tickets)

```
Title: <verb-first, one slice>
Type: research | decision | prototype | task | build
Blocked-by: #a, #b
Charter-refs: §Scope(item), §No-touch
Acceptance (executable — required for build tickets):
- run: <command>        expect: <observable result>
- run: <command>        expect: <observable result>
Size: fits one session (if in doubt, split before starting, not after failing)
```

A build ticket without runnable acceptance lines fails the TICKETS gate. "Looks
right" is not checkable by the merge gate; "`npx vitest run src/x.test.ts` passes
with 6 new assertions" is.

## Gate checklists (Auditor runs these in fresh context; record PASS/FAIL + reasons in state.md)

**MAP gate**
- [ ] Every charter Scope-In item → a node or a cited icebox entry
- [ ] Every Decision node lists its charter sections
- [ ] Edges form a DAG; every node sized to one session
- [ ] codingstandards.md exists or a Task node will create it

**SPEC gate**
- [ ] Every requirement traces to charter, braindump, or a D-entry (else → icebox)
- [ ] TDD seams named explicitly
- [ ] Every requirement carries executable acceptance criteria
- [ ] No no-touch zone implicated; scope now FROZEN

**TICKETS gate**
- [ ] Vertical tracer-bullet slices; each independently mergeable (flags where needed)
- [ ] Acceptance criteria copied onto each ticket verbatim
- [ ] Blocking edges form a DAG; no ticket exceeds one session

**MERGE gate (mechanical — any FAIL fails the attempt)**
- [ ] CI green (all charter-listed commands)
- [ ] Ratchets hold (tests ↑, xfail/skip ↓, arc-specific)
- [ ] Every acceptance `run:` line passes as written
- [ ] Diff clean of no-touch zones; base = integration branch
- [ ] Review findings from the final cycle addressed or explicitly waived with a D-entry

**DONE gate**
- [ ] Every charter Done-when line passes
- [ ] Full sweep green; completion report written; single PR opened to target branch

## halt-report.md

```
# HALT — <arc> — <date>
Reason: <one line: which budget/gate/conflict>
Phase & ticket: <where it stopped>
What is safely merged: <list, on integration branch>
Blocked tickets: <#id — why — attempts>
Open decisions: <D-candidates the charter could not answer — phrased as the exact
questions a human should answer, so resuming = appending answers to the charter's
Silence-defaults or Scope and re-running the runner>
Resume: fix the above, then `claude -p "/unattended-flow resume"`
```

## Completion report (FINISH)

```
# DONE — <arc> — <date>
Shipped: <slice list with ticket refs>
Done-when results: <each command + observed result>
Decisions: <count>; Type 1 ADRs: <ids>
Icebox: <count + one-line each>
Blocked/descoped: <list or none>
PR: <url>  (integration → target)
```
