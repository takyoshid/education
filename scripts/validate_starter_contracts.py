#!/usr/bin/env python3
"""Verify that public tests for unfinished starters fail for the intended reason."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
STARTERS = (
    "phase8-concurrency-reliability/exercises/async-timeout",
    "phase8-concurrency-reliability/exercises/bank-transfer",
    "phase8-concurrency-reliability/exercises/check-then-act",
    "phase8-concurrency-reliability/exercises/idempotency",
    "phase8-concurrency-reliability/exercises/retry-backoff",
    "phase8-concurrency-reliability/project/starter",
    "phase11-distributed-systems/exercises/cache-stampede",
    "phase11-distributed-systems/exercises/consistency",
    "phase11-distributed-systems/exercises/failure-modes",
    "phase11-distributed-systems/exercises/partitioning",
    "phase11-distributed-systems/exercises/quorum",
    "phase11-distributed-systems/exercises/replication-lag",
    "phase11-distributed-systems/exercises/time-and-ordering",
    "longitudinal-project/starter/phase2",
)

DISCOVERY_ERRORS = (
    "Failed to import test module",
    "ModuleNotFoundError",
    "ImportError:",
    "SyntaxError:",
    "_FailedTest",
)


def validate(directory: str) -> list[str]:
    path = ROOT / directory
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=path,
        capture_output=True,
        text=True,
        check=False,
    )
    output = completed.stdout + completed.stderr
    errors: list[str] = []

    match = re.search(r"Ran (\d+) tests?", output)
    if match is None or int(match.group(1)) == 0:
        errors.append("no tests were collected")
    if completed.returncode == 0:
        errors.append("tests unexpectedly passed; this starter is meant to be unfinished")
    if "NotImplementedError" not in output:
        errors.append("failure did not reach an intentional NotImplementedError stub")
    for marker in DISCOVERY_ERRORS:
        if marker in output:
            errors.append(f"test discovery failed ({marker})")

    if errors:
        print(f"FAIL {directory}: {'; '.join(errors)}", file=sys.stderr)
    else:
        print(f"OK   {directory}: public tests reached the intentional stubs")
    return errors


def main() -> int:
    failed = [directory for directory in STARTERS if validate(directory)]
    if failed:
        print(f"\nStarter contract validation failed for {len(failed)} target(s).", file=sys.stderr)
        return 1
    print(f"\nValidated {len(STARTERS)} unfinished starter contracts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
