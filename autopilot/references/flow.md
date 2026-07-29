# Control flow — the run's state machine

A state-machine map of the autopilot run, derived **only** from this folder's
files (SKILL.md **Version 1.0**, state `schema: 1`). State names are the exact
vocabulary the run persists: `state.md`'s `status:` and `phase:` values, and the
ticket files' `status:` values (see `references/formats.md`). Guards quote or
closely paraphrase the skill text; the traceability table below maps every state
and edge to its source. Line numbers refer to the files at the repo revision
this document was authored against (`23384e3`). This is a map, not a normative
source — where it and SKILL.md disagree, SKILL.md wins.

States are the configurations a run can be in **between** sessions. Composite
nesting mirrors loop nesting: the session chain (RUNNING) contains the wave loop
(BUILD), which contains the per-ticket cycles. Terminal styling: green = success,
red = halted (human needed), amber = paused (human re-arms).

```mermaid
stateDiagram-v2
    direction TB

    classDef success fill:#1a7f37,color:#ffffff,stroke:#1a7f37,stroke-width:2px
    classDef halt fill:#cf222e,color:#ffffff,stroke:#cf222e,stroke-width:2px
    classDef pause fill:#9a6700,color:#ffffff,stroke:#9a6700,stroke-width:2px

    state "READY" as READY
    state "PAUSED-SPEC-REVIEW" as PAUSED_SPEC_REVIEW
    state "DONE" as DONE
    state "HALTED" as HALTED
    state "HALTED-AWAITING-CHARTER" as HALTED_AWAITING_CHARTER
    state "HALTED-BY-USER" as HALTED_BY_USER

    [*] --> READY : charter mode (human) — interview writes CHARTER.md, confirmed full read-back sets status READY (its one state edit)
    READY --> RUNNING : launch (human) — dashboard issue, scheduling canary, arm runner lane, set status RUNNING

    state "RUNNING" as RUNNING {
        [*] --> VALIDATE
        VALIDATE --> MAP : gate PASS [charter valid → record baselines, advance to MAP]

        MAP --> MAP : gate FAIL, loop phase back with reason recorded [same-gate consecutive failures < 2]
        MAP --> DECIDE : gate PASS [every Scope-In item → a node or a cited icebox entry, edges form a DAG]

        DECIDE --> DECIDE : work decision tickets off the frontier, one per session — Griller-Decider exchanges [≤ max_griller_questions = 7 per ticket] [map not yet closed]
        DECIDE --> SPEC : [map closed — every node closed]

        SPEC --> SPEC : gate FAIL, loop phase back with reason recorded [same-gate consecutive failures < 2]
        SPEC --> TICKETS : gate PASS, scope FROZEN [line-by-line charter traceability, seams named] [pause_after_spec = false]

        TICKETS --> TICKETS : gate FAIL, loop phase back with reason recorded [same-gate consecutive failures < 2]
        TICKETS --> BUILD : gate PASS [sizes, DAG, independent mergeability]

        state "BUILD (wave loop)" as BUILD {
            state "open" as t_open
            state "claimed" as t_claimed
            state "review" as t_review
            state "ci-pending" as t_ci_pending
            state "merged" as t_merged
            state "blocked" as t_blocked
            state "split" as t_split
            state "icebox" as t_icebox

            [*] --> t_open
            t_open --> t_claimed : wave dispatch to isolated worktree [≤ max_parallel = 3, prefer disjoint Touches, overlapping frontier → smaller wave down to 1]
            t_claimed --> t_review : worker returns — TDD red→green at pre-agreed seams only
            t_claimed --> t_split : TOO_BIG tripwire [clean split consumes an attempt, split generations ≤ 2]
            t_claimed --> t_blocked : [TOO_BIG past max 2 split generations] or [Type 1 mid-build fork — blocks the ticket, spawns a decision ticket]
            t_split --> t_open : sub-tickets join the map [fresh budgets]
            t_review --> t_review : findings → fixer pass → re-review [fix rounds ≤ max_review_cycles = 2, spec-faithfulness findings never waivable]
            t_review --> t_merged : INTEGRATE serially — rebase onto origin/main, full local gate, PR, squash-merge [checks green within ci_wait_minutes = 20]
            t_review --> t_ci_pending : CI wait timeout [mark ci-pending, move on — dependents stay blocked until the merge actually lands]
            t_review --> t_open : attempt failed [rebase conflict → retry solo next wave] or [CI red again after one fix push, ≤ flake_reruns = 1] [attempts < 3]
            t_review --> t_blocked : [attempts 3/3 exhausted → blocked + charter stall policy]
            t_ci_pending --> t_merged : Reconcile [PR merged meanwhile → close ticket]
            t_ci_pending --> t_open : Reconcile [still stuck → attempt logic]
            t_blocked --> t_open : blocker resolved → refresh the frontier (paraphrase — see table)
            t_blocked --> t_icebox : charter stall policy [descope-to-icebox]
            t_merged --> t_open : architecture checkpoint [every arch_checkpoint_every = 5 merged tickets — Decider triage, at most 1 bounded-refactor ticket, default deferred to icebox]
        }

        BUILD --> BUILD : next wave — Reconcile, schedule wave, dispatch parallel workers, review, integrate serially [frontier not empty]
        BUILD --> MAP : replan scoped to the gap [frontier empty and Done-when unmet and replans used < replans = 1]
        BUILD --> FINISH : [frontier empty and Done-when met] (inferred — see table)

        FINISH --> FINISH : gate FAIL, loop phase back with reason recorded [same-gate consecutive failures < 2]
    }

    RUNNING --> RUNNING : session chain — one unit per session, push state, schedule exactly one next wake [just-pushed status = RUNNING], crashed chain resumed by the hourly babysitter

    VALIDATE --> HALTED_AWAITING_CHARTER : [missing or invalid charter in a headless session] — notification fires
    SPEC --> PAUSED_SPEC_REVIEW : after gate PASS [charter set pause_after_spec = true] — notification fires
    FINISH --> DONE : DONE gate [every charter Done-when line passes against main, archive PR opened, Routines disabled] — notification fires
    BUILD --> HALTED : [frontier empty after the replan budget is spent]

    RUNNING --> HALTED : [two consecutive failures of the same gate]
    RUNNING --> HALTED : stall path [sessions_used at max_sessions = 60 cap, or max_hours exceeded, or no_progress_sessions = 3 resumes without a state change]
    RUNNING --> HALTED : [decision question unanswerable safely, or unknown state schema — HALT, never guess]
    RUNNING --> HALTED_BY_USER : stop mode (human) — finish current write-back, delete Routines, update dashboard [honored immediately at any point]

    PAUSED_SPEC_REVIEW --> RUNNING : human reads spec.md, launch re-arms [resume at the persisted phase]
    HALTED --> RUNNING : Repair interview answers halt-report questions, then launch re-arms (human) [resume at the persisted phase]
    HALTED_BY_USER --> RUNNING : /autopilot offers Repair interview, then launch (human)
    HALTED_AWAITING_CHARTER --> READY : human runs the charter interview from any device [sets status READY]

    DONE --> [*]

    note right of RUNNING
        Session and memory model — the ONLY persisted state is docs/auto/ on the
        coordination branch auto/arc-slug, pushed at session end, fetched at session
        start (origin is the program). state.md is the program counter — status,
        phase, wave, claims, budgets, trigger ids. Sessions are ephemeral fresh
        clones doing ONE unit of work each. Resume paths re-enter at the persisted
        phase, not at VALIDATE.
    end note

    note right of HALTED
        Halting well is a success state. Never widen scope or fabricate preferences
        to avoid halting — halt-report.md carries the exact questions a human must
        answer, and /autopilot offers Repair → launch. Every loop is bounded, every
        bound is enforced in state.md. Exhausting any budget takes the stall path,
        never silent continuation.
    end note

    class DONE success
    class HALTED halt
    class HALTED_AWAITING_CHARTER halt
    class HALTED_BY_USER halt
    class PAUSED_SPEC_REVIEW pause
```

## What is deliberately NOT a state

- **preflight** — proves the environment but writes no `status:`; it only gates
  `launch` socially ("Offer `launch` on full pass", operations.md L183).
- **claims** — the `claim:` field is an intra-session mutex (rejected push →
  exit quietly; stale after `max_session_minutes` → adoptable), not a phase
  (SKILL.md L75-77).
- **Griller / Decider / red-team / Auditor** — subagent roles inside one
  session; their loop bound (`max_griller_questions`) appears on the DECIDE
  self-loop (SKILL.md L191-224).
- **Lane A / lane B scheduling, canary, babysitter** — runner machinery that
  keeps the chain alive; it never changes `status:` except via the guards shown
  (operations.md L35-124).

## Traceability

Sources: `S` = SKILL.md, `F` = references/formats.md, `O` =
references/operations.md, `P` = references/playbooks.md, `I` =
references/interview-guide.md, `C` = references/charter-template.md.
Flags: **⚑ inferred/paraphrase** (not verbatim in the skill text — kept because
the complement or mechanism is explicit; see footnotes), **✱ resume synthesis**
(edge is explicit; the "resume at persisted phase" detail is synthesized from
state.md being the program counter, S L60).

### States

| State | Vocabulary source | Defined at |
| --- | --- | --- |
| `READY` | `status:` enum, F L14 | S §Modes L32 (charter's one state edit); I §Output L194-196 |
| `RUNNING` | `status:` enum, F L14 | S §Modes L34, L36; F L36-38 (run mode only moves RUNNING → RUNNING, PAUSED-SPEC-REVIEW, DONE, HALTED\*) |
| `PAUSED-SPEC-REVIEW` | `status:` enum, F L14 | S §Phase machine L138-140 |
| `DONE` | `status:` enum, F L14 | S §Phase machine (FINISH) L186-189 |
| `HALTED` | `status:` enum, F L15 | S L20-22 ("Halting well is a success state"), L111-112 |
| `HALTED-AWAITING-CHARTER` | `status:` enum, F L15 | S §Phase machine (VALIDATE) L116-117 |
| `HALTED-BY-USER` | `status:` enum, F L15 | S §Modes L37; O §Stop L219 |
| `VALIDATE` `MAP` `DECIDE` `SPEC` `TICKETS` `BUILD` `FINISH` | `phase:` enum, F L16 | S §Phase machine L114, L121, L130, L133, L143, L149, L186 |
| `open` `claimed` `review` `ci-pending` `merged` `blocked` `split` `icebox` | ticket `status:` enum, F L45 | F §Ticket file L40-66 |

### Edges and guards

| Edge | Guard (as drawn) | Source | Basis |
| --- | --- | --- | --- |
| `[*] → READY` | confirmed full read-back | S L32; I L188-199 | "on confirmed read-back sets `status: READY` (its one state edit)" |
| `READY → RUNNING` | launch (human) | S L34; O §Launch L185-213 | "Set `status: RUNNING` (from READY / a repaired HALT / PAUSED-SPEC-REVIEW)" |
| `RUNNING → RUNNING` (session chain) | [just-pushed status = RUNNING], one wake; babysitter resumes crashes | S L102-105, L240-245; O §Guards L111-113 | "schedule only when `status: RUNNING`, only **after** state is successfully pushed, and only **one** next session" |
| `VALIDATE → MAP` | gate PASS | S L118-119 | "Valid → record baselines, advance to MAP"; checklist F L93-101 |
| `VALIDATE → HALTED-AWAITING-CHARTER` | [missing/invalid charter, headless] | S L115-118 | "Missing/invalid charter in a headless session → `HALTED-AWAITING-CHARTER` + notification" |
| `MAP → MAP`, `SPEC → SPEC`, `TICKETS → TICKETS`, `FINISH → FINISH` | [same-gate consecutive failures < 2] | S L110-112 | "A failed gate loops the phase back with the reason recorded"; default `consecutive_same_gate_failures 2` S L236 |
| `MAP → DECIDE` | [Scope-In → node or cited icebox entry, edges form a DAG] | S L126-128 | gate quoted verbatim; checklist F L103-107 |
| `DECIDE → DECIDE` | [map not yet closed], [≤ max_griller_questions = 7] | S L129-131, L203-204; P §5 L129-131 | "one per session"; "loop ≤ `max_griller_questions`" |
| `DECIDE → SPEC` | [map closed — every node closed] | S L131-132 | "Close the map when every node is closed." |
| `SPEC → TICKETS` | [traceability, seams named] [pause_after_spec = false] | S L135-138; C L62 | "line-by-line charter traceability …, seams named. **After this gate scope is FROZEN**" |
| `SPEC → PAUSED-SPEC-REVIEW` | [pause_after_spec = true] | S L138-140 | "If the charter set `pause_after_spec: true` → `PAUSED-SPEC-REVIEW` + notification" |
| `PAUSED-SPEC-REVIEW → RUNNING` ✱ | human reads spec.md → launch | S L140-141; O L211-215 | "the human reads spec.md … and re-arms via `launch`" |
| `TICKETS → BUILD` | [sizes, DAG, independent mergeability] | S L146-147 | gate quoted verbatim; checklist F L116-120 |
| `BUILD → BUILD` (wave loop) | [frontier not empty] | S L149-174; exit complement L183-184 | wave steps 1-5 ("Reconcile … Schedule the wave … Dispatch … Review … Integrate serially") |
| `open → claimed` | [≤ max_parallel = 3, disjoint Touches, down to 1] | S L152-158 | "pick up to `max_parallel` frontier tickets … Overlapping frontier → smaller wave, down to 1" |
| `claimed → review` | worker returns | S L156-164; P §3-4 | worker TDD loop, then "Review each returned ticket" |
| `review → review` | [fix rounds ≤ max_review_cycles = 2] | S L164-165; P §4 L120-122 | "≤ `max_review_cycles` fix rounds"; "spec-faithfulness findings are unwaivable" |
| `review → merged` | [checks green ≤ ci_wait_minutes = 20] | S L166-170; F §INTEGRATE L122-131 | "rebase … full local gate … push branch → open PR … wait on checks ≤ `ci_wait_minutes` → squash-merge" |
| `review → ci-pending` | CI timeout | S L173-174 | "Timeout → mark `ci-pending`, move on; dependents stay blocked until the merge actually lands" |
| `review → open` | [rebase conflict → solo next wave] / [CI red after one fix push, ≤ flake_reruns = 1] [attempts < 3] | S L171-173, L236; O L144 | "Rebase conflict → drop from this wave, retry solo next wave (counts an attempt). CI red → diagnose from logs, one fix push; red again → attempt failed" |
| `review → blocked` | [attempts 3/3] | S L175 | "Attempts: 3 per ticket, then `blocked` + the charter's stall policy" |
| `claimed → split` | [split consumes an attempt, generations ≤ 2] | S L176-177; P §3 L85-89 | "A clean `TOO_BIG` split consumes an attempt; sub-tickets get fresh budgets" |
| `split → open` | [fresh budgets] | S L176-177 | "sub-tickets get fresh budgets" |
| `claimed → blocked` | [past 2 split generations] / [Type 1 fork] | S L177, L218-219; P L82-84 | "max 2 split generations, then blocked"; "anything Type 1 blocks the ticket and spawns a decision ticket" |
| `ci-pending → merged` | [merged meanwhile] | S L150-152 | "resolve any `ci-pending` PRs (merged meanwhile → close tickets …)" |
| `ci-pending → open` | [still stuck → attempt logic] | S L150-152 | "… still stuck → attempt logic" |
| `blocked → open` ⚑ | blocker resolved → refresh the frontier | S L152, L174; P L82-84 | paraphrase — see footnote 2 |
| `blocked → icebox` | [stall policy descope-to-icebox] | C §Stall policy L45-49; S L175 | "Ticket blocked after max attempts: `descope-to-icebox` \| `leave-blocked`" (leave-blocked = no edge) |
| `merged → open` (checkpoint) | [every arch_checkpoint_every = 5 merged, ≤ 1 bounded refactor] | S L178-181; P §6 L135-159 | "triaged by the Decider into blocking-task / bounded-refactor / icebox — the only lawful ways scope moves"; "at most ONE refactor ticket per checkpoint" |
| `BUILD → MAP` (replan) | [frontier empty and Done-when unmet and replans < 1] | S L183-184, L234 | "Frontier empty but Done-when unmet → one replan pass (back to MAP, scoped to the gap; consumes the replan budget)" |
| `BUILD → HALTED` | [frontier empty after replan budget spent] | S L184 | "Empty after that → HALT." |
| `BUILD → FINISH` ⚑ | [frontier empty and Done-when met] | inferred | see footnote 1 |
| `FINISH → DONE` | [Done-when passes on main, archive PR, Routines disabled] | S L186-189; F §DONE L132-135 | "`status: DONE` (notification fires)" |
| `RUNNING → HALTED` | [two consecutive failures of the same gate] | S L111-112 | quoted verbatim; tracked per gate in `gate_failures:` F L24 — see footnote 3 |
| `RUNNING → HALTED` | [sessions cap / max_hours / no_progress_sessions = 3] | S L229-231, L243-245; O §Guards L114-116 | "exhausting any budget takes the stall path, never silent continuation"; "→ HALT instead of scheduling" |
| `RUNNING → HALTED` | [unanswerable question / unknown schema] | S L222-224; F L5-6; O L126-132 | "If a question cannot be answered safely → HALT"; "a session that reads a schema it doesn't know must HALT, not guess" |
| `RUNNING → HALTED-BY-USER` | stop mode, immediate | S L37, L267-268; O §Stop L217-227 | "at any point, if state says `HALTED-BY-USER`, finish the current write-back and exit" |
| `HALTED → RUNNING` ✱ | Repair → launch (human) | S L34, L39-41; F L193-195; O L211-215 | "Resume: run /autopilot in any session — it will offer the Repair interview, then launch" |
| `HALTED-BY-USER → RUNNING` ✱ | Repair → launch (human) | O L224-226 | "`/autopilot` will offer Repair → launch whenever they want to resume" |
| `HALTED-AWAITING-CHARTER → READY` | charter interview (human) | S L117-118, L32 | "the human runs the charter interview from any device"; charter sets READY |
| `DONE → [*]` | terminal | S L94-96; F L36-38 | "Terminal status (`DONE`, any `HALTED*`, `PAUSED*`)? Report, verify the Routines are disabled, exit" |

**Footnotes**

1. **`BUILD → FINISH` is inferred**, not quoted: SKILL.md L183-184 defines what
   happens when the frontier is empty and Done-when is *unmet* (replan, then
   HALT); no sentence states the complementary transition. FINISH's definition
   (L186-189, "every charter Done-when command against `main`") and the DONE
   gate (F L132-135) confirm FINISH is where a met Done-when is verified, so the
   guard shown is the documented exits' complement.
2. **`blocked → open` is a close paraphrase**: no sentence says a blocked ticket
   re-opens. It is composed from "refresh the frontier" (S L152), "dependents
   stay blocked until the merge actually lands" (S L174 — i.e. they unblock when
   it does), and Type 1 forks blocking a ticket on a spawned decision ticket
   (S L218-219), which must unblock on that ticket's closure for DECIDE/BUILD to
   progress. Attempts-exhausted `blocked` tickets have no documented way back to
   `open` short of the human Repair path.
3. **Gate-failure vs attempt budgets (resolved after authoring)**: this audit
   originally flagged an overlap — state.md tracks `INTEGRATE(#09)=1` in
   `gate_failures:` (F L24) and "two consecutive failures of the same gate →
   HALT" (S L111-112), while attempts are "3 per ticket, then `blocked`"
   (S L175) — leaving unspecified whether two consecutive INTEGRATE failures
   on one ticket halt the run before its third attempt. The spine has since
   pinned it (commit `d0024c4`): the same-gate HALT bounds **phase** gates
   only; an INTEGRATE failure burns that ticket's attempt, and `INTEGRATE(#NN)`
   entries are per-ticket visibility, not HALT inputs. The diagram as drawn
   (`review → open` on attempts, `review → blocked` at 3/3, same-gate HALT on
   the phase self-loops only) matches the pinned reading.

## Loop-bound audit

Every cycle in the diagram carries a documented exit condition — **no
[UNGUARDED] edges were found**. The skill states the invariant outright: "Every
loop is bounded and every bound is enforced in state.md; exhausting any budget
takes the stall path, never silent continuation" (S L229-231). Bounds by loop:
session chain — `max_sessions 60`, `max_hours`, `no_progress_sessions 3`; wave
loop — frontier-empty exits; gate retries — `consecutive_same_gate_failures 2`;
decision grilling — `max_griller_questions 7`; review — `max_review_cycles 2`;
attempts — `max_attempts_per_ticket 3`; splits — `split_generations 2`; CI wait
— `ci_wait_minutes 20`, `flake_reruns 1`; replanning — `replans 1`; checkpoints
— every `arch_checkpoint_every 5` merges, ≤ 1 refactor ticket each (S L232-238;
P §6).
