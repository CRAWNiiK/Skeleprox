import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import main


class ProxyCheckerTests(unittest.TestCase):
    def test_parse_proxy_line_uses_first_token(self):
        self.assertEqual(main.parse_proxy_line("1.2.3.4:8080 extra"), "1.2.3.4:8080")
        self.assertEqual(main.parse_proxy_line("   "), "")

    def test_extract_ip_accepts_ipv4_and_ipv6(self):
        self.assertEqual(main.extract_ip("Address: 203.0.113.10"), "203.0.113.10")
        self.assertEqual(main.extract_ip("[2001:db8::1]"), "2001:db8::1")
        self.assertIsNone(main.extract_ip("not an address"))

    def test_proxy_host_normalizes_ipv6(self):
        self.assertEqual(main.proxy_host("[2001:0DB8:0:0:0:0:0:1]:8080"), "2001:db8::1")

    def test_load_proxies_deduplicates_without_reordering(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "proxies.txt"
            source.write_text("1.2.3.4:80\n\n1.2.3.4:80 note\n5.6.7.8:8080\n")
            self.assertEqual(main.load_proxies(str(source)), ["1.2.3.4:80", "5.6.7.8:8080"])

    def test_check_proxy_reuses_expected_proxy_identity(self):
        response = Mock(text="203.0.113.10\n")
        session = Mock()
        session.get.return_value = response
        with patch.object(main, "get_session", return_value=session), patch.object(
            main, "URLS", ["https://example.test/ip"]
        ):
            self.assertEqual(main.check_proxy("203.0.113.10:8080", "http", 1), ("203.0.113.10:8080", True))
        session.cookies.clear.assert_called_once()
        session.get.assert_called_once()


if __name__ == "__main__":
    unittest.main()
