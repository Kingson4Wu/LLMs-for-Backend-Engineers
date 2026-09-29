# Publication Figure Style Contract

This contract adapts the structural principles in figures4papers to the book's
accessible SVG workflow. It is a visual system, not a source of copied assets.

## Palette and type

| Role | Value |
| --- | --- |
| Primary structure | `#0F4D92` |
| Secondary structure | `#3775BA` |
| Positive state | `#DDF3DE`, `#AADCA9`, `#8BCF8B` |
| Contrast or risk | `#F6CFCB`, `#E9A6A1`, `#B64342` |
| Neutral scaffold | `#CFCECE` |
| Emphasis | `#FFD700` |
| Ink | `#17324D` |
| Canvas | `#FFFFFF` |

Use Arial or Helvetica at 30--32px for an in-figure title, 20--23px for
labels, and 14--18px only for short supporting notes. Use colour to reinforce
meaning, never as its only encoding.

## Layout contract

- Prefer a wide 900px SVG canvas with a calm white background and 32px or more
  of exterior whitespace.
- Give every text block an explicit invisible rectangle with
  `data-figure-safe-zone="text"`; it includes the block's intended breathing
  room, not only its glyph bounds.
- Mark every routed connector with `data-figure-connector="true"`. Use simple
  line, polyline, or straight SVG path segments so the audit can inspect it.
- Route connectors through dedicated gutters. A connector must never cross a
  text safe zone; enter labelled cards via their edge rather than their label.
- Keep labels out of arrowheads, plotting axes, card borders, legends, and
  one another. Directly label chart series when that removes an ambiguous
  legend.

## Bilingual and delivery contract

- Chinese and English counterparts retain the same information architecture,
  palette roles, geometry, and directional meaning; only language-dependent
  text width and line breaks may differ.
- SVGs remain self-contained and include `role="img"`, a concise `<title>`,
  and a substantive `<desc>`.
- Validate source structure, the connector-safe-zone audit, raster rendering at
  desktop and 390px width, and the source-pair manifest before publishing.
