import unittest

from worker import FailureKind, Message, ProcessingError, ReliableWorker


class WorkerTest(unittest.TestCase):
    def test_duplicate_is_not_processed_twice(self):
        effects = []
        worker = ReliableWorker(lambda message: effects.append(message.payload))
        message = Message("1", "send-email")
        self.assertTrue(worker.process(message))
        self.assertTrue(worker.process(message))
        self.assertEqual(effects, ["send-email"])

    def test_transient_failure_requests_redelivery(self):
        worker = ReliableWorker(lambda _: (_ for _ in ()).throw(ProcessingError(FailureKind.TRANSIENT, "timeout")))
        self.assertFalse(worker.process(Message("1", "work")))
        self.assertEqual(worker.dead_letters, [])

    def test_permanent_failure_goes_to_dead_letter(self):
        worker = ReliableWorker(lambda _: (_ for _ in ()).throw(ProcessingError(FailureKind.PERMANENT, "invalid")))
        message = Message("1", "work")
        self.assertTrue(worker.process(message))
        self.assertEqual(worker.dead_letters, [message])

    def test_shutdown_rejects_new_work(self):
        worker = ReliableWorker(lambda _: None)
        worker.shutdown()
        with self.assertRaises(RuntimeError):
            worker.process(Message("1", "work"))


if __name__ == "__main__":
    unittest.main()
