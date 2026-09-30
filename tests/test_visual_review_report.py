from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/book-kit"))


class VisualReviewReportTests(unittest.TestCase):
    def test_fixed_matrix_covers_representative_routes_locales_themes_and_viewports(self):
        from capture_visual_review import ROUTES, THEMES, VIEWPORTS, visual_matrix

        matrix = visual_matrix()
        self.assertEqual(
            {route["name"] for route in ROUTES},
            {"home", "dense-math", "dense-table-code", "diagram-heavy", "downloads", "ai-learning"},
        )
        self.assertEqual(set(THEMES), {"light", "dark"})
        self.assertEqual(set(VIEWPORTS), {"desktop", "mobile"})
        self.assertEqual(len(matrix), 48)
        self.assertTrue(all(item["screenshot"].endswith(".png") for item in matrix))
        self.assertTrue(all(item["route"].startswith(f"/{item['locale']}/") for item in matrix))

    def test_report_entry_preserves_render_failure_as_advisory(self):
        from capture_visual_review import advisory_entry

        entry = advisory_entry({"name": "home", "locale": "en", "route": "/en/"}, "render-failed", "timeout")
        self.assertEqual(entry["findings"], [{"severity": "advisory", "code": "render-failed", "message": "timeout"}])
        self.assertIsNone(entry["screenshot"])

    def test_ci_runs_visual_review_independently_and_uploads_artifact(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("capture_visual_review.py", workflow)
        self.assertIn("visual-review-report", workflow)
        self.assertIn("visual-review-screenshots", workflow)
        start = workflow.index("- name: Capture advisory visual review matrix")
        end = workflow.index("- uses: actions/upload-artifact@v4", start)
        step = workflow[start:end]
        self.assertIn("if: always()", step)
        self.assertIn("continue-on-error: true", step)
        smoke = workflow[workflow.index("- name: Run browser and accessibility smoke checks"):start]
        self.assertNotIn("capture_visual_review.py", smoke)


if __name__ == "__main__":
    unittest.main()
