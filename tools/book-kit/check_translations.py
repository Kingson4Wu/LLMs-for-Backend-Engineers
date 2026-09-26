"""Validate translation coverage and detect stale source hashes (not editorial quality)."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from book_meta import catalog_entries, part_entries, load_catalog, resolve_book_dir


def check_hashes(book: Path, entries: list[dict], articles: dict) -> list[str]:
    errors = []
    expected = {entry['id'] for entry in entries}
    if set(articles) != expected:
        errors.append('Translation status must cover exactly the catalog article IDs')
    for entry in entries:
        state = articles.get(entry['id'], {})
        digest = hashlib.sha256((book / entry['path']).read_bytes()).hexdigest()
        if state.get('source_sha256') != digest:
            errors.append(f"{entry['id']}: stale translation, source hash changed")
        if state.get('status') not in ('reviewed-by-agent', 'human-reviewed'):
            errors.append(f"{entry['id']}: incomplete review status")
    return errors


def main():
    book = resolve_book_dir(None)
    registry = json.loads((book / 'editions.json').read_text())
    default_catalog = load_catalog(book)
    entries = catalog_entries(default_catalog) + part_entries(default_catalog)
    errors = []
    for code, edition in registry['editions'].items():
        if code == registry['default'] or edition['status'] != 'published':
            continue
        source = book / edition['source']
        status = json.loads((source / 'status.json').read_text())
        if status.get('version') != 1 or status.get('locale') != code:
            errors.append(f'{code}: invalid translation status schema')
        errors.extend(check_hashes(book, entries, status.get('articles', {})))
        translated_catalog = load_catalog(source)
        translated = catalog_entries(translated_catalog) + part_entries(translated_catalog)
        if [e['id'] for e in entries] != [e['id'] for e in translated]:
            errors.append(f'{code}: article order differs from source')
    if errors:
        raise SystemExit('\n'.join(errors))
    print('Published translation coverage and source hashes are current. Human editorial quality is not implied.')


if __name__ == '__main__':
    main()
