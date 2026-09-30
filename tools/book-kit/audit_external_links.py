#!/usr/bin/env python3
"""Write an advisory health report for public external links in book sources."""
from __future__ import annotations

import argparse
import datetime as dt
import ipaddress
import json
from pathlib import Path
import re
import socket
import urllib.error
import urllib.parse
import urllib.request


SCHEMA_VERSION = 1
URL = re.compile(r"https?://[^\s<>\])}]+")
TRAILING_PUNCTUATION = ".,;:!?"
SOURCE_PATHS = (
    ("zh-Hans", "book/index.md"),
    ("zh-Hans", "book/chapters"),
    ("zh-Hans", "book/parts"),
    ("en", "book/translations/en/index.md"),
    ("en", "book/translations/en/chapters"),
    ("en", "book/translations/en/parts"),
)
SCOPE = (
    "Advisory external-link reachability evidence only; a reachable URL does not "
    "establish the correctness, currency, or meaning of the linked source."
)


def _clean_url(value: str) -> str:
    return value.rstrip(TRAILING_PUNCTUATION)


def inventory_links(root: Path) -> list[dict]:
    """Extract unique public URLs with stable source locations from both editions."""
    by_url: dict[str, list[dict]] = {}
    for locale, relative_path in SOURCE_PATHS:
        source_path = root / relative_path
        paths = [source_path] if source_path.is_file() else sorted(source_path.rglob("*.md"))
        for path in paths:
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                for match in URL.finditer(line):
                    url = _clean_url(match.group(0))
                    by_url.setdefault(url, []).append(
                        {"locale": locale, "path": path.relative_to(root).as_posix(), "line": line_number}
                    )
    return [{"url": url, "locations": locations} for url, locations in sorted(by_url.items())]


def _is_public_https(url: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        return False
    try:
        addresses = {record[4][0] for record in socket.getaddrinfo(parsed.hostname, None)}
    except OSError:
        return False
    return bool(addresses) and all(ipaddress.ip_address(address).is_global for address in addresses)


def fetch_public_url(url: str) -> tuple[str | None, str | None, str | None]:
    """Fetch a declared public URL without proxy inheritance or response bodies."""
    if not _is_public_https(url):
        return None, "unsafe-or-unresolvable-url", "URL is not a resolvable public HTTP(S) destination"
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "Understanding-LLMs-link-monitor/1.0"})
    try:
        with opener.open(request, timeout=15) as response:
            final_url = response.geturl()
            if not _is_public_https(final_url):
                return None, "unsafe-final-url", "Redirect left the public HTTP(S) destination policy"
            return final_url, None, None
    except urllib.error.HTTPError as exc:
        return None, "http-error", f"HTTP {exc.code}"
    except (OSError, ValueError, urllib.error.URLError) as exc:
        return None, "fetch-failed", str(getattr(exc, "reason", exc))


def audit_links(inventory: list[dict], *, fetch=fetch_public_url, timestamp: str | None = None) -> dict:
    """Create a reviewable report; failures are findings rather than process errors."""
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "audit_external_links", "version": "1.0"},
        "generated_at": timestamp or dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z"),
        "scope": SCOPE,
        "links": [],
    }
    for entry in inventory:
        final_url, code, message = fetch(entry["url"])
        findings = [] if code is None else [{"severity": "advisory", "code": code, "message": message}]
        report["links"].append({**entry, "final_url": final_url, "findings": findings})
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_links(inventory_links(args.root.resolve()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
