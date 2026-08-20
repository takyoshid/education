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
        if max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        self.handler = handler
        self.max_attempts = max_attempts
        self.processed: set[str] = set()
        self.dead_letters: list[Message] = []
        self.attempts: dict[str, int] = {}
        self.accepting = True

    def process(self, message: Message) -> bool:
        if not self.accepting:
            raise RuntimeError("worker is shutting down")
        if message.message_id in self.processed:
            return True

        attempt = self.attempts.get(message.message_id, 0) + 1
        self.attempts[message.message_id] = attempt
        try:
            self.handler(message)
        except ProcessingError as exc:
            if exc.kind is FailureKind.PERMANENT or attempt >= self.max_attempts:
                self.dead_letters.append(message)
                self.processed.add(message.message_id)
                return True
            return False

        self.processed.add(message.message_id)
        return True

    def shutdown(self) -> None:
        self.accepting = False
