import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from remote import (  # noqa: E402
    CallResult,
    Outcome,
    RemoteRejected,
    RemoteTimeout,
    UnreliableService,
    call_remote,
)


class CallRemoteTest(unittest.TestCase):
    def test_success(self):
        result = call_remote(lambda: "value")
        self.assertEqual(result.outcome, Outcome.SUCCESS)
        self.assertEqual(result.value, "value")

    def test_explicit_rejection_is_failed(self):
        def rejected():
            raise RemoteRejected("400 Bad Request")

        self.assertEqual(call_remote(rejected).outcome, Outcome.FAILED)

    def test_timeout_is_unknown_not_failed(self):
        """ここがこの演習の核心。timeout は FAILED ではない。"""

        def times_out():
            raise RemoteTimeout("応答なし")

        self.assertEqual(call_remote(times_out).outcome, Outcome.UNKNOWN)

    def test_other_exceptions_propagate(self):
        def bug():
            raise ZeroDivisionError("実装のバグ")

        with self.assertRaises(ZeroDivisionError):
            call_remote(bug)


class RetryDecisionTest(unittest.TestCase):
    def test_success_is_never_retried(self):
        r = CallResult(Outcome.SUCCESS, "v")
        self.assertFalse(r.is_safe_to_retry(idempotent=True))
        self.assertFalse(r.is_safe_to_retry(idempotent=False))

    def test_explicit_failure_is_always_retryable(self):
        r = CallResult(Outcome.FAILED)
        self.assertTrue(r.is_safe_to_retry(idempotent=True))
        self.assertTrue(r.is_safe_to_retry(idempotent=False))

    def test_unknown_is_retryable_only_when_idempotent(self):
        r = CallResult(Outcome.UNKNOWN)
        self.assertTrue(r.is_safe_to_retry(idempotent=True))
        self.assertFalse(
            r.is_safe_to_retry(idempotent=False),
            "冪等でない操作を UNKNOWN で再試行すると二重実行になる",
        )


class TwoGeneralsTest(unittest.TestCase):
    def test_side_effect_happens_even_when_response_is_lost(self):
        """成功したのに timeout する。これが区別できない状態。"""
        service = UnreliableService()
        with self.assertRaises(RemoteTimeout):
            service.submit("req-1", lose_response=True)

        self.assertEqual(
            service.applied, ["req-1"], "応答は失われたが、副作用は起きている"
        )

    def test_naive_retry_causes_duplicate(self):
        """冪等でない操作を UNKNOWN で再試行すると、副作用が 2 回起きる。"""
        service = UnreliableService()

        result = call_remote(lambda: service.submit("req-1", lose_response=True))
        self.assertEqual(result.outcome, Outcome.UNKNOWN)

        # 冪等でないのに再試行してしまった場合
        service.submit("req-1")

        self.assertEqual(
            service.applied, ["req-1", "req-1"], "二重に適用されてしまった"
        )

    def test_idempotent_retry_is_safe(self):
        """冪等なら、何回再試行しても副作用は 1 回。"""
        service = UnreliableService()

        with self.assertRaises(RemoteTimeout):
            service.submit_idempotent("req-1", lose_response=True)

        for _ in range(5):
            service.submit_idempotent("req-1")

        self.assertEqual(service.applied, ["req-1"], "副作用は 1 回だけであるべき")


if __name__ == "__main__":
    unittest.main()
