"""Export one complete, LLM-friendly Markdown manuscript per language."""
from __future__ import annotations

from pathlib import Path
import re

from book_meta import load_catalog
from publication import parse_args, prepare, write_manifest
from watermark import provenance_line

PUBLIC_ASSET_ROOT = 'https://kingson4wu.github.io/Understanding-LLMs/assets/'
IMAGE_LINK_RE = re.compile(r'(!\[[^]]*\]\()([^\s)]+)(\))')
TEXT_LINK_RE = re.compile(r'(?<!!)\[([^]]+)\]\(([^\s)]+)\)')


def part_heading(part: dict, index: int, english: bool) -> str:
    if index < 4:
        return f"# Part {index + 1}: {part['title']}" if english else f"# 第{'一二三四'[index]}部分：{part['title']}"
    return f"# {part['title']}"


def part_anchor(index: int) -> str:
    return f"part-{index + 1}"


def portable_images(text: str) -> str:
    def replace(match: re.Match) -> str:
        target = match.group(2)
        if 'assets/' not in target or target.startswith(('http://', 'https://', 'data:')):
            return match.group(0)
        return f'{match.group(1)}{PUBLIC_ASSET_ROOT}{target.split("assets/", 1)[1]}{match.group(3)}'

    return IMAGE_LINK_RE.sub(replace, text)


def portable_chapter_links(text: str, source: Path, current_path: str, chapter_ids: dict[Path, str]) -> str:
    def replace(match: re.Match) -> str:
        label, target = match.groups()
        if target.startswith(('http://', 'https://', 'mailto:', '#')):
            return match.group(0)
        target_path, _, _fragment = target.partition('#')
        if not target_path.endswith('.md'):
            return match.group(0)
        candidates = ((source / current_path).parent / target_path, source / target_path)
        for candidate in candidates:
            if chapter_id := chapter_ids.get(candidate.resolve()):
                return f'[{label}](#{chapter_id})'
        return match.group(0)

    return TEXT_LINK_RE.sub(replace, text)


def chapter_text(source: Path, entry: dict, number: int, appendix: bool, english: bool, chapter_ids: dict[Path, str]) -> str:
    text = (source / entry['path']).read_text(encoding='utf-8').strip()
    lines = text.splitlines()
    if lines and lines[0].startswith('# '):
        if appendix:
            prefix = 'Appendix' if english else '附录'
            lines[0] = f"## {prefix}: {entry['title']}"
        elif entry['path'] not in ('index.md', 'preface.md'):
            prefix = f"Chapter {number}" if english else f"第{number}章"
            lines[0] = f"## {prefix}: {entry['title']}"
        lines.insert(0, f'<a id="{entry["id"]}"></a>')
    text = '\n'.join(lines)
    return portable_chapter_links(portable_images(text), source, entry['path'], chapter_ids)


def main() -> None:
    args = parse_args('Export a complete Markdown manuscript for AI-assisted learning.')
    book, source, meta, _work, ast = prepare(args, 'markdown')
    catalog = load_catalog(source)
    english = source != book
    entries = [*catalog['frontmatter'], *(entry for part in catalog['parts'] for entry in part['chapters'])]
    chapter_ids = {(source / entry['path']).resolve(): entry['id'] for entry in entries}
    blocks = [
        f"# {meta['title']}",
        '',
        '> This is the complete single-file Markdown edition. Use it as the primary source for AI-assisted study.' if english else '> 这是完整单文件 Markdown 版书稿。请将它作为 AI 辅助学习的主要材料。',
        '',
        provenance_line(meta['language']),
        '',
        '## Contents' if english else '## 目录',
        '',
    ]
    for index, part in enumerate(catalog['parts']):
        blocks.append(
            f"- [{part_heading(part, index, english).lstrip('# ').strip()}](#{part_anchor(index)})"
        )
        blocks.extend(f"  - [{entry['title']}](#{entry['id']})" for entry in part['chapters'])
    blocks.append('')
    for entry in catalog['frontmatter']:
        blocks.append(chapter_text(source, entry, 0, False, english, chapter_ids))
        blocks.append('')
    number = 0
    for index, part in enumerate(catalog['parts']):
        blocks.extend([f'<a id="{part_anchor(index)}"></a>', part_heading(part, index, english), ''])
        for entry in part['chapters']:
            appendix = part['id'] == 'appendix'
            if not appendix:
                number += 1
            blocks.extend([chapter_text(source, entry, number, appendix, english, chapter_ids), ''])
    output = book / meta['outputs']['markdown']
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text('\n'.join(blocks).strip() + '\n', encoding='utf-8')
    provenance = (ast.parent / 'provenance.json').read_text(encoding='utf-8')
    import json
    write_manifest(book, args.locale, output, json.loads(provenance))
    print(output)


if __name__ == '__main__':
    main()
