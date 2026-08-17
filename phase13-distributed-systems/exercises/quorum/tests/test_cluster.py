import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cluster import (  # noqa: E402
    Cluster,
    NoQuorumError,
    majority_size,
    tolerable_failures,
)


class MajorityTest(unittest.TestCase):
    def test_majority_size(self):
        expected = {1: 1, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 4}
        for n, want in expected.items():
            self.assertEqual(majority_size(n), want, f"{n} ノードの過半数")

    def test_rejects_invalid_node_count(self):
        with self.assertRaises(ValueError):
            majority_size(0)

    def test_even_node_counts_are_wasteful(self):
        """4台は3台と、6台は5台と同じ耐障害性しかない。

        これが「クラスタは奇数台にする」の根拠。
        """
        self.assertEqual(tolerable_failures(3), tolerable_failures(4))
        self.assertEqual(tolerable_failures(5), tolerable_failures(6))
        self.assertEqual(tolerable_failures(3), 1)
        self.assertEqual(tolerable_failures(5), 2)
        self.assertEqual(tolerable_failures(7), 3)


class WriteAcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.cluster = Cluster(["a", "b", "c", "d", "e"])

    def test_majority_side_accepts_writes(self):
        self.assertTrue(self.cluster.can_accept_writes(frozenset({"a", "b", "c"})))

    def test_minority_side_rejects_writes(self):
        self.assertFalse(self.cluster.can_accept_writes(frozenset({"d", "e"})))

    def test_rejects_unknown_node(self):
        with self.assertRaises(ValueError):
            self.cluster.can_accept_writes(frozenset({"a", "zzz"}))

    def test_elect_leader_requires_quorum(self):
        self.assertEqual(self.cluster.elect_leader(frozenset({"c", "b", "a"})), "a")
        with self.assertRaises(NoQuorumError):
            self.cluster.elect_leader(frozenset({"d", "e"}))


class SplitBrainTest(unittest.TestCase):
    def test_no_two_majorities_can_coexist(self):
        """全ての分断パターンで、両側が同時に書き込めることは無い。

        これが「過半数の集合は必ず互いに重なる」の実験的な確認。
        3〜7 ノードすべてについて総当たりする。
        """
        for n in range(1, 8):
            nodes = [chr(ord("a") + i) for i in range(n)]
            cluster = Cluster(nodes)
            partitions = cluster.all_partitions()

            self.assertEqual(
                len(partitions), 2 ** (n - 1), f"{n} ノードの分断パターン数"
            )

            for part in partitions:
                a_ok = cluster.can_accept_writes(part.side_a)
                b_ok = cluster.can_accept_writes(part.side_b)
                self.assertFalse(
                    a_ok and b_ok,
                    f"split-brain: {n}ノード {set(part.side_a)} と "
                    f"{set(part.side_b)} が両方書き込み可能",
                )

    def test_odd_cluster_always_has_a_working_side(self):
        """奇数台なら、どう分断されても必ず片側は動ける。"""
        for n in (3, 5, 7):
            nodes = [chr(ord("a") + i) for i in range(n)]
            cluster = Cluster(nodes)
            for part in cluster.all_partitions():
                a_ok = cluster.can_accept_writes(part.side_a)
                b_ok = cluster.can_accept_writes(part.side_b)
                self.assertTrue(
                    a_ok or b_ok,
                    f"{n}ノードが全停止した: {set(part.side_a)} / {set(part.side_b)}",
                )

    def test_even_cluster_can_deadlock_on_even_split(self):
        """偶数台は 2:2 に割れると両側とも停止する。奇数台にすべき理由。"""
        cluster = Cluster(["a", "b", "c", "d"])
        left = frozenset({"a", "b"})
        right = frozenset({"c", "d"})
        self.assertFalse(cluster.can_accept_writes(left))
        self.assertFalse(cluster.can_accept_writes(right))


if __name__ == "__main__":
    unittest.main()
