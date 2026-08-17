from __future__ import annotations

import sys
from pathlib import Path

REQUIRED_FILES = ("incident.md", "runbook.md", "postmortem.md")
REQUIRED_INCIDENT_TERMS = ("impact", "timeline", "hypothesis", "evidence", "rollback", "verification")
REQUIRED_RUNBOOK_TERMS = ("detect", "rollback", "verify", "escalate")


def main(root: Path) -> int:
    errors = []
    for name in REQUIRED_FILES:
        if not (root / name).is_file():
            errors.append(f"missing {name}")
    if (root / "incident.md").is_file():
        text = (root / "incident.md").read_text(encoding="utf-8").casefold()
        errors.extend(f"incident.md missing: {term}" for term in REQUIRED_INCIDENT_TERMS if term not in text)
    if (root / "runbook.md").is_file():
        text = (root / "runbook.md").read_text(encoding="utf-8").casefold()
        errors.extend(f"runbook.md missing: {term}" for term in REQUIRED_RUNBOOK_TERMS if term not in text)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Submission structure passed. Human review is still required.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(Path(sys.argv[1] if len(sys.argv) > 1 else "submission")))
