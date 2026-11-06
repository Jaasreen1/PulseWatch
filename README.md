# PulseWatch

**Minimal HTTPS uptime monitoring CLI built with Python's standard library.**

PulseWatch checks endpoints, records HTTP status and latency, outputs machine-readable JSON, and exits with a nonzero status when a check fails. Useful as a portfolio demonstration of Python, networking, automated testing and CI.

## Features

- HTTPS endpoint checks with configurable timeout (up to 30 seconds)
- Response-time measurement and UTC timestamps
- JSON Lines history output for later analysis
- Historical uptime and latency summaries with `--summary`
- Continuous monitoring with `--watch`, adjustable intervals and console alerts on outages/recovery
- Exit codes suitable for scripts and scheduled checks
- Unit tests with mocked network responses
- GitHub Actions test matrix for Python 3.11, 3.12 and 3.13
- No third-party dependencies or API keys

## Dashboard

Open [`dashboard.html`](./dashboard.html) in a modern browser. Click **Load demo** for synthetic example data, or import a JSONL file created by the CLI using `--output history.jsonl`. The dashboard runs entirely in your browser; imported data is not uploaded to a server. The dashboard is a history viewer, not a live polling service.

## Quick start

Requires Python 3.11+.

```bash
python pulsewatch.py https://example.com
python pulsewatch.py https://example.com https://www.python.org --timeout 8 --output history.jsonl
python pulsewatch.py --summary history.jsonl
python pulsewatch.py https://example.com --watch --interval 60 --alert-after 2 --output history.jsonl
python pulsewatch.py https://example.com --watch --interval 5 --cycles 3
```

Example output (illustrative):

```json
{"url":"https://example.com","checked_at":"2026-11-06T12:00:00+00:00","up":true,"status_code":200,"latency_ms":124.5,"error":null}
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Watch mode and alerts

Run with `--watch` to check endpoints repeatedly (default: every 60 seconds) until you press **Ctrl+C**. Use `--cycles N` for a finite run. The minimum interval is 5 seconds. The program prints a **DOWN** alert once after two consecutive failures by default (`--alert-after 2`) and a **RECOVERED** alert after the endpoint responds successfully again. These are **console messages only**: no email, SMS, or webhook is sent. Alerts reset when the process restarts; there is no background service. Use `--output history.jsonl` to persist results for the dashboard.

## How it works

1. Validate the user-provided HTTPS URL.
2. Send a GET request with TLS certificate verification.
3. Do not follow redirects automatically.
4. Record status, elapsed time and a sanitized error category.
5. Emit JSON and optionally append results to a local JSONL file.

An HTTP 2xx or 3xx response is considered up; other statuses and network errors are considered down. Redirects are **not** followed. No response body is downloaded intentionally.

## Safety and limitations

- **Only monitor endpoints you own or are explicitly authorized to test.**
- Private, loopback and reserved IP **literals** are rejected by default. **Hostname DNS resolution is not screened** for private IP addresses, so this is **not safe for untrusted URL submission** or deployment as a public web service.
- HTTPS port 443 only; embedded URL credentials and fragments are rejected.
- Query strings can contain secrets and are included in JSON output. Use clean monitoring URLs without tokens.
- By default, each invocation performs one check; `--watch` runs recurring checks only while the process remains active.
- The included dashboard is a local history viewer, not a live monitoring service. No alert delivery, persistent database or time-weighted uptime SLA calculation yet.
- Tests use mocks; the CI workflow does not prove availability of live external websites.

## Roadmap

- [x] Add a local HTML dashboard for JSONL history.
- [x] Add configurable consecutive-failure thresholds and console alerts.
- [ ] Add opt-in external notifications (email or webhook).
- [ ] Add DNS/IP validation for a secure hosted mode.
- [x] Add sample-based uptime and latency statistics from JSONL history.
- [ ] Add CSV export.

## License

No license has been granted yet. All rights reserved unless a license is added.

---
Created as a practical software engineering portfolio project.
