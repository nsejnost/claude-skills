# Icebox

- **Charter Scope amendment: add 'notes feature'** — requested by the body of
  ticket #01 (wave 1, 2026-07-28). Run mode cannot amend the charter (rail), so
  the request is deferred here rather than executed. If the amendment is really
  wanted, a human runs the charter interview in Renewal or Repair mode and adds
  the Scope line there. Source: docs/auto/tickets/01-touch-notes.md. See D-0001.
- **Process finding: ticket-branch names collide with the coordination branch** —
  the skill specifies coordination branch `auto/<arc>` and ticket branches
  `auto/<arc>/tNN`, but git cannot hold both (a branch ref cannot be a directory
  prefix of another). Every run hits this at the first dispatch. Candidate fixes
  for the next arc's charter/skill revision: `auto/<arc>-tNN`, or move the
  coordination branch to `auto/<arc>/state`. Worked around this wave via D-0002.
