"""ノード追加時に移動するキーの割合を実測する。

    python3 measure.py

このスクリプトは実装が完成してから実行してください。
"""

from collections import Counter

from partitioner import (
    ConsistentHashPartitioner,
    FixedPartitioner,
    ModuloPartitioner,
)

KEYS = [f"user-{i}" for i in range(100_000)]


def moved_ratio(before, after) -> float:
    moved = sum(1 for k in KEYS if before.get_node(k) != after.get_node(k))
    return moved / len(KEYS)


def _grown(nodes: list[str], new_node: str) -> FixedPartitioner:
    """4 台構成を作ってから 1 台足す(最初から 5 台で作るのとは別物)"""
    p = FixedPartitioner(nodes)
    p.add_node(new_node)
    return p


def imbalance(partitioner) -> float:
    counts = Counter(partitioner.get_node(k) for k in KEYS)
    return max(counts.values()) / (len(KEYS) / len(counts))


def main() -> None:
    nodes4 = ["n1", "n2", "n3", "n4"]
    nodes5 = [*nodes4, "n5"]

    cases = [
        ("hash % N", ModuloPartitioner(nodes4), ModuloPartitioner(nodes5)),
        ("固定512パーティション", FixedPartitioner(nodes4), _grown(nodes4, "n5")),
        (
            "コンシステントハッシュ",
            ConsistentHashPartitioner(nodes4),
            ConsistentHashPartitioner(nodes5),
        ),
    ]

    print(f"キー数: {len(KEYS):,}  ノード: 4 台 → 5 台\n")
    print(f"  {'方式':<26} {'移動率':>8}  {'偏り(最大/平均)':>16}")
    print("  " + "-" * 54)
    for name, before, after in cases:
        print(f"  {name:<26} {moved_ratio(before, after):>7.1%}  {imbalance(after):>15.2f}")

    print()
    print("  理論値: 5 台へ増やすとき、理想的には 1/5 = 20% だけが移動すればよい。")
    print("  hash % N がそれを大きく超えるのが、この方式を使えない理由。")


if __name__ == "__main__":
    main()
