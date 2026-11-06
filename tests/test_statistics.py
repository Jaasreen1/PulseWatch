import json
import tempfile
import unittest
from pathlib import Path

from statistics import summarize


class TestStatistics(unittest.TestCase):
    def write_history(self, lines):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        path = Path(temp.name) / "history.jsonl"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return path

    def test_grouped_uptime_and_latency(self):
        path = self.write_history([
            json.dumps({"url": "https://a.example", "up": True, "latency_ms": 100}),
            json.dumps({"url": "https://a.example", "up": False, "latency_ms": 300}),
            json.dumps({"url": "https://b.example", "up": True, "latency_ms": None}),
        ])
        report = summarize(path)
        self.assertEqual(len(report), 2)
        self.assertEqual(report[0]["sample_uptime_pct"], 50.0)
        self.assertEqual(report[0]["avg_latency_ms"], 200.0)
        self.assertEqual(report[0]["max_latency_ms"], 300)
        self.assertIsNone(report[1]["avg_latency_ms"])

    def test_empty_file(self):
        self.assertEqual(summarize(self.write_history([])), [])

    def test_malformed_json(self):
        with self.assertRaisesRegex(ValueError, "line 1"):
            summarize(self.write_history(["not json"]))

    def test_invalid_record(self):
        with self.assertRaisesRegex(ValueError, "line 1"):
            summarize(self.write_history(['{"url":"https://a.example","up":"yes"}']))


if __name__ == "__main__":
    unittest.main()
