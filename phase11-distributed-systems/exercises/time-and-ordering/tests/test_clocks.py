import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from clocks import (  # noqa: E402
    LamportClock,
    Ordering,
    VectorClock,
    Version,
    VersionedRegister,
    last_write_wins,
)


class LamportClockTest(unittest.TestCase):
    def test_tick_starts_at_one(self):
        clock = LamportClock()
        self.assertEqual(clock.tick(), 1)
        self.assertEqual(clock.tick(), 2)

    def test_send_advances_the_clock(self):
        clock = LamportClock()
        clock.tick()
        self.assertEqual(clock.send(), 2)

    def test_receive_takes_the_maximum_and_adds_one(self):
        clock = LamportClock()
        clock.tick()  # 1
        self.assertEqual(clock.receive(5), 6)

    def test_receive_still_advances_when_incoming_is_behind(self):
        # 相手が遅れていても、受信は出来事なので必ず進む。
        clock = LamportClock()
        for _ in range(10):
            clock.tick()
        self.assertEqual(clock.receive(2), 11)

    def test_causality_is_reflected_in_the_numbers(self):
        # A → B ならば C(A) < C(B) が成り立つ。
        sender = LamportClock()
        receiver = LamportClock()
        receiver.tick()
        receiver.tick()

        sent_at = sender.send()
        received_at = receiver.receive(sent_at)
        self.assertLess(sent_at, received_at)


class VectorClockTest(unittest.TestCase):
    def test_tick_only_advances_own_entry(self):
        clock = VectorClock("P")
        clock.tick()
        clock.tick()
        self.assertEqual(clock.counters.get("P"), 2)
        self.assertEqual(clock.counters.get("Q", 0), 0)

    def test_merge_takes_maximum_then_advances_self(self):
        p = VectorClock("P", {"P": 1, "Q": 5})
        q = VectorClock("Q", {"P": 3, "Q": 2})
        p.merge(q)
        self.assertEqual(p.counters["P"], 4)   # max(1, 3) = 3、そこに +1
        self.assertEqual(p.counters["Q"], 5)   # max(5, 2) = 5

    def test_equal_clocks(self):
        a = VectorClock("P", {"P": 1, "Q": 1})
        b = VectorClock("Q", {"P": 1, "Q": 1})
        self.assertEqual(a.compare(b), Ordering.EQUAL)

    def test_before_and_after(self):
        earlier = VectorClock("P", {"P": 1})
        later = VectorClock("P", {"P": 2})
        self.assertEqual(earlier.compare(later), Ordering.BEFORE)
        self.assertEqual(later.compare(earlier), Ordering.AFTER)

    def test_missing_entries_count_as_zero(self):
        a = VectorClock("P", {"P": 1})
        b = VectorClock("P", {"P": 1, "Q": 1})
        self.assertEqual(a.compare(b), Ordering.BEFORE)

    def test_detects_concurrent_updates(self):
        # 互いに相手より進んでいる要素がある = 並行。
        # これが Lamport clock には判定できなかったもの。
        a = VectorClock("P", {"P": 2, "Q": 0})
        b = VectorClock("Q", {"P": 1, "Q": 3})
        self.assertEqual(a.compare(b), Ordering.CONCURRENT)
        self.assertEqual(b.compare(a), Ordering.CONCURRENT)

    def test_causal_chain_is_not_concurrent(self):
        # P が書き、Q がそれを見てから書いた場合は因果がある。
        p = VectorClock("P")
        p.tick()
        first = p.copy()

        q = VectorClock("Q")
        q.merge(p)
        second = q.copy()

        self.assertEqual(first.compare(second), Ordering.BEFORE)


class VersionedRegisterTest(unittest.TestCase):
    def _version(self, value, process, counters):
        return Version(value, VectorClock(process, counters))

    def test_single_write(self):
        register = VersionedRegister()
        register.write(self._version("a", "P", {"P": 1}))
        self.assertEqual(register.read(), ["a"])
        self.assertFalse(register.has_conflict)

    def test_causal_overwrite_replaces_the_old_value(self):
        register = VersionedRegister()
        register.write(self._version("a", "P", {"P": 1}))
        register.write(self._version("b", "P", {"P": 2}))
        self.assertEqual(register.read(), ["b"])
        self.assertFalse(register.has_conflict)

    def test_older_write_is_ignored(self):
        register = VersionedRegister()
        register.write(self._version("b", "P", {"P": 2}))
        register.write(self._version("a", "P", {"P": 1}))
        self.assertEqual(register.read(), ["b"])

    def test_concurrent_writes_are_both_kept(self):
        # ここが核心。並行な書き込みは、どちらも捨ててはいけない。
        register = VersionedRegister()
        register.write(self._version("cart:apple", "P", {"P": 2, "Q": 0}))
        register.write(self._version("cart:banana", "Q", {"P": 1, "Q": 3}))

        self.assertTrue(register.has_conflict)
        self.assertCountEqual(register.read(), ["cart:apple", "cart:banana"])

    def test_later_causal_write_resolves_the_conflict(self):
        # 競合を見たクライアントが、両方を知ったうえで書き直すと収束する。
        register = VersionedRegister()
        register.write(self._version("apple", "P", {"P": 2, "Q": 0}))
        register.write(self._version("banana", "Q", {"P": 1, "Q": 3}))
        self.assertTrue(register.has_conflict)

        register.write(self._version("apple+banana", "P", {"P": 3, "Q": 3}))
        self.assertFalse(register.has_conflict)
        self.assertEqual(register.read(), ["apple+banana"])


class LastWriteWinsTest(unittest.TestCase):
    def _version(self, value, process):
        return Version(value, VectorClock(process, {process: 1}))

    def test_picks_the_largest_timestamp(self):
        versions = [self._version("old", "P"), self._version("new", "Q")]
        result = last_write_wins(versions, {"P": 100, "Q": 200})
        self.assertEqual(result, "new")

    def test_silently_discards_a_concurrent_write(self):
        """LWW は競合を解決しない。片方を黙って捨てる。

        ここでは P の時計が 5 秒進んでいる状況を作る。
        実際には Q の書き込みが後なのに、P が勝ってしまう。
        エラーにもならず、ログにも残らないのが問題の本質。
        """
        versions = [
            self._version("Pが書いた値", "P"),
            self._version("Qが書いた値", "Q"),
        ]
        # P の時計が進んでいるせいで、実際には後の Q が負ける
        skewed = {"P": 1_000_005, "Q": 1_000_001}
        result = last_write_wins(versions, skewed)

        self.assertEqual(result, "Pが書いた値")
        self.assertNotIn("Qが書いた値", [result])

    def test_versioned_register_keeps_what_lww_would_lose(self):
        """同じ入力を両方式に与えて、失われる情報の差を見る。"""
        concurrent = [
            Version("Pが書いた値", VectorClock("P", {"P": 2, "Q": 0})),
            Version("Qが書いた値", VectorClock("Q", {"P": 1, "Q": 3})),
        ]

        lww_result = last_write_wins(concurrent, {"P": 1_000_005, "Q": 1_000_001})
        self.assertEqual(lww_result, "Pが書いた値")

        register = VersionedRegister()
        for version in concurrent:
            register.write(version)

        # LWW は 1 つしか残さない。バージョン管理は両方残す。
        self.assertEqual(len(register.read()), 2)
        self.assertIn("Qが書いた値", register.read())


if __name__ == "__main__":
    unittest.main(verbosity=2)
