from __future__ import annotations

import argparse
import json
import re
from urllib.parse import urlsplit, urlunsplit
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from book_meta import chapter_paths, load_meta, resolve_book_dir, resolve_build_dir, resolve_source_dir, normalize_locale, load_catalog, render_summary


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a Honkit site for a locale-aware book.")
    parser.add_argument("book_dir", nargs="?", help="Book directory path")
    parser.add_argument("--serve", action="store_true")
    parser.add_argument("--locale", help="Locale to build, for example en or zh-Hans")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove the staged source directory and built output before rebuilding.",
    )
    return parser.parse_args(argv)


def stage_source(book_dir: Path, source_dir: Path, locale: str | None) -> Path:
    stage_root = book_dir / "_build" / "honkit" / normalize_locale(locale)
    stage_src = stage_root / "src"
    if stage_root.exists():
        shutil.rmtree(stage_root)
    stage_src.mkdir(parents=True, exist_ok=True)

    meta = load_meta(book_dir, locale)
    source_files = set(chapter_paths(source_dir))
    source_files.add("SUMMARY.md")
    source_files.add(str(meta.get("readme_path", "README.md")))
    if (source_dir / "README.md").exists():
        source_files.add("README.md")
    source_files.add("book.json")

    for rel_path in sorted(source_files):
        source_path = source_dir / rel_path
        if not source_path.exists():
            raise SystemExit(f"Missing staged source file: {source_path}")
        dest_path = stage_src / rel_path
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest_path)
        if source_path.suffix == ".md":
            def normalize_link(match):
                target = match.group(1)
                url = urlsplit(target)
                if url.scheme or url.netloc or not url.path or Path(url.path).suffix:
                    return match.group(0)
                if (source_path.parent / (url.path + ".md")).is_file():
                    return "](" + urlunsplit(("", "", url.path + ".md", url.query, url.fragment)) + ")"
                return match.group(0)
            dest_path.write_text(re.sub(r"\]\(([^)]+)\)", normalize_link, source_path.read_text(encoding="utf-8")), encoding="utf-8")


    for shared_name in ("assets", "styles", "diagrams"):
        shared_path = book_dir / shared_name
        if not shared_path.exists():
            continue
        dest_path = stage_src / shared_name
        if dest_path.exists() or dest_path.is_symlink():
            if dest_path.is_dir() and not dest_path.is_symlink():
                shutil.rmtree(dest_path)
            else:
                dest_path.unlink()
        shutil.copytree(shared_path, dest_path)

    (stage_src / "SUMMARY.md").write_text(render_summary(load_catalog(source_dir)), encoding="utf-8")
    return stage_src


def locale_codes(book_dir: Path) -> list[str]:
    return [code for code in json.loads((book_dir / "editions.json").read_text())["editions"] if code != "zh-Hans"]


def preserve_locale_builds(book_dir: Path, build_dir: Path, locale: str | None) -> tuple[Path, list[tuple[Path, Path]]]:
    temp_root = Path(tempfile.mkdtemp(prefix="honkit-preserve-"))
    preserved: list[tuple[Path, Path]] = []
    if normalize_locale(locale) != "zh-Hans":
        return temp_root, preserved
    for code in locale_codes(book_dir):
        locale_build = build_dir / code
        if not locale_build.exists():
            continue
        temp_target = temp_root / code
        shutil.move(str(locale_build), str(temp_target))
        preserved.append((temp_target, locale_build))
    return temp_root, preserved


def restore_locale_builds(temp_root: Path, preserved: list[tuple[Path, Path]]) -> None:
    try:
        for temp_source, target in preserved:
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists():
                shutil.rmtree(target)
            shutil.move(str(temp_source), str(target))
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def main() -> None:
    args = parse_args(sys.argv[1:])
    book_dir = resolve_book_dir(args.book_dir)
    source_dir = resolve_source_dir(book_dir, args.locale)
    build_dir = resolve_build_dir(book_dir, args.locale)

    temp_root, preserved = preserve_locale_builds(book_dir, build_dir, args.locale)
    try:
        if args.clean:
            if build_dir.exists():
                shutil.rmtree(build_dir)
            stage_root = book_dir / "_build" / "honkit" / normalize_locale(args.locale)
            if stage_root.exists():
                shutil.rmtree(stage_root)

        stage_src = stage_source(book_dir, source_dir, args.locale)
        build_dir.parent.mkdir(parents=True, exist_ok=True)

        if not (book_dir / "node_modules/.bin/honkit").is_file():
            raise SystemExit("Missing local Honkit; run npm ci in book/ first.")
        subprocess.run(
            [str(book_dir / "node_modules/.bin/honkit"), "serve" if args.serve else "build", str(stage_src), str(build_dir)],
            cwd=book_dir,
            check=True,
        )
    finally:
        restore_locale_builds(temp_root, preserved)

    print(build_dir)


if __name__ == "__main__":
    main()
