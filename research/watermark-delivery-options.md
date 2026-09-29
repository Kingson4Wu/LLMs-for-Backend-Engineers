# Watermark options for the published book

**Question.** Add a restrained, diagonal watermark to the book's delivered forms without degrading reading, accessibility, or the reflowable nature of the ebook.

**Scope inspected.** The current project produces an Astro reader, standalone print HTML, XeLaTeX/Pandoc PDF, EPUB 3, and a single-file Markdown manuscript. The print HTML and EPUB share `book/styles/publication.css`; the PDF has its own XeLaTeX header built in `tools/book-kit/export_book_pdf.py`; Markdown is plain semantic text.

## What a watermark can and cannot do

A visible watermark is an attribution and provenance cue. It is not copy protection: a reader can remove CSS, crop/rasterize pages, or copy the text. It should therefore say something factual and enduring, such as `UNDERSTANDING LLMS · KINGSON WU`, rather than `CONFIDENTIAL`, a user identity, a timestamp, or an opaque legal claim. Per-recipient forensic watermarking is a different feature: it requires a separately generated, authenticated file for each recipient and a privacy policy; it should not be inferred from a public release.

The aesthetic requirement is best met by a single large, low-contrast wordmark behind the page or reading surface, rotated about `-28deg` to `-32deg`. It must be decorative—not real document text—so it cannot be announced by assistive technology, selected, copied into notes, or intercept a link/tap.

## Format-by-format assessment

| Delivered form | Feasible approach | Reading/accessibility result | Recommendation |
| --- | --- | --- | --- |
| Astro reader | A fixed, `aria-hidden` overlay (or pseudo-element) confined to the reading route, behind controls and with `pointer-events: none`; use CSS `transform: rotate(...)` and a theme-specific low-contrast color. | Does not change the DOM reading order or selection. `pointer-events: none` lets pointer input reach underlying links, but the overlay must have no focusable descendant. | **Yes.** Use a view-only overlay for article pages, not the homepage, navigation, search, dialogs, code, or diagrams. |
| Standalone print HTML | A print/screen CSS pseudo-element or SVG background, with the same noninteractive treatment. It remains visual only when opened in a browser. | Browser print is CSS-driven, but printer settings and background-printing policy can suppress it. It is not a reliable way to create the release PDF. | **Yes, best effort.** Include the mark in the HTML view; do not promise it appears in every browser-generated printout. |
| PDF | Add the watermark in the XeLaTeX header. `draftwatermark` is purpose-built for a textual watermark on every page and exposes text, color, font size/scale, rotation, and placement controls. | The mark is part of the paginated output and does not affect text flow. It must be placed behind body content and excluded from title/cover/blank pages if those need an unmarked presentation. | **Yes, canonical repeated watermark.** This is the only format where “every page” can be enforced reliably. |
| EPUB (reflowable) | A CSS/SVG background is technically allowed, but a fixed or absolutely positioned overlay is not portable across readers. | Reflowable EPUB deliberately allows readers to alter fonts, pagination, themes, and CSS; EPUB Content Documents specifically warn that fixed/absolute positioning is problematic with reader pagination. | **Default: no body-wide diagonal overlay.** Preserve reflow/accessibility; add an unobtrusive ownership/provenance line in frontmatter/colophon and a consistent cover mark instead. A CSS mark can be offered only as explicitly documented best-effort behaviour after reader-matrix testing. |
| Single-file Markdown | There is no presentation layer that can guarantee opacity, rotation, or a background mark across renderers. | Injecting repeated text would pollute copy/paste, search, LLM ingestion, and the source manuscript. HTML/CSS embedded in Markdown would be renderer-specific and violates the goal of a clean portable study artifact. | **No diagonal watermark.** Add one concise provenance line near the title only. |

## Why EPUB is the exception

EPUB 3 is a package of XHTML, CSS, SVG, and other resources, so CSS can be supplied. But its primary value is reflow: reading systems lay out text according to viewport, font size, and user settings. The EPUB specification warns that reading-system pagination can interact poorly with CSS and calls fixed/absolute positioning particularly problematic. It also notes that real readers may not support all desired CSS and may alter author styling. Converting this book to fixed-layout EPUB merely to force a mark would harm text configuration and accessibility; the EPUB specification cautions that fixed-layout systems often restrict user styles and that this has usability and accessibility consequences.

## Visual specification to prototype

Use the book identity rather than a legalistic label:

```text
UNDERSTANDING LLMS · KINGSON WU
```

For Chinese pages, the localized equivalent may be used only if it is visually stable at the chosen font; otherwise retain the short Latin mark consistently. Suggested starting values, to be judged by rendered screenshots rather than treated as fixed requirements:

| Property | Starting point | Guardrail |
| --- | --- | --- |
| Angle | `-30deg` | Keep the direction identical across web, HTML, and PDF. |
| Size | 5–7vw web; 32–40pt PDF | It should read as a quiet field mark, not a heading. |
| Opacity/colour | Approx. 0.035–0.055 on light; a separately tested muted value on dark | Do not simply reuse the light alpha in dark mode; test code blocks, math, tables, and diagrams. |
| Density | One mark per viewport/page, never a tiled pattern | Tiling produces visible interference with formulas and figures. |
| Stacking | Behind prose, above the paper/background; never over controls/figures | No text, line, arrow, formula, or diagram should compete with it. |
| Interaction | `aria-hidden="true"`, no text node in the reading flow, `pointer-events: none`, no focusable content | Selection, screen readers, keyboard navigation, search, and local notes remain unchanged. |

Do not encode opacity alone as the only signal of ownership. The visual mark is supplementary; a short readable provenance/attribution statement in frontmatter is the accessible source of that information.

## Project-specific implementation path

1. **Establish a single watermark configuration** (display text, Chinese display text if used, angle, and light/dark colours) in publication metadata or a small shared configuration module. Do not scatter literal values across output pipelines.
2. **Web reader:** render exactly one decorative overlay inside the reader shell only. Make it a sibling/background layer, `aria-hidden`, with `pointer-events: none`; keep it out of print styles unless deliberately testing browser printing. Add visual tests at 390px and desktop in light/dark, and keyboard/selection checks.
3. **Print HTML:** extend `book/styles/publication.css` with an SVG/data-URI background or pseudo-element. Test it in the supported browser renderer; document that print-dialog “background graphics” settings can remove it.
4. **PDF:** include a small generated LaTeX fragment in the existing `--include-in-header` path. Configure `draftwatermark` with a subdued gray and rotation, and add a CI check that the package is provisioned. Apply it after title pages are emitted or use its page-selection facility so the cover/title/TOC policy is intentional. Render both languages and inspect rasterized sample pages containing Chinese text, dense equations, code, tables, and diagrams.
5. **EPUB and Markdown:** retain the clean reflowable/portable bodies. Put an explicit, single provenance line in their frontmatter/colophon and retain the branded cover. This means every artifact carries attribution, while only formats with dependable page geometry get a repeated diagonal mark.
6. **Release validation:** add artifact checks that verify the PDF watermark text is present and that the HTML has the configured class/asset; use screenshot/PDF-image review for collision detection. Automated string checks alone cannot prove visual quality. Run `epubcheck` unchanged and test at least one mainstream EPUB reader before claiming display consistency.

For the web reader, a persisted “reduce decorative watermark” preference is worth considering. It should be on by default only if the screenshots demonstrate that it is genuinely quiet, and should not affect the underlying content or the downloadable release files. This provides a practical escape hatch for readers using high zoom, high contrast, or visual-assistance tools.

## Primary-source findings

- [Pandoc User’s Guide: header includes](https://pandoc.org/MANUAL.html#extension-yaml_metadata_block) documents format-specific raw header content and `--include-in-header`, matching the existing PDF pipeline's header injection point.
- [Pandoc User’s Guide: standalone HTML title output](https://pandoc.org/MANUAL.html#title-block) confirms standalone HTML is styled through CSS, matching the print-HTML route.
- [MDN: printing and `@page`](https://developer.mozilla.org/en-US/docs/Web/CSS/Guides/Media_queries/Printing) documents `@media print` and `@page` as the browser-print styling mechanisms; it does not make browser printing a stable PDF-generation contract.
- [MDN: `position`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/position) states that fixed-position boxes repeat in the same position on every page in printed documents, which makes a one-element print-HTML watermark feasible in browser engines.
- [MDN: `pointer-events`](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/pointer-events) documents that `pointer-events: none` lets pointer activity target what is underneath; it also notes this alone does not remove keyboard focus, hence the overlay must contain no focusable element.
- [EPUB Content Documents 3.2, CSS conformance and reading-system caveats](https://www.w3.org/2019/epub32/epub-contentdocs.html#sec-css-style-sheets) permits CSS but explicitly identifies fixed and absolute positioning as problematic with reader-induced pagination.
- [EPUB 3.4, fixed-layout accessibility consideration](https://www.w3.org/TR/epub-34/#sec-fixed-layouts) explains that pre-paginated documents can restrict user styling and advises considering the negative usability/accessibility impact.
- [CTAN `draftwatermark` documentation](https://ctan.org/pkg/draftwatermark) and its [package manual](https://mirrors.ctan.org/macros/latex/contrib/draftwatermark/draftwatermark.pdf) describe page-level textual watermarking and its configurable visual parameters; the package uses LaTeX shipout hooks in current releases.
- [LaTeX shipout hooks documentation](https://www.latex-project.org/help/documentation/ltshipout-doc.pdf) describes the `shipout/background` hook, whose contents are placed behind page content; it is an alternative to the package when a custom PDF watermark is needed.

## Decision

Adopt a **subtle repeated visual watermark only for the web reader, standalone print HTML, and canonical PDF**. Give EPUB and Markdown the same clear provenance and branded cover, but deliberately do not force diagonal marks into their reflowable/portable bodies. This is the narrowest implementation that fulfills the desired elegant, low-impact attribution while respecting the formats’ actual constraints.
