import sys
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from inventory import Inventory, reserve_many, reserve_safe  # noqa: E402


class ReserveSafeTest(unittest.TestCase):
    def test_single_thread_basic(self):
        inventory = Inventory(stock=2)
        self.assertTrue(reserve_safe(inventory))
        self.assertTrue(reserve_safe(inventory))
        self.assertFalse(reserve_safe(inventory))
        self.assertEqual(inventory.stock, 0)

    def test_never_oversells_under_contention(self):
        """在庫1に対して32スレッドが殺到しても、成功は1件だけ。

        並行バグは1回の実行では出ないことがあるため、繰り返し試行する。
        """
        for _ in range(50):
            inventory = Inventory(stock=1)
            with ThreadPoolExecutor(max_workers=32) as pool:
                results = list(pool.map(lambda _: reserve_safe(inventory), range(32)))

            self.assertEqual(sum(results), 1, "成功した予約は1件でなければならない")
            self.assertEqual(inventory.stock, 0)
            self.assertGreaterEqual(inventory.stock, 0, "在庫が負になった")

    def test_success_count_matches_stock_decrease(self):
        """不変条件: True を返した回数 == 減った在庫数"""
        initial = 50
        inventory = Inventory(stock=initial)
        attempts = 200

        with ThreadPoolExecutor(max_workers=16) as pool:
            results = list(pool.map(lambda _: reserve_safe(inventory), range(attempts)))

        succeeded = sum(results)
        self.assertEqual(succeeded, initial)
        self.assertEqual(inventory.stock, 0)
        self.assertEqual(inventory.reserved_count, initial)


class ReserveManyTest(unittest.TestCase):
    def test_rejects_invalid_count(self):
        inventory = Inventory(stock=10)
        for bad in (0, -1):
            with self.assertRaises(ValueError):
                reserve_many(inventory, bad)

    def test_all_or_nothing(self):
        inventory = Inventory(stock=3)
        self.assertEqual(reserve_many(inventory, 5), 0)
        self.assertEqual(inventory.stock, 3, "確保できないなら在庫を変えてはいけない")

        self.assertEqual(reserve_many(inventory, 3), 3)
        self.assertEqual(inventory.stock, 0)

    def test_concurrent_bulk_reservations_never_oversell(self):
        """合計要求が在庫を超える一括予約を同時に流す"""
        for _ in range(30):
            inventory = Inventory(stock=10)
            with ThreadPoolExecutor(max_workers=8) as pool:
                results = list(pool.map(lambda _: reserve_many(inventory, 4), range(8)))

            self.assertGreaterEqual(inventory.stock, 0, "在庫が負になった")
            self.assertEqual(sum(results), 10 - inventory.stock)
            # 4個ずつなので、成功は0か4の倍数
            for r in results:
                self.assertIn(r, (0, 4))


if __name__ == "__main__":
    unittest.main()
