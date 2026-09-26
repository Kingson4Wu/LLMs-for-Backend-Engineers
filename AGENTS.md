# Repository Guidelines

## Source of truth

This book uses an Astro reading website and independent Pandoc publication tools. Preserve the four-part structure and descriptive source filenames.

- `book/book.json`: Chinese book metadata; `book/catalog.json`: ordered frontmatter and grouped articles.
- `book/editions.json`: available languages and source directories.
- `book/chapters/`: Chinese source, divided into mathematics and machine-learning foundations, LLM internals, external systems, and LLM infrastructure.
- `book/parts/`: four website-only part landing pages; each is reached by its part title and is not a numbered core chapter.
- `book/translations/en/`: English mirror, localized catalog/metadata, glossary and source hashes.
- `book/SUMMARY.md`: generated legacy navigation; update via `validate_book.py --write-summary`.
- `web/`: Astro homepage, reader, search, typography and local reading data.
- `tools/book-kit/`: validation and standalone print HTML/PDF/EPUB generation.
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

Run the block from the repository root after installing publication prerequisites: the Python tests require Pandoc and librsvg and regenerate Chinese HTML/EPUB outputs. Check `SITE_BASE=/` as well as the default `/LLMs-for-Backend-Engineers/` when touching routing. Search requires a full build and preview. Node 22.12+ (CI 24), npm 9.6.5+, Python 3.11+. Publication prerequisites and legacy Honkit commands are in `LOCAL_DEVELOPMENT.md`.

## Content and design

- Before drafting or revising book prose, follow [BOOK_CONTENT_GUIDELINES.md](BOOK_CONTENT_GUIDELINES.md). It defines the book's required global framing, clear causal explanations, and selective mechanism-level depth.
- No duplicate article IDs or duplicated publication entries; groups are not chapters.
- Do not silently substitute Chinese for a missing requested language.
- English source hashes track change, not translation quality; preserve AI-assisted review disclosure.
- Body max width 900px; centered responsive images; `text-rendering: optimizeLegibility`.
- Validate Chinese/English typography, 390px mobile and desktop, light/dark, formulas, code, tables, keyboard access.
- Local notes are private browser storage with export/import, not a cloud service.

## Delivery

PR validates. On the upstream repository, matching main-branch path changes (or manual dispatch) trigger Pages deployment; v-prefixed numeric tags such as `v1.0.0` trigger versioned PDF/EPUB/HTML releases. Pages includes HTML/EPUB, while PDF is built by the separate release workflow. See the actual workflow filters in `.github/workflows/`. Do not publish partial or mixed-source releases: the three formats within each language must share source provenance. Never label a build or translation as verified without actual checks.

Use concise imperative commit messages focused on a single change. Do not invent a content/code license: the author has not selected one.
