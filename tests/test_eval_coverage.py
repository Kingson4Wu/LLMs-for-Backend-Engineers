import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/book-kit"))


class EvalCoverageTests(unittest.TestCase):
    def test_priority_mechanisms_have_evidence_cases(self):
        from validate_eval_coverage import covered_chapters

        root = Path(__file__).resolve().parents[1]
        self.assertTrue(
            {
                "vanishing-exploding-gradients",
                "residual-connections",
                "layer-norm",
                "softmax-gradient-scaling",
                "fine-tuning-and-distillation",
                "rnn-to-transformer",
                "inference-performance-capacity",
                "optimizer-selection",
                "llm-inference-nondeterminism",
                "serving-control-plane",
                "agent-eval-business-quality-system",
            }.issubset(covered_chapters(root))
        )

    def test_every_policy_covered_core_chapter_has_evidence_or_exception(self):
        from validate_eval_coverage import validate_changed_chapters

        root = Path(__file__).resolve().parents[1]
        catalog = json.loads((root / "book/catalog.json").read_text(encoding="utf-8"))
        missing = []
        for part in catalog["parts"][:4]:
            for chapter in part["chapters"]:
                errors = validate_changed_chapters(root, {f"book/{chapter['path']}"})
                if errors:
                    missing.extend(errors)
        self.assertEqual(missing, [])

    def write_fixture(self, root, *, cases=(), locks=(), exceptions=()):
        (root / "evals/claims").mkdir(parents=True)
        (root / "evals/formulas").mkdir(parents=True)
        (root / "evals/reviews").mkdir(parents=True)
        (root / "evals/claims/cases.json").write_text(
            json.dumps({"cases": list(cases)}), encoding="utf-8"
        )
        (root / "evals/formulas/cases.json").write_text(
            json.dumps({"cases": []}), encoding="utf-8"
        )
        (root / "evals/reviews/locks.json").write_text(
            json.dumps({"locks": list(locks)}), encoding="utf-8"
        )
        (root / "evals/coverage-policy.json").write_text(
            json.dumps(
                {
                    "version": 1,
                    "rules": [
                        {
                            "family": "model-mechanisms",
                            "path_prefix": "book/chapters/part2/",
                        }
                    ],
                    "exceptions": list(exceptions),
                }
            ),
            encoding="utf-8",
        )

    def test_uncovered_high_risk_change_fails(self):
        from validate_eval_coverage import validate_changed_chapters

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(root)
            errors = validate_changed_chapters(
                root, {"book/chapters/part2/new-mechanism.md"}
            )
        self.assertIn(
            "high-risk changed chapter lacks evaluation coverage: new-mechanism (model-mechanisms)",
            errors,
        )

    def test_ordinary_change_needs_no_evaluation_case(self):
        from validate_eval_coverage import validate_changed_chapters

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(root)
            errors = validate_changed_chapters(root, {"README.md"})
        self.assertEqual(errors, [])

    def test_claim_or_formula_case_covers_high_risk_change(self):
        from validate_eval_coverage import validate_changed_chapters

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(root, cases=({"id": "case", "chapter": "covered"},))
            errors = validate_changed_chapters(root, {"book/chapters/part2/covered.md"})
        self.assertEqual(errors, [])

    def test_formula_case_is_coverage_evidence(self):
        from validate_eval_coverage import validate_changed_chapters

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(root)
            formula_path = root / "evals/formulas/cases.json"
            formula_path.write_text(
                json.dumps({"cases": [{"id": "formula", "chapter": "formula-covered"}]}),
                encoding="utf-8",
            )
            self.assertEqual(
                validate_changed_chapters(root, {"book/chapters/part2/formula-covered.md"}),
                [],
            )

    def test_orphan_or_incomplete_review_lock_cannot_cover_a_high_risk_change(self):
        from validate_eval_coverage import validate_changed_chapters

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(root, locks=({"chapter": "orphan"},))
            errors = validate_changed_chapters(root, {"book/chapters/part2/orphan.md"})
            self.assertIn(
                "high-risk changed chapter lacks evaluation coverage: orphan (model-mechanisms)",
                errors,
            )

    def test_no_changed_files_is_valid(self):
        from validate_eval_coverage import validate_changed_chapters

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(root)
            self.assertEqual(validate_changed_chapters(root, set()), [])

    def test_cli_accepts_repeated_changed_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(root, cases=({"id": "case", "chapter": "covered"},))
            command = [
                sys.executable,
                str(Path(__file__).resolve().parents[1] / "tools/book-kit/validate_eval_coverage.py"),
                "--root",
                str(root),
                "--changed-file",
                "README.md",
                "--changed-file",
                "book/chapters/part2/covered.md",
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_reviewed_exception_covers_high_risk_change(self):
        from validate_eval_coverage import validate_changed_chapters

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(
                root,
                exceptions=(
                    {
                        "chapter": "reviewed",
                        "family": "model-mechanisms",
                        "reviewer": "Editorial reviewer",
                        "reviewed_at": "2026-09-29",
                        "reason": "Typographic correction only; no mechanism changed.",
                    },
                ),
            )
            errors = validate_changed_chapters(root, {"book/chapters/part2/reviewed.md"})
        self.assertEqual(errors, [])

    def test_malformed_exception_is_rejected(self):
        from validate_eval_coverage import validate_changed_chapters

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.write_fixture(
                root,
                exceptions=(
                    {
                        "chapter": "reviewed",
                        "family": "model-mechanisms",
                        "reviewed_at": "not-a-date",
                        "reason": "Missing reviewer and invalid date.",
                    },
                ),
            )
            errors = validate_changed_chapters(root, {"book/chapters/part2/reviewed.md"})
        self.assertIn("exception:reviewed: reviewer must be a non-empty string", errors)
        self.assertIn("exception:reviewed: reviewed_at must be an ISO date", errors)

    def test_workflows_pass_reproducible_changed_paths_to_coverage_gate(self):
        root = Path(__file__).resolve().parents[1]
        workflows = root / ".github/workflows"
        for name in ("ci.yml", "deploy-docs.yml"):
            workflow = (workflows / name).read_text(encoding="utf-8")
            self.assertIn("fetch-depth: 0", workflow, name)
            self.assertIn("git merge-base", workflow, name)
            self.assertIn("git rev-parse \"$HEAD_SHA^\"", workflow, name)
            self.assertIn("validate_eval_coverage.py", workflow, name)
            self.assertIn('--changed-file "$file"', workflow, name)
        release = (workflows / "release-books.yml").read_text(encoding="utf-8")
        self.assertIn("validate_eval_coverage.py", release)
        self.assertIn("git describe --tags --abbrev=0", release)
        self.assertIn("git merge-base", release)
        self.assertIn("git rev-parse \"$HEAD_SHA^\"", release)
        self.assertIn("git hash-object -t tree /dev/null", release)
        self.assertIn('--changed-file "$file"', release)


if __name__ == "__main__":
    unittest.main()
