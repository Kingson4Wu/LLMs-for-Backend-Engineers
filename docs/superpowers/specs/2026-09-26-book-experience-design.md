# Book Experience Design

## Goal

Make the repository and reading homepage explain the book's scope and four-part structure before a reader starts an article, without turning the book into an Agent course or an experiment platform.

## Decisions

- The homepage keeps its existing four clickable knowledge-map cards. A small native SVG overlay traces the dependency path from foundations to service delivery. The static map remains complete when scripts or motion are unavailable.
- The animation is explanatory rather than decorative: it highlights one part at a time and labels the relationship as a learning path. It supports pause, keyboard operation, dark mode, mobile layout, and `prefers-reduced-motion`.
- A single reusable overview illustration appears in the reading guide and the four part landing pages link to the appropriate stage rather than duplicating diagrams in every article.
- The README becomes an orientation page: scope, reading routes, book map, formats, dialogue learning, source layout, contribution, and licence. It does not add badges, sponsors, provider recommendations, experiment setup, or a skills installation workflow.
- A short figure standard records the visual rules used by future diagrams: one question per figure, clear data flow, accessible text alternatives, no image-only prose, and a stable palette.

## Verification

Build the Astro site under both deployment bases, run the existing static and publication checks, then inspect the homepage at desktop and 390px widths in light/dark and reduced-motion modes. The SVG must not rely on animation for meaning.
