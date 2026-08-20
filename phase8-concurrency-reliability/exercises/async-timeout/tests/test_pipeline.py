import asyncio
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pipeline import TaskFailed, fetch_all, run_with_cleanup  # noqa: E402


def make_fetcher(value, *, delay=0.0, fail=False, started=None, finished=None):
    async def fetcher():
        if started is not None:
            started.append(value)
        try:
            await asyncio.sleep(delay)
            if fail:
                raise ValueError(f"{value} で失敗")
            return value
        finally:
            if finished is not None:
                finished.append(value)

    return fetcher


class FetchAllTest(unittest.IsolatedAsyncioTestCase):
    async def test_returns_results_in_order(self):
        # わざと逆順に遅延を付ける。完了順ではなく引数順で返るべき。
        fetchers = [
            make_fetcher("a", delay=0.03),
            make_fetcher("b", delay=0.02),
            make_fetcher("c", delay=0.01),
        ]
        result = await fetch_all(fetchers, limit=3, timeout=1.0)
        self.assertEqual(result, ["a", "b", "c"])

    async def test_respects_concurrency_limit(self):
        running = 0
        peak = 0

        def make_tracked():
            async def fetcher():
                nonlocal running, peak
                running += 1
                peak = max(peak, running)
                try:
                    await asyncio.sleep(0.02)
                    return "x"
                finally:
                    running -= 1

            return fetcher

        await fetch_all([make_tracked() for _ in range(12)], limit=3, timeout=2.0)
        self.assertLessEqual(peak, 3, f"同時実行数が limit を超えた: {peak}")
        self.assertGreater(peak, 1, "並行に実行されていない")

    async def test_cancels_siblings_on_failure(self):
        started: list[str] = []
        finished: list[str] = []

        fetchers = [
            make_fetcher("fails", delay=0.01, fail=True, started=started, finished=finished),
            make_fetcher("slow1", delay=5.0, started=started, finished=finished),
            make_fetcher("slow2", delay=5.0, started=started, finished=finished),
        ]

        with self.assertRaises(TaskFailed) as ctx:
            await fetch_all(fetchers, limit=3, timeout=2.0)

        # 5秒待つタスクが2つあるが、取り消されるので即座に戻ってくるはず
        self.assertEqual(len(started), 3)
        self.assertEqual(
            len(finished), 3, "取消された兄弟タスクも finally を通るべき"
        )
        # 元の例外が残っている
        self.assertIsNotNone(ctx.exception.__cause__)

    async def test_cancellation_is_fast(self):
        """兄弟タスクが本当に取り消されているか(待たされていないか)を計測する"""
        fetchers = [
            make_fetcher("fails", delay=0.01, fail=True),
            make_fetcher("slow", delay=10.0),
        ]

        loop = asyncio.get_running_loop()
        started_at = loop.time()
        with self.assertRaises(TaskFailed):
            await fetch_all(fetchers, limit=2, timeout=30.0)
        elapsed = loop.time() - started_at

        self.assertLess(elapsed, 1.0, "兄弟タスクの完了を待ってしまっている")

    async def test_timeout(self):
        fetchers = [make_fetcher("slow", delay=5.0)]
        with self.assertRaises(TimeoutError):
            await fetch_all(fetchers, limit=1, timeout=0.05)

    async def test_semaphore_is_released_on_cancellation(self):
        """取消後も semaphore が枯渇していないことを確認する。

        1回目で取消が起きた後、2回目が正常に完走できれば漏れていない。
        """
        failing = [
            make_fetcher("fails", delay=0.01, fail=True),
            make_fetcher("slow", delay=5.0),
            make_fetcher("slow2", delay=5.0),
        ]
        with self.assertRaises(TaskFailed):
            await fetch_all(failing, limit=2, timeout=2.0)

        ok = [make_fetcher(f"v{i}", delay=0.01) for i in range(6)]
        result = await asyncio.wait_for(fetch_all(ok, limit=2, timeout=2.0), timeout=3.0)
        self.assertEqual(len(result), 6)

    async def test_rejects_invalid_limit(self):
        with self.assertRaises(ValueError):
            await fetch_all([make_fetcher("a")], limit=0, timeout=1.0)


class RunWithCleanupTest(unittest.IsolatedAsyncioTestCase):
    async def test_cleanup_runs_on_success(self):
        calls: list[str] = []

        async def body():
            return "done"

        async def cleanup():
            calls.append("cleanup")

        result = await run_with_cleanup(body, cleanup, timeout=1.0)
        self.assertEqual(result, "done")
        self.assertEqual(calls, ["cleanup"])

    async def test_cleanup_runs_on_failure(self):
        calls: list[str] = []

        async def body():
            raise ValueError("失敗")

        async def cleanup():
            calls.append("cleanup")

        with self.assertRaises(ValueError):
            await run_with_cleanup(body, cleanup, timeout=1.0)
        self.assertEqual(calls, ["cleanup"])

    async def test_cleanup_runs_on_timeout(self):
        calls: list[str] = []

        async def body():
            await asyncio.sleep(5.0)
            return "never"

        async def cleanup():
            calls.append("cleanup")

        with self.assertRaises(TimeoutError):
            await run_with_cleanup(body, cleanup, timeout=0.05)
        self.assertEqual(calls, ["cleanup"], "timeout 時も cleanup が必要")

    async def test_cleanup_runs_on_external_cancellation(self):
        calls: list[str] = []

        async def body():
            await asyncio.sleep(5.0)
            return "never"

        async def cleanup():
            calls.append("cleanup")

        task = asyncio.create_task(run_with_cleanup(body, cleanup, timeout=10.0))
        await asyncio.sleep(0.02)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task

        self.assertEqual(calls, ["cleanup"], "外部から取消されても cleanup が必要")


if __name__ == "__main__":
    unittest.main()
