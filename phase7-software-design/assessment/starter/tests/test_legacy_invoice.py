import unittest

import legacy_invoice as legacy


class LegacyInvoiceTest(unittest.TestCase):
    def setUp(self):
        legacy.INVOICES.clear()
        legacy.EVENTS.clear()

    def test_existing_discount_behavior(self):
        invoice = legacy.create_invoice("1", "alice", [{"price": 100, "quantity": 2}], 0.1)
        self.assertEqual(invoice["total"], 180)
        self.assertEqual(legacy.EVENTS[-1], ("invoice.created", "1", 180))

    def test_refund_cannot_exceed_paid_total(self):
        legacy.create_invoice("1", "alice", [{"price": 100, "quantity": 1}], 0.2)
        legacy.refund("1", 50)
        with self.assertRaises(ValueError):
            legacy.refund("1", 31)


if __name__ == "__main__":
    unittest.main()
