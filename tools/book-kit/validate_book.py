"""Validate catalog coverage, generated navigation and edition configuration."""
import argparse
import json
from book_meta import load_catalog, render_summary, resolve_book_dir, resolve_source_dir


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('book_dir', nargs='?')
    parser.add_argument('--locale', default='zh-Hans')
    parser.add_argument('--write-summary', action='store_true')
    parser.add_argument('--check-links', action='store_true', help='Validate chapter fragments and local resources using Pandoc')
    args = parser.parse_args()
    book = resolve_book_dir(args.book_dir)
    source = resolve_source_dir(book,args.locale)
    catalog = load_catalog(source)
    expected = render_summary(catalog)
    summary = source / 'SUMMARY.md'
    if args.write_summary:
        summary.write_text(expected,encoding='utf-8')
    if not summary.exists() or summary.read_text(encoding='utf-8') != expected:
        raise SystemExit('SUMMARY.md differs from catalog; run validate_book.py --write-summary')
    default_ids = [c['id'] for p in load_catalog(book)['parts'] for c in p['chapters']]
    ids = [c['id'] for p in catalog['parts'] for c in p['chapters']]
    if ids != default_ids:
        raise SystemExit('Edition chapter identities/order must match the default catalog')
    if args.check_links:
        from publication import build_document
        build_document(book, source)
    print(f'Valid {args.locale}: {len(ids)} chapters, {len(catalog["frontmatter"])} frontmatter entries')

if __name__ == '__main__':
    main()
