# Learn This Book with an AI Tutor

Use an LLM as an interactive tutor grounded in the book, not as a one-shot summarizer. It should locate chapters, explain causes, offer counterexamples, test your understanding, and return every important conclusion to evidence you can inspect.

## Recommended path: one prompt, complete PDF

Open the [English home page](https://kingson4wu.github.io/Understanding-LLMs/en/), copy its single learning prompt, and paste it into Codex, Claude, ChatGPT, DeepSeek, or another AI that can download files. The prompt tells the AI to download the complete PDF before it teaches, so the book—not an improvised summary—remains the shared evidence base. It also tells the AI to map the four parts, cite chapters and figures, distinguish evidence from inference, and check your understanding one concept at a time.

If the AI cannot download the linked file, give it an edition from the [downloads page](https://kingson4wu.github.io/Understanding-LLMs/en/downloads/). PDF is the default complete reading edition; Markdown, EPUB, and print HTML remain available for tools or readers that handle those formats better.

For an AI that can retrieve web material autonomously, give it the public [AI learning entry](https://kingson4wu.github.io/Understanding-LLMs/ai-learning/en.md). It links the complete editions, learning index, contract, and book map. The site-root `llms.txt` also lists both language entries.

## Local-source path

### Clone + Codex (best for figures, formulas, and source files)

Start Codex from the repository root. It reads `AGENTS.md`; ask it to read this file, the [book map](BOOK_MAP.md), the [learning index](index.json), and the matching learning contract: [Chinese](LEARNING_CONTRACT.zh-Hans.md) / [English](LEARNING_CONTRACT.en.md). The Chinese and English editions are strictly aligned counterparts; read the edition chosen by the learner.

## Learner-owned work

To keep questions, concept maps, or a review queue, copy [WORKSPACE_TEMPLATE](WORKSPACE_TEMPLATE) to `learning/workspace/`. That directory is ignored by Git and is neither book source nor release content.

## Start from an engineering question

This route works well when you already have a design, incident, review, or technical judgement in mind. For example:

- “What do long context, RAG, and tool use each solve, and how should I choose?”
- “Why do Prefill and Decode have different capacity characteristics?”
- “What actually happens from an input token to a tool execution?”

The tutor should first locate the question in the book’s causal chain, then explain the mechanism, constraints, and adjacent concepts. It should return to the corresponding source instead of giving a decontextualized answer.

## Study the book as a path

You can also state your goal, prior experience, and available time, for example:

> I have backend and distributed-systems experience and want a working model of Transformers and inference serving. Use this book to plan a path, and test my understanding at every step.

You do not need to begin with Chapter 1. `BOOK_MAP.md` provides entries for different questions, prerequisites, and optional paths; the tutor can adjust order and depth from there.

## File roles

| File | Purpose |
| --- | --- |
| [BOOK_MAP.md](BOOK_MAP.md) | Four parts, chapter relationships, question entry points, and study paths |
| [DIALOGUE_LEARNING.md](DIALOGUE_LEARNING.md) | Dialogue, follow-up questions, citations, and evidence boundaries |
| [AI_ENTRY.en.md](AI_ENTRY.en.md) | English machine-facing learning entry published with the site |
| `../book/` | Verifiable manuscript source, catalogue, and figures |

This directory deliberately contains no MCP configuration, Skill, startup script, or hidden prompt. Those would bind learning to a specific tool and turn an open discussion into a preset execution flow. Let the current question decide when tools, code, or outside sources are necessary.
