"""Assemble versioned artifacts only when every required format has matching provenance."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from book_meta import resolve_book_dir


def package(book: Path, destination: Path, version: str, expected_commit: str) -> dict:
    if not re.fullmatch(r'v[0-9][A-Za-z0-9._-]*', version):
        raise ValueError('Version must be a safe v-prefixed tag')
    editions = json.loads((book / 'editions.json').read_text())['editions']
    pending = []
    for locale, edition in editions.items():
        if edition['status'] != 'published':
            continue
        output = book / 'exported' / locale
        manifest = json.loads((output / 'manifest.json').read_text())
        artifacts = {a['file']: a for a in manifest['artifacts']}
        required = {'book.pdf', 'book.epub', 'book-print.html'}
        if set(artifacts) != required:
            raise ValueError(f'{locale}: incomplete required formats')
        if len({a.get('source_digest') for a in artifacts.values()}) != 1:
            raise ValueError(f'{locale}: formats come from different source bytes')
        for name, artifact in artifacts.items():
            if artifact.get('source_commit') != expected_commit or artifact.get('source_dirty') is not False:
                raise ValueError(f'{locale}: release requires clean tagged source')
            source = output / name
            digest = hashlib.sha256(source.read_bytes()).hexdigest()
            if digest != artifact['sha256']:
                raise ValueError(f'{locale}: artifact checksum mismatch')
            suffix = 'print.html' if name.endswith('html') else name.split('.')[-1]
            target = f'LLMs-for-Backend-Engineers-{locale}-{version}.{suffix}'
            pending.append((source, {**artifact, 'file':target, 'locale':locale}))
    if not pending:
        raise ValueError('No published editions')
    # Validate everything before writing a partial release directory.
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError('Release destination must be empty')
    for source, artifact in pending:
        shutil.copyfile(source, destination / artifact['file'])
    manifest = {'version':version, 'source_commit':expected_commit, 'artifacts':[a for _, a in pending]}
    (destination / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    checksums = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in sorted(destination.iterdir())]
    (destination / 'SHA256SUMS').write_text('\n'.join(checksums) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', required=True)
    parser.add_argument('--output', default='release')
    args = parser.parse_args()
    book = resolve_book_dir(None)
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=book, text=True).strip()
    result = package(book, Path(args.output), args.version, commit)
    print(f"Packaged {len(result['artifacts'])} artifacts into {args.output}")


if __name__ == '__main__':
    main()
