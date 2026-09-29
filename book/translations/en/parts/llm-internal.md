# Part II: LLM Internals

This part answers two connected questions: **how do parameters acquire capabilities through training, and how do existing parameters turn one request from input into output?** Training, architecture, and generation describe the same model at different time scales.

On [the book’s main map](../index.md#the-books-main-map), this part connects learnable computation to an application call. It discusses parameters and computation inside the model; it does not recast external facts or execution results as model capability.

| Group | What to understand | Where to begin |
| --- | --- | --- |
| Capability formation and adaptation | How parameters learn from data and adapt to a task | [How Models Acquire Their Capabilities Through Training](../chapters/part2-llm-internal/model-training-lifecycle.md), optimizers, fine-tuning, and distillation |
| Representation and computation | How token representations undergo sequence modeling, context exchange, and deep transformation | Embedding evolution, RNNs to Transformers, Transformers, scaled dot products, residuals, and LayerNorm |
| Generation and extension | How a model produces output step by step and how language and modalities share or extend representations | LLM generation, inference nondeterminism, multilinguality, and multimodality |

The catalog follows “training — representation and computation — generation and extension,” but each group can also be entered independently. This part describes statistical computation and parameter state inside a model; it does not turn current facts, authorization, or external execution into model capability.
