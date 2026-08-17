from __future__ import annotations

import hashlib
from dataclasses import dataclass, field


@dataclass
class WriteRecord:
    key: str
    value: str
    position: int


class Leader:
    def __init__(self) -> None:
        self.log: list[WriteRecord] = []
        self.data: dict[str, str] = {}

    def write(self, key: str, value: str) -> int:
        position = len(self.log) + 1
        self.data[key] = value
        self.log.append(WriteRecord(key, value, position))
        return position

    def read(self, key: str) -> str | None:
        return self.data.get(key)


@dataclass
class Follower:
    leader: Leader
    name: str = "follower"
    applied_position: int = 0
    data: dict[str, str] = field(default_factory=dict)

    def replicate(self, up_to: int | None = None) -> None:
        target = len(self.leader.log) if up_to is None else min(up_to, len(self.leader.log))
        for record in self.leader.log[self.applied_position:target]:
            self.data[record.key] = record.value
            self.applied_position = record.position

    def read(self, key: str) -> str | None:
        return self.data.get(key)

    @property
    def lag(self) -> int:
        return len(self.leader.log) - self.applied_position


class ReadRouter:
    def __init__(self, leader: Leader, followers: list[Follower]) -> None:
        if not followers:
            raise ValueError("follower が空です")
        self.leader = leader
        self.followers = followers
        self._last_write: dict[str, int] = {}

    def note_write(self, user_id: str, position: int) -> None:
        self._last_write[user_id] = max(position, self._last_write.get(user_id, 0))

    def read_naive(self, key: str, follower_index: int = 0) -> str | None:
        return self.followers[follower_index].read(key)

    def read_your_writes(self, user_id: str, key: str) -> str | None:
        required = self._last_write.get(user_id, 0)
        for follower in self.followers:
            if follower.applied_position >= required:
                return follower.read(key)
        return self.leader.read(key)

    def read_monotonic(self, user_id: str, key: str) -> str | None:
        digest = hashlib.sha256(user_id.encode("utf-8")).digest()
        index = int.from_bytes(digest[:8], "big") % len(self.followers)
        return self.followers[index].read(key)
