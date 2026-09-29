# Appendix II: Learn This Book with AI

This manuscript can itself be the shared material for a conversation with AI. Let a network-capable AI download the complete PDF first and learn from it; when it cannot download files, give it a same-language PDF, Markdown, EPUB, or complete print HTML edition instead. AI’s role is not to produce a one-shot summary, but to help you locate, explain, question, and test understanding.

## Start Learning with AI

Copy the home page’s single learning prompt. It asks AI to first download the complete PDF at `https://kingson4wu.github.io/Understanding-LLMs/exported/en/Understanding-LLMs.pdf`, then learn from its table of contents, chapters, formulas, and figures.

## How AI Should Help You Learn

Ask AI to treat this book as evidence that can be checked, not background that it may freely rewrite. For an important conclusion, it should name the chapter, heading, or figure it uses; call what the book explicitly says **book evidence**, call a judgement derived from it an **inference**, and label claims that depend on current sources, product behavior, or real-world data as **requiring external verification**. It should say when it does not know.

One learning conversation should begin with one question that can change the path, not a long questionnaire. AI may first ask about your background, goal, or point of difficulty, then use a counterexample, trade-off, or retrieval question to test understanding. Keep your own judgement: an AI answer is not a new authoritative source; the manuscript and verifiable external sources remain the evidence.

## Book Map: Return from a Question to Chapters

The first four parts form a chain from mechanism to delivery. Part I explains vectors, probability, learning, and gradients; Part II explains training, representations, Transformers, and generation; Part III explains how evidence, tools, and external systems enter an application; Part IV explains inference-service performance, capacity, control planes, and reliable delivery. Further reading and appendices discuss boundaries, judgement, and additional material.

- To understand formulas, training, or Transformers, begin with Parts I and II.
- To design RAG, tool use, or agents, begin with Part III, then return to Part II when needed.
- To investigate latency, throughput, memory, or cost, begin with Part IV, then revisit generation and architecture.
- To build a complete mental model, study the four parts in order and restate the causal chain after each part.

## Five Learning Modes

1. **Diagnose and route:** state your backend experience, goal, and available time; ask AI for the shortest path and why each chapter belongs on it.
2. **Chapter dialogue:** ask AI to place one chapter in the full chain, explain it through an engineering problem, then ask one judgement question.
3. **Formula or figure explanation:** ask AI to identify inputs, transformation, outputs, and constraints before explaining symbols or arrows, and name one common misconception.
4. **Retrieval practice:** ask AI to ask one question at a time and not give the answer first; after you answer, it should identify the missing causal link and chapter to revisit.
5. **Engineering synthesis:** map your case to training, model architecture, runtime, external systems, or infrastructure, and distinguish book evidence from conclusions that need current sources.

## A First Message You Can Send

> I am studying this book. I have backend-engineering experience and want to understand RAG, tool use, and inference serving in two weeks. First build the shortest path from the table of contents; in every explanation, name the relevant chapter and heading, distinguish book evidence from your inference and claims requiring external verification, and test my understanding with one question after each section.

You can replace the goal with a concrete case, such as “Why do Prefill and Decode have different capacity characteristics?” or “What do long context, RAG, and tool use each solve?” Beginning with a question is more likely to produce understanding that can be checked and transferred than asking to “summarize the whole book.”

## Copyable Starter Prompt

Copy this single prompt into Codex, Claude Code, ChatGPT, DeepSeek, or another AI tool. It downloads the complete PDF first; if the tool cannot download files, give it the corresponding edition from the downloads page.

```text
I want to study Understanding LLMs for Software Engineers. First download and read the complete PDF manuscript: https://kingson4wu.github.io/Understanding-LLMs/exported/en/Understanding-LLMs.pdf

If you cannot download or read that file, tell me clearly and ask me to upload the same-language edition; do not pretend that you have read it. After you have read it, summarize the book’s four parts from its table of contents, then give me the shortest learning path for my goal. In every explanation, name the relevant chapter, heading, formula, or figure; distinguish “book evidence,” “your inference,” and claims that “require external verification.” Explain one concept at a time, then ask one question that checks my understanding.
```

## Boundaries of Figures, Formulas, and External Facts

Text, the table of contents, and formulas in the PDF are usually enough to begin learning; AI tools differ in their ability to read PDF images, long documents, and persistent context. If a question depends on spatial layout, arrows, or small labels in a figure, ask the tool to open that page, or use another edition from the downloads page when it cannot read the PDF. Do not treat a tool’s current behavior, model version, price, paper result, or production metric as a fixed fact from this book; check reliable current sources separately.

## Repository Tools Are an Enhanced Path

When you clone the repository and use Codex, Claude Code, or another tool that can read local files, AI can also inspect the original Markdown, SVG figures, learning index, and bilingual mapping. That makes it better for figure-by-figure checking, traceable citations, or private learning records. This is an enhancement, not a prerequisite: the complete PDF alone should let you begin a high-quality learning dialogue from this appendix.
