# PulseWatch

**Minimal HTTPS uptime monitoring CLI built with Python's standard library.**

PulseWatch checks endpoints, records HTTP status and latency, outputs machine-readable JSON, and exits with a nonzero status when a check fails. Useful as a portfolio demonstration of Python, networking, automated testing and CI.

## Features

- HTTPS endpoint checks with configurable timeout (up to 30 seconds)
- Response-time measurement and UTC timestamps
- JSON Lines history output for later analysis
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
```

Example output (illustrative):

```json
{"url":"https://example.com","checked_at":"2026-11-06T12:00:00+00:00","up":true,"status_code":200,"latency_ms":124.5,"error":null}
```

Run tests:

```bash
python -m unittest discover -s tests -v
```

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
- Each invocation performs a single check; schedule externally if you need recurring checks.
- No alert delivery, dashboards, persistent database or uptime SLA calculation yet.
- Tests use mocks; the CI workflow does not prove availability of live external websites.

## Roadmap

- [x] Add a local HTML dashboard for JSONL history.
- [ ] Add configurable alert thresholds and opt-in notifications.
- [ ] Add DNS/IP validation for a secure hosted mode.
- [ ] Add CSV export and uptime statistics.

## License

No license has been granted yet. All rights reserved unless a license is added.

---
Created as a practical software engineering portfolio project.
