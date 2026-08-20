import tempfile
import unittest
from decimal import Decimal
from pathlib import Path

from order_report import Order, atomic_write_json, load_orders, parse_order, summarize


class OrderReportTest(unittest.TestCase):
    def test_parse_trims_and_converts(self):
        order = parse_order(
            {"order_id": " A-1 ", "product": " Book ", "quantity": "2", "unit_price": "12.30"}, 2
        )
        self.assertEqual(order, Order("A-1", "Book", 2, Decimal("12.30")))

    def test_rejects_invalid_quantity(self):
        with self.assertRaisesRegex(ValueError, "quantity"):
            parse_order({"order_id": "A", "product": "Book", "quantity": "0", "unit_price": "1.00"}, 2)

    def test_summarizes_without_float_error(self):
        result = summarize([Order("1", "Pen", 3, Decimal("0.10")), Order("2", "Pen", 1, Decimal("0.20"))])
        self.assertEqual(result["Pen"], {"quantity": 4, "amount": "0.50"})

    def test_duplicate_is_reported_and_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "orders.csv"
            path.write_text(
                "order_id,product,quantity,unit_price\nA,Pen,1,1.00\nA,Book,1,2.00\n",
                encoding="utf-8",
            )
            orders, errors = load_orders(path)
        self.assertEqual(len(orders), 1)
        self.assertEqual(len(errors), 1)
        self.assertIn("3", errors[0])

    def test_atomic_write_replaces_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.json"
            path.write_text("old", encoding="utf-8")
            atomic_write_json(path, {"ok": True})
            self.assertEqual(path.read_text(encoding="utf-8"), '{\n  "ok": true\n}\n')


if __name__ == "__main__":
    unittest.main()
