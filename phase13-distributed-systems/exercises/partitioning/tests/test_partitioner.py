import sys
import unittest
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from partitioner import (  # noqa: E402
    ConsistentHashPartitioner,
    FixedPartitioner,
    ModuloPartitioner,
    stable_hash,
)

KEYS = [f"user-{i}" for i in range(10_000)]
NODES_4 = ["n1", "n2", "n3", "n4"]
NODES_5 = ["n1", "n2", "n3", "n4", "n5"]


def moved_ratio(before, after, keys=KEYS) -> float:
    """ノード追加前後で担当が変わったキーの割合"""
    moved = sum(1 for k in keys if before.get_node(k) != after.get_node(k))
    return moved / len(keys)


def imbalance(partitioner, keys=KEYS) -> float:
    """最も多いノードの負荷 / 平均負荷。1.0 に近いほど均等。"""
    counts = Counter(partitioner.get_node(k) for k in keys)
    return max(counts.values()) / (len(keys) / len(counts))


class StableHashTest(unittest.TestCase):
    def test_is_deterministic(self):
        self.assertEqual(stable_hash("abc"), stable_hash("abc"))
        self.assertNotEqual(stable_hash("abc"), stable_hash("abd"))


class ModuloTest(unittest.TestCase):
    def test_assigns_every_key_to_a_known_node(self):
        p = ModuloPartitioner(NODES_4)
        for key in KEYS[:100]:
            self.assertIn(p.get_node(key), NODES_4)

    def test_is_deterministic(self):
        a, b = ModuloPartitioner(NODES_4), ModuloPartitioner(NODES_4)
        for key in KEYS[:100]:
            self.assertEqual(a.get_node(key), b.get_node(key))

    def test_distribution_is_balanced(self):
        self.assertLess(imbalance(ModuloPartitioner(NODES_4)), 1.1)

    def test_adding_a_node_moves_most_keys(self):
        """これがこの方式の致命的な欠点。4→5 台で 7 割以上が移動する。"""
        ratio = moved_ratio(ModuloPartitioner(NODES_4), ModuloPartitioner(NODES_5))
        self.assertGreater(ratio, 0.7, f"移動率が予想より低い: {ratio:.1%}")


class FixedPartitionTest(unittest.TestCase):
    def test_partition_is_independent_of_node_count(self):
        """パーティション番号はノード数に依存しない。ここが要点。"""
        a = FixedPartitioner(NODES_4, partition_count=512)
        b = FixedPartitioner(NODES_5, partition_count=512)
        for key in KEYS[:200]:
            self.assertEqual(a.get_partition(key), b.get_partition(key))

    def test_rejects_too_few_partitions(self):
        with self.assertRaises(ValueError):
            FixedPartitioner(NODES_4, partition_count=2)

    def test_distribution_is_balanced(self):
        self.assertLess(imbalance(FixedPartitioner(NODES_4)), 1.15)

    def test_initial_assignment_is_even(self):
        p = FixedPartitioner(NODES_4, partition_count=512)
        counts = Counter(p.assignment)
        self.assertEqual(len(counts), 4)
        self.assertLessEqual(max(counts.values()) - min(counts.values()), 1)

    def test_add_node_rebalances_evenly(self):
        p = FixedPartitioner(NODES_4, partition_count=512)
        p.add_node("n5")
        counts = Counter(p.assignment)
        self.assertEqual(len(counts), 5)
        self.assertLessEqual(max(counts.values()) - min(counts.values()), 1)

    def test_add_node_rejects_duplicate(self):
        p = FixedPartitioner(NODES_4, partition_count=512)
        with self.assertRaises(ValueError):
            p.add_node("n1")

    def test_add_node_moves_only_the_new_share(self):
        """4→5 台で移動するのは全体の 2 割程度。

        `partition % node_count` で求める実装だと 8 割動いてしまう。
        割り当て表を持つ意味はここにある。
        """
        before = FixedPartitioner(NODES_4, partition_count=512)
        after = FixedPartitioner(NODES_4, partition_count=512)
        moved_partitions = after.add_node("n5")

        self.assertLessEqual(moved_partitions, 512 // 5 + 1)

        ratio = moved_ratio(before, after)
        self.assertLess(ratio, 0.3, f"移動しすぎ: {ratio:.1%}")
        self.assertGreater(ratio, 0.05, f"移動が少なすぎる: {ratio:.1%}")


class ConsistentHashTest(unittest.TestCase):
    def test_assigns_every_key_to_a_known_node(self):
        p = ConsistentHashPartitioner(NODES_4)
        for key in KEYS[:100]:
            self.assertIn(p.get_node(key), NODES_4)

    def test_is_deterministic(self):
        a, b = ConsistentHashPartitioner(NODES_4), ConsistentHashPartitioner(NODES_4)
        for key in KEYS[:200]:
            self.assertEqual(a.get_node(key), b.get_node(key))

    def test_distribution_is_reasonably_balanced(self):
        """仮想ノードにより、偏りは 1.3 倍以内に収まる"""
        self.assertLess(imbalance(ConsistentHashPartitioner(NODES_4, vnodes=150)), 1.3)

    def test_more_vnodes_reduce_imbalance(self):
        few = imbalance(ConsistentHashPartitioner(NODES_4, vnodes=1))
        many = imbalance(ConsistentHashPartitioner(NODES_4, vnodes=200))
        self.assertLess(many, few, "仮想ノードを増やすと偏りが減るはず")

    def test_adding_a_node_moves_about_one_over_n(self):
        """4→5 台で移動するのは 2〜3 割程度(理論値 1/5 = 20%)。

        素朴な % 方式の 7 割超と比べてください。
        """
        ratio = moved_ratio(
            ConsistentHashPartitioner(NODES_4),
            ConsistentHashPartitioner(NODES_5),
        )
        self.assertLess(ratio, 0.35, f"移動しすぎ: {ratio:.1%}")
        self.assertGreater(ratio, 0.05, f"移動が少なすぎる(実装を確認): {ratio:.1%}")

    def test_consistent_hash_beats_modulo(self):
        """同じ条件で比べると、桁違いの差が出る"""
        modulo = moved_ratio(ModuloPartitioner(NODES_4), ModuloPartitioner(NODES_5))
        chash = moved_ratio(
            ConsistentHashPartitioner(NODES_4), ConsistentHashPartitioner(NODES_5)
        )
        self.assertLess(chash * 2, modulo, f"chash={chash:.1%} modulo={modulo:.1%}")


if __name__ == "__main__":
    unittest.main()
