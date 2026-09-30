# Repository Guidelines

## Source of truth

This book uses an Astro reading website and independent Pandoc publication tools. Preserve the four-part structure and descriptive source filenames.

- `book/book.json`: Chinese-edition metadata and the shared article ordering reference; `book/catalog.json`: ordered frontmatter and grouped articles.
- `book/editions.json`: available languages and source directories.
- `book/chapters/`: Simplified Chinese edition, divided into mathematics and machine-learning foundations, LLM internals, external systems, and LLM infrastructure.
- `book/parts/`: four website-only part landing pages; each is reached by its part title and is not a numbered core chapter.
- `book/translations/en/`: English counterpart, localized catalog/metadata, glossary and alignment hashes.
- `book/SUMMARY.md`: generated legacy navigation; update via `validate_book.py --write-summary`.
- `web/`: Astro homepage, reader, search, typography and local reading data.
- `tools/book-kit/`: validation and standalone Markdown/print HTML/PDF/EPUB generation.
- `tests/`: publication and delivery regressions.

Do not treat `_book/`, `_build/`, `exported/`, `dist/`, `.astro/`, `release/` or `node_modules/` as source. Keep PDF intermediates out of deployable website output.

## Commands

```bash
python3 -m unittest discover -s tests -v
python3 tools/book-kit/validate_book.py --check-links
python3 tools/book-kit/validate_book.py --locale en --check-links
python3 tools/book-kit/check_translations.py
cd web
npm ci
npm run check
npm test
npm run build
npm run check:deployment
npm run dev
```

Run the block from the repository root after installing publication prerequisites: the Python tests require Pandoc and librsvg and regenerate Chinese HTML/EPUB outputs. Check `SITE_BASE=/` as well as the default `/Understanding-LLMs/` when touching routing. Search requires a full build and preview. Node 22.12+ (CI 24), npm 9.6.5+, Python 3.11+.

## Content and design

- Before drafting or revising book prose, follow [BOOK_CONTENT_GUIDELINES.md](BOOK_CONTENT_GUIDELINES.md). It defines the book's required global framing, clear causal explanations, and selective mechanism-level depth.
- No duplicate article IDs or duplicated publication entries; groups are not chapters.
- Do not silently substitute Chinese for a missing requested language.
- Alignment hashes track synchronized changes, not edition rank or translation quality; keep the two published editions strictly matched.
- Body max width 900px; centered responsive images; `text-rendering: optimizeLegibility`.
- Validate Chinese/English typography, 390px mobile and desktop, light/dark, formulas, code, tables, keyboard access.
- Local notes are private browser storage with export/import, not a cloud service.

## Learning mode

When the user asks to learn rather than edit, read `learning/README.md`, the appropriate `learning/LEARNING_CONTRACT.*.md`, `learning/index.json`, and the relevant source chapter before answering. Cite chapter ID, title, source path, and heading; distinguish book evidence, inference, and facts that require external verification. Learning mode is read-only: do not change `book/`, `web/`, `tools/`, or this file unless the user explicitly asks to edit them. Write learner material only under `learning/workspace/` after explicit request.

## Delivery

PR validates. On the upstream repository, matching main-branch path changes (or manual dispatch) trigger Pages deployment; v-prefixed numeric tags such as `v1.0.0` trigger versioned Markdown/PDF/EPUB/HTML releases. Pages rebuilds and includes all four formats; the release workflow packages the same four formats as versioned assets. See the actual workflow filters in `.github/workflows/`. Do not publish partial or mixed-source releases: the four formats within each language must share source provenance. Never label a build or translation as verified without actual checks.

Use concise imperative commit messages focused on a single change. Do not invent a content/code license: the author has not selected one.
