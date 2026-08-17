#!/usr/bin/env python3
"""Run each public test suite against its separate reference implementation."""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Target:
    name: str
    implementation: str
    tests: str
    module: str


TARGETS = (
    Target("phase8/async-timeout", "phase8-concurrency-reliability/exercises/solutions/async-timeout/pipeline.py", "phase8-concurrency-reliability/exercises/async-timeout/tests", "pipeline.py"),
    Target("phase8/bank-transfer", "phase8-concurrency-reliability/exercises/solutions/bank-transfer/bank.py", "phase8-concurrency-reliability/exercises/bank-transfer/tests", "bank.py"),
    Target("phase8/check-then-act", "phase8-concurrency-reliability/exercises/solutions/check-then-act/inventory.py", "phase8-concurrency-reliability/exercises/check-then-act/tests", "inventory.py"),
    Target("phase8/idempotency", "phase8-concurrency-reliability/exercises/solutions/idempotency/orders.py", "phase8-concurrency-reliability/exercises/idempotency/tests", "orders.py"),
    Target("phase8/retry-backoff", "phase8-concurrency-reliability/exercises/solutions/retry-backoff/retry.py", "phase8-concurrency-reliability/exercises/retry-backoff/tests", "retry.py"),
    Target("phase8/worker", "phase8-concurrency-reliability/project/solution/worker.py", "phase8-concurrency-reliability/project/starter/tests", "worker.py"),
    Target("phase11/failure-modes", "phase11-distributed-systems/exercises/solutions/failure-modes/remote.py", "phase11-distributed-systems/exercises/failure-modes/tests", "remote.py"),
    Target("phase11/consistency", "phase11-distributed-systems/exercises/solutions/consistency/modes.py", "phase11-distributed-systems/exercises/consistency/tests", "modes.py"),
    Target("phase11/quorum", "phase11-distributed-systems/exercises/solutions/quorum/cluster.py", "phase11-distributed-systems/exercises/quorum/tests", "cluster.py"),
    Target("phase11/replication-lag", "phase11-distributed-systems/exercises/solutions/replication-lag/store.py", "phase11-distributed-systems/exercises/replication-lag/tests", "store.py"),
    Target("phase11/cache-stampede", "phase11-distributed-systems/exercises/solutions/cache-stampede/cache.py", "phase11-distributed-systems/exercises/cache-stampede/tests", "cache.py"),
    Target("phase11/partitioning", "phase11-distributed-systems/exercises/solutions/partitioning/partitioner.py", "phase11-distributed-systems/exercises/partitioning/tests", "partitioner.py"),
)


def validate(target: Target, work_root: Path) -> tuple[bool, int]:
    work = work_root / target.name.replace("/", "-")
    work.mkdir()
    shutil.copy2(ROOT / target.implementation, work / target.module)
    shutil.copytree(ROOT / target.tests, work / "tests")
    completed = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        cwd=work,
        capture_output=True,
        text=True,
        check=False,
    )
    output = completed.stdout + completed.stderr
    match = re.search(r"Ran (\d+) tests?", output)
    count = int(match.group(1)) if match else 0
    if completed.returncode != 0 or count == 0:
        print(f"FAIL {target.name}\n{output}", file=sys.stderr)
        return False, count
    print(f"OK   {target.name}: {count} public tests passed")
    return True, count


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="curriculum-reference-") as directory:
        results = [validate(target, Path(directory)) for target in TARGETS]
    failed = sum(not success for success, _ in results)
    total = sum(count for _, count in results)
    if failed:
        print(f"\n{failed} reference implementation(s) failed.", file=sys.stderr)
        return 1
    print(f"\nValidated {len(TARGETS)} reference implementations ({total} tests).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
