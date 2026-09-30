import json
import re
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools' / 'book-kit'))


class FigureValidationTests(unittest.TestCase):
    def test_book_sources_avoid_pdf_unsupported_subscript_k(self):
        """Noto's CI CJK font lacks U+2096 in both SVGs and PDF figure captions."""
        figures = Path('book/assets').rglob('*.svg')
        chapters = list(Path('book/chapters').rglob('*.md')) + list(
            Path('book/translations/en/chapters').rglob('*.md')
        )
        offenders = [
            path.as_posix()
            for path in [*figures, *chapters]
            if 'ₖ' in path.read_text(encoding='utf-8')
        ]
        self.assertEqual(offenders, [])

    def test_mhs_mcp_diagrams_use_the_paper_pastel_palette(self):
        roots = (
            Path('book/assets/zh/posts/20260831-mhs-mcp-domain-capability-protocol'),
            Path('book/assets/en/diagrams/mhs-mcp-domain-capability-protocol'),
        )
        forbidden = {'#0F4D92', '#17324D', '#3775BA', '#416985', '#5E7F9C', '#8F3635', '#765800'}
        for root in roots:
            for diagram in root.glob('*.svg'):
                with self.subTest(diagram=diagram):
                    content = diagram.read_text(encoding='utf-8')
                    self.assertFalse(any(token in content for token in forbidden))
                    self.assertIsNone(
                        re.search(r'<(?:rect|path|circle|polygon|ellipse)\b[^>]*fill="#665F57"', content)
                    )

    def test_browser_layout_audit_reports_text_outside_its_visual_card(self):
        from audit_figure_layout import containment_error

        error = containment_error(
            {"x": 182, "y": 42, "width": 48, "height": 16},
            {"x": 100, "y": 30, "width": 120, "height": 50},
        )

        self.assertEqual(error, {"right": 10.0})

    def test_audit_reports_missing_metadata_and_out_of_bounds_text(self):
        from audit_figures import audit_svg

        with tempfile.TemporaryDirectory() as tmp:
            figure = Path(tmp) / 'broken.svg'
            figure.write_text(
                '<svg viewBox="0 0 100 50" role="img"><text x="140" y="20">x</text></svg>',
                encoding='utf-8',
            )
            errors = audit_svg(figure)
            self.assertTrue(any('title' in error for error in errors))
            self.assertTrue(any('desc' in error for error in errors))
            self.assertTrue(any('viewBox' in error for error in errors))

    def test_audit_reports_connector_intersecting_text_safe_zone(self):
        from audit_figures import audit_svg

        with tempfile.TemporaryDirectory() as tmp:
            figure = Path(tmp) / 'overlap.svg'
            figure.write_text(
                '''<svg viewBox="0 0 100 60" role="img">
                <title>Overlap</title><desc>A connector crosses a text safe zone.</desc>
                <rect data-figure-safe-zone="text" x="35" y="20" width="30" height="20"/>
                <path data-figure-connector="true" d="M 10 30 H 90"/>
                </svg>''',
                encoding='utf-8',
            )
            errors = audit_svg(figure)
            self.assertTrue(any('connector intersects text safe zone' in error for error in errors))

    def test_audit_allows_connector_outside_text_safe_zone(self):
        from audit_figures import audit_svg

        with tempfile.TemporaryDirectory() as tmp:
            figure = Path(tmp) / 'clear.svg'
            figure.write_text(
                '''<svg viewBox="0 0 100 60" role="img">
                <title>Clear</title><desc>A connector remains in the routing gutter.</desc>
                <rect data-figure-safe-zone="text" x="35" y="20" width="30" height="20"/>
                <path data-figure-connector="true" d="M 10 10 H 90"/>
                </svg>''',
                encoding='utf-8',
            )
            errors = audit_svg(figure)
            self.assertFalse(any('connector intersects text safe zone' in error for error in errors))

    def test_audit_supports_a_curved_connector_in_a_clear_routing_gutter(self):
        from audit_figures import audit_svg

        with tempfile.TemporaryDirectory() as tmp:
            figure = Path(tmp) / 'curved-clear.svg'
            figure.write_text(
                '''<svg viewBox="0 0 100 60" role="img">
                <title>Curved route</title><desc>A Bezier connector stays above the text.</desc>
                <rect data-figure-safe-zone="text" x="35" y="20" width="30" height="20"/>
                <path data-figure-connector="true" d="M 10 10 C 30 10 70 10 90 10"/>
                </svg>''',
                encoding='utf-8',
            )
            errors = audit_svg(figure)
            self.assertFalse(any('supported straight routing path' in error for error in errors))
            self.assertFalse(any('connector intersects text safe zone' in error for error in errors))

    def test_audit_does_not_connect_separate_path_subpaths(self):
        from audit_figures import audit_svg

        with tempfile.TemporaryDirectory() as tmp:
            figure = Path(tmp) / 'separate-subpaths.svg'
            figure.write_text(
                '''<svg viewBox="0 0 100 60" role="img">
                <title>Separate routes</title><desc>Two routes stay above and below the label.</desc>
                <rect data-figure-safe-zone="text" x="35" y="20" width="30" height="20"/>
                <path data-figure-connector="true" d="M 10 10 H 90 M 10 50 H 90"/>
                </svg>''',
                encoding='utf-8',
            )
            errors = audit_svg(figure)
            self.assertFalse(any('connector intersects text safe zone' in error for error in errors))

    def test_audit_allows_a_text_safe_zone_to_extend_past_canvas_padding(self):
        from audit_figures import audit_svg

        with tempfile.TemporaryDirectory() as tmp:
            figure = Path(tmp) / 'edge-label.svg'
            figure.write_text(
                '''<svg viewBox="0 0 100 60" role="img">
                <title>Edge label</title><desc>Safety padding may extend outside the canvas.</desc>
                <rect data-figure-safe-zone="text" x="-12" y="-12" width="40" height="30"/>
                </svg>''',
                encoding='utf-8',
            )
            errors = audit_svg(figure)
            self.assertFalse(any('safe zone needs' in error for error in errors))

    def test_publication_palette_repaints_legacy_semantic_colours(self):
        from repaint_publication_figures import repaint_svg

        with tempfile.TemporaryDirectory() as tmp:
            figure = Path(tmp) / 'legacy.svg'
            figure.write_text(
                '<svg><rect fill="#fffdf8"/><path stroke="#315f55"/><circle fill="#bd6257"/></svg>',
                encoding='utf-8',
            )
            self.assertTrue(repaint_svg(figure))
            result = figure.read_text(encoding='utf-8')
            self.assertIn('#FFFFFF', result)
            self.assertIn('#0F4D92', result)
            self.assertIn('#B64342', result)

    def test_softmax_layout_fix_wraps_the_overlong_english_output_heading(self):
        from fix_figure_layouts import relayout_softmax_english

        source = (
            '<text x="812" y="216" class="h" fill="#17324D">Output probabilities p</text>'
            '<text x="560" y="335" text-anchor="middle" class="b" fill="#765800">exponentiate + normalize</text>'
            '<text x="976" y="269" class="b" fill="#17324D">p₁ = 0.659</text>'
        )
        result = relayout_softmax_english(source)
        self.assertIn('>Output</text>', result)
        self.assertIn('>probabilities p</text>', result)
        self.assertNotIn('>Output probabilities p</text>', result)
        self.assertIn('>exponentiate</text>', result)
        self.assertIn('>+ normalize</text>', result)
        self.assertIn('x="950" y="285"', result)

    def test_prefill_layout_fix_wraps_long_english_card_labels(self):
        from fix_figure_layouts import relayout_prefill_decode_english

        source = (
            '<text x="97" y="291" class="s" fill="#5E7F9C">prompt and conversation history</text>'
            '<text x="398" y="229" class="b" fill="#765800">process existing input tokens in parallel</text>'
            '<text x="438" y="442" class="h" fill="#FFFFFF">KV cache: accumulated attention state</text>'
        )
        result = relayout_prefill_decode_english(source)
        self.assertIn('>process existing input tokens</text>', result)
        self.assertIn('>in parallel</text>', result)
        self.assertIn('>KV cache: accumulated</text>', result)
        self.assertIn('>attention state</text>', result)
        self.assertIn('>prompt and</text>', result)
        self.assertIn('>conversation history</text>', result)

    def test_tanh_and_system_map_layout_fixes_keep_long_english_labels_in_cards(self):
        from fix_figure_layouts import relayout_system_map_english, relayout_tanh_english

        tanh = relayout_tanh_english(
            '<text x="738" y="224" class="b" fill="#416985">positive and negative are symmetric</text>'
        )
        system_map = relayout_system_map_english('<rect width="156" height="184" rx="18" fill="#23332F"/>')
        self.assertIn('>positive and negative</text>', tanh)
        self.assertIn('>are symmetric</text>', tanh)
        self.assertIn('width="200" height="184"', system_map)
        details = relayout_system_map_english('<text x="26" y="150" fill="#64736C" font-size="14">How information enters learnable computation</text>')
        self.assertIn('>How information enters</text>', details)
        self.assertIn('>learnable computation</text>', details)

    def test_xor_network_layout_fix_wraps_the_long_footer_note(self):
        from fix_figure_layouts import relayout_xor_network_english

        source = '<text x="92" y="563" font-size="17" fill="#8F3635">This is an explicit illustrative construction: nonlinearity partitions the plane into composable regions; training need not find these exact weights.</text>'
        result = relayout_xor_network_english(source)
        self.assertIn('>This is an explicit illustrative construction: nonlinearity partitions the plane into composable regions.</text>', result)
        self.assertIn('>Training need not find these exact weights.</text>', result)

    def test_feedback_boundary_layout_fix_wraps_the_overlong_input_label(self):
        from fix_figure_layouts import relayout_feedback_boundary_english

        source = (
            '<rect x="625" y="225" width="260" height="118" rx="23"/>'
            '<path d="M885 284H950"/>'
            '<text x="160" y="294" fill="#0F4D92">inputs and objectives</text>'
            '<text x="1060" y="294" fill="#B64342">environment + feedback</text>'
        )
        result = relayout_feedback_boundary_english(source)
        self.assertIn('>inputs and</text>', result)
        self.assertIn('>objectives</text>', result)
        self.assertNotIn('>inputs and objectives</text>', result)
        self.assertIn('width="280"', result)
        self.assertIn('>environment +</text>', result)
        self.assertIn('>feedback</text>', result)

    def test_product_stack_layout_fix_wraps_layer_descriptions(self):
        from fix_figure_layouts import relayout_product_stack_english

        source = (
            '<text x="270" y="510" font-size="17" fill="#B64342">source of learned language and calling patterns</text>'
            '<text x="620" y="310" font-size="17" fill="#765800">integration and discovery for tools and context</text>'
            '<text x="795" y="210" font-size="17" fill="#0F4D92">user experience, workflow, and execution boundary</text>'
        )
        result = relayout_product_stack_english(source)
        self.assertIn('>source of learned language</text>', result)
        self.assertIn('>and calling patterns</text>', result)
        self.assertIn('>integration and discovery</text>', result)
        self.assertIn('>for tools and context</text>', result)
        self.assertIn('>user experience and workflow</text>', result)
        self.assertIn('>execution boundary</text>', result)

    def test_runtime_diagram_layout_fixes_keep_labels_inside_their_cards(self):
        from fix_figure_layouts import relayout_skill_contents_english, relayout_stable_path_layers_english

        stable = relayout_stable_path_layers_english(
            '<text x="230" y="203" font-size="22" font-weight="700" fill="#17324D">stable goals, constraints, and acceptance conditions</text>'
            '<text x="235" y="306" font-size="22" font-weight="700" fill="#765800">adaptive layer: model selects the next step from observations</text>'
        )
        self.assertIn('>stable goals, constraints,</text>', stable)
        self.assertIn('>and acceptance conditions</text>', stable)
        self.assertIn('>adaptive layer</text>', stable)
        self.assertIn('>model selects the next step from observations</text>', stable)
        skill = relayout_skill_contents_english(
            '<text x="455" y="480" font-size="21" font-weight="700" fill="#B64342">acceptance, recovery, escalation</text>'
            '<text x="790" y="480" font-size="17" fill="#B64342">how to confirm, and how to handle failure</text>'
        )
        self.assertIn('x="455" y="466"', skill)
        self.assertIn('x="455" y="492"', skill)
        resources = relayout_skill_contents_english(
            '<text x="790" y="385" font-size="17" fill="#0F4D92">scripts, templates, references, known-good practices</text>'
        )
        self.assertIn('>scripts, templates, references,</text>', resources)
        self.assertIn('>known-good practices</text>', resources)

    def test_kv_reuse_layout_fix_wraps_small_card_and_panel_labels(self):
        from fix_figure_layouts import relayout_kv_prefix_reuse_english

        source = (
            '<text x="165" y="290" font-size="19" font-weight="700" fill="#17324D">processed tokens</text>'
            '<text x="475" y="290" font-size="19" font-weight="700" fill="#17324D">next attention step</text>'
            '<text x="1045" y="320" font-size="16" fill="#0F4D92">compute new suffix only</text>'
            '<text x="885" y="415" text-anchor="middle" font-size="17" fill="#765800">Similar text does not guarantee a hit; authority boundaries cannot be shared.</text>'
        )
        result = relayout_kv_prefix_reuse_english(source)
        self.assertIn('>processed</text>', result)
        self.assertIn('>tokens</text>', result)
        self.assertIn('>next attention</text>', result)
        self.assertIn('>step</text>', result)
        self.assertIn('>compute new</text>', result)
        self.assertIn('>suffix only</text>', result)
        self.assertIn('>Similar text does not guarantee a hit.</text>', result)

    def test_foundation_layout_fixes_prevent_card_overflow(self):
        from fix_figure_layouts import relayout_deep_scale_drift_english, relayout_system_flow_english

        drift = relayout_deep_scale_drift_english('<rect x="316" y="410" width="488" height="72" rx="23"/>')
        self.assertIn('x="270" y="410" width="580"', drift)
        flow = relayout_system_flow_english(
            '<rect x="55" y="235" width="200" height="74" rx="15"/>'
            '<text x="155" y="291">patterns learned over time</text>'
        )
        self.assertIn('height="100"', flow)
        self.assertIn('>patterns learned</text>', flow)
        self.assertIn('>over time</text>', flow)

    def test_external_interaction_layout_fixes_wrap_overlong_labels(self):
        from fix_figure_layouts import (
            relayout_agent_feedback_loop_english,
            relayout_structured_output_validation_english,
            relayout_validation_boundaries_english,
        )
        agent = relayout_agent_feedback_loop_english('<text x="140" y="226" font-size="22" font-weight="700" fill="#17324D">task + explicit state</text>')
        self.assertIn('>task + explicit</text>', agent)
        structured = relayout_structured_output_validation_english('<text x="385" y="242" font-size="22" font-weight="700" fill="#765800">grammar / schema state</text>')
        self.assertIn('>grammar / schema</text>', structured)
        boundaries = relayout_validation_boundaries_english('<text x="650" y="184" font-size="18" fill="#765800">parseable? complete fields? correct types?</text>')
        self.assertIn('x="410" y="208"', boundaries)

    def test_engine_layout_fix_wraps_the_narrow_engine_card_copy(self):
        from fix_figure_layouts import relayout_config_weights_engine_english
        result = relayout_config_weights_engine_english('<text x="914" y="255" class="b" fill="#8F3635">architecture adapter: builds</text><text x="914" y="287" class="b" fill="#8F3635">general runtime: schedules and runs</text>')
        self.assertIn('>architecture adapter builds</text>', result)
        self.assertIn('>general runtime schedules</text>', result)
        self.assertIn('>and runs</text>', result)

    def test_mcp_and_mhs_layout_fixes_wrap_canvas_width_copy(self):
        from fix_figure_layouts import relayout_mcp_basic_shape_english, relayout_mhs_integration_pain_english
        mcp = relayout_mcp_basic_shape_english('<text x="94" y="515" font-size="18" fill="#FFFFFF">MCP answers how to connect and expose; reliability, security, and business semantics of the exposed capability still need modeling.</text>')
        self.assertIn('>MCP answers how to connect and expose.</text>', mcp)
        mhs = relayout_mhs_integration_pain_english('<text x="94" y="542" font-size="18" fill="#FFFFFF">The goal is not one universal function name, but reusable capability semantics that make cross-device workflows reliable and governable.</text>')
        self.assertIn('>The goal is reusable capability semantics for reliable,</text>', mhs)

    def test_mhs_editorial_figures_wrap_english_copy_inside_cards(self):
        root = Path(__file__).resolve().parents[1]
        integration = (root / 'book/assets/en/diagrams/mhs-mcp-domain-capability-protocol/mhs-integration-pain.svg').read_text(encoding='utf-8')
        capability = (root / 'book/assets/en/diagrams/mhs-mcp-domain-capability-protocol/hardware-capability-model.svg').read_text(encoding='utf-8')
        examples = (root / 'book/assets/en/diagrams/mhs-mcp-domain-capability-protocol/domain-examples.svg').read_text(encoding='utf-8')

        self.assertRegex(integration, r'agents can discover</text><text x="877" y="436"')
        self.assertRegex(capability, r'constraints: workspace .*?</text><text x="447" y="359"')
        self.assertRegex(examples, r'objects: payment .*?</text><text x="97" y="273"')

    def test_multimodal_signal_layout_fix_wraps_the_right_card_and_footer(self):
        from fix_figure_layouts import relayout_cross_modal_training_signals_english
        result = relayout_cross_modal_training_signals_english('<text x="750" y="221" class="b">given some modalities, predict text or another modality</text><text x="94" y="594" font-size="17" fill="#8F3635">Paired material does not automatically teach a specific Q&amp;A task; targets and evaluation must cover the cross-modal relation you need.</text>')
        self.assertIn('>given modalities, predict text</text>', result)
        self.assertIn('>or another modality</text>', result)
        self.assertIn('>Paired material alone does not teach a specific Q&amp;A task.</text>', result)

    def test_parameter_update_layout_fix_wraps_forward_prediction_copy(self):
        from fix_figure_layouts import relayout_parameter_update_cycle_english
        result = relayout_parameter_update_cycle_english('<text x="400" y="264" font-size="16" fill="#0F4D92">θ participates in computation</text><text x="400" y="290" font-size="16" fill="#0F4D92">to produce vocabulary probabilities</text>')
        self.assertIn('>θ participates</text>', result)
        self.assertIn('>in computation</text>', result)
        self.assertIn('>produce vocabulary</text>', result)

    def test_overview_and_rollout_layout_fixes_keep_long_copy_inside_cards(self):
        from fix_figure_layouts import (
            relayout_multimodal_overview_english,
            relayout_progressive_rollout_english,
        )

        overview = relayout_multimodal_overview_english(
            '<text x="58" y="105" font-size="18" fill="#5E7F9C">Each modality first becomes a representation the model can consume; accepting input does not imply generating that modality or fully understanding reality.</text>'
            '<rect x="935" y="390" width="190" height="74" rx="18" stroke="#B64342"/>'
            '<text x="1030" y="436" font-size="20" font-weight="700" fill="#B64342">image / video representation + decoder</text>'
        )
        self.assertIn('>Each modality becomes a representation the model can consume; accepting input</text>', overview)
        self.assertIn('>does not imply generating that modality or fully understanding reality.</text>', overview)
        self.assertIn('y="380" width="230" height="100"', overview)
        self.assertIn('>image / video</text>', overview)
        self.assertIn('>representation</text>', overview)

        rollout = relayout_progressive_rollout_english(
            '<rect x="310" y="450" width="580" height="78" rx="20" fill="#F6CFCB" stroke="#B64342" stroke-width="3"/>'
            '<text x="600" y="512" text-anchor="middle" font-size="17" fill="#B64342">Quality, error rate, TTFT, cost, policy, or safety metrics trigger predefined stopping conditions.</text>'
        )
        self.assertIn('y="443" width="580" height="99"', rollout)
        self.assertIn('>trigger predefined stopping conditions.</text>', rollout)
        self.assertIn('y="525"', rollout)

    def test_chinese_counterparts_keep_output_and_example_labels_inside_cards(self):
        from fix_figure_layouts import (
            relayout_domain_examples_chinese,
            relayout_multimodal_overview_chinese,
        )

        overview = relayout_multimodal_overview_chinese(
            '<path d="M870 330H930"/>'
            '<rect x="935" y="290" width="190" height="74" rx="18" stroke="#B64342"/>'
            '<text x="1030" y="336" font-size="20" font-weight="700" fill="#B64342">音频 token／解码器 → 声音</text>'
            '<text x="1030" y="436" font-size="20" font-weight="700" fill="#B64342">图像／视频表示 + 解码器</text>'
        )
        self.assertIn('d="M870 330H890"', overview)
        self.assertIn('x="895" y="290" width="245"', overview)
        self.assertIn('>音频 token／</text>', overview)
        self.assertIn('>图像／视频表示</text>', overview)

        examples = relayout_domain_examples_chinese(
            '<text x="837" y="389" class="s" fill="#8D625A">HomeKit / 米家 / Google Home / Home Assistant</text>'
        )
        self.assertIn('>HomeKit / 米家 / Google Home</text>', examples)
        self.assertIn('>Home Assistant</text>', examples)

    def test_layout_contract_marks_text_safety_zones_and_connectors(self):
        from add_figure_layout_contract import contract_svg

        with tempfile.TemporaryDirectory() as tmp:
            figure = Path(tmp) / 'source.svg'
            figure.write_text(
                '''<svg viewBox="0 0 100 60" role="img"><title>Safe</title><desc>Safe route.</desc>
                <text x="50" y="25" font-size="20">Label</text>
                <path d="M 10 50 H 90" marker-end="url(#arrow)"/></svg>''',
                encoding='utf-8',
            )
            self.assertTrue(contract_svg(figure))
            result = figure.read_text(encoding='utf-8')
            self.assertIn('data-figure-safe-zone="text"', result)
            self.assertIn('data-figure-connector="true"', result)
            from audit_figures import audit_svg
            self.assertFalse(any('invalid XML' in error for error in audit_svg(figure)))
            self.assertFalse(contract_svg(figure))

    def test_layout_contract_does_not_measure_math_subscripts_as_wide_cjk_glyphs(self):
        from add_figure_layout_contract import TEXT, text_zone

        match = TEXT.search('<text x="97" y="304" class="b">x₁, x₂ ∈ {0, 1}</text>')
        self.assertIsNotNone(match)
        zone = text_zone(match)
        self.assertIsNotNone(zone)
        width = float(re.search(r'width="([0-9.]+)"', zone).group(1))
        self.assertLess(width, 180)

    def test_manifest_requires_each_editorial_svg_and_accessible_metadata(self):
        from validate_figures import validate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / 'book' / 'assets'
            assets.mkdir(parents=True)
            (assets / 'diagram.svg').write_text(
                '<svg role="img"><title>Diagram</title><desc>Explains a flow.</desc></svg>',
                encoding='utf-8',
            )
            manifest = root / 'figures.json'
            manifest.write_text(
                json.dumps({'figures': [{'path': 'book/assets/diagram.svg', 'kind': 'diagram'}]}),
                encoding='utf-8',
            )
            self.assertEqual(validate(root, manifest), [])

            (assets / 'diagram.svg').write_text('<svg></svg>', encoding='utf-8')
            errors = validate(root, manifest)
            self.assertTrue(any('role="img"' in error for error in errors))
            self.assertTrue(any('<title>' in error for error in errors))
            self.assertTrue(any('<desc>' in error for error in errors))

    def test_manifest_flags_unlisted_svg_assets(self):
        from validate_figures import validate

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            assets = root / 'book' / 'assets'
            assets.mkdir(parents=True)
            (assets / 'unlisted.svg').write_text('<svg></svg>', encoding='utf-8')
            manifest = root / 'figures.json'
            manifest.write_text(json.dumps({'figures': []}), encoding='utf-8')
            self.assertTrue(any('not listed' in error for error in validate(root, manifest)))

    def test_semantic_inventory_requires_explicit_roles_alternatives_and_source_context(self):
        from validate_figures import validate_semantics

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            zh_asset = root / 'book/assets/zh/diagram.svg'
            en_asset = root / 'book/assets/en/diagram.svg'
            decorative = root / 'book/assets/cover.svg'
            for asset in (zh_asset, en_asset, decorative):
                asset.parent.mkdir(parents=True, exist_ok=True)
                asset.write_text('<svg/>', encoding='utf-8')
            zh_source = root / 'book/chapters/topic.md'
            en_source = root / 'book/translations/en/chapters/topic.md'
            zh_source.parent.mkdir(parents=True)
            en_source.parent.mkdir(parents=True)
            zh_source.write_text('## 正确标题\n\n![中文等效说明](../assets/zh/diagram.svg)', encoding='utf-8')
            en_source.write_text('## Correct heading\n\n![English equivalent explanation](../../../assets/en/diagram.svg)', encoding='utf-8')
            figures = {'figures': [
                {'id': 'zh-topic-diagram', 'path': 'book/assets/zh/diagram.svg', 'kind': 'diagram', 'role': 'informational'},
                {'id': 'en-topic-diagram', 'path': 'book/assets/en/diagram.svg', 'kind': 'diagram', 'role': 'informational'},
                {'id': 'cover', 'path': 'book/assets/cover.svg', 'kind': 'cover'},
            ]}
            pairs = {'pairs': [{
                'id': 'topic-diagram', 'chapter': 'topic', 'ordinal': 1,
                'zh': 'book/assets/zh/diagram.svg', 'en': 'book/assets/en/diagram.svg',
                'zh_id': 'zh-topic-diagram', 'en_id': 'en-topic-diagram',
                'zh_source': 'book/chapters/topic.md', 'en_source': 'book/translations/en/chapters/topic.md',
                'semantics': {
                    'zh': {'chapter': 'topic', 'heading': '错误标题', 'alternative': ''},
                    'en': {'chapter': 'topic', 'heading': 'Correct heading', 'alternative': 'English equivalent explanation'},
                },
            }]}
            errors = validate_semantics(root, figures, pairs)

        self.assertIn('figure needs explicit role: book/assets/cover.svg', errors)
        self.assertIn('informational figure needs zh alternative text: topic-diagram', errors)
        self.assertIn('semantic heading is absent from zh source: topic-diagram', errors)

    def test_semantic_inventory_derives_chapter_from_both_catalogues(self):
        from validate_figures import validate_semantics

        root = Path(__file__).resolve().parents[1]
        figures = json.loads((root / 'book/figures.json').read_text(encoding='utf-8'))
        pairs = json.loads((root / 'book/figure-pairs.json').read_text(encoding='utf-8'))
        mutated = deepcopy(pairs)
        pair = mutated['pairs'][0]
        pair['chapter'] = 'coordinated-wrong-chapter'
        pair['semantics']['zh']['chapter'] = 'coordinated-wrong-chapter'
        pair['semantics']['en']['chapter'] = 'coordinated-wrong-chapter'

        errors = validate_semantics(root, figures, mutated)

        self.assertIn('semantic zh source chapter does not match catalog: introduction-01', errors)
        self.assertIn('semantic en source chapter does not match catalog: introduction-01', errors)

    def test_semantic_inventory_rejects_an_unpaired_informational_figure(self):
        from validate_figures import validate_semantics

        figures = {'figures': [{
            'id': 'orphan-diagram', 'path': 'book/assets/en/orphan.svg',
            'kind': 'diagram', 'role': 'informational',
        }]}

        self.assertIn(
            'informational figure has no semantic pair: orphan-diagram',
            validate_semantics(Path('.'), figures, {'pairs': []}),
        )

    def test_pair_validation_reports_a_missing_english_counterpart(self):
        from validate_figures import validate_pairs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chinese = root / 'book/assets/zh/diagrams/topic/source.svg'
            chinese.parent.mkdir(parents=True)
            chinese.write_text('<svg/>', encoding='utf-8')
            pairs = {
                'pairs': [
                    {
                        'chapter': 'topic',
                        'ordinal': 1,
                        'zh': 'book/assets/zh/diagrams/topic/source.svg',
                        'en': 'book/assets/en/diagrams/topic/counterpart.svg',
                    }
                ]
            }
            errors = validate_pairs(root, pairs)
            self.assertTrue(any('missing English counterpart' in error for error in errors))

    def test_pair_validation_requires_each_counterpart_to_be_referenced_in_its_source(self):
        from validate_figures import validate_pairs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chinese = root / 'book/assets/zh/diagrams/topic/source.svg'
            english = root / 'book/assets/en/diagrams/topic/counterpart.svg'
            chinese.parent.mkdir(parents=True)
            english.parent.mkdir(parents=True)
            chinese.write_text('<svg/>', encoding='utf-8')
            english.write_text('<svg/>', encoding='utf-8')
            zh_source = root / 'book/chapters/part/topic.md'
            en_source = root / 'book/translations/en/chapters/part/topic.md'
            zh_source.parent.mkdir(parents=True)
            en_source.parent.mkdir(parents=True)
            zh_source.write_text('![zh](../../../assets/zh/diagrams/topic/source.svg)', encoding='utf-8')
            en_source.write_text('# Missing image reference', encoding='utf-8')
            pairs = {
                'pairs': [{
                    'chapter': 'topic', 'ordinal': 1,
                    'zh': 'book/assets/zh/diagrams/topic/source.svg',
                    'en': 'book/assets/en/diagrams/topic/counterpart.svg',
                    'zh_source': 'book/chapters/part/topic.md',
                    'en_source': 'book/translations/en/chapters/part/topic.md',
                }]
            }
            errors = validate_pairs(root, pairs)
            self.assertTrue(any('does not reference English counterpart' in error for error in errors))

    def test_pair_validation_reports_a_chinese_figure_missing_from_the_pair_manifest(self):
        from validate_figures import validate_pairs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            zh_assets = root / 'book/assets/zh/diagrams/topic'
            en_assets = root / 'book/assets/en/diagrams/topic'
            zh_assets.mkdir(parents=True)
            en_assets.mkdir(parents=True)
            for path in (zh_assets / 'one.svg', zh_assets / 'two.svg', en_assets / 'one.svg'):
                path.write_text('<svg/>', encoding='utf-8')
            zh_source = root / 'book/chapters/part/topic.md'
            en_source = root / 'book/translations/en/chapters/part/topic.md'
            zh_source.parent.mkdir(parents=True)
            en_source.parent.mkdir(parents=True)
            zh_source.write_text(
                '![one](../../assets/zh/diagrams/topic/one.svg)\n![two](../../assets/zh/diagrams/topic/two.svg)',
                encoding='utf-8',
            )
            en_source.write_text('![one](../../../../assets/en/diagrams/topic/one.svg)', encoding='utf-8')
            pairs = {'pairs': [{
                'chapter': 'topic', 'ordinal': 1,
                'zh': 'book/assets/zh/diagrams/topic/one.svg',
                'en': 'book/assets/en/diagrams/topic/one.svg',
                'zh_source': 'book/chapters/part/topic.md',
                'en_source': 'book/translations/en/chapters/part/topic.md',
            }]}
            errors = validate_pairs(root, pairs)
            self.assertTrue(any('unpaired Chinese editorial figure' in error for error in errors))

    def test_pair_validation_detects_an_unpaired_image_when_alt_text_contains_brackets(self):
        from validate_figures import validate_pairs

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            figure = root / 'book/assets/zh/diagrams/topic/scale.svg'
            figure.parent.mkdir(parents=True)
            figure.write_text('<svg/>', encoding='utf-8')
            source = root / 'book/chapters/part/topic.md'
            source.parent.mkdir(parents=True)
            source.write_text(
                '![Softmax logits [2, 1, 0]](../../assets/zh/diagrams/topic/scale.svg)',
                encoding='utf-8',
            )
            errors = validate_pairs(root, {'pairs': []})
            self.assertTrue(any('unpaired Chinese editorial figure' in error for error in errors))
