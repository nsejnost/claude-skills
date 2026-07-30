# Autopilot validation program — capstone

Date: 2026-07-30 · Skill: autopilot (final at v1.1, `skill_version: 1.1`,
`schema: 1`) · Target for all runs: nsejnost/tracklist-sandbox · Companion
docs: `2026-07-29-csv-export-arc-postmortem.md`,
`2026-07-29-smoke-gate-repair-drill.md`,
`2026-07-29-scheduling-tool-approval-policy.md`.

This closes the validation program: four production runs exercising every core
and high-consequence path of the skill. Part 1 reports the final run (the Type 1
ADR drill). Part 2 summarizes the whole program.

---

## Part 1 — Type 1 ADR drill (fuzzy-search)

**Why.** Across the first three runs, no decision ever triggered the Decision
Protocol's Type 1 path (research → prototype → full ADR → adversarial red-team →
Auditor countersign). csv-export's decisions were Type 2; smoke-gate had zero;
xlsx-export's one one-way-door decision (dependency vs hand-roll) was pinned in
the charter. So the highest-consequence decision path — the one whose failure
would be worst because the decisions are irreversible — was never observed live.

**Design.** The inverse of xlsx-export: a fixture charter (`auto/fuzzy-search`)
for a client-side fuzzy-search feature that *deliberately left the matching
engine open* — "adopt at most one search dependency vs hand-roll" — and
delegated it to the run as a Type 1 decision, with the dependency freeze
explicitly loosened to exactly one candidate gated behind a justified ADR. "New
runtime dependency" is the skill's own canonical Type 1, so classification was
unambiguous: waving it through as Type 2 would have been an immediate finding.
The drill was halted by design after the ADR landed — it never needed to reach
BUILD.

**Result — a comprehensive pass; zero findings.** The run (5/8 sessions,
halted-by-user after DECIDE):
- MAP charted a genuine **decision ticket** (#03) fed by a **research** ticket
  (#01) and a **prototype** ticket (#02) — it did not route around the fork.
- Research ran foreground against primary sources (Fuse.js / fuzzysort / uFuzzy
  profiled from npm registry + bundlephobia + docs); prototype ran empirically
  (a ~40-line hand-rolled subsequence matcher, 4.54 ms/query over 10k rows, on a
  scratch branch never merged to main — the prototype rail honored).
- DECIDE ran the full protocol in **five isolated subagent contexts**: Griller
  (3 evidence-bearing forks, facts bounced) → Decider (saw only charter + empty
  ledger + questions) → Red-team → Decider-answers → Auditor.
- The **red-team was genuinely adversarial** — it pressed the strongest case
  *for* a library ("approximate ⇒ edit-distance ⇒ Priority 3 > Priority 2 forces
  Fuse.js"), explicitly called the prototype "grading own homework," and demanded
  four amendments.
- The ADR (D-0001) **concluded NOT to adopt a dependency**, grounded in charter
  text: "approximate" is typed by the charter against *substring*, not
  edit-distance (grep-confirmed the words typo/edit-distance/substitution appear
  nowhere in the charter), so typo-tolerance is untyped and the dependency
  stance's "absent a justified ADR, hand-roll" governs. It carried a killer
  invariance argument — *even under the adversarial reading, a dependency-free
  banded-Levenshtein satisfies edit-distance, so the dependency is never
  compelled* — making the conclusion robust to the central ambiguity's outcome.
- It was **intellectually honest**: conceded the multi-column objection was
  factually true (then showed it discriminated nothing between the options), and
  logged the chosen matcher's no-substitution-typo bound openly as "deliberate,
  textually-grounded, not an oversight." Fuse.js v7.5.0 recorded as the drop-in
  runner-up with a concrete "declined because."
- The **Auditor countersign re-verified** the pivotal premise independently
  (grep-confirming the absent terms), not a rubber stamp.

The drill was built to test whether the Type 1 machinery *fires*; it fired and
produced a nuanced "no dependency" over its own red-team's strongest push,
grounded in text — the opposite of the easy failure mode (theatrically adopting
the obvious library). Arguably the strongest single artifact the skill produced.

---

## Part 2 — program completion summary

### The four runs

| Run | Role | Outcome | What it proved |
| --- | --- | --- | --- |
| **csv-export** | feature arc (happy path) | DONE · 8 tickets first-try · 11/40 sessions · ~5.8 h · 0 halts | Charter→merged-on-main unattended works end to end |
| **smoke-gate** | small arc + **repair drill** | DONE · deliberate budget HALT → Repair → resume → DONE | HALT-well-and-recover: the escape hatch opens; 8 fixes found |
| **xlsx-export** | feature arc (hardest) | DONE · 5 tickets first-try · 10/30 sessions · independently corroborated | Hand-rolled binary format ships; **two-axis review caught a real shipping bug** (a hollow chunk loop = 10k UI freeze that passed naive tests) |
| **fuzzy-search** | **Type 1 drill** | HALTED-by-design after the ADR · 5/8 sessions · zero findings | The Type 1 ADR path fires with full rigor and lands on justified restraint |

xlsx-export was independently corroborated (state.md / session-log.md /
completion-report.md / decisions.md read directly): numbers reconcile with real
build logic (bundle held at 216 KB until the UI imported the engine, then 220),
and the review-caught bug is logged.

### Coverage — exercised in production
Full phase machine (VALIDATE→…→FINISH); charter New/Renewal/Repair sub-modes;
`pause_after_spec` pause + re-arm; parallel waves with disjoint touches; research
tickets (foreground, primary-source); prototype tickets (logic, scratch-branch);
Decision Protocol **Type 2** (xlsx ×4) and **Type 1 ADR + red-team + countersign**
(fuzzy-search); two-axis review catching a real spec-faithfulness violation;
architecture checkpoint (ran, triaged to icebox); HALT→Repair→resume;
`launched:` re-stamp; the staleness rail (re-fetch before acting after a
park/interruption); babysitter carrying the run through a live `send_later` MCP
disconnect; squash-merge PRs, dashboard lifecycle, archive PR; denied-re-arm
absorption (Lane A approval-reality).

### Coverage — still harness-only (rare paths; safe to meet live)
TOO_BIG split (came close in xlsx #03/#06, justified not-split; fuzzy-search
halted before BUILD); architecture checkpoint *inserting* a bounded-refactor
ticket (xlsx's checkpoint correctly triaged all findings to icebox instead);
replan path; rebase-conflict retry-solo; CI-red diagnose/fix loop (xlsx's review
caught the freeze pre-CI, so CI never went red needing it); ci-pending timeout;
**Lane B** (upstream-blocked by #54260 — cannot be exercised on this account).

### Findings — all patched, none open
- **Interview compression family** (≥4 instances across two interviews): the core
  defect — bare prompts without analysis — was fixed in three escalating attempts,
  ending structural (`e8cc074`): the per-question analysis now rides *inside* the
  AskUserQuestion call, verified live in the xlsx-export interview (compliant from
  question one on). Two residuals, logged honestly: (a) a follow-on *layout*
  refinement (`4380e3f` — per-option pros/cons in the option descriptions,
  visible-label references) landed mid-interview and has **not yet faced a live
  interview** — its first exercise is the next charter run (low risk: the analysis
  is present regardless, with the question-text fallback preserved); (b) this class
  is **instruction-enforced, not test-enforced** — charter mode refuses headless
  invocation, so unlike every run-mode contract it has no deterministic harness
  gate. That interactivity is precisely why it regressed twice; the structural
  placement is the strongest available lever, not a guarantee.
- **Repair drill**: 8 fixes (attendance measured-not-inferred; babysitter
  survives awaiting-human states; `launched:` re-stamp; INTEGRATE-vs-same-gate
  semantics; the staleness rail; and more — see that report).
- **Scheduling approval**: documented as platform policy
  (`requiresUserInteraction`), not a bug — the dual-lane (opportunistic chain +
  guaranteed babysitter floor) is the permanent web architecture.
- **Type 1 drill**: zero findings — the machinery worked on first live exercise.

### Platform constraints catalogued (encoded in the skill)
MCP-created fresh-session Routines don't materialize (anthropics/claude-code#54260)
→ babysitter is human-pasted; scheduling tools force per-call approval → chain is
opportunistic, babysitter is the floor; agents cannot modify UI-created Routines
→ human deletes the babysitter; branch deletion is proxy-blocked → human cleanup;
the org rejects the `connectors` param on MCP triggers → Lane B doubly dead here.

### Bottom line
The skill is production-proven. Its honest trade holds — decision quality is
capped by charter quality, and charter silence produces conservative, reversible
defaults, never invented intent. Across four runs and roughly two dozen sessions,
**every failure failed safe**: a report, a refusal, or a clean halt — never a
wrong edit to main. The remaining untested paths are rare and low-consequence to
encounter live, because each degrades to the same safe halt. What's left is not
more validation but use.
