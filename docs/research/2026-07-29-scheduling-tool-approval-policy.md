# Scheduling-tool approval policy on Claude Code web — experiment closed

Date: 2026-07-29 · Surfaces: Claude Code web (fresh sessions on
nsejnost/tracklist-sandbox, environment "Personal") · Outcome: **per-call
approval for the claude-code-remote scheduling tools is server-side policy;
no client-side configuration can pre-approve them.**

## Question

Can `send_later` / `create_trigger` / `delete_trigger` be pre-approved so an
autopilot chain wake can re-arm with no human present — collapsing unattended
cadence from the hourly babysitter floor to ~3-minute chain links?

## Experiment — three rounds, all provenance-verified

Each round: config written → fresh session (settings load at session start) →
container verified via `~/.claude/skills-provenance.txt` → the probe's first
`send_later` observed.

| Round | Config | Where | Verified by | Result |
| --- | --- | --- | --- | --- |
| 1 | `permissions.allow` rules, both spellings (`mcp__claude-code-remote*`, `mcp__Claude_Code_Remote*`), server-wide + per-tool | repo `.claude/settings.json` (committed) | file present on main (e135edb) | **prompted** |
| 2 | same 12 rules | `~/.claude/settings.json` via setup script v18 | `setup v18 … settings allowlist: applied` | **prompted** |
| 3 | rules + `permissions.defaultMode: "bypassPermissions"` | `~/.claude/settings.json` via setup script v19 | v19 provenance incl. defaultMode | **prompted** |

Rule naming was confirmed correct by observation (the probe session reported
the verbatim tool id `mcp__Claude_Code_Remote__send_later`; MCP tool names
cannot contain spaces, so no third spelling exists). Round 3's probe went one
step further than provenance: it `cat`-verified `~/.claude/settings.json`
in-container — `defaultMode: "bypassPermissions"` and all 12 rules present
exactly as written — immediately before the gate denied the call ("Denied by
user" after a human Deny; nothing scheduled). Config delivery is ruled out as
a variable; the gate itself is the mechanism.

## Root cause (documented)

code.claude.com/docs/en/mcp, "Require approval for a specific tool": an MCP
server may set `_meta["anthropic/requiresUserInteraction"]: true` on a tool;
then Claude Code

> "shows that tool's permission prompt on every call, even in `acceptEdits`,
> `auto`, and `bypassPermissions` permission modes, and doesn't offer a
> 'don't ask again' option for it. Allow rules that match the tool don't skip
> the prompt either. In `dontAsk` mode, which never prompts, Claude Code
> denies the call instead."

Organization connector controls set to `ask` produce identical behavior
(docs/en/mcp, "Organization controls on connector tools"). Both mechanisms
are server/platform-side. This matches every observation: the missing
always-allow option, ignored allow rules at two scopes, ignored
`bypassPermissions` — and why GitHub MCP tools ran unattended all night
(different server, unflagged).

## What WOULD work

1. **Agent SDK harness**: the SDK's `canUseTool` callback "does receive these
   calls and can approve them" (docs, same section) — requires building and
   hosting an app with an API key; out of scope for the subscription-only,
   web-only constraint this project operates under.
2. **Upstream change**: an account-owner-level override for self-scheduling
   tools, or unflagging `send_later` for self-bind wakes. Feature-ask
   territory.

## Implications for autopilot

The dual-lane doctrine is the permanent web architecture, not a workaround:
the chain is opportunistic (minutes-cadence only while a human taps
approvals), the human-created hourly babysitter is the guaranteed unattended
floor (~1 work unit/hour). Recorded in
`autopilot/references/operations.md` ("Approval reality"). The experiment's
settings changes were reverted (setup script v20); the flag makes allow rules
permanently inert for these tools, so none were kept.
