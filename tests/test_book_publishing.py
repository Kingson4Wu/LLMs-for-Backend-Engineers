import json
from pathlib import Path
import re
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools/book-kit'))
import book_meta

class CatalogTests(unittest.TestCase):
    def test_readmes_and_publications_use_locale_specific_covers(self):
        zh_meta = json.loads((ROOT / 'book/book.json').read_text())
        en_meta = json.loads((ROOT / 'book/translations/en/book.json').read_text())
        self.assertEqual(zh_meta['cover_image'], 'assets/cover-zh-Hans.svg')
        self.assertEqual(en_meta['cover_image'], 'assets/cover-en.svg')
        self.assertTrue((ROOT / 'book' / zh_meta['cover_image']).is_file())
        self.assertTrue((ROOT / 'book' / en_meta['cover_image']).is_file())
        self.assertIn('book/assets/cover-zh-Hans.svg', (ROOT / 'README.zh-CN.md').read_text())
        self.assertIn('book/assets/cover-en.svg', (ROOT / 'README.md').read_text())

    def test_catalog_has_all_chapters_once(self):
        paths = book_meta.chapter_paths(ROOT / 'book')
        actual = {p.relative_to(ROOT / 'book').as_posix() for p in (ROOT / 'book/chapters').rglob('*.md')}
        self.assertEqual(len(paths), len(set(paths)))
        self.assertEqual(set(paths) - {'index.md', 'preface.md'}, actual)

    def test_missing_locale_never_falls_back(self):
        with self.assertRaises((ValueError, SystemExit)):
            book_meta.resolve_source_dir(ROOT / 'book', 'not-a-locale')

    def test_locale_alias(self):
        self.assertEqual(book_meta.normalize_locale('zh-hans'), 'zh-Hans')

    def test_duplicate_ids_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'a.md').write_text('# A')
            (root / 'catalog.json').write_text(json.dumps({'version': 1, 'frontmatter': [{'id':'a','path':'a.md','title':'A'},{'id':'a','path':'a.md','title':'A'}], 'parts': []}))
            with self.assertRaises(ValueError):
                book_meta.load_catalog(root)


class PublicationTests(unittest.TestCase):
    def test_display_math_does_not_nest_align_environment(self):
        sources = list((ROOT / 'book/chapters').rglob('*.md'))
        sources.extend((ROOT / 'book/translations/en/chapters').rglob('*.md'))
        nested_align = re.compile(r'\$\$\s*\\begin\{align\}', re.DOTALL)
        offenders = [path.relative_to(ROOT).as_posix() for path in sources if nested_align.search(path.read_text())]
        self.assertEqual(offenders, [])

    def test_ast_links_and_ids(self):
        from publication import build_document, walk
        doc = build_document(ROOT / 'book', ROOT / 'book')
        ids = [n['c'][1][0] for n in walk(doc) if n.get('t') == 'Header']
        self.assertEqual(len(ids), len(set(ids)))
        self.assertIn('introduction', ids)
        links = [n['c'][2][0] for n in walk(doc) if n.get('t') == 'Link']
        self.assertTrue(all(target[1:] in ids for target in links if target.startswith('#')))

    def test_single_backslash_inline_tex_is_math(self):
        from publication import build_document, walk
        source = ROOT / 'book/translations/en'
        doc = build_document(ROOT / 'book', source)
        formulas = [node['c'][1] for node in walk(doc) if node.get('t') == 'Math']
        self.assertIn(r'-1<x<0', formulas)
        self.assertIn(r'\operatorname{ReLU}(x+1)', formulas)

    def test_staging_copies_assets(self):
        from build_honkit import stage_source
        stage = stage_source(ROOT / 'book', ROOT / 'book', 'zh-Hans')
        self.assertFalse((stage / 'assets').is_symlink())
        self.assertTrue((stage / 'assets/cover.svg').is_file())
        chapter = stage / 'chapters/part1-math-foundations/softmax.md'
        self.assertTrue(chapter.is_file())

class ExportArtifactTests(unittest.TestCase):
    def test_real_html_and_epub_exports_are_portable(self):
        import subprocess
        import zipfile
        import xml.etree.ElementTree as ET
        from html.parser import HTMLParser
        class Inspector(HTMLParser):
            def __init__(self):
                super().__init__(); self.ids = []; self.links = []; self.resources = []
            def handle_starttag(self, tag, attrs):
                attrs = dict(attrs)
                if 'id' in attrs: self.ids.append(attrs['id'])
                if tag == 'a': self.links.append(attrs.get('href', ''))
                if tag in ('img', 'script'): self.resources.append(attrs.get('src', ''))
                if tag == 'link': self.resources.append(attrs.get('href', ''))
        for script in ('build_print_html.py', 'export_epub.py'):
            subprocess.run([sys.executable,str(ROOT/'tools/book-kit'/script)], check=True, capture_output=True)
        output = ROOT / 'book/exported/zh-Hans'
        html = Inspector(); html.feed((output/'book-print.html').read_text())
        self.assertEqual(len(html.ids), len(set(html.ids)))
        self.assertTrue(all(link[1:] in html.ids for link in html.links if link.startswith('#')))
        self.assertTrue(all(url.startswith(('data:', '../../assets/')) for url in html.resources))
        with zipfile.ZipFile(output/'book.epub') as archive:
            self.assertEqual(archive.read('mimetype'), b'application/epub+zip')
            opf = ET.fromstring(archive.read('EPUB/content.opf'))
            self.assertEqual(opf.attrib['version'], '3.0')
            self.assertTrue(any(node.attrib.get('properties') == 'cover-image' and node.attrib.get('media-type') == 'image/png' for node in opf.iter()))
            self.assertTrue(any(b'<math' in archive.read(name) for name in archive.namelist() if name.endswith('.xhtml')))
            pages = {name: ET.fromstring(archive.read(name)) for name in archive.namelist() if name.endswith('.xhtml')}
            import posixpath
            from urllib.parse import unquote
            for name, page in pages.items():
                ids = [node.attrib['id'] for node in page.iter() if 'id' in node.attrib]
                self.assertEqual(len(ids),len(set(ids)))
                for node in page.iter():
                    href = node.attrib.get('href','')
                    if '#' not in href or '://' in href: continue
                    path, fragment = href.split('#',1)
                    dest = posixpath.normpath(posixpath.join(posixpath.dirname(name),path)) if path else name
                    self.assertIn(dest,pages)
                    self.assertIn(unquote(fragment),{n.attrib.get('id') for n in pages[dest].iter()})

class ManifestProvenanceTests(unittest.TestCase):
    def test_sequential_exports_preserve_provenance_and_exclude_unrecorded_files(self):
        from publication import source_provenance, write_manifest
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = root / 'book'
            book.mkdir()
            (book / 'chapter.md').write_text('Original content')
            subprocess.run(['git', 'init', '-q', str(root)], check=True)
            subprocess.run(['git', 'add', '.'], cwd=root, check=True)
            subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'Initial'], cwd=root, check=True)
            out = book / 'exported/zh-Hans'
            out.mkdir(parents=True)
            epub = out / 'book.epub'
            epub.write_bytes(b'old epub')
            original = source_provenance(book, book)
            write_manifest(book, 'zh-Hans', epub, original)
            (book / 'chapter.md').write_text('Committed updated content')
            subprocess.run(['git', 'add', 'book/chapter.md'], cwd=root, check=True)
            subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'Second'], cwd=root, check=True)
            (book / 'chapter.md').write_text('Dirty updated content')
            current = source_provenance(book, book)
            self.assertNotEqual(original['source_commit'], current['source_commit'])
            self.assertNotEqual(original['source_digest'], current['source_digest'])
            self.assertTrue(current['source_dirty'])
            html = out / 'book-print.html'
            html.write_bytes(b'new html')
            (out / 'book.pdf').write_bytes(b'unrecorded pdf')
            write_manifest(book, 'zh-Hans', html, current)
            manifest = json.loads((out / 'manifest.json').read_text())
            records = {item['file']: item for item in manifest['artifacts']}
            self.assertEqual(set(records), {'book.epub', 'book-print.html'})
            self.assertEqual(records['book.epub']['source_commit'], original['source_commit'])
            self.assertEqual(records['book-print.html']['source_commit'], current['source_commit'])
            self.assertEqual(records['book.epub']['source_digest'], original['source_digest'])
            self.assertEqual(records['book-print.html']['source_digest'], current['source_digest'])
            epub.write_bytes(b'tampered epub')
            write_manifest(book, 'zh-Hans', html, current)
            manifest = json.loads((out / 'manifest.json').read_text())
            self.assertEqual([item['file'] for item in manifest['artifacts']], ['book-print.html'])

if __name__ == '__main__':
    unittest.main()
