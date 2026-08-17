import sys
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from cache import Cache, CountingLoader, FakeClock  # noqa: E402

CONCURRENCY = 64


class BasicTest(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.cache = Cache(self.clock)

    def test_set_and_get(self):
        self.cache.set("k", "v", ttl=10)
        self.assertEqual(self.cache.get("k"), "v")

    def test_expires_after_ttl(self):
        self.cache.set("k", "v", ttl=10)
        self.clock.advance(9.9)
        self.assertEqual(self.cache.get("k"), "v")
        self.clock.advance(0.2)
        self.assertIsNone(self.cache.get("k"), "TTL 経過後は None")

    def test_missing_key(self):
        self.assertIsNone(self.cache.get("nope"))

    def test_rejects_non_positive_ttl(self):
        for bad in (0, -1):
            with self.assertRaises(ValueError):
                self.cache.set("k", "v", ttl=bad)


class StampedeTest(unittest.TestCase):
    """対策なしの実装で、実際に何本が DB へ流れるかを測る"""

    def _run_concurrently(self, fn) -> None:
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
            list(pool.map(lambda _: fn(), range(CONCURRENCY)))

    def test_naive_lets_many_requests_through(self):
        clock = FakeClock()
        cache = Cache(clock)
        loader = CountingLoader()
        # 全スレッドが同時にミスする状況を作る
        loader.barrier = threading.Barrier(CONCURRENCY, timeout=5)

        self._run_concurrently(
            lambda: cache.get_or_load_naive("hot", loader, ttl=10)
        )

        self.assertEqual(
            loader.calls,
            CONCURRENCY,
            "対策なしなら全リクエストが DB へ流れるはず(これが stampede)",
        )

    def test_locked_lets_exactly_one_through(self):
        clock = FakeClock()
        cache = Cache(clock)
        loader = CountingLoader()

        self._run_concurrently(
            lambda: cache.get_or_load_locked("hot", loader, ttl=10)
        )

        self.assertEqual(loader.calls, 1, f"DB へ {loader.calls} 本流れた。1 本であるべき")
        self.assertEqual(cache.get("hot"), "loaded")

    def test_locked_returns_correct_value_to_everyone(self):
        clock = FakeClock()
        cache = Cache(clock)
        loader = CountingLoader(value="the-value")

        with ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
            results = list(
                pool.map(
                    lambda _: cache.get_or_load_locked("hot", loader, ttl=10),
                    range(CONCURRENCY),
                )
            )

        self.assertEqual(set(results), {"the-value"}, "全員が正しい値を得るべき")

    def test_locked_reloads_after_expiry(self):
        clock = FakeClock()
        cache = Cache(clock)
        loader = CountingLoader()

        cache.get_or_load_locked("hot", loader, ttl=10)
        self.assertEqual(loader.calls, 1)

        clock.advance(11)
        cache.get_or_load_locked("hot", loader, ttl=10)
        self.assertEqual(loader.calls, 2, "期限切れ後は読み直すべき")

    def test_locked_does_not_block_cache_hits(self):
        """ヒット時はロックを取らないこと(取ると全体が直列化する)"""
        clock = FakeClock()
        cache = Cache(clock)
        loader = CountingLoader()

        cache.get_or_load_locked("hot", loader, ttl=100)
        self._run_concurrently(
            lambda: cache.get_or_load_locked("hot", loader, ttl=100)
        )
        self.assertEqual(loader.calls, 1)


class JitterTest(unittest.TestCase):
    def setUp(self):
        self.clock = FakeClock()
        self.cache = Cache(self.clock)

    def test_jitter_stays_within_range(self):
        lo = self.cache.set_with_jitter("a", "v", ttl=100, rand=lambda a, b: a)
        hi = self.cache.set_with_jitter("b", "v", ttl=100, rand=lambda a, b: b)
        self.assertEqual(lo, 100.0)
        self.assertEqual(hi, 120.0)

    def test_rejects_negative_ratio(self):
        with self.assertRaises(ValueError):
            self.cache.set_with_jitter("a", "v", ttl=10, jitter_ratio=-0.1)

    def test_many_keys_expire_at_different_times(self):
        """同時に作った 200 キーの期限がばらけること"""
        for i in range(200):
            self.cache.set_with_jitter(f"k{i}", "v", ttl=300)

        expiries = {entry.expires_at for entry in self.cache._entries.values()}
        self.assertGreater(len(expiries), 100, "期限が集中している(ジッターが効いていない)")


if __name__ == "__main__":
    unittest.main()
