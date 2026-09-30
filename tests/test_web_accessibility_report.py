from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/book-kit"))


class WebAccessibilityReportTests(unittest.TestCase):
    def test_axe_summary_preserves_violations_and_incomplete_checks_as_advisories(self):
        from audit_axe_accessibility import audit_routes, summarize_axe_result

        self.assertEqual(
            summarize_axe_result({"violations": [{"id": "color-contrast"}], "incomplete": [{"id": "aria"}], "passes": [{"id": "html-has-lang"}]}),
            {
                "violations": [{"id": "color-contrast"}],
                "incomplete": [{"id": "aria"}],
                "passes": 1,
                "findings": [
                    {"severity": "advisory", "code": "axe-violation", "message": "color-contrast"},
                    {"severity": "advisory", "code": "axe-incomplete", "message": "aria"},
                ],
            },
        )
        report = audit_routes(
            "http://127.0.0.1:4322/Understanding-LLMs",
            None,
            Path("/does-not-exist/axe.min.js"),
            timestamp="2026-09-30T00:00:00Z",
        )
        self.assertEqual(report["findings"][0]["code"], "axe-script-unavailable")

    def test_route_matrix_covers_required_routes_locales_and_viewports(self):
        from audit_web_accessibility import ROUTE_MATRIX, VIEWPORTS, route_matrix

        matrix = route_matrix()
        self.assertEqual({route["name"] for route in ROUTE_MATRIX}, {
            "home", "dense-math", "diagram-heavy", "downloads", "ai-learning",
        })
        self.assertEqual(set(VIEWPORTS), {"desktop", "mobile"})
        self.assertEqual(len(matrix), 20)
        self.assertEqual({item["locale"] for item in matrix}, {"zh-Hans", "en"})
        self.assertEqual({item["viewport"] for item in matrix}, {"desktop", "mobile"})
        self.assertTrue(all(item["route"].startswith(f"/{item['locale']}/") for item in matrix))

    def test_snapshot_analysis_reports_only_observable_advisories(self):
        from audit_web_accessibility import analyze_snapshot

        result = analyze_snapshot(
            {
                "document_lang": "",
                "headings": [1, 3, 2],
                "images": {"total": 3, "without_alt": ["/diagram.svg"]},
                "focus": {"count": 4, "active_tag": "A", "focus_visible": True, "indicator": True},
                "layout": {"scroll_width": 420, "viewport_width": 390},
            },
            expected_locale="en",
        )
        self.assertEqual(result["document_lang"], "")
        self.assertTrue(result["layout"]["horizontal_overflow"])
        codes = {finding["code"] for finding in result["findings"]}
        self.assertEqual(codes, {
            "document-language-mismatch",
            "heading-level-skip",
            "image-without-alt",
            "horizontal-overflow",
        })
        self.assertTrue(all(finding["severity"] == "advisory" for finding in result["findings"]))

    def test_ci_writes_and_preserves_nonblocking_route_matrix_report(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("audit_web_accessibility.py", workflow)
        self.assertIn("web-accessibility-route-report", workflow)
        self.assertIn("web-accessibility-routes.json", workflow)
        self.assertIn("if: always()", workflow)
        self.assertLess(workflow.index("npx astro preview"), workflow.index("audit_web_accessibility.py"))
        audit_step = workflow[workflow.index("- name: Run website accessibility route report"):workflow.index("- uses: actions/upload-artifact@v4", workflow.index("web-accessibility-route-report"))]
        self.assertIn("if: always()", audit_step)
        self.assertIn("continue-on-error: true", audit_step)
        smoke_step = workflow[workflow.index("- name: Run browser and accessibility smoke checks"):workflow.index("- name: Run website accessibility route report")]
        self.assertNotIn("audit_web_accessibility.py", smoke_step)

    def test_ci_preserves_nonblocking_axe_route_matrix_report(self):
        root = Path(__file__).resolve().parents[1]
        workflow = (root / ".github/workflows/ci.yml").read_text(encoding="utf-8")
        self.assertIn("audit_axe_accessibility.py", workflow)
        self.assertIn("axe-accessibility-route-report", workflow)
        self.assertIn("axe-accessibility-routes.json", workflow)
        axe_step = workflow[workflow.index("- name: Run axe accessibility route report"):workflow.index("- name: Capture advisory visual review matrix")]
        self.assertIn("if: always()", axe_step)
        self.assertIn("continue-on-error: true", axe_step)


if __name__ == "__main__":
    unittest.main()
