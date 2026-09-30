#!/usr/bin/env python3
"""Run axe-core on the fixed reader route matrix and write an advisory report."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

from audit_web_accessibility import route_matrix, site_identifier


SCHEMA_VERSION = 1
TAGS = ["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"]
SCOPE = (
    "Advisory axe-core evidence only; automated findings do not establish WCAG "
    "conformance or assistive-technology usability."
)


def _finding(code: str, message: str) -> dict:
    return {"severity": "advisory", "code": code, "message": message}


def summarize_axe_result(result: dict) -> dict:
    """Preserve machine findings without converting them into a conformance claim."""
    violations = result.get("violations", []) if isinstance(result.get("violations"), list) else []
    incomplete = result.get("incomplete", []) if isinstance(result.get("incomplete"), list) else []
    passed = result.get("passes", []) if isinstance(result.get("passes"), list) else []
    findings = [
        _finding("axe-violation", str(item.get("id", "unknown-rule")))
        for item in violations if isinstance(item, dict)
    ] + [
        _finding("axe-incomplete", str(item.get("id", "unknown-rule")))
        for item in incomplete if isinstance(item, dict)
    ]
    return {"violations": violations, "incomplete": incomplete, "passes": len(passed), "findings": findings}


def audit_routes(base_url: str, site_dir: Path | None, axe_script: Path, *, timestamp: str | None = None) -> dict:
    """Inspect each configured route, retaining route and scanner failures as evidence."""
    timestamp = timestamp or dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "audit_axe_accessibility", "version": "1.0", "tags": TAGS},
        "generated_at": timestamp,
        "scope": SCOPE,
        "site": {"base_url": base_url.rstrip("/"), "directory": site_dir.as_posix() if site_dir else None, "identifier": site_identifier(site_dir)},
        "routes": [],
    }
    if not axe_script.is_file():
        report["findings"] = [_finding("axe-script-unavailable", f"Cannot read axe-core script: {axe_script}")]
        return report

    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        report["findings"] = [_finding("playwright-unavailable", str(exc))]
        return report

    script = axe_script.read_text(encoding="utf-8")
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            try:
                report["browser"] = {"engine": "chromium", "version": browser.version}
                for item in route_matrix():
                    page = browser.new_page(viewport=item["viewport_size"])
                    entry = {key: item[key] for key in ("name", "locale", "route", "viewport", "viewport_size")}
                    entry["url"] = report["site"]["base_url"] + item["route"]
                    try:
                        response = page.goto(entry["url"], wait_until="domcontentloaded")
                        page.add_script_tag(content=script)
                        result = page.evaluate("async tags => await axe.run(document, { runOnly: { type: 'tag', values: tags } })", TAGS)
                        entry.update(summarize_axe_result(result))
                        entry["http_status"] = response.status if response else None
                        if response is not None and response.status >= 400:
                            entry["findings"].append(_finding("route-http-error", f"Route returned HTTP {response.status}."))
                    except Exception as exc:
                        entry.update({"violations": [], "incomplete": [], "passes": 0, "findings": [_finding("axe-route-unavailable", str(exc))]})
                    finally:
                        page.close()
                    report["routes"].append(entry)
            finally:
                browser.close()
    except Exception as exc:
        report["findings"] = [_finding("axe-browser-unavailable", str(exc))]
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--site-dir", type=Path)
    parser.add_argument("--axe-script", type=Path, default=Path("web/node_modules/axe-core/axe.min.js"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = audit_routes(args.base_url, args.site_dir, args.axe_script)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
