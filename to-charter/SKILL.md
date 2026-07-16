---
name: to-charter
description: Build or renew a CHARTER.md for an unattended-flow run through a structured, human-attended interview. Use when the user asks to write, create, build, or renew a charter, says "interview me for the charter" or "grill me for the charter", invokes /to-charter, or when docs/auto/state.md shows HALTED-AWAITING-CHARTER and a human is present. Strictly interactive — if no human can answer (headless -p invocation or an unattended-flow session), refuse and exit immediately — this skill asks questions and waits.
---

# To Charter

Interview the human, transcribe their judgment into `docs/auto/CHARTER.md`. The
charter is the fixed oracle an unattended run reasons from — every runtime decision
traces back to it — so its quality is the ceiling on the whole run. This skill
raises that ceiling the only legitimate way: by asking the human better questions
at authoring time, never by inventing answers.

Division of labor, absolute: **the human makes every decision; this skill supplies
recon, structure, and persistence.** A charter line may exist only if it traces to
(a) an answer the human gave, (b) a repo fact the human confirmed, or (c) a template
default the human explicitly accepted. No fourth source.

## Attendance check (before anything else)

If this is a non-interactive invocation (`claude -p`, a runner loop, or any context
where a human cannot answer the next question), print one line — "to-charter is a
human-attended interview; run it in an interactive session" — and exit. Do not
scaffold, guess, or partially fill anything.

## Mode detection

1. **Repair** — `docs/auto/halt-report.md` exists with open decisions: interview
   only those questions; output is appended charter lines (usually Silence-defaults
   or Scope), not a rewrite.
2. **Renewal** — a substantive charter exists (`docs/auto/CHARTER.md` with real
   content, or under `docs/auto/archive/`): carry the stable sections forward as
   labeled proposals (No-touch, Silence-defaults, Stall policy, Budgets, Branch &
   merge, Quality invariants, Tech constraints, Glossary); interview only
   Destination, Done-when, and Scope, plus one pass of "any standing policy
   changes this arc?"
3. **New** — otherwise: full interview.

## Phase 0 — Recon (read-only, before the first question)

Explore the repo and pre-fill FACTS as proposals so questions are spent on
DECISIONS:

- CI / test / lint / typecheck commands (workflows, package scripts, Makefile) and
  current baselines — run the test suite once to capture test and xfail/skip
  counts for the Quality-invariants ratchets.
- Conventions: state management, styling/tokens, dependency posture, doc layout,
  existing `docs/agents/` tracker config.
- Fragile or high-blast-radius paths → No-touch candidates.
- Default branch and protection → Branch & merge proposals.

Present recon output as **proposals the human confirms or edits** — labeled as
proposals, because unlabeled suggestions anchor. Never silently write a fact into
the charter.

## The interview

- **One question per message.** Multi-part questions get shallow answers.
- Budget: ~15 questions for Renewal, ~25 for New. Approaching the cap, switch from
  questions to proposals-to-edit for the remaining low-stakes sections.
- Order: Destination → Done-when → Scope (In, then adversarial Out) → No-touch →
  Priorities (forced ranking) → Silence-defaults (scenario elicitation) → Stall
  policy → Budgets → Branch & merge → Quality invariants → Tech constraints →
  Glossary (harvest terms the human used ambiguously during the interview).
- Depth is uneven on purpose: Done-when, Silence-defaults, and Scope-Out carry
  most of a run's failure modes and deserve most of the budget; Budgets and Branch
  policy are usually quick confirms. Per-section techniques, question banks, and
  worked examples live in `references/interview-guide.md` — read it before the
  first question.

Three techniques are load-bearing:

- **Done-when coaching**: refuse vibes. Every outcome becomes `command → expected`,
  and each command is executed during the interview to prove it runs (recon
  baselines double as evidence). A Done-when line that can't run guarantees a
  bootstrap halt later.
- **Scenario elicitation** for Silence-defaults: don't ask "what are your
  defaults?" — pose concrete mid-run dilemmas ("the agent needs a place to persist
  UI state and the charter is silent — what should it do?"), generalize the answer
  into a rule, read the rule back.
- **Adversarial Scope-Out**: ask what an eager agent would plausibly add that the
  human would hate, plus recon-informed temptations ("this repo has no analytics —
  is adding telemetry in or out?").

## Read-back gates

After each section: read the drafted section back verbatim; the human confirms or
edits before the next section begins. After the last section: full-charter
read-back and explicit confirmation before any file is written. The confirmation
gate that unattended-flow mechanized at runtime lives here in its original, human
form.

## Output

- Write `docs/auto/CHARTER.md` (create `docs/auto/` if needed). Match the
  formatting of the scaffolded charter if unattended-flow's bootstrap already
  created one; else use the installed unattended-flow template
  (`references/charter-template.md` in that skill's folder) if locatable; else
  generate from the section order above — the sections are the contract, the
  prose is not.
- Save the transcript to `docs/auto/charter-interview.md` with per-line provenance
  tags ([ANSWER] / [FACT-CONFIRMED] / [DEFAULT-ACCEPTED]) — format in
  `references/interview-guide.md`.
- Leave `state.md` alone. Validation is unattended-flow's job; its bootstrap
  re-validates on the next runner invocation.
- Offer (don't assume) a commit of the charter + transcript; recommend yes.
- Close with the next step: start the runner, or a single
  `claude -p "/unattended-flow resume"` to watch bootstrap validate.

## Rails

- Never fabricate, infer, or self-answer a decision question — silence in the
  human's answers stays silent (the template's guidance comments remain in place).
- Never start the run, create branches or issues, or modify anything outside
  `docs/auto/CHARTER.md` and `docs/auto/charter-interview.md` (plus the optional,
  explicitly confirmed commit).
- Recon is read-only except for running the existing test suite to capture
  baselines.
- If the human wants to stop mid-interview, write no charter, save the partial
  transcript with a PARTIAL header, and tell them resuming later restarts from
  the last confirmed section.
