#!/usr/bin/env python3
"""Write an advisory EPUB metadata and default-reading-order report.

The report makes package declarations and source/catalogue alignment visible.
It is deliberately not an EPUB Accessibility or WCAG conformance assessment.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import posixpath
import sys
import xml.etree.ElementTree as ET
import zipfile

from book_meta import catalog_entries, load_catalog, normalize_locale, resolve_book_dir, resolve_source_dir


SCHEMA_VERSION = 1
TOOL_VERSION = "1.0"
ACCESSIBILITY_PROPERTIES = (
    "schema:accessMode",
    "schema:accessibilityFeature",
    "schema:accessibilityHazard",
    "schema:accessibilitySummary",
)
REQUIRED_DISCOVERY_PROPERTIES = ACCESSIBILITY_PROPERTIES[:3]
SCOPE = (
    "Advisory package metadata and default-reading-order evidence only; this report "
    "does not establish EPUB Accessibility or WCAG conformance."
)


def _local_name(element: ET.Element) -> str:
    return element.tag.rsplit("}", 1)[-1]


def _sha256(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


def _package_path(archive: zipfile.ZipFile) -> str:
    """Find the OPF through the container when available, with a Pandoc fallback."""
    container = "META-INF/container.xml"
    if container in archive.namelist():
        root = ET.fromstring(archive.read(container))
        for element in root.iter():
            if _local_name(element) == "rootfile" and element.attrib.get("full-path"):
                return element.attrib["full-path"]
    return "EPUB/content.opf"


def _advisory(report: dict, code: str, message: str) -> None:
    report["findings"].append({"severity": "advisory", "code": code, "message": message})


def _base_report(epub: Path, locale: str, timestamp: str) -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "tool": {"name": "audit_epub_accessibility", "version": TOOL_VERSION},
        "generated_at": timestamp,
        "locale": locale,
        "scope": SCOPE,
        "artifact": {"path": epub.as_posix(), "sha256": _sha256(epub)},
        "findings": [],
    }


def deterministic_gate_errors(report: dict) -> list[str]:
    """Return only EPUB package facts that have a stable local pass/fail oracle.

    This deliberately excludes the quality of ``accessibilitySummary`` and all
    reader-experience judgements; those remain advisory human-review evidence.
    """
    errors = []
    metadata = report.get("accessibility_metadata", {})
    for property_name in REQUIRED_DISCOVERY_PROPERTIES:
        value = metadata.get(property_name, {}) if isinstance(metadata, dict) else {}
        if not isinstance(value, dict) or value.get("missing") is not False:
            errors.append(f"EPUB accessibility metadata is missing {property_name}")
    language = report.get("language", {})
    if not isinstance(language, dict) or language.get("matches_locale") is not True:
        errors.append("EPUB language does not match its locale")
    navigation = report.get("navigation", {})
    if not isinstance(navigation, dict) or navigation.get("present") is not True:
        errors.append("EPUB navigation document is unavailable")
    reading_order = report.get("reading_order", {})
    if not isinstance(reading_order, dict) or reading_order.get("matches_catalog") is not True:
        errors.append("EPUB spine chapter order does not match the catalog")
    return errors


def _catalog_chapter_ids(book: Path, locale: str) -> list[str]:
    source = resolve_source_dir(book, locale)
    return [entry["id"] for entry in catalog_entries(load_catalog(source))]


def _spine(archive: zipfile.ZipFile, opf: ET.Element, opf_path: str) -> list[dict]:
    manifest = {
        item.attrib["id"]: item
        for item in opf.iter()
        if _local_name(item) == "item" and item.attrib.get("id")
    }
    resources = []
    base = posixpath.dirname(opf_path)
    for itemref in opf.iter():
        if _local_name(itemref) != "itemref":
            continue
        identifier = itemref.attrib.get("idref")
        item = manifest.get(identifier)
        if item is None:
            resources.append({"idref": identifier, "missing_manifest_item": True})
            continue
        href = item.attrib.get("href", "")
        resources.append(
            {
                "idref": identifier,
                "href": href,
                "path": posixpath.normpath(posixpath.join(base, href)),
                "linear": itemref.attrib.get("linear", "yes"),
                "media_type": item.attrib.get("media-type"),
            }
        )
    return resources


def _chapter_ids_in_resource(archive: zipfile.ZipFile, path: str, expected: set[str]) -> list[str]:
    if path not in archive.namelist() or not path.endswith((".xhtml", ".html")):
        return []
    root = ET.fromstring(archive.read(path))
    return [element.attrib["id"] for element in root.iter() if element.attrib.get("id") in expected]


def audit_epub(book: Path, epub: Path, locale: str, *, timestamp: str | None = None) -> dict:
    """Return an advisory-only evidence record for one already-built EPUB."""
    locale = normalize_locale(locale)
    timestamp = timestamp or dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")
    report = _base_report(epub, locale, timestamp)
    try:
        expected_chapters = _catalog_chapter_ids(book, locale)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        _advisory(report, "catalog-unavailable", f"Cannot read catalog chapter sequence: {exc}")
        expected_chapters = []

    report["accessibility_metadata"] = {
        property_name: {"values": [], "missing": True}
        for property_name in ACCESSIBILITY_PROPERTIES
    }
    report["language"] = {"value": None, "expected": locale, "matches_locale": False}
    report["navigation"] = {"present": False, "resources": []}
    report["reading_order"] = {
        "catalog_chapter_ids": expected_chapters,
        "spine_resources": [],
        "spine_chapter_ids": [],
        "missing_catalog_chapter_ids": expected_chapters,
        "matches_catalog": False,
    }

    if not epub.is_file():
        _advisory(report, "epub-unavailable", "Generated EPUB artifact is unavailable for inspection.")
        return report

    try:
        with zipfile.ZipFile(epub) as archive:
            opf_path = _package_path(archive)
            opf = ET.fromstring(archive.read(opf_path))
            metadata = [element for element in opf.iter() if _local_name(element) == "meta"]
            for property_name in ACCESSIBILITY_PROPERTIES:
                values = [
                    (element.text or "").strip()
                    for element in metadata
                    if element.attrib.get("property") == property_name and (element.text or "").strip()
                ]
                report["accessibility_metadata"][property_name] = {
                    "values": values,
                    "missing": not values,
                }
                if not values:
                    _advisory(report, f"missing-{property_name}", f"OPF metadata is missing {property_name}.")

            language_values = [
                (element.text or "").strip()
                for element in opf.iter()
                if _local_name(element) == "language" and (element.text or "").strip()
            ]
            language = language_values[0] if language_values else None
            report["language"] = {
                "value": language,
                "expected": locale,
                "matches_locale": language == locale,
            }
            if language is None:
                _advisory(report, "missing-language", "OPF metadata is missing dc:language.")
            elif language != locale:
                _advisory(report, "language-locale-mismatch", f"OPF language {language!r} does not match locale {locale!r}.")

            resources = _spine(archive, opf, opf_path)
            report["reading_order"]["spine_resources"] = resources
            manifest_items = [element for element in opf.iter() if _local_name(element) == "item"]
            nav_resources = [
                posixpath.normpath(posixpath.join(posixpath.dirname(opf_path), item.attrib.get("href", "")))
                for item in manifest_items
                if "nav" in item.attrib.get("properties", "").split()
            ]
            report["navigation"] = {
                "present": bool(nav_resources) and all(path in archive.namelist() for path in nav_resources),
                "resources": nav_resources,
            }
            if not report["navigation"]["present"]:
                _advisory(report, "navigation-unavailable", "EPUB navigation document is missing or undeclared.")

            expected = set(expected_chapters)
            actual = []
            for resource in resources:
                path = resource.get("path")
                if not isinstance(path, str):
                    continue
                try:
                    chapter_ids = _chapter_ids_in_resource(archive, path, expected)
                except ET.ParseError:
                    _advisory(report, "spine-resource-unreadable", f"Cannot parse spine resource {path}.")
                    chapter_ids = []
                resource["catalog_chapter_ids"] = chapter_ids
                actual.extend(chapter_ids)
            report["reading_order"]["spine_chapter_ids"] = actual
            report["reading_order"]["missing_catalog_chapter_ids"] = [chapter for chapter in expected_chapters if chapter not in actual]
            report["reading_order"]["matches_catalog"] = actual == expected_chapters
            if actual != expected_chapters:
                _advisory(
                    report,
                    "catalog-reading-order-mismatch",
                    "Catalog chapter sequence does not match chapter IDs found in EPUB spine resources.",
                )
    except (KeyError, OSError, ET.ParseError, zipfile.BadZipFile) as exc:
        _advisory(report, "epub-unreadable", f"Cannot inspect EPUB package: {exc}")
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("book_dir", nargs="?")
    parser.add_argument("--locale", default="zh-Hans")
    parser.add_argument("--epub", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--timestamp", help="ISO-8601 timestamp for reproducible report fixtures")
    args = parser.parse_args()
    book = resolve_book_dir(args.book_dir)
    report = audit_epub(book, args.epub, args.locale, timestamp=args.timestamp)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
