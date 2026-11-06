"""PulseWatch: safe, dependency-free uptime checks for explicitly configured endpoints."""

from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from ipaddress import ip_address
from pathlib import Path

USER_AGENT = "PulseWatch/1.0 (+portfolio uptime monitor)"


@dataclass(frozen=True)
class CheckResult:
    url: str
    checked_at: str
    up: bool
    status_code: int | None
    latency_ms: float | None
    error: str | None


def validate_url(url: str, *, allow_private: bool = False) -> str:
    """Allow only HTTPS URLs; block credentials and private/loopback IP literals."""
    parsed = urllib.parse.urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Only absolute HTTPS URLs are supported")
    if parsed.username or parsed.password or parsed.fragment:
        raise ValueError("Credentials and URL fragments are not allowed")
    if parsed.port not in (None, 443):
        raise ValueError("Only HTTPS port 443 is supported")
    if not allow_private:
        try:
            addr = ip_address(parsed.hostname)
        except ValueError:
            pass
        else:
            if not addr.is_global:
                raise ValueError("Private, loopback and reserved IPs are not allowed")
    return url


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise urllib.error.HTTPError(request.full_url, code, "Redirect not followed", headers, fp)


def check(url: str, timeout: float = 5.0) -> CheckResult:
    url = validate_url(url)
    if timeout <= 0 or timeout > 30:
        raise ValueError("Timeout must be between 0 and 30 seconds")
    started = time.perf_counter()
    status = None
    error = None
    try:
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
        opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPSHandler(context=ssl.create_default_context()))
        with opener.open(req, timeout=timeout) as response:
            status = response.status
    except urllib.error.HTTPError as exc:
        status = exc.code
        error = f"HTTP {exc.code}"
    except (urllib.error.URLError, TimeoutError, OSError, socket.timeout) as exc:
        # Do not expose potentially sensitive URLs or transport details in reports.
        error = type(exc).__name__
    elapsed = round((time.perf_counter() - started) * 1000, 2)
    return CheckResult(
        url=url, checked_at=datetime.now(timezone.utc).isoformat(),
        up=status is not None and 200 <= status < 400,
        status_code=status, latency_ms=elapsed, error=error,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Monitor HTTPS endpoints you own or are authorized to test.")
    parser.add_argument("urls", nargs="+", help="HTTPS endpoint URLs")
    parser.add_argument("--timeout", type=float, default=5.0)
    parser.add_argument("--output", type=Path, help="Append JSON Lines results to a local file")
    args = parser.parse_args(argv)
    try:
        results = [check(url, args.timeout) for url in args.urls]
    except ValueError as exc:
        parser.error(str(exc))
    for result in results:
        print(json.dumps(asdict(result), ensure_ascii=False))
    if args.output:
        with args.output.open("a", encoding="utf-8") as f:
            for result in results:
                f.write(json.dumps(asdict(result)) + "\n")
    return 0 if all(item.up for item in results) else 1


if __name__ == "__main__":
    sys.exit(main())
