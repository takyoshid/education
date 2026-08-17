"""演習: 過半数クォーラムが split-brain を防ぐことを、総当たりで確かめる。

    python3 -m unittest discover -s tests -v

証明を読むのではなく、全分断パターンを実行して確認します。
"""

from __future__ import annotations

from dataclasses import dataclass


class NoQuorumError(Exception):
    """過半数に達していないため、決定できない"""


def majority_size(node_count: int) -> int:
    """node_count 台のクラスタにおける過半数の最小サイズを返す。

    要件:
      - 3 台なら 2、4 台なら 3、5 台なら 3
      - node_count が 1 未満なら ValueError

    ヒント: 「半分より多い」を整数で表す。node_count // 2 + 1
    """
    raise NotImplementedError


def tolerable_failures(node_count: int) -> int:
    """過半数を維持したまま耐えられる障害ノード数を返す。

    要件:
      - 3 台なら 1、4 台なら 1、5 台なら 2、6 台なら 2
      - この関数の結果から「偶数台に意味がない」ことが読み取れるはず
    """
    raise NotImplementedError


@dataclass(frozen=True)
class Partition:
    """ネットワーク分断によって分かれたノード群"""

    side_a: frozenset[str]
    side_b: frozenset[str]


class Cluster:
    """ノードの集合。分断された状態で書き込めるかを判定する。"""

    def __init__(self, nodes: list[str]) -> None:
        if not nodes:
            raise ValueError("ノードが空です")
        if len(set(nodes)) != len(nodes):
            raise ValueError("ノード名が重複しています")
        self.nodes = list(nodes)

    def can_accept_writes(self, reachable: frozenset[str]) -> bool:
        """reachable(到達可能なノード集合)から見て、書き込みを受け付けてよいか。

        要件:
          - reachable がクラスタの過半数を含むなら True
          - そうでなければ False
          - reachable にクラスタ外のノードが含まれていたら ValueError

        これが「分断された側のうち、過半数を持つ側だけが動く」の実装。
        """
        raise NotImplementedError

    def elect_leader(self, reachable: frozenset[str]) -> str:
        """reachable の中からリーダーを選ぶ。

        要件:
          - 過半数が無ければ NoQuorumError
          - あれば reachable の中で辞書順が最小のノードを返す
            (実際の Raft はログの新しさで選ぶが、ここでは決定的であればよい)
        """
        raise NotImplementedError

    def all_partitions(self) -> list[Partition]:
        """このクラスタで起こりうる全ての 2 分割を列挙する。

        要件:
          - 片側が空になる分割(=分断なし)も含める
          - (A|B) と (B|A) は同じ分断なので、片方だけを返す
          - n ノードなら 2^(n-1) 通り

        ヒント: 各ノードが side_a か side_b かの 2 択。
        重複を避けるため、常に特定のノード(例: nodes[0])を side_a に固定する。
        """
        raise NotImplementedError
