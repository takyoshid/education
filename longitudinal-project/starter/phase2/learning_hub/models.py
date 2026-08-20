from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass(frozen=True)
class Session:
    started_at: datetime
    minutes: int
    topic: str
    reflection: str
    tags: tuple[str, ...] = ()
    session_id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        """不変条件を検証し、文字列とタグを正規化する。"""
        raise NotImplementedError

    def to_dict(self) -> dict[str, object]:
        raise NotImplementedError

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Session":
        raise NotImplementedError
