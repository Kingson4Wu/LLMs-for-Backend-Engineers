# Preface

Language models come with many terms: tokens, embeddings, attention, pretraining, fine-tuning, RAG, and agents. Each has an explanation somewhere, yet their connections may remain unclear. What has the model learned? Why does different input change the behavior of the same model? How does a system that generates text begin retrieving information and performing actions?

This book offers a stable explanatory framework so readers can use the boundaries among data, parameters, context, and external programs to explain what a language-model system is doing.

## Intended Readers

The primary audience is backend engineers with programming experience but little machine-learning background. Familiarity with functions, data structures, caches, interfaces, and service operation helps with the examples; completing a machine-learning course is not a prerequisite.

For developers already working with models, the book also helps correct scattered terminology by placing it into the relationships among training, inference, context, and external systems. AI application and platform engineers who need to understand the mechanisms behind RAG, tool use, agents, evaluation, or inference services—and other software engineers who want to connect model mechanisms to system boundaries—are also a good fit.

Its purpose is to understand LLM principles, causal chains, and system boundaries rather than instruct application development. This is not a framework or vendor-API tutorial, nor a replacement for a model-source tour, training recipes, GPU-kernel optimization, or a distributed-training reference. Use it first to reason about mechanisms, boundaries, and trade-offs, then consult current tool documentation for implementation detail.

## How the Book Explains Things

We treat a model as a system whose inputs, outputs, parameters, and computations can be examined. Engineering analogies establish intuition without replacing mechanisms. Resembling routing does not make attention a network router; resembling memory does not mean a conversation has been written into parameters.

The book enters detail where it changes understanding: representations are explained through vectors and training objectives; generation through decoding and state; external systems through the boundary between a model proposal and program execution; and infrastructure through the way resources and scheduling constrain a service. It does not attempt to catalog every model architecture, training algorithm, or application framework, nor does it require a philosophical verdict about whether models think like people.

Readers can follow the full route in the introduction or start with a problem they are currently facing. In either case, the goal is to explain what a concept changes, what it does not guarantee, and how it differs from adjacent mechanisms.

## Contributing

The manuscript and build sources are publicly hosted on GitHub. Questions, suggestions, and corrections are welcome. Feedback can include a difficult passage, your interpretation, and what remains unclear.
