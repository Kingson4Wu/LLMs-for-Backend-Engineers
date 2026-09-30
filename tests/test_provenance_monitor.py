import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/book-kit"))


class ProvenanceMonitorTests(unittest.TestCase):
    def write_fixture(self, root: Path, *, sources, baseline_sources=(), claims=()):
        (root / "evals/claims").mkdir(parents=True)
        (root / "evals/provenance.json").write_text(json.dumps({"sources": sources}), encoding="utf-8")
        (root / "evals/provenance-monitor-baseline.json").write_text(
            json.dumps({"version": 1, "sources": list(baseline_sources)}), encoding="utf-8"
        )
        (root / "evals/claims/cases.json").write_text(json.dumps({"cases": list(claims)}), encoding="utf-8")

    def test_changed_digest_and_expired_time_sensitive_review_are_advisory(self):
        from monitor_provenance import FetchResponse, monitor

        url = "https://sources.example/spec"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(
                root,
                sources=[{"url": url, "type": "specification"}],
                baseline_sources=[{"url": url, "final_url": url, "content_digest": hashlib.sha256(b"old").hexdigest()}],
                claims=[
                    {
                        "id": "freshness-case",
                        "kind": "time-sensitive",
                        "review_interval_days": 7,
                        "review": {"reviewed_at": "2026-09-01"},
                    }
                ],
            )
            report = monitor(
                root,
                fetcher=lambda requested: FetchResponse(requested, 200, b"new", {"ETag": "v2"}),
                timestamp="2026-09-30T00:00:00Z",
            )

        source = report["sources"][0]
        self.assertEqual(source["canonical_url"], url)
        self.assertEqual(source["status"], 200)
        self.assertEqual(source["change"]["status"], "content-changed")
        codes = {finding["code"] for finding in report["findings"]}
        self.assertEqual(codes, {"content-changed", "time-sensitive-review-expired"})
        self.assertTrue(all(finding["severity"] == "advisory" for finding in report["findings"]))

    def test_network_failure_persists_as_per_source_advisory(self):
        from monitor_provenance import monitor

        url = "https://sources.example/unavailable"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(root, sources=[{"url": url, "type": "paper"}])
            report = monitor(
                root,
                fetcher=lambda requested: (_ for _ in ()).throw(TimeoutError("timed out")),
                timestamp="2026-09-30T00:00:00Z",
            )

        self.assertIsNone(report["sources"][0]["status"])
        self.assertEqual(report["sources"][0]["findings"][0]["code"], "fetch-failed")
        self.assertEqual(report["sources"][0]["findings"][0]["severity"], "advisory")

    def test_incomplete_previous_report_falls_back_to_versioned_baseline(self):
        from monitor_provenance import FetchResponse, monitor

        url = "https://sources.example/fallback"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(
                root,
                sources=[{"url": url, "type": "paper"}],
                baseline_sources=[{"url": url, "content_digest": hashlib.sha256(b"old").hexdigest()}],
            )
            previous = root / "previous.json"
            previous.write_text(json.dumps({"sources": [{"canonical_url": url, "content_digest": None}]}), encoding="utf-8")
            report = monitor(
                root,
                fetcher=lambda requested: FetchResponse(requested, 200, b"new", {}),
                previous_report_path=previous,
                timestamp="2026-09-30T00:00:00Z",
            )
        self.assertEqual(report["sources"][0]["change"]["status"], "content-changed")

    def test_unsafe_or_unregistered_destination_is_not_fetched(self):
        from monitor_provenance import is_safe_url, monitor

        called = []
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            unsafe = "http://127.0.0.1/private"
            self.write_fixture(root, sources=[{"url": unsafe, "type": "official-documentation"}])
            report = monitor(root, fetcher=lambda requested: called.append(requested))

        self.assertFalse(is_safe_url(unsafe))
        self.assertFalse(is_safe_url("https://sources.example:8443/nonstandard"))
        self.assertEqual(called, [])
        self.assertEqual(report["sources"][0]["findings"][0]["code"], "unsafe-canonical-url")

    def test_safe_opener_ignores_ambient_proxy_configuration(self):
        from monitor_provenance import ProxyHandler, build_safe_opener

        with patch("urllib.request.getproxies", return_value={"https": "http://127.0.0.1:8080"}):
            opener = build_safe_opener()
        self.assertFalse(any(isinstance(handler, ProxyHandler) for handler in opener.handlers))

    def test_broken_registry_or_timestamp_still_returns_and_writes_global_advisory(self):
        from monitor_provenance import monitor

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = monitor(root, timestamp="not-a-timestamp")
            (root / "evals").mkdir()
            (root / "evals/provenance.json").write_text("{not-json", encoding="utf-8")
            malformed = monitor(root, timestamp="2026-09-30T00:00:00Z")
            output = root / "report.json"
            command = [
                sys.executable,
                str(Path(__file__).resolve().parents[1] / "tools/book-kit/monitor_provenance.py"),
                "--root",
                str(root),
                "--timestamp",
                "not-a-timestamp",
                "--output",
                str(output),
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            persisted = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual({finding["code"] for finding in report["findings"]}, {"invalid-timestamp", "registry-unavailable"})
        self.assertEqual({finding["code"] for finding in malformed["findings"]}, {"registry-unavailable"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual({finding["code"] for finding in persisted["findings"]}, {"invalid-timestamp", "registry-unavailable"})

    def test_scheduled_workflow_is_manual_or_scheduled_only_and_uploads_report(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/provenance-monitor.yml").read_text(encoding="utf-8")
        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("pull_request:", workflow)
        self.assertIn("monitor_provenance.py", workflow)
        self.assertIn("continue-on-error: true", workflow)
        self.assertIn("provenance-monitor-report", workflow)
        self.assertIn("if: always()", workflow)


if __name__ == "__main__":
    unittest.main()
