"""演習: 3 つの読み取りモードで、それぞれ何が観測できてしまうかを示す。

    python3 -m unittest discover -s tests -v

「弱い整合性だと変な値が読める」ではなく、
【どの異常が、どの条件で起きるか】を言えるようになるための演習です。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ReadMode(Enum):
    STRONG = "strong"        # 常に最新。linearizable
    CAUSAL = "causal"        # 因果関係のある書き込みは必ず順序どおりに見える
    EVENTUAL = "eventual"    # 何が見えるか保証しない


@dataclass(frozen=True)
class Write:
    key: str
    value: str
    position: int
    depends_on: int | None = None   # 因果関係: この書き込みの前提となる position


@dataclass
class Replica:
    """任意の position まで適用できる複製"""

    name: str
    applied: set[int] = field(default_factory=set)
    data: dict[str, str] = field(default_factory=dict)

    def apply(self, write: Write) -> None:
        self.applied.add(write.position)
        self.data[write.key] = write.value

    def has(self, position: int) -> bool:
        return position in self.applied


class Store:
    """1 つの leader と複数の replica を持つデータストア"""

    def __init__(self, replicas: list[str]) -> None:
        if not replicas:
            raise ValueError("replica が空です")
        self.log: list[Write] = []
        self.replicas = [Replica(name) for name in replicas]

    def write(self, key: str, value: str, depends_on: int | None = None) -> int:
        """書き込んで position を返す。

        要件:
          - position は 1 始まりの単調増加
          - depends_on が未知の position なら ValueError
        """
        raise NotImplementedError

    def replicate_to(self, replica_index: int, positions: list[int]) -> None:
        """指定した replica へ、指定した position だけを適用する。

        要件:
          - 存在しない position なら ValueError
          - 順序は positions の並びどおりに適用する
            (わざと順序を入れ替えて異常を再現できるようにする)
        """
        raise NotImplementedError

    def _causally_ready(self, replica: Replica, write: Write) -> bool:
        """この replica で、その書き込みを見せてよいか。

        要件:
          - depends_on が None なら見せてよい
          - depends_on の position がその replica に適用済みなら見せてよい
          - そうでなければ見せてはいけない(因果順序が崩れるため)
        """
        raise NotImplementedError

    def read(self, key: str, mode: ReadMode, replica_index: int = 0) -> str | None:
        """指定したモードで読み取る。

        要件:
          - STRONG   : 常にログ上の最新値を返す(replica を見ない)
          - EVENTUAL : その replica が持っている値をそのまま返す
          - CAUSAL   : その replica が持つ値のうち、因果的に見せてよい最新の
                       書き込みの値を返す。見せてよいものが無ければ None

        ヒント: CAUSAL では、その key に対する書き込みをログから新しい順に見て、
        「replica に適用済み」かつ「_causally_ready」である最初のものを返す。
        """
        raise NotImplementedError
