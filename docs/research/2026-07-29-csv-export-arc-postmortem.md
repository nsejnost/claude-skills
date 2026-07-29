# Post-mortem — csv-export arc (autopilot v1.0, first production run)

Date: 2026-07-29 · Target repo: nsejnost/tracklist-sandbox · Skill: autopilot 1.0
(schema 1) · Runner: Lane A self-bind chain + UI-created hourly babysitter.

Evidence: the frozen spec, the DONE status report, dashboard/session screenshots,
and the skills-repo commit log. Two archive files were not yet read directly
(session-log.md, the completion report verbatim — see "Evidence gaps"); numbers
quoted from the status report are treated as authoritative since it read state
from origin.

## Verdict

**The skill did the thing it was built for.** A human-authored charter went to
merged-on-main with zero mid-run human decisions: the only human touches after
launch were approval taps for chain wakes (optional by design) and the
`pause_after_spec` review (a deliberate checkpoint). Every unattended hour was
carried by the babysitter exactly as the approval-reality doctrine predicted.
Eight findings surfaced across the arc's lifecycle; all eight were patched to
main the same day they were found, none required touching the running arc's
state, and one was exercised by the run itself: the babysitter survived the
spec pause (its headless disable was refused) and carried BUILD to DONE.

## Outcome metrics

| Metric | Result | Budget / expectation |
| --- | --- | --- |
| Tickets closed | 8/8, all first-attempt | attempts allowed: 3 each |
| Build waves | 2 (#06 solo → #07 ∥ #08) | max_parallel 3 |
| Halts / gate failures / replans | 0 / 0 / 0 | — |
| Sessions used | 11/40 | 3.6× headroom |
| Wall clock | 01:12Z → 07:00Z on 07-29 (~5.8 h incl. ~1 h review pause) | max_hours 24; elapsed 5.8 |
| Tests | 80/80 green (63 baseline + 12 engine + 5 UI) | spec floor ≥75; math exact |
| Bundle | 216 KB | ratchet ≤ 230 KB |
| Done-when | 5/5 re-verified against main | charter |
| Decisions | 16 (1 Type-1 ADR, red-teamed) | — |
| Icebox | 4 findings (XLSX; smoke-in-CI; +2 unread) | — |
| Archive | PR #7 merged; dashboard #2 closed ✅ | — |

## Timeline

All times 2026-07-29 UTC — the arc's whole life fit one calendar day; the
human's overnight fell inside it because ET midnight is 04:00Z.

| When (Z) | What |
| --- | --- |
| ~00:30 | Charter interview (compression defect found mid-flight, patched) |
| 01:12–01:45 | Launch (`launched: 01:12Z`); VALIDATE passes (Auditor 4/4); chain armed |
| 01:45–03:40 | MAP → DECIDE (16 D-entries, research + prototype) → SPEC frozen (Auditor 5/5) |
| 03:40–~04:45 | PAUSED-SPEC-REVIEW (~1 h same-evening human review; babysitter idled correctly) |
| ~04:45 | Re-arm (pre-dates the re-stamp fix; the original `launched:` stamp stood) |
| ~04:50 | TICKETS gate PASS (caught a real cross-ticket defect); chain wake then parks on an unanswered approval |
| 05:34–07:00 | Babysitter carries BUILD wave 1, wave 2, FINISH at hourly cadence |
| 07:00 | DONE. Archive merged, dashboard closed |
| ~11:54 | Parked chain turn resumed by a human "stop" message with a ~7 h-stale world-model (defense-in-depth held; new rail patched) |

Correction (2026-07-29): an earlier revision dated the re-arm and DONE to
07-30 and inferred a ~21.5 h review pause. Container-clock provenance
(`setup v18 ran 2026-07-29T13:03Z`, on a container whose skills clone
post-dates this document's first commit) disproved that: the pause was ~1 h
and the whole arc ran 01:12–07:00Z on 07-29. Finding 6's fix was authored on
the mistaken premise — see the corrected ledger row.

## Defect ledger — 8 found, 8 fixed, 0 open

| # | Finding | Found by | Fix |
| --- | --- | --- | --- |
| 1 | Ticket-branch ref collision (`auto/<arc>/tNN` impossible when `auto/<arc>` exists) | harness s7, pre-arc | e4f0361 (hyphenated `-tNN`) |
| 2 | Interview compression (bare prompts, no pros/cons/rationale/clarification path) | live interview screenshot | 2b28181 (mandatory per-question template) |
| 3 | VALIDATE demanded Done-when lines *pass* at arc start (would halt every valid charter) | red-team of the real charter, pre-launch | 92e190b (lines must RUN; unmet = baseline) |
| 4 | INTEGRATE failures vs consecutive-same-gate HALT unspecified | flow.md traceability audit (PR #6) | d0024c4 (attempts govern; HALT is phase-gates-only) |
| 5 | Wakes at `PAUSED*` told to disable Routines — would kill the babysitter the resume depends on | reasoning about the live pause | b86a3ab (babysitter survives PAUSED*) |
| 6 | `max_hours` counts calendar time incl. human pauses — a long review pause could eat the whole budget | bedtime arithmetic on the live arc (premise later found mis-dated) | 273c3b4 (re-arm re-stamps `launched:`) — correct doctrine, **unexercised**: the original 01:12Z stamp stood and elapsed 5.8 h never approached 24 h |
| 7 | Agents cannot disable/delete UI-created Routines (deletion is human-only, not a fallback) | status session's refused attempt | 4a6fc77 (terminal reports hand the human the step) |
| 8 | A parked turn resumed hours later acts on stale conversation memory (ran stop against a DONE arc) | the sleepwalker incident | 36fa97f (staleness rail: re-fetch before any state change; terminal ⇒ report only) |

Mean discovery→merged-fix latency: minutes to low hours. None required an arc
stop; all were schema-1-compatible.

## Platform constraint catalog (environment truths, now encoded in the skill)

1. MCP-created fresh-session Routines never materialize (anthropics/claude-code#54260,
   closed not-planned); UI-created ones work → babysitter is human-pasted.
2. Scheduling MCP tools are "Allow once" per call in the web UI → the chain is
   opportunistic; the babysitter is the guaranteed floor (~1 unit/hour unattended).
3. Agents cannot modify UI-created Routines (mirror of #1; verified 07-29).
4. Branch deletion from sessions is blocked (403 / silently swallowed) → cleanup
   of ticket branches is a human step; runs must not treat it as failure.
5. MCP servers can re-register under a different tool prefix mid-conversation;
   retry by name, then fall through to the babysitter.

## What the process caught (gates earning their keep)

- **TICKETS gate**: found #07 pinning "= 80 total tests" while #06 allowed
  "≥ 12" — a spurious-failure coupling; pinned #06 to exactly T1–T12 before
  BUILD. This is the strongest single data point for fresh-context gate audits.
- **SPEC red-team + decision pipeline**: D-0010's prototype de-risked the two
  riskiest assumptions (Node native TS import; resolve-hook confinement) before
  they could burn attempts.
- **Claim protocol + non-FF push rejection**: made both the parked-turn
  resurrection (finding 8) and any overlap between chain and babysitter
  harmless in practice. "Origin is the program" held under real chaos.

## Paths exercised vs not

Exercised in production: full phase machine VALIDATE→…→DONE, pause/re-arm,
parallel wave with disjoint touches, prototype + research + decision tickets,
Type-1 ADR red-team, archive PR, dashboard lifecycle, babysitter adoption of a
dead chain, denied-approval absorption.

**Not yet exercised** (known-untested, not defects): HALT → Repair interview
(only in harness s-tests), replan path, TOO_BIG split, architecture checkpoint
(needs ≥5 merged build tickets; this arc merged 4), rebase-conflict retry-solo,
CI-red diagnose/fix loop (CI never went red), ci-pending timeout path, Lane B
(upstream-blocked). The next arc should expect first-exercise wrinkles on any
of these.

## Cost & cadence data (for budgeting arc two)

- 8-ticket arc ≈ 11 claiming sessions + ~6 babysitter no-op fires + 3 attended
  sessions (interview, preflight+launch, re-arm).
- Attended-cadence phases (human approving wakes): VALIDATE→SPEC in ~2.5 h.
  Unattended cadence: ~1 unit/hour (babysitter floor) → BUILD waves + FINISH
  in the ~2 h overnight tail.
- Budget calibration: max_sessions 40 was 3.6× actual; keep generous — the cost
  of headroom is zero, the cost of a mid-BUILD budget halt is a repair cycle.
- Total calendar 01:12→07:00Z (~5.8 h), of which ~1 h was the deliberate
  spec-review pause. `max_hours` (24) was never in sight this arc; the
  re-stamp doctrine matters for arcs whose pauses span days.

## Charter lessons for the next arc

1. `pause_after_spec: true` earned its keep (calibration + the review caught
   nothing wrong — which is itself calibration). Keep ON for arc two, consider
   OFF after.
2. Spec craft: avoid cross-ticket count pins ("= 80 total") — totals belong to
   the final ticket or the gate. (The gate caught it, but authoring can avoid it.)
3. Renewal should carry forward: dep freeze, no-touch zones, ratchet commands,
   stall policy — all behaved. Fresh interview needed for Destination/Done-when/
   Scope only, as designed.
4. XLSX is the charter-named next candidate and sized similarly (engine + UI +
   fixture path already exist); expect the architecture checkpoint to fire this
   time if ticket count ≥5 merged builds.

## Recommendations & open backlog

1. **Skill status: production-ready** for arcs of this shape on this account.
   Version freeze at 1.0/schema 1 held for the whole arc; setup script now v17
   → all fixes propagate.
2. Backlog, in rough priority: (a) test repo-level `.claude/settings.json`
   permission allowlisting of the scheduling tools — if it works, the chain
   stops being approval-gated and unattended cadence drops from ~60 min to
   ~3 min; (b) first-exercise the Repair path deliberately (e.g. induce a
   benign HALT in a sandbox arc); (c) skill-atlas.html refresh; (d) upstream
   follow-up on #54260 with the 14/14 repro data.

## Evidence gaps

Read before treating this as final: `docs/auto/archive/csv-export/session-log.md`
(per-session cadence, babysitter vs chain attribution) and the completion
report + icebox verbatim (2 of 4 icebox entries unknown here). The sandbox repo
was not attachable from the authoring session (MCP approval unavailable); a
paste or a fresh-session read closes the gap.
