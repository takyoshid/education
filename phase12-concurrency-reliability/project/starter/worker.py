from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable


class FailureKind(Enum):
    TRANSIENT = "transient"
    PERMANENT = "permanent"


class ProcessingError(RuntimeError):
    def __init__(self, kind: FailureKind, message: str):
        super().__init__(message)
        self.kind = kind


@dataclass(frozen=True)
class Message:
    message_id: str
    payload: str


class ReliableWorker:
    def __init__(self, handler: Callable[[Message], None], max_attempts: int = 3) -> None:
        self.handler = handler
        self.max_attempts = max_attempts
        self.processed: set[str] = set()
        self.dead_letters: list[Message] = []
        self.attempts: dict[str, int] = {}
        self.accepting = True

    def process(self, message: Message) -> bool:
        """成功・処理済みはTrue、再配送が必要ならFalseを返す。"""
        raise NotImplementedError

    def shutdown(self) -> None:
        self.accepting = False
