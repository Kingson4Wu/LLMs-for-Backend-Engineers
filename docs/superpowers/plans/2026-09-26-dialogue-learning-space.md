# 对话式学习空间 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a model-agnostic, Markdown-only entry point for dialogue-based learning from this book.

**Architecture:** `learning/` contains the reader-facing entry, a map from questions to book sources, and concise dialogue-quality guidance. It has no executable configuration. `README.zh-CN.md` links to it so the repository exposes the entry point without changing the published book catalog.

**Tech Stack:** Markdown, existing repository link validation, Astro static-site build.

---

### Task 1: Add the learning-space documents

**Files:**
- Create: `learning/README.md`
- Create: `learning/BOOK_MAP.md`
- Create: `learning/DIALOGUE_LEARNING.md`

- [x] **Step 1: Write the entry document**

Describe both question-driven and path-driven learning, and make clear that no Skill, MCP, script or vendor-specific configuration is required.

- [x] **Step 2: Write the book map**

Map the four book parts, their source chapters, core dependencies and common engineering questions without duplicating chapter prose.

- [x] **Step 3: Write the dialogue guidance**

Require global framing, mechanism and boundary explanations, source paths for claims about the book, and explicit distinction between book content, inference and current external facts.

- [x] **Step 4: Verify local links**

Run: `python3 tools/book-kit/validate_book.py --check-links`

Expected: `Valid zh-Hans: 35 chapters, 2 frontmatter entries`.

### Task 2: Expose and verify the entry point

**Files:**
- Modify: `README.zh-CN.md`

- [x] **Step 1: Add a concise repository entry link**

Link the Chinese README's start section to `learning/README.md` without presenting it as a website feature.

- [x] **Step 2: Verify publication and site integrity**

Run:

```bash
python3 tools/book-kit/validate_book.py --check-links
python3 tools/book-kit/validate_book.py --locale en --check-links
python3 tools/book-kit/check_translations.py
npm --prefix web run check
npm --prefix web test
npm --prefix web run build
npm --prefix web run check:deployment
```

Expected: all commands exit successfully; Astro may retain its existing type hints but reports no errors.

- [ ] **Step 3: Commit the documentation change**

```bash
git add learning README.zh-CN.md docs/superpowers
git commit -m "docs: add dialogue learning space"
```
