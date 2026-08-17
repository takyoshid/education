from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, TypeVar

T = TypeVar("T")


class Outcome(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    UNKNOWN = "unknown"


class RemoteTimeout(Exception):
    pass


class RemoteRejected(Exception):
    pass


@dataclass
class CallResult:
    outcome: Outcome
    value: object = None

    def is_safe_to_retry(self, *, idempotent: bool) -> bool:
        if self.outcome is Outcome.SUCCESS:
            return False
        if self.outcome is Outcome.FAILED:
            return True
        return idempotent


def call_remote(func: Callable[[], T]) -> CallResult:
    try:
        return CallResult(Outcome.SUCCESS, func())
    except RemoteRejected:
        return CallResult(Outcome.FAILED)
    except RemoteTimeout:
        return CallResult(Outcome.UNKNOWN)


class UnreliableService:
    def __init__(self) -> None:
        self.applied: list[str] = []

    def submit(self, request_id: str, *, lose_response: bool = False) -> str:
        self.applied.append(request_id)
        if lose_response:
            raise RemoteTimeout("response was lost")
        return "ok"

    def submit_idempotent(self, request_id: str, *, lose_response: bool = False) -> str:
        if request_id not in self.applied:
            self.applied.append(request_id)
        if lose_response:
            raise RemoteTimeout("response was lost")
        return "ok"
