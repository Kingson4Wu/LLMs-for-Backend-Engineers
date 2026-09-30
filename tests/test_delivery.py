import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/book-kit'))

class DeliveryTests(unittest.TestCase):
    def test_delivery_formats_keep_attribution_without_polluting_reflowable_text(self):
        root = Path(__file__).resolve().parents[1]
        watermark_path = root / 'tools/book-kit/watermark.py'
        self.assertTrue(watermark_path.is_file())
        watermark = watermark_path.read_text(encoding='utf-8')
        markdown = (root / 'tools/book-kit/export_markdown.py').read_text(encoding='utf-8')
        epub = (root / 'tools/book-kit/export_epub.py').read_text(encoding='utf-8')
        print_html = (root / 'tools/book-kit/build_print_html.py').read_text(encoding='utf-8')
        pdf = (root / 'tools/book-kit/export_book_pdf.py').read_text(encoding='utf-8')

        self.assertIn('Kingson Wu', watermark)
        self.assertIn('shipout/background', watermark)
        self.assertIn('provenance_line', markdown)
        self.assertIn('provenance_line', epub)
        self.assertIn('append_provenance', epub)
        self.assertIn("publication-epub.css", epub)
        self.assertIn('watermark_html', print_html)
        self.assertIn('watermark_tex', pdf)

    def test_delivery_workflows_validate_the_learning_index(self):
        root = Path(__file__).resolve().parents[1]
        workflows = root / '.github/workflows'
        for name in ('ci.yml', 'deploy-docs.yml', 'release-books.yml'):
            self.assertIn(
                '--check-learning-index',
                (workflows / name).read_text(encoding='utf-8'),
                f'{name} must reject a stale learning/index.json',
            )

    def test_deployment_runs_when_publication_evaluation_contract_changes(self):
        workflow = (Path(__file__).resolve().parents[1] / '.github/workflows/deploy-docs.yml').read_text(encoding='utf-8')
        self.assertIn("- 'evals/**'", workflow)
        self.assertIn("- 'tests/**'", workflow)

    def test_release_workflow_reverifies_downloaded_github_assets(self):
        workflow = (Path(__file__).resolve().parents[1] / '.github/workflows/release-books.yml').read_text(encoding='utf-8')
        self.assertIn('gh release download "$RELEASE_TAG" --dir published-release', workflow)
        self.assertIn('validate_release_provenance.py --release published-release --version "$RELEASE_TAG" --commit "$GITHUB_SHA"', workflow)
        self.assertLess(
            workflow.index('gh release download "$RELEASE_TAG" --dir published-release'),
            workflow.index('validate_release_provenance.py --release published-release'),
        )

    def test_release_rejects_mismatched_provenance(self):
        from package_release import package
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'editions.json').write_text(json.dumps({'editions': {'en': {'status':'published'}}}))
            out = root / 'exported/en'; out.mkdir(parents=True)
            artifacts=[]
            for name in ('Understanding-LLMs.pdf', 'Understanding-LLMs.epub', 'Understanding-LLMs.print.html', 'Understanding-LLMs.md'):
                (out/name).write_bytes(b'content')
                artifacts.append({'file':name,'sha256':hashlib.sha256(b'content').hexdigest(),'source_commit':'abc','source_dirty':False,'source_digest':name})
            (out/'manifest.json').write_text(json.dumps({'artifacts':artifacts}))
            with self.assertRaisesRegex(ValueError,'source'):
                package(root, root/'release', 'v1.0', expected_commit='abc')
    def test_release_packages_verified_formats_and_manifest_checksums(self):
        from package_release import package, validate_release_provenance
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'editions.json').write_text(json.dumps({'editions': {'en': {'status':'published'}}}))
            out = root / 'exported/en'; out.mkdir(parents=True)
            artifacts = []
            for name in ('Understanding-LLMs.pdf', 'Understanding-LLMs.epub', 'Understanding-LLMs.print.html', 'Understanding-LLMs.md'):
                data = name.encode()
                (out / name).write_bytes(data)
                artifacts.append({'file':name, 'sha256':hashlib.sha256(data).hexdigest(), 'source_commit':'abc', 'source_dirty':False, 'source_digest':'same'})
            (out / 'manifest.json').write_text(json.dumps({'artifacts':artifacts}))
            destination = root / 'release'
            result = package(
                root,
                destination,
                'v1.0',
                expected_commit='abc',
                workflow_context={"provider": "github-actions", "repository": "owner/repo", "run_id": "42"},
            )
            self.assertEqual(len(result['artifacts']), 4)
            for line in (destination / 'SHA256SUMS').read_text().splitlines():
                digest, name = line.split('  ')
                self.assertEqual(digest, hashlib.sha256((destination / name).read_bytes()).hexdigest())
            self.assertIn('manifest.json', (destination / 'SHA256SUMS').read_text())
            self.assertTrue((destination / 'Understanding-LLMs-en-v1.0.print.html').is_file())
            provenance = json.loads((destination / 'release-provenance.json').read_text())
            self.assertEqual(provenance['release_tag'], 'v1.0')
            self.assertEqual(provenance['git_commit'], 'abc')
            self.assertEqual(provenance['workflow_context']['run_id'], '42')
            self.assertEqual(provenance['files'][0]['sha256'], hashlib.sha256((destination / provenance['files'][0]['file']).read_bytes()).hexdigest())
            self.assertEqual(validate_release_provenance(destination, expected_version='v1.0', expected_commit='abc'), [])

    def test_release_provenance_rejects_a_tampered_download(self):
        from package_release import package, validate_release_provenance
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'editions.json').write_text(json.dumps({'editions': {'en': {'status':'published'}}}))
            out = root / 'exported/en'; out.mkdir(parents=True)
            artifacts = []
            for name in ('Understanding-LLMs.pdf', 'Understanding-LLMs.epub', 'Understanding-LLMs.print.html', 'Understanding-LLMs.md'):
                data = name.encode()
                (out / name).write_bytes(data)
                artifacts.append({'file':name, 'sha256':hashlib.sha256(data).hexdigest(), 'source_commit':'abc', 'source_dirty':False, 'source_digest':'same'})
            (out / 'manifest.json').write_text(json.dumps({'artifacts':artifacts}))
            destination = root / 'release'
            package(root, destination, 'v1.0', expected_commit='abc')
            (destination / 'Understanding-LLMs-en-v1.0.md').write_text('changed')
            self.assertTrue(any('checksum mismatch' in error for error in validate_release_provenance(destination)))

    def test_release_provenance_rejects_a_tampered_source_digest(self):
        from package_release import package, validate_release_provenance
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'editions.json').write_text(json.dumps({'editions': {'en': {'status':'published'}}}))
            out = root / 'exported/en'; out.mkdir(parents=True)
            artifacts = []
            for name in ('Understanding-LLMs.pdf', 'Understanding-LLMs.epub', 'Understanding-LLMs.print.html', 'Understanding-LLMs.md'):
                data = name.encode()
                (out / name).write_bytes(data)
                artifacts.append({'file':name, 'sha256':hashlib.sha256(data).hexdigest(), 'source_commit':'abc','source_dirty':False,'source_digest':'same'})
            (out / 'manifest.json').write_text(json.dumps({'artifacts':artifacts}))
            destination = root / 'release'
            package(root, destination, 'v1.0', expected_commit='abc')
            record_path = destination / 'release-provenance.json'
            record = json.loads(record_path.read_text())
            record['source_provenance'][0]['source_digest'] = 'wrong'
            record_path.write_text(json.dumps(record))
            self.assertTrue(any('source provenance mismatch' in error for error in validate_release_provenance(destination)))

    def test_release_workflow_validates_and_publishes_release_provenance(self):
        workflow = (Path(__file__).resolve().parents[1] / '.github/workflows/release-books.yml').read_text(encoding='utf-8')
        self.assertIn('validate_release_provenance.py', workflow)
        self.assertIn('release-provenance.json', workflow)
    def test_translation_hash_detects_source_change(self):
        from check_translations import check_hashes
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'index.md').write_text('new source')
            errors=check_hashes(root,[{'id':'intro','path':'index.md'}],{'intro':{'source_sha256':hashlib.sha256(b'old source').hexdigest(),'status':'human-reviewed'}})
            self.assertTrue(any('intro' in e and 'stale' in e for e in errors))

class PDFLogTests(unittest.TestCase):
    def test_pdf_header_maps_common_math_text_symbols(self):
        from export_book_pdf import render_header
        header = render_header('ctexbook', 'Noto Serif CJK SC')
        self.assertIn(r'\newunicodechar{₁}{\ensuremath{_{1}}}', header)
        self.assertIn(r'\newunicodechar{∑}{\ensuremath{\sum}}', header)
        self.assertIn(r'\newunicodechar{✓}{\ensuremath{\checkmark}}', header)

    def test_pdf_watermark_uses_a_rotated_background_text_layer(self):
        from export_book_pdf import render_header
        from watermark import WATERMARK_INTERVAL, display_text

        header = render_header('book', None)
        self.assertEqual(WATERMARK_INTERVAL, 3)
        self.assertEqual(display_text('en'), 'Kingson Wu')
        self.assertIn(r'\AddToHook{shipout/background}', header)
        self.assertIn(r'\usepackage{tikz}', header)
        self.assertIn(r'rotate=-30', header)
        self.assertIn('current page.center', header)
        self.assertIn('text=black!8', header)
        self.assertIn(r'\newcounter{watermarkpage}', header)
        self.assertIn(r'\stepcounter{watermarkpage}', header)
        self.assertIn(r'\ifnum\value{watermarkpage}=3', header)
        self.assertIn(r'\setcounter{watermarkpage}{0}', header)

    def test_pdf_verbatim_symbols_use_ascii_equivalents(self):
        from export_book_pdf import normalize_pdf_verbatim_symbols
        document = {
            'blocks': [
                {'t': 'CodeBlock', 'c': [['', [], []], 'x₁ → ∏ ✓']},
                {'t': 'Para', 'c': [{'t': 'Code', 'c': [['', [], []], 'L₂ = ∑']}]},
            ]
        }
        normalize_pdf_verbatim_symbols(document)
        self.assertEqual(document['blocks'][0]['c'][1], 'x_1 -> prod [ok]')
        self.assertEqual(document['blocks'][1]['c'][0]['c'][1], 'L_2 = sum')

    def test_missing_glyphs_fail_publication(self):
        from export_book_pdf import validate_pdf_log
        with self.assertRaisesRegex(ValueError, 'missing glyph'):
            validate_pdf_log('[WARNING] Missing character: There is no ∇ in font Songti')
        validate_pdf_log('[WARNING] Deprecated option. Output written successfully.')


class PublicationArtifactValidationTests(unittest.TestCase):
    def test_publication_validator_requires_the_embedded_ai_learning_guide(self):
        from validate_publication_artifacts import (
            AI_LEARNING_GUIDE_MARKERS,
            PROVENANCE_MARKERS,
            VISUAL_WATERMARK_MARKER,
            validate_markdown,
        )

        self.assertEqual(AI_LEARNING_GUIDE_MARKERS["zh-Hans"], "用 AI 学习本书")
        self.assertEqual(AI_LEARNING_GUIDE_MARKERS["en"], "Learn This Book with AI")
        self.assertEqual(PROVENANCE_MARKERS["en"], "Copyright © Kingson Wu")
        self.assertEqual(VISUAL_WATERMARK_MARKER, "Kingson Wu")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'Understanding-LLMs.md'
            path.write_text('# Book\n\n## Chapter\n\nLearn This Book with AI')
            self.assertEqual(
                validate_markdown(
                    path,
                    AI_LEARNING_GUIDE_MARKERS['en'],
                    PROVENANCE_MARKERS['en'],
                ),
                ['Markdown is missing the publication provenance'],
            )

    def test_epub_toc_allows_parts_and_chapters_but_rejects_deeper_sections(self):
        from validate_publication_artifacts import epub_toc_depth
        import xml.etree.ElementTree as ET

        nav = ET.fromstring(
            '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">'
            '<nav epub:type="toc"><ol><li><a href="part.xhtml">Part I</a><ol><li><a href="chapter.xhtml">Chapter 1</a><ol><li><a href="chapter.xhtml#section">Section</a></li></ol></li></ol></li></ol></nav>'
            '</html>'
        )
        self.assertEqual(epub_toc_depth(nav), 3)

    def test_pdf_text_bounds_report_overflowing_text(self):
        from validate_publication_artifacts import pdf_text_out_of_bounds

        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / 'bbox.html'
            report.write_text(
                '<doc><page width="100" height="200"><word xMin="90" yMin="10" xMax="105" yMax="20">overflow</word></page></doc>',
                encoding='utf-8',
            )
            self.assertEqual(pdf_text_out_of_bounds(report), ['page 1: overflow'])

    def test_pdf_text_bounds_ignores_only_known_rotated_watermark_fragments(self):
        from validate_publication_artifacts import WATERMARK_BBOX_ARTIFACTS, pdf_text_out_of_bounds

        with tempfile.TemporaryDirectory() as tmp:
            report = Path(tmp) / 'bbox.html'
            report.write_text(
                '<doc><page width="100" height="200">'
                '<word xMin="-2" yMin="10" xMax="5" yMax="20">©</word>'
                '<word xMin="-2" yMin="10" xMax="5" yMax="20">S</word>'
                '<word xMin="90" yMin="10" xMax="105" yMax="20">overflow</word>'
                '</page></doc>',
                encoding='utf-8',
            )
            self.assertEqual(
                pdf_text_out_of_bounds(report, ignored_words=WATERMARK_BBOX_ARTIFACTS),
                ['page 1: overflow'],
            )

    def test_pdf_toc_detects_indented_section_entries(self):
        from validate_publication_artifacts import pdf_toc_has_section_entries

        self.assertTrue(pdf_toc_has_section_entries('  A section . . . . . 17'))
        self.assertFalse(pdf_toc_has_section_entries('Chapter 1: A chapter . . . . . 17'))

    def test_pdf_provenance_requires_the_watermark_identity_in_metadata(self):
        from validate_publication_artifacts import pdf_has_watermark_provenance

        self.assertTrue(pdf_has_watermark_provenance('Subject: Publication watermark · Kingson Wu', 'Kingson Wu'))
        self.assertFalse(pdf_has_watermark_provenance('Subject: Understanding LLMs', 'Kingson Wu'))

    def test_release_workflow_validates_each_generated_edition(self):
        workflow = (Path(__file__).resolve().parents[1] / '.github/workflows/release-books.yml').read_text()

        self.assertIn('qpdf', workflow)
        self.assertIn('python3 tools/book-kit/validate_publication_artifacts.py --locale "$locale"', workflow)

    def test_publication_workflows_run_the_content_manifest_gate_for_available_formats(self):
        root = Path(__file__).resolve().parents[1] / '.github/workflows'
        ci = (root / 'ci.yml').read_text(encoding='utf-8')
        self.assertIn(
            'validate_publication_artifacts.py --locale "$locale" --formats markdown,html,epub',
            ci,
        )
        for name in ('deploy-docs.yml', 'release-books.yml'):
            self.assertIn(
                'validate_publication_artifacts.py --locale "$locale" --formats markdown,html,epub,pdf',
                (root / name).read_text(encoding='utf-8'),
            )

    def test_publication_workflows_preserve_epubcheck_and_pdf_audit_reports(self):
        root = Path(__file__).resolve().parents[1] / '.github/workflows'
        for name in ('ci.yml', 'deploy-docs.yml', 'release-books.yml'):
            workflow = (root / name).read_text(encoding='utf-8')
            self.assertIn('> "$RUNNER_TEMP/epubcheck-$locale.txt" 2>&1', workflow)
            self.assertIn('name: epubcheck-reports', workflow)
            self.assertIn('path: ${{ runner.temp }}/epubcheck-*.txt', workflow)
        for name in ('deploy-docs.yml', 'release-books.yml'):
            workflow = (root / name).read_text(encoding='utf-8')
            audit = workflow.index('name: pdf-formula-audits')
            self.assertIn('if: always()', workflow[max(0, audit - 80):audit])
