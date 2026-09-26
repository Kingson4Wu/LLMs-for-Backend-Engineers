# How LLMs Interact with the External World: From Generation to Action

Part II explained how a model turns context into the next token. Connecting an LLM to external systems adds no separate magic: an application places instructions, material, tool contracts, and current state in context; the model still generates tokens; an external program interprets some output as structured data or a tool request, executes it, and returns the result to a later turn.

This chain marks the model's boundary. A model can write “24 items remain,” but cannot read live inventory from that sentence; it can generate arguments for `refund_order`, but does not thereby receive refund authority; it can claim completion, but cannot replace the final state in a database, browser, or business system. This chapter places prompts, structured output, tools, RAG, MCP, skills, harnesses, Agent runtimes, hallucination, and evaluation on one interaction chain.

```text
task, rules, material, history, tool contracts
                    │
                    ▼
           current context / prompt
                    │
                    ▼
         LLM decoding: next-token generation
             │                         │
             │ text answer             └──→ structured proposal / tool request
             ▼                                      │
        present to user                             ▼
                                      program validates, authorizes, executes
                                                       │
                                                       ▼
                                         result, error, external state
                                                       │
                                                       └──→ later context
```

Only the execution environment can directly change the external world. The model proposes a next step; the application decides what it sees, what it may do, whether to execute it, when to stop, and how facts outside the model establish success.

## Prompts and Context: Conditions on Decoding, Not Program Commands

From the model's view, a system prompt, user request, examples, retrieved material, conversation history, tool declarations, and previous tool results are all part of the current context. The decoder computes:

$$
P(\text{next token} \mid \text{current context})
$$

The essence of a prompt is to change that condition. It can state goals, boundaries, output form, and priorities, making some continuations more likely. It does not change parameters or force an external system to execute as a function call would. “Answer only from the policy below, and cite it” can guide output; it cannot guarantee complete material, correct citations, or the absence of invention.

| Information | Purpose | A common mistake |
| --- | --- | --- |
| Instructions and constraints | State the goal, prohibitions, delivery form, and escalation rule | One long prompt covers every exception |
| User task | Supplies this request and its inputs | User text is inherently trustworthy and unambiguous |
| Examples | Show desired judgment or form | More examples are always better |
| Facts and state | Supply material, tool results, and session state | Context automatically becomes truth |
| Tool contracts | State available operations, arguments, and results | Declaring a tool grants authority |

Context is finite working space, not unlimited memory. Irrelevant history, repeated material, and many overlapping tools consume attention and obscure decisive evidence. **Context engineering** selects sufficient, relevant, traceable tokens for each call rather than continually accumulating prompt text. [Anthropic's context-engineering discussion](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) frames the same problem as selection under finite attention.

This also explains prompt injection. Text from a web page, email, document, or tool result may say “ignore earlier rules,” but it is still context to the model. An application must distinguish trusted instructions from untrusted data, and have programs check authority, arguments, and goals before execution.

## Structured Output: Handing a Generated Proposal to a Program

Free text is useful for explanation, but unreliable for program branches. Structured output asks a model to produce agreed data—a classification, extracted fields, candidate SQL, interface state, or tool arguments:

```json
{
  "action": "lookup_inventory",
  "warehouse": "SZ-01",
  "sku": "water-500ml"
}
```

This is still decoding. The difference is that some interfaces can constrain available tokens during generation to a JSON Schema-like grammar, or a parser can reject invalid output afterward. Either approach limits its guarantee to fields, types, and nesting matching the agreement; [Structured Outputs documentation](https://platform.openai.com/docs/guides/structured-outputs) describes its guarantee as schema adherence, not factual correctness.

Generation-time constraints track the grammar or schema state for the current prefix, mask tokens that cannot extend that prefix into a valid structure, and continue decoding among the remaining candidates:

```text
model logits → grammar / schema state → valid-token mask → next-token selection
```

This excludes structurally impossible paths earlier than post-generation parsing, but cannot make field meaning, facts, or business authority correct. When a schema is too restrictive, cannot be reconciled with tokenization, or is unsupported by a service, the application must explicitly fail, retry, or fall back; it cannot assume a universal silent fallback.

```text
model output
  → syntax and structure: parseable, complete fields, correct types
  → business meaning: correct order, sensible amount and state
  → authorization and policy: may this user perform it; is approval required
  → execution and result: did the downstream system succeed; is the goal met
```

`{"order_id":"A-17","amount":100}` can be valid JSON and still name the wrong order, exceed a limit, or repeat a refund. Structured output does not make the model understand business truth. It creates an interface between a model proposal and deterministic checks. It underlies tool calling and is often sufficient for extraction, routing, and form completion without adding an Agent loop.

## Tool Calling: The Model Requests; a Program Reaches the World

A tool is an executable capability supplied by the application, usually described by a name, description, argument schema, and result format. The model generates a contract-conforming request; the host validates it and actually calls the service; the result or error becomes a new message in later context.

```text
user: How much 500 ml water is in the Shenzhen warehouse?
application → model: question + get_inventory declaration and schema
model → application: get_inventory({"sku":"water-500ml", "warehouse":"SZ-01"})
application → inventory service: authenticated actual request
service → application: { "available": 24, "as_of": "10:32" }
application → model: tool result
model → user: Shenzhen currently has 24 available items (10:32).
```

Function calling is therefore structured-output protocol, not a model directly calling a function. A model cannot open a database connection or bypass identity, tenant isolation, idempotency, and auditing. A tool result is also not task completion: a request can time out, return no record, partially succeed, or race with another update. Later context must contain the observed result, not a substitution of “called” for “completed.”

Read, calculation, and side-effect tools need different controls. Read tools need scope and freshness; calculation tools need input and unit validation; writes, payments, deletion, and publication need stronger permission, limits, idempotency keys, approval, or human confirmation. Tool descriptions must be clear and narrowly bounded: if a person cannot decide which of two tools applies, a model cannot reliably decide either. Names and descriptions are the model interface; authentication and execution policy are the program interface.

## Multi-turn Interaction: The Boundary Between Workflows and Agent Loops

One tool call is already an LLM–external-system interaction, but not necessarily an Agent. If steps and branches can be determined in advance—“query inventory → calculate total → write reply”—use a fixed workflow. It is easier to test, observe, and recover. A fixed workflow need not be a straight line: prompt chaining decomposes known subtasks; routing classifies before choosing a branch; independent work can run in parallel; generate–evaluate–rewrite is worth looping only when criteria are clear. Program code determines the control flow in each case.

An Agent loop begins when the next step depends on newly observed results. A missing product can lead the model to search a catalog; a pallet unit can lead it to query package size; it can then choose a next action from inventory, shipping limits, and the user's goal. The essential mechanism is that **an observation changes the next input, and the next decoding chooses an action**.

```text
task and state → assemble context → model proposes a next step
      ▲                                          │
      │                                          ▼
update state ← results, errors, observations ← validate and execute tool
      │
      └── stop on goal, inability, budget, or required approval
```

[ReAct](https://arxiv.org/abs/2210.03629) studies interleaving reasoning traces and environment actions. Its useful mechanism is feedback changing later action, not a particular “thought–action” template as the definition of every Agent. Reflection, retries, critique, and self-correction likewise place a new observation into later context and decode again. Unless training actually updates parameters, they are not runtime learning.

Loops accumulate cost, latency, and error and can repeat calls or oscillate between plans. State should explicitly record the goal, actions taken, decisive evidence, unmet conditions, resource use, and recovery point; the runtime must check stopping conditions. Multiple Agents help only when they add independent information, specialist tools, genuinely parallel work, or independent verification. Distributing one mistaken premise to many roles adds calls and lossy summaries.

## Material, Memory, and RAG: Selecting Evidence for This Turn

Parameters contain statistical regularities from training, not business knowledge queryable by version, authority, and time. **RAG** retrieves external material for the current context so generation is conditioned on it. The original [RAG paper](https://arxiv.org/abs/2005.11401) combined a parametric model with retrievable non-parametric memory to address knowledge access, update, and provenance.

The typical chain is “question → retrieve or query → select passages/records → place them in context → generate an evidence-based reply.” Vector retrieval is only one recall method; keyword search, SQL, knowledge graphs, permission filters, and reranking may fit better. The point of RAG is not a vector database. It is placing relevant, accessible, correctly versioned evidence into the context this inference can see.

| Concept | What it is | What it does not guarantee |
| --- | --- | --- |
| Context | Tokens actually visible in this inference | Automatic persistence next turn |
| Memory | Records persisted by an application and selected later | Influence on the current model already happened |
| RAG | Retrieving external material for a current question | Complete retrieval, correct material, or faithful use |
| KV cache | Reuse of inference computation for processed prefixes | User preferences or durable business memory |

Hallucination is not limited to cases where the model lacks material. Its objective is a context-consistent continuation, not automatic proof of each sentence. Bad retrieval, stale facts, conflicting context, and a conclusion detached from its citation can all yield fluent error. Factual tasks need sources, checks that conclusions follow from evidence, and tools or rules for important claims. RAG supplies and constrains evidence; it does not guarantee truth.

[RAG and Context Engineering: How Evidence Enters a Model](rag-context-evidence.md) explains how material is chunked, retrieved, filtered, reranked, and compressed into a turn's context.

## MCP, Skills, Harnesses, and Agent Runtimes: Their Places in the Chain

| Name | Location | What it solves | What it does not solve |
| --- | --- | --- | --- |
| Tool | Between proposal and executor | One callable capability and its input/output | Authorization, success, or task completion |
| MCP | Between client and external capability | Discovery and use of prompts, resources, and tools | Business-authorization decisions, control flow, and correctness |
| Skill | Before task knowledge enters context | Packages instructions, scripts, and resources for a task | Parameter updates or safe automatic script execution |
| Harness | Around each model call | Assembles context, calls the model, routes tool results | Business-system authority and fact judgment |
| Agent runtime | Around the whole multi-turn task | State, policy, budget, recovery, audit, and stopping | Intrinsically trustworthy model output |

The [MCP specification](https://modelcontextprotocol.io/specification/draft/server/index) defines prompts, resources, and tools as different server primitives: a prompt is a selectable task template, a resource is contextual material an application may supply, and a tool is a capability a model may propose calling. MCP can also negotiate protocol capabilities needed for authentication and authorization. But a token or established identity does not itself decide whether a user may perform a particular operation on a particular resource. The client and business service still determine scope and execution conditions by user, tenant, resource, and operation.

A Skill is closer to an on-demand task manual, packaging instructions, workflow, scripts, and resources. It may be delivered by MCP or by a file, repository, or product configuration. In every case it changes guidance and resources available for a task, not model parameters.

A harness is the control program around one or several calls: it selects context, sends requests, receives structured output, calls an executor, and records observations in state. An Agent runtime is the wider layer for state across turns, budgets, permission policy, concurrent tasks, recovery, and traceability. A simple Q&A application may need only a prompt and structured output; a full harness and runtime are justified when feedback must determine continued action. GPU scheduling and serving of each model request belong to [Part IV: LLM Infrastructure](../part4-serving-runtime/llm-infrastructure.md).

[Harnesses, Agent Runtimes, and Skills: How Multi-turn Tasks Run Reliably](harness-runtime-skills.md) develops multi-turn state, deterministic execution, recovery, and final-state verification.

## Reliability Comes from a Verifiable Loop, Not a Longer Prompt

Reliable systems assign each check to the responsible layer: schemas validate structure; business rules validate meaning and authority; executors return observed results; external state validates the goal; evaluations test behavior across representative tasks. Prompts, self-critique, and “check carefully” can supply signals but do not replace these controls. A guardrail is not one model: input filtering, output checks, tool-argument validation, sandboxes, limits, approvals, and auditing protect different entry points and consequences.

An **evaluation** is not asking a model to grade itself in one request. It repeatedly tests fixed tasks, input versions, allowed tools, and scoring rules. It should separately inspect:

| Dimension | Example |
| --- | --- |
| Final result | An order exists; an answer has supporting sources |
| Process quality | Correct tool choice; timeouts, empty results, and access denial handled |
| Safety and side effects | No overreach, duplicate refund, or unauthorized data exposure |
| Cost and latency | Calls, tokens, tool use, and completion time stay within budget |

For a multi-turn system, final environment state often matters more than the model saying it is done. Traces should preserve input versions, model and policy decisions, tool calls, returned results, and final judgment so failures can be reproduced and changes compared. [Anthropic's Agent-evaluation guide](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) likewise treats evaluation as testing a system's outputs and behavior against grading logic.

The book-wide map is now simple: prompts, RAG, and skills determine what the model sees this turn; structured output and tool calls turn generation into program-readable proposals; harnesses and runtimes organize proposals and observations into finite loops; authorization, executors, and evaluations establish what happened in the world. Understanding this responsibility chain prevents any framework label from being mistaken for the whole essence of an Agent.
