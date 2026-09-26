"""Write the unified, namespaced Pandoc JSON document for inspection/reuse."""
from publication import parse_args, prepare


def main():
    args = parse_args(__doc__)
    *_, ast = prepare(args, 'pandoc')
    print(ast)

if __name__ == '__main__':
    main()
