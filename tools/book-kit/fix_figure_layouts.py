#!/usr/bin/env python3
"""Apply reviewed, language-specific relayouts to editorial SVG diagrams."""
from __future__ import annotations

import argparse
from pathlib import Path


def relayout_softmax_english(source: str) -> str:
    revised = source.replace(
        '<text x="812" y="216" class="h" fill="#17324D">Output probabilities p</text>',
        '<text x="812" y="205" class="h" fill="#17324D">Output</text>'
        '<text x="812" y="232" class="h" fill="#17324D">probabilities p</text>',
    )
    revised = revised.replace(
        '<text x="560" y="335" text-anchor="middle" class="b" fill="#765800">exponentiate + normalize</text>',
        '<text x="560" y="327" text-anchor="middle" class="b" fill="#765800">exponentiate</text>'
        '<text x="560" y="355" text-anchor="middle" class="b" fill="#765800">+ normalize</text>',
    )
    return revised.replace(
        '<text x="976" y="269" class="b" fill="#17324D">p₁ = 0.659</text>',
        '<text x="950" y="285" class="b" fill="#17324D">p₁ = 0.659</text>',
    )


def relayout_prefill_decode_english(source: str) -> str:
    replacements = {
        '<text x="97" y="291" class="s" fill="#5E7F9C">prompt and conversation history</text>': (
            '<text x="97" y="282" class="s" fill="#5E7F9C">prompt and</text>'
            '<text x="97" y="301" class="s" fill="#5E7F9C">conversation history</text>'
        ),
        '<rect x="366" y="145" width="312" height="182"': '<rect x="366" y="145" width="312" height="200"',
        '<text x="398" y="229" class="b" fill="#765800">process existing input tokens in parallel</text>': (
            '<text x="398" y="229" class="b" fill="#765800">process existing input tokens</text>'
            '<text x="398" y="252" class="b" fill="#765800">in parallel</text>'
        ),
        '<text x="398" y="260" class="b" fill="#765800">establish K / V state for each layer</text>': '<text x="398" y="279" class="b" fill="#765800">establish K / V state for each layer</text>',
        '<rect x="398" y="281" width="248" height="26"': '<rect x="398" y="299" width="248" height="26"',
        '<text x="522" y="301" text-anchor="middle" font-size="14" fill="#765800">the main compute before the first token</text>': '<text x="522" y="319" text-anchor="middle" font-size="14" fill="#765800">the main compute before the first token</text>',
        '<rect x="405" y="400" width="395" height="110"': '<rect x="405" y="400" width="395" height="134"',
        '<text x="438" y="442" class="h" fill="#FFFFFF">KV cache: accumulated attention state</text>': (
            '<text x="438" y="435" class="h" fill="#FFFFFF">KV cache: accumulated</text>'
            '<text x="438" y="460" class="h" fill="#FFFFFF">attention state</text>'
        ),
        '<text x="438" y="472" class="b" fill="#CFCECE">reuse existing K / V and append entries for the new token</text>': (
            '<text x="438" y="487" class="b" fill="#CFCECE">reuse existing K / V and append entries</text>'
            '<text x="438" y="509" class="b" fill="#CFCECE">for the new token</text>'
        ),
        '<text x="438" y="495" class="s" fill="#CFCECE">reduces repeated work, while consuming memory</text>': '<text x="438" y="528" class="s" fill="#CFCECE">reduces repeated work, while consuming memory</text>',
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    return source


def relayout_tanh_english(source: str) -> str:
    return source.replace(
        '<text x="738" y="224" class="b" fill="#416985">positive and negative are symmetric</text>',
        '<text x="738" y="214" class="b" fill="#416985">positive and negative</text>'
        '<text x="738" y="238" class="b" fill="#416985">are symmetric</text>',
    )


def relayout_system_map_english(source: str) -> str:
    revised = source.replace(
        '<rect width="156" height="184" rx="18" fill="#23332F"/>',
        '<rect width="200" height="184" rx="18" fill="#23332F"/>',
    )
    replacements = {
        '<text x="26" y="150" fill="#64736C" font-size="14">How information enters learnable computation</text>': (
            '<text x="26" y="145" fill="#64736C" font-size="14">How information enters</text>'
            '<text x="26" y="166" fill="#64736C" font-size="14">learnable computation</text>'
        ),
        '<text x="26" y="150" fill="#64736C" font-size="14">How parameters and context produce output</text>': (
            '<text x="26" y="145" fill="#64736C" font-size="14">How parameters and context</text>'
            '<text x="26" y="166" fill="#64736C" font-size="14">produce output</text>'
        ),
        '<text x="26" y="150" fill="#64736C" font-size="14">How a proposal becomes an outside action</text>': (
            '<text x="26" y="145" fill="#64736C" font-size="14">How a proposal becomes</text>'
            '<text x="26" y="166" fill="#64736C" font-size="14">an outside action</text>'
        ),
    }
    for old, new in replacements.items():
        revised = revised.replace(old, new)
    return revised


def relayout_xor_network_english(source: str) -> str:
    source = source.replace(
        '<rect x="65" y="535" width="970" height="42" rx="13" fill="#F6CFCB"/>',
        '<rect x="65" y="520" width="970" height="70" rx="13" fill="#F6CFCB"/>',
    )
    return source.replace(
        '<text x="92" y="563" font-size="17" fill="#8F3635">This is an explicit illustrative construction: nonlinearity partitions the plane into composable regions; training need not find these exact weights.</text>',
        '<text x="92" y="548" font-size="17" fill="#8F3635">This is an explicit illustrative construction: nonlinearity partitions the plane into composable regions.</text>'
        '<text x="92" y="573" font-size="17" fill="#8F3635">Training need not find these exact weights.</text>',
    )


def relayout_feedback_boundary_english(source: str) -> str:
    replacements = {
        '<text x="160" y="294" fill="#0F4D92">inputs and objectives</text>': (
            '<text x="160" y="282" fill="#0F4D92">inputs and</text>'
            '<text x="160" y="307" fill="#0F4D92">objectives</text>'
        ),
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    return (
        source
        .replace('<rect x="625" y="225" width="260" height="118" rx="23"', '<rect x="625" y="225" width="280" height="118" rx="23"')
        .replace('<path d="M885 284H950"', '<path d="M905 284H970"')
        .replace(
            '<text x="1060" y="294" fill="#B64342">environment + feedback</text>',
            '<text x="1060" y="282" fill="#B64342">environment +</text>'
            '<text x="1060" y="307" fill="#B64342">feedback</text>',
        )
    )


def relayout_product_stack_english(source: str) -> str:
    replacements = {
        '<text x="270" y="510" font-size="17" fill="#B64342">source of learned language and calling patterns</text>': (
            '<text x="270" y="503" font-size="17" fill="#B64342">source of learned language</text>'
            '<text x="270" y="528" font-size="17" fill="#B64342">and calling patterns</text>'
        ),
        '<text x="620" y="310" font-size="17" fill="#765800">integration and discovery for tools and context</text>': (
            '<text x="620" y="303" font-size="17" fill="#765800">integration and discovery</text>'
            '<text x="620" y="328" font-size="17" fill="#765800">for tools and context</text>'
        ),
        '<text x="795" y="210" font-size="17" fill="#0F4D92">user experience, workflow, and execution boundary</text>': (
            '<text x="795" y="203" font-size="17" fill="#0F4D92">user experience and workflow</text>'
            '<text x="795" y="228" font-size="17" fill="#0F4D92">execution boundary</text>'
        ),
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    return source


def relayout_stable_path_layers_english(source: str) -> str:
    replacements = {
        '<text x="58" y="105" text-anchor="start" font-size="18" fill="#5E7F9C">Models can propose strategy under uncertainty; assurance comes from explicit constraints, deterministic execution, and external-state validation.</text>': (
            '<text x="58" y="105" text-anchor="start" font-size="18" fill="#5E7F9C">Models can propose strategy under uncertainty; assurance comes from explicit constraints and deterministic execution.</text>'
            '<text x="58" y="129" text-anchor="start" font-size="18" fill="#5E7F9C">External-state validation supplies the evidence that a task actually succeeded, failed, or should continue.</text>'
        ),
        '<text x="230" y="203" font-size="22" font-weight="700" fill="#17324D">stable goals, constraints, and acceptance conditions</text>': (
            '<text x="400" y="188" font-size="17" font-weight="700" fill="#17324D">stable goals, constraints,</text>'
            '<text x="400" y="214" font-size="17" font-weight="700" fill="#17324D">and acceptance conditions</text>'
        ),
        '<text x="235" y="306" font-size="22" font-weight="700" fill="#765800">adaptive layer: model selects the next step from observations</text>': (
            '<text x="600" y="292" font-size="22" font-weight="700" fill="#765800">adaptive layer</text>'
            '<text x="600" y="319" font-size="17" fill="#765800">model selects the next step from observations</text>'
        ),
        '<text x="650" y="306" font-size="17" fill="#765800">exploration, explanation, planning, candidate generation</text>': '<text x="600" y="344" font-size="17" fill="#765800">exploration, explanation, planning, candidate generation</text>',
        '<text x="235" y="438" font-size="22" font-weight="700" fill="#17324D">assurance layer: deterministic programs execute stable paths</text>': (
            '<text x="600" y="424" font-size="22" font-weight="700" fill="#17324D">assurance layer</text>'
            '<text x="600" y="451" font-size="17" fill="#17324D">deterministic programs execute stable paths</text>'
        ),
        '<text x="650" y="438" font-size="17" fill="#0F4D92">queries, calculations, writes, verified scripts</text>': '<text x="600" y="476" font-size="17" fill="#0F4D92">queries, calculations, writes, verified scripts</text>',
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    return source


def relayout_skill_contents_english(source: str) -> str:
    replacements = {
        ('195', '#17324D', 'goals and stopping conditions', 'when this task is complete or must stop'): ('181', '207'),
        ('290', '#765800', 'tools and necessary constraints', 'available capabilities, data boundaries, risk conditions'): ('276', '302'),
        ('385', '#17324D', 'verified steps and resources', 'scripts, templates, references, known-good practices'): ('371', '397'),
        ('480', '#B64342', 'acceptance, recovery, escalation', 'how to confirm, and how to handle failure'): ('466', '492'),
    }
    for (old_y, color, heading, detail), (heading_y, detail_y) in replacements.items():
        source = source.replace(
            f'<text x="455" y="{old_y}" font-size="21" font-weight="700" fill="{color}">{heading}</text>',
            f'<text x="455" y="{heading_y}" font-size="21" font-weight="700" fill="{color}">{heading}</text>',
        ).replace(
            f'<text x="790" y="{old_y}" font-size="17" fill="{color}">{detail}</text>',
            f'<text x="455" y="{detail_y}" font-size="17" fill="{color}">{detail}</text>',
        )
    for old in (
        '<text x="790" y="385" font-size="17" fill="#0F4D92">scripts, templates, references, known-good practices</text>',
        '<text x="455" y="397" font-size="17" fill="#0F4D92">scripts, templates, references, known-good practices</text>',
    ):
        source = source.replace(
            old,
            '<text x="455" y="386" font-size="17" fill="#0F4D92">scripts, templates, references,</text>'
            '<text x="455" y="406" font-size="17" fill="#0F4D92">known-good practices</text>',
        )
    return source


def relayout_kv_prefix_reuse_english(source: str) -> str:
    replacements = {
        '<rect x="90" y="250" width="150" height="100"': '<rect x="90" y="250" width="150" height="120"',
        '<rect x="260" y="250" width="130" height="100"': '<rect x="260" y="250" width="130" height="120"',
        '<rect x="410" y="250" width="130" height="100"': '<rect x="410" y="250" width="130" height="120"',
        '<rect x="980" y="250" width="130" height="100"': '<rect x="980" y="250" width="130" height="120"',
        '<text x="165" y="290" font-size="19" font-weight="700" fill="#17324D">processed tokens</text>': (
            '<text x="165" y="282" font-size="19" font-weight="700" fill="#17324D">processed</text>'
            '<text x="165" y="305" font-size="19" font-weight="700" fill="#17324D">tokens</text>'
        ),
        '<text x="165" y="320" font-size="16" fill="#0F4D92">this turn’s prefix</text>': '<text x="165" y="339" font-size="16" fill="#0F4D92">this turn’s prefix</text>',
        '<text x="325" y="320" font-size="16" fill="#765800">kept in memory</text>': '<text x="325" y="339" font-size="16" fill="#765800">kept in memory</text>',
        '<text x="475" y="290" font-size="19" font-weight="700" fill="#17324D">next attention step</text>': (
            '<text x="475" y="282" font-size="19" font-weight="700" fill="#17324D">next attention</text>'
            '<text x="475" y="305" font-size="19" font-weight="700" fill="#17324D">step</text>'
        ),
        '<text x="475" y="320" font-size="16" fill="#0F4D92">reads existing K/V</text>': (
            '<text x="475" y="331" font-size="16" fill="#0F4D92">reads existing</text>'
            '<text x="475" y="352" font-size="16" fill="#0F4D92">K/V</text>'
        ),
        '<text x="1045" y="320" font-size="16" fill="#0F4D92">compute new suffix only</text>': (
            '<text x="1045" y="315" font-size="16" fill="#0F4D92">compute new</text>'
            '<text x="1045" y="339" font-size="16" fill="#0F4D92">suffix only</text>'
        ),
        '<text x="885" y="415" text-anchor="middle" font-size="17" fill="#765800">Similar text does not guarantee a hit; authority boundaries cannot be shared.</text>': (
            '<text x="885" y="405" text-anchor="middle" font-size="17" fill="#765800">Similar text does not guarantee a hit.</text>'
            '<text x="885" y="430" text-anchor="middle" font-size="17" fill="#765800">Authority boundaries cannot be shared.</text>'
        ),
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    return source


def relayout_deep_scale_drift_english(source: str) -> str:
    return (
        source
        .replace('<rect x="316" y="410" width="488" height="72" rx="23"', '<rect x="270" y="410" width="580" height="72" rx="23"')
        .replace('<path d="M320 414H800"', '<path d="M274 414H846"')
    )


def relayout_system_flow_english(source: str) -> str:
    source = source.replace('<rect x="55" y="235" width="200" height="74" rx="15"', '<rect x="55" y="235" width="200" height="100" rx="15"')
    replacements = {
        '<text x="155" y="266" font-weight="700">trained parameters</text>': '<text x="155" y="260" font-weight="700">trained parameters</text>',
        '<text x="155" y="291">patterns learned over time</text>': (
            '<text x="155" y="285">patterns learned</text>'
            '<text x="155" y="310">over time</text>'
        ),
    }
    for old, new in replacements.items():
        source = source.replace(old, new)
    return source


def relayout_agent_feedback_loop_english(source: str) -> str:
    replacements = {
        '<text x="140" y="226" font-size="22" font-weight="700" fill="#17324D">task + explicit state</text>': '<text x="140" y="214" font-size="20" font-weight="700" fill="#17324D">task + explicit</text><text x="140" y="238" font-size="20" font-weight="700" fill="#17324D">state</text>',
        '<text x="635" y="226" font-size="22" font-weight="700" fill="#17324D">model proposes next step</text>': '<text x="635" y="214" font-size="20" font-weight="700" fill="#17324D">model proposes</text><text x="635" y="238" font-size="20" font-weight="700" fill="#17324D">next step</text>',
    }
    for old, new in replacements.items(): source = source.replace(old, new)
    return source


def relayout_structured_output_validation_english(source: str) -> str:
    return (source
        .replace('<text x="385" y="242" font-size="22" font-weight="700" fill="#765800">grammar / schema state</text>', '<text x="385" y="230" font-size="20" font-weight="700" fill="#765800">grammar / schema</text><text x="385" y="254" font-size="20" font-weight="700" fill="#765800">state</text>')
        .replace('<text x="882" y="242" font-size="22" font-weight="700" fill="#17324D">parseable proposal</text>', '<text x="882" y="242" font-size="20" font-weight="700" fill="#17324D">parseable proposal</text>')
        .replace('<text x="1090" y="208" text-anchor="middle" font-size="18" font-weight="700" fill="#765800">execution checks</text>', '<text x="1090" y="208" text-anchor="middle" font-size="16" font-weight="700" fill="#765800">execution checks</text>'))


def relayout_validation_boundaries_english(source: str) -> str:
    for y, color, detail in [(184,'#765800','parseable? complete fields? correct types?'),(279,'#0F4D92','are order, amount, object, and state sensible?'),(374,'#B64342','is this actor allowed? approval or extra conditions?'),(469,'#0F4D92','did the downstream action succeed? was goal state reached?')]:
        source = source.replace(f'<text x="650" y="{y}" font-size="18" fill="{color}">{detail}</text>', f'<text x="410" y="{y + 24}" font-size="17" fill="{color}">{detail}</text>')
    return source


def relayout_config_weights_engine_english(source: str) -> str:
    return source.replace(
        '<text x="914" y="255" class="b" fill="#8F3635">architecture adapter: builds</text><text x="914" y="287" class="b" fill="#8F3635">general runtime: schedules and runs</text>',
        '<text x="914" y="247" class="b" fill="#8F3635">architecture adapter builds</text><text x="914" y="273" class="b" fill="#8F3635">general runtime schedules</text><text x="914" y="299" class="b" fill="#8F3635">and runs</text>',
    )


def relayout_mcp_basic_shape_english(source: str) -> str:
    return (source
        .replace('<text x="65" y="103" class="b" fill="#416985">The protocol defines a communication and exposure boundary; a server still governs the permissions, semantics, and execution of connected systems.</text>', '<text x="65" y="103" class="b" fill="#416985">The protocol defines a communication and exposure boundary; a server still governs permissions and semantics.</text><text x="65" y="127" class="b" fill="#416985">Execution of connected systems remains a separate responsibility.</text>')
        .replace('<text x="877" y="237" class="h" fill="#8F3635">External systems</text>', '<text x="877" y="225" class="h" fill="#8F3635">External</text><text x="877" y="252" class="h" fill="#8F3635">systems</text>')
        .replace('<rect x="65" y="485" width="970" height="46" rx="13"', '<rect x="65" y="475" width="970" height="70" rx="13"')
        .replace('<text x="94" y="515" font-size="18" fill="#FFFFFF">MCP answers how to connect and expose; reliability, security, and business semantics of the exposed capability still need modeling.</text>', '<text x="94" y="504" font-size="18" fill="#FFFFFF">MCP answers how to connect and expose.</text><text x="94" y="530" font-size="18" fill="#FFFFFF">Reliability, security, and business semantics still need modeling.</text>'))


def relayout_mhs_integration_pain_english(source: str) -> str:
    return (source
        .replace('<rect x="65" y="510" width="1070" height="49" rx="14"', '<rect x="65" y="500" width="1070" height="70" rx="14"')
        .replace('<text x="94" y="542" font-size="18" fill="#FFFFFF">The goal is not one universal function name, but reusable capability semantics that make cross-device workflows reliable and governable.</text>', '<text x="94" y="530" font-size="18" fill="#FFFFFF">The goal is reusable capability semantics for reliable,</text><text x="94" y="555" font-size="18" fill="#FFFFFF">governable cross-device workflows—not one universal function name.</text>'))


def relayout_cross_modal_training_signals_english(source: str) -> str:
    return (source
        .replace('<text x="750" y="221" class="b">given some modalities, predict text or another modality</text>', '<text x="750" y="215" class="b">given modalities, predict text</text><text x="750" y="239" class="b">or another modality</text>')
        .replace('<text x="750" y="251" class="s">learn to use input evidence to produce a target</text>', '<text x="750" y="267" class="s">learn to use input evidence to produce a target</text>')
        .replace('<rect x="68" y="563" width="1064" height="48" rx="14"', '<rect x="68" y="552" width="1064" height="70" rx="14"')
        .replace('<text x="94" y="594" font-size="17" fill="#8F3635">Paired material does not automatically teach a specific Q&amp;A task; targets and evaluation must cover the cross-modal relation you need.</text>', '<text x="94" y="580" font-size="17" fill="#8F3635">Paired material alone does not teach a specific Q&amp;A task.</text><text x="94" y="606" font-size="17" fill="#8F3635">Targets and evaluation must cover the cross-modal relation you need.</text>'))


def relayout_parameter_update_cycle_english(source: str) -> str:
    return source.replace('<text x="400" y="264" font-size="16" fill="#0F4D92">θ participates in computation</text><text x="400" y="290" font-size="16" fill="#0F4D92">to produce vocabulary probabilities</text>', '<text x="400" y="254" font-size="16" fill="#0F4D92">θ participates</text><text x="400" y="277" font-size="16" fill="#0F4D92">in computation</text><text x="400" y="300" font-size="16" fill="#0F4D92">produce vocabulary</text><text x="400" y="323" font-size="16" fill="#0F4D92">probabilities</text>')


def relayout_multimodal_overview_english(source: str) -> str:
    return (source.replace('<text x="58" y="105" font-size="18" fill="#5E7F9C">Each modality first becomes a representation the model can consume; accepting input does not imply generating that modality or fully understanding reality.</text>', '<text x="58" y="105" font-size="18" fill="#5E7F9C">Each modality becomes a representation the model can consume; accepting input</text><text x="58" y="129" font-size="18" fill="#5E7F9C">does not imply generating that modality or fully understanding reality.</text>')
        .replace('<path d="M870 330H930"', '<path d="M870 330H905"')
        .replace('<text x="427" y="305" font-size="19" fill="#765800">vision encoder + projection</text>', '<text x="427" y="285" font-size="17" fill="#765800">vision encoder</text><text x="427" y="322" font-size="17" fill="#765800">+ projection</text>')
        .replace('<text x="427" y="400" font-size="19" fill="#765800">audio encoder + projection</text>', '<text x="427" y="380" font-size="17" fill="#765800">audio encoder</text><text x="427" y="417" font-size="17" fill="#765800">+ projection</text>')
        .replace('<text x="427" y="495" font-size="19" fill="#765800">video encoder + projection</text>', '<text x="427" y="475" font-size="17" fill="#765800">video encoder</text><text x="427" y="512" font-size="17" fill="#765800">+ projection</text>')
        .replace('<text x="735" y="347" font-size="18" fill="#0F4D92">interleaved multimodal</text><text x="735" y="376" font-size="18" fill="#0F4D92">representations affect each other</text>', '<text x="735" y="342" font-size="17" fill="#0F4D92">interleaved representations</text><text x="735" y="370" font-size="17" fill="#0F4D92">share one context</text>')
        .replace('<rect x="935" y="190" width="190" height="74"', '<rect x="910" y="190" width="230" height="74"').replace('<rect x="935" y="290" width="190" height="74"', '<rect x="910" y="290" width="230" height="74"').replace('<rect x="935" y="390" width="190" height="74"', '<rect x="910" y="390" width="230" height="74"')
        .replace('<text x="1030" y="236" font-size="20" font-weight="700" fill="#B64342">text tokens → text</text>', '<text x="1025" y="236" font-size="20" font-weight="700" fill="#B64342">text tokens → text</text>')
        .replace('<text x="1030" y="336" font-size="20" font-weight="700" fill="#B64342">audio tokens / decoder → sound</text>', '<text x="1025" y="326" font-size="18" font-weight="700" fill="#B64342">audio tokens / decoder</text><text x="1025" y="350" font-size="18" font-weight="700" fill="#B64342">→ sound</text>')
        .replace('<text x="1030" y="436" font-size="20" font-weight="700" fill="#B64342">image / video representation + decoder</text>', '<text x="1025" y="426" font-size="18" font-weight="700" fill="#B64342">image / video representation</text><text x="1025" y="450" font-size="18" font-weight="700" fill="#B64342">+ decoder</text>')
        .replace('<rect x="910" y="390" width="230" height="74" rx="18" stroke="#B64342"', '<rect x="910" y="380" width="230" height="100" rx="18" stroke="#B64342"')
        .replace('<text x="1025" y="426" font-size="18" font-weight="700" fill="#B64342">image / video representation</text><text x="1025" y="450" font-size="18" font-weight="700" fill="#B64342">+ decoder</text>', '<text x="1025" y="414" font-size="17" font-weight="700" fill="#B64342">image / video</text><text x="1025" y="438" font-size="17" font-weight="700" fill="#B64342">representation</text><text x="1025" y="462" font-size="17" font-weight="700" fill="#B64342">+ decoder</text>'))


def relayout_data_control_plane_english(source: str) -> str:
    return source.replace(
        '<text x="58" y="68" font-size="31" font-weight="700" fill="#17324D">Data plane executes requests; control plane maintains long-lived service promises</text>',
        '<text x="58" y="62" font-size="29" font-weight="700" fill="#17324D">Data plane executes requests; control plane maintains</text><text x="58" y="94" font-size="29" font-weight="700" fill="#17324D">long-lived service promises</text>',
    ).replace(
        '<text x="910" y="195" font-size="18" fill="#765800">release, observation, governance</text>',
        '<text x="910" y="183" font-size="16" fill="#765800">release and observation</text><text x="910" y="207" font-size="16" fill="#765800">governance</text>',
    ).replace(
        '<text x="58" y="105" font-size="18" fill="#5E7F9C">The responsibilities may run in one process or separate systems; their boundary is the decision type and time horizon they serve.</text>',
        '<text x="58" y="126" font-size="18" fill="#5E7F9C">The responsibilities may run in one process or separate systems; their boundary is the decision type and time horizon they serve.</text>',
    )


def relayout_progressive_rollout_english(source: str) -> str:
    return (source
        .replace('<text x="865" y="300" font-size="16" fill="#0F4D92">within an observation window</text>', '<text x="865" y="292" font-size="16" fill="#0F4D92">within an observation</text><text x="865" y="316" font-size="16" fill="#0F4D92">window</text>')
        .replace('<rect x="310" y="450" width="580" height="78" rx="20" fill="#F6CFCB" stroke="#B64342" stroke-width="3"/>', '<rect x="310" y="443" width="580" height="99" rx="20" fill="#F6CFCB" stroke="#B64342" stroke-width="3"/>')
        .replace('<text x="600" y="512" text-anchor="middle" font-size="17" fill="#B64342">Quality, error rate, TTFT, cost, policy, or safety metrics trigger predefined stopping conditions.</text>', '<text x="600" y="501" text-anchor="middle" font-size="17" fill="#B64342">Quality, error rate, TTFT, cost, policy, or safety metrics</text><text x="600" y="525" text-anchor="middle" font-size="17" fill="#B64342">trigger predefined stopping conditions.</text>')
        .replace('<text x="600" y="505" text-anchor="middle" font-size="17" fill="#B64342">Quality, error rate, TTFT, cost, policy, or safety metrics</text><text x="600" y="528" text-anchor="middle" font-size="17" fill="#B64342">trigger predefined stopping conditions.</text>', '<text x="600" y="501" text-anchor="middle" font-size="17" fill="#B64342">Quality, error rate, TTFT, cost, policy, or safety metrics</text><text x="600" y="525" text-anchor="middle" font-size="17" fill="#B64342">trigger predefined stopping conditions.</text>'))


def relayout_multimodal_overview_chinese(source: str) -> str:
    return (source
        .replace('<path d="M870 330H930"', '<path d="M870 330H890"')
        .replace('<rect x="935" y="190" width="190" height="74" rx="18" stroke="#B64342"', '<rect x="895" y="190" width="245" height="74" rx="18" stroke="#B64342"')
        .replace('<rect x="935" y="290" width="190" height="74" rx="18" stroke="#B64342"', '<rect x="895" y="290" width="245" height="74" rx="18" stroke="#B64342"')
        .replace('<rect x="935" y="390" width="190" height="74" rx="18" stroke="#B64342"', '<rect x="895" y="390" width="245" height="74" rx="18" stroke="#B64342"')
        .replace('<text x="1030" y="236" font-size="20" font-weight="700" fill="#B64342">文本 token → 文字</text>', '<text x="1018" y="236" font-size="19" font-weight="700" fill="#B64342">文本 token → 文字</text>')
        .replace('<text x="1030" y="336" font-size="20" font-weight="700" fill="#B64342">音频 token／解码器 → 声音</text>', '<text x="1018" y="326" font-size="18" font-weight="700" fill="#B64342">音频 token／</text><text x="1018" y="350" font-size="18" font-weight="700" fill="#B64342">解码器 → 声音</text>')
        .replace('<text x="1030" y="436" font-size="20" font-weight="700" fill="#B64342">图像／视频表示 + 解码器</text>', '<text x="1018" y="426" font-size="18" font-weight="700" fill="#B64342">图像／视频表示</text><text x="1018" y="450" font-size="18" font-weight="700" fill="#B64342">+ 解码器</text>'))


def relayout_domain_examples_chinese(source: str) -> str:
    return source.replace(
        '<text x="837" y="389" class="s" fill="#8D625A">HomeKit / 米家 / Google Home / Home Assistant</text>',
        '<text x="837" y="382" class="s" fill="#8D625A">HomeKit / 米家 / Google Home</text><text x="837" y="410" class="s" fill="#8D625A">Home Assistant</text>',
    )


def relayout_scaled_dot_product_chinese(source: str) -> str:
    """Keep the mathematical subscript visually correct in CI PDF exports."""
    return source.replace(
        "ₖ",
        '<tspan baseline-shift="sub" font-size="70%">k</tspan>',
    )


def update_file(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    relative = path.as_posix()
    if relative.endswith("zh/diagrams/multimodal-models/multimodal-overview.svg"):
        revised = relayout_multimodal_overview_chinese(source)
    elif relative.endswith("zh/diagrams/softmax-gradient-scaling/scale-to-gradient-chain.svg"):
        revised = relayout_scaled_dot_product_chinese(source)
    elif relative.endswith("zh/posts/20260831-mhs-mcp-domain-capability-protocol/domain-examples.svg"):
        revised = relayout_domain_examples_chinese(source)
    elif path.name == "softmax-distribution.svg":
        revised = relayout_softmax_english(source)
    elif path.name == "prefill-decode-state.svg":
        revised = relayout_prefill_decode_english(source)
    elif path.name == "tanh-curve.svg":
        revised = relayout_tanh_english(source)
    elif path.name == "xor-relu-network.svg":
        revised = relayout_xor_network_english(source)
    elif path.name == "ai-feedback-boundary.svg":
        revised = relayout_feedback_boundary_english(source)
    elif path.name == "product-to-model-stack.svg":
        revised = relayout_product_stack_english(source)
    elif path.name == "stable-path-layers.svg":
        revised = relayout_stable_path_layers_english(source)
    elif path.name == "skill-contents.svg":
        revised = relayout_skill_contents_english(source)
    elif path.name == "kv-prefix-reuse.svg":
        revised = relayout_kv_prefix_reuse_english(source)
    elif path.name == "deep-scale-drift.svg":
        revised = relayout_deep_scale_drift_english(source)
    elif path.name == "system-flow.svg":
        revised = relayout_system_flow_english(source)
    elif path.name == "agent-feedback-loop.svg":
        revised = relayout_agent_feedback_loop_english(source)
    elif path.name == "structured-output-validation.svg":
        revised = relayout_structured_output_validation_english(source)
    elif path.name == "validation-boundaries.svg":
        revised = relayout_validation_boundaries_english(source)
    elif path.name == "config-weights-engine.svg":
        revised = relayout_config_weights_engine_english(source)
    elif path.name == "mcp-basic-shape.svg":
        revised = relayout_mcp_basic_shape_english(source)
    elif path.name == "mhs-integration-pain.svg":
        revised = relayout_mhs_integration_pain_english(source)
    elif path.name == "cross-modal-training-signals.svg":
        revised = relayout_cross_modal_training_signals_english(source)
    elif path.name == "parameter-update-cycle.svg":
        revised = relayout_parameter_update_cycle_english(source)
    elif path.name == "multimodal-overview.svg":
        revised = relayout_multimodal_overview_english(source)
    elif path.name == "data-control-plane.svg":
        revised = relayout_data_control_plane_english(source)
    elif path.name == "progressive-rollout.svg":
        revised = relayout_progressive_rollout_english(source)
    else:
        revised = relayout_system_map_english(source)
    if revised == source:
        return False
    path.write_text(revised, encoding="utf-8")
    return True


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=root)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    targets = [
        root / "book/assets/en/diagrams/activation-functions/softmax-distribution.svg",
        root / "book/assets/en/diagrams/activation-functions/tanh-curve.svg",
        root / "book/assets/en/diagrams/activation-functions/xor-relu-network.svg",
        root / "book/assets/en/diagrams/appendices/ai-feedback-boundary.svg",
        root / "book/assets/en/diagrams/function-calling-tool-use/product-to-model-stack.svg",
        root / "book/assets/en/diagrams/harness-runtime-skills/stable-path-layers.svg",
        root / "book/assets/en/diagrams/harness-runtime-skills/skill-contents.svg",
        root / "book/assets/en/diagrams/inference-performance-capacity/kv-prefix-reuse.svg",
        root / "book/assets/en/diagrams/layer-norm/deep-scale-drift.svg",
        root / "book/assets/en/diagrams/introduction/system-flow.svg",
        root / "book/assets/en/diagrams/llm-external-interaction/agent-feedback-loop.svg",
        root / "book/assets/en/diagrams/llm-external-interaction/structured-output-validation.svg",
        root / "book/assets/en/diagrams/llm-external-interaction/validation-boundaries.svg",
        root / "book/assets/en/diagrams/llm-infrastructure/config-weights-engine.svg",
        root / "book/assets/en/diagrams/mhs-mcp-domain-capability-protocol/mcp-basic-shape.svg",
        root / "book/assets/en/diagrams/mhs-mcp-domain-capability-protocol/mhs-integration-pain.svg",
        root / "book/assets/en/diagrams/multimodal-models/cross-modal-training-signals.svg",
        root / "book/assets/en/diagrams/model-training-lifecycle/parameter-update-cycle.svg",
        root / "book/assets/en/diagrams/multimodal-models/multimodal-overview.svg",
        root / "book/assets/en/diagrams/serving-control-plane/data-control-plane.svg",
        root / "book/assets/en/diagrams/serving-control-plane/progressive-rollout.svg",
        root / "book/assets/en/diagrams/llm-infrastructure/prefill-decode-state.svg",
        root / "book/assets/book-system-map-en.svg",
        root / "book/assets/zh/diagrams/multimodal-models/multimodal-overview.svg",
        root / "book/assets/zh/diagrams/softmax-gradient-scaling/scale-to-gradient-chain.svg",
        root / "book/assets/zh/posts/20260831-mhs-mcp-domain-capability-protocol/domain-examples.svg",
    ]
    if not args.write:
        print("\n".join(path.relative_to(root).as_posix() for path in targets))
        return 0
    print(f"Updated {sum(update_file(path) for path in targets)} reviewed figure layouts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
