from __future__ import annotations

from dataclasses import dataclass, replace


class NotFoundError(LookupError):
    pass


class ConflictError(RuntimeError):
    pass


@dataclass(frozen=True)
class Task:
    task_id: int
    owner_id: str
    title: str
    version: int = 1


class TaskService:
    def __init__(self) -> None:
        self.tasks: dict[int, Task] = {}
        self.idempotency: dict[tuple[str, str], tuple[str, Task]] = {}
        self.next_id = 1

    def create(self, owner_id: str, title: str, idempotency_key: str) -> Task:
        raise NotImplementedError

    def get(self, requester_id: str, task_id: int) -> Task:
        raise NotImplementedError

    def update(self, requester_id: str, task_id: int, title: str, expected_version: int) -> Task:
        raise NotImplementedError

    def list_for(self, requester_id: str, limit: int = 20, after_id: int | None = None) -> list[Task]:
        raise NotImplementedError
