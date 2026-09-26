# Introduction

> An LLM system is not a black box that “answers questions.” It is a chain formed by training, the current context, external programs, and service execution.

Four different things are easy to conflate in an LLM application: what training writes into parameters; what the model sees in this request; how an application lets it retrieve material or perform an action; and how a serving system delivers the computation to a user. Confusing them turns RAG into training, tool calling into an innate model capability, or a model’s statement that it is finished into evidence that an outside task is complete.

This book starts from those four questions and builds a map for readers with programming experience to reason about system behavior. While reading, repeatedly trace a request: where information enters, what computation changes it, which state is retained, and who verifies the result.

## AI’s Scope and This Book’s Place Within It

AI is a family of techniques and systems that form predictions, content, decisions, or actions from inputs; it is not synonymous with generative AI. It serves both digital information systems and physical environments:

~~~text
AI
├─ digital information systems
│  ├─ perception and understanding: text, images, speech, multimodality
│  ├─ prediction, ranking, and optimization: recommendations, risk, demand, resource allocation
│  ├─ generative AI: text, code, images, audio, video, structured content
│  └─ digital agents: retrieve information, call software tools, run workflows
└─ physical-world systems
   ├─ embodied AI and robotics: perception, localization, planning, control, execution
   └─ automated driving: sensor fusion, scene perception, behavior prediction, path planning, vehicle control
~~~

These directions are not mutually exclusive. Automated driving can use Transformers or multimodal large models, while remaining a system that must perceive, predict, plan, control, and verify safety in a dynamic physical environment. A content-generating component alone does not classify the whole system as generative AI. The techniques behind these systems also overlap: rules and search, statistical machine learning, deep learning, and hybrid systems are technical approaches; supervised, self-supervised, imitation, and reinforcement learning provide different learning signals; Transformers are one family of architectures for organizing neural computation, while diffusion is another generative method.

This book concentrates on one path for digital information and software systems:

~~~text
AI
└─ deep learning
   └─ foundation models trained on broad data and adaptable to many tasks
      └─ Transformer-centered generative language models and their multimodal extensions
         └─ this book: training, model computation, external systems, and serving
~~~

The book therefore explains how Transformers, generation, context, RAG, tool calling, MCP, skills, harnesses, Agent runtimes, and inference infrastructure form a deliverable LLM system. It does not systematically cover general vision or speech algorithms, recommendation and ranking, sensor fusion, SLAM, trajectory prediction, motion planning, vehicle or robot control, or sim-to-real transfer. Those are equally important AI threads, but they solve problems outside this book’s scope.

“Narrow or weak AI,” “AGI,” “strong AI,” and “superintelligence” are not stages on one technical maturity ladder either. The first usually describes task scope; AGI concerns cross-domain capability; strong AI is the philosophical claim that a machine has mind or understanding; superintelligence denotes a hypothetical level of capability. They may all be discussed of one system, but none entails another. [Is “Artificial Intelligence” an Accurate Name? Reflections on AI’s Conceptual Boundary](chapters/appendices/what-ai-really-means.md) gives the full boundary between these terms.

## Start with the System View

~~~text
Training material + learning objective
          ↓
  Optimize parameters into a trained model

User request + instructions + conversation history + retrieved material
          ↓
      Assemble the current context
          ↓
Tokens → vector representations → Transformer computation → next-token distribution
          ↓
  Generate an answer or propose a tool call
          ↓
Application checks, authorizes, and performs the external action
          ↓
Results and state enter the next context, or serve as evidence of completion

Serving runtime: schedules computation for each model call, retains KV cache,
manages concurrency, and returns output
~~~

The upper section is training: data and objectives change parameters through optimization, shaping the patterns a model can learn. The middle is inference: the context of this request and the trained parameters jointly determine the next-token distribution, and a decoding strategy selects the emitted output. In an ordinary online call, retrieval, tools, and Agents do not modify model parameters; they change the information currently visible, the actions available, and the next input. The serving runtime does not decide whether a model understands something, but it determines whether requests can be delivered reliably within capacity, latency, and cost constraints.

These layers depend on one another, but none replaces another. A larger model cannot supply missing authorization; a longer context cannot prove that material is correct; and a successful tool invocation does not by itself establish that the task goal was reached.

## Why the Same Model Can Behave Differently

“The model learned it,” “it learned from a few examples,” and “let it think longer” often describe different mechanisms. The following distinction places long-term model capability, per-request adaptation, and external system guarantees in their proper roles:

| Layer | What it changes | Does it update model parameters? |
| --- | --- | --- |
| Pretraining | Forms language, code, and common task patterns from broad material | Yes |
| Post-training | Adjusts instruction following, output format, preferences, and some tool-use tendencies | Yes |
| Current context | Changes the conditions of this decoding through instructions, history, or examples; few-shot and in-context learning belong here | No |
| Stepwise computation and external connections | Adds information and computation available to this task through intermediate tokens, retrieved evidence, tool results, or extra turns | No |
| Validation and execution | Uses schemas, authorization, business rules, and external state to determine which proposals can run and whether the task really completed | No |

Providing examples is therefore not temporary training; retrieval, chain-of-thought, retries, and tool calls do not modify weights at runtime either. They change the current input, visible evidence, or subsequent computation path. The training chapter explains how parameters form and change capability; the generation chapter explains how context affects the next token; the external-systems section explains how a program validates and executes a model proposal.

## How the Four Parts Form One Thread

## The Book’s Main Map

![A four-layer map from training to service: mathematics and machine-learning foundations, LLM internals, external systems, and LLM infrastructure. It distinguishes parameters, current context, external actions, and service constraints.](assets/book-system-map-en.svg)

The map is not a one-way pipeline. It is a coordinate system for reading and diagnosing: the first two parts explain how a model is formed and computes; the third explains how an application supplies evidence and action interfaces; the fourth explains how that computation is delivered reliably. When facing a system question, first locate its layer, then identify the conditions it inherits from neighboring layers.

| Part | Core question | What you should be able to explain |
| --- | --- | --- |
| Part I: Mathematics and Machine Learning Foundations | How vectors, probabilities, and error form a learnable computation | How discrete tokens become vectors and how prediction error changes parameters |
| Part II: LLM Internals | How parameters acquire capability and how one input becomes output | Where training, Transformers, attention, decoding, and KV cache belong |
| Part III: LLMs and External Systems | How a model obtains current evidence and participates in an outside task | The responsibilities of context, RAG, tools, MCP, skills, harnesses, and Agent runtimes |
| Part IV: LLM Infrastructure | How one model call becomes a service | How requests, state, scheduling, capacity, deployment, and delivery constrain the experience |

Part I establishes the language needed for later computation. Part II organizes those foundations into a language model. Part III places that model back in an application and the external world. Part IV explains the runtime that carries the chain. The order follows dependencies, not a list of fashionable terms.

## Where to Start

On a first pass, follow the whole thread: in Part I, understand vectors, Softmax, cross-entropy, and backpropagation; in Part II, read the training lifecycle, Transformer, attention, and generation; in Part III, read context, RAG, tool calling, and the Agent runtime; then enter Part IV to see how one request is scheduled and delivered.

If your current work is closer to applications, begin with Part III. Return to Part II when you need to explain why a model produces an output, and move to Part IV when the question concerns latency, concurrency, or cost. Each article answers a focused question, but its place in this thread determines both what it explains and what it cannot replace.

After reading the book, you do not need to treat language models as mysterious abilities or master every training framework and inference engine. You should be able to distinguish patterns learned in parameters, evidence supplied by current context, actions performed by external programs, and constraints carried by the serving system.
