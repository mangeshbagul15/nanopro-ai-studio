"""
Regression test for the Neon snapshot loop.

A state that changes during the settle window must still be uploaded. The old
loop recorded the settled state as its baseline without uploading it, so a
burst of two quick writes followed by inactivity was never snapshotted and was
lost on the next container restart.
"""
import unittest
from unittest import mock

from app.core import dm_persistence as persistence


class TestSnapshotLoop(unittest.TestCase):

    def _run_loop(self, states):
        index = {"i": 0}
        uploads = []
        waits = {"n": 0}

        def state_signature():
            i = min(index["i"], len(states) - 1)
            index["i"] += 1
            return states[i]

        def fake_wait(_timeout):
            waits["n"] += 1
            if waits["n"] >= 6:
                persistence._stop.set()
            return False

        def fake_snapshot():
            uploads.append({"status": "ok"})
            return {"status": "ok"}

        with mock.patch.object(persistence, "_state_signature", state_signature), \
                mock.patch.object(persistence, "_files_signature", lambda: None), \
                mock.patch.object(persistence, "snapshot_now", fake_snapshot), \
                mock.patch.object(persistence, "_last_signature", ("baseline", None)), \
                mock.patch.object(persistence._stop, "wait", fake_wait):
            persistence._stop.clear()
            persistence._loop()
        return uploads

    def test_change_during_settle_is_still_uploaded(self):
        uploads = self._run_loop(["state_a", "state_b", "state_b", "state_b", "state_b"])
        self.assertEqual(len(uploads), 1)

    def test_no_change_means_no_upload(self):
        uploads = self._run_loop(["baseline", "baseline", "baseline", "baseline", "baseline"])
        self.assertEqual(uploads, [])


if __name__ == "__main__":
    unittest.main()
