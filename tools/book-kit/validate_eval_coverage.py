#!/usr/bin/env python3
"""Require evidence when a high-risk source chapter changes.

This intentionally consumes a file list supplied by CI instead of invoking Git:
the resulting decision is reproducible locally and does not depend on checkout
depth or credentials.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


def _load_json(path: Path) -> tuple[object | None, list[str]]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), []
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"coverage policy: cannot read {path}: {exc}"]


def _nonempty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _date(value: object) -> bool:
    if not _nonempty_string(value):
        return False
    try:
        dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def load_policy(root: Path) -> tuple[dict[str, object], list[str]]:
    """Load a deliberately small, reviewable policy file."""
    data, errors = _load_json(root / "evals" / "coverage-policy.json")
    if errors:
        return {}, errors
    if not isinstance(data, dict):
        return {}, ["coverage policy: top-level value must be an object"]
    if data.get("version") != 1:
        errors.append("coverage policy: version must be 1")

    rules = data.get("rules")
    if not isinstance(rules, list) or not rules:
        errors.append("coverage policy: rules must be a non-empty list")
        rules = []
    prefixes: set[str] = set()
    for index, rule in enumerate(rules):
        prefix = f"policy rule {index}"
        if not isinstance(rule, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        family, path_prefix = rule.get("family"), rule.get("path_prefix")
        if not _nonempty_string(family):
            errors.append(f"{prefix}: family must be a non-empty string")
        if not _nonempty_string(path_prefix) or not path_prefix.endswith("/"):
            errors.append(f"{prefix}: path_prefix must be a non-empty directory prefix")
        elif path_prefix in prefixes:
            errors.append(f"{prefix}: duplicate path_prefix")
        else:
            prefixes.add(path_prefix)

    exceptions = data.get("exceptions")
    if not isinstance(exceptions, list):
        errors.append("coverage policy: exceptions must be a list")
        exceptions = []
    seen_exceptions: set[tuple[str, str]] = set()
    for exception in exceptions:
        chapter = exception.get("chapter") if isinstance(exception, dict) else None
        label = chapter if _nonempty_string(chapter) else "<missing>"
        prefix = f"exception:{label}"
        if not isinstance(exception, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        family = exception.get("family")
        if not _nonempty_string(chapter):
            errors.append(f"{prefix}: chapter must be a non-empty string")
        if not _nonempty_string(family):
            errors.append(f"{prefix}: family must be a non-empty string")
        elif _nonempty_string(chapter):
            key = (chapter, family)
            if key in seen_exceptions:
                errors.append(f"{prefix}: duplicate exception for family {family}")
            seen_exceptions.add(key)
        if not _nonempty_string(exception.get("reviewer")):
            errors.append(f"{prefix}: reviewer must be a non-empty string")
        if not _date(exception.get("reviewed_at")):
            errors.append(f"{prefix}: reviewed_at must be an ISO date")
        if not _nonempty_string(exception.get("reason")):
            errors.append(f"{prefix}: reason must be a non-empty string")
    return data, errors


def covered_chapters(root: Path) -> set[str]:
    """Return chapters evidenced by an executable claim or formula case.

    Source-review locks attest to a case already selected for review; by
    themselves they are neither an evaluation nor proof that one exists.
    ``validate_evals.py`` validates those locks against their associated cases.
    """
    covered: set[str] = set()
    for directory, key in ((root / "evals" / "claims", "cases"), (root / "evals" / "formulas", "cases")):
        for path in sorted(directory.glob("*.json")):
            data, _ = _load_json(path)
            if not isinstance(data, dict) or not isinstance(data.get(key), list):
                continue
            for record in data[key]:
                if isinstance(record, dict) and _nonempty_string(record.get("chapter")):
                    covered.add(record["chapter"])
    return covered


def _changed_high_risk_chapters(policy: dict[str, object], changed_files: set[str]) -> set[tuple[str, str]]:
    changed: set[tuple[str, str]] = set()
    rules = policy.get("rules", [])
    for changed_file in changed_files:
        normalized = changed_file.replace("\\", "/").lstrip("./")
        for rule in rules if isinstance(rules, list) else []:
            if not isinstance(rule, dict):
                continue
            path_prefix, family = rule.get("path_prefix"), rule.get("family")
            if (
                _nonempty_string(path_prefix)
                and _nonempty_string(family)
                and normalized.startswith(path_prefix)
                and normalized.endswith(".md")
            ):
                chapter = Path(normalized).stem
                changed.add((chapter, family))
    return changed


def validate_changed_chapters(root: Path, changed_files: set[str]) -> list[str]:
    """Validate changed file paths against policy; an empty input is valid."""
    policy, errors = load_policy(root)
    if errors:
        return errors
    covered = covered_chapters(root)
    exceptions = {
        (item["chapter"], item["family"])
        for item in policy.get("exceptions", [])
        if isinstance(item, dict)
        and _nonempty_string(item.get("chapter"))
        and _nonempty_string(item.get("family"))
    }
    for chapter, family in sorted(_changed_high_risk_chapters(policy, changed_files)):
        if chapter not in covered and (chapter, family) not in exceptions:
            errors.append(
                f"high-risk changed chapter lacks evaluation coverage: {chapter} ({family})"
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--changed-file", action="append", default=[])
    args = parser.parse_args()
    errors = validate_changed_chapters(args.root.resolve(), set(args.changed_file))
    if errors:
        print("Evaluation coverage validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Evaluation coverage validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
