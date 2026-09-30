#!/usr/bin/env python3
"""Advisory monitoring for the explicit provenance registry only.

Remote responses are maintenance evidence. This tool never changes provenance,
claims, source locks, or book content, and findings are intentionally advisory.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import datetime as dt
import hashlib
import ipaddress
import json
from pathlib import Path
import socket
import sys
from typing import Callable
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener


SCHEMA_VERSION = 1
TOOL_VERSION = "1.0"
DEFAULT_TIMEOUT_SECONDS = 15
DEFAULT_MAX_BYTES = 2_000_000
SCOPE = (
    "Advisory monitoring of the explicit provenance registry only. Remote responses "
    "do not establish a claim's truth and never update source locks, cases, or book content."
)
INTERESTING_HEADERS = ("content-type", "content-length", "etag", "last-modified")


@dataclass(frozen=True)
class FetchResponse:
    final_url: str
    status: int | None
    body: bytes
    headers: dict[str, str]


def is_safe_url(value: object) -> bool:
    """Reject credentials, insecure schemes, and obvious private destinations."""
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        return False
    try:
        if parsed.port not in (None, 443):
            return False
    except ValueError:
        return False
    host = parsed.hostname.rstrip(".").lower()
    if host == "localhost" or host.endswith(".local"):
        return False
    try:
        return ipaddress.ip_address(host).is_global
    except ValueError:
        return True


def _public_destination(url: str) -> bool:
    """Resolve a URL hostname and reject any non-public result before connecting."""
    if not is_safe_url(url):
        return False
    hostname = urlsplit(url).hostname
    assert hostname is not None
    try:
        addresses = {record[4][0] for record in socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)}
    except OSError:
        return False
    return bool(addresses) and all(ipaddress.ip_address(address).is_global for address in addresses)


class _SafeRedirectHandler(HTTPRedirectHandler):
    max_redirections = 3

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not _public_destination(newurl):
            raise ValueError("redirect destination is not an allowed public HTTPS URL")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def build_safe_opener():
    """Disable ambient proxy environment variables for this direct-only monitor."""
    return build_opener(ProxyHandler({}), _SafeRedirectHandler())


def fetch_url(url: str, *, timeout: int = DEFAULT_TIMEOUT_SECONDS, max_bytes: int = DEFAULT_MAX_BYTES) -> FetchResponse:
    """Fetch one registry URL with bounded redirects, time, bytes, and destinations."""
    if not _public_destination(url):
        raise ValueError("canonical URL is not an allowed public HTTPS destination")
    request = Request(url, headers={"User-Agent": "Understanding-LLMs-provenance-monitor/1.0"})
    opener = build_safe_opener()
    try:
        response = opener.open(request, timeout=timeout)
    except HTTPError as error:
        response = error
    with response:
        body = response.read(max_bytes + 1)
        if len(body) > max_bytes:
            raise ValueError(f"response exceeds {max_bytes} byte limit")
        headers = {
            name: value
            for name in INTERESTING_HEADERS
            if (value := response.headers.get(name)) is not None
        }
        return FetchResponse(response.geturl(), response.getcode(), body, headers)


def _load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _sources(root: Path) -> list[dict]:
    data = _load_json(root / "evals" / "provenance.json")
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        raise ValueError("provenance registry needs a sources list")
    return data["sources"]


def _baseline(path: Path | None) -> dict[str, dict]:
    if path is None or not path.is_file():
        return {}
    data = _load_json(path)
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("sources"), list):
        return {}
    return {
        source["url"]: source
        for source in data["sources"]
        if isinstance(source, dict) and isinstance(source.get("url"), str)
    }


def _previous_report(path: Path | None) -> dict[str, dict]:
    if path is None or not path.is_file():
        return {}
    data = _load_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("sources"), list):
        return {}
    return {
        source["canonical_url"]: source
        for source in data["sources"]
        if isinstance(source, dict) and isinstance(source.get("canonical_url"), str)
    }


def _advisory(target: dict, code: str, message: str) -> dict:
    finding = {"severity": "advisory", "code": code, "message": message}
    target.setdefault("findings", []).append(finding)
    return finding


def _change(record: dict, baseline: dict | None) -> tuple[dict, list[tuple[str, str]]]:
    if not baseline or not isinstance(baseline.get("content_digest"), str):
        return {"status": "uninitialized", "baseline": None}, [("baseline-content-digest-unavailable", "No versioned content digest is available for comparison.")]
    changes = []
    if record["content_digest"] != baseline["content_digest"]:
        changes.append(("content-changed", "Fetched content digest differs from the selected baseline."))
    if isinstance(baseline.get("final_url"), str) and record["final_url"] != baseline["final_url"]:
        changes.append(("final-url-changed", "Final URL differs from the selected baseline."))
    return {"status": changes[0][0] if changes else "unchanged", "baseline": baseline.get("content_digest")}, changes


def _time_sensitive_reviews(root: Path, as_of: dt.date) -> list[dict]:
    reviews = []
    for path in sorted((root / "evals" / "claims").glob("*.json")):
        try:
            data = _load_json(path)
        except (OSError, json.JSONDecodeError):
            continue
        for case in data.get("cases", []) if isinstance(data, dict) and isinstance(data.get("cases"), list) else []:
            if not isinstance(case, dict) or case.get("kind") != "time-sensitive":
                continue
            review = case.get("review") if isinstance(case.get("review"), dict) else {}
            reviewed_at, interval = review.get("reviewed_at"), case.get("review_interval_days")
            try:
                review_date = dt.date.fromisoformat(reviewed_at) if isinstance(reviewed_at, str) else None
            except ValueError:
                review_date = None
            due = review_date + dt.timedelta(days=interval) if review_date and isinstance(interval, int) and not isinstance(interval, bool) and interval > 0 else None
            reviews.append({
                "id": case.get("id"), "reviewed_at": reviewed_at, "review_interval_days": interval,
                "due_on": due.isoformat() if due else None, "expired": bool(due and as_of > due),
            })
    return reviews


def monitor(
    root: Path,
    *,
    fetcher: Callable[[str], FetchResponse] | None = None,
    baseline_path: Path | None = None,
    previous_report_path: Path | None = None,
    timestamp: str | None = None,
) -> dict:
    """Fetch only registered provenance URLs and return an advisory report."""
    timestamp = timestamp or dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    baseline_path = baseline_path if baseline_path is not None else root / "evals" / "provenance-monitor-baseline.json"
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "monitor_provenance", "version": TOOL_VERSION},
        "generated_at": timestamp,
        "scope": SCOPE,
        "comparison": {"previous_report": previous_report_path.as_posix() if previous_report_path else None, "baseline": baseline_path.as_posix() if baseline_path else None},
        "sources": [], "time_sensitive_reviews": [], "findings": [],
    }
    try:
        as_of = dt.date.fromisoformat(timestamp[:10])
    except (TypeError, ValueError):
        as_of = None
        _advisory(report, "invalid-timestamp", "Report timestamp is not an ISO-8601 date/time value.")
    try:
        previous = _previous_report(previous_report_path)
    except (OSError, json.JSONDecodeError) as exc:
        previous = {}
        _advisory(report, "previous-report-unavailable", f"Cannot read previous report: {exc}")
    try:
        baseline = _baseline(baseline_path)
    except (OSError, json.JSONDecodeError) as exc:
        baseline = {}
        _advisory(report, "baseline-unavailable", f"Cannot read baseline: {exc}")
    try:
        sources = _sources(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        sources = []
        _advisory(report, "registry-unavailable", f"Cannot read provenance registry: {exc}")
    for source in sources:
        url = source.get("url") if isinstance(source, dict) else None
        record = {"canonical_url": url, "final_url": None, "status": None, "content_digest": None, "headers": {}, "findings": []}
        report["sources"].append(record)
        if not is_safe_url(url):
            finding = _advisory(record, "unsafe-canonical-url", "Registry URL is not a public HTTPS destination without credentials.")
            report["findings"].append(finding)
            continue
        try:
            response = (fetcher(url) if fetcher else fetch_url(url))
            if not isinstance(response, FetchResponse):
                raise TypeError("fetcher must return FetchResponse")
            record.update({"final_url": response.final_url, "status": response.status, "content_digest": hashlib.sha256(response.body).hexdigest(), "headers": {key.lower(): value for key, value in response.headers.items() if key.lower() in INTERESTING_HEADERS}})
            if not is_safe_url(response.final_url):
                finding = _advisory(record, "unsafe-final-url", "Fetcher returned a final URL outside the public HTTPS policy.")
                report["findings"].append(finding)
                continue
            if response.status is None or response.status >= 400:
                finding = _advisory(record, "http-error", f"Source returned HTTP status {response.status}.")
                report["findings"].append(finding)
                continue
            previous_record = previous.get(url)
            selected = previous_record if isinstance(previous_record, dict) and isinstance(previous_record.get("content_digest"), str) else baseline.get(url)
            record["change"], changes = _change(record, selected)
            for code, message in changes:
                finding = _advisory(record, code, message)
                report["findings"].append(finding)
        except Exception as exc:
            finding = _advisory(record, "fetch-failed", f"Source fetch failed: {exc}")
            report["findings"].append(finding)
    report["time_sensitive_reviews"] = _time_sensitive_reviews(root, as_of) if as_of else []
    for review in report["time_sensitive_reviews"]:
        if review["expired"]:
            report["findings"].append({"severity": "advisory", "code": "time-sensitive-review-expired", "message": f"Time-sensitive case {review['id']!r} exceeded its review interval."})
    return report


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--previous-report", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timestamp", help="ISO-8601 timestamp for reproducible reports")
    args = parser.parse_args()
    try:
        report = monitor(args.root.resolve(), baseline_path=args.baseline, previous_report_path=args.previous_report, timestamp=args.timestamp)
    except Exception as exc:  # Preserve an advisory artifact even for an unexpected monitor defect.
        report = {
            "schema_version": SCHEMA_VERSION,
            "tool": {"name": "monitor_provenance", "version": TOOL_VERSION},
            "generated_at": args.timestamp,
            "scope": SCOPE,
            "comparison": {
                "previous_report": str(args.previous_report) if args.previous_report else None,
                "baseline": str(args.baseline) if args.baseline else None,
            },
            "sources": [],
            "time_sensitive_reviews": [],
            "findings": [{"severity": "advisory", "code": "monitor-unavailable", "message": f"Monitor failed before completion: {exc}"}],
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
