---
name: skill-test
description: Test the autopilot skill's contract on subscription only — no API key. Builds fixture branches, schedules real fresh Claude Code web sessions via one-shot Routines to run seven behavioral scenarios against the skill, captures tool-call evidence via hooks, then judges outcomes deterministically and reports. Use when the user asks to test autopilot, run the skill tests or scenarios, collect skill-test results, clean up test fixtures, or invokes /skill-test. Human-attended; scenario sessions themselves are fired headless by the harness.
---

# Skill-test

Behavioral test harness for the **autopilot** skill, running entirely on the
user's subscription: real fresh web sessions execute scenarios; deterministic
scripts judge them. No API key, no external services. The seven scenarios and
the prompt template live in `references/scenarios.md` — read it before running.

How evidence works: `.claude/settings.json` (on main) registers two hooks that
no-op everywhere except fixture branches — a PreToolUse hook appending every
tool call to `.skill-test/events.jsonl` when a `.skill-test-scenario` marker
exists, and a Stop hook that commits and pushes that log (`[skill-test]`-prefixed
commits) so evidence survives the session container. Judges separate those
harness commits from behavior-under-test commits by that prefix.

## Modes

**`run [sN | all]`** — stage and fire scenarios:

1. `python3 tests/fixtures/build_fixture.py <sN|all>` — builds and force-pushes
   the fixture branch(es) `auto/sktest-*` (and `sktest-s7-target` for s7).
2. **Canary before anything else** — scenario sessions need fresh contexts, so
   only fresh-session Routines can automate them, and that mechanism is known
   to fail silently on some accounts (verified 12/12 "Ran"-but-no-session on
   this skill's home account, 2026-07). Create ONE one-shot fresh-session
   Routine ~2 minutes out whose prompt is: "git fetch origin auto/sktest-s1 &&
   git checkout auto/sktest-s1, append a line '[skill-test] canary <UTC time>'
   to .skill-test/canary.txt, commit with message '[skill-test] canary', push,
   end." Tell the user to reply in ~5 minutes; on their reply, fetch the
   branch and check for the canary commit.
3. **Canary passed** → for each scenario, create a one-shot fresh-session
   Routine with the scenario prompt from `references/scenarios.md`, spaced ~4
   minutes apart, plus one **collector Routine** ~6 minutes after the last
   (push notifications on) whose prompt is: "Read skill-test/SKILL.md in this
   repo and perform its collect mode." Report the timetable, then stop.
   **Canary failed** → guided-manual mode: print the seven ready-to-paste
   scenario prompts (filled from the template) in run order, tell the user to
   paste each into a fresh session and reply here when done; collect then runs
   from any session. Self-bind cannot substitute — it would reuse one
   conversation and break scenario isolation.

**`collect`** — judge and report (run by the collector Routine, or manually):

1. `python3 tests/judges/judge.py all` (or the subset that was run) — fetches
   each fixture branch, gathers facts, runs the deterministic checks, writes
   `tests/reports/<ts>-report.md` and prints it.
2. Publish the report: commit it to branch `skill-test/reports` (create from
   main if absent, via a temp worktree) and push.
3. End with a compact PASS/FAIL summary per scenario plus one line per failing
   check — this final message is what the phone notification carries. Failures
   are findings about the autopilot skill: report them; never edit
   `autopilot/**` from this harness.

**`clean`** — after results are read:

1. Neutralize harness branches: for each of `auto/sktest-s1`..`s7` and
   `sktest-s7-target`, force-push main's sha to the ref
   (`git push -f origin <main-sha>:refs/heads/<branch>`) so it carries zero
   diff. Then attempt real deletion (`git push origin --delete <branch>`) —
   the environment's git proxy may silently ignore deletes; if branches
   survive, tell the user they're zero-diff husks deletable anytime in the
   GitHub app (repo → Branches). Never touch `skill-test/reports` — reports
   are history.
2. Close any PRs the s7 scenario opened against `sktest-s7-target`.
3. Delete any leftover Routines whose names start with "skill-test".

## Rails

- Touch only harness-owned refs: `auto/sktest-*`, `sktest-*`,
  `skill-test/reports`. Never modify `autopilot/**`, `main`, or anything else.
- Name every Routine "skill-test <scenario|collector>" so clean mode can find
  them; never touch Routines not named that way.
- One `run` at a time: if `auto/sktest-*` branches already exist, offer clean
  first.
- Scenario sessions cost subscription usage (~8 short sessions per full run);
  say so when starting a full run.
- A judge PASS on an empty trace is weaker evidence (end-state only) — the
  report flags this; treat "0 trace events" on a scenario that should have
  acted as suspicious, not as green.
