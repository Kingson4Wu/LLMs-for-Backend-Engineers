import json
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "book-kit"))


def valid_review() -> dict:
    return {
        "reviewed_at": "2026-09-29",
        "reviewer": "Kingson Wu",
        "proposition": True,
        "conditions_and_quantifiers": True,
        "formula_symbols_and_units": True,
        "figure_meaning": True,
        "link_target": True,
        "english_heading": "Evidence boundary",
        "english_anchor_text": "RAG changes visible evidence.",
    }


def valid_claim(**overrides: object) -> dict:
    case = {
        "id": "rag-evidence-boundary",
        "chapter": "rag-context-evidence",
        "heading": "证据边界",
        "anchor_text": "RAG 改变当前可见证据",
        "kind": "boundary",
        "sources": ["https://example.com/rag"],
        "expectation": "RAG changes current evidence rather than model weights.",
        "must_not_imply": ["RAG guarantees truth."],
        "review": valid_review(),
    }
    case.update(overrides)
    return case


def valid_formula(**overrides: object) -> dict:
    case = {
        "id": "softmax-normalizes",
        "chapter": "rag-context-evidence",
        "heading": "证据边界",
        "anchor_text": "RAG 改变当前可见证据",
        "evaluator": "softmax",
        "inputs": {"logits": [0, 0]},
        "expected": [0.5, 0.5],
        "tolerance": 1e-12,
        "domain": "finite logits",
        "review": valid_review(),
    }
    case.update(overrides)
    return case


class EvaluationFixture:
    def __init__(self, *, claims: list[dict] | None = None, formulas: list[dict] | None = None):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        source = self.root / "book" / "chapters"
        source.mkdir(parents=True)
        (source / "rag.md").write_text(
            "# RAG\n\n## 证据边界\n\nRAG 改变当前可见证据。\n\n$$x=1$$\n", encoding="utf-8"
        )
        (self.root / "book" / "catalog.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "frontmatter": [],
                    "parts": [
                        {
                            "id": "external",
                            "path": "parts/external.md",
                            "title": "External",
                            "chapters": [
                                {
                                    "id": "rag-context-evidence",
                                    "path": "chapters/rag.md",
                                    "title": "RAG",
                                }
                            ],
                        }
                    ],
                },
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        english_source = self.root / "book" / "translations" / "en" / "chapters"
        english_source.mkdir(parents=True)
        (english_source / "rag.md").write_text(
            "# RAG\n\n## Evidence boundary\n\nRAG changes visible evidence.\n", encoding="utf-8"
        )
        (self.root / "book" / "translations" / "en" / "catalog.json").write_text(
            json.dumps(
                {"version": 1, "frontmatter": [], "parts": [{"id": "external", "path": "parts/external.md", "title": "External", "chapters": [{"id": "rag-context-evidence", "path": "chapters/rag.md", "title": "RAG"}]}]},
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        eval_root = self.root / "evals"
        (eval_root / "claims").mkdir(parents=True)
        (eval_root / "formulas").mkdir(parents=True)
        (eval_root / "claims" / "cases.json").write_text(
            json.dumps({"cases": claims if claims is not None else [valid_claim()]}, ensure_ascii=False),
            encoding="utf-8",
        )
        (eval_root / "formulas" / "cases.json").write_text(
            json.dumps({"cases": formulas if formulas is not None else [valid_formula()]}, ensure_ascii=False),
            encoding="utf-8",
        )
        (eval_root / "provenance.json").write_text(
            json.dumps(
                {
                    "sources": [
                        {
                            "type": "paper",
                            "url": "https://example.com/rag",
                            "locator": "Fixture evidence",
                            "published_or_versioned_at": "2026-09-29",
                            "retrieved_at": "2026-09-29",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        review_root = eval_root / "reviews"
        review_root.mkdir()
        (review_root / "source-locks.json").write_text(
            json.dumps(
                {
                    "locks": [
                        {
                            "chapter": "rag-context-evidence",
                            "zh_digest": hashlib.sha256((source / "rag.md").read_bytes()).hexdigest(),
                            "en_digest": hashlib.sha256((english_source / "rag.md").read_bytes()).hexdigest(),
                            "english_heading": "Evidence boundary",
                            "english_anchor_text": "RAG changes visible evidence.",
                            "reviewed_at": "2026-09-29",
                            "reviewer": "Kingson Wu",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )

    def close(self) -> None:
        self.directory.cleanup()


class EvaluationSuiteTests(unittest.TestCase):
    def test_committed_evaluation_suite_is_valid(self):
        from validate_evals import validate

        self.assertEqual(validate(ROOT), [])

    def test_committed_cases_have_explicit_english_review_anchors(self):
        for path in sorted((ROOT / "evals").glob("claims/*.json")) + sorted((ROOT / "evals").glob("formulas/*.json")):
            for case in json.loads(path.read_text(encoding="utf-8"))["cases"]:
                review = case["review"]
                self.assertIsInstance(review.get("english_heading"), str, case["id"])
                self.assertTrue(review.get("english_heading", "").strip(), case["id"])
                self.assertIsInstance(review.get("english_anchor_text"), str, case["id"])
                self.assertTrue(review.get("english_anchor_text", "").strip(), case["id"])

    def test_case_without_english_review_anchor_is_rejected(self):
        from validate_evals import validate

        review = valid_review()
        review.pop("english_anchor_text")
        fixture = EvaluationFixture(claims=[valid_claim(review=review)])
        self.addCleanup(fixture.close)
        self.assertIn(
            "claim:rag-evidence-boundary: review.english_anchor_text must be a non-empty string",
            validate(fixture.root),
        )

    def test_claim_case_reports_a_stale_anchor(self):
        from validate_evals import validate

        fixture = EvaluationFixture(claims=[valid_claim(anchor_text="missing sentence")])
        self.addCleanup(fixture.close)
        self.assertEqual(
            validate(fixture.root),
            ["claim:rag-evidence-boundary: anchor text is absent from source"],
        )

    def test_formula_case_reports_a_wrong_expected_value(self):
        from validate_evals import validate

        fixture = EvaluationFixture(formulas=[valid_formula(expected=[0.2, 0.8])])
        self.addCleanup(fixture.close)
        self.assertEqual(
            validate(fixture.root),
            ["formula:softmax-normalizes: expected value differs from evaluator output"],
        )

    def test_formula_case_rejects_a_stale_fingerprint(self):
        from validate_evals import validate

        fixture = EvaluationFixture(
            formulas=[valid_formula(formula_anchor="x=1", formula_fingerprint="0" * 64)]
        )
        self.addCleanup(fixture.close)
        self.assertIn(
            "formula:softmax-normalizes: formula_fingerprint differs from formula_anchor",
            validate(fixture.root),
        )

    def test_claim_rejects_duplicate_id_and_incomplete_review(self):
        from validate_evals import validate

        incomplete_review = valid_review()
        incomplete_review["conditions_and_quantifiers"] = False
        fixture = EvaluationFixture(
            claims=[valid_claim(), valid_claim(review=incomplete_review)]
        )
        self.addCleanup(fixture.close)
        errors = validate(fixture.root)
        self.assertIn("claim:rag-evidence-boundary: duplicate id", errors)
        self.assertIn(
            "claim:rag-evidence-boundary: review.conditions_and_quantifiers must be true",
            errors,
        )

    def test_claim_rejects_missing_heading_and_noncanonical_source(self):
        from validate_evals import validate

        fixture = EvaluationFixture(
            claims=[valid_claim(heading="Missing", sources=["notes.txt"])]
        )
        self.addCleanup(fixture.close)
        errors = validate(fixture.root)
        self.assertIn("claim:rag-evidence-boundary: heading is absent from source", errors)
        self.assertIn(
            "claim:rag-evidence-boundary: source URL must be absolute HTTP(S)", errors
        )

    def test_claim_rejects_an_unregistered_provenance_url(self):
        from validate_evals import validate

        fixture = EvaluationFixture(claims=[valid_claim(sources=["https://unknown.example/evidence"])])
        self.addCleanup(fixture.close)
        self.assertIn(
            "claim:rag-evidence-boundary: every source URL must be registered in provenance.json",
            validate(fixture.root),
        )

    def test_time_sensitive_claim_requires_a_current_review_interval(self):
        from validate_evals import validate

        review = valid_review()
        review["reviewed_at"] = "2000-01-01"
        fixture = EvaluationFixture(
            claims=[valid_claim(kind="time-sensitive", review=review, review_interval_days=1)]
        )
        self.addCleanup(fixture.close)
        self.assertIn(
            "claim:rag-evidence-boundary: time-sensitive review interval has elapsed",
            validate(fixture.root),
        )

    def test_softmax_evaluator_is_shift_invariant(self):
        from validate_evals import evaluate_formula

        self.assertEqual(evaluate_formula("softmax", {"logits": [0, 0]}), [0.5, 0.5])
        self.assertEqual(evaluate_formula("softmax", {"logits": [7, 7]}), [0.5, 0.5])

    def test_cross_entropy_requires_a_probability_distribution(self):
        from validate_evals import evaluate_formula

        with self.assertRaisesRegex(ValueError, "probabilities must sum to 1"):
            evaluate_formula(
                "cross_entropy_one_hot", {"probabilities": [0.7, 0.7], "target": 0}
            )

    def test_masked_attention_excludes_disallowed_keys(self):
        from validate_evals import evaluate_formula

        self.assertEqual(
            evaluate_formula(
                "masked_attention",
                {
                    "scores": [[0, 100]],
                    "mask": [[True, False]],
                    "values": [[2], [999]],
                },
            ),
            [[2.0]],
        )

    def test_temperature_and_kv_cache_domains_are_checked(self):
        from validate_evals import evaluate_formula

        with self.assertRaisesRegex(ValueError, "temperature must be a positive finite number"):
            evaluate_formula("temperature_softmax", {"logits": [0, 1], "temperature": 0})
        self.assertEqual(
            evaluate_formula(
                "kv_cache_bytes",
                {"layers": 2, "tokens": 3, "kv_heads": 4, "head_dim": 5, "bytes_per_element": 2},
            ),
            480,
        )

    def test_unknown_formula_evaluator_is_rejected(self):
        from validate_evals import validate_formula

        self.assertEqual(
            validate_formula(valid_formula(id="x", evaluator="python")),
            ["formula:x: evaluator is unsupported"],
        )

    def test_committed_suite_requires_claim_and_formula_cases(self):
        from validate_evals import validate

        fixture = EvaluationFixture(claims=[], formulas=[])
        self.addCleanup(fixture.close)
        self.assertEqual(
            validate(fixture.root),
            [
                "claims: at least one case is required",
                "formulas: at least one case is required",
            ],
        )

    def test_every_publication_workflow_runs_the_eval_validator(self):
        for workflow in ("ci.yml", "deploy-docs.yml", "release-books.yml"):
            content = (ROOT / ".github/workflows" / workflow).read_text(encoding="utf-8")
            self.assertIn("python3 tools/book-kit/validate_evals.py", content, workflow)

    def test_review_rejects_an_absent_english_anchor(self):
        from validate_evals import validate

        review = valid_review()
        review["english_anchor_text"] = "missing English sentence"
        fixture = EvaluationFixture(claims=[valid_claim(review=review)])
        self.addCleanup(fixture.close)
        self.assertIn(
            "claim:rag-evidence-boundary: review.english_anchor_text is absent from English source",
            validate(fixture.root),
        )

    def test_source_lock_rejects_changed_english_mirror(self):
        from validate_evals import validate

        fixture = EvaluationFixture()
        self.addCleanup(fixture.close)
        lock_dir = fixture.root / "evals" / "reviews"
        (lock_dir / "source-locks.json").write_text(
            json.dumps(
                {
                    "locks": [
                        {
                            "chapter": "rag-context-evidence",
                            "zh_digest": hashlib.sha256(
                                (fixture.root / "book" / "chapters" / "rag.md").read_bytes()
                            ).hexdigest(),
                            "en_digest": "0" * 64,
                            "english_heading": "Evidence boundary",
                            "english_anchor_text": "RAG changes visible evidence.",
                            "reviewed_at": "2026-09-29",
                            "reviewer": "Kingson Wu",
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        self.assertIn(
            "review:rag-context-evidence: English source digest differs from lock",
            validate(fixture.root),
        )


if __name__ == "__main__":
    unittest.main()
