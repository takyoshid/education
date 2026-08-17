import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from learning_hub.models import Session
from learning_hub.storage import JsonSessionRepository


class RepositoryTest(unittest.TestCase):
    def test_missing_file_is_empty(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = JsonSessionRepository(Path(directory) / "data.json")
            self.assertEqual(repository.load(), [])

    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = JsonSessionRepository(Path(directory) / "data.json")
            original = [Session(datetime.now(timezone.utc), 30, "SQL", "JOIN")]
            repository.save(original)
            self.assertEqual(repository.load(), original)
            raw = json.loads(repository.path.read_text(encoding="utf-8"))
            self.assertEqual(raw["schema_version"], 1)

    def test_unknown_schema_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.json"
            path.write_text('{"schema_version": 99, "sessions": []}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "schema"):
                JsonSessionRepository(path).load()


if __name__ == "__main__":
    unittest.main()
