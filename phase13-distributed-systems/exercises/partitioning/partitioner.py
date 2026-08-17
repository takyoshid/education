"""演習: 3 つの分割方式を実装し、ノード追加時の移動量を実測する。

    python3 -m unittest discover -s tests -v
    python3 measure.py        # 移動するキーの割合を実測する

「コンシステントハッシュなら移動は 1/N 程度」を、自分の目で確かめます。
"""

from __future__ import annotations

import bisect
import hashlib


def stable_hash(key: str) -> int:
    """決定的なハッシュ値を返す。

    Python 組み込みの hash() は文字列に対してプロセスごとに変わる
    (PYTHONHASHSEED によるランダム化)ため、永続的な分割には使えない。
    """
    return int(hashlib.sha256(key.encode("utf-8")).hexdigest(), 16)


class ModuloPartitioner:
    """素朴な hash(key) % N。ノード数が変わるとほぼ全部が移動する。"""

    def __init__(self, nodes: list[str]) -> None:
        if not nodes:
            raise ValueError("ノードが空です")
        self.nodes = sorted(nodes)

    def get_node(self, key: str) -> str:
        """key を担当するノード名を返す。

        要件: stable_hash(key) % ノード数 で決める
        """
        raise NotImplementedError


class FixedPartitioner:
    """固定数のパーティションを、ノードへ「明示的に割り当てる」方式。

    重要: パーティション番号からノードを求めるときに
    `partition % node_count` としてはいけない。それでは結局
    ModuloPartitioner と同じで、ノード追加時にほぼ全部が移動する。

    この方式の要点は、パーティション→ノードの割り当てを
    【表として保持し】、ノード追加時に必要な分だけ引っ越すこと。
    Elasticsearch や Riak が採る方式。
    """

    def __init__(self, nodes: list[str], partition_count: int = 512) -> None:
        if not nodes:
            raise ValueError("ノードが空です")
        if partition_count < len(nodes):
            raise ValueError("partition_count はノード数以上である必要があります")
        self.partition_count = partition_count
        # assignment[i] = パーティション i を担当するノード名
        self.assignment: list[str] = []
        self._initial_assign(sorted(nodes))

    def _initial_assign(self, nodes: list[str]) -> None:
        """パーティションをノードへ均等に配る(ラウンドロビンでよい)。

        要件: self.assignment を長さ partition_count のリストにする
        """
        raise NotImplementedError

    @property
    def nodes(self) -> list[str]:
        return sorted(set(self.assignment))

    def get_partition(self, key: str) -> int:
        """key が属するパーティション番号を返す。

        要件: stable_hash(key) % partition_count
        ここはノード数に依存しないので、ノードが増えても変わらない。
        """
        raise NotImplementedError

    def get_node(self, key: str) -> str:
        """key を担当するノード名を返す。

        要件: 割り当て表を引くだけ。計算し直さない。
        """
        raise NotImplementedError

    def add_node(self, node: str) -> int:
        """ノードを追加し、担当を引き取らせる。移動したパーティション数を返す。

        要件:
          - 追加後、各ノードの担当数がほぼ均等(差が 1 以下)になる
          - 移動させるのは必要最小限
            (新ノードの取り分 = partition_count // 新しいノード数 だけ)
          - 最も多く担当しているノードから順に取り上げる
          - すでに存在するノードなら ValueError

        ここが「固定数パーティション」方式の本体です。
        """
        raise NotImplementedError


class ConsistentHashPartitioner:
    """コンシステントハッシュ法。

    ハッシュ空間を円環とみなし、ノードを vnodes 個の仮想ノードとして配置する。
    キーは「時計回りで最初に出会ったノード」が担当する。
    """

    def __init__(self, nodes: list[str], vnodes: int = 150) -> None:
        if not nodes:
            raise ValueError("ノードが空です")
        if vnodes < 1:
            raise ValueError("vnodes は 1 以上である必要があります")
        self.vnodes = vnodes
        self._ring: list[tuple[int, str]] = []
        for node in nodes:
            self.add_node(node)

    def add_node(self, node: str) -> None:
        """ノードを円環へ追加する。

        要件:
          - vnodes 個の仮想ノードを、stable_hash(f"{node}#{i}") の位置に配置する
          - self._ring は (ハッシュ値, ノード名) のリストで、常にソート済みに保つ

        ヒント: bisect.insort を使うとソートを保ったまま挿入できる
        """
        raise NotImplementedError

    def get_node(self, key: str) -> str:
        """key を担当するノード名を返す。

        要件:
          - stable_hash(key) の位置から時計回りで最初の仮想ノードを探す
          - 円環なので、末尾を越えたら先頭に戻る

        ヒント: bisect.bisect で挿入位置を求め、リスト長で割った余りを使う
        """
        raise NotImplementedError
