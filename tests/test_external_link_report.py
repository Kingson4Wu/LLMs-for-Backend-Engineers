from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools/book-kit"))


class ExternalLinkReportTests(unittest.TestCase):
    def test_inventory_deduplicates_urls_and_preserves_bilingual_locations(self):
        from audit_external_links import inventory_links

        root = Path(__file__).resolve().parents[1]
        inventory = inventory_links(root)

        self.assertGreater(len(inventory), 30)
        self.assertEqual(len(inventory), len({entry["url"] for entry in inventory}))
        self.assertTrue(all(entry["locations"] for entry in inventory))
        self.assertTrue(any({location["locale"] for location in entry["locations"]} == {"zh-Hans", "en"} for entry in inventory))

    def test_inventory_does_not_mislabel_translation_sources_as_chinese(self):
        from audit_external_links import inventory_links

        root = Path(__file__).resolve().parents[1]
        inventory = inventory_links(root)
        locations = [location for entry in inventory for location in entry["locations"]]

        self.assertTrue(
            all(
                (location["locale"] == "en")
                == location["path"].startswith("book/translations/en/")
                for location in locations
            )
        )

    def test_report_keeps_failed_fetch_as_an_advisory(self):
        from audit_external_links import audit_links

        report = audit_links(
            [{"url": "https://example.test/reference", "locations": [{"locale": "en", "path": "chapter.md", "line": 1}]}],
            fetch=lambda _url: (None, "fetch-failed", "connection reset"),
            timestamp="2026-09-30T00:00:00Z",
        )

        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["links"][0]["findings"], [{"severity": "advisory", "code": "fetch-failed", "message": "connection reset"}])

    def test_scheduled_workflow_preserves_external_link_report_without_gating(self):
        workflow = (Path(__file__).resolve().parents[1] / ".github/workflows/external-link-monitor.yml").read_text(encoding="utf-8")
        self.assertIn("audit_external_links.py", workflow)
        self.assertIn("external-link-report", workflow)
        self.assertIn("external-link-report.json", workflow)
        self.assertIn("schedule:", workflow)
        self.assertIn("continue-on-error: true", workflow)


if __name__ == "__main__":
    unittest.main()
