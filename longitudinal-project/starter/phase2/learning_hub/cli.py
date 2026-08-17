from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from .models import Session
from .service import list_sessions
from .storage import JsonSessionRepository


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="learning-hub")
    parser.add_argument("--data", type=Path, default=Path("learning-data.json"))
    subparsers = parser.add_subparsers(dest="command", required=True)
    add = subparsers.add_parser("add")
    add.add_argument("--started-at", required=True)
    add.add_argument("--minutes", required=True, type=int)
    add.add_argument("--topic", required=True)
    add.add_argument("--reflection", required=True)
    add.add_argument("--tag", action="append", default=[])
    listing = subparsers.add_parser("list")
    listing.add_argument("--topic")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repository = JsonSessionRepository(args.data)
    if args.command == "add":
        repository.add(Session(datetime.fromisoformat(args.started_at), args.minutes, args.topic, args.reflection, tuple(args.tag)))
        return 0
    for session in list_sessions(repository, args.topic):
        print(f"{session.started_at.isoformat()}\t{session.minutes}\t{session.topic}\t{session.reflection}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
