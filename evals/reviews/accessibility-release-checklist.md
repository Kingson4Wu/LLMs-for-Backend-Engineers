# Release accessibility review checklist

This is a human-review record for a tagged release. It complements automated
route, axe, EPUB, and build checks; it is **not a conformance claim**.

Copy the record below into a private release review, fill it from the actual
published artifact, and retain the completed record with the release evidence.
Do not commit an unperformed review or infer a pass from a CI report.

```text
Release tag and commit:
Reviewer and date:
Artifacts and browsers/readers used:

[ ] Keyboard: reach navigation, language switcher, search, notes, and every
    interactive reader control; focus is visible and Escape closes overlays.
[ ] 200% zoom: English and Chinese home, contents, a formula-heavy chapter,
    a figure-heavy chapter, and downloads have no clipped content or horizontal
    scrolling at desktop width.
[ ] Mobile: the same representative routes work at a 390px viewport.
[ ] Themes: light and dark preserve readable text, formulas, code, figures,
    focus indicators, and controls.
[ ] Screen reader: document language, main heading, part/chapter navigation,
    figure alternative text, table headings, and displayed formulas have a
    meaningful reading order.
[ ] EPUB: the table of contents, language metadata, reading order, images, and
    formulas remain understandable in the reader actually used.

Findings, affected routes/artifacts, and follow-up issue or decision:
```

