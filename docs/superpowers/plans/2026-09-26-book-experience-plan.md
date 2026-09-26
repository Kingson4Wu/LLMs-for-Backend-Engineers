# Book Experience Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Improve first-contact orientation through a concise README, a semantic four-part homepage animation, and reusable book-wide visual guidance.

**Architecture:** Keep the homepage map as server-rendered content and place a native SVG enhancement inside its own component. Store the overview diagram as a local SVG asset so it can be embedded in Markdown and published with the book. Keep explanatory prose in the existing part landings and reading guide.

**Tech Stack:** Astro, TypeScript, native SVG, Markdown, existing Python and Node publication checks.

---

### Task 1: Add a static, reusable book overview diagram

**Files:**
- Create: `book/assets/book-system-map.svg`
- Modify: `book/index.md`
- Modify: `book/parts/math-foundations.md`
- Modify: `book/parts/llm-internal.md`
- Modify: `book/parts/llm-external.md`
- Modify: `book/parts/ai-infrastructure.md`

- [x] Create an accessible SVG that shows four labelled stages and the dependency path between them.
- [x] Place it in the reading guide and link each part landing to its stage and reading purpose without repeating the figure.
- [x] Run `python3 tools/book-kit/validate_book.py --check-links`.

### Task 2: Add a progressive homepage map animation

**Files:**
- Create: `web/src/components/KnowledgeMap.astro`
- Modify: `web/src/components/Home.astro`
- Modify: `web/src/styles/site.css`
- Test: `web/test/home.test.mjs`

- [x] Render the existing four cards through the component and add an SVG path overlay whose labels remain HTML text.
- [x] Use one button to pause or resume motion, retain a useful still state for reduced motion, and stop animation when the map is off screen or the tab is hidden.
- [x] Add a regression test that asserts the four part links and pause control are present.
- [x] Run `npm --prefix web test`, `npm --prefix web run check`, and both deployment-base builds.

### Task 3: Reorganize repository orientation and record figure rules

**Files:**
- Modify: `README.md`
- Modify: `README.zh-CN.md`
- Create: `BOOK_FIGURE_GUIDELINES.md`

- [x] Keep the primary reading and download links at the top; add scope, routes, source map, and dialogue-learning orientation.
- [x] Mirror the information architecture in natural English and Chinese without claiming human translation review.
- [x] Add concise figure rules that apply the book content principles to diagrams.
- [x] Run book link validation and inspect rendered README links.

### Task 4: Deliver and inspect

**Files:**
- Modify: implementation files from Tasks 1–3 only as needed by checks.

- [x] Run the repository's required validation suite.
- [x] Inspect desktop, 390px mobile, light/dark, and reduced-motion homepage states.
- [x] Commit one focused change, push `main`, and verify CI and Pages deployment before reporting completion.
