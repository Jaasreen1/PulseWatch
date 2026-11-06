"""Aggregate PulseWatch JSONL history into per-endpoint statistics."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def summarize(path: Path) -> list[dict]:
    groups: dict[str, list[dict]] = defaultdict(list)
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {line_number}") from exc
            if not isinstance(item, dict) or not isinstance(item.get("url"), str) or not isinstance(item.get("up"), bool):
                raise ValueError(f"Invalid monitoring record at line {line_number}")
            groups[item["url"]].append(item)
    results = []
    for url, rows in sorted(groups.items()):
        successful = sum(row["up"] for row in rows)
        times = [row.get("latency_ms") for row in rows]
        times = [t for t in times if isinstance(t, (int, float)) and not isinstance(t, bool) and 0 <= t < float("inf")]
        results.append({
            "url": url,
            "checks": len(rows),
            "successful": successful,
            "failed": len(rows) - successful,
            "sample_uptime_pct": round(successful / len(rows) * 100, 2),
            "avg_latency_ms": round(sum(times) / len(times), 2) if times else None,
            "max_latency_ms": round(max(times), 2) if times else None,
        })
    return results
