# RAG and Context Engineering: How Evidence Enters a Model

Model parameters come from past training, while the policy, inventory, document revision, and user authority needed for one answer belong to the present external world. RAG and context engineering bridge that gap. They do not put every document into a prompt. They select a small set of trustworthy, relevant, and authorized evidence for the task at hand. They operate before decoding and determine what the model can see in this turn.

This is more than “adding a knowledge base.” Wrong, stale, decontextualized, or unauthorized material can still produce a fluent answer; even good material does not prove that a conclusion follows from it. RAG improves access to evidence and makes verification possible. It does not turn a generative model into a database or a proof system.

## RAG Supplies Current Facts, Not Missing Parameters

Training compresses much material into parameter patterns useful for predicting later tokens, but parameters are not records queryable by time, source, revision, or authority. When a policy changes, an order is cancelled, or a document is limited to one tenant, the application must read external facts at request time.

```text
trained parameters: language regularities, common associations, task patterns
external material: current revision, source, authority, business state
                                  │
                                  ▼
question → retrieval or query → selected evidence → current context → generation
```

RAG input need not be a document. It may be a manual passage, database record, ticket state, search result, knowledge-graph relation, or a value read live by a tool. The common property is that selected external information enters the context for this inference.

## From Material to Context: Each Stage Narrows Candidates

A dependable RAG system is not “a vector database plus an LLM.” It makes a series of choices:

```text
sources
  → clean, version, chunk, and annotate
  → build an index or query path
  → retrieve candidates for the question
  → filter by authority, time, and business conditions
  → rerank, deduplicate, preserve needed context
  → assemble evidence, question, and output requirement
  → generate; check citations and final state
```

Chunking is not merely storage work. Chunks that are too small separate definitions from their conditions and exceptions; chunks that are too large bury the decisive sentence in noise. Titles, source, update time, tenant, product revision, and access scope are part of the evidence because later filtering and explanation depend on them.

Retrieval is not the last decision. The system must still ask whether material is visible to this user, has the intended revision, conflicts with another result, or directly supports the conclusion. Deterministic filters, retrieval models, rerankers, and business queries can each contribute to that decision.

## Retrieval Is More Than Semantic Similarity

Vectorizing every question and taking the nearest results can miss exact entities, structured conditions, and authority boundaries.

| Path | Best for | Typical boundary |
| --- | --- | --- |
| Term or sparse retrieval | Error codes, model numbers, API names, legal clauses | A paraphrase can miss recall |
| Vector or dense retrieval | Synonyms and different wording for related concepts | Similar entities can be confused |
| Structured queries | Inventory, orders, authority, time ranges, computable conditions | Only answers modeled data relationships |
| Graph or relation queries | Explicit entities, paths, and multi-hop constraints | Modeling and maintenance cost |

Dense representations help with “the user did not use the source's words, but what do they likely mean?” Sparse representations preserve “this exact error code, revision, or product name must not become another one.” They are often combined: retrieve candidates through different paths, then merge and rerank for the task. This dense/sparse distinction concerns evidence selection. It is not the same as MoE routing or sparse attention inside a Transformer.

No path is inherently superior. An authorized database query is preferable to guessing from passages when the question is whether order A-17 is refunded now. Source-backed document retrieval fits policy interpretation. Multi-turn retrieval and tools are justified only when later action depends on earlier results.

## Context Engineering Preserves Decisive Information in a Finite Workspace

A larger context window does not mean that all history, files, and tool descriptions should be included. The model attends only to tokens visible in this turn; irrelevant material consumes length, adds cost, and makes conflicting information harder to distinguish. Long context can hold more evidence, but it does not automatically retrieve, rank, or verify it.

The useful question is not “how much more fits?” but “what decisive information is absent for this judgment?”

| Content | What to retain | What not to assume |
| --- | --- | --- |
| Instructions | Goal, boundaries, output form, escalation conditions | Instructions replace authority or business rules |
| Task state | Current input, completed steps, unmet conditions | More history is always better |
| External evidence | Directly relevant text or records with source information | The model will use it faithfully |
| Tool contracts | Capabilities, arguments, and result forms needed now | A tool list grants authority |

Summaries, compression, and memory are also selections, not lossless storage. A summary can omit a condition; durable memory must later be retrieved and verified; KV cache reuses inference computation and is not application memory. Evidence should retain its source, time, and trust level rather than becoming an unsupported conclusion.

## Most Evidence Failures Precede Generation

An incorrect answer is often only the visible symptom of an earlier evidence failure.

| Symptom | Check first |
| --- | --- |
| A key fact is absent | Missing source, harmful chunking, mismatched query, or weak recall |
| The answer cites the wrong material | Entity confusion, revision-filter failure, reranking error, or source conflict |
| The answer exposes forbidden information | Retrieval did not filter by user, tenant, resource, and operation |
| A citation does not support the conclusion | The model mixed adjacent material, prior knowledge, or a guess into the claim |
| Quality falls with long context | Noise, repetition, and conflict displaced decisive evidence |

Evaluation should inspect these stages separately, not only assign one score to the final response. It can test recall of decisive material, authorization filters, whether a conclusion has supporting evidence, whether a citation names the right revision, and whether the system admits uncertainty when material is missing. For payments, publication, and other writes, RAG supplies reasons; tools and business systems still establish authority and outcome.

## RAG, Memory, Tools, and Fine-Tuning Fill Different Gaps

| Mechanism | What it changes | Fits | Does not replace |
| --- | --- | --- | --- |
| RAG | External evidence visible this turn | Mutable, sourced, access-controlled material | Reliable execution or truth guarantees |
| Memory | Durable records that may be selected later | Preferences, task state, verified conclusions | Having influenced this inference already |
| Tool | An external read, calculation, or action | Live state, deterministic computation, business actions | Correct interpretation by the model |
| Fine-tuning | Behavioral tendencies in parameters | Stable formats, task patterns, domain expression | New private facts or per-request authority |

Use retrieval or queries when material changes and requires sources or access control; use tools when an external result must decide the outcome; adapt training only when the behavior pattern itself is stable. The distinction tells us whether a failure lies in the model, evidence, or execution.

## Summary

RAG is not about storing more text. It brings the decisive evidence for a current task, with correct source, revision, and authority, into limited context. Retrieval narrows candidates, filtering and reranking select them, the model generates from evidence, and programs validate citations, authority, and external results. The next chapter, [Function Calling and Tool Use: Mechanism, Difference, and Essence](function-calling-tool-use.md), explains how a model proposal reaches an external program when evidence alone cannot answer or an action is needed.
