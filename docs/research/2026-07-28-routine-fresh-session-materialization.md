# Routine-fired fresh sessions do not materialize — root cause

**Date:** 2026-07-28 · **Status:** Root cause identified (upstream platform bug) ·
**Blocks:** autopilot lane B (fresh-session runner chain), skill-test `run` mode

## Verdict

This is **not a configuration error and not a bug in this repo's skills.** It is a
known, reproduced, still-unfixed defect in the Claude Code **Routines research
preview**: the scheduler dispatches the run and marks the trigger
`ended_reason: run_once_fired`, but the cloud container never finishes
initialising, so no session is ever created and the prompt never executes. The
"fired" signal is written regardless of whether the container came up.

Nothing on the account can fix it. Lane A (self-bind) remains the only working
lane, which is what `autopilot/references/operations.md` already assumes.

## Upstream evidence

The closest match is **anthropics/claude-code#54260**, "Code Routines: cron fires
but cloud containers never execute prompts (silent failure with
`ended_reason: run_once_fired`)" — the same string this account sees in
`list_triggers`. That report includes a minimal reproducible smoke test (a
one-line prompt that `curl`s a webhook; trigger marked complete in 57s, zero
requests received) and explicitly rules out env id, secrets, MCP attachments,
quota, and repo auth. Labels: `area:routines`, `bug`, `has repro`. **Closed as
not planned.**

The same defect surfaces as a family of reports, all `area:routines`,
`platform:web`, mostly closed as duplicates with no fix:

| Issue | Symptom |
| --- | --- |
| [#54260](https://github.com/anthropics/claude-code/issues/54260) | Cron fires, container never executes prompt; `run_once_fired` set anyway |
| [#56480](https://github.com/anthropics/claude-code/issues/56480) | "Failed to start run" on all triggers; Runs list shows "No runs yet" |
| [#53691](https://github.com/anthropics/claude-code/issues/53691) | All scheduled runs stuck at "Setting up a cloud container" since 2026-04-24 |
| [#54444](https://github.com/anthropics/claude-code/issues/54444), [#54685](https://github.com/anthropics/claude-code/issues/54685), [#55140](https://github.com/anthropics/claude-code/issues/55140), [#55736](https://github.com/anthropics/claude-code/issues/55736), [#58240](https://github.com/anthropics/claude-code/issues/58240), [#66243](https://github.com/anthropics/claude-code/issues/66243) | Same container-provisioning hang, various dates |

In the run viewer the four init steps — *Setting up a cloud container → Clone
repository → Run setup script → Start Claude Code* — sit on spinners forever and
never transition to failed. That is why there is no error, no notification, and
no session: the failure is upstream of the agent.

## Account-side evidence (this repo)

Independent of the session-list UI, which is a weak observation channel:

- Fixture branches `auto/sktest-s2` … `s7` carry **only** their 00:59Z fixture
  commit. The Stop hook (`tests/hooks/push_evidence.sh`) pushed nothing.
- The hook demonstrably works: the **manual** s1 run pushed
  `7cbcb75 [skill-test] evidence (s1)` at 02:28Z on `auto/sktest-s1`.
- 12 fresh-session triggers fired 01:02Z–12:49Z across both environments
  (`env_01MxCBpAq4yj9HhLhwpLMQDu` Personal, `env_01NuK6BzdEhMKDiGg6EJsqgP`
  Default), all `run_once_fired`, zero side effects.
- The self-bind control (`trig_015zmYVxxyCxRsRNQ9BRhpg4`, 12:50Z) woke its
  session normally.

### Confirming canary, 2026-07-28 13:23Z

`trig_01MZfFBbJo6RBWd5zq24cKjn` was created specifically to remove the two
confounds in every earlier probe. Earlier probes only asked the session to
*report* the time — output visible nowhere but the session itself, so they could
only ever be judged by the session list. This one wrote an externally observable
side effect, and pushed to **`claude/canary-lane-b`** — a prefix routine sessions
*are* permitted to write, so a branch-push rejection could not mask the result.

Fired 13:23:36Z (36s after schedule), `ended_reason: run_once_fired`. Six minutes
later: no branch, no commit, no session. **Failure 13 of 13**, and the first one
whose negative result cannot be explained by either the branch-push restriction
or a weak observation channel.

Both environments are `kind: anthropic_cloud`, `state: active`, created
2026-05-07 and 2026-02-09 — not new, and Personal is continuously warmed by
interactive sessions, so the cold-start variant in #55140 does not apply.

## Ruled out

- **Trigger misconfiguration.** Five of the failed triggers carry a
  `notifications` block, which the server *rejects* unless
  `create_new_session_on_fire=true`. Its acceptance is server-side proof they
  were stored as genuine fresh-session triggers.
- **Environment choice.** Failed in both environments, with explicit and
  inherited `environment_id`.
- **Repo access.** The same repo clones and pushes fine from interactive
  sessions; #54260 reproduced with a public repo needing no auth.
- **Usage caps.** One-off runs are exempt from the daily routine cap, and the
  self-bind control ran in the same window.
- **UI visibility.** Real for the Desktop surface ([#78229](https://github.com/anthropics/claude-code/issues/78229),
  [#67992](https://github.com/anthropics/claude-code/issues/67992)), but cannot
  explain zero repo side effects here.

## Two further blockers found while investigating

These are independent of materialisation and would bite the moment it is fixed.

### 1. Routine sessions may only push to `claude/`-prefixed branches

Per the Routines docs: *"By default, Claude can only push to branches prefixed
with `claude/`… To remove this restriction for a specific repository, enable
**Allow unrestricted branch pushes**."* That setting exists only on the web
routine form — the `create_trigger` MCP tool has no equivalent parameter.

Everything this project pushes from a fired session is outside that prefix:

- `tests/hooks/push_evidence.sh:17` → `auto/sktest-*`
- autopilot's coordination branch `auto/<arc>` and ticket branches `auto/<arc>/tNN`
- **the canary defined in `autopilot/references/operations.md`**, which appends to
  `docs/auto/session-log.md` on the coordination branch — so the canary itself
  would report failure forever even after the platform is fixed

### 2. MCP-created routines get no connectors unless asked

`create_trigger` returns: *"this trigger stores no MCP connectors, so the sessions
it fires will run without connector (`mcp__<server>__*`) tools."* Every trigger
created for skill-test and every lane-B link omitted the `connectors` parameter,
so those sessions would have had **no GitHub MCP tools** — and web sessions have
no `gh` CLI. Autopilot's entire GitHub operations table (PR create, CI poll,
squash-merge, dashboard issue) would be unavailable.

This one is a straightforward fix: pass `connectors: ["github"]` explicitly.

## Recommendations

1. **Keep lane A as the runner.** The current default in `operations.md` is
   correct. No redesign is needed; this research confirms the choice rather than
   changing it.
2. **Fix the canary before trusting it.** Point it at a `claude/`-prefixed
   branch, otherwise it conflates the platform bug with the branch-push
   restriction and can never pass.
3. **Pass `connectors` explicitly** on any future fresh-session trigger.
4. **Decide the branch-naming question** if lane B is ever revived: either rename
   autopilot's refs to `claude/auto/<arc>…`, or create routines from
   [claude.ai/code/routines](https://claude.ai/code/routines) where
   "Allow unrestricted branch pushes" can be enabled. Note `/schedule` is
   unavailable inside web sessions, so the web form is the only route.
5. **Finish s2–s7 manually** — the suite does not depend on Routines.

## Bug report draft (for `/bug`)

> Fresh-session Routines fire but never materialise a session. 13 one-shot
> triggers created via the claude-code-remote MCP `create_trigger`
> (`create_new_session_on_fire: true`) between 2026-07-28 01:00Z and 13:23Z all
> reached `ended_reason: run_once_fired` within ~60s of schedule, across two
> `anthropic_cloud` environments (`env_01MxCBpAq4yj9HhLhwpLMQDu`,
> `env_01NuK6BzdEhMKDiGg6EJsqgP`). No session appeared in the session list and
> no run produced any side effect — verified repo-side: seven sessions were
> instructed to push evidence commits and none did, while the identical work run
> manually from an interactive session pushed correctly. A self-bind `send_later`
> trigger in the same window woke its session normally, so scheduling and
> delivery work; only new-session creation fails. Trigger ids:
> trig_01PWuvNejDMir7fhiy7kJsW5, trig_01UJhW4VCqa5mvJef5nEYEDP,
> trig_01LkEm72Gq8vxkAWhKrW981X, trig_01MKisnS1snuxQPApnRXpj1S,
> trig_0112iFjknwjuR5AMzvWG4AcE, trig_01FHY7Diqb5xjfx298yi37Xv,
> trig_0133Bty25KGfTdUDYFqWjVBL, trig_01TPbCC3pKtJdTXX8sPzsBdk,
> trig_016A49PxE3rPdPC1wCpqyTKW, trig_01Hj2FMRjhNpZNDHCoMaYkXZ,
> trig_01JnvbnuKXLi3xPcL9qYka7p, trig_017uxW6cBAnxNEvjdRt12RMx,
> trig_01MZfFBbJo6RBWd5zq24cKjn. Appears to be the defect in
> anthropics/claude-code#54260, which was closed as not planned.
