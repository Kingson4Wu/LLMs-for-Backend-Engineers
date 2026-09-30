#!/usr/bin/env python3
"""Capture a fixed, advisory screenshot matrix for human visual review.

This tool deliberately does not compare pixels or establish visual quality.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path


SCHEMA_VERSION = 1
TOOL_VERSION = "1.0"
SCOPE = (
    "Advisory screenshots for human review only; no pixel baseline or visual-quality "
    "threshold is evaluated, and this report does not establish accessibility or rendering conformance."
)
VIEWPORTS = {"desktop": {"width": 1440, "height": 1000}, "mobile": {"width": 390, "height": 844}}
THEMES = ("light", "dark")
ROUTES = (
    {"name": "home", "path": "/{locale}/"},
    {"name": "dense-math", "path": "/{locale}/read/cross-entropy/"},
    {"name": "dense-table-code", "path": "/{locale}/read/llm-external-interaction/"},
    {"name": "diagram-heavy", "path": "/{locale}/read/transformer-architecture/"},
    {"name": "downloads", "path": "/{locale}/downloads/"},
    {"name": "ai-learning", "path": "/{locale}/read/ai-learning-guide/"},
)


def visual_matrix() -> list[dict]:
    return [
        {
            "name": route["name"], "locale": locale, "route": route["path"].format(locale=locale),
            "theme": theme, "viewport": viewport, "viewport_size": size,
            "screenshot": f"{locale}/{theme}/{viewport}/{route['name']}.png",
        }
        for locale in ("zh-Hans", "en") for route in ROUTES for theme in THEMES
        for viewport, size in VIEWPORTS.items()
    ]


def advisory_entry(item: dict, code: str, message: str) -> dict:
    return {**item, "screenshot": None, "findings": [{"severity": "advisory", "code": code, "message": message}]}


def site_identifier(site_dir: Path | None) -> str | None:
    if site_dir is None or not site_dir.is_dir():
        return None
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in site_dir.rglob("*") if candidate.is_file()):
        digest.update(path.relative_to(site_dir).as_posix().encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def capture(base_url: str, site_dir: Path | None, screenshot_dir: Path, *, timestamp: str | None = None) -> dict:
    from playwright.sync_api import sync_playwright

    timestamp = timestamp or dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "capture_visual_review", "version": TOOL_VERSION},
        "generated_at": timestamp,
        "scope": SCOPE,
        "site": {"base_url": base_url.rstrip("/"), "identifier": site_identifier(site_dir)},
        "browser": {}, "screenshots": [], "findings": [],
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        report["browser"] = {"engine": "chromium", "version": browser.version}
        for item in visual_matrix():
            page = browser.new_page(viewport=item["viewport_size"])
            entry = {key: item[key] for key in ("name", "locale", "route", "theme", "viewport", "viewport_size")}
            entry["url"] = report["site"]["base_url"] + item["route"]
            entry["captured_at"] = timestamp
            entry["findings"] = []
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            try:
                page.add_init_script(f"localStorage.setItem('llms-theme', {json.dumps(item['theme'])});")
                response = page.goto(entry["url"], wait_until="domcontentloaded")
                page.wait_for_timeout(150)
                entry["http_status"] = response.status if response else None
                if response is not None and response.status >= 400:
                    entry["findings"].append({"severity": "advisory", "code": "route-http-error", "message": f"Route returned HTTP {response.status}."})
                if page.locator("html").get_attribute("data-theme") != item["theme"]:
                    entry["findings"].append({"severity": "advisory", "code": "theme-not-applied", "message": "Requested theme was not reflected on the document."})
                target = screenshot_dir / item["screenshot"]
                target.parent.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(target), full_page=False)
                entry["screenshot"] = item["screenshot"]
                if errors:
                    entry["findings"].append({"severity": "advisory", "code": "page-error", "message": "; ".join(errors)})
            except Exception as exc:
                entry = advisory_entry(entry, "render-failed", f"Screenshot capture failed: {exc}")
            finally:
                page.close()
            report["screenshots"].append(entry)
            report["findings"].extend(entry["findings"])
        browser.close()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--site-dir", type=Path)
    parser.add_argument("--screenshot-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timestamp")
    args = parser.parse_args()
    report = capture(args.base_url, args.site_dir, args.screenshot_dir, timestamp=args.timestamp)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
