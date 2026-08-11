#!/usr/bin/env python3
"""Small caching proxy for SolarAssistant's local metrics REST API."""

from __future__ import annotations

import base64
import fnmatch
import json
import os
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


class UpstreamError(RuntimeError):
    pass


class MetricsCache:
    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        ttl_seconds: float,
        max_stale_seconds: float,
        timeout_seconds: float,
    ) -> None:
        parsed = urllib.parse.urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("SOLARASSISTANT_URL must be an HTTP or HTTPS URL")
        if parsed.username or parsed.password:
            raise ValueError("put credentials in the dedicated environment variables")

        self.metrics_url = base_url.rstrip("/") + "/api/v1/metrics"
        self.username = username
        self.password = password
        self.ttl_seconds = ttl_seconds
        self.max_stale_seconds = max_stale_seconds
        self.timeout_seconds = timeout_seconds
        self._metrics: dict[str, dict[str, Any]] = {}
        self._updated_monotonic = 0.0
        self._lock = threading.Lock()

    def _fetch(self) -> dict[str, dict[str, Any]]:
        credentials = base64.b64encode(
            f"{self.username}:{self.password}".encode("utf-8")
        ).decode("ascii")
        request = urllib.request.Request(
            self.metrics_url,
            headers={
                "Accept": "application/json",
                "Authorization": f"Basic {credentials}",
                "User-Agent": "cfos-solarassistant-metrics-proxy/1.0",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                if response.status != 200:
                    raise UpstreamError(f"upstream returned HTTP {response.status}")
                payload = json.load(response)
        except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
            raise UpstreamError("cannot read SolarAssistant metrics") from exc

        if not isinstance(payload, list):
            raise UpstreamError("SolarAssistant metrics response is not an array")

        metrics: dict[str, dict[str, Any]] = {}
        for record in payload:
            if not isinstance(record, dict) or not isinstance(record.get("topic"), str):
                continue
            metrics[record["topic"]] = record
        if not metrics:
            raise UpstreamError("SolarAssistant returned no usable metrics")
        return metrics

    def snapshot(self) -> tuple[dict[str, dict[str, Any]], float]:
        now = time.monotonic()
        with self._lock:
            age = now - self._updated_monotonic
            if self._metrics and age <= self.ttl_seconds:
                return self._metrics.copy(), age

            try:
                self._metrics = self._fetch()
                self._updated_monotonic = time.monotonic()
                return self._metrics.copy(), 0.0
            except UpstreamError:
                age = time.monotonic() - self._updated_monotonic
                if self._metrics and age <= self.max_stale_seconds:
                    return self._metrics.copy(), age
                raise


def make_handler(cache: MetricsCache) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "cFosSolarAssistantProxy/1.0"

        def _json_response(self, status: int, payload: Any) -> None:
            body = json.dumps(payload, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def _text_response(self, status: int, value: Any) -> None:
            if isinstance(value, bool):
                text = "true" if value else "false"
            else:
                text = str(value)
            body = (text + "\n").encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self) -> None:  # noqa: N802 - BaseHTTPRequestHandler API
            parsed = urllib.parse.urlsplit(self.path)
            if parsed.path not in {"/health", "/api/v1/metrics"}:
                self._json_response(404, {"error": "not found"})
                return

            try:
                metrics, age = cache.snapshot()
            except UpstreamError:
                self._json_response(503, {"error": "SolarAssistant unavailable"})
                return

            if parsed.path == "/health":
                self._json_response(
                    200,
                    {
                        "status": "ok",
                        "topics": len(metrics),
                        "cache_age_seconds": round(age, 3),
                    },
                )
                return

            query = urllib.parse.parse_qs(parsed.query, keep_blank_values=True)
            topic_filter = query.get("topic", ["*"])[0]
            records = [
                record
                for topic, record in sorted(metrics.items())
                if fnmatch.fnmatchcase(topic, topic_filter)
            ]

            if query.get("value", ["0"])[0] == "1":
                if len(records) != 1 or "value" not in records[0]:
                    self._json_response(
                        404,
                        {"error": "topic must resolve to exactly one metric"},
                    )
                    return
                self._text_response(200, records[0]["value"])
                return

            self._json_response(200, records)

        def log_message(self, format_string: str, *args: Any) -> None:
            # Requests only come from localhost; avoid noisy per-field access logs.
            return

    return Handler


def positive_float(name: str, default: str) -> float:
    value = float(os.environ.get(name, default))
    if value <= 0:
        raise ValueError(f"{name} must be positive")
    return value


def main() -> None:
    base_url = os.environ["SOLARASSISTANT_URL"]
    username = os.environ.get("SOLARASSISTANT_USERNAME", "admin")
    password = os.environ["SOLARASSISTANT_PASSWORD"]
    listen_host = os.environ.get("LISTEN_HOST", "127.0.0.1")
    listen_port = int(os.environ.get("LISTEN_PORT", "9180"))

    cache = MetricsCache(
        base_url=base_url,
        username=username,
        password=password,
        ttl_seconds=positive_float("CACHE_TTL_SECONDS", "1.0"),
        max_stale_seconds=positive_float("MAX_STALE_SECONDS", "5.0"),
        timeout_seconds=positive_float("UPSTREAM_TIMEOUT_SECONDS", "3.0"),
    )
    cache.snapshot()

    server = ThreadingHTTPServer((listen_host, listen_port), make_handler(cache))
    server.daemon_threads = True
    server.serve_forever()


if __name__ == "__main__":
    main()
