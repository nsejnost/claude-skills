# CHARTER — <arc name>

STATUS: TEMPLATE — the charter interview removes this line; validation refuses to run while it is present.

<!-- Authored by a human through the /autopilot charter interview, once, before
     launch. Read-only in run mode; amended only through the interview (Repair /
     Renewal). Every section is load-bearing: the Decider answers runtime
     questions from this document, so an unanswerable question here becomes a
     silence-default or a halt there. Write it like testimony, not a wish list. -->

## Destination
One paragraph. The outcome, not an implementation.

## Done-when (mechanically checkable — this defines termination)
Every line is a command and an expected result, proven runnable during the
interview. If it can't be run, it can't terminate an unattended run.
- [ ] `<command>` → `<expected>`
- [ ] `<command>` → `<expected>`

## Priorities (strict ranking — the Decider's tiebreaker for Type 2 decisions)
1. <e.g. mergeability / zero regressions>
2. <e.g. faithfulness to existing conventions>
3. <e.g. feature completeness>
4. <e.g. polish>

## Scope
**In (the braindump):** candidate features, rough shapes, examples.
**Out (explicit — be blunt):** everything an eager agent might plausibly add
that you'd hate. Ambiguity goes here, not into silence.

## No-touch zones
Paths, modules, and behaviors the run must not modify. Violating one fails the
integrate gate regardless of green tests.
- <e.g. `src/example-generated/**` (generated code)>
- <e.g. `docs/legal/**`>

## Silence-defaults (what the Decider does when this charter is quiet)
Default of defaults, applied in order: (1) follow the existing codebase
convention; (2) pick the smallest reversible option; (3) prefer no new
dependency; (4) still tied → defer to Priorities. Domain-specific rules below:
- <e.g. new UI state → the existing preferences store, versioned>
- <e.g. visual questions → match existing design tokens; never invent a palette>
- <e.g. user-facing copy → match the tone of existing strings; en-US>

## Stall policy
- Ticket blocked after max attempts: `descope-to-icebox` | `leave-blocked`
- Unresolvable decision conflict: `halt` | `descope-to-icebox`
- Done-when unmet after replan budget: `halt`  (recommended; override knowingly)
- CI red that reproduces on main (pre-existing): `note-and-continue` | `halt`

## Budgets
- max_sessions: 60
- max_parallel: 3
- max_attempts_per_ticket: 3
- max_review_cycles: 2
- max_griller_questions: 7
- replans: 1
- ci_wait_minutes: 20
- arch_checkpoint_every: 5        # merged tickets between architecture checkpoints; 0 disables
- max_session_minutes: 90
- max_hours:                      # optional wall clock for the whole run; blank = none
- pause_after_spec: false         # true = halt for a human read of the frozen spec
- mutation_check: false           # true = reviewer reverts one behavior to prove its test goes red

## Merge & CI policy
- target_branch: main
- delivery: per-ticket PRs, squash-merged automatically on green; no human review gate
- required repo settings: squash merge enabled; no required human reviews on main;
  auto-merge enabled if branch protection requires status checks
- ci: <the workflow(s) that must pass, or "none configured — local gates only">

## Quality invariants (ratchets — monotonic for the whole run)
- CI green on every merge — commands, verbatim: <e.g. `npm test`, `npm run typecheck`>
- Test count never decreases; xfail/skip never increases (consolidation requires
  an Auditor-countersigned D-entry)
- Baselines at charter time: tests=<n> xfail=<n> skip=<n>  (recorded by recon)
- <arc-specific ratchets, e.g. bundle ≤ current + N kB, measured by: `<command>`>

## Tech constraints
Stack boundaries, environments, versions. Dependency policy (default: new
runtime dependencies require a Type 1 ADR).

## Glossary (optional but high-leverage)
Terms the Griller and Decider must use consistently — ambiguous vocabulary is
the top source of confidently-wrong autonomous decisions.
- <term> — <meaning>
