import unittest
from datetime import datetime, timezone

from monitor import monitor
from pulsewatch import CheckResult


def result(up):
    return CheckResult("https://example.com", datetime.now(timezone.utc).isoformat(),
                       up, 200 if up else 503, 15.0, None if up else "HTTP 503")


class TestMonitoring(unittest.TestCase):
    def test_down_alert_once_and_recovery(self):
        values = iter([False, False, False, True])
        messages = []
        monitor(["https://example.com"], interval=5, cycles=4, alert_after=2,
                check_fn=lambda url, timeout: result(next(values)),
                sleep_fn=lambda seconds: None, emit=messages.append)
        alerts = [message for message in messages if message.startswith("ALERT")]
        self.assertEqual(len(alerts), 2)
        self.assertIn("ALERT DOWN", alerts[0])
        self.assertIn("ALERT RECOVERED", alerts[1])

    def test_transient_failure_no_alert(self):
        values = iter([False, True])
        messages = []
        monitor(["https://example.com"], interval=5, cycles=2,
                check_fn=lambda url, timeout: result(next(values)),
                sleep_fn=lambda seconds: None, emit=messages.append)
        self.assertFalse(any(x.startswith("ALERT") for x in messages))

    def test_invalid_settings(self):
        for kwargs in ({"interval": 1}, {"cycles": -1}, {"alert_after": 0},
                       {"timeout": 0}):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    monitor(["https://example.com"], **kwargs)


if __name__ == "__main__":
    unittest.main()
