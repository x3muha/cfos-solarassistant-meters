import json
import sys
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import TestCase, main


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "proxy"))
from solarassistant_metrics_proxy import MetricsCache, make_handler  # noqa: E402


METRICS = [
    {
        "topic": "total/grid_power",
        "group": "Status",
        "name": "Grid power",
        "value": -123,
        "unit": "W",
    },
    {
        "topic": "total/grid_voltage",
        "group": "Status",
        "name": "Grid voltage",
        "value": 231.5,
        "unit": "V",
    },
]


class FakeSolarAssistant(BaseHTTPRequestHandler):
    requests = 0

    def do_GET(self):  # noqa: N802 - BaseHTTPRequestHandler API
        type(self).requests += 1
        if self.path != "/api/v1/metrics":
            self.send_error(404)
            return
        body = json.dumps(METRICS).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format_string, *args):
        return


class ProxyTest(TestCase):
    @classmethod
    def setUpClass(cls):
        FakeSolarAssistant.requests = 0
        cls.upstream = ThreadingHTTPServer(("127.0.0.1", 0), FakeSolarAssistant)
        cls.upstream_thread = threading.Thread(
            target=cls.upstream.serve_forever, daemon=True
        )
        cls.upstream_thread.start()

        upstream_url = f"http://127.0.0.1:{cls.upstream.server_port}"
        cache = MetricsCache(upstream_url, "admin", "secret", 30, 60, 2)
        cls.proxy = ThreadingHTTPServer(("127.0.0.1", 0), make_handler(cache))
        cls.proxy_thread = threading.Thread(target=cls.proxy.serve_forever, daemon=True)
        cls.proxy_thread.start()
        cls.proxy_url = f"http://127.0.0.1:{cls.proxy.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.proxy.shutdown()
        cls.proxy.server_close()
        cls.upstream.shutdown()
        cls.upstream.server_close()

    def test_plain_value_and_cache(self):
        with urllib.request.urlopen(
            self.proxy_url + "/api/v1/metrics?topic=total/grid_power&value=1"
        ) as response:
            self.assertEqual(response.read().decode().strip(), "-123")

        with urllib.request.urlopen(
            self.proxy_url + "/api/v1/metrics?topic=total/grid_voltage&value=1"
        ) as response:
            self.assertEqual(response.read().decode().strip(), "231.5")

        self.assertEqual(FakeSolarAssistant.requests, 1)

    def test_glob_and_health(self):
        with urllib.request.urlopen(
            self.proxy_url + "/api/v1/metrics?topic=total/grid_*"
        ) as response:
            payload = json.load(response)
        self.assertEqual([item["topic"] for item in payload], [
            "total/grid_power",
            "total/grid_voltage",
        ])

        with urllib.request.urlopen(self.proxy_url + "/health") as response:
            health = json.load(response)
        self.assertEqual(health["status"], "ok")
        self.assertEqual(health["topics"], 2)


if __name__ == "__main__":
    main()
