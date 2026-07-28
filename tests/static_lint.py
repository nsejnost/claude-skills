#!/usr/bin/env python3
"""Static, zero-model validation of the autopilot skill (and harness wiring).

Checks structure only — no Claude involved, safe to run on every push:
frontmatter well-formed, referenced files exist, status vocabulary consistent
across SKILL.md and formats.md, budget keys consistent with the charter
template, sentinel present in the template, hooks wired.
Exit nonzero with a findings list on any failure.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FINDINGS = []

def fail(msg):
    FINDINGS.append(msg)

def frontmatter(path: Path) -> dict:
    text = path.read_text()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail(f"{path}: missing frontmatter")
        return {}
    fm = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            fm[k.strip()] = v.strip()
    return fm

def main() -> int:
    ap = ROOT / "autopilot"
    skill = ap / "SKILL.md"
    if not skill.exists():
        fail("autopilot/SKILL.md missing")
        print("\n".join(FINDINGS)); return 1
    text = skill.read_text()

    fm = frontmatter(skill)
    if fm.get("name") != "autopilot":
        fail(f"frontmatter name is {fm.get('name')!r}, expected 'autopilot'")
    if not fm.get("description") or len(fm.get("description", "")) < 100:
        fail("frontmatter description missing or suspiciously short")

    # every references/<file> mentioned anywhere in the skill must exist, and vice versa
    mentioned = set(re.findall(r"references/([a-z0-9-]+\.(?:md|sh|py))", text))
    on_disk = {p.name for p in (ap / "references").glob("*")}
    for f in mentioned - on_disk:
        fail(f"SKILL.md mentions references/{f} which does not exist")
    for f in on_disk - mentioned:
        fail(f"references/{f} exists but SKILL.md never mentions it")

    # status vocabulary must agree between SKILL.md and formats.md
    statuses = ["READY", "RUNNING", "PAUSED-SPEC-REVIEW", "DONE",
                "HALTED-AWAITING-CHARTER", "HALTED-BY-USER"]
    formats = (ap / "references" / "formats.md").read_text()
    for s in statuses:
        if s not in text:
            fail(f"status {s} absent from SKILL.md")
        if s not in formats:
            fail(f"status {s} absent from references/formats.md")

    # budget keys named in SKILL.md defaults must appear in the charter template
    template = (ap / "references" / "charter-template.md").read_text()
    for key in ["max_sessions", "max_parallel", "max_attempts_per_ticket",
                "max_review_cycles", "max_griller_questions", "replans",
                "ci_wait_minutes", "arch_checkpoint_every", "max_session_minutes",
                "pause_after_spec"]:
        if key not in text:
            fail(f"budget key {key} absent from SKILL.md")
        if key not in template:
            fail(f"budget key {key} absent from charter-template.md")

    if "STATUS: TEMPLATE" not in template:
        fail("charter-template.md is missing its sentinel line")
    example = (ap / "references" / "example-charter.md").read_text()
    if "STATUS: TEMPLATE" in example:
        fail("example-charter.md must NOT contain the sentinel line")

    # harness wiring
    settings = ROOT / ".claude" / "settings.json"
    if not settings.exists() or "log_tool_use.py" not in settings.read_text():
        fail(".claude/settings.json missing or not wired to tests/hooks/log_tool_use.py")
    for p in ["tests/hooks/log_tool_use.py", "tests/hooks/push_evidence.sh",
              "tests/fixtures/build_fixture.py", "tests/judges/judge.py"]:
        if not (ROOT / p).exists():
            fail(f"harness file missing: {p}")
    st = ROOT / "skill-test" / "SKILL.md"
    if not st.exists() or frontmatter(st).get("name") != "skill-test":
        fail("skill-test/SKILL.md missing or misnamed")

    if FINDINGS:
        print(f"static lint: {len(FINDINGS)} finding(s)")
        for f in FINDINGS:
            print(f"- {f}")
        return 1
    print("static lint: clean")
    return 0

if __name__ == "__main__":
    sys.exit(main())
