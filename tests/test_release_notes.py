from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools/book-kit'))


class ReleaseNotesTests(unittest.TestCase):
    def test_release_workflow_updates_an_existing_tag_in_place(self):
        workflow = (Path(__file__).resolve().parents[1] / '.github/workflows/release-books.yml').read_text()

        self.assertIn('if gh release view "$RELEASE_TAG"', workflow)
        self.assertIn('gh release upload "$RELEASE_TAG" release/* --clobber', workflow)
        self.assertIn('gh release edit "$RELEASE_TAG"', workflow)
        self.assertIn('--title "$RELEASE_TAG"', workflow)

    def test_notes_use_the_standard_english_release_template(self):
        from release_notes import render_notes

        notes = render_notes(
            version='v1.2.0',
            source_commit='a1b2c3d4e5f6',
            commits=['fix: repair EPUB navigation', 'docs: clarify reading path'],
        )

        self.assertIn('# v1.2.0', notes)
        self.assertIn('## Downloads', notes)
        self.assertIn('English edition', notes)
        self.assertIn('Simplified Chinese edition', notes)
        self.assertIn('Markdown, PDF, EPUB, and print HTML', notes)
        self.assertIn('## Integrity', notes)
        self.assertIn('- repair EPUB navigation', notes)
        self.assertIn('- clarify reading path', notes)
        self.assertIn('a1b2c3d4e5f6', notes)
        self.assertIn('manifest.json', notes)
        self.assertNotRegex(notes, r'[\u4e00-\u9fff]')

    def test_notes_explain_when_no_changes_are_available_in_english(self):
        from release_notes import render_notes

        notes = render_notes(version='v1.0.0', source_commit='abc', commits=[])

        self.assertIn('No commit summaries are available for this tag.', notes)
        self.assertNotRegex(notes, r'[\u4e00-\u9fff]')


if __name__ == '__main__':
    unittest.main()
