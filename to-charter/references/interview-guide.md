# Interview Guide

Per-section strategy for the to-charter interview. SKILL.md holds the rules; this
file holds the craft. Question counts are guidance, not quotas — spend the budget
where this repo's answers are least obvious.

## Destination (1–2 questions)
Goal: one paragraph, outcome-shaped, implementation-free.
- "Finish this sentence: this arc succeeds if ___."
- If the answer names technologies, reflect it back stripped: "so the outcome is X,
  and TanStack is one way there — should the charter fix the tool or the outcome?"

## Done-when (3–6 questions; highest stakes)
Goal: every line is `command → expected`, proven runnable during the interview.
Conversion moves:
- Vibe → observable: "app feels responsive" → "what would you measure to know?" →
  a timing or Lighthouse budget with a command.
- Feature → test: "metronome works" → "which test file proves it? If none exists,
  the Done-when is `npx vitest run tests/metronome.test.ts` passing with ≥N
  assertions — and writing that test is part of the arc."
- Ratchets need baselines: run the suite now, record counts, write the invariant
  relative to them.
Refusal is part of the job: a line that can't be made runnable moves to
Destination prose, not Done-when.

## Scope (3–5 questions)
In: transcribe the braindump, then ask "what's the smallest version you'd still
call success?" — the answer usually splits v1 from icebox.
Out (adversarial, at least 2 questions):
- "What would an eager agent plausibly add that you'd hate?"
- Recon-informed temptations: name real gaps ("no telemetry, no i18n, thin
  README — in or out?").
- Anything ambiguous lands in Out explicitly; silence is what eager agents exploit.

## No-touch zones (1–2 questions)
Present recon candidates (fragile paths, generated code, vendored dirs, files
under active human revision) as a checklist to confirm or extend. Remind: touching
one fails the merge gate regardless of green tests.

## Priorities (1 question)
Force a strict ranking of 3–5 values (mergeability, convention-faithfulness,
completeness, polish, speed). No ties — the Decider uses this ranking to break
Type 2 deadlocks, and ties break nothing.

## Silence-defaults (3–5 questions; second-highest stakes)
Scenario bank — pose concretely, then generalize the answer into a rule and read
the rule back:
- Persistence: "mid-run, the agent needs to store user preferences and the charter
  is silent. What should it do?"
- Dependency: "a ticket is 10x easier with a new npm package. Allowed? Under what
  ceiling (size, license, maintenance)?"
- Visual: "a spacing decision isn't covered by the tokens. Match the nearest
  existing pattern, or halt?"
- Copy/tone: "the agent must write user-facing text. What's the style source?"
- Data shape: "a migration would simplify state. Type 1 always, or Type 2 below
  some blast radius?"
Always confirm the general rule, not just the scenario answer.

## Stall policy (1 question)
Walk the three stalls (blocked ticket / decision conflict / done-when unmet after
replan) with the skill's defaults; change only what the human objects to.

## Budgets (0–1 questions)
Propose defaults scaled by arc size from recon (ticket-count guess → sessions).
Ask only if the human's risk posture is unclear.

## Branch & merge (0–1 questions)
Propose from recon (default branch, protection). Confirm the integration-branch
name.

## Quality invariants (1–2 questions)
Start from recon baselines (test count, xfail count, bundle size if measurable,
CI commands verbatim). Ask only for arc-specific additions.

## Tech constraints (1–2 questions)
Stack boundaries and the dependency-policy line (usually "new runtime deps require
a Type 1 ADR"). Confirm the environments and versions recon found.

## Glossary (0–1 questions)
Harvest, don't ask cold: terms the human used two ways during the interview, or
domain words recon found in code comments. Read back one-line definitions.

## Renewal mode
Diff-first: show carried-forward sections as a compact list of proposals tagged
"(carried from <arc>)"; interview Destination / Done-when / Scope fresh; end with
one question — "any standing policy that should change this arc?" — before the
full read-back.

## Repair mode
Read halt-report.md's open decisions verbatim. Each becomes one question. Answers
append to the named charter section under a dated
`# appended after HALT <date>` comment. No other section is touched or
re-confirmed.

## Transcript format (docs/auto/charter-interview.md)

    # Charter interview — <arc> — <date> — mode: NEW|RENEWAL|REPAIR
    ## <section>
    Q1: <question>
    A1: <answer verbatim> [ANSWER]
    P1: <proposal shown> → <confirmed | edited: ...> [FACT-CONFIRMED]
    D1: <template default> → accepted [DEFAULT-ACCEPTED]
    => charter lines written: <the exact lines>

    (repeat per section; end with)
    ## Full read-back
    Confirmed by human: <date/time>

A PARTIAL header at the top marks an interrupted interview:
`STATUS: PARTIAL — resumed interviews restart at the last confirmed section.`

## Anchoring discipline (applies everywhere)
Every proposal is labeled "proposal — edit freely." Recon facts are stated with
their evidence ("vitest reports 214 tests"). If the human hesitates, present the
opposite option with equal weight before they choose.
