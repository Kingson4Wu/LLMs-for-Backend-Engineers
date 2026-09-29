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
        "A bilingual, engineering-focused guide to large language models and their production systems.",
        "",
        "## Downloads",
        "",
        "- **English edition:** Markdown, PDF, EPUB, and print HTML",
        "- **Simplified Chinese edition:** Markdown, PDF, EPUB, and print HTML",
        "",
        "All eight publication files are attached to this release.",
        "",
        "## Changes",
    ]
    if changes:
        lines.extend(f"- {subject}" for subject in changes)
    else:
        lines.append("- No commit summaries are available for this tag.")
    lines.extend(
        [
            "",
            "## Integrity",
            f"- Source commit: `{source_commit}`",
            "- Every format is built from the same tagged source.",
            "- `manifest.json` records publication provenance; `SHA256SUMS` verifies downloaded files.",
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
