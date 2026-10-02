import json
from pathlib import Path
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools/book-kit"))


def catalogue_ids(book: Path) -> list[str]:
    catalogue = json.loads((book / "catalog.json").read_text(encoding="utf-8"))
    return [entry["id"] for part in catalogue["parts"] for entry in part["chapters"]]


class LearningIndexTests(unittest.TestCase):
    def test_learning_index_covers_every_bilingual_chapter(self):
        from generate_learning_index import build_index

        index = build_index(ROOT / "book")
        self.assertEqual([chapter["id"] for chapter in index["chapters"]], catalogue_ids(ROOT / "book"))
        for chapter in index["chapters"]:
            self.assertTrue(chapter["source"]["zh-Hans"]["path"])
            self.assertTrue(chapter["source"]["en"]["path"])
            self.assertTrue(chapter["source"]["zh-Hans"]["headings"])
            self.assertTrue(chapter["source"]["en"]["headings"])

    def test_committed_learning_index_matches_source_and_lists_real_figures(self):
        from generate_learning_index import render_index

        rendered = render_index(ROOT / "book")
        committed = (ROOT / "learning" / "index.json").read_text(encoding="utf-8")
        self.assertEqual(committed, rendered)
        index = json.loads(committed)
        self.assertEqual(index["chapters"][-1]["id"], "ai-learning-guide")
        for chapter in index["chapters"]:
            for locale in ("zh-Hans", "en"):
                for figure in chapter["source"][locale]["figures"]:
                    self.assertTrue(
                        (ROOT / "book" / figure).is_file(),
                        f"missing indexed figure: {figure}",
                    )
                metadata = chapter["source"][locale]
                self.assertTrue(
                    set(metadata["formula_sections"]).issubset(
                        {heading["anchor"] for heading in metadata["headings"]}
                    )
                )
                if metadata["formula_count"]:
                    self.assertTrue(metadata["formula_sections"])

    def test_reasoning_models_follows_generation_in_part_two(self):
        catalogue = json.loads((ROOT / "book" / "catalog.json").read_text(encoding="utf-8"))
        part_two = next(part for part in catalogue["parts"] if part["id"] == "llm-internal")
        ids = [chapter["id"] for chapter in part_two["chapters"]]
        self.assertEqual(ids[ids.index("llm-generation") + 1], "reasoning-models")

    def test_learning_contracts_require_traceable_read_only_tutoring(self):
        for name in ("LEARNING_CONTRACT.zh-Hans.md", "LEARNING_CONTRACT.en.md"):
            text = (ROOT / "learning" / name).read_text(encoding="utf-8").lower()
            self.assertIn("chapter id", text)
            self.assertIn("inference", text)
            self.assertIn("do not modify", text)

    def test_workspace_is_private_but_its_template_is_available(self):
        ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("learning/workspace/", ignored)
        self.assertTrue((ROOT / "learning/WORKSPACE_TEMPLATE/study-log.md").is_file())

    def test_readmes_lead_with_both_ai_learning_paths(self):
        for name in ("README.zh-CN.md", "README.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("Codex", text)
            self.assertIn("ChatGPT", text)
            self.assertIn("learning/index.json", text)
        for name in ("learning/README.md", "learning/README.en.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("Codex", text)
            self.assertIn("ChatGPT", text)
            self.assertIn("index.json", text)

    def test_public_descriptions_name_the_actual_reader_scope(self):
        chinese = [
            ROOT / "README.zh-CN.md",
            ROOT / "book/preface.md",
            ROOT / "book/book.json",
        ]
        english = [
            ROOT / "README.md",
            ROOT / "book/translations/en/preface.md",
            ROOT / "book/translations/en/book.json",
        ]
        for path in chinese:
            self.assertIn("AI 应用", path.read_text(encoding="utf-8"), path)
            self.assertIn("平台", path.read_text(encoding="utf-8"), path)
        for path in english:
            self.assertIn("AI application", path.read_text(encoding="utf-8"), path)
            self.assertIn("platform", path.read_text(encoding="utf-8"), path)

    def test_reader_descriptions_prioritize_understanding_over_application_instruction(self):
        chinese = (ROOT / "README.zh-CN.md").read_text(encoding="utf-8")
        english = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("而不是指导开发应用", chinese)
        self.assertIn("rather than instruct application development", english)

    def test_public_book_titles_name_the_software_engineering_audience(self):
        chinese = (ROOT / "book/book.json").read_text(encoding="utf-8")
        english = (ROOT / "book/translations/en/book.json").read_text(encoding="utf-8")
        self.assertIn("理解大模型：面向软件工程师的原理与系统指南", chinese)
        self.assertIn("Understanding LLMs for Software Engineers", english)
        self.assertIn("理解大模型：面向软件工程师的原理与系统指南", (ROOT / "README.zh-CN.md").read_text(encoding="utf-8"))
        self.assertIn("Understanding LLMs for Software Engineers", (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_public_materials_do_not_rank_or_disclaim_either_edition(self):
        public_materials = (
            "README.md",
            "README.zh-CN.md",
            "book/preface.md",
            "book/translations/en/preface.md",
            "learning/README.md",
            "learning/README.en.md",
            "learning/AI_ENTRY.zh-Hans.md",
            "learning/AI_ENTRY.en.md",
            "learning/LEARNING_CONTRACT.zh-Hans.md",
            "learning/LEARNING_CONTRACT.en.md",
        )
        prohibited = (
            "AI-assisted English edition",
            "awaits human editorial review",
            "尚待人工编辑审校",
            "中文是权威内容",
            "Chinese is authoritative",
        )
        for relative_path in public_materials:
            text = (ROOT / relative_path).read_text(encoding="utf-8")
            for phrase in prohibited:
                self.assertNotIn(phrase, text, relative_path)


if __name__ == "__main__":
    unittest.main()
