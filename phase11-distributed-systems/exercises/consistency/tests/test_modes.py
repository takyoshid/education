import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from modes import ReadMode, Store  # noqa: E402


class WriteTest(unittest.TestCase):
    def test_positions_increase(self):
        store = Store(["r1"])
        self.assertEqual(store.write("a", "1"), 1)
        self.assertEqual(store.write("a", "2"), 2)

    def test_rejects_unknown_dependency(self):
        store = Store(["r1"])
        with self.assertRaises(ValueError):
            store.write("a", "1", depends_on=99)

    def test_replicate_rejects_unknown_position(self):
        store = Store(["r1"])
        store.write("a", "1")
        with self.assertRaises(ValueError):
            store.replicate_to(0, [99])


class StrongReadTest(unittest.TestCase):
    def test_always_returns_latest_regardless_of_replication(self):
        store = Store(["r1"])
        store.write("x", "v1")
        store.write("x", "v2")
        # replica には何も複製していない
        self.assertEqual(store.read("x", ReadMode.STRONG), "v2")


class EventualReadTest(unittest.TestCase):
    def test_can_return_stale_value(self):
        store = Store(["r1"])
        p1 = store.write("x", "v1")
        store.write("x", "v2")
        store.replicate_to(0, [p1])      # 1 件目だけ複製

        self.assertEqual(store.read("x", ReadMode.EVENTUAL), "v1", "古い値が読める")
        self.assertEqual(store.read("x", ReadMode.STRONG), "v2")

    def test_can_return_nothing(self):
        store = Store(["r1"])
        store.write("x", "v1")
        self.assertIsNone(store.read("x", ReadMode.EVENTUAL), "未複製なら見えない")

    def test_breaks_causal_order(self):
        """異常の再現: 返信だけが先に見えてしまう"""
        store = Store(["r1"])
        q = store.write("msg:1", "今日の天気は?")
        a = store.write("msg:2", "晴れです", depends_on=q)

        store.replicate_to(0, [a])       # 返信だけが先に届いた

        self.assertEqual(store.read("msg:2", ReadMode.EVENTUAL), "晴れです")
        self.assertIsNone(store.read("msg:1", ReadMode.EVENTUAL))
        # → 質問が見えないのに返信だけが見える


class CausalReadTest(unittest.TestCase):
    def test_hides_write_whose_cause_is_missing(self):
        """因果モードなら、原因が届いていない書き込みは見せない"""
        store = Store(["r1"])
        q = store.write("msg:1", "今日の天気は?")
        a = store.write("msg:2", "晴れです", depends_on=q)

        store.replicate_to(0, [a])       # 返信だけが届いた

        self.assertIsNone(
            store.read("msg:2", ReadMode.CAUSAL),
            "原因(質問)が未着なので、返信を見せてはいけない",
        )

    def test_shows_write_once_cause_arrives(self):
        store = Store(["r1"])
        q = store.write("msg:1", "今日の天気は?")
        a = store.write("msg:2", "晴れです", depends_on=q)

        store.replicate_to(0, [a, q])    # 順序は逆でも、両方揃えば見せてよい

        self.assertEqual(store.read("msg:1", ReadMode.CAUSAL), "今日の天気は?")
        self.assertEqual(store.read("msg:2", ReadMode.CAUSAL), "晴れです")

    def test_allows_stale_but_causally_consistent_value(self):
        """因果整合性は「最新」を保証しない。順序だけを保証する。"""
        store = Store(["r1"])
        p1 = store.write("x", "v1")
        store.write("x", "v2")           # 因果関係なし
        store.replicate_to(0, [p1])

        self.assertEqual(
            store.read("x", ReadMode.CAUSAL), "v1",
            "古い値でよい。因果整合性は最新性を約束しない",
        )

    def test_independent_writes_are_not_blocked(self):
        store = Store(["r1"])
        store.write("a", "1")
        p2 = store.write("b", "2")       # a とは無関係
        store.replicate_to(0, [p2])

        self.assertEqual(store.read("b", ReadMode.CAUSAL), "2")


class ModeComparisonTest(unittest.TestCase):
    def test_same_state_three_different_answers(self):
        """まったく同じ複製状態で、モードによって答えが変わる。

        この表がこの演習の結論です。
        """
        store = Store(["r1"])
        q = store.write("msg", "質問")
        store.write("msg", "回答", depends_on=q)
        # 何も複製しない状態で、"msg" を読む

        self.assertEqual(store.read("msg", ReadMode.STRONG), "回答")
        self.assertIsNone(store.read("msg", ReadMode.CAUSAL))
        self.assertIsNone(store.read("msg", ReadMode.EVENTUAL))

        store.replicate_to(0, [q])
        self.assertEqual(store.read("msg", ReadMode.STRONG), "回答")
        self.assertEqual(store.read("msg", ReadMode.CAUSAL), "質問")
        self.assertEqual(store.read("msg", ReadMode.EVENTUAL), "質問")


if __name__ == "__main__":
    unittest.main()
