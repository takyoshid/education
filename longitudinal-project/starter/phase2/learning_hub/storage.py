from __future__ import annotations

from pathlib import Path

from .models import Session


class JsonSessionRepository:
    SCHEMA_VERSION = 1

    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> list[Session]:
        """存在しないファイルは空として扱い、破損・未知versionは明示的に失敗する。"""
        raise NotImplementedError

    def save(self, sessions: list[Session]) -> None:
        """同じディレクトリに一時保存してからatomicに置換する。"""
        raise NotImplementedError

    def add(self, session: Session) -> None:
        sessions = self.load()
        if any(existing.session_id == session.session_id for existing in sessions):
            raise ValueError(f"duplicate session_id: {session.session_id}")
        self.save([*sessions, session])
