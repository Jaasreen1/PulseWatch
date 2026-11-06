"""Periodic monitoring and state-change alerts for PulseWatch."""

from __future__ import annotations

import json
import time
from dataclasses import asdict
from pathlib import Path
from typing import Callable

from pulsewatch import CheckResult, check


def monitor(
    urls: list[str],
    *,
    interval: float = 60,
    cycles: int = 0,
    timeout: float = 5,
    alert_after: int = 2,
    output: Path | None = None,
    check_fn: Callable[[str, float], CheckResult] = check,
    sleep_fn: Callable[[float], None] = time.sleep,
    emit: Callable[[str], None] = print,
) -> None:
    """Run checks until interrupted, or for a specified number of cycles.

    Alerts are printed on transition to DOWN after alert_after consecutive
    failures and on recovery. A running process is required; no notifications
    are sent externally.
    """
    if not urls:
        raise ValueError("At least one endpoint is required")
    if interval < 5 or interval > 86400:
        raise ValueError("Interval must be between 5 and 86400 seconds")
    if cycles < 0:
        raise ValueError("Cycles must be zero (continuous) or positive")
    if alert_after < 1:
        raise ValueError("alert_after must be at least 1")
    if not 0 < timeout <= 30:
        raise ValueError("Timeout must be between 0 and 30 seconds")

    failures = {url: 0 for url in urls}
    alerted = {url: False for url in urls}
    iteration = 0
    while cycles == 0 or iteration < cycles:
        iteration += 1
        started = time.monotonic()
        for url in urls:
            result = check_fn(url, timeout)
            emit(json.dumps(asdict(result), ensure_ascii=False))
            if output is not None:
                with output.open("a", encoding="utf-8") as stream:
                    stream.write(json.dumps(asdict(result), ensure_ascii=False) + "\n")
            if result.up:
                if alerted[url]:
                    emit(f"ALERT RECOVERED: {url} is responding again")
                failures[url] = 0
                alerted[url] = False
            else:
                failures[url] += 1
                if failures[url] >= alert_after and not alerted[url]:
                    emit(f"ALERT DOWN: {url} failed {failures[url]} consecutive checks")
                    alerted[url] = True
        if cycles == 0 or iteration < cycles:
            sleep_fn(max(0.0, interval - (time.monotonic() - started)))
