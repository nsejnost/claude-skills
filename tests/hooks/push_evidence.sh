#!/usr/bin/env bash
# Stop hook: persist the scenario event log before the session container dies.
# Only acts on skill-test fixture branches (auto/sktest-*); otherwise exits fast.
# Commits ONLY the evidence file, with a "[skill-test]" message so judges can
# separate harness commits from the behavior under test. Never fails the session.
set -u
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0
[ -f .skill-test-scenario ] || exit 0
branch="$(git branch --show-current 2>/dev/null)" || exit 0
case "$branch" in auto/sktest-*) ;; *) exit 0 ;; esac
scenario="$(cat .skill-test-scenario 2>/dev/null || echo unknown)"
git add .skill-test/events.jsonl 2>/dev/null || true
if ! git diff --cached --quiet 2>/dev/null; then
  git -c user.name="skill-test" -c user.email="skill-test@local" \
    commit -m "[skill-test] evidence ($scenario)" >/dev/null 2>&1 || true
fi
git push origin "HEAD:$branch" >/dev/null 2>&1 || { sleep 3; git push origin "HEAD:$branch" >/dev/null 2>&1 || true; }
exit 0
