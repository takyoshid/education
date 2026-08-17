import unittest

from scheduler import DependencyError, schedule


class SchedulerTest(unittest.TestCase):
    def test_deterministic_topological_order(self):
        result = schedule(["deploy", "build", "lint", "test"], [("test", "build"), ("deploy", "test")])
        self.assertEqual(result, ["build", "lint", "test", "deploy"])

    def test_rejects_unknown_task(self):
        with self.assertRaises(DependencyError):
            schedule(["build"], [("deploy", "build")])

    def test_rejects_self_dependency(self):
        with self.assertRaises(DependencyError):
            schedule(["build"], [("build", "build")])

    def test_cycle_message_mentions_members(self):
        with self.assertRaises(DependencyError) as caught:
            schedule(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")])
        self.assertTrue({"a", "b", "c"}.issubset(set(str(caught.exception))))

    def test_does_not_mutate_inputs(self):
        tasks = ["b", "a"]
        dependencies = [("b", "a")]
        schedule(tasks, dependencies)
        self.assertEqual(tasks, ["b", "a"])
        self.assertEqual(dependencies, [("b", "a")])


if __name__ == "__main__":
    unittest.main()
