import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/book-kit'))

class DeliveryTests(unittest.TestCase):
    def test_release_rejects_mismatched_provenance(self):
        from package_release import package
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'editions.json').write_text(json.dumps({'editions': {'en': {'status':'published'}}}))
            out = root / 'exported/en'; out.mkdir(parents=True)
            artifacts=[]
            for name in ('book.pdf','book.epub','book-print.html'):
                (out/name).write_bytes(b'content')
                artifacts.append({'file':name,'sha256':hashlib.sha256(b'content').hexdigest(),'source_commit':'abc','source_dirty':False,'source_digest':name})
            (out/'manifest.json').write_text(json.dumps({'artifacts':artifacts}))
            with self.assertRaisesRegex(ValueError,'source'):
                package(root, root/'release', 'v1.0', expected_commit='abc')
    def test_release_packages_verified_formats_and_manifest_checksums(self):
        from package_release import package
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'editions.json').write_text(json.dumps({'editions': {'en': {'status':'published'}}}))
            out = root / 'exported/en'; out.mkdir(parents=True)
            artifacts = []
            for name in ('book.pdf', 'book.epub', 'book-print.html'):
                data = name.encode()
                (out / name).write_bytes(data)
                artifacts.append({'file':name, 'sha256':hashlib.sha256(data).hexdigest(), 'source_commit':'abc', 'source_dirty':False, 'source_digest':'same'})
            (out / 'manifest.json').write_text(json.dumps({'artifacts':artifacts}))
            destination = root / 'release'
            result = package(root, destination, 'v1.0', expected_commit='abc')
            self.assertEqual(len(result['artifacts']), 3)
            for line in (destination / 'SHA256SUMS').read_text().splitlines():
                digest, name = line.split('  ')
                self.assertEqual(digest, hashlib.sha256((destination / name).read_bytes()).hexdigest())
            self.assertIn('manifest.json', (destination / 'SHA256SUMS').read_text())
            self.assertTrue((destination / 'LLMs-for-Backend-Engineers-en-v1.0.print.html').is_file())
    def test_translation_hash_detects_source_change(self):
        from check_translations import check_hashes
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'index.md').write_text('new source')
            errors=check_hashes(root,[{'id':'intro','path':'index.md'}],{'intro':{'source_sha256':hashlib.sha256(b'old source').hexdigest(),'status':'reviewed-by-agent'}})
            self.assertTrue(any('intro' in e and 'stale' in e for e in errors))

class PDFLogTests(unittest.TestCase):
    def test_pdf_header_maps_common_math_text_symbols(self):
        from export_book_pdf import render_header
        header = render_header('ctexbook', 'Noto Serif CJK SC')
        self.assertIn(r'\newunicodechar{₁}{\ensuremath{_{1}}}', header)
        self.assertIn(r'\newunicodechar{∑}{\ensuremath{\sum}}', header)
        self.assertIn(r'\newunicodechar{✓}{\ensuremath{\checkmark}}', header)

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
