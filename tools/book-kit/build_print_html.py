"""Export a portable print edition directly from Markdown (no website required)."""
from publication import parse_args, prepare, finish


def main():
    args = parse_args('Export standalone print HTML with embedded images and CSS.')
    book, source, meta, work, ast = prepare(args, 'html')
    finish(book,meta,'print_html',args,ast,['-t','html5','--mathml','--embed-resources','--css',str(book / 'styles/publication.css')])

if __name__ == '__main__':
    main()
