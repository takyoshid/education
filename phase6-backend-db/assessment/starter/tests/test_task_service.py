import unittest

from task_service import ConflictError, NotFoundError, TaskService


class TaskServiceTest(unittest.TestCase):
    def setUp(self):
        self.service = TaskService()

    def test_idempotent_create_returns_same_task(self):
        first = self.service.create("alice", "learn SQL", "key-1")
        second = self.service.create("alice", "learn SQL", "key-1")
        self.assertEqual(first, second)
        self.assertEqual(len(self.service.tasks), 1)

    def test_key_reuse_with_different_payload_conflicts(self):
        self.service.create("alice", "one", "key-1")
        with self.assertRaises(ConflictError):
            self.service.create("alice", "two", "key-1")

    def test_other_owner_cannot_observe_task(self):
        task = self.service.create("alice", "private", "key-1")
        with self.assertRaises(NotFoundError):
            self.service.get("bob", task.task_id)

    def test_stale_update_conflicts(self):
        task = self.service.create("alice", "v1", "key-1")
        updated = self.service.update("alice", task.task_id, "v2", expected_version=1)
        self.assertEqual(updated.version, 2)
        with self.assertRaises(ConflictError):
            self.service.update("alice", task.task_id, "lost", expected_version=1)

    def test_cursor_pagination_is_stable(self):
        created = [self.service.create("alice", str(index), f"k-{index}") for index in range(5)]
        self.service.create("bob", "hidden", "bob-key")
        page = self.service.list_for("alice", limit=2, after_id=created[1].task_id)
        self.assertEqual([task.task_id for task in page], [created[2].task_id, created[3].task_id])


if __name__ == "__main__":
    unittest.main()
