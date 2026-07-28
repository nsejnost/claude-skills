# CHARTER — sktest-s7

## Destination
A throwaway test arc used by the skill-test harness to exercise the autopilot
skill's contract. It builds nothing.

## Done-when (mechanically checkable — this defines termination)
- [ ] `true` → exit 0

## Priorities (strict ranking)
1. Zero regressions
2. Faithfulness to existing conventions
3. Completeness

## Scope
**In:** (test arc — no features)
**Out (explicit):** everything else; any change outside docs/auto/ except as the
skill's own protocol requires.

## No-touch zones
- README.md

## Silence-defaults
Default order: existing convention → smallest reversible → no new dependency →
Priorities.

## Stall policy
- Ticket blocked after max attempts: leave-blocked
- Unresolvable decision conflict: halt
- Done-when unmet after replan budget: halt
- CI red that reproduces on main: halt

## Budgets
- max_sessions: 5
- max_parallel: 1
- max_attempts_per_ticket: 1
- max_review_cycles: 1
- max_griller_questions: 3
- replans: 0
- ci_wait_minutes: 5
- arch_checkpoint_every: 0
- max_session_minutes: 90
- max_hours:
- pause_after_spec: false
- mutation_check: false

## Merge & CI policy
- target_branch: sktest-s7-target
- delivery: per-ticket PRs, squash-merged automatically on green
- ci: none configured — local gates only

## Quality invariants (ratchets)
- CI green on every merge — commands: `true`
- Baselines at charter time: tests=0 xfail=0 skip=0

## Tech constraints
None. New runtime dependencies require a Type 1 ADR.

## Glossary
- test arc — this fixture; it exists only to be observed
