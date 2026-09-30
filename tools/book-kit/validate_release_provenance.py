#!/usr/bin/env python3
"""Verify a release-origin provenance record against copied download files."""
from __future__ import annotations

import argparse
from pathlib import Path

from package_release import validate_release_provenance


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--release", type=Path, default=Path("release"))
    parser.add_argument("--version")
    parser.add_argument("--commit")
    args = parser.parse_args()
    errors = validate_release_provenance(args.release, expected_version=args.version, expected_commit=args.commit)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"Release provenance is valid: {args.release / 'release-provenance.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
