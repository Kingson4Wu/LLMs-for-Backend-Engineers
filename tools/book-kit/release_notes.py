"""Create concise, source-linked notes for a versioned book release."""

from __future__ import annotations

import argparse
import re
import subprocess
from pathlib import Path


PREFIX = re.compile(r"^(?:build|chore|ci|docs|feat|fix|refactor|style|test)(?:\([^)]*\))?!?:\s*", re.I)


def render_notes(*, version: str, source_commit: str, commits: list[str]) -> str:
    changes = [PREFIX.sub("", subject).strip() for subject in commits if subject.strip()]
    lines = [
        f"# {version}",
        "",
        "本版本的 PDF、EPUB 与打印 HTML 均由同一 tagged source 构建。",
        "",
        "## 本次更新",
    ]
    if changes:
        lines.extend(f"- {subject}" for subject in changes)
    else:
        lines.append("- 没有可列出的提交说明。")
    lines.extend(
        [
            "",
            "## 来源与校验",
            f"- Source commit: `{source_commit}`",
            "- 下载包中的 `manifest.json` 记录各格式的来源，`SHA256SUMS` 用于校验文件完整性。",
        ]
    )
    return "\n".join(lines) + "\n"


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True).strip()


def commit_subjects(tag: str) -> list[str]:
    try:
        previous = command("git", "describe", "--tags", "--abbrev=0", f"{tag}^")
        revision = f"{previous}..{tag}"
    except subprocess.CalledProcessError:
        revision = tag
    output = command("git", "log", "--format=%s", revision)
    return [line for line in output.splitlines() if line]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source_commit = command("git", "rev-list", "-n", "1", args.tag)
    args.output.write_text(
        render_notes(
            version=args.tag,
            source_commit=source_commit,
            commits=commit_subjects(args.tag),
        )
    )


if __name__ == "__main__":
    main()
