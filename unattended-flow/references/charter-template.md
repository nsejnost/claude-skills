# CHARTER — <arc name>

<!-- Written by a human, once, before launch. Agents treat this file as read-only.
     Every section is load-bearing: the Decider role answers grill questions from
     this document, so an unanswerable question here becomes a silence-default or
     a halt there. Write it like testimony, not like a wish list. -->

## Destination
One paragraph. The loose idea, stated as an outcome, not an implementation.

## Done-when (mechanically checkable — this defines termination)
Every line is a command and an expected result. If it can't be run, it can't
terminate an unattended run.
- [ ] `<command>` → `<expected>`
- [ ] `<command>` → `<expected>`

## Priorities (strict ranking — the Decider's tiebreaker for Type 2 decisions)
1. e.g. Mergeability / zero regressions
2. e.g. Faithfulness to existing conventions
3. e.g. Feature completeness
4. e.g. Polish / aesthetics

## Scope
**In:** bullet the braindump — candidate features, rough shapes, examples.
**Out (explicit):** anything an eager agent might reasonably add. Be blunt.

## No-touch zones
Paths, modules, behaviors, and issues the run must not modify. Violating one is a
failed merge gate regardless of test results.
- e.g. `analytics/**` (Python engine), penalty-coefficient logic (issue #35), `Help.jsx` copy (#27)

## Silence-defaults (what the Decider does when this charter is quiet)
Default of defaults, applied in order: (1) follow the existing codebase convention;
(2) pick the smallest reversible option; (3) prefer no new dependency; (4) if still
tied, defer to Priorities. Add domain-specific defaults below:
- e.g. New UI state → versioned localStorage via the existing preferences store
- e.g. Visual questions → match the existing design tokens; never invent a palette

## Stall policy (choose one per line)
- Ticket blocked after max attempts: `descope-to-icebox` | `leave-blocked`
- Unresolvable decision conflict: `halt` | `descope-to-icebox`
- Done-when unmet after replan budget: `halt` (recommended; do not override lightly)

## Budgets (override skill defaults here)
- max_sessions: 60
- max_attempts_per_ticket: 3
- max_review_cycles_per_attempt: 2
- max_griller_questions_per_decision: 7
- replans: 1

## Branch & merge policy
- target_branch: main
- integration_branch: auto/<arc-slug>   <!-- created at bootstrap; sole merge target during the run -->
- final delivery: one PR integration → target; a human may review it later, or not.

## Quality invariants (ratchets — monotonic for the whole run)
- CI green on every merge (list the exact commands if CI config is ambiguous)
- Test count never decreases; xfail/skip count never increases
- Add arc-specific ratchets, e.g. bundle size ≤ current + N kB, Lighthouse a11y ≥ current

## Tech constraints
Stack boundaries, dependency policy (e.g. "new runtime deps require a Type 1 ADR"),
environments, anything the spec must respect.

## Glossary (optional but high-leverage)
Domain terms the Griller and Decider must use consistently. Ambiguous vocabulary is
the top source of confidently-wrong autonomous decisions.
- term — meaning
