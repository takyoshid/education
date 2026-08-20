import sys
import time
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from retry import (  # noqa: E402
    PermanentError,
    RetryBudgetExceeded,
    TransientError,
    compute_delay,
    retry_call,
)


class FakeClock:
    """時間を自分で進める偽の時計。実際には待たない。"""

    def __init__(self) -> None:
        self.now = 0.0
        self.slept: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.now += seconds


def max_jitter(low: float, high: float) -> float:
    """jitter を無効化して上限を返す(決定的にテストするため)"""
    return high


def min_jitter(low: float, high: float) -> float:
    return low


class ComputeDelayTest(unittest.TestCase):
    def test_grows_exponentially(self):
        delays = [
            compute_delay(i, base_delay=1.0, cap=100.0, rand=max_jitter)
            for i in range(5)
        ]
        self.assertEqual(delays, [1.0, 2.0, 4.0, 8.0, 16.0])

    def test_respects_cap(self):
        delay = compute_delay(20, base_delay=1.0, cap=10.0, rand=max_jitter)
        self.assertEqual(delay, 10.0)

    def test_full_jitter_lower_bound_is_zero(self):
        delay = compute_delay(3, base_delay=1.0, cap=100.0, rand=min_jitter)
        self.assertEqual(delay, 0.0)

    def test_rejects_negative_attempt(self):
        with self.assertRaises(ValueError):
            compute_delay(-1, base_delay=1.0, cap=10.0)


class RetryCallTest(unittest.TestCase):
    def test_returns_immediately_on_success(self):
        clock = FakeClock()
        calls = []

        def succeeds():
            calls.append(1)
            return "ok"

        result = retry_call(
            succeeds, sleep=clock.sleep, monotonic=clock.monotonic, rand=max_jitter
        )
        self.assertEqual(result, "ok")
        self.assertEqual(len(calls), 1)
        self.assertEqual(clock.slept, [], "成功時に待機してはいけない")

    def test_retries_transient_then_succeeds(self):
        clock = FakeClock()
        attempts = []

        def fails_twice():
            attempts.append(1)
            if len(attempts) < 3:
                raise TransientError("一時的")
            return "ok"

        result = retry_call(
            fails_twice,
            base_delay=1.0,
            sleep=clock.sleep,
            monotonic=clock.monotonic,
            rand=max_jitter,
        )
        self.assertEqual(result, "ok")
        self.assertEqual(len(attempts), 3)
        self.assertEqual(clock.slept, [1.0, 2.0])

    def test_does_not_retry_permanent_error(self):
        clock = FakeClock()
        attempts = []

        def always_permanent():
            attempts.append(1)
            raise PermanentError("恒久的")

        with self.assertRaises(PermanentError):
            retry_call(
                always_permanent,
                sleep=clock.sleep,
                monotonic=clock.monotonic,
                rand=max_jitter,
            )

        self.assertEqual(len(attempts), 1, "retry_on に無い例外は再試行しない")
        self.assertEqual(clock.slept, [])

    def test_raises_last_error_after_max_attempts(self):
        clock = FakeClock()
        attempts = []

        def always_transient():
            attempts.append(1)
            raise TransientError("だめ")

        with self.assertRaises(TransientError):
            retry_call(
                always_transient,
                max_attempts=4,
                base_delay=1.0,
                sleep=clock.sleep,
                monotonic=clock.monotonic,
                rand=max_jitter,
            )

        self.assertEqual(len(attempts), 4)
        # 最後の試行の後には待機しない
        self.assertEqual(clock.slept, [1.0, 2.0, 4.0])

    def test_stops_without_sleeping_when_deadline_would_be_exceeded(self):
        clock = FakeClock()
        attempts = []

        def always_transient():
            attempts.append(1)
            raise TransientError("だめ")

        with self.assertRaises(RetryBudgetExceeded) as ctx:
            retry_call(
                always_transient,
                max_attempts=10,
                base_delay=1.0,
                deadline=2.5,
                sleep=clock.sleep,
                monotonic=clock.monotonic,
                rand=max_jitter,
            )

        # 1.0 待機 → 経過1.0、次は2.0待つと3.0で2.5を超えるので待たずに打ち切る
        self.assertEqual(clock.slept, [1.0])
        self.assertEqual(len(attempts), 2)
        self.assertIsInstance(ctx.exception.__cause__, TransientError)

    def test_rejects_invalid_max_attempts(self):
        with self.assertRaises(ValueError):
            retry_call(lambda: "x", max_attempts=0)

    def test_custom_retry_on(self):
        clock = FakeClock()
        attempts = []

        def raises_value_error():
            attempts.append(1)
            if len(attempts) < 2:
                raise ValueError("一時的とみなす")
            return "ok"

        result = retry_call(
            raises_value_error,
            retry_on=(ValueError,),
            base_delay=1.0,
            sleep=clock.sleep,
            monotonic=clock.monotonic,
            rand=max_jitter,
        )
        self.assertEqual(result, "ok")
        self.assertEqual(len(attempts), 2)


class TestSuiteSpeedTest(unittest.TestCase):
    def test_retry_never_uses_real_time(self):
        """実時間を待っていないことを検証する。

        FakeClock を使っているので、5回の retry でも一瞬で終わるはず。
        """
        clock = FakeClock()

        def always_transient():
            raise TransientError("だめ")

        started = time.monotonic()
        with self.assertRaises(TransientError):
            retry_call(
                always_transient,
                max_attempts=5,
                base_delay=60.0,        # 実時間なら合計15分以上かかる設定
                cap=600.0,
                sleep=clock.sleep,
                monotonic=clock.monotonic,
                rand=max_jitter,
            )
        elapsed = time.monotonic() - started

        self.assertLess(elapsed, 0.5, "実時間を待ってはいけない")
        # 仮想時間では 60 + 120 + 240 + 480 = 900 秒(15分)経過している。
        # 実時間で待っていたら、このテストだけで15分かかる。
        self.assertEqual(clock.slept, [60.0, 120.0, 240.0, 480.0])
        self.assertEqual(sum(clock.slept), 900.0)


if __name__ == "__main__":
    unittest.main()
