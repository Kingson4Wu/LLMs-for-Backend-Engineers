import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "book-kit"))


class BilingualMirrorTests(unittest.TestCase):
    def test_formula_semantics_ignore_localized_text_but_reject_math_changes(self):
        from audit_bilingual_mirror import compare_formula_semantics

        self.assertEqual(
            compare_formula_semantics(
                [r"H(P,Q)=-\\log Q_{\\text{正确类}}"],
                [r"H(P,Q)=-\\log Q_{\\text{correct class}}"],
            ),
            [],
        )
        self.assertEqual(
            compare_formula_semantics([r"y=Wx+b"], [r"y=Wx-b"]),
            ["Formula 1 mathematical structure differs"],
        )

    def test_full_catalogue_is_a_strict_bilingual_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root), {})

    def test_ai_learning_guide_is_a_strict_bilingual_appendix_mirror(self):
        from audit_bilingual_mirror import audit_book
        import json

        root = Path(__file__).resolve().parents[1]
        source_catalogue = json.loads((root / "book/catalog.json").read_text(encoding="utf-8"))
        english_catalogue = json.loads(
            (root / "book/translations/en/catalog.json").read_text(encoding="utf-8")
        )
        self.assertEqual(source_catalogue["parts"][-1]["chapters"][-1]["id"], "ai-learning-guide")
        self.assertEqual(english_catalogue["parts"][-1]["chapters"][-1]["id"], "ai-learning-guide")
        self.assertEqual(audit_book(root, article="ai-learning-guide"), {})

    def test_inventory_preserves_heading_formula_image_and_link_order(self):
        from audit_bilingual_mirror import inventory_markdown

        inventory = inventory_markdown(
            "# Title\n\n## Section\n\n$$x$$\n\n"
            "![diagram](assets/a.svg)\n\n[Next](next.md)\n"
        )

        self.assertEqual(
            [unit["kind"] for unit in inventory],
            ["heading:1", "heading:2", "formula", "image", "link"],
        )
        self.assertEqual([unit["ordinal"] for unit in inventory], list(range(5)))

    def test_audit_rejects_extra_english_unit_and_unpaired_figure(self):
        from audit_bilingual_mirror import compare_ledgers

        errors = compare_ledgers(
            [{"kind": "heading:2", "ordinal": 0}],
            [{"kind": "heading:2", "ordinal": 0}, {"kind": "image", "ordinal": 1}],
            {"units": [{"zh": 0, "en": 0}]},
        )

        self.assertIn("English has an unmapped image at ordinal 1", errors)

    def test_inventory_comparison_reports_the_first_structural_divergence(self):
        from audit_bilingual_mirror import compare_inventories

        errors = compare_inventories(
            [{"kind": "heading:1", "ordinal": 0}, {"kind": "formula", "ordinal": 1}],
            [{"kind": "heading:1", "ordinal": 0}, {"kind": "paragraph", "ordinal": 1}],
        )

        self.assertEqual(errors, ["Unit 1 differs: Chinese formula, English paragraph"])

    def test_figure_pair_comparison_rejects_an_incorrect_english_asset(self):
        from audit_bilingual_mirror import compare_figure_paths

        errors = compare_figure_paths(
            ["../../assets/zh/diagrams/example/source.svg"],
            ["../../../../assets/en/diagrams/example/wrong.svg"],
            [{"zh": "book/assets/zh/diagrams/example/source.svg", "en": "book/assets/en/diagrams/example/target.svg"}],
        )

        self.assertEqual(errors, ["Figure 1 English asset differs: expected assets/en/diagrams/example/target.svg, found assets/en/diagrams/example/wrong.svg"])

    def test_article_filter_limits_the_audit_to_one_article(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        errors = audit_book(root, article="softmax")

        self.assertEqual(errors, {})

    def test_vanishing_gradient_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertNotIn("vanishing-exploding-gradients", audit_book(root, part="math-foundations"))

    def test_backpropagation_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertNotIn("backpropagation", audit_book(root, part="math-foundations"))

    def test_activation_functions_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertNotIn("activation-functions", audit_book(root, part="math-foundations"))

    def test_onehot_embedding_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertNotIn("from-onehot-to-embedding", audit_book(root, part="math-foundations"))

    def test_dot_product_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertNotIn("dot-product-angle", audit_book(root, part="math-foundations"))

    def test_perceptron_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertNotIn("perceptron-learning", audit_book(root, part="math-foundations"))

    def test_softmax_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertNotIn("softmax", audit_book(root, part="math-foundations"))

    def test_ai_math_foundations_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertNotIn("ai-math-foundations", audit_book(root, part="math-foundations"))

    def test_cross_entropy_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertNotIn("cross-entropy", audit_book(root, part="math-foundations"))

    def test_inference_nondeterminism_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="llm-inference-nondeterminism"), {})

    def test_llm_infrastructure_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="llm-infrastructure"), {})

    def test_rnn_to_transformer_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="rnn-to-transformer"), {})

    def test_fine_tuning_and_distillation_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="fine-tuning-and-distillation"), {})

    def test_layer_norm_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="layer-norm"), {})

    def test_residual_connections_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="residual-connections"), {})

    def test_embedding_evolution_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="embedding-evolution"), {})

    def test_optimizer_selection_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="optimizer-selection"), {})

    def test_softmax_gradient_scaling_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="softmax-gradient-scaling"), {})

    def test_mhs_mcp_domain_capability_protocol_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="mhs-mcp-domain-capability-protocol"), {})

    def test_function_calling_tool_use_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="function-calling-tool-use"), {})

    def test_agent_eval_business_quality_system_chapter_is_a_strict_structural_mirror(self):
        from audit_bilingual_mirror import audit_book

        root = Path(__file__).resolve().parents[1]
        self.assertEqual(audit_book(root, article="agent-eval-business-quality-system"), {})
