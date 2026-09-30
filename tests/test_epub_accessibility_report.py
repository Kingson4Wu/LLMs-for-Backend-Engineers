import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/book-kit"))


class EpubAccessibilityReportTests(unittest.TestCase):
    def test_deterministic_gate_rejects_missing_core_metadata_and_wrong_reading_order(self):
        from audit_epub_accessibility import audit_epub, deterministic_gate_errors

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_book(root)
            epub = self.make_epub(root, chapter_order=("first", "introduction", "second"))
            report = audit_epub(root / "book", epub, "en", timestamp="2026-09-29T00:00:00Z")

        self.assertEqual(
            deterministic_gate_errors(report),
            [
                "EPUB accessibility metadata is missing schema:accessMode",
                "EPUB accessibility metadata is missing schema:accessibilityFeature",
                "EPUB accessibility metadata is missing schema:accessibilityHazard",
                "EPUB spine chapter order does not match the catalog",
            ],
        )

    def make_book(self, root: Path) -> None:
        source = root / "book"
        (source / "chapters/part").mkdir(parents=True)
        (source / "index.md").write_text("# Introduction", encoding="utf-8")
        (source / "chapters/part/first.md").write_text("# First", encoding="utf-8")
        (source / "chapters/part/second.md").write_text("# Second", encoding="utf-8")
        (source / "parts").mkdir()
        (source / "parts/part.md").write_text("# Part", encoding="utf-8")
        (source / "catalog.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "frontmatter": [{"id": "introduction", "path": "index.md", "title": "Introduction"}],
                    "parts": [
                        {
                            "id": "part",
                            "path": "parts/part.md",
                            "title": "Part",
                            "chapters": [
                                {"id": "first", "path": "chapters/part/first.md", "title": "First"},
                                {"id": "second", "path": "chapters/part/second.md", "title": "Second"},
                            ],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (source / "editions.json").write_text(
            json.dumps({"editions": {"en": {"source": "."}}}), encoding="utf-8"
        )

    def make_epub(self, root: Path, *, chapter_order=("introduction", "first", "second"), metadata="") -> Path:
        epub = root / "edition.epub"
        items = [
            '<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
            *[
                f'<item id="{chapter}" href="text/{chapter}.xhtml" media-type="application/xhtml+xml"/>'
                for chapter in chapter_order
            ],
        ]
        spine = ['<itemref idref="nav"/>', *[f'<itemref idref="{chapter}"/>' for chapter in chapter_order]]
        opf = (
            '<package xmlns="http://www.idpf.org/2007/opf" version="3.0">'
            '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
            '<dc:language>en</dc:language>'
            f'{metadata}'
            '</metadata><manifest>' + ''.join(items) + '</manifest><spine>' + ''.join(spine) + '</spine></package>'
        )
        with zipfile.ZipFile(epub, "w") as archive:
            archive.writestr("EPUB/content.opf", opf)
            archive.writestr("EPUB/nav.xhtml", '<html xmlns="http://www.w3.org/1999/xhtml"><body/></html>')
            for chapter in chapter_order:
                archive.writestr(
                    f"EPUB/text/{chapter}.xhtml",
                    f'<html xmlns="http://www.w3.org/1999/xhtml"><body><section id="{chapter}"/></body></html>',
                )
        return epub

    def test_report_records_metadata_language_navigation_and_catalog_order(self):
        from audit_epub_accessibility import audit_epub

        metadata = (
            '<meta property="schema:accessMode">textual</meta>'
            '<meta property="schema:accessibilityFeature">readingOrder</meta>'
            '<meta property="schema:accessibilityHazard">none</meta>'
            '<meta property="schema:accessibilitySummary">Automated metadata and order report only.</meta>'
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_book(root)
            epub = self.make_epub(root, metadata=metadata)
            digest = hashlib.sha256(epub.read_bytes()).hexdigest()
            report = audit_epub(root / "book", epub, "en", timestamp="2026-09-29T00:00:00Z")

        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["artifact"]["sha256"], digest)
        self.assertEqual(report["language"]["value"], "en")
        self.assertTrue(report["navigation"]["present"])
        self.assertEqual(report["reading_order"]["catalog_chapter_ids"], ["introduction", "first", "second"])
        self.assertEqual(report["reading_order"]["spine_chapter_ids"], ["introduction", "first", "second"])
        self.assertTrue(report["reading_order"]["matches_catalog"])
        self.assertEqual(report["findings"], [])
        self.assertIn("does not establish EPUB Accessibility or WCAG conformance", report["scope"])

    def test_missing_metadata_and_wrong_order_are_advisory_findings(self):
        from audit_epub_accessibility import audit_epub

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_book(root)
            epub = self.make_epub(root, chapter_order=("first", "introduction", "second"))
            report = audit_epub(root / "book", epub, "en", timestamp="2026-09-29T00:00:00Z")

        codes = {finding["code"] for finding in report["findings"]}
        self.assertIn("missing-schema:accessMode", codes)
        self.assertIn("missing-schema:accessibilitySummary", codes)
        self.assertIn("catalog-reading-order-mismatch", codes)
        self.assertTrue(all(finding["severity"] == "advisory" for finding in report["findings"]))

    def test_publication_workflows_preserve_advisory_epub_reports(self):
        root = Path(__file__).resolve().parents[1]
        for name in ("ci.yml", "deploy-docs.yml", "release-books.yml"):
            workflow = (root / ".github/workflows" / name).read_text(encoding="utf-8")
            self.assertIn("audit_epub_accessibility.py", workflow, name)
            self.assertIn("epub-accessibility-reports", workflow, name)
            self.assertIn("epub-accessibility-*.json", workflow, name)
            self.assertIn("if: always()", workflow, name)
            self.assertLess(workflow.index("export_epub.py"), workflow.index("audit_epub_accessibility.py"), name)

    def test_cli_writes_an_advisory_report_without_gating_missing_epub(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_book(root)
            output = root / "report.json"
            command = [
                sys.executable,
                str(Path(__file__).resolve().parents[1] / "tools/book-kit/audit_epub_accessibility.py"),
                str(root / "book"),
                "--locale",
                "en",
                "--epub",
                str(root / "missing.epub"),
                "--output",
                str(output),
                "--timestamp",
                "2026-09-29T00:00:00Z",
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            report = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(report["findings"][-1]["code"], "epub-unavailable")

    def test_fresh_localized_exports_include_honest_accessibility_summary(self):
        from audit_epub_accessibility import audit_epub

        root = Path(__file__).resolve().parents[1]
        expectations = {
            "zh-Hans": ("不宣称符合 EPUB Accessibility 或 WCAG", "具体阅读器和辅助技术"),
            "en": ("does not claim EPUB Accessibility or WCAG conformance", "assistive technology"),
        }
        for locale, phrases in expectations.items():
            subprocess.run(
                [sys.executable, str(root / "tools/book-kit/export_epub.py"), "--locale", locale],
                check=True,
                capture_output=True,
            )
            report = audit_epub(
                root / "book",
                root / "book/exported" / locale / "Understanding-LLMs.epub",
                locale,
                timestamp="2026-09-29T00:00:00Z",
            )
            summary = report["accessibility_metadata"]["schema:accessibilitySummary"]["values"]
            self.assertEqual(len(summary), 1, locale)
            self.assertTrue(all(phrase in summary[0] for phrase in phrases), locale)
            self.assertEqual(report["findings"], [], locale)

    def test_exporter_repairs_all_missing_opf_accessibility_metadata(self):
        from audit_epub_accessibility import audit_epub
        from export_epub import ensure_accessibility_metadata

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            epub = root / "edition.epub"
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr("EPUB/content.opf", '<package xmlns="http://www.idpf.org/2007/opf"><metadata/></package>')
                archive.writestr("EPUB/keep.txt", "unchanged")
            ensure_accessibility_metadata(epub, "A localized summary.")
            with zipfile.ZipFile(epub) as archive:
                opf = archive.read("EPUB/content.opf").decode("utf-8")
                self.assertEqual(opf.count('property="schema:accessMode"'), 1)
                self.assertEqual(opf.count('property="schema:accessibilityFeature"'), 4)
                self.assertEqual(opf.count('property="schema:accessibilityHazard"'), 1)
                self.assertEqual(opf.count('property="schema:accessibilitySummary"'), 1)
                self.assertIn(
                    '<meta property="schema:accessMode">textual</meta>',
                    opf,
                )
                self.assertIn(
                    '<meta property="schema:accessibilityFeature">readingOrder</meta>',
                    opf,
                )
                self.assertIn(
                    '<meta property="schema:accessibilityHazard">none</meta>',
                    opf,
                )
                self.assertIn("A localized summary.", opf)
                self.assertEqual(archive.read("EPUB/keep.txt"), b"unchanged")

            self.make_book(root)
            audited = self.make_epub(root)
            ensure_accessibility_metadata(audited, "A localized summary.")
            report = audit_epub(root / "book", audited, "en", timestamp="2026-09-29T00:00:00Z")
            self.assertEqual(report["findings"], [])


if __name__ == "__main__":
    unittest.main()
