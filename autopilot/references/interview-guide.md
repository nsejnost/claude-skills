# Interview Guide — charter mode

The charter is the fixed oracle the whole run reasons from; its quality is the
ceiling on the run. This interview raises the ceiling the only legitimate way:
better questions at authoring time, never invented answers. Division of labor,
absolute: **the human makes every decision; the agent supplies recon, structure,
options, and persistence.** A charter line exists only if it traces to (a) an
answer the human gave, (b) a repo fact the human confirmed, or (c) a default the
human explicitly accepted.

Attendance: strictly interactive. Headless invocation → print one line ("charter
mode is a human-attended interview — run it from a chat session") and exit.

## Sub-mode detection

1. **Repair** — halt-report.md has open decisions: ask ONLY those questions
   (verbatim from the report); answers append to the named charter sections
   under a dated `# appended after HALT <date>` comment; every appended
   Done-when-style line is executed to prove it runs; end by offering `launch`.
2. **Renewal** — a substantive charter exists (current or in `archive/`): move
   the finished arc's docs/auto contents to `archive/<arc>/` first; carry stable
   sections forward as labelled "(carried from <arc>)" proposals (No-touch,
   Silence-defaults, Stall policy, Budgets, Merge & CI, Quality invariants,
   Tech constraints, Glossary); interview Destination, Done-when, Scope fresh;
   close with one question — "any standing policy that should change this arc?"
3. **New** — otherwise: full interview. Offer `references/example-charter.md`
   as pre-reading ("here's what a finished charter looks like").

Question budget: ~25 (New), ~15 (Renewal). Clarification exchanges do NOT count;
grill-deeper spawned questions DO. Near the cap, switch to proposals-to-edit for
the remaining low-stakes sections.

## Phase 0 — Recon (before the first question)

Read-only, except running the existing test suite once for baselines. Never run
anything with side effects beyond the repo (deploys, migrations, anything
needing credentials) — note such commands, don't execute them.

- CI/test/lint/typecheck commands (workflows, package scripts) + current
  baselines: test count, xfail/skip, the exact ratchet commands.
- **Baseline red?** Surface it immediately: the arc must either include fixing
  it (early tickets) or the charter must adjust the CI-green invariant — a red
  baseline with a green-CI ratchet guarantees a halt at the first merge.
- **No test infra at all?** Then bootstrapping a runner + CI becomes the arc's
  mandatory first tickets — raise it as a question, and Done-when coaching
  builds on the to-be-created infra ("the Done-when is `npx vitest run
  tests/x.test.ts` passing — and creating that harness is ticket #1").
- Conventions (state management, styling, dependency posture), fragile paths →
  No-touch candidates, default branch + protection → Merge & CI proposals,
  repo maturity → budget proposals.

Present recon output as **labelled proposals the human confirms or edits** —
unlabelled suggestions anchor. Never silently write a fact into the charter.

## The question protocol (every question follows this loop)

One question per message. Multi-part questions get shallow answers.

1. **Context inside the clickable prompt's question text** (chat prose may
   duplicate it, never replace it — two live interviews proved separate prose
   gets dropped): what's being decided, why it matters for the run, then the
   **pros, cons, and implications of every option — equal analytical effort
   each**; the recommended option's cons are never softened. Then the **recommendation and its rationale**, tied to
   something checkable (a recon fact, an earlier answer, the ranked priorities)
   so the human can dispute the premise, not just the pick.
2. **The clickable prompt** (AskUserQuestion): recommended option first,
   suffixed "(Recommended)"; each option's description is a one-line distillation
   of its trade-off; multi-select where naturally multi-pick (e.g. no-touch
   candidates); more than 4 candidates → chunk into sequential prompts. The
   built-in "Other" field is the free-text path.
3. **Branch on the response**:
   - a click, or a typed **answer** → read the resulting charter line(s) back,
     log with provenance, next question.
   - a typed **question** → **clarification mode**: answer it fully; ask "more
     clarification, or ready to answer?" (clickable); when ready, re-present the
     ORIGINAL question unchanged — the choice is always made against the full
     option set, never from memory of it.
4. **Grill-deeper trigger**: if clarification surfaces (a) a constraint or risk
   the options don't reflect, (b) a viable alternative not offered, or (c)
   evidence the question's premise is wrong — do NOT just re-ask. Acknowledge
   what changed, recon if it's factual, revise the option set or spawn follow-up
   questions, and continue that thread until the human confirms shared
   understanding; then return to the (possibly revised) original question.
   Log with [CLARIFICATION] / [OPTION-REVISED] tags (format in formats.md).

**Per-question compliance template (required — structural since 2026-07-29,
after chat-prose delivery failed two verified acceptance tests).** Every
choice question MUST carry this shape inside the clickable prompt, SPLIT
across two fields — the shared framing in the question text, the per-option
Pros/Cons in the option descriptions — never crammed into the question text
alone:

> **Deciding:** <what this settles, and the charter line it will write>
> **Why it matters mid-run:** <the concrete failure a good answer prevents>
> **<exact option label>.** Pros: <…> Cons: <…>   ← one block per option;
> name options by their exact visible labels, never letters (dialogs may not
> render "A/B/C")
> **Recommendation: <label>, because <rationale tied to a recon fact or an
> earlier answer — something the human can dispute>.**
> *Not sure what's being asked? Type a question into "Other" — clarification
> is free, doesn't count against the budget, and the original question comes
> back afterward.*

Placement is load-bearing (observed 2026-07-30): the AskUserQuestion question
field renders as ONE block with line breaks collapsed, so per-option Pros/Cons
copied into it stack into an unreadable wall. So each option's Pros/Cons live
in that option's `description` field ONLY (verified to render in full on
Claude Code web) — do NOT duplicate them into the question text. The question
text stays to the shared elements above, terse; the per-option detail lives in
the separately-rendered option boxes. Analysis in separate chat prose (outside
the dialog) remains a violation.

The Other-reminder line is mandatory on every question — never assume the
human knows the Other field doubles as the clarification channel. Each
question's full template (framing + per-option Pros/Cons) is logged verbatim
in the interview transcript (formats), where the section read-back gates
verify it mechanically — a QN entry without its block fails the gate.
Self-check: the failure to prevent is a bare prompt with NO analysis anywhere
in the dialog; the fix is analysis IN the dialog — terse framing in the
question text, full Pros/Cons in the option boxes — NOT a long question text.
A bare prompt with unexplained options recreates the shallow-answer failure
the one-question rule exists to prevent.

Two question shapes: most sections are choice-shaped and use the full loop.
Generative questions (Destination, the braindump, first-pass Done-when) open as
free text; then convert your synthesis into clickable choices ("three tightened
phrasings — pick or edit").

**Anchoring discipline**: recommendations are permitted precisely because every
option carries honest pros/cons; if the human hesitates, present the opposite
option with equal weight before they choose. Recon facts are stated with
evidence ("vitest reports 214 tests").

## Section order and craft

**Destination** (1–2 Q). One paragraph, outcome-shaped, implementation-free.
"Finish this sentence: this arc succeeds if ___." Tech names get reflected back
stripped: "so the outcome is X and TanStack is one way there — fix the tool or
the outcome?"

**Done-when** (3–6 Q; highest stakes). Every line becomes `command → expected`,
**executed during the interview** to prove it runs. Conversion moves: vibe →
observable ("feels fast" → what would you measure → a budget with a command);
feature → test ("export works" → which test file proves it — writing it is part
of the arc). A line that can't be made runnable moves to Destination prose.
Refusal is part of the job.

**Scope** (3–5 Q). In: transcribe the braindump, then "what's the smallest
version you'd still call success?" — the answer splits v1 from icebox. Out
(adversarial, ≥2 Q): "what would an eager agent plausibly add that you'd hate?"
plus recon-informed temptations ("no telemetry, no i18n, thin README — in or
out?"). Ambiguity lands in Out explicitly; silence is what eager agents exploit.

**No-touch zones** (1–2 Q, multi-select). Recon candidates (fragile paths,
generated code, vendored dirs, files under active human revision) as a
checklist. Remind: touching one fails the integrate gate regardless of green
tests.

**Priorities** (1 Q). A strict ranking of 3–5 values (mergeability,
convention-faithfulness, completeness, polish, speed) — offer 2–4 candidate
rankings as options. No ties; ties break nothing.

**Silence-defaults** (3–5 Q; second-highest stakes). Scenario elicitation —
pose concrete mid-run dilemmas, generalize each answer into a rule, read the
rule back: persistence ("agent needs to store user prefs, charter silent — what
does it do?"), dependency ("a ticket is 10× easier with a new package — allowed?
under what ceiling?"), visual ("spacing not covered by tokens — match nearest
pattern or halt?"), copy/tone ("agent must write user-facing text — style
source?"), data shape ("a migration would simplify state — Type 1 always, or
Type 2 below some blast radius?"). Confirm the general rule, not just the
scenario answer.

**Stall policy** (1 Q). Walk the stalls (blocked ticket / decision conflict /
done-when unmet after replan) with defaults; change only what the human objects
to.

**Budgets** (0–1 Q). Propose defaults scaled by recon's ticket-count guess
(including `max_parallel`, `arch_checkpoint_every`, optional `max_hours`). Ask
only if risk posture is unclear.

**Merge & CI** (1–2 Q). Confirm: per-ticket squash-merged PRs auto-merged on
green (the autopilot default), target branch, `ci_wait_minutes`, the no-CI
stance if recon found none, and repo-settings prerequisites (squash merge on, no
required human reviews). `pause_after_spec`: recommend ON for the human's first
arc or two as a calibration ritual, off after.

**Quality invariants** (1–2 Q). From recon baselines: exact CI commands, test
count, xfail/skip, plus arc-specific ratchets (bundle size, a11y score). Record
the measurement commands verbatim.

**Tech constraints** (1–2 Q). Stack boundaries; the dependency line (default:
new runtime deps require a Type 1 ADR); environments and versions recon found.

**Glossary** (0–1 Q). Harvest, don't ask cold: terms the human used two ways
during the interview, domain words from code comments. Read back one-line
definitions — ambiguous vocabulary is the top source of confidently-wrong
autonomous decisions.

## Read-back gates

After each section: read the drafted section back verbatim; the human confirms
or edits before the next begins. After the last: full-charter read-back and
explicit confirmation before anything is written.

**Teeth (2026-07-29, after a live interview skipped this gate twice):** a
confirmation question is lawful only in a turn whose visible text already
contains the exact text being confirmed. Never ask against "above" when above
is empty, and never absorb a read-back demand into the question's label —
print the document, then ask. Permitted stronger form for the full charter:
write the draft to the coordination branch FIRST with the template's sentinel
line still present (an abandoned draft can then never pass VALIDATE), print
the pushed file verbatim, and on confirmation remove the sentinel and set
`status: READY` — confirming against the real artifact beats confirming
against a promise.

## Output (after the confirmed full read-back)

1. Create/checkout the coordination branch `auto/<arc-slug>` from main.
2. Write `docs/auto/CHARTER.md` (from `references/charter-template.md`, sentinel
   line removed) and `docs/auto/charter-interview.md` (provenance format in
   formats.md).
3. Initialize state.md with `status: READY` — the ONE state edit charter mode
   may make (this is what lets a later run session start; it exists to prevent
   the resume deadlock).
4. Commit and push the coordination branch.
5. Close with next steps: run `preflight` now (recommended — same session is
   fine), then `launch`.

If the human stops mid-interview: write no charter; save the partial transcript
with the PARTIAL header; resuming restarts at the last confirmed section.

## Rails

- Never fabricate, infer, or self-answer a decision question — silence in the
  human's answers stays silent.
- Never start the run, create Routines, or modify anything outside
  `docs/auto/` on the coordination branch.
- Recon is read-only except the baseline test run; nothing with external side
  effects, ever.
