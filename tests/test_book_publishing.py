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
    def test_publication_groups_numbered_chapters_under_book_parts(self):
        import export_book_pdf
        import publication

        self.assertEqual(publication.TOC_DEPTH, 2)
        self.assertEqual(export_book_pdf.TOC_DEPTH, 1)
        document = publication.build_document(ROOT / 'book', ROOT / 'book')
        headers = [node['c'] for node in publication.walk(document) if node.get('t') == 'Header']
        index = next(index for index, (_, attributes, _) in enumerate(headers) if attributes[0] == 'math-foundations')
        part_level, _, part_title = headers[index]
        chapter_level, chapter_attributes, chapter_title = headers[index + 1]
        self.assertEqual(part_level, 1)
        self.assertEqual(''.join(item['c'] for item in part_title if item['t'] == 'Str'), '第一部分：数学与机器学习基础')
        self.assertEqual(chapter_level, 2)
        self.assertEqual(chapter_attributes[0], 'ai-math-foundations')
        self.assertTrue(''.join(item['c'] for item in chapter_title if item['t'] == 'Str').startswith('第1章：'))

        appendix = next(
            (level, attributes, title)
            for level, attributes, title in headers
            if attributes[0] == 'learning-resources'
        )
        self.assertEqual(appendix[0], 2)
        self.assertEqual(
            ''.join(item['c'] for item in appendix[2] if item['t'] == 'Str'),
            '附录A：推荐学习资料',
        )
        learning_guide = next(
            (level, attributes, title)
            for level, attributes, title in headers
            if attributes[0] == 'ai-learning-guide'
        )
        self.assertEqual(learning_guide[0], 2)
        self.assertEqual(
            ''.join(item['c'] for item in learning_guide[2] if item['t'] == 'Str'),
            '附录B：用AI学习本书',
        )
        intro_section = next(
            attributes
            for _, attributes, _ in headers
            if attributes[0] == 'introduction--ai-的范围与本书的位置'
        )
        self.assertIn('unlisted', intro_section[1])

        pdf_document = publication.build_document(ROOT / 'book', ROOT / 'book', for_pdf=True)
        pdf_headers = [node['c'] for node in publication.walk(pdf_document) if node.get('t') == 'Header']
        pdf_intro = next(header for header in pdf_headers if header[1][0] == 'introduction')
        pdf_intro_section = next(
            header for header in pdf_headers if header[1][0] == 'introduction--ai-的范围与本书的位置'
        )
        self.assertEqual(pdf_intro[0], 2)
        self.assertEqual(pdf_intro_section[0], 3)

    def test_figures_are_not_nested_directly_inside_ordered_list_items(self):
        sources = list((ROOT / 'book/chapters').rglob('*.md'))
        sources.extend((ROOT / 'book/translations/en/chapters').rglob('*.md'))
        offenders = []
        for path in sources:
            lines = path.read_text(encoding='utf-8').splitlines()
            for index, line in enumerate(lines[:-1]):
                if re.match(r'^\d+\.\s+', line) and re.match(r'^\s+!\[', lines[index + 1]):
                    offenders.append(f'{path.relative_to(ROOT).as_posix()}:{index + 2}')
        self.assertEqual(offenders, [])

    def test_english_math_operators_are_not_emitted_as_plain_text(self):
        sources = (ROOT / 'book/translations/en/chapters').rglob('*.md')
        offenders = [
            path.relative_to(ROOT).as_posix()
            for path in sources
            if re.search(r'[∏∑]', path.read_text(encoding='utf-8'))
        ]
        self.assertEqual(offenders, [])

    def test_fenced_code_blocks_are_separated_from_preceding_paragraphs(self):
        sources = list((ROOT / 'book/chapters').rglob('*.md'))
        sources.extend((ROOT / 'book/translations/en/chapters').rglob('*.md'))
        fence = re.compile(r'^(?:```|~~~)[A-Za-z0-9_+-]+')
        offenders = []
        for path in sources:
            lines = path.read_text(encoding='utf-8').splitlines()
            for index, line in enumerate(lines[1:], start=1):
                if fence.match(line) and lines[index - 1].strip():
                    offenders.append(f'{path.relative_to(ROOT).as_posix()}:{index + 1}')
        self.assertEqual(offenders, [])

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
        self.assertIn(r'-1 < x < 0', formulas)
        self.assertIn(
            '\n\\hat{y} = \\text{ReLU}(x+1) + \\text{ReLU}(x) + \\text{ReLU}(x-1)\n',
            formulas,
        )

class ExportArtifactTests(unittest.TestCase):
    def test_markdown_export_uses_portable_assets_and_internal_anchors(self):
        import subprocess

        for locale in ('zh-Hans', 'en'):
            subprocess.run(
                [sys.executable, str(ROOT / 'tools/book-kit/export_markdown.py'), '--locale', locale],
                check=True,
                capture_output=True,
            )
            text = (ROOT / 'book/exported' / locale / 'Understanding-LLMs.md').read_text(encoding='utf-8')
            image_targets = re.findall(r'!\[[^]]*\]\(([^)\s]+)', text)
            self.assertTrue(image_targets)
            self.assertTrue(
                all(target.startswith('https://kingson4wu.github.io/Understanding-LLMs/assets/') for target in image_targets),
                f'{locale} Markdown must use absolute public asset URLs',
            )
            self.assertNotRegex(text, r'(?<!!)\[[^]]+\]\([^)]*\.md(?:#|\))')
            anchor_ids = set(re.findall(r'<a id="([^"]+)"></a>', text))
            internal_targets = re.findall(r'(?<!!)\[[^]]+\]\(#([^)]*)\)', text)
            self.assertTrue(internal_targets)
            self.assertTrue(set(internal_targets).issubset(anchor_ids))

    def test_markdown_export_links_its_contents_to_parts_and_chapters(self):
        import subprocess

        for locale in ('zh-Hans', 'en'):
            subprocess.run(
                [sys.executable, str(ROOT / 'tools/book-kit/export_markdown.py'), '--locale', locale],
                check=True,
                capture_output=True,
            )
            text = (ROOT / 'book/exported' / locale / 'Understanding-LLMs.md').read_text(encoding='utf-8')
            self.assertRegex(text, r'- \[[^\]]+\]\(#part-1\)')
            self.assertRegex(text, r'  - \[[^\]]+\]\(#[a-z0-9-]+\)')

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
        html = Inspector(); html.feed((output/'Understanding-LLMs.print.html').read_text())
        html_text = (output / 'Understanding-LLMs.print.html').read_text(encoding='utf-8')
        self.assertIn('ai-learning-guide', html_text)
        self.assertIn('用 AI 学习本书', html_text)
        self.assertEqual(len(html.ids), len(set(html.ids)))
        self.assertTrue(all(link[1:] in html.ids for link in html.links if link.startswith('#')))
        self.assertTrue(all(url.startswith(('data:', '../../assets/')) for url in html.resources))
        with zipfile.ZipFile(output/'Understanding-LLMs.epub') as archive:
            self.assertEqual(archive.read('mimetype'), b'application/epub+zip')
            opf = ET.fromstring(archive.read('EPUB/content.opf'))
            self.assertEqual(opf.attrib['version'], '3.0')
            self.assertTrue(any(node.attrib.get('properties') == 'cover-image' and node.attrib.get('media-type') == 'image/png' for node in opf.iter()))
            self.assertTrue(any(b'<math' in archive.read(name) for name in archive.namelist() if name.endswith('.xhtml')))
            self.assertTrue(
                any(
                    '用 AI 学习本书'.encode('utf-8') in archive.read(name)
                    for name in archive.namelist()
                    if name.endswith('.xhtml')
                )
            )
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
            epub = out / 'Understanding-LLMs.epub'
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
            html = out / 'Understanding-LLMs.print.html'
            html.write_bytes(b'new html')
            (out / 'Understanding-LLMs.pdf').write_bytes(b'unrecorded pdf')
            write_manifest(book, 'zh-Hans', html, current)
            manifest = json.loads((out / 'manifest.json').read_text())
            records = {item['file']: item for item in manifest['artifacts']}
            self.assertEqual(set(records), {'Understanding-LLMs.epub', 'Understanding-LLMs.print.html'})
            self.assertEqual(records['Understanding-LLMs.epub']['source_commit'], original['source_commit'])
            self.assertEqual(records['Understanding-LLMs.print.html']['source_commit'], current['source_commit'])
            self.assertEqual(records['Understanding-LLMs.epub']['source_digest'], original['source_digest'])
            self.assertEqual(records['Understanding-LLMs.print.html']['source_digest'], current['source_digest'])
            epub.write_bytes(b'tampered epub')
            write_manifest(book, 'zh-Hans', html, current)
            manifest = json.loads((out / 'manifest.json').read_text())
            self.assertEqual([item['file'] for item in manifest['artifacts']], ['Understanding-LLMs.print.html'])

if __name__ == '__main__':
    unittest.main()
