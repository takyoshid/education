import sqlite3
import sys
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from orders import SCHEMA, ConflictError, OrderService  # noqa: E402


class IdempotencyTestCase(unittest.TestCase):
    def setUp(self):
        # ファイルベースの SQLite を使う。複数スレッドから別々の接続で
        # 同じ DB を開くため、インメモリでは共有できない。
        self._tmpdir = tempfile.TemporaryDirectory()
        self.db_path = str(Path(self._tmpdir.name) / "test.db")

        def conn_factory():
            conn = sqlite3.connect(self.db_path, timeout=10)
            conn.execute("PRAGMA busy_timeout = 10000")
            return conn

        self.conn_factory = conn_factory

        conn = conn_factory()
        conn.executescript(SCHEMA)
        conn.commit()
        conn.close()

        self.service = OrderService(conn_factory=conn_factory)

    def tearDown(self):
        self._tmpdir.cleanup()


class SequentialTest(IdempotencyTestCase):
    def test_creates_order(self):
        result = self.service.create_order("key-1", {"user_id": "u1", "amount": 100})
        self.assertIn("order_id", result)
        self.assertEqual(self.service.count_orders(), 1)

    def test_same_key_same_payload_is_idempotent(self):
        payload = {"user_id": "u1", "amount": 100}
        first = self.service.create_order("key-1", payload)
        second = self.service.create_order("key-1", payload)
        third = self.service.create_order("key-1", payload)

        self.assertEqual(first, second)
        self.assertEqual(second, third)
        self.assertEqual(self.service.count_orders(), 1, "副作用は1回だけ")

    def test_same_key_different_payload_is_rejected(self):
        self.service.create_order("key-1", {"user_id": "u1", "amount": 100})
        with self.assertRaises(ConflictError):
            self.service.create_order("key-1", {"user_id": "u1", "amount": 999})
        self.assertEqual(self.service.count_orders(), 1)

    def test_payload_key_order_does_not_matter(self):
        """辞書の順序が違っても同じ内容として扱う"""
        a = self.service.create_order("key-1", {"user_id": "u1", "amount": 100})
        b = self.service.create_order("key-1", {"amount": 100, "user_id": "u1"})
        self.assertEqual(a, b)
        self.assertEqual(self.service.count_orders(), 1)

    def test_different_keys_create_different_orders(self):
        payload = {"user_id": "u1", "amount": 100}
        self.service.create_order("key-1", payload)
        self.service.create_order("key-2", payload)
        self.assertEqual(self.service.count_orders(), 2)

    def test_rejects_empty_key(self):
        with self.assertRaises(ValueError):
            self.service.create_order("", {"user_id": "u1", "amount": 100})


class ConcurrentTest(IdempotencyTestCase):
    def test_twenty_threads_same_key_create_one_order(self):
        """同じ key を20スレッドから同時に送っても副作用は1回。

        全クライアントは「成功した結果」か ConflictError のどちらかを得る。
        どちらであっても、注文が2件できてはいけない。
        """
        payload = {"user_id": "u1", "amount": 100}

        def call():
            try:
                return ("ok", self.service.create_order("key-1", payload))
            except ConflictError as exc:
                return ("conflict", str(exc))

        with ThreadPoolExecutor(max_workers=20) as pool:
            results = list(pool.map(lambda _: call(), range(20)))

        self.assertEqual(self.service.count_orders(), 1, "注文は1件だけであるべき")

        successes = [r for status, r in results if status == "ok"]
        self.assertGreater(len(successes), 0, "少なくとも1つは成功すべき")

        # 成功したものは全部同じ order_id を返している
        order_ids = {r["order_id"] for r in successes}
        self.assertEqual(len(order_ids), 1, f"複数の order_id が返された: {order_ids}")

    def test_concurrent_different_keys_all_succeed(self):
        payload = {"user_id": "u1", "amount": 100}

        with ThreadPoolExecutor(max_workers=10) as pool:
            list(pool.map(
                lambda i: self.service.create_order(f"key-{i}", payload), range(20)
            ))

        self.assertEqual(self.service.count_orders(), 20)

    def test_repeated_runs_are_stable(self):
        """並行テストは1回通っただけでは証拠にならない。繰り返して安定を確認する。"""
        payload = {"user_id": "u1", "amount": 50}

        for round_no in range(10):
            key = f"round-{round_no}"

            def call():
                try:
                    self.service.create_order(key, payload)
                except ConflictError:
                    pass

            with ThreadPoolExecutor(max_workers=8) as pool:
                list(pool.map(lambda _: call(), range(8)))

        self.assertEqual(self.service.count_orders(), 10, "各ラウンド1件ずつのはず")


if __name__ == "__main__":
    unittest.main()
