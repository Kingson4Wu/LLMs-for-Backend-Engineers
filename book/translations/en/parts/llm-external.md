# Part III: LLMs and External Systems

Model parameters and current context can only determine what output is likely next. They do not independently obtain current information, call a business system, acquire authority, or prove that work is complete. This part starts from that boundary and explains how an application turns model generation into readable structure, executable requests, and verifiable results.

On [the book’s main map](../index.md#the-books-main-map), this part lies between model computation and service delivery. It adds current evidence and executable actions without modifying model parameters at runtime.

The first chapter establishes the interaction map. The following chapters explain how material becomes evidence through retrieval, filtering, and reranking; how models propose tool calls; how protocols make external capabilities discoverable; how harnesses, runtimes, and skills organize multi-turn work; and how evaluation checks final quality. Afterward, readers should be able to distinguish a model proposal, program execution, and a fact in the environment.

| Reading order | Question answered |
| --- | --- |
| [How LLMs Interact with the External World: From Generation to Action](../chapters/part3-llm-external/llm-external-interaction.md) | How are responsibility for generation, execution, and external facts divided? |
| [RAG and Context Engineering: How Evidence Enters a Model](../chapters/part3-llm-external/rag-context-evidence.md) | Which material belongs in this turn's context, and how can missing, wrong, or unauthorized evidence be avoided? |
| [Function Calling and Tool Use: Mechanism, Difference, and Essence](../chapters/part3-llm-external/function-calling-tool-use.md) | How does a model propose a structured call, and how does a program execute it? |
| [From MHS and MCP to Domain Capability Protocols](../chapters/part3-llm-external/mhs-mcp-domain-capability-protocol.md) | How can external capabilities gain reusable semantics and interfaces? |
| [Harnesses, Agent Runtimes, and Skills: How Multi-turn Tasks Run Reliably](../chapters/part3-llm-external/harness-runtime-skills.md) | How do multi-turn tasks preserve state, recover, constrain authority, and confirm final state? |
| [AI Agent Evaluation: From Tests to a Business Quality System](../chapters/part3-llm-external/agent-eval-business-quality-system.md) | How can repeatable evidence show that a system has truly improved? |
