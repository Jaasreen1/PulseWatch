import unittest
from unittest.mock import patch
import urllib.error

from pulsewatch import check, validate_url


class TestValidation(unittest.TestCase):
    def test_https_only(self):
        with self.assertRaises(ValueError):
            validate_url("http://example.com")
        self.assertEqual(validate_url("https://example.com/health"), "https://example.com/health")

    def test_reject_credentials(self):
        with self.assertRaises(ValueError):
            validate_url("https://user:password@example.com")

    def test_reject_private_ip(self):
        with self.assertRaises(ValueError):
            validate_url("https://127.0.0.1")
        with self.assertRaises(ValueError):
            validate_url("https://192.168.1.5")

    def test_reject_nonstandard_port(self):
        with self.assertRaises(ValueError):
            validate_url("https://example.com:8443")


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class TestCheck(unittest.TestCase):
    @patch("urllib.request.OpenerDirector.open", return_value=FakeResponse())
    def test_success(self, _open):
        result = check("https://example.com")
        self.assertTrue(result.up)
        self.assertEqual(result.status_code, 200)
        self.assertGreaterEqual(result.latency_ms, 0)

    @patch("urllib.request.OpenerDirector.open")
    def test_http_error(self, open_mock):
        open_mock.side_effect = urllib.error.HTTPError(
            "https://example.com", 503, "Service unavailable", {}, None
        )
        result = check("https://example.com")
        self.assertFalse(result.up)
        self.assertEqual(result.status_code, 503)

    def test_invalid_timeout(self):
        with self.assertRaises(ValueError):
            check("https://example.com", timeout=-1)


if __name__ == "__main__":
    unittest.main()
