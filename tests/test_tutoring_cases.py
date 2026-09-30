import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/book-kit"))


def write_book(root: Path) -> None:
    (root / "book" / "chapters").mkdir(parents=True)
    (root / "book" / "catalog.json").write_text(
        json.dumps(
            {
                "frontmatter": [],
                "parts": [
                    {
                        "id": "foundations",
                        "chapters": [
                            {"id": "softmax", "title": "Softmax", "path": "chapters/softmax.md"}
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (root / "book" / "chapters" / "softmax.md").write_text(
        "# Softmax\n\n## Probability distribution\n\nText.\n", encoding="utf-8"
    )
    english = root / "book" / "translations" / "en"
    (english / "chapters").mkdir(parents=True)
    (english / "catalog.json").write_text(
        json.dumps(
            {
                "frontmatter": [],
                "parts": [
                    {
                        "id": "foundations",
                        "chapters": [
                            {"id": "softmax", "title": "Softmax in English", "path": "chapters/softmax.md"}
                        ],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (english / "chapters" / "softmax.md").write_text(
        "# Softmax in English\n\n## Distribution in English\n\nText.\n", encoding="utf-8"
    )


def valid_case() -> dict:
    return {
        "schema_version": 1,
        "id": "softmax-evidence-boundary",
        "artifact_requirements": {
            "locale": "zh-Hans",
            "complete_format": "markdown",
            "file": "Understanding-LLMs.md",
        },
        "learner_task": "Explain why softmax produces a distribution.",
        "source_locations": [
            {
                "chapter_id": "softmax",
                "title": "Softmax",
                "path": "chapters/softmax.md",
                "heading": "Probability distribution",
            }
        ],
        "required_labels": ["book_evidence", "inference", "external_verification"],
        "formula_constraint": {
            "location": {"chapter_id": "softmax", "heading": "Probability distribution"},
            "domain": "finite logits",
            "numeric_golden": {"inputs": {"logits": [0, 0]}, "expected": [0.5, 0.5], "tolerance": 1e-12},
        },
        "comprehension_question": "What changes if one logit is much larger?",
        "prohibited_claims": ["Softmax makes an answer true."],
        "figure_format_limitations": "A Markdown or PDF extraction can omit or flatten figure details; do not invent arrows or spatial relationships.",
    }


class TutoringCaseTests(unittest.TestCase):
    def test_reusable_human_review_packets_define_scope_without_claiming_a_result(self):
        accessibility = (ROOT / "evals/reviews/accessibility-release-checklist.md").read_text(encoding="utf-8")
        self.assertIn("Keyboard", accessibility)
        self.assertIn("200%", accessibility)
        self.assertIn("screen reader", accessibility.lower())
        self.assertIn("not a conformance claim", accessibility.lower())

        template = json.loads((ROOT / "evals/tutoring/human-review-template.json").read_text(encoding="utf-8"))
        self.assertEqual(template["schema_version"], 1)
        self.assertEqual(template["judgement"], "unreviewed")
        self.assertEqual(set(template["learning_paths"]), {"ai-downloads-artifact", "user-supplies-artifact"})
        self.assertIn("does_not_use_model_as_judge", template["limitations"])

    def test_versioned_case_schema_documents_public_contract(self):
        schema = json.loads((ROOT / "evals/tutoring/schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["$id"], "https://understanding-llms.dev/evals/tutoring/schema-1.json")
        self.assertIn("source_locations", schema["required"])
        self.assertIn("figure_format_limitations", schema["required"])

    def test_development_case_requires_traceable_contract_fields(self):
        from validate_tutoring_cases import validate_case

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_book(root)
            self.assertEqual(validate_case(root, valid_case()), [])

            missing = valid_case()
            del missing["figure_format_limitations"]
            errors = validate_case(root, missing)
            self.assertTrue(any("figure_format_limitations" in error for error in errors), errors)

            untraceable_formula = valid_case()
            untraceable_formula["formula_constraint"]["location"]["heading"] = "Invented heading"
            errors = validate_case(root, untraceable_formula)
            self.assertTrue(any("formula_constraint.location" in error for error in errors), errors)

    def test_case_uses_the_locale_matched_source_catalogue(self):
        from validate_tutoring_cases import validate_case

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_book(root)
            case = valid_case()
            case["artifact_requirements"]["locale"] = "en"
            case["source_locations"][0].update(
                {"title": "Softmax in English", "heading": "Distribution in English"}
            )
            case["formula_constraint"]["location"]["heading"] = "Distribution in English"
            self.assertEqual(validate_case(root, case), [])

    def test_execution_report_binds_the_transcript_to_a_complete_artifact(self):
        from validate_tutoring_cases import evaluate_execution

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_book(root)
            artifact = root / "Understanding-LLMs.md"
            artifact.write_text("complete exported book", encoding="utf-8")
            digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
            execution = {
                "schema_version": 1,
                "case_id": "softmax-evidence-boundary",
                "artifact": {
                    "locale": "zh-Hans",
                    "format": "markdown",
                    "file": "Understanding-LLMs.md",
                    "sha256": digest,
                },
                "transcript": "book_evidence\ninference\nexternal_verification\nWhat changes if one logit is much larger?",
                "observed": {
                    "source_locations": valid_case()["source_locations"],
                    "formula_numeric_answers": [[0.5, 0.5]],
                    "comprehension_question": "What changes if one logit is much larger?",
                    "figure_format_limitations_acknowledged": True,
                },
            }
            report = evaluate_execution(root, valid_case(), execution, artifact)
            self.assertEqual(report["findings"], [])
            self.assertEqual(report["artifact"]["sha256"], digest)
            self.assertIn("human adjudication", report["limitations"])

    def test_bad_artifact_hash_is_an_advisory_finding_not_a_model_score(self):
        from validate_tutoring_cases import evaluate_execution

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_book(root)
            artifact = root / "Understanding-LLMs.md"
            artifact.write_text("complete exported book", encoding="utf-8")
            report = evaluate_execution(
                root,
                valid_case(),
                {
                    "schema_version": 1,
                    "case_id": "softmax-evidence-boundary",
                    "artifact": {
                        "locale": "zh-Hans",
                        "format": "markdown",
                        "file": "Understanding-LLMs.md",
                        "sha256": "0" * 64,
                    },
                    "transcript": "",
                    "observed": {},
                },
                artifact,
            )
            self.assertTrue(any(item["code"] == "artifact-sha256-mismatch" for item in report["findings"]))
            self.assertNotIn("score", report)

    def test_only_public_development_cases_are_a_ci_contract(self):
        workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        release = (ROOT / ".github/workflows/release-books.yml").read_text(encoding="utf-8")
        self.assertIn("validate_tutoring_cases.py --development", workflow)
        self.assertNotIn("validate_tutoring_cases.py", release)
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("evals/tutoring/holdout/*.json", ignored)

    def test_public_development_suite_covers_multiple_learning_boundaries(self):
        from validate_tutoring_cases import load_development_cases

        cases, errors = load_development_cases(ROOT / "evals/tutoring/development")
        chapters = {
            location["chapter_id"]
            for case in cases
            for location in case.get("source_locations", [])
            if isinstance(location, dict) and isinstance(location.get("chapter_id"), str)
        }
        self.assertEqual(errors, [])
        self.assertGreaterEqual(len(cases), 8)
        self.assertGreaterEqual(len(chapters), 8)


if __name__ == "__main__":
    unittest.main()
