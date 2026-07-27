# CHARTER — results-export  (worked example)

<!-- A filled, realistic charter for a fictional TypeScript web app ("tracklist",
     a Vite + React + vitest repo with a results table page). Offered to the
     human as pre-reading at interview start. Notice throughout: outcomes not
     implementations, commands not vibes, blunt Scope-Out, rules not answers. -->

## Destination
Users of the results table can take their data with them: filtered, sorted
results leave the app as files they can open in a spreadsheet, without the
export ever blocking the UI or changing what the table itself does today.

## Done-when (mechanically checkable — this defines termination)
- [ ] `npx vitest run src/export/` → passes with ≥ 12 assertions
- [ ] `npx vitest run` → all green, total test count ≥ 231 (baseline 214 + new)
- [ ] `npm run typecheck` → exit 0
- [ ] `npm run build` → exit 0; `dist/` total ≤ 940 kB (baseline 897 kB + 43)
- [ ] `node scripts/smoke-export.mjs` → prints `csv:ok xlsx:ok` (script created
      by the arc; exports a 10k-row fixture through the real code path)

## Priorities (strict ranking)
1. Zero regressions to the existing table (mergeability)
2. Faithfulness to existing conventions
3. Feature completeness (both formats)
4. Polish

## Scope
**In:** CSV export of the current filtered+sorted view; XLSX export of the same;
an export button in the table toolbar; progress indication for large exports;
respecting the user's visible-columns selection.
**Out (explicit):** PDF export; scheduled/emailed exports; export templates or
column re-mapping UI; server-side export endpoints; analytics/telemetry of any
kind; i18n beyond existing en-US strings; any change to filtering or sorting
behavior itself; upgrading React or Vite.

## No-touch zones
- `src/analytics-shim/**` (vendored, fragile)
- `src/table/sorting.ts` (under active human revision — issue #88)
- `.github/workflows/release.yml`

## Silence-defaults
Default order: existing convention → smallest reversible → no new dependency →
Priorities. Arc-specific:
- New UI state (e.g. "last export format") → the existing `prefs` store,
  versioned key, per-table not global
- Visual questions → match the toolbar's existing button/spinner patterns;
  never invent a palette or spacing
- User-facing strings → sentence case, tone of existing toolbar tooltips
- File naming → `<table-name>-<yyyy-mm-dd>.<ext>`; when in doubt, mirror what
  the browser's own save dialog would default to

## Stall policy
- Ticket blocked after max attempts: descope-to-icebox
- Unresolvable decision conflict: halt
- Done-when unmet after replan budget: halt
- CI red that reproduces on main: note-and-continue

## Budgets
- max_sessions: 40
- max_parallel: 2
- max_attempts_per_ticket: 3
- max_review_cycles: 2
- max_griller_questions: 7
- replans: 1
- ci_wait_minutes: 15
- arch_checkpoint_every: 5
- max_session_minutes: 90
- max_hours: 12
- pause_after_spec: true          # first arc with autopilot — calibration ritual
- mutation_check: false

## Merge & CI policy
- target_branch: main
- delivery: per-ticket PRs, squash-merged automatically on green
- required repo settings: confirmed at preflight (squash on, no required reviews)
- ci: `.github/workflows/ci.yml` (vitest + typecheck + build) must pass per PR

## Quality invariants (ratchets)
- CI green on every merge — commands: `npx vitest run`, `npm run typecheck`, `npm run build`
- Test count never decreases; xfail/skip never increases (baseline: tests=214 xfail=0 skip=3)
- Bundle: `npm run build` then `node scripts/bundle-size.mjs` ≤ 940 kB

## Tech constraints
TypeScript strict; React function components only; state via the existing
zustand stores. New runtime dependencies require a Type 1 ADR — and for XLSX
specifically: prefer a zero-dependency writer if a prototype shows it's feasible
under the bundle ratchet; otherwise the ADR must compare at least two libraries
on size, license (MIT/Apache only), and maintenance.

## Glossary
- **view** — the rows currently visible after filters and sort, in order
- **export** — writing the view (visible columns only) to a client-side file;
  never a server round-trip
- **large export** — > 5,000 rows; the threshold where progress UI must appear
