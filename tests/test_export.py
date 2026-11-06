import csv
import tempfile
import unittest
from pathlib import Path

from export import export_csv


class TestCsvExport(unittest.TestCase):
    def test_export_and_formula_escape(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "history.jsonl"
            target = Path(folder) / "history.csv"
            source.write_text('{"url":"=HYPERLINK(1)","up":false,"latency_ms":12}\n', encoding="utf-8")
            self.assertEqual(export_csv(source, target), 1)
            with target.open(newline="", encoding="utf-8") as stream:
                rows = list(csv.DictReader(stream))
            self.assertEqual(rows[0]["url"], "'=HYPERLINK(1)")
            self.assertEqual(rows[0]["up"], "False")

    def test_invalid_json_does_not_create_csv(self):
        with tempfile.TemporaryDirectory() as folder:
            source = Path(folder) / "history.jsonl"
            target = Path(folder) / "history.csv"
            source.write_text("invalid\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                export_csv(source, target)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()
