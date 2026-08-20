"""演習: 因果と競合を、時計を使わずに見分ける。

    python3 -m unittest discover -s tests -v

壁時計を一切使わずに、2 つの操作が
「一方が先か」「並行か」を判定できるようにします。

最後の課題では、last-write-wins が実際にデータを捨てる様子を再現します。
「捨てられる」と読むのと、消えるところを自分で作るのとでは理解が違います。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Ordering(Enum):
    """2 つの出来事の関係。"""

    BEFORE = "before"          # 自分のほうが先に起きた
    AFTER = "after"            # 相手のほうが先に起きた
    CONCURRENT = "concurrent"  # 順序が決まらない(競合)
    EQUAL = "equal"            # 同じ時点


# ---------------------------------------------------------------------------
# 課題 1: Lamport clock
# ---------------------------------------------------------------------------


class LamportClock:
    """各プロセスが 1 つのカウンタを持つ論理時計。

    規則は 2 つだけ。

      1. 何か起きるたびに、自分のカウンタを 1 増やす
      2. メッセージを受け取ったら
         `自分のカウンタ = max(自分, 受け取った値) + 1`

    これで「A → B ならば C(A) < C(B)」が成り立つ。
    ただし逆は成り立たない(課題 2 でその限界を確かめる)。
    """

    def __init__(self) -> None:
        self.counter = 0

    def tick(self) -> int:
        """ローカルで出来事が起きた。カウンタを進めて、その値を返す。

        要件:
          - 呼ぶたびに 1 増える
          - 最初の呼び出しは 1 を返す
        """
        raise NotImplementedError

    def send(self) -> int:
        """メッセージを送る。添えるカウンタ値を返す。

        送信もひとつの出来事なので、カウンタは進む。
        """
        raise NotImplementedError

    def receive(self, incoming: int) -> int:
        """メッセージを受け取る。更新後のカウンタ値を返す。

        要件:
          - `max(自分, incoming) + 1` になること
          - 受信もひとつの出来事なので、必ず 1 以上進む
        """
        raise NotImplementedError


# ---------------------------------------------------------------------------
# 課題 2: Vector clock
# ---------------------------------------------------------------------------


@dataclass
class VectorClock:
    """全プロセス分のカウンタを持つ論理時計。

    Lamport clock と違い、「並行かどうか」を判定できる。
    ここが本質的な差なので、compare() の実装が本演習の核心。
    """

    process_id: str
    counters: dict[str, int] = field(default_factory=dict)

    def tick(self) -> None:
        """ローカルで出来事が起きた。自分の要素だけを 1 増やす。"""
        raise NotImplementedError

    def merge(self, other: "VectorClock") -> None:
        """メッセージを受け取った。

        要件:
          - 各プロセスの要素について、大きいほうを採用する
          - そのうえで、自分の要素を 1 増やす(受信も出来事なので)
        """
        raise NotImplementedError

    def compare(self, other: "VectorClock") -> Ordering:
        """2 つの時計の関係を判定する。

        すべての要素について自分 <= 相手 で、1 つ以上が自分 < 相手
            -> BEFORE(自分のほうが先)
        すべての要素について自分 >= 相手 で、1 つ以上が自分 > 相手
            -> AFTER
        すべての要素が等しい
            -> EQUAL
        どちらでもない(互いに勝っている要素がある)
            -> CONCURRENT

        注意: 相手に無い要素は 0 として扱う。
        「まだ一度も動いていないプロセス」と「存在しないプロセス」は同じ。
        """
        raise NotImplementedError

    def copy(self) -> "VectorClock":
        return VectorClock(self.process_id, dict(self.counters))


# ---------------------------------------------------------------------------
# 課題 3: 競合の検出と解決
# ---------------------------------------------------------------------------


@dataclass
class Version:
    """ある値と、それが書かれた時点の論理時計。"""

    value: object
    clock: VectorClock


class VersionedRegister:
    """1 つのキーの値を保持する。競合したら両方を残す。

    ここが last-write-wins との決定的な違い。
    LWW は片方を黙って捨てるが、この実装は「決められない」ことを
    決められないまま保持し、解決を呼び出し側に委ねる。
    """

    def __init__(self) -> None:
        self.versions: list[Version] = []

    def write(self, version: Version) -> None:
        """新しい版を書き込む。

        要件:
          - 既存の版のうち、新しい版より前(BEFORE)のものは捨てる
            (因果的に上書きされたので、残す意味がない)
          - 既存の版に、新しい版より後(AFTER)または同じ(EQUAL)ものが
            あれば、新しい版のほうが古いので何もしない
          - 並行(CONCURRENT)な版はすべて残す
        """
        raise NotImplementedError

    def read(self) -> list[object]:
        """現在の値を返す。

        競合していなければ要素 1 つ、競合していれば複数になる。
        呼び出し側は「複数返る」ことを想定しなければならない。
        """
        return [version.value for version in self.versions]

    @property
    def has_conflict(self) -> bool:
        return len(self.versions) > 1


# ---------------------------------------------------------------------------
# 課題 4: last-write-wins が何を捨てるか
# ---------------------------------------------------------------------------


def last_write_wins(versions: list[Version], wall_clocks: dict[str, int]) -> object:
    """壁時計のタイムスタンプが最大の版を選ぶ。

    `wall_clocks` は「各プロセスが記録した壁時計の値」。
    実際のシステムと同じく、この値はずれている可能性がある。

    要件:
      - wall_clocks[version.clock.process_id] が最大の版の value を返す
      - 同点のときは、後ろにある版を優先する(任意の決め方でよい)

    この関数はテストで「正しく動く」ことを確認するが、
    同時に「正しく動いても、データが失われる」ことも確認する。
    そこが課題の主眼。
    """
    raise NotImplementedError
