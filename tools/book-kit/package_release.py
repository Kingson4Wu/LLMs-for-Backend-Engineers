"""Assemble versioned artifacts only when every required format has matching provenance."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess

from book_meta import resolve_book_dir


RELEASE_PROVENANCE_FILE = "release-provenance.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_release_provenance(*, version: str, commit: str, artifacts: list[dict], workflow_context: dict[str, str]) -> dict:
    """Record reproducible origin/integrity facts; this is not a signature."""
    source_provenance = []
    for locale in sorted({artifact["locale"] for artifact in artifacts}):
        locale_artifacts = [artifact for artifact in artifacts if artifact["locale"] == locale]
        source_provenance.append({
            "locale": locale,
            "source_commit": locale_artifacts[0]["source_commit"],
            "source_digest": locale_artifacts[0]["source_digest"],
            "source_dirty": locale_artifacts[0]["source_dirty"],
        })
    return {
        "schema_version": 1,
        "kind": "release-origin-provenance",
        "release_tag": version,
        "git_commit": commit,
        "artifact_version": version,
        "workflow_context": workflow_context,
        "files": [
            {"file": artifact["file"], "sha256": artifact["sha256"], "bytes": artifact["bytes"]}
            for artifact in sorted(artifacts, key=lambda item: item["file"])
        ],
        "source_provenance": source_provenance,
        "limitations": (
            "This JSON records build provenance and SHA-256 integrity only. "
            "It is not a cryptographic signature, a GitHub artifact attestation, "
            "or evidence of content quality or security."
        ),
    }


def validate_release_provenance(destination: Path, *, expected_version: str | None = None, expected_commit: str | None = None) -> list[str]:
    """Verify the release-side provenance record against copied download files."""
    try:
        record = json.loads((destination / RELEASE_PROVENANCE_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"release provenance is unreadable: {exc}"]
    errors: list[str] = []
    if record.get("schema_version") != 1 or record.get("kind") != "release-origin-provenance":
        errors.append("release provenance has an unsupported schema")
    if expected_version is not None and record.get("release_tag") != expected_version:
        errors.append("release provenance tag mismatch")
    if expected_commit is not None and record.get("git_commit") != expected_commit:
        errors.append("release provenance commit mismatch")
    if record.get("artifact_version") != record.get("release_tag"):
        errors.append("release provenance artifact version mismatch")
    if not isinstance(record.get("workflow_context"), dict):
        errors.append("release provenance workflow context is invalid")
    files = record.get("files")
    if not isinstance(files, list) or not files:
        return errors + ["release provenance has no generated files"]
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict) or not isinstance(entry.get("file"), str):
            errors.append("release provenance has an invalid file entry")
            continue
        name = entry["file"]
        if name in seen:
            errors.append(f"release provenance duplicates {name}")
            continue
        seen.add(name)
        file_path = destination / name
        if not file_path.is_file():
            errors.append(f"release provenance file is missing: {name}")
        elif entry.get("sha256") != sha256(file_path):
            errors.append(f"release provenance checksum mismatch: {name}")
        elif entry.get("bytes") != file_path.stat().st_size:
            errors.append(f"release provenance byte count mismatch: {name}")
    try:
        manifest = json.loads((destination / "manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return errors + [f"release manifest is unreadable: {exc}"]
    manifest_files = {entry.get("file"): entry.get("sha256") for entry in manifest.get("artifacts", []) if isinstance(entry, dict)}
    provenance_files = {entry.get("file"): entry.get("sha256") for entry in files if isinstance(entry, dict)}
    if manifest.get("version") != record.get("release_tag") or manifest.get("source_commit") != record.get("git_commit"):
        errors.append("release provenance does not match manifest identity")
    if manifest_files != provenance_files:
        errors.append("release provenance does not match manifest file checksums")
    expected_sources: dict[str, dict] = {}
    for artifact in manifest.get("artifacts", []):
        if not isinstance(artifact, dict) or not isinstance(artifact.get("locale"), str):
            continue
        expected = {
            "locale": artifact["locale"],
            "source_commit": artifact.get("source_commit"),
            "source_digest": artifact.get("source_digest"),
            "source_dirty": artifact.get("source_dirty"),
        }
        if artifact["locale"] in expected_sources and expected_sources[artifact["locale"]] != expected:
            errors.append(f"release manifest has inconsistent source provenance: {artifact['locale']}")
        expected_sources[artifact["locale"]] = expected
    actual_sources = record.get("source_provenance")
    if not isinstance(actual_sources, list) or {entry.get("locale"): entry for entry in actual_sources if isinstance(entry, dict)} != expected_sources:
        errors.append("release provenance source provenance mismatch")
    return errors


def package(book: Path, destination: Path, version: str, expected_commit: str, workflow_context: dict[str, str] | None = None) -> dict:
    if not re.fullmatch(r"v[0-9][A-Za-z0-9._-]*", version):
        raise ValueError("Version must be a safe v-prefixed tag")
    editions = json.loads((book / "editions.json").read_text())["editions"]
    pending = []
    for locale, edition in editions.items():
        if edition["status"] != "published":
            continue
        output = book / "exported" / locale
        manifest = json.loads((output / "manifest.json").read_text())
        artifacts = {a["file"]: a for a in manifest["artifacts"]}
        required = {"Understanding-LLMs.pdf", "Understanding-LLMs.epub", "Understanding-LLMs.print.html", "Understanding-LLMs.md"}
        if set(artifacts) != required:
            raise ValueError(f"{locale}: incomplete required formats")
        if len({a.get("source_digest") for a in artifacts.values()}) != 1:
            raise ValueError(f"{locale}: formats come from different source bytes")
        for name, artifact in artifacts.items():
            if artifact.get("source_commit") != expected_commit or artifact.get("source_dirty") is not False:
                raise ValueError(f"{locale}: release requires clean tagged source")
            source = output / name
            if sha256(source) != artifact["sha256"]:
                raise ValueError(f"{locale}: artifact checksum mismatch")
            suffix = "print.html" if name.endswith("html") else name.split(".")[-1]
            target = f"Understanding-LLMs-{locale}-{version}.{suffix}"
            pending.append((source, {**artifact, "file": target, "locale": locale, "bytes": source.stat().st_size}))
    if not pending:
        raise ValueError("No published editions")
    destination.mkdir(parents=True, exist_ok=True)
    if any(destination.iterdir()):
        raise ValueError("Release destination must be empty")
    for source, artifact in pending:
        shutil.copyfile(source, destination / artifact["file"])
    manifest = {"version": version, "source_commit": expected_commit, "artifacts": [a for _, a in pending]}
    (destination / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    provenance = build_release_provenance(
        version=version, commit=expected_commit, artifacts=manifest["artifacts"], workflow_context=workflow_context or {}
    )
    (destination / RELEASE_PROVENANCE_FILE).write_text(json.dumps(provenance, indent=2) + "\n")
    if errors := validate_release_provenance(destination, expected_version=version, expected_commit=expected_commit):
        raise ValueError("; ".join(errors))
    checksums = [f"{sha256(path)}  {path.name}" for path in sorted(destination.iterdir())]
    (destination / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True)
    parser.add_argument("--output", default="release")
    args = parser.parse_args()
    book = resolve_book_dir(None)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=book, text=True).strip()
    workflow_context = {
        key: value for key, value in {
            "provider": "github-actions" if os.environ.get("GITHUB_ACTIONS") == "true" else "local",
            "repository": os.environ.get("GITHUB_REPOSITORY"),
            "workflow": os.environ.get("GITHUB_WORKFLOW"),
            "run_id": os.environ.get("GITHUB_RUN_ID"),
            "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
            "ref": os.environ.get("GITHUB_REF"),
        }.items() if value
    }
    result = package(book, Path(args.output), args.version, commit, workflow_context=workflow_context)
    print(f"Packaged {len(result['artifacts'])} artifacts into {args.output}")


if __name__ == "__main__":
    main()
