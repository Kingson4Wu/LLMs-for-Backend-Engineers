#!/usr/bin/env python3
"""Write an advisory accessibility evidence report for a built reading site.

This records observable route facts. It does not establish WCAG conformance or
the usability of the site with assistive technology.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import sys


SCHEMA_VERSION = 1
TOOL_VERSION = "1.0"
SCOPE = (
    "Advisory automated route evidence only; this report does not establish WCAG "
    "conformance, accessibility conformance, or assistive-technology usability."
)
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1000},
    "mobile": {"width": 390, "height": 844},
}
ROUTE_MATRIX = (
    {"name": "home", "path": "/{locale}/"},
    {"name": "dense-math", "path": "/{locale}/read/backpropagation/"},
    {"name": "diagram-heavy", "path": "/{locale}/read/transformer-architecture/"},
    {"name": "downloads", "path": "/{locale}/downloads/"},
    {"name": "ai-learning", "path": "/{locale}/read/ai-learning-guide/"},
)


SNAPSHOT_SCRIPT = r"""() => {
  const visible = element => {
    const style = getComputedStyle(element);
    const rect = element.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity) !== 0 && rect.width > 0 && rect.height > 0;
  };
  const focusables = [...document.querySelectorAll('a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), summary, [tabindex]:not([tabindex="-1"])')]
    .filter(visible);
  const images = [...document.images];
  return {
    document_lang: document.documentElement.lang || '',
    headings: [...document.querySelectorAll('main h1, main h2, main h3, main h4, main h5, main h6')]
      .filter(visible).map(heading => Number(heading.tagName.slice(1))),
    images: {
      total: images.length,
      without_alt: images.filter(image => !image.hasAttribute('alt')).map(image => image.currentSrc || image.src || '<unknown>'),
    },
    focus: { count: focusables.length },
    layout: { scroll_width: document.documentElement.scrollWidth, viewport_width: window.innerWidth },
  };
}"""


FOCUS_SCRIPT = r"""() => {
  const element = document.activeElement;
  if (!element || element === document.body) return { active_tag: null, focus_visible: false, indicator: false };
  const style = getComputedStyle(element);
  const outline = style.outlineStyle !== 'none' && parseFloat(style.outlineWidth || '0') > 0;
  return {
    active_tag: element.tagName,
    active_id: element.id || null,
    focus_visible: element.matches(':focus-visible'),
    indicator: outline || style.boxShadow !== 'none',
  };
}"""


def route_matrix() -> list[dict]:
    """Expand the intentionally small two-locale, two-viewport route matrix."""
    return [
        {
            "name": route["name"],
            "locale": locale,
            "route": route["path"].format(locale=locale),
            "viewport": viewport,
            "viewport_size": size,
        }
        for locale in ("zh-Hans", "en")
        for route in ROUTE_MATRIX
        for viewport, size in VIEWPORTS.items()
    ]


def _advisory(result: dict, code: str, message: str) -> None:
    result["findings"].append({"severity": "advisory", "code": code, "message": message})


def analyze_snapshot(snapshot: dict, *, expected_locale: str) -> dict:
    """Turn one browser snapshot into transparent, advisory-only observations."""
    result = {
        "document_lang": snapshot.get("document_lang", ""),
        "headings": snapshot.get("headings", []),
        "images": snapshot.get("images", {"total": 0, "without_alt": []}),
        "focus": snapshot.get("focus", {"count": 0}),
        "layout": dict(snapshot.get("layout", {})),
        "findings": [],
    }
    if result["document_lang"] != expected_locale:
        _advisory(result, "document-language-mismatch", f"Document language does not match expected locale {expected_locale!r}.")

    headings = result["headings"]
    if not headings or headings[0] != 1:
        _advisory(result, "missing-leading-h1", "The visible main-content heading sequence does not begin with h1.")
    elif headings.count(1) > 1:
        _advisory(result, "multiple-h1", "Visible main content contains more than one h1.")
    for previous, current in zip(headings, headings[1:]):
        if current > previous + 1:
            _advisory(result, "heading-level-skip", f"Visible heading level jumps from h{previous} to h{current}.")

    missing_alt = result["images"].get("without_alt", [])
    if missing_alt:
        _advisory(result, "image-without-alt", f"{len(missing_alt)} image(s) lack an alt attribute.")

    scroll_width = result["layout"].get("scroll_width", 0)
    viewport_width = result["layout"].get("viewport_width", 0)
    result["layout"]["horizontal_overflow"] = bool(viewport_width and scroll_width > viewport_width)
    if result["layout"]["horizontal_overflow"]:
        _advisory(result, "horizontal-overflow", "Document scroll width exceeds viewport width.")
    return result


def site_identifier(site_dir: Path | None) -> str | None:
    """Fingerprint built site bytes without treating the hash as a quality verdict."""
    if site_dir is None or not site_dir.is_dir():
        return None
    digest = hashlib.sha256()
    for path in sorted(candidate for candidate in site_dir.rglob("*") if candidate.is_file()):
        digest.update(path.relative_to(site_dir).as_posix().encode("utf-8") + b"\0")
        digest.update(hashlib.sha256(path.read_bytes()).digest())
    return digest.hexdigest()


def audit_routes(base_url: str, site_dir: Path | None, *, timestamp: str | None = None) -> dict:
    """Inspect the route matrix in Chromium; findings never cause a nonzero result."""
    from playwright.sync_api import sync_playwright

    timestamp = timestamp or dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    report = {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "audit_web_accessibility", "version": TOOL_VERSION},
        "generated_at": timestamp,
        "scope": SCOPE,
        "site": {
            "base_url": base_url.rstrip("/"),
            "directory": site_dir.as_posix() if site_dir else None,
            "identifier": site_identifier(site_dir),
        },
        "browser": {},
        "routes": [],
    }
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        report["browser"] = {"engine": "chromium", "version": browser.version}
        for item in route_matrix():
            page = browser.new_page(viewport=item["viewport_size"])
            result = {key: item[key] for key in ("name", "locale", "route", "viewport", "viewport_size")}
            result["url"] = report["site"]["base_url"] + item["route"]
            try:
                response = page.goto(result["url"], wait_until="domcontentloaded")
                page.wait_for_timeout(150)
                snapshot = page.evaluate(SNAPSHOT_SCRIPT)
                page.keyboard.press("Tab")
                snapshot["focus"].update(page.evaluate(FOCUS_SCRIPT))
                result.update(analyze_snapshot(snapshot, expected_locale=item["locale"]))
                result["http_status"] = response.status if response else None
                if response is not None and response.status >= 400:
                    _advisory(result, "route-http-error", f"Route returned HTTP {response.status}.")
            except Exception as exc:  # The report must preserve route failures as review evidence.
                result.update({"findings": []})
                _advisory(result, "route-unavailable", f"Browser inspection failed: {exc}")
            finally:
                page.close()
            report["routes"].append(result)
        browser.close()
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", required=True)
    parser.add_argument("--site-dir", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timestamp", help="ISO-8601 timestamp for reproducible fixtures")
    args = parser.parse_args()
    report = audit_routes(args.base_url, args.site_dir, timestamp=args.timestamp)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
