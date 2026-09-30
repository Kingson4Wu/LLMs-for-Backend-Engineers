# Deterministic book-quality evaluations

`evals/` contains reviewed, versioned source cases for the book's highest-risk
claims and formulas. It supplements, rather than replaces, expert editorial
review and the repository's existing publication checks.

Run the local gate from the repository root:

```bash
python3 tools/book-kit/validate_evals.py
```

The gate is offline. A source URL records evidence provenance but is never
fetched during CI. Cases must therefore be specific enough for a reviewer to
check against the named source, and must keep their source chapter heading and
anchor text current. Every cited URL must also appear in `provenance.json` with
its evidence type, a human-checkable locator, and a version/retrieval date.

`reviews/source-locks.json` is the bilingual stale-review guard. It contains
one SHA-256 lock for each chapter touched by a case, for both Chinese and
English counterpart files. Any prose change in either edition invalidates the lock;
refreshing a lock is a deliberate editorial review action, not a mechanical
formatting step.

## Claim cases

Claim cases belong in `claims/*.json`. They name a Chinese chapter anchor and
heading, preserve an exact text anchor, record authoritative source URLs, and
state a proposition. Boundary cases also record a tempting false implication
that the chapter must not make. Every case includes a bilingual semantic review
record.

```json
{
  "id": "rag-evidence-not-weights",
  "chapter": "rag-context-evidence",
  "heading": "RAG：检索改变的是当前证据，而非模型参数",
  "anchor_text": "检索通常改变的是当前上下文中可见的证据",
  "kind": "boundary",
  "sources": ["https://arxiv.org/abs/2005.11401"],
  "expectation": "RAG changes current evidence, not trained weights.",
  "must_not_imply": ["RAG guarantees that an answer is true."],
  "review": {
    "reviewed_at": "2026-09-29",
    "reviewer": "Kingson Wu",
    "proposition": true,
    "conditions_and_quantifiers": true,
    "formula_symbols_and_units": true,
    "figure_meaning": true,
    "link_target": true
  }
}
```

## Formula cases

Formula cases belong in `formulas/*.json`. They test a deliberately fixed
evaluator registry rather than dynamically executing expressions from a data
file. Each case records inputs, expected result, tolerance, and its domain.

```json
{
  "id": "softmax-normalizes",
  "chapter": "softmax",
  "heading": "Softmax：把一组分数变成概率分布",
  "anchor_text": "Softmax 的输出非负，且所有分量之和为 1",
  "evaluator": "softmax",
  "inputs": {"logits": [0, 0]},
  "expected": [0.5, 0.5],
  "tolerance": 1e-12,
  "domain": "finite logits",
  "review": {
    "reviewed_at": "2026-09-29",
    "reviewer": "Kingson Wu",
    "proposition": true,
    "conditions_and_quantifiers": true,
    "formula_symbols_and_units": true,
    "figure_meaning": true,
    "link_target": true
  }
}
```

The fixed evaluator registry includes softmax, one-hot cross-entropy, chain
rule products, masked attention, LayerNorm, temperature softmax, and KV-cache
memory arithmetic. It deliberately does not execute expressions supplied by a
case file. Formula cases that correspond to display math also carry a normalized
equation fingerprint; the gate rejects a changed or removed equation before it
checks the independent numerical result.

When a covered section changes, update its anchor and review the aligned
counterpart before changing the lock. Never use a passing evaluation case as
evidence that all surrounding prose has been independently fact-checked.

## Tutoring-contract cases

`tutoring/` is a separate, offline scaffold for human review of AI-assisted
learning sessions. It validates public development-case structure and can bind
a supplied transcript to the SHA-256 of a complete Markdown or PDF artifact;
it never invokes or scores a model. See `tutoring/README.md`. Reviewer-owned
holdouts are intentionally excluded from the repository and CI.

## Advisory monitors

Two repeatable monitors collect evidence without turning transient external
conditions or automated heuristics into a publication gate:

- `tools/book-kit/audit_axe_accessibility.py` runs in every CI build against
  the fixed bilingual reader route matrix. Its `axe-accessibility-route-report`
  artifact preserves violations, incomplete checks, and route failures for
  review. It is deliberately non-blocking: automated checks cannot certify
  WCAG conformance or real assistive-technology usability.
- `tools/book-kit/audit_external_links.py` inventories source links from the
  canonical Chinese and English manuscripts, checks only resolvable public
  HTTP(S) endpoints without inherited proxy settings, and writes an advisory
  report. `.github/workflows/external-link-monitor.yml` runs it every Monday
  and on manual dispatch; retrieve the `external-link-report` artifact from
  that workflow. Reachability is not evidence that a source remains correct
  or current.

To inspect either report locally, write it outside the source tree, for
example:

```bash
python3 tools/book-kit/audit_external_links.py --output /tmp/external-links.json
cd web
PYTHONPATH=../tools/book-kit python3 ../tools/book-kit/audit_axe_accessibility.py \
  --base-url http://127.0.0.1:4322/Understanding-LLMs \
  --site-dir dist --axe-script node_modules/axe-core/axe.min.js \
  --output /tmp/axe-accessibility.json
```
