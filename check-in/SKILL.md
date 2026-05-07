---
name: check-in
description: Report task progress and check for uncommitted, unpushed, and unmerged git changes. Use whenever the user asks where things stand, what the state of work is, whether work is done, what's left to push or merge, or invokes /check-in. Also use proactively at natural stopping points to confirm everything is on the way to main.
---

# Check-in

This skill produces a quick status read — first on the current task, then on git.

## What to do

First, tell the user whether you're still actively in the middle of a task or whether we're at a clean stopping point. Be honest about partial completion: if a task is half-done, name what's done and what's left.

If we're at a stopping point, walk the chain of states this work could be in and report where we are. Each state must clear before the next:

1. **Working tree** — Run `git status`. Surface any uncommitted or unstaged changes.

2. **Unpushed commits** — Run `git log @{u}..HEAD --oneline`. Surface any commits in this working tree that haven't been pushed to the remote. If the upstream isn't set, fall back to `git log --branches --not --remotes --oneline`.

3. **Current branch** — Run `git branch --show-current`. Always report the branch name. If it starts with `claude/`, note it explicitly so the user can find it on GitHub.

4. **PR status** — Run `gh pr list --head "$(git branch --show-current)" --state all --json number,state,title,url`. Report whether a PR exists for this branch, its state (open / merged / closed), and the URL if any. If `gh` isn't available or auth fails, skip this step and note that PR status couldn't be checked.

5. **Merged to main** — Run `git log origin/main..HEAD --oneline` (or `origin/master` if that's the default). Surface commits on this branch not yet on main. If the PR is merged this should be empty; if it's not, this list shows what's still in flight.

Tailor the closing summary to where the chain stopped:

- All checks clean and merged to main: "All caught up — work is merged to main."
- Uncommitted changes present: flag them prominently. In an ephemeral sandbox these will be lost if the task ends, so the user needs to know.
- Pushed to a `claude/*` branch with no PR yet: "Work is pushed to `<branch-name>` but no PR is open. The next task you start will spin up from main and won't see this work until it's merged. Open a PR when ready."
- PR open: "Work is pushed and PR #<n> is open at <url>. Waiting on merge."
- PR merged but the working branch is still ahead of main: rare, usually means a force-push or rebase mismatch — flag it explicitly.

Don't pad with file diffs, commit messages, or commentary unless the user asks. The point of this skill is a fast status read.
