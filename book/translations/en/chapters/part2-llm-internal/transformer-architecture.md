# Transformer Architecture Through Data Flow

To understand a Transformer, ask how token vectors exchange information and gradually become representations useful for prediction. This chapter follows that complete data flow, including how attention matches and aggregates information.

## Two Kinds of Computation in Each Layer

Treating a position as a processing unit gives this sketch:

```text
Input representations with positional information
                       ↓
Attention: aggregate from accessible positions
                       ↓
FFN: transform each position nonlinearly
                       ↓
Repeat layers to form output representations
```

Actual layers also contain residual connections and normalization; their ordering varies by architecture. A residual connection has the form $y=x+F(x)$, preserving a short path for information and gradients and making deep optimization easier. It does not guarantee lossless gradient flow: normalization, parameter scale, optimization, and data jointly determine stability. Together with attention and FFNs, these components affect information and gradient propagation.

In a backend analogy, attention resembles input-dependent weighted routing and an FFN resembles local processing at each position. But tokens are not independent services, and weights are not network routing tables: the computation uses tensors rather than RPCs between nodes.

### MoE: Sparse FFN Computation

Mixture of Experts (MoE) can replace a dense FFN in some Transformer layers with several expert FFNs. A router selects a small subset for each token representation and combines their outputs:

```text
token representation → router → selected FFN experts → weighted combination
```

The purpose is to increase capacity without sending every token through every parameter. MoE can appear in text or multimodal models, but it is not required for multimodal input, tool calling, or Agents. It also differs from an external system routing a whole request to one model: the former is learned computation for a token inside a layer; the latter is application control flow.

## Why This Architecture Is Useful

Sequence modeling has involved different trade-offs. A fixed-window feed-forward model can directly use only a limited neighborhood; RNNs and LSTMs carry earlier context forward through recurrent state, but positions in a layer have sequential dependencies and distant information travels through a longer path.

| Approach | How it uses context | Main limitation | Transformer response |
| --- | --- | --- | --- |
| N-grams and fixed-window feed-forward networks | Read a fixed number of preceding positions | Information outside the window cannot enter the current computation directly; rare combinations have sparse support | Let a position aggregate from accessible context based on content |
| RNNs and LSTMs | Pass hidden state along the sequence | Positions within a layer have sequential dependencies, limiting cross-position parallelism; distant information has a longer path | Build direct relationships among accessible positions and organize them as matrix operations |
| Transformers | Build content-dependent direct relationships | Dense attention still has quadratic long-sequence computation and storage costs | Continue trading off representation, optimization, and execution cost |

Word embeddings give discrete tokens trainable continuous representations, but they do not by themselves determine how a current token combines context. This chapter concerns that exchange of information across a sequence.

A Transformer lets a position aggregate accessible positions directly based on content. This does not guarantee that a model will remember distant information, but it shortens the path through which an association can be made; when a complete sequence is known, many position computations can also be organized together. That change explains the value of attention, while pairwise relationships remain its long-sequence cost.

## What Changes Compared with an RNN?

An RNN position uses the previous position's hidden state, creating a recurrence along the sequence within a layer. Transformer self-attention computes relationships directly from the current layer's inputs, allowing many position computations over a known sequence to be organized in parallel.

Direct relationships also shorten some long-distance information paths: information need not pass only through adjacent positions. This does not make total computation constant. Standard dense self-attention forms pairwise relationships for a sequence of length $n$; the associated computation and attention-matrix size grow with $n^2$, with representation dimensions and implementation also affecting cost.

Matrix operations suit parallel hardware, while quadratic growth remains a long-sequence cost. “Suitable for GPU execution” does not mean “more computation is inherently better.” The original [Transformer paper](https://arxiv.org/abs/1706.03762) discusses these distinctions between parallelism, complexity, and path length.

## Parallel Computation Does Not Remove Order

Self-attention over input vectors without positional information cannot, by that operation alone, distinguish full sequence order. The architecture therefore needs positional encodings or another position mechanism.

Masks impose another constraint. A bidirectional structure can let a position read earlier and later context; causal attention for autoregressive generation usually permits only the current and preceding positions. “All positions communicate” must therefore be qualified by what is visible.

## Attention Is the Context Computation Inside a Transformer

For input states $X$, one attention layer forms three projections:

$$
Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V.
$$

It scores each accessible position by comparing a query with keys, applies scaling and a mask, turns the scores into weights with Softmax, and uses those weights to combine values:

$$
\operatorname{Attention}(Q,K,V)=\operatorname{softmax}\left(\frac{QK^T}{\sqrt{d_k}}+M\right)V.
$$

This is differentiable weighted aggregation. It is not a database lookup, a network call, or an explicit table of relationships. $QK^T$ determines where and how strongly a position reads; the weighted sum of $V$ determines what it brings back. Q, K, and V are computed from the current states at each layer, so the same token can aggregate from different places in different contexts.

Dividing by $\sqrt{d_k}$ helps keep scores from making Softmax too extreme during training. A causal mask blocks future positions for next-token prediction; a padding mask excludes artificial fill positions in a batch; specialized structures can restrict other pairs. The causal visibility used for training and inference must agree, or training would expose answers that generation cannot see.

Multi-head attention repeats this computation in several learned projection subspaces, concatenates the results, and projects them back together. Heads are not assigned fixed human meanings: training may make some emphasize local, syntactic, referential, or formatting patterns, and some may be redundant. Attention handles cross-position aggregation; the FFN then transforms each position nonlinearly. Neither component retrieves external information, stores a queryable long-term memory, or executes a tool.

During training, predictions at many positions can be computed in parallel. During ordinary autoregressive generation, a token must still be selected before it becomes part of subsequent input. Parallel computation inside layers and dependencies in an output sequence concern different levels.

## Model, Training, and Runtime Are Different Layers

A Transformer system involves three layers. Separating them shows whether a change affects model representation, parameter learning, or execution cost.

| Layer | Question it answers | Typical mechanisms | Main entry in this book |
| --- | --- | --- | --- |
| Model architecture | How do representations exchange and transform information? | Attention, FFNs, position mechanisms, masks, and the structural placement of residual paths and normalization | This chapter; [Gradient propagation](../part1-math-foundations/vanishing-exploding-gradients.md) |
| Training process | How do parameters learn stably from data? | Losses, backpropagation, optimizers, warmup, and numerical precision | [Optimizer choice](optimizer-selection.md), [LayerNorm](layer-norm.md) |
| Runtime system | How does a trained model process a request? | Prefill, decode, KV cache, and batching strategies | [Generation](llm-generation.md) |

The layers constrain one another, but none substitutes for another. For example, a KV cache reuses intermediate state because of causal-attention computation; it does not define attention. Learning-rate warmup can affect training stability without changing the calculation in an attention layer. Algorithms such as FlashAttention change how attention is executed, not the attention result it is intended to compute.

## Encoders, Decoders, and Model Uses

| Structure | Information organization | Typical uses |
| --- | --- | --- |
| Encoder | Contextually encode a supplied input, often with bidirectional visibility | Representations, classification, retrieval |
| Decoder-only | Causally model a prefix and continue generating | Text continuation and conversation |
| Encoder-decoder | Encode input; generate using both encoded input and the generated prefix | Translation, summarization, and other text generation |

These are typical associations, not mutually exclusive capability lists. The original Transformer used an encoder-decoder structure; [T5](https://arxiv.org/abs/1910.10683) also demonstrates how that structure supports diverse text tasks. A GPT-style decoder-only choice must not become a claim that all LLMs require it.

The original encoder-decoder flow is:

```text
source sequence → embeddings + positional information → encoder stack → encoded representations
target prefix   → embeddings + positional information → masked self-attention
                                                           ↓
                                         cross-attention reads encoded representations
                                                           ↓
                                            FFN → LM head → next token
```

The encoder first forms contextual representations of the complete input. The decoder reads only the known target prefix while cross-attention gives it access to the encoded source. A decoder-only LLM removes the separate encoder and cross-attention: prompts, chat-template tokens, and generated tokens all occupy one causal sequence. It still uses attention—causally masked self-attention—and still generates by choosing a next token and appending it to that sequence.

## Summary

A Transformer repeatedly combines cross-position aggregation with per-position nonlinear transformation. Positional mechanisms, masks, residual paths, and normalization organize that computation. This explains how it processes a sequence; what it learns also depends on training data, objectives, and scale.

## Further Reading

- [Generation](llm-generation.md) — parallel training and stepwise decoding
- [Vanishing and Exploding Gradients](../part1-math-foundations/vanishing-exploding-gradients.md) — residual paths and gradient propagation
