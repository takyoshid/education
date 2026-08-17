import unittest
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

from bank import Account, transfer


class TransferTest(unittest.TestCase):
    def test_parallel_opposite_transfers_preserve_total(self):
        left = Account("A", Decimal("1000"))
        right = Account("B", Decimal("1000"))
        with ThreadPoolExecutor(max_workers=8) as pool:
            futures = []
            for _ in range(100):
                futures.append(pool.submit(transfer, left, right, Decimal("1")))
                futures.append(pool.submit(transfer, right, left, Decimal("1")))
            for future in futures:
                future.result(timeout=2)
        self.assertEqual(left.balance + right.balance, Decimal("2000"))
        self.assertGreaterEqual(left.balance, 0)
        self.assertGreaterEqual(right.balance, 0)

    def test_rejects_invalid_amount(self):
        with self.assertRaises(ValueError):
            transfer(Account("A", Decimal("1")), Account("B", Decimal("1")), Decimal("0"))


if __name__ == "__main__":
    unittest.main()
