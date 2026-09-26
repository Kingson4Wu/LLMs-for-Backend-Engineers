import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools' / 'book-kit'))


class FigureValidationTests(unittest.TestCase):
    def test_manifest_requires_each_editorial_svg_and_accessible_metadata(self):
        from validate_figures import validate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / 'book' / 'assets'
            assets.mkdir(parents=True)
            (assets / 'diagram.svg').write_text(
                '<svg role="img"><title>Diagram</title><desc>Explains a flow.</desc></svg>',
                encoding='utf-8',
            )
            manifest = root / 'figures.json'
            manifest.write_text(
                json.dumps({'figures': [{'path': 'book/assets/diagram.svg', 'kind': 'diagram'}]}),
                encoding='utf-8',
            )
            self.assertEqual(validate(root, manifest), [])

            (assets / 'diagram.svg').write_text('<svg></svg>', encoding='utf-8')
            errors = validate(root, manifest)
            self.assertTrue(any('role="img"' in error for error in errors))
            self.assertTrue(any('<title>' in error for error in errors))
            self.assertTrue(any('<desc>' in error for error in errors))

    def test_manifest_flags_unlisted_svg_assets(self):
        from validate_figures import validate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / 'book' / 'assets'
            assets.mkdir(parents=True)
            (assets / 'unlisted.svg').write_text('<svg></svg>', encoding='utf-8')
            manifest = root / 'figures.json'
            manifest.write_text(json.dumps({'figures': []}), encoding='utf-8')
            self.assertTrue(any('not listed' in error for error in validate(root, manifest)))
