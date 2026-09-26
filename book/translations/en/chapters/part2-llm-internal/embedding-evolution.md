# From Word2Vec to Transformers: The Changing Role of Embeddings

## The Problem This Section Addresses

Embeddings and contextual representations need a strict distinction. In both Word2Vec and Transformers, an input embedding is usually a fixed vector retrieved from a parameter table by token ID. The fact that the same word has different behavior in different sentences comes from later hidden states, not from the lookup entry becoming a different version.

The real change is how a model uses those vectors. Word2Vec often uses word vectors directly as features for similarity, clustering, or downstream tasks. RNNs, CNNs, and Transformers use input embeddings as the start of sequence computation. A Transformer produces context-dependent hidden states through many attention and feed-forward layers.

Understanding this change is essential to understanding LLM internals.

## How the Mechanism Works

### Word2Vec: The Embedding Is the End Product

The original skip-gram formulation predicts context words from a center word. Its common negative-sampling variant instead approximates this with an objective that distinguishes observed center–context pairs from random negative pairs:

```
Corpus: "Beijing municipal government held a meeting"

Task: give high scores to observed nearby pairs such as “held–Beijing municipal government” and “held–meeting”

Positive pairs: (held, Beijing municipal government), (held, meeting)
Negative pair: (held, random word), which should receive a low pair score
```

After training, the embedding itself is the result:
- Every word has a fixed vector.
- `bank` gets the same vector in every sentence.
- That vector is used directly for classification, clustering, or similarity search.

```
Embedding table E (lookup)
  │
  ▼
"bank" -> [0.12, -0.45, 0.78, ...]  # Always the same vector
```

### The RNN/CNN Era: Embeddings as Input Features

RNNs and CNNs introduced sequence modeling and local feature extraction:

```
Input: Embedding (word -> fixed vector)
  │
  ▼
RNN/CNN layers (sequence modeling / local features)
  │
  ▼
Fully connected layer + Softmax -> output
```

The embedding remains context-independent, but downstream layers model the sequence. Updates to the embedding are driven by backpropagation through the whole RNN/CNN, rather than a separate local prediction task.

### Transformers: Embeddings Are the Starting Point

The Transformer changes the architecture:

```
Input: Token Embedding + Position Embedding
  │
  ▼
N layers of Self-Attention + Feed-Forward
  │
  ▼
Top-layer Hidden State
  │
  ▼
Output layer -> predict next token / masked token
```

**The central change**: the embedding is the beginning of a deep computational graph, rather than its final output.

For an autoregressive model such as GPT, the objective maximizes sequence log-likelihood: predict token t from the preceding t-1 tokens, then sum the log probabilities over positions.

For a masked language model such as BERT, the objective maximizes log-likelihood at masked positions: predict randomly hidden tokens from the visible context, then sum the corresponding log probabilities.

In both cases, prediction loss updates the embedding through the full computation:

```
loss -> output layer -> Transformer layers -> input embedding
```

**The final contextual semantic representation is the top-layer hidden state, not the embedding-table entry.**

### The Critical Distinction: Context-Free Embedding Versus Contextual Hidden State

This is a common source of confusion:

```
Word2Vec:    word -> embedding -> direct use (context-independent)
Transformer: word -> embedding -> attention layers -> hidden state -> use (context-dependent)
```

In a Transformer:
- **The token embedding table itself remains context-independent**: `E["bank"]` is always the same vector for that token.
- **The hidden state at each layer changes with context**:

```
bank in "river bank":
  Layer 4: [0.1, 0.3, -0.2, ...]   # Representation associated with a riverbank

bank in "bank of China":
  Layer 4: [0.8, -0.1, 0.4, ...]   # Representation associated with a financial institution
```

**This is central to representing multiple senses of the same word.**

### Weight Tying: From Two Tables to Shared Parameters

Word2Vec explicitly maintains separate input and output tables because a word has different roles as a center word and as a candidate context word.

Many Transformers use **weight tying**: the output projection reuses the token-embedding matrix, transposed according to the matrix convention. This connects the two roles while reducing parameter count: **the same parameters are reused at different positions in the model**.

## Formalization (Optional Notes)

### Core Formulas

**Transformer embedding input**:

`h_0 = E_token[x] + E_pos[p]`

Token and position embeddings are added to form layer zero’s input in architectures using additive position embeddings.

**GPT autoregressive loss, in words**:

Maximize `sum_t log P(token t | preceding t-1 tokens)`: predict the next token from its prefix.

**BERT masked objective, in words**:

Maximize `sum_{masked positions} log P(masked token | visible context)`: predict the hidden token from context.

### Architectural Comparison

| Property | Word2Vec | Transformer |
|----------|----------|-------------|
| Learnable embedding? | Yes | Yes |
| Contextual embedding-table entry? | No | No |
| Final semantic representation | Embedding itself | Top-layer hidden state |
| Learning signal | Local context prediction | Sequence modeling |
| Embedding’s role | End product of training | Starting point for deep computation |
| Input/output vectors | Two independent tables | Often shared weights |

## Section Summary

The embedding remains a learnable parameter matrix, but its role changes from the final product in Word2Vec to the starting point in a Transformer. Contextual representations come from hidden states after multiple self-attention layers, not from the lookup table itself.

## Further Reading

- [Backpropagation](../part1-math-foundations/backpropagation.md) — How gradients shape embedding parameters.
- [Transformer Architecture](./transformer-architecture.md) — The full data flow around the embedding layer.
