import json
import base64
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/book-kit"))


class ContentManifestTests(unittest.TestCase):
    def make_book(self, root: Path) -> Path:
        book = root / "book"
        (book / "chapters").mkdir(parents=True)
        (book / "assets").mkdir()
        (book / "editions.json").write_text(
            json.dumps({"editions": {"zh-Hans": {"source": "."}}}), encoding="utf-8"
        )
        (book / "catalog.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "frontmatter": [],
                    "parts": [
                        {
                            "id": "foundations",
                            "title": "Foundations",
                            "path": "parts.md",
                            "chapters": [
                                {"id": "example", "path": "chapters/example.md", "title": "Example title"}
                            ],
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        (book / "parts.md").write_text("# Foundations\n", encoding="utf-8")
        (book / "assets/example.svg").write_text("<svg/>", encoding="utf-8")
        (book / "chapters/example.md").write_text(
            "# Example title\n\n## A heading\n\n$$x = y$$\n\n![Diagram](../assets/example.svg)\n\n## 用 AI 学习本书\n",
            encoding="utf-8",
        )
        return book

    def add_second_chapter(self, book: Path) -> None:
        catalog_path = book / "catalog.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["parts"][0]["chapters"].append(
            {"id": "second", "path": "chapters/second.md", "title": "Second title"}
        )
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        (book / "chapters/second.md").write_text(
            "# Second title\n\n## Second heading\n\n$$a = b$$\n", encoding="utf-8"
        )

    def test_source_manifest_records_ordered_chapter_signals(self):
        from content_manifest import derive_source_manifest

        with tempfile.TemporaryDirectory() as tmp:
            manifest = derive_source_manifest(self.make_book(Path(tmp)), "zh-Hans")

        self.assertEqual(manifest["locale"], "zh-Hans")
        self.assertEqual([chapter["id"] for chapter in manifest["chapters"]], ["example"])
        chapter = manifest["chapters"][0]
        self.assertEqual(chapter["title"], "Example title")
        self.assertEqual(chapter["h1"], "Example title")
        self.assertEqual(chapter["h2"], ["A heading", "用 AI 学习本书"])
        self.assertEqual([figure["path"] for figure in chapter["figures"]], ["assets/example.svg"])
        self.assertEqual(len(chapter["figures"][0]["sha256"]), 64)
        self.assertEqual(len(chapter["display_math"]), 1)
        self.assertTrue(manifest["ai_learning_guide_present"])

    def test_markdown_validation_reports_a_missing_source_formula(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            manuscript = root / "Understanding-LLMs.md"
            manuscript.write_text(
                "# Book\n\n# Example title\n\n## A heading\n\n![Diagram](assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"markdown": manuscript}, formats={"markdown"}
            )

        self.assertEqual(len(errors), 1)
        self.assertRegex(errors[0], r"^markdown:example: missing display math fingerprint [0-9a-f]{12}$")

    def test_markdown_validation_reports_a_missing_source_h2(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            manuscript = root / "Understanding-LLMs.md"
            manuscript.write_text(
                "# Example title\n\n$$x = y$$\n\n![Diagram](https://example.test/assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"markdown": manuscript}, formats={"markdown"}
            )

        self.assertIn("markdown:example: missing heading 'A heading'", errors)

    def test_markdown_body_prose_cannot_satisfy_a_source_heading(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            manuscript = root / "Understanding-LLMs.md"
            manuscript.write_text(
                "# Example title\n\nA heading appears only in body prose.\n\n$$x = y$$\n\n"
                "![Diagram](assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"markdown": manuscript}, formats={"markdown"}
            )

        self.assertIn("markdown:example: missing heading 'A heading'", errors)

    def test_markdown_h3_cannot_satisfy_a_source_h2(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            manuscript = root / "Understanding-LLMs.md"
            manuscript.write_text(
                "# Example title\n\n### A heading\n\n$$x = y$$\n\n![Diagram](assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"markdown": manuscript}, formats={"markdown"}
            )

        self.assertIn("markdown:example: missing heading 'A heading'", errors)

    def test_chapter_segment_accepts_real_export_heading_nesting(self):
        """A catalogue chapter H2 wraps source H1/H2 as H2/H3 in Pandoc output."""
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            manuscript = root / "Understanding-LLMs.md"
            manuscript.write_text(
                "<a id=\"example\"></a>\n## Chapter 1: Example title\n\n### A heading\n\n"
                "$$x = y$$\n\n![Diagram](assets/example.svg)\n\n### 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"markdown": manuscript}, formats={"markdown"}
            )

        self.assertEqual(errors, [])

    def test_markdown_and_html_reject_swapped_catalogue_chapter_segments(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            self.add_second_chapter(book)
            image = base64.b64encode((book / "assets/example.svg").read_bytes()).decode()
            artifacts = {
                "markdown": root / "Understanding-LLMs.md",
                "html": root / "Understanding-LLMs.print.html",
            }
            artifacts["markdown"].write_text(
                "<a id=\"second\"></a>\n## Chapter 2: Second title\n\n### Second heading\n\n$$a = b$$\n\n"
                "<a id=\"example\"></a>\n## Chapter 1: Example title\n\n### A heading\n\n$$x = y$$\n\n"
                "![Diagram](assets/example.svg)\n\n### 用 AI 学习本书\n",
                encoding="utf-8",
            )
            artifacts["html"].write_text(
                '<h2 id="second">Chapter 2: Second title</h2><h3>Second heading</h3>'
                '<math><annotation encoding="application/x-tex">a = b</annotation></math>'
                '<h2 id="example">Chapter 1: Example title</h2><h3>A heading</h3>'
                '<math><annotation encoding="application/x-tex">x = y</annotation></math>'
                f'<img src="data:image/svg+xml;base64,{image}"><h3>用 AI 学习本书</h3>',
                encoding="utf-8",
            )
            manifest = derive_source_manifest(book, "zh-Hans")
            errors = {
                kind: validate_artifact_manifest(manifest, {kind: path}, formats={kind})
                for kind, path in artifacts.items()
            }

        expected = "chapter segment order ['second', 'example'] does not match catalog ['example', 'second']"
        self.assertIn(f"markdown: {expected}", errors["markdown"])
        self.assertIn(f"html: {expected}", errors["html"])

    def test_markdown_rejects_missing_repeated_formula_and_figure_occurrences(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            (book / "chapters/example.md").write_text(
                "# Example title\n\n## A heading\n\n$$x = y$$\n\n$$x = y$$\n\n"
                "![First](../assets/example.svg)\n\n![Second](../assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            manuscript = root / "Understanding-LLMs.md"
            manuscript.write_text(
                '<a id="example"></a>\n## Chapter 1: Example title\n\n### A heading\n\n$$x = y$$\n\n'
                "![First](assets/example.svg)\n\n### 用 AI 学习本书\n",
                encoding="utf-8",
            )
            manifest = derive_source_manifest(book, "zh-Hans")
            errors = validate_artifact_manifest(manifest, {"markdown": manuscript}, formats={"markdown"})
            fingerprint = manifest["chapters"][0]["display_math"][0][:12]

        self.assertIn(f"markdown:example: missing display math fingerprint {fingerprint} occurrence 2", errors)
        self.assertIn("markdown:example: missing figure example.svg occurrence 2", errors)

    def test_markdown_rejects_a_duplicate_chapter_boundary(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            manuscript = root / "Understanding-LLMs.md"
            section = "## Chapter 1: Example title\n\n### A heading\n\n$$x = y$$\n\n![Diagram](assets/example.svg)\n\n### 用 AI 学习本书\n"
            manuscript.write_text(f'<a id="example"></a>\n{section}\n<a id="example"></a>\n{section}', encoding="utf-8")
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"markdown": manuscript}, formats={"markdown"}
            )

        self.assertIn("markdown:example: duplicate chapter segment boundary", errors)

    def test_epub_rejects_segments_swapped_in_its_opf_spine(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            self.add_second_chapter(book)
            epub = root / "Understanding-LLMs.epub"
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr("EPUB/media/example.svg", (book / "assets/example.svg").read_bytes())
                archive.writestr(
                    "EPUB/text/example.xhtml",
                    '<section id="example"><h1>Example title</h1><h2>A heading</h2>'
                    '<math><annotation encoding="application/x-tex">x = y</annotation></math>'
                    '<img src="../media/example.svg"><h2>用 AI 学习本书</h2></section>',
                )
                archive.writestr(
                    "EPUB/text/second.xhtml",
                    '<section id="second"><h1>Second title</h1><h2>Second heading</h2>'
                    '<math><annotation encoding="application/x-tex">a = b</annotation></math></section>',
                )
                archive.writestr(
                    "EPUB/content.opf",
                    '<package><manifest><item id="example" href="text/example.xhtml"/>'
                    '<item id="second" href="text/second.xhtml"/></manifest>'
                    '<spine><itemref idref="second"/><itemref idref="example"/></spine></package>',
                )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"epub": epub}, formats={"epub"}
            )

        self.assertIn(
            "epub: chapter segment order ['second', 'example'] does not match catalog ['example', 'second']", errors
        )

    def test_html_chapter_segment_accepts_a_wrapped_source_h1_and_h2(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            image = base64.b64encode((book / "assets/example.svg").read_bytes()).decode()
            html = root / "Understanding-LLMs.print.html"
            html.write_text(
                '<h2 id="example">Chapter 1: Example title</h2><h3>A heading</h3>'
                '<math><annotation encoding="application/x-tex">x = y</annotation></math>'
                f'<img src="data:image/svg+xml;base64,{image}"><h3>用 AI 学习本书</h3>',
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"html": html}, formats={"html"}
            )

        self.assertEqual(errors, [])

    def test_epub_section_segment_accepts_its_local_source_h1_and_h2(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            epub = root / "Understanding-LLMs.epub"
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr("EPUB/media/example.svg", (book / "assets/example.svg").read_bytes())
                archive.writestr(
                    "EPUB/text/chapter.xhtml",
                    '<section id="example"><h1>Example title</h1><h2>A heading</h2>'
                    '<math><annotation encoding="application/x-tex">x = y</annotation></math>'
                    '<img src="../media/example.svg"><h2>用 AI 学习本书</h2></section>',
                )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"epub": epub}, formats={"epub"}
            )

        self.assertEqual(errors, [])

    def test_markdown_heading_requires_an_exact_normalized_label(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            manuscript = root / "Understanding-LLMs.md"
            manuscript.write_text(
                "# Example title\n\n## A heading, but altered\n\n$$x = y$$\n\n![Diagram](assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"markdown": manuscript}, formats={"markdown"}
            )

        self.assertIn("markdown:example: missing heading 'A heading'", errors)

    def test_markdown_h3_cannot_satisfy_a_source_h1(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            manuscript = root / "Understanding-LLMs.md"
            manuscript.write_text(
                "### Example title\n\n#### A heading\n\n$$x = y$$\n\n![Diagram](assets/example.svg)\n\n#### 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"markdown": manuscript}, formats={"markdown"}
            )

        self.assertIn("markdown:example: missing heading '第1章：Example title'", errors)

    def test_markdown_heading_must_belong_to_its_chapter_anchor(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            manuscript = root / "Understanding-LLMs.md"
            manuscript.write_text(
                "<a id=\"other\"></a>\n# Example title\n\n## A heading\n\n"
                "<a id=\"example\"></a>\n# Example title\n\n## A different heading\n\n"
                "$$x = y$$\n\n![Diagram](assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"markdown": manuscript}, formats={"markdown"}
            )

        self.assertIn("markdown:example: missing heading 'A heading'", errors)

    def test_export_uses_the_published_heading_without_requiring_source_h1_identity(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            (book / "chapters/example.md").write_text(
                "# Source H1: canonical title\n\n## A heading\n\n$$x = y$$\n\n![Diagram](../assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            manuscript = root / "Understanding-LLMs.md"
            manuscript.write_text(
                '<a id="example"></a>\n## Chapter 1: Example title\n\n### A heading\n\n$$x = y$$\n\n'
                "![Diagram](assets/example.svg)\n\n### 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"markdown": manuscript}, formats={"markdown"}
            )

        self.assertEqual(errors, [])

    def test_appendix_uses_each_renderer_s_published_heading(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            catalog_path = book / "catalog.json"
            catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
            catalog["parts"][0]["id"] = "appendix"
            catalog["parts"][0]["chapters"][0]["title"] = "附录一：Example title"
            catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
            image = base64.b64encode((book / "assets/example.svg").read_bytes()).decode()
            markdown = root / "Understanding-LLMs.md"
            markdown.write_text(
                '<a id="example"></a>\n## 附录: 附录一：Example title\n\n### A heading\n\n$$x = y$$\n\n'
                "![Diagram](assets/example.svg)\n\n### 用 AI 学习本书\n",
                encoding="utf-8",
            )
            html = root / "Understanding-LLMs.print.html"
            html.write_text(
                '<h2 id="example">附录 A：Example title</h2><h3>A heading</h3>'
                '<math><annotation encoding="application/x-tex">x = y</annotation></math>'
                f'<img src="data:image/svg+xml;base64,{image}"><h3>用 AI 学习本书</h3>',
                encoding="utf-8",
            )
            manifest = derive_source_manifest(book, "zh-Hans")
            markdown_errors = validate_artifact_manifest(manifest, {"markdown": markdown}, formats={"markdown"})
            html_errors = validate_artifact_manifest(manifest, {"html": html}, formats={"html"})

        self.assertEqual(markdown_errors, [])
        self.assertEqual(html_errors, [])

    def test_markdown_figure_requires_its_exact_local_path(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            manuscript = root / "Understanding-LLMs.md"
            manuscript.write_text(
                "# Example title\n\n## A heading\n\n$$x = y$$\n\n"
                "![Diagram](https://example.test/assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"markdown": manuscript}, formats={"markdown"}
            )

        self.assertEqual(errors, ["markdown:example: missing figure example.svg"])

    def test_html_validation_reports_missing_mathml_annotation(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            fingerprint = derive_source_manifest(book, "zh-Hans")["chapters"][0]["display_math"][0][:12]
            html = root / "Understanding-LLMs.print.html"
            image = base64.b64encode((book / "assets/example.svg").read_bytes()).decode()
            html.write_text(
                f"<h1>Example title</h1><h2>A heading</h2><math><mrow>x=y</mrow></math>"
                f'<img src="data:image/svg+xml;base64,{image}"><h2>用 AI 学习本书</h2>',
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"html": html}, formats={"html"}
            )

        self.assertIn(f"html:example: missing display math fingerprint {fingerprint}", errors)

    def test_epub_validation_reports_a_missing_chapter(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            (book / "chapters/example.md").write_text(
                "# Source H1\n\n## A heading\n\n$$x = y$$\n\n![Diagram](../assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            epub = root / "Understanding-LLMs.epub"
            with zipfile.ZipFile(epub, "w") as archive:
                archive.writestr("EPUB/text/chapter.xhtml", "<h2>用 AI 学习本书</h2>")
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"epub": epub}, formats={"epub"}
            )

        self.assertIn("epub:example: missing heading '第1章：Example title'", errors)

    def test_html_validation_reports_the_missing_figure_by_name(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            html = root / "Understanding-LLMs.print.html"
            html.write_text(
                '<h1>Example title</h1><h2>A heading</h2>'
                '<math><annotation encoding="application/x-tex">x = y</annotation></math>'
                '<h2>用 AI 学习本书</h2>',
                encoding="utf-8",
            )
            errors = validate_artifact_manifest(
                derive_source_manifest(book, "zh-Hans"), {"html": html}, formats={"html"}
            )

        self.assertEqual(errors, ["html:example: missing figure example.svg"])

    def test_pdf_formula_evidence_reports_each_unavailable_formula(self):
        from content_manifest import pdf_formula_evidence

        evidence = pdf_formula_evidence(r"\\frac{x}{y}")

        self.assertEqual(evidence["status"], "requires_allowlist")
        self.assertIn("TeX control sequence", evidence["detection_reason"])

    def test_pdf_uses_text_only_heading_policy_not_extracted_heading_assertions(self):
        from content_manifest import derive_source_manifest, validate_artifact_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            pdf = root / "Understanding-LLMs.pdf"
            pdf.write_bytes(b"not a real PDF fixture")
            with patch("content_manifest._pdf_content", return_value=("用 AI 学习本书", [], [], [])):
                errors = validate_artifact_manifest(
                    derive_source_manifest(book, "zh-Hans"), {"pdf": pdf}, formats={"pdf"}
                )

        self.assertEqual(errors, [])

    def test_pdf_formula_evidence_keeps_a_simple_formula_fingerprint(self):
        from content_manifest import math_fingerprint, pdf_formula_evidence

        evidence = pdf_formula_evidence("x = y")

        self.assertEqual(evidence, {"fingerprint": math_fingerprint("x = y"), "status": "extractable", "text": "x=y"})

    def test_pdf_missing_extractable_formula_uses_its_reviewed_allowlist_record(self):
        from content_manifest import derive_source_manifest, pdf_formula_audit, validate_pdf_formula_audit

        with tempfile.TemporaryDirectory() as tmp:
            manifest = derive_source_manifest(self.make_book(Path(tmp)), "zh-Hans")
            fingerprint = manifest["chapters"][0]["pdf_display_math"][0]["fingerprint"]
            audit = pdf_formula_audit(
                manifest,
                "",
                {"version": 1, "formulas": [{
                    "chapter": "example", "fingerprint": fingerprint,
                    "reason": "renderer text extraction loses this formula", "reviewer": "tester", "reviewed_at": "2026-09-30",
                }]},
            )

        formula = audit["chapters"][0]["formulas"][0]
        self.assertEqual(formula["status"], "unavailable")
        self.assertEqual(validate_pdf_formula_audit(manifest, audit), [])

    def test_pdf_missing_extractable_formula_without_allowlist_remains_a_hard_failure(self):
        from content_manifest import derive_source_manifest, write_pdf_formula_audit

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            manifest = derive_source_manifest(self.make_book(root), "zh-Hans")
            pdf = root / "edition.pdf"
            pdf.write_bytes(b"fixture")
            with patch("content_manifest._pdf_content", return_value=("", [], [], [])):
                _audit, errors = write_pdf_formula_audit(manifest, pdf, root / "audit.json", {"version": 1, "formulas": []})

        self.assertTrue(any("missing display math fingerprint" in error for error in errors), errors)

    def test_pdf_formula_audit_requires_an_unavailable_formula_entry(self):
        from content_manifest import derive_source_manifest, validate_pdf_formula_audit

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            (book / "chapters/example.md").write_text(
                "# Example title\n\n## A heading\n\n$$\\frac{x}{y}$$\n\n![Diagram](../assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_pdf_formula_audit(
                derive_source_manifest(book, "zh-Hans"),
                {
                    "heading_validation": {
                        "status": "text-only",
                        "reason": "PDF text extraction does not retain heading node structure",
                    },
                    "chapters": [],
                },
            )

        self.assertRegex(errors[0], r"^pdf audit:example: missing formula [0-9a-f]{12}$")

    def test_pdf_formula_audit_does_not_reuse_one_record_for_repeated_formulae(self):
        from content_manifest import derive_source_manifest, validate_pdf_formula_audit

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            (book / "chapters/example.md").write_text(
                "# Example title\n\n## A heading\n\n$$\\frac{x}{y}$$\n\n$$\\frac{x}{y}$$\n\n"
                "![Diagram](../assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            manifest = derive_source_manifest(book, "zh-Hans")
            fingerprint = manifest["chapters"][0]["display_math"][0]
            errors = validate_pdf_formula_audit(
                manifest,
                {
                    "heading_validation": {
                        "status": "text-only",
                        "reason": "PDF text extraction does not retain heading node structure",
                    },
                    "chapters": [{"id": "example", "formulas": [{
                        "fingerprint": fingerprint,
                        "status": "unavailable",
                        "reason": "reviewed",
                        "reviewer": "tester",
                        "reviewed_at": "2026-09-29",
                    }]}],
                },
            )

        self.assertIn(f"pdf audit:example: missing formula {fingerprint[:12]} occurrence 2", errors)

    def test_unavailable_pdf_formula_requires_a_reviewed_allowlist_record(self):
        from content_manifest import derive_source_manifest, validate_pdf_formula_allowlist

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            (book / "chapters/example.md").write_text(
                "# Example title\n\n## A heading\n\n$$\\frac{x}{y}$$\n\n![Diagram](../assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            errors = validate_pdf_formula_allowlist(derive_source_manifest(book, "zh-Hans"), {"version": 1, "formulas": []})

        self.assertRegex(errors[0], r"^pdf allowlist:example: missing formula [0-9a-f]{12}$")

    def test_unavailable_pdf_formula_rejects_incomplete_review_metadata(self):
        from content_manifest import derive_source_manifest, validate_pdf_formula_allowlist

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = self.make_book(root)
            (book / "chapters/example.md").write_text(
                "# Example title\n\n## A heading\n\n$$\\frac{x}{y}$$\n\n![Diagram](../assets/example.svg)\n\n## 用 AI 学习本书\n",
                encoding="utf-8",
            )
            fingerprint = derive_source_manifest(book, "zh-Hans")["chapters"][0]["display_math"][0]
            errors = validate_pdf_formula_allowlist(
                derive_source_manifest(book, "zh-Hans"),
                {"version": 1, "formulas": [{"chapter": "example", "fingerprint": fingerprint, "reason": "reviewed"}]},
            )

        self.assertRegex(errors[0], r"^pdf allowlist:example: incomplete review metadata [0-9a-f]{12}$")

    def test_committed_pdf_allowlist_covers_both_locales(self):
        from content_manifest import derive_source_manifest, validate_pdf_formula_allowlist

        root = Path(__file__).resolve().parents[1]
        allowlist = json.loads((root / "evals/pdf-formula-allowlist.json").read_text(encoding="utf-8"))

        for locale in ("zh-Hans", "en"):
            self.assertEqual(validate_pdf_formula_allowlist(derive_source_manifest(root / "book", locale), allowlist), [])

    def test_committed_allowlist_covers_ci_proven_unavailable_plain_formulas(self):
        from content_manifest import derive_source_manifest, pdf_formula_audit

        root = Path(__file__).resolve().parents[1]
        allowlist = json.loads((root / "evals/pdf-formula-allowlist.json").read_text(encoding="utf-8"))
        audit = pdf_formula_audit(derive_source_manifest(root / "book", "zh-Hans"), "", allowlist)
        unavailable = {
            (chapter["id"], formula["fingerprint"][:12])
            for chapter in audit["chapters"]
            for formula in chapter["formulas"]
            if formula["status"] == "unavailable"
        }

        self.assertTrue({
            ("from-onehot-to-embedding", "6f0ce408d33b"),
            ("activation-functions", "58d6ae7dc052"),
            ("backpropagation", "9355d17cbee8"),
            ("backpropagation", "56d4726c3447"),
            ("vanishing-exploding-gradients", "b4139eca80fc"),
            ("vanishing-exploding-gradients", "d4c12460710b"),
            ("residual-connections", "b180adbca2da"),
            ("residual-connections", "b30e1f7430cb"),
            ("residual-connections", "0d9d34020eaa"),
            ("layer-norm", "58d6ae7dc052"),
            ("llm-inference-nondeterminism", "4938458aacfd"),
        }.issubset(unavailable))

if __name__ == "__main__":
    unittest.main()
