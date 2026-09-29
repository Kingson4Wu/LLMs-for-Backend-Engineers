"""Independent EPUB3 exporter. Pandoc and rsvg-convert are the only dependencies."""
import json
import subprocess
from publication import parse_args, prepare, finish
from watermark import append_provenance, provenance_line


def main():
    args = parse_args('Export EPUB3 with internal navigation and MathML.')
    book, source, meta, work, ast = prepare(args, 'epub')
    document = json.loads(ast.read_text(encoding='utf-8'))
    append_provenance(document, meta['language'])
    ast.write_text(json.dumps(document, ensure_ascii=False), encoding='utf-8')
    extra = ['-t','epub3','--mathml','--css',str(book / 'styles/publication-epub.css'), '-M', f'rights={provenance_line(meta["language"])}']
    if meta.get('cover_image'):
        cover = source / meta['cover_image']
        if not cover.exists():
            cover = book / meta['cover_image']
        if cover.suffix == '.svg':
            png = work / 'cover.png'
            subprocess.run(['rsvg-convert','-w','1600','-o',str(png),str(cover)],check=True)
            cover = png
        extra += ['--epub-cover-image',str(cover)]
    finish(book,meta,'epub',args,ast,extra)

if __name__ == '__main__':
    main()
