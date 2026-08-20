import unittest
from datetime import datetime, timezone

from learning_hub.models import Session


class SessionTest(unittest.TestCase):
    def test_round_trip_and_normalization(self):
        session = Session(datetime(2026, 8, 17, tzinfo=timezone.utc), 25, " Python ", " Learned tests ", ("TDD", "tdd", " api "))
        restored = Session.from_dict(session.to_dict())
        self.assertEqual(restored, session)
        self.assertEqual(session.topic, "Python")
        self.assertEqual(session.tags, ("TDD", "api"))

    def test_rejects_naive_datetime(self):
        with self.assertRaises(ValueError):
            Session(datetime(2026, 8, 17), 25, "Python", "Learned")

    def test_rejects_invalid_minutes(self):
        for minutes in (0, 1441):
            with self.subTest(minutes=minutes), self.assertRaises(ValueError):
                Session(datetime.now(timezone.utc), minutes, "Python", "Learned")


if __name__ == "__main__":
    unittest.main()
