#!/usr/bin/env python3
"""Validate offline, source-backed book-quality evaluation cases."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import math
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


CLAIM_KINDS = {"stable-mechanism", "boundary", "time-sensitive"}
PROVENANCE_TYPES = {"paper", "specification", "official-documentation"}
REVIEW_KEYS = (
    "proposition",
    "conditions_and_quantifiers",
    "formula_symbols_and_units",
    "figure_meaning",
    "link_target",
)
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.MULTILINE)
DISPLAY_MATH = re.compile(r"\$\$\s*(.*?)\s*\$\$", re.DOTALL)


def load_cases(directory: Path) -> list[dict]:
    cases: list[dict] = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return [{"_load_error": f"cannot read {path}: {exc}"}]
        if not isinstance(data, dict) or not isinstance(data.get("cases"), list):
            return [{"_load_error": f"{path} needs a cases list"}]
        cases.extend(data["cases"])
    return cases


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_math(value: str) -> str:
    return " ".join(value.split())


def load_source_locks(directory: Path) -> tuple[list[dict], list[str]]:
    """Load chapter review locks without making an absent directory an error."""
    locks: list[dict] = []
    errors: list[str] = []
    for path in sorted(directory.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"review:{path.name}: cannot read lock file: {exc}")
            continue
        if not isinstance(data, dict) or not isinstance(data.get("locks"), list):
            errors.append(f"review:{path.name}: lock file needs a locks list")
            continue
        locks.extend(data["locks"])
    return locks, errors


def load_provenance(root: Path) -> tuple[dict[str, dict], list[str]]:
    path = root / "evals" / "provenance.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {}, [f"provenance: cannot read registry: {exc}"]
    records = data.get("sources") if isinstance(data, dict) else None
    if not isinstance(records, list):
        return {}, ["provenance: registry needs a sources list"]
    indexed: dict[str, dict] = {}
    errors: list[str] = []
    for record in records:
        if not isinstance(record, dict) or not is_http_url(record.get("url")):
            errors.append("provenance:<missing>: source needs an absolute HTTP(S) URL")
            continue
        url = record["url"]
        if url in indexed:
            errors.append(f"provenance:{url}: duplicate source")
            continue
        indexed[url] = record
        prefix = f"provenance:{url}"
        if record.get("type") not in PROVENANCE_TYPES:
            errors.append(f"{prefix}: type is unsupported")
        for key in ("locator", "published_or_versioned_at", "retrieved_at"):
            value = record.get(key)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{prefix}: {key} must be a non-empty string")
            elif key != "locator":
                try:
                    dt.date.fromisoformat(value)
                except ValueError:
                    errors.append(f"{prefix}: {key} must be an ISO date")
    return indexed, errors


def validate_source_locks(
    root: Path,
    cases: list[object],
    sources: dict[str, Path],
    english_sources: dict[str, Path],
) -> list[str]:
    """Require one reviewed Chinese/English source snapshot per covered chapter."""
    errors: list[str] = []
    covered = {
        case["chapter"]
        for case in cases
        if isinstance(case, dict) and isinstance(case.get("chapter"), str)
    }
    locks, lock_errors = load_source_locks(root / "evals" / "reviews")
    errors.extend(lock_errors)
    indexed: dict[str, dict] = {}
    for lock in locks:
        if not isinstance(lock, dict):
            errors.append("review:<missing>: lock must be an object")
            continue
        chapter = lock.get("chapter")
        prefix = f"review:{chapter if isinstance(chapter, str) and chapter else '<missing>'}"
        if not isinstance(chapter, str) or not chapter:
            errors.append(f"{prefix}: chapter must be a non-empty string")
            continue
        if chapter in indexed:
            errors.append(f"{prefix}: duplicate source lock")
            continue
        indexed[chapter] = lock

    for chapter in sorted(covered):
        prefix = f"review:{chapter}"
        lock = indexed.get(chapter)
        if lock is None:
            errors.append(f"{prefix}: source lock is required for every covered chapter")
            continue
        chinese_source, english_source = sources.get(chapter), english_sources.get(chapter)
        if chinese_source is None or not chinese_source.is_file():
            errors.append(f"{prefix}: Chinese source is missing from catalog")
            continue
        if english_source is None or not english_source.is_file():
            errors.append(f"{prefix}: English source is missing from catalog")
            continue
        for key, source, label in (
            ("zh_digest", chinese_source, "Chinese"),
            ("en_digest", english_source, "English"),
        ):
            expected = lock.get(key)
            if not isinstance(expected, str) or not re.fullmatch(r"[0-9a-f]{64}", expected):
                errors.append(f"{prefix}: {key} must be a lowercase SHA-256 digest")
            elif digest(source) != expected:
                errors.append(f"{prefix}: {label} source digest differs from lock")
        english_text = english_source.read_text(encoding="utf-8")
        headings = {match.group(1).strip() for match in HEADING.finditer(english_text)}
        english_heading = lock.get("english_heading")
        if not isinstance(english_heading, str) or english_heading not in headings:
            errors.append(f"{prefix}: english_heading is absent from English source")
        english_anchor = lock.get("english_anchor_text")
        if not isinstance(english_anchor, str) or english_anchor not in english_text:
            errors.append(f"{prefix}: english_anchor_text is absent from English source")
        reviewed_at = lock.get("reviewed_at")
        try:
            dt.date.fromisoformat(reviewed_at) if isinstance(reviewed_at, str) else None
        except ValueError:
            errors.append(f"{prefix}: reviewed_at must be an ISO date")
        else:
            if not isinstance(reviewed_at, str):
                errors.append(f"{prefix}: reviewed_at must be an ISO date")
        reviewer = lock.get("reviewer")
        if not isinstance(reviewer, str) or not reviewer.strip():
            errors.append(f"{prefix}: reviewer must be a non-empty string")
    return errors


def chapter_sources(root: Path, locale: str = "zh-Hans") -> dict[str, Path]:
    catalog_path = (
        root / "book" / "catalog.json"
        if locale == "zh-Hans"
        else root / "book" / "translations" / locale / "catalog.json"
    )
    try:
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot read {locale} catalog: {exc}") from exc
    entries = list(catalog.get("frontmatter", []))
    entries.extend(
        chapter
        for part in catalog.get("parts", [])
        if isinstance(part, dict)
        for chapter in part.get("chapters", [])
    )
    sources: dict[str, Path] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        identifier, relative = entry.get("id"), entry.get("path")
        if isinstance(identifier, str) and isinstance(relative, str):
            sources[identifier] = catalog_path.parent / relative
    return sources


def is_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def error_prefix(category: str, case: object) -> str:
    identifier = case.get("id") if isinstance(case, dict) else None
    return f"{category}:{identifier if isinstance(identifier, str) and identifier else '<missing>'}"


def required_string(case: dict, key: str, prefix: str, errors: list[str]) -> str | None:
    value = case.get(key)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{prefix}: {key} must be a non-empty string")
        return None
    return value


def validate_review(case: dict, prefix: str, english_sources: dict[str, Path] | None) -> list[str]:
    errors: list[str] = []
    review = case.get("review")
    if not isinstance(review, dict):
        return [f"{prefix}: review must be an object"]
    reviewed_at = review.get("reviewed_at")
    try:
        dt.date.fromisoformat(reviewed_at) if isinstance(reviewed_at, str) else None
    except ValueError:
        errors.append(f"{prefix}: review.reviewed_at must be an ISO date")
    else:
        if not isinstance(reviewed_at, str):
            errors.append(f"{prefix}: review.reviewed_at must be an ISO date")
    if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
        errors.append(f"{prefix}: review.reviewer must be a non-empty string")
    for key in REVIEW_KEYS:
        if review.get(key) is not True:
            errors.append(f"{prefix}: review.{key} must be true")
    english_heading = review.get("english_heading")
    english_anchor = review.get("english_anchor_text")
    if not isinstance(english_heading, str) or not english_heading.strip():
        errors.append(f"{prefix}: review.english_heading must be a non-empty string")
    if not isinstance(english_anchor, str) or not english_anchor.strip():
        errors.append(f"{prefix}: review.english_anchor_text must be a non-empty string")
    if english_sources is not None:
        chapter = case.get("chapter")
        english_source = english_sources.get(chapter) if isinstance(chapter, str) else None
        if english_source is None or not english_source.is_file():
            errors.append(f"{prefix}: English source is missing from catalog")
        else:
            english_text = english_source.read_text(encoding="utf-8")
            headings = {match.group(1).strip() for match in HEADING.finditer(english_text)}
            if isinstance(english_heading, str) and english_heading.strip() and english_heading not in headings:
                errors.append(f"{prefix}: review.english_heading is absent from English source")
            if isinstance(english_anchor, str) and english_anchor.strip() and english_anchor not in english_text:
                errors.append(f"{prefix}: review.english_anchor_text is absent from English source")
    return errors


def validate_source_reference(
    case: dict, prefix: str, sources: dict[str, Path]
) -> tuple[list[str], str]:
    errors: list[str] = []
    chapter = required_string(case, "chapter", prefix, errors)
    heading = required_string(case, "heading", prefix, errors)
    anchor = required_string(case, "anchor_text", prefix, errors)
    source = sources.get(chapter) if chapter else None
    text = ""
    if source is None:
        errors.append(f"{prefix}: chapter is absent from Chinese catalog")
    elif not source.is_file():
        errors.append(f"{prefix}: Chinese source file is missing")
    else:
        text = source.read_text(encoding="utf-8")
        headings = {match.group(1).strip() for match in HEADING.finditer(text)}
        if heading and heading not in headings:
            errors.append(f"{prefix}: heading is absent from source")
        if anchor and anchor not in text:
            errors.append(f"{prefix}: anchor text is absent from source")
    return errors, text


def validate_claim(case: object, sources: dict[str, Path], english_sources: dict[str, Path], provenance: dict[str, dict], seen: set[str]) -> list[str]:
    if not isinstance(case, dict):
        return ["claim:<missing>: case must be an object"]
    prefix = error_prefix("claim", case)
    errors: list[str] = []
    identifier = required_string(case, "id", prefix, errors)
    if identifier and identifier in seen:
        errors.append(f"{prefix}: duplicate id")
    elif identifier:
        seen.add(identifier)
    errors.extend(validate_source_reference(case, prefix, sources)[0])
    kind = required_string(case, "kind", prefix, errors)
    if kind and kind not in CLAIM_KINDS:
        errors.append(f"{prefix}: kind is unsupported")
    source_urls = case.get("sources")
    if not isinstance(source_urls, list) or not source_urls:
        errors.append(f"{prefix}: sources must be a non-empty list")
    elif any(not is_http_url(url) for url in source_urls):
        errors.append(f"{prefix}: source URL must be absolute HTTP(S)")
    elif any(url not in provenance for url in source_urls):
        errors.append(f"{prefix}: every source URL must be registered in provenance.json")
    if kind == "time-sensitive":
        interval = case.get("review_interval_days")
        if isinstance(interval, bool) or not isinstance(interval, int) or interval <= 0:
            errors.append(f"{prefix}: time-sensitive case needs a positive review_interval_days")
        else:
            reviewed_at = case.get("review", {}).get("reviewed_at") if isinstance(case.get("review"), dict) else None
            try:
                review_date = dt.date.fromisoformat(reviewed_at) if isinstance(reviewed_at, str) else None
            except ValueError:
                review_date = None
            if review_date is not None and (dt.date.today() - review_date).days > interval:
                errors.append(f"{prefix}: time-sensitive review interval has elapsed")
    required_string(case, "expectation", prefix, errors)
    if kind == "boundary":
        counterexamples = case.get("must_not_imply")
        if not isinstance(counterexamples, list) or not counterexamples or any(
            not isinstance(item, str) or not item.strip() for item in counterexamples
        ):
            errors.append(f"{prefix}: boundary case needs a non-empty must_not_imply list")
    errors.extend(validate_review(case, prefix, english_sources))
    return errors


def require_finite_vector(inputs: object, key: str) -> list[float]:
    if not isinstance(inputs, dict) or not isinstance(inputs.get(key), list) or not inputs[key]:
        raise ValueError(f"{key} must be a non-empty numeric list")
    values = inputs[key]
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) for value in values):
        raise ValueError(f"{key} must contain only finite numbers")
    return [float(value) for value in values]


def require_distribution(inputs: object, key: str) -> list[float]:
    values = require_finite_vector(inputs, key)
    if any(value <= 0 for value in values):
        raise ValueError("probabilities must be strictly positive")
    if not math.isclose(sum(values), 1.0, rel_tol=0.0, abs_tol=1e-12):
        raise ValueError("probabilities must sum to 1")
    return values


def require_index(value: object, length: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0 or value >= length:
        raise ValueError("target must be a valid probability index")
    return value


def require_positive_number(inputs: object, key: str) -> float:
    if not isinstance(inputs, dict):
        raise ValueError("inputs must be an object")
    value = inputs.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value <= 0:
        raise ValueError(f"{key} must be a positive finite number")
    return float(value)


def require_matrix(inputs: object, key: str) -> list[list[float]]:
    if not isinstance(inputs, dict) or not isinstance(inputs.get(key), list) or not inputs[key]:
        raise ValueError(f"{key} must be a non-empty numeric matrix")
    rows = inputs[key]
    if not all(isinstance(row, list) and row for row in rows):
        raise ValueError(f"{key} must be a non-empty numeric matrix")
    width = len(rows[0])
    if any(len(row) != width for row in rows):
        raise ValueError(f"{key} rows must have equal length")
    if any(isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) for row in rows for value in row):
        raise ValueError(f"{key} must contain only finite numbers")
    return [[float(value) for value in row] for row in rows]


def evaluate_formula(name: str, inputs: dict) -> float | list[float]:
    if name == "softmax":
        logits = require_finite_vector(inputs, "logits")
        maximum = max(logits)
        weights = [math.exp(value - maximum) for value in logits]
        total = sum(weights)
        return [weight / total for weight in weights]
    if name == "cross_entropy_one_hot":
        probabilities = require_distribution(inputs, "probabilities")
        target = require_index(inputs.get("target"), len(probabilities))
        return -math.log(probabilities[target])
    if name == "chain_rule_product":
        return math.prod(require_finite_vector(inputs, "gradients"))
    if name == "temperature_softmax":
        logits = require_finite_vector(inputs, "logits")
        temperature = require_positive_number(inputs, "temperature")
        return evaluate_formula("softmax", {"logits": [value / temperature for value in logits]})
    if name == "masked_attention":
        scores = require_matrix(inputs, "scores")
        values = require_matrix(inputs, "values")
        mask = inputs.get("mask") if isinstance(inputs, dict) else None
        if not isinstance(mask, list) or len(mask) != len(scores) or any(
            not isinstance(row, list) or len(row) != len(scores[0]) or any(not isinstance(item, bool) for item in row)
            for row in mask
        ):
            raise ValueError("mask must be a boolean matrix matching scores")
        if len(scores[0]) != len(values):
            raise ValueError("scores key dimension must match values rows")
        output: list[list[float]] = []
        for score_row, mask_row in zip(scores, mask):
            allowed = [score if allowed else float("-inf") for score, allowed in zip(score_row, mask_row)]
            if not any(mask_row):
                raise ValueError("each attention row must permit at least one key")
            maximum = max(score for score, allowed in zip(score_row, mask_row) if allowed)
            weights = [math.exp(score - maximum) if allowed else 0.0 for score, allowed in zip(score_row, mask_row)]
            total = sum(weights)
            output.append([
                sum(weight * value[column] for weight, value in zip(weights, values)) / total
                for column in range(len(values[0]))
            ])
        return output
    if name == "layer_norm":
        values = require_finite_vector(inputs, "values")
        epsilon = require_positive_number(inputs, "epsilon")
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        return [(value - mean) / math.sqrt(variance + epsilon) for value in values]
    if name == "kv_cache_bytes":
        layers = require_positive_number(inputs, "layers")
        tokens = require_positive_number(inputs, "tokens")
        kv_heads = require_positive_number(inputs, "kv_heads")
        head_dim = require_positive_number(inputs, "head_dim")
        bytes_per_element = require_positive_number(inputs, "bytes_per_element")
        if any(value != int(value) for value in (layers, tokens, kv_heads, head_dim, bytes_per_element)):
            raise ValueError("KV-cache dimensions must be whole numbers")
        return 2 * int(layers) * int(tokens) * int(kv_heads) * int(head_dim) * int(bytes_per_element)
    raise ValueError("evaluator is unsupported")


def values_close(actual: object, expected: object, tolerance: float) -> bool:
    if isinstance(actual, list) and isinstance(expected, list):
        return len(actual) == len(expected) and all(
            values_close(left, right, tolerance) for left, right in zip(actual, expected)
        )
    return (
        not isinstance(actual, bool)
        and not isinstance(expected, bool)
        and isinstance(actual, (int, float))
        and isinstance(expected, (int, float))
        and math.isclose(float(actual), float(expected), rel_tol=0.0, abs_tol=tolerance)
    )


def validate_formula(case: object, sources: dict[str, Path] | None = None, english_sources: dict[str, Path] | None = None, seen: set[str] | None = None) -> list[str]:
    if not isinstance(case, dict):
        return ["formula:<missing>: case must be an object"]
    prefix = error_prefix("formula", case)
    errors: list[str] = []
    identifier = required_string(case, "id", prefix, errors)
    if seen is not None and identifier:
        if identifier in seen:
            errors.append(f"{prefix}: duplicate id")
        else:
            seen.add(identifier)
    if sources is not None:
        source_errors, source_text = validate_source_reference(case, prefix, sources)
        errors.extend(source_errors)
        equation = case.get("formula_anchor")
        fingerprint = case.get("formula_fingerprint")
        if equation is not None or fingerprint is not None:
            if not isinstance(equation, str) or not equation.strip():
                errors.append(f"{prefix}: formula_anchor must be a non-empty display-math string")
            elif not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
                errors.append(f"{prefix}: formula_fingerprint must be a lowercase SHA-256 digest")
            else:
                normalized_equation = normalize_math(equation)
                source_equations = {normalize_math(block) for block in DISPLAY_MATH.findall(source_text)}
                if normalized_equation not in source_equations:
                    errors.append(f"{prefix}: formula_anchor is absent from source display math")
                elif hashlib.sha256(normalized_equation.encode("utf-8")).hexdigest() != fingerprint:
                    errors.append(f"{prefix}: formula_fingerprint differs from formula_anchor")
    evaluator = required_string(case, "evaluator", prefix, errors)
    inputs = case.get("inputs")
    if not isinstance(inputs, dict):
        errors.append(f"{prefix}: inputs must be an object")
    expected = case.get("expected")
    tolerance = case.get("tolerance")
    if isinstance(tolerance, bool) or not isinstance(tolerance, (int, float)) or tolerance < 0:
        errors.append(f"{prefix}: tolerance must be a non-negative number")
    required_string(case, "domain", prefix, errors)
    errors.extend(validate_review(case, prefix, english_sources))
    if errors:
        return errors
    try:
        actual = evaluate_formula(evaluator, inputs)
    except ValueError as exc:
        return [f"{prefix}: {exc}"]
    if not values_close(actual, expected, float(tolerance)):
        return [f"{prefix}: expected value differs from evaluator output"]
    return []


def validate(root: Path) -> list[str]:
    try:
        sources = chapter_sources(root)
        english_sources = chapter_sources(root, "en")
    except ValueError as exc:
        return [str(exc)]
    errors: list[str] = []
    provenance, provenance_errors = load_provenance(root)
    errors.extend(provenance_errors)
    seen: set[str] = set()
    all_cases: list[object] = []
    for category, validator in (("claims", validate_claim), ("formulas", validate_formula)):
        cases = load_cases(root / "evals" / category)
        all_cases.extend(cases)
        if not cases:
            errors.append(f"{category}: at least one case is required")
        for case in cases:
            if isinstance(case, dict) and "_load_error" in case:
                errors.append(case["_load_error"])
            elif category == "claims":
                errors.extend(validator(case, sources, english_sources, provenance, seen))
            else:
                errors.extend(validator(case, sources, english_sources, seen))
    errors.extend(validate_source_locks(root, all_cases, sources, english_sources))
    return sorted(errors)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    errors = validate(args.root.resolve())
    if errors:
        print("Evaluation validation failed:", *[f"- {error}" for error in errors], sep="\n")
        return 1
    print("Evaluation validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
