---
name: check-in
description: Report task progress and check for uncommitted/unpushed git changes. Use this whenever the user asks where things stand, what the state of work is, whether work is done, what's left to push, or invokes /checkin. Also use proactively at natural stopping points to confirm everything's saved and pushed.
---

# Check-in

This skill produces a quick status read — first on the current task, then on git.

## What to do

First, tell the user whether you're still actively in the middle of a task or whether we're at a clean stopping point. Be honest about partial completion: if a task is half-done, name what's done and what's left.

If we're at a stopping point, run these two git checks and report what they show:

1. `git status` — surfaces uncommitted changes in the working directory and staging area.
2. `git log @{u}..HEAD --oneline` — surfaces commits that exist locally but haven't been pushed to the remote. If the upstream isn't set, fall back to `git log --branches --not --remotes --oneline`.

Keep the report tight. If both checks come back clean, just say "all caught up — nothing uncommitted, nothing unpushed." Don't pad with file diffs or commentary unless the user asks for them.
