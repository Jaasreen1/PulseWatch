"""Export PulseWatch monitoring history to CSV for spreadsheet analysis."""

from __future__ import annotations

import csv
import json
from pathlib import Path

FIELDS = ("checked_at", "url", "up", "status_code", "latency_ms", "error")


def export_csv(source: Path, destination: Path) -> int:
    """Convert JSONL records to a CSV file; fail on invalid records."""
    rows = []
    with source.open(encoding="utf-8") as stream:
        for number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {number}") from exc
            if not isinstance(row, dict) or not isinstance(row.get("url"), str) or not isinstance(row.get("up"), bool):
                raise ValueError(f"Invalid monitoring record at line {number}")
            rows.append({field: row.get(field) for field in FIELDS})
    with destination.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=FIELDS)
        writer.writeheader()
        for row in rows:
            # Reduce spreadsheet formula injection risk for attacker-controlled values.
            safe = {}
            for key, value in row.items():
                if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
                    value = "'" + value
                safe[key] = value
            writer.writerow(safe)
    return len(rows)
