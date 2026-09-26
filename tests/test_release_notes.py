from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/book-kit'))


class ReleaseNotesTests(unittest.TestCase):
    def test_notes_include_version_changes_and_provenance(self):
        from release_notes import render_notes

        notes = render_notes(
            version='v1.2.0',
            source_commit='a1b2c3d4e5f6',
            commits=['fix: repair EPUB navigation', 'docs: clarify reading path'],
        )

        self.assertIn('# v1.2.0', notes)
        self.assertIn('- repair EPUB navigation', notes)
        self.assertIn('- clarify reading path', notes)
        self.assertIn('a1b2c3d4e5f6', notes)
        self.assertIn('manifest.json', notes)

    def test_notes_state_when_no_changes_are_available(self):
        from release_notes import render_notes

        notes = render_notes(version='v1.0.0', source_commit='abc', commits=[])

        self.assertIn('没有可列出的提交说明', notes)


if __name__ == '__main__':
    unittest.main()
