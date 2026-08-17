from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ReadMode(Enum):
    STRONG = "strong"
    CAUSAL = "causal"
    EVENTUAL = "eventual"


@dataclass(frozen=True)
class Write:
    key: str
    value: str
    position: int
    depends_on: int | None = None


@dataclass
class Replica:
    name: str
    applied: set[int] = field(default_factory=set)
    data: dict[str, str] = field(default_factory=dict)

    def apply(self, write: Write) -> None:
        self.applied.add(write.position)
        self.data[write.key] = write.value

    def has(self, position: int) -> bool:
        return position in self.applied


class Store:
    def __init__(self, replicas: list[str]) -> None:
        if not replicas:
            raise ValueError("replica が空です")
        self.log: list[Write] = []
        self.replicas = [Replica(name) for name in replicas]

    def write(self, key: str, value: str, depends_on: int | None = None) -> int:
        if depends_on is not None and not any(w.position == depends_on for w in self.log):
            raise ValueError("unknown dependency")
        position = len(self.log) + 1
        self.log.append(Write(key, value, position, depends_on))
        return position

    def replicate_to(self, replica_index: int, positions: list[int]) -> None:
        replica = self.replicas[replica_index]
        by_position = {write.position: write for write in self.log}
        for position in positions:
            if position not in by_position:
                raise ValueError("unknown position")
            replica.apply(by_position[position])

    def _causally_ready(self, replica: Replica, write: Write) -> bool:
        return write.depends_on is None or replica.has(write.depends_on)

    def read(self, key: str, mode: ReadMode, replica_index: int = 0) -> str | None:
        if mode is ReadMode.STRONG:
            return next((w.value for w in reversed(self.log) if w.key == key), None)
        replica = self.replicas[replica_index]
        if mode is ReadMode.EVENTUAL:
            return replica.data.get(key)
        return next(
            (
                w.value
                for w in reversed(self.log)
                if w.key == key and replica.has(w.position) and self._causally_ready(replica, w)
            ),
            None,
        )
