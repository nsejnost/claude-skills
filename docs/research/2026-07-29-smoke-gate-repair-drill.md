# Repair-path drill — smoke-gate arc (autopilot v1.0 → v1.1)

Date: 2026-07-29 · Target: nsejnost/tracklist-sandbox · Purpose: first
production exercise of the skill's crash-recovery loop — HALT → halt-report →
detection → Repair interview → re-launch → resume → DONE — before real work
depends on it. Design: a real one-ticket arc (the csv arc's iceboxed
smoke-in-CI finding) chartered via Renewal with a deliberately starved budget
(`max_sessions: 2`, documented in-charter as a drill), guaranteeing a benign
budget HALT after MAP. No babysitter by choice: the chain ran attended, then
manual-poke after approval prompts stopped materializing.

## Arc outcome (the work itself)

Shipped: `npm run test:smoke` wired into `.github/workflows/ci.yml` + README
Commands line (PR #10, squash-merged, +3/−1 across three files, 1/3 attempts).
All 3 Done-when lines proven against main at FINISH; 80/80 suite; bundle
ratchet exactly 216; archive PR #11 merged. 7/12 sessions, ~3.4 h wall
including the drill halt and repair. 5 gates first-try; 2 red-team passes
(14 findings, all dispositioned); zero-finding build review; 0 Type 1
decisions; 9 architecture findings iceboxed (top 2: aggregate check script;
declare the Node ≥22.18 floor).

## Drill checkpoints

| Checkpoint | Verdict |
| --- | --- |
| Renewal detection + icebox-mined arc candidates | PASS |
| Done-when lines executed during interview | PASS |
| Deliberate starvation read as intent (charter note → preflight budget check) | PASS |
| Benign HALT | PASS, one better — s02 halted at the *scheduling guard* rather than wasting a third session (stricter than the predicted shape, per spec) |
| Halt-report quality (cold-read: exact question, evidence, recommendation, append target, resume line) | PASS — exemplary |
| Phone alert (dashboard 🛑 retitle + @-mention) | PASS |
| Cold detection: bare `/autopilot` at HALTED offers Repair | **FAIL — safe direction.** Session inferred "headless" (its tool-approval prompt went unanswered) and did run-mode report-and-exit; recovery unreachable until the human asserted presence. → patch: attendance is measured, never inferred |
| Repair interview: verbatim question, dated §Budgets append, nothing else touched | PASS |
| Re-launch: READY→RUNNING, `launched:` re-stamped (first live exercise of the 273c3b4 fix) | PASS — "wall clock 18 minutes into 24h" |
| Resume at persisted phase, session counter continuing (3/12, not restarting) | PASS |
| Post-repair run to DONE | PASS — SPEC, TICKETS, BUILD, FINISH all first-try |

## Bonus coverage (unplanned, all absorbed)

- **Mid-unit platform server error** during TICKETS (skeptic in flight), human
  retry, human stop: session recognized its own held claim on resume,
  re-fetched state per the staleness rail, treated the killed subagent as a
  clean re-launch, lost nothing.
- **Scheduling MCP server absent** at multiple re-arm attempts: guard fired
  correctly every time (skip the link, log, never error).
- Denied/unanswered re-arm approvals → session wrote the manual-chain posture
  into state notes and adapted.
- The predicted Node-22 CI wrinkle **never materialized**: modern Node 22.x
  type-strips by default, and because the PR edits the workflow itself, its CI
  ran the extended gate — the smoke step proved itself before governing main.

## Findings → patches (batch merged with this report; skill 1.0 → 1.1)

1. **Compression family** (4 instances: missing per-question template from Q1;
   pick-a-paragraph with paragraphs unshown; full read-back skipped twice —
   second re-ask absorbed the demand into the question label; launch
   confirmation without restatement): enforcement moved into SKILL.md
   ("Interview output contract" — a confirmation question is lawful only in a
   turn whose visible text contains the text being confirmed); interview-guide
   read-back gates got teeth + a write-draft-first-with-sentinel option;
   launch step 1 requires verbatim restatement. Reference-file mandates
   degrade under context pressure; spine-file constraints and structural gates
   survive — the drill's central lesson.
2. **Attendance misclassification** (biggest catch): SKILL.md now requires
   attendance be measured by one clickable question when dispatch depends on
   it; a missed tool approval is not evidence of absence.
3. **Babysitter survival line redrawn**: survives every awaiting-human state
   (PAUSED*, HALTED, HALTED-AWAITING-CHARTER); comes down only at DONE or
   stop's HALTED-BY-USER.
4. **connectors-param rejection** recorded in Lane B (org rejects it on
   MCP-created triggers — Lane B doubly dead on this account).
5. **sessions_used increments in the claim commit** — comment strengthened
   after s05 self-caught incrementing at write-back (undercounts crashed
   sessions).
6. **Canary fast path**: human may assert a known lane verdict and skip the
   ~11-minute wait.
7. **Probe-branch cleanup** named as a human step in preflight's GitHub check.
8. Post-mortem backlog item (b) closed by this drill.

## Conclusion

The recovery loop is production-real: the measured price of a benign halt is
one phone notification, one clickable question, and ~2 minutes of human time,
after which the run resumes exactly where it stopped with budgets and clocks
accounted correctly. Every failure found across both arcs has failed in the
safe direction — reports and refusals, never wrong edits. Remaining untested:
replan, TOO_BIG splits, architecture-checkpoint ticket insertion,
ci-pending timeout — all rare-path; acceptable to meet in the wild on arc
three (XLSX, 11 icebox entries queued).
