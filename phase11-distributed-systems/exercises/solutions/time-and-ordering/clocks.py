"""模範解答: 因果と競合を、時計を使わずに見分ける。

壁時計は一度も登場しません(last_write_wins を除く。そこは
「壁時計を使うとどうなるか」を見せるための関数なので、あえて使います)。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Ordering(Enum):
    BEFORE = "before"
    AFTER = "after"
    CONCURRENT = "concurrent"
    EQUAL = "equal"


class LamportClock:
    def __init__(self) -> None:
        self.counter = 0

    def tick(self) -> int:
        self.counter += 1
        return self.counter

    def send(self) -> int:
        # 送信もひとつの出来事。tick と同じ扱いでよい。
        return self.tick()

    def receive(self, incoming: int) -> int:
        # max を取るだけでは足りない。受信も出来事なので +1 する。
        # これを忘れると、送信と受信が同じ値になり、
        # 「A → B ならば C(A) < C(B)」が崩れる。
        self.counter = max(self.counter, incoming) + 1
        return self.counter


@dataclass
class VectorClock:
    process_id: str
    counters: dict[str, int] = field(default_factory=dict)

    def tick(self) -> None:
        self.counters[self.process_id] = self.counters.get(self.process_id, 0) + 1

    def merge(self, other: "VectorClock") -> None:
        for process, value in other.counters.items():
            self.counters[process] = max(self.counters.get(process, 0), value)
        # 受信も出来事なので、自分の要素を進める。
        self.tick()

    def compare(self, other: "VectorClock") -> Ordering:
        # 両方に現れるプロセスをすべて見る。
        # 片方にしか無いプロセスは 0 として扱う
        # (「まだ動いていない」と「存在しない」を区別する必要がない)。
        processes = set(self.counters) | set(other.counters)

        self_ahead = False   # 自分が勝っている要素があるか
        other_ahead = False  # 相手が勝っている要素があるか

        for process in processes:
            mine = self.counters.get(process, 0)
            theirs = other.counters.get(process, 0)
            if mine > theirs:
                self_ahead = True
            elif mine < theirs:
                other_ahead = True

        # 両方が勝っている = どちらも相手を知らなかった = 並行。
        if self_ahead and other_ahead:
            return Ordering.CONCURRENT
        if self_ahead:
            return Ordering.AFTER
        if other_ahead:
            return Ordering.BEFORE
        return Ordering.EQUAL

    def copy(self) -> "VectorClock":
        return VectorClock(self.process_id, dict(self.counters))


@dataclass
class Version:
    value: object
    clock: VectorClock


class VersionedRegister:
    def __init__(self) -> None:
        self.versions: list[Version] = []

    def write(self, version: Version) -> None:
        # 新しい版が、既存のどれかより「前」または「同じ」なら、
        # それは古い書き込みなので何もしない。
        for existing in self.versions:
            ordering = version.clock.compare(existing.clock)
            if ordering in (Ordering.BEFORE, Ordering.EQUAL):
                return

        # 新しい版に因果的に上書きされる版は捨てる。
        # 残るのは「並行な版」だけになる。
        survivors = [
            existing
            for existing in self.versions
            if version.clock.compare(existing.clock) is not Ordering.AFTER
        ]
        survivors.append(version)
        self.versions = survivors

    def read(self) -> list[object]:
        return [version.value for version in self.versions]

    @property
    def has_conflict(self) -> bool:
        return len(self.versions) > 1


def last_write_wins(versions: list[Version], wall_clocks: dict[str, int]) -> object:
    # max は同点のとき最初の要素を返すので、
    # 「後ろを優先する」ために逆順で走査する。
    best = None
    best_timestamp = None
    for version in reversed(versions):
        timestamp = wall_clocks.get(version.clock.process_id, 0)
        if best_timestamp is None or timestamp > best_timestamp:
            best, best_timestamp = version, timestamp

    # この関数は「正しく」動く。それでもデータは失われる。
    # 壁時計がずれていれば、実際には後の書き込みが負けるからだ。
    # 実装の誤りではなく、方式そのものの性質である。
    return best.value if best is not None else None
