import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from store import Follower, Leader, ReadRouter  # noqa: E402


class LeaderTest(unittest.TestCase):
    def test_positions_increase_from_one(self):
        leader = Leader()
        self.assertEqual(leader.write("a", "1"), 1)
        self.assertEqual(leader.write("b", "2"), 2)
        self.assertEqual(leader.read("a"), "1")


class ReplicationTest(unittest.TestCase):
    def test_follower_catches_up(self):
        leader = Leader()
        follower = Follower(leader)
        leader.write("a", "1")
        leader.write("a", "2")

        self.assertIsNone(follower.read("a"), "複製前は見えない")
        self.assertEqual(follower.lag, 2)

        follower.replicate()
        self.assertEqual(follower.read("a"), "2")
        self.assertEqual(follower.lag, 0)

    def test_partial_replication(self):
        leader = Leader()
        follower = Follower(leader)
        leader.write("a", "1")
        leader.write("a", "2")

        follower.replicate(up_to=1)
        self.assertEqual(follower.read("a"), "1", "1件目までしか適用していない")
        self.assertEqual(follower.lag, 1)


class AnomalyReproductionTest(unittest.TestCase):
    """3 つの異常を確定的に再現する"""

    def test_read_your_writes_violation(self):
        leader = Leader()
        follower = Follower(leader)
        router = ReadRouter(leader, [follower])

        pos = leader.write("comment:1", "はじめまして")
        router.note_write("alice", pos)
        # follower はまだ複製していない

        self.assertIsNone(
            router.read_naive("comment:1"),
            "自分が書いたコメントが自分に見えない(異常が再現できている)",
        )

    def test_monotonic_reads_violation(self):
        leader = Leader()
        fast = Follower(leader, name="fast")
        slow = Follower(leader, name="slow")

        leader.write("post:1", "本文")
        fast.replicate()          # fast だけ追いついた

        self.assertEqual(fast.read("post:1"), "本文")
        self.assertIsNone(slow.read("post:1"), "遅い follower では消えて見える")

    def test_consistent_prefix_violation(self):
        """因果関係のある2件が、順序を入れ替えて見える"""
        leader = Leader()
        follower = Follower(leader)

        leader.write("msg:1", "今日の天気は?")
        leader.write("msg:2", "晴れです")

        # 2件目だけが先に届いた状況を模す
        follower.data["msg:2"] = "晴れです"

        self.assertEqual(follower.read("msg:2"), "晴れです")
        self.assertIsNone(follower.read("msg:1"), "返信だけが先に見えている")


class ReadYourWritesTest(unittest.TestCase):
    def test_falls_back_to_leader_when_follower_is_behind(self):
        leader = Leader()
        follower = Follower(leader)
        router = ReadRouter(leader, [follower])

        pos = leader.write("comment:1", "はじめまして")
        router.note_write("alice", pos)

        self.assertEqual(
            router.read_your_writes("alice", "comment:1"),
            "はじめまして",
            "follower が遅れているなら leader から読むべき",
        )

    def test_uses_follower_once_caught_up(self):
        leader = Leader()
        follower = Follower(leader)
        router = ReadRouter(leader, [follower])

        pos = leader.write("comment:1", "はじめまして")
        router.note_write("alice", pos)
        follower.replicate()

        self.assertEqual(router.read_your_writes("alice", "comment:1"), "はじめまして")

    def test_other_users_may_read_from_follower(self):
        leader = Leader()
        follower = Follower(leader)
        router = ReadRouter(leader, [follower])

        pos = leader.write("comment:1", "はじめまして")
        router.note_write("alice", pos)

        # bob は何も書いていないので、古い値が見えても構わない
        self.assertIsNone(router.read_your_writes("bob", "comment:1"))

    def test_note_write_keeps_the_latest_position(self):
        leader = Leader()
        follower = Follower(leader)
        router = ReadRouter(leader, [follower])

        router.note_write("alice", 5)
        router.note_write("alice", 2)      # 古い位置で上書きしてはいけない
        leader.write("x", "1")
        follower.replicate()               # position 1 まで適用

        # alice は position 5 を待つべきなので leader へ回る
        self.assertEqual(router.read_your_writes("alice", "x"), "1")


class MonotonicReadsTest(unittest.TestCase):
    def test_same_user_always_hits_the_same_follower(self):
        leader = Leader()
        followers = [Follower(leader, name=f"f{i}") for i in range(3)]
        router = ReadRouter(leader, followers)

        leader.write("k", "v")
        followers[0].replicate()      # 1台だけ追いつかせる

        results = {router.read_monotonic("alice", "k") for _ in range(20)}
        self.assertEqual(len(results), 1, "同じ利用者の読み取り結果がぶれている")

    def test_routing_is_stable_across_instances(self):
        """プロセスをまたいでも同じ振り分けになること(組み込み hash は不可)"""
        leader = Leader()
        followers = [Follower(leader, name=f"f{i}") for i in range(5)]
        r1 = ReadRouter(leader, followers)
        r2 = ReadRouter(leader, followers)

        leader.write("k", "v")
        for f in followers:
            f.replicate()

        for user in ("alice", "bob", "carol", "dave"):
            self.assertEqual(
                r1.read_monotonic(user, "k"), r2.read_monotonic(user, "k")
            )


if __name__ == "__main__":
    unittest.main()
