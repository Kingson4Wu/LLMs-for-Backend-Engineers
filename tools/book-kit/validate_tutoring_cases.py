#!/usr/bin/env python3
"""Validate offline tutoring-contract cases and render advisory execution reports.

This tool never invokes a model or contacts a network service.  A passing
development case means only that its review instructions remain traceable to
the book; judging tutoring quality remains a human task.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
from pathlib import Path


TOOL_VERSION = "1"
REQUIRED_LABELS = {"book_evidence", "inference", "external_verification"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)


def _catalogue(root: Path, locale: str) -> tuple[Path, dict[str, dict]]:
    source = root / "book" if locale == "zh-Hans" else root / "book" / "translations" / locale
    catalog = json.loads((source / "catalog.json").read_text(encoding="utf-8"))
    entries = list(catalog.get("frontmatter", []))
    entries.extend(
        chapter for part in catalog.get("parts", []) if isinstance(part, dict)
        for chapter in part.get("chapters", []) if isinstance(chapter, dict)
    )
    return source, {entry["id"]: entry for entry in entries if isinstance(entry.get("id"), str)}


def _error(case: dict, message: str) -> str:
    identifier = case.get("id") if isinstance(case.get("id"), str) else "<missing>"
    return f"tutoring:{identifier}: {message}"


def _nonempty(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_case(root: Path, case: object) -> list[str]:
    """Validate one public development case against the Chinese source tree."""
    if not isinstance(case, dict):
        return ["tutoring:<missing>: case must be an object"]
    errors: list[str] = []
    if case.get("schema_version") != 1:
        errors.append(_error(case, "schema_version must be 1"))
    for key in ("id", "learner_task", "comprehension_question", "figure_format_limitations"):
        if not _nonempty(case.get(key)):
            errors.append(_error(case, f"{key} must be a non-empty string"))
    requirements = case.get("artifact_requirements")
    if not isinstance(requirements, dict):
        errors.append(_error(case, "artifact_requirements must be an object"))
    else:
        if requirements.get("locale") not in {"zh-Hans", "en"}:
            errors.append(_error(case, "artifact_requirements.locale must name a supported locale"))
        if requirements.get("complete_format") not in {"markdown", "pdf"}:
            errors.append(_error(case, "artifact_requirements.complete_format must be markdown or pdf"))
        if not _nonempty(requirements.get("file")):
            errors.append(_error(case, "artifact_requirements.file must be a non-empty string"))
    labels = case.get("required_labels")
    if not isinstance(labels, list) or not REQUIRED_LABELS.issubset(set(labels)):
        errors.append(_error(case, "required_labels must include book_evidence, inference, and external_verification"))
    prohibited = case.get("prohibited_claims")
    if not isinstance(prohibited, list) or not prohibited or not all(_nonempty(item) for item in prohibited):
        errors.append(_error(case, "prohibited_claims must be a non-empty list of strings"))

    try:
        locale = requirements.get("locale") if isinstance(requirements, dict) else "zh-Hans"
        source_root, catalogue = _catalogue(root, locale)
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [_error(case, f"cannot read source catalog: {exc}")]
    locations = case.get("source_locations")
    if not isinstance(locations, list) or not locations:
        errors.append(_error(case, "source_locations must be a non-empty list"))
        locations = []
    for index, location in enumerate(locations):
        prefix = f"source_locations[{index}]"
        if not isinstance(location, dict):
            errors.append(_error(case, f"{prefix} must be an object"))
            continue
        chapter = location.get("chapter_id")
        entry = catalogue.get(chapter) if isinstance(chapter, str) else None
        if entry is None:
            errors.append(_error(case, f"{prefix}.chapter_id is absent from the Chinese catalog"))
            continue
        if location.get("title") != entry.get("title"):
            errors.append(_error(case, f"{prefix}.title does not match the catalog"))
        if location.get("path") != entry.get("path"):
            errors.append(_error(case, f"{prefix}.path does not match the catalog"))
        source = source_root / entry["path"]
        headings = {match.group(1).strip() for match in HEADING.finditer(source.read_text(encoding="utf-8"))}
        if location.get("heading") not in headings:
            errors.append(_error(case, f"{prefix}.heading is absent from {entry['path']}"))
    formula = case.get("formula_constraint")
    if formula is not None:
        if not isinstance(formula, dict):
            errors.append(_error(case, "formula_constraint must be an object when present"))
        else:
            formula_location = formula.get("location")
            known_locations = {
                (location.get("chapter_id"), location.get("heading"))
                for location in locations if isinstance(location, dict)
            }
            if (
                not isinstance(formula_location, dict)
                or (formula_location.get("chapter_id"), formula_location.get("heading")) not in known_locations
            ):
                errors.append(_error(case, "formula_constraint.location must match a required source location"))
            if not _nonempty(formula.get("domain")):
                errors.append(_error(case, "formula_constraint.domain must be a non-empty string"))
            golden = formula.get("numeric_golden")
            if not isinstance(golden, dict) or not {"inputs", "expected", "tolerance"}.issubset(golden):
                errors.append(_error(case, "formula_constraint.numeric_golden needs inputs, expected, and tolerance"))
            elif not isinstance(golden["tolerance"], (int, float)) or golden["tolerance"] < 0:
                errors.append(_error(case, "formula_constraint.numeric_golden.tolerance must be non-negative"))
    return errors


def load_development_cases(directory: Path) -> tuple[list[dict], list[str]]:
    cases: list[dict] = []
    errors: list[str] = []
    for path in sorted(directory.glob("*.json")):
        try:
            case = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"tutoring:{path.name}: cannot read case: {exc}")
            continue
        cases.append(case)
    return cases, errors


def _finding(code: str, message: str) -> dict:
    return {"severity": "advisory", "code": code, "message": message}


def evaluate_execution(root: Path, case: dict, execution: object, artifact_path: Path | None) -> dict:
    """Create a deterministic advisory record for a supplied tutoring output."""
    findings: list[dict] = []
    execution = execution if isinstance(execution, dict) else {}
    artifact = execution.get("artifact") if isinstance(execution.get("artifact"), dict) else {}
    requirements = case.get("artifact_requirements", {})
    if execution.get("case_id") != case.get("id"):
        findings.append(_finding("case-id-mismatch", "execution report does not identify this case"))
    for execution_key, requirement_key in (("locale", "locale"), ("format", "complete_format"), ("file", "file")):
        if artifact.get(execution_key) != requirements.get(requirement_key):
            findings.append(_finding("artifact-identity-mismatch", f"artifact {execution_key} does not match the case requirement"))
    actual_digest = None
    if artifact_path is None or not artifact_path.is_file():
        findings.append(_finding("artifact-unavailable", "no readable complete artifact was supplied for hash verification"))
    else:
        actual_digest = hashlib.sha256(artifact_path.read_bytes()).hexdigest()
        if artifact.get("sha256") != actual_digest:
            findings.append(_finding("artifact-sha256-mismatch", "execution report SHA-256 differs from the supplied artifact"))
    transcript = execution.get("transcript") if isinstance(execution.get("transcript"), str) else ""
    for label in case.get("required_labels", []):
        if label not in transcript:
            findings.append(_finding("required-label-missing", f"transcript does not contain required label: {label}"))
    for claim in case.get("prohibited_claims", []):
        if isinstance(claim, str) and claim.lower() in transcript.lower():
            findings.append(_finding("prohibited-claim-present", f"transcript contains prohibited claim: {claim}"))
    observed = execution.get("observed") if isinstance(execution.get("observed"), dict) else {}
    if observed.get("source_locations") != case.get("source_locations"):
        findings.append(_finding("source-locations-unconfirmed", "execution report does not reproduce the required source locations"))
    if not _nonempty(observed.get("comprehension_question")):
        findings.append(_finding("comprehension-question-missing", "execution report does not record a comprehension question"))
    if not observed.get("figure_format_limitations_acknowledged"):
        findings.append(_finding("figure-limitations-unacknowledged", "execution report does not acknowledge figure-format limitations"))
    formula = case.get("formula_constraint")
    if isinstance(formula, dict) and isinstance(formula.get("numeric_golden"), dict):
        expected = formula["numeric_golden"].get("expected")
        answers = observed.get("formula_numeric_answers")
        if not isinstance(answers, list) or expected not in answers:
            findings.append(_finding("formula-golden-unconfirmed", "execution report does not record the expected numerical formula result"))
    return {
        "schema_version": 1,
        "tool": "validate_tutoring_cases",
        "tool_version": TOOL_VERSION,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "case_id": case.get("id"),
        "artifact": {**artifact, "verified_sha256": actual_digest},
        "findings": findings,
        "limitations": "This is an advisory execution template, not a model score; human adjudication decides tutoring quality and factual adequacy.",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--development", action="store_true", help="validate committed public development cases")
    parser.add_argument("--case", type=Path, help="case JSON for an advisory execution report")
    parser.add_argument("--execution-report", type=Path)
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.development:
        cases, errors = load_development_cases(root / "evals" / "tutoring" / "development")
        for case in cases:
            errors.extend(validate_case(root, case))
        if errors:
            print("\n".join(errors))
            return 1
        print(f"Validated {len(cases)} public tutoring development case(s).")
        return 0
    if not (args.case and args.execution_report and args.output):
        parser.error("use --development or provide --case, --execution-report, and --output")
    case = json.loads(args.case.read_text(encoding="utf-8"))
    execution = json.loads(args.execution_report.read_text(encoding="utf-8"))
    report = evaluate_execution(root, case, execution, args.artifact)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote advisory tutoring execution report: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
