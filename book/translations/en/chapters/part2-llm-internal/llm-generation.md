# LLM Generation: From Input to the Next Token

A chat interface shows a question and an answer; the model processes numbers. To understand generation, follow one request: how text enters the model, what the model produces, and where the next step begins.

This article uses a common autoregressive, decoder-only text model as its example. This is an important architecture, not the definition of every language model; encoder-decoder models can generate text too.

## From Text to Model Input

### Tokens, IDs, and Vectors Are Different Things

A tokenizer divides text into units from the model's vocabulary and converts them into IDs. A token may represent a word, part of a word, punctuation, or a byte fragment. Token counts are not interchangeable with word or character counts.

The following segmentation and IDs are illustrative, not output from a real tokenizer:

```text
Text: check order
  ↓ tokenize and assign IDs
[check] [order] → [31, 208]
  ↓ look up the embedding table
vectors e31 and e208
  ↓ combine position and context through model layers
contextual representations at each position
```

An ID is a vocabulary index: 208 is not semantically “greater” than 31. Embeddings map discrete IDs to vectors; subsequent layers transform those representations using context. See [The Evolving Role of Embeddings](embedding-evolution.md) for the distinction between input and contextual representations.

### How Chat Messages Become a Sequence

Conversation interfaces usually store messages with roles, including user questions, assistant replies, and tool results. A service uses the model's chat template to arrange messages with boundary markers. Conceptually:

```text
[instruction] Explain the error briefly
[user] The request returned 403. What might be wrong?
[assistant] ...generation continues here...
```

These labels are illustrative. Actual special markers depend on the model's format and cannot be replaced by arbitrary strings. Roles and boundaries help identify who said what; they are not program-level authorization checks. [Hugging Face's chat template documentation](https://huggingface.co/docs/transformers/main/en/chat_templating) shows how messages become token sequences.

## What One Generation Step Does

Given the current sequence, the model computes a hidden representation at the last position. An output projection produces a score, or logit, for each vocabulary token. Softmax converts scores to a probability distribution, and the decoding procedure selects a token.

```text
Existing input → Transformer → last-position representation
                                          ↓
                                  vocabulary logits
                                          ↓
                               decoding selects a token
                                          ↓
                           append it and begin the next step
```

This is a conditional probability:

$$
p_\theta(x_{t+1}\mid x_1,\ldots,x_t)
$$

Here $\theta$ denotes model parameters. During ordinary generation, the sequence and intermediate computation state change; parameters usually remain fixed. High token probability means a continuation is favored by the model, not that a factual claim has that probability of being true.

Stopping also has mechanisms: the model emits an end marker, or the runtime applies a length limit, stop string, or other restriction. Truncation is different from the model producing an ending.

## Why Training Can Be Parallel but Generation Has Dependencies

During training, the subsequent tokens in the example are already available. For a simplified sequence `[I, love, coding, EOS]`, a single forward pass can compute predictions at several positions and compare each with its target:

```text
Known prefix I              → target love
Known prefix I love         → target coding
Known prefix I love coding  → target EOS
```

A causal mask prevents a position from reading later answers, keeping its representation dependent only on the allowed prefix. What runs in parallel is computation at multiple positions in a known example. The model has not generated an unknown future in advance.

At inference time, the next input includes the token just selected, so ordinary autoregressive decoding advances step by step. Selecting “love” produces a different next-step condition from selecting “like.” Methods such as speculative decoding can propose and verify candidates in batches, improving execution efficiency. They do not erase the distinction between known training targets and unknown inference outputs.

## Prefill, Decode, and the KV Cache

### Processing the Input and Continuing Generation

**Prefill** processes the supplied input sequence and establishes computation state; **decode** then continues generation from that state. This separates time to the first output token from the interval between later tokens.

For input `[A, B, C]`:

```text
Prefill: process A, B, C → use C's output to predict D
Decode: feed D into the model → use D's output to predict E
Decode: feed E into the model → predict the following token
```

When predicting D, D has not yet been selected, so its representation cannot already be computed. Selecting D and feeding it back are separate steps.

### What the Cache Stores

With causal attention, appending D does not change the prefixes that A, B, and C could originally access. When the model and computation conditions are compatible, each layer's historical keys and values can therefore be reused instead of recomputing the entire old prefix. This is the core of the KV cache.

A KV cache is **runtime computation state** available to causal decoding. It uses the model's existing attention computation, but it does not define Transformer architecture and is not application-level long-term memory. See [Transformer Architecture](transformer-architecture.md) for the map that separates model, training, and runtime layers.

The new position's query still matches against the accessible historical keys and aggregates values. Caching removes repeated computation; it does not make reading long contexts free, and the cache consumes memory. See the [Transformers caching explanation](https://huggingface.co/docs/transformers/main/en/cache_explanation).

Editing a prefix changes information on which later positions depend, so old cache entries after the change cannot be reused unconditionally. Cross-request prefix caching further reuses computation for shared inputs; matching, retention, and billing depend on the service.

A KV cache is computation state, not a persistent user record. Deleting a cache usually means recomputing; deleting stored history may mean losing the information needed to reconstruct an input. [How LLMs Interact with the External World](../part3-llm-external/llm-external-interaction.md) develops this distinction.

## Sampling: Choosing a Token from a Distribution

### Temperature: Changing Concentration

For logits $z_i$ and positive temperature $T$:

$$
p_i(T)=\frac{\exp(z_i/T)}{\sum_j\exp(z_j/T)}
$$

Lower temperature generally concentrates a distribution; higher temperature flattens it. If three candidates have probabilities `[0.6, 0.3, 0.1]` at $T=1$, changing temperature to $0.5$ is equivalent to squaring and renormalizing these probabilities, giving approximately `[0.783, 0.196, 0.022]`.

This changes selection tendencies without adding factual evidence. Low temperature can reliably produce an incorrect answer. The formula does not apply at $T=0$; APIs typically handle zero temperature separately, for example with greedy decoding.

### Top-K and Top-P: Narrowing the Candidate Set

Top-K retains the K most probable candidates. Top-P accumulates probabilities in descending order and retains the smallest prefix reaching the threshold, then renormalizes within that set.

With probabilities `[0.6, 0.3, 0.1]` and Top-P of 0.8, the first two candidates remain, with renormalized probabilities of approximately `[0.667, 0.333]`. The number retained depends on the distribution; it is not always two.

When filters are combined, their order matters. The example below explicitly uses “temperature → Top-K → normalization → Top-P.” Services do not necessarily use identical combinations.

### Random Sampling, Greedy Decoding, and Beam Search

| Method | Selection | Boundary to understand |
| --- | --- | --- |
| Random sampling | Draw according to candidate probabilities | More diversity does not imply more factual accuracy |
| Greedy decoding | Choose the highest-scoring candidate each step | Deterministic for identical logits; no guarantee of correctness or whole-service reproducibility |
| Beam search | Continue a limited set of high-scoring sequences | Optimizes a sequence score; guarantees neither a global optimum nor real-world correctness |

Keeping multiple beams increases computation and state. It should not be equated with a fixed API billing multiplier. See [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751) for research on probability truncation and generation quality.

### A Minimal Sampling Example

This example handles one-dimensional logits representable as finite float32 values and returns a token ID. It omits batched generation, stop markers, and caching to expose the mechanism. It requires PyTorch.

```python
import torch

def sample_next_token(logits, temperature=1.0, top_k=0, top_p=1.0):
    if logits.ndim != 1 or logits.numel() == 0:
        raise ValueError("logits must be a nonempty vector")
    scores = logits.float()
    if not torch.isfinite(scores).all():
        raise ValueError("logits must be finite in float32")
    if not 0 < temperature < float("inf"):
        raise ValueError("temperature must be positive and finite")
    if not isinstance(top_k, int) or top_k < 0 or not 0 < top_p <= 1:
        raise ValueError("invalid top_k or top_p")

    scores = (scores - scores.max()) / temperature
    scores, indices = torch.sort(scores, descending=True)
    if top_k > 0:
        scores, indices = scores[:top_k], indices[:top_k]
    probs = torch.softmax(scores, dim=-1)

    # Keep the token that first reaches the cumulative threshold.
    keep = torch.cumsum(probs, dim=-1) - probs < top_p
    keep[0] = True
    probs, indices = probs[keep], indices[keep]
    probs = probs / probs.sum()
    return indices[torch.multinomial(probs, 1).item()].item()
```

Even with Top-K disabled, sorting is required before applying a cumulative Top-P threshold. Putting the most probable token last in vocabulary order is a useful way to check this behavior.

## Why Intermediate Reasoning Steps Can Help

“Token-by-token generation” describes an output mechanism. By itself, it proves neither the presence nor the absence of a reasoning ability. Consider comparing totals for two orders: a model could state a conclusion immediately, or first list the amounts, add them, and compare.

The second route places intermediate results into subsequent context, making room for stepwise processing. The [Chain-of-Thought paper](https://arxiv.org/abs/2201.11903) studies the effects of demonstrations containing intermediate steps on reasoning tasks. This does not mean that more words always improve accuracy: an intermediate step can be wrong, and later steps can inherit that error.

Three ways of spending more inference-time computation should be distinguished:

- Generate more intermediate steps along one path.
- Generate multiple candidates, then compare or verify them.
- Use external tools to obtain new evidence or execution results.

These provide different computation, information, and selection opportunities. Without a way to identify correct results, retries merely produce more answers. Visible reasoning text is not necessarily a faithful record of all internal computation; whether a product displays it is a separate product and interface choice.

## Summary

A generation step maps current input to a distribution over the next token, selects a token, and continues. Training changes parameters, context changes conditions, caching reuses computation, and sampling changes selection. Separating these changes helps explain an answer and determine whether more information, different training, or an external tool is needed.

## Further Reading

- [How Model Capabilities Are Trained](model-training-lifecycle.md)
- [Softmax](../part1-math-foundations/softmax.md)
- [How LLMs Interact with the External World](../part3-llm-external/llm-external-interaction.md)
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — foundations of attention architectures and causal constraints
