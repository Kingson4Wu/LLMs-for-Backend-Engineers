"""Export a portable print edition directly from Markdown (no website required)."""
from publication import parse_args, prepare, finish
from watermark import watermark_html


def main():
    args = parse_args('Export standalone print HTML with embedded images and CSS.')
    book, source, meta, work, ast = prepare(args, 'html')
    watermark = work / 'watermark.html'
    watermark.write_text(watermark_html(meta['language']), encoding='utf-8')
    finish(book,meta,'print_html',args,ast,['-t','html5','--mathml','--embed-resources','--css',str(book / 'styles/publication.css'),'--include-before-body',str(watermark)])

if __name__ == '__main__':
    main()
