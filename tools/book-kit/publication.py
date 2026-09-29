"""Shared Pandoc AST pipeline; each chapter retains its own anchor namespace."""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from urllib.parse import unquote, urlsplit
from book_meta import APPENDIX_PREFIX_RE, load_catalog, load_meta, normalize_locale, resolve_book_dir, resolve_source_dir

TOC_DEPTH = 2


def walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk(child)


def heading_inlines(text: str) -> list[dict]:
    tokens: list[dict] = []
    for fragment in text.split(" "):
        if tokens:
            tokens.append({"t": "Space"})
        tokens.append({"t": "Str", "c": fragment})
    return tokens


def part_heading(part: dict, index: int, *, english: bool) -> str:
    if index < 4:
        roman = ("I", "II", "III", "IV")[index]
        return f"Part {roman}: {part['title']}" if english else f"第{'一二三四'[index]}部分：{part['title']}"
    return part["title"]


def chapter_heading(entry: dict, number: int, *, appendix: bool, english: bool) -> str:
    if appendix:
        title = entry['title']
        if match := APPENDIX_PREFIX_RE.match(title):
            title = match.group(2)
        label = chr(ord("A") + number - 1)
        return f"Appendix {label}: {title}" if english else f"附录 {label}：{title}"
    return f"Chapter {number}: {entry['title']}" if english else f"第{number}章：{entry['title']}"


def build_document(book_dir: Path, source: Path, *, for_pdf: bool = False) -> dict:
    catalog = load_catalog(source)
    english = source != book_dir
    documents = []
    anchors = {}

    def parse_entry(
        entry: dict, *, header_offset: int, title: str, hide_subheadings_from_toc: bool = False
    ) -> tuple[Path, dict]:
        path = (source / entry['path']).resolve()
        result = subprocess.run(['pandoc', '-f', 'markdown+tex_math_single_backslash', '-t', 'json', str(path)], check=True, capture_output=True, text=True)
        doc = json.loads(result.stdout)
        first = True
        for node in walk(doc):
            if node.get('t') == 'Header':
                old = node['c'][1][0]
                new = entry['id'] if first else entry['id'] + '--' + old
                first = False
                anchors[(path, old)] = new
                node['c'][1][0] = new
                node['c'][0] = min(6, node['c'][0] + header_offset)
                if new == entry['id']:
                    node['c'][2] = heading_inlines(title)
                elif hide_subheadings_from_toc:
                    node['c'][1][1].append('unlisted')
        anchors[(path, '')] = entry['id']
        if first:
            doc['blocks'].insert(0, {'t':'Header','c':[1 + header_offset,[entry['id'],[],[]],heading_inlines(title)]})
        return path, doc

    for entry in catalog['frontmatter']:
        documents.append(
            parse_entry(
                entry,
                header_offset=1 if for_pdf else 0,
                title=entry['title'],
                hide_subheadings_from_toc=True,
            )
        )

    chapter_number = 0
    appendix_number = 0
    for part_index, part in enumerate(catalog['parts']):
        documents.append((None, {'blocks': [{'t': 'Header', 'c': [1, [part['id'], [], []], heading_inlines(part_heading(part, part_index, english=english))]}]}))
        for entry in part['chapters']:
            appendix = part['id'] == 'appendix'
            if appendix:
                appendix_number += 1
            else:
                chapter_number += 1
            documents.append(
                parse_entry(
                    entry,
                    header_offset=1,
                    title=chapter_heading(
                        entry,
                        appendix_number if appendix else chapter_number,
                        appendix=appendix,
                        english=english,
                    ),
                )
            )

    for path, doc in documents:
        if path is None:
            continue
        for node in walk(doc):
            if node.get('t') not in ('Link', 'Image'):
                continue
            target = node['c'][2][0]
            url = urlsplit(target)
            if url.scheme or url.netloc:
                continue
            dest = (path.parent / unquote(url.path)).resolve() if url.path else path
            if node['t'] == 'Link':
                candidates = [dest, dest.with_suffix('.md')] if dest.suffix in ('', '.html') else [dest]
                chapter = next((p for p in candidates if (p, '') in anchors), None)
                if chapter:
                    key = (chapter, unquote(url.fragment))
                    if key not in anchors:
                        raise ValueError(f'Unknown chapter fragment: {path}: {target}')
                    node['c'][2][0] = '#' + anchors[key]
                    continue
            if not dest.is_file():
                # Localized editions share assets with the default edition.
                # Source posts use site-root asset URLs. Resolve those against
                # the book asset tree for portable HTML, EPUB, and PDF builds.
                dest = (book_dir / unquote(url.path).lstrip('/')).resolve()
            if not dest.is_file():
                raise ValueError(f'Missing local resource: {path}: {target}')
            node['c'][2][0] = str(dest)
    combined = documents[0][1]
    combined['blocks'] = [block for _, doc in documents for block in doc['blocks']]
    return combined


def parse_args(description, argv=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('book_dir', nargs='?')
    parser.add_argument('--locale', default='zh-Hans')
    parser.add_argument('--draft', action='store_true')
    parser.add_argument('--clean', action='store_true')
    return parser.parse_args(argv)


def prepare(args, kind):
    book = resolve_book_dir(args.book_dir)
    source = resolve_source_dir(book, args.locale)
    meta = load_meta(book, args.locale)
    work = book / '_build' / kind / normalize_locale(args.locale)
    if args.clean and work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True, exist_ok=True)
    provenance = source_provenance(book, source)
    document = build_document(book, source, for_pdf=kind == 'pdf')
    for key in ('title','author','language'):
        document['meta'][('lang' if key == 'language' else key)] = {'t':'MetaString','c':str(meta[key])}
    if args.draft:
        document['meta']['subtitle'] = {'t':'MetaString','c':'Draft'}
    ast = work / 'book.json'
    ast.write_text(json.dumps(document, ensure_ascii=False), encoding='utf-8')
    (work / 'provenance.json').write_text(json.dumps(provenance), encoding='utf-8')
    return book, source, meta, work, ast


def source_provenance(book, source):
    """Fingerprint source bytes, including uncommitted and untracked inputs."""
    try:
        revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=book, text=True, stderr=subprocess.DEVNULL).strip()
        dirty = bool(subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=normal'], cwd=book, text=True).strip())
    except (subprocess.CalledProcessError, FileNotFoundError):
        revision, dirty = None, None
    excluded = {'_build', '_book', 'exported', 'node_modules', '__pycache__', '.git'}
    roots = {'edition': source, 'shared-assets': book / 'assets', 'shared-styles': book / 'styles',
             'shared-diagrams': book / 'diagrams', 'pipeline': book.parent / 'tools/book-kit'}
    digest = hashlib.sha256()
    for label, root in sorted(roots.items()):
        if not root.is_dir():
            continue
        for path in sorted(root.rglob('*')):
            relative = path.relative_to(root)
            if not path.is_file() or excluded.intersection(relative.parts):
                continue
            if label == 'edition' and relative.parts[0] == 'translations':
                continue
            digest.update((label + '/' + relative.as_posix()).encode('utf-8') + b'\0')
            digest.update(hashlib.sha256(path.read_bytes()).digest())
    return {'source_commit': revision, 'source_dirty': dirty, 'source_digest': digest.hexdigest()}


def write_manifest(book, locale, artifact, provenance):
    """Record only verified artifacts; never relabel an older export as current."""
    code = normalize_locale(locale)
    out = book / 'exported' / code
    manifest_path = out / 'manifest.json'
    previous = json.loads(manifest_path.read_text()) if manifest_path.is_file() else {}
    artifacts = {}
    for entry in previous.get('artifacts', []):
        name = entry.get('file')
        if name not in ('Understanding-LLMs.print.html', 'Understanding-LLMs.pdf', 'Understanding-LLMs.epub', 'Understanding-LLMs.md') or 'source_digest' not in entry:
            continue
        path = out / name
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == entry.get('sha256'):
            artifacts[name] = entry
    if artifact.parent != out or artifact.name not in ('Understanding-LLMs.print.html', 'Understanding-LLMs.pdf', 'Understanding-LLMs.epub', 'Understanding-LLMs.md'):
        raise ValueError(f'Unexpected publication artifact: {artifact}')
    artifacts[artifact.name] = {'file': artifact.name, 'bytes': artifact.stat().st_size,
                               'sha256': hashlib.sha256(artifact.read_bytes()).hexdigest(),
                               'built_at': dt.datetime.now(dt.timezone.utc).isoformat(), **provenance}
    manifest = {'version': 2, 'locale': code, 'artifacts': [artifacts[name] for name in sorted(artifacts)]}
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n')


def finish(book, meta, kind, args, ast, extra):
    output = book / meta['outputs'][kind]
    output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['pandoc',str(ast),'-f','json','--standalone','--toc',f'--toc-depth={TOC_DEPTH}',*extra,'-o',str(output)],check=True,cwd=book)
    provenance = json.loads((ast.parent / 'provenance.json').read_text())
    write_manifest(book, args.locale, output, provenance)
    print(output)
    return output
