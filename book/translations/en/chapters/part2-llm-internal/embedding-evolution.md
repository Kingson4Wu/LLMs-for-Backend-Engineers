# From Word2Vec to Transformers: The Changing Role of Embeddings

In Skip-gram with Negative Sampling, Embeddings are gradually learned from a corpus through an objective and loss that predict context. Transformers likewise start from learnable token vectors, but those vectors are no longer the final product: they are the beginning of deep sequence computation. The difference is not whether Embeddings are learned, but what objective constrains them, where they sit in the computational structure, and what function they serve.

When comparing them, look at an Embedding's place in the optimization objective and computation graph, rather than only at architectural complexity.

---

## A Unified View: Embedding Is a Learnable Parameter Table

For common learnable token lookup tables, Word2Vec and Transformer input embeddings have the same basic mathematical form:

- Both can be represented by a matrix $E \in \mathbb{R}^{V \times d}$.
- Every token ID $i$ corresponds to one row vector $\mathbf{e}_i = E[i]$.
- Vector values begin with random initialization and are continually updated through backpropagation.

Other architectures may use weight tying, factorized embeddings, fixed positional encodings, or continuous input representations; this discussion concerns the token embedding table.

**An embedding is not a predefined semantic representation; it is part of the model parameters.**

The difference between the two model families is not whether an embedding is a parameter, but:

> **which task shapes the embedding, in which structure, and under which loss function.**

---

## Embedding in Word2Vec: A Direct Optimization Target

In Skip-gram with Negative Sampling, embeddings have these characteristics:

### 2.1 Training Mechanism

- **Direct objective:** distinguish real co-occurring word pairs from random word pairs.
- **Loss function:** depends only on $\mathbf{v}_c^\top \mathbf{u}_w$.
- **Update driver:** entirely local context co-occurrence statistics.

### 2.2 Core Features

1. The training objective is “predict the context.”
2. The context window is local and fixed in size.
3. **The embedding itself is the final output** and can be used independently after training.
4. **The embedding is context-independent:** the same word always corresponds to the same vector.

### 2.3 The Design of Two Tables

Word2Vec explicitly distinguishes:

- input vector table $E_{\text{in}}$;
- output vector table $E_{\text{out}}$.

This is not accidental, but one instance of a more general modeling choice, whose extension in Transformers appears later.

---

## Embedding in Transformers: The Start of Deep Computation

### 3.1 Change in Structural Position

For GPT/BERT, the Transformer input layer has three parts:

1. **Token Embedding** (word or subword vector).
2. **Position Embedding** (position information).
3. (BERT also has Segment Embedding.)

After addition, they form the model's initial input:

```
h_0 = E_token[x] + E_pos[p] (+ E_seg)
```

From this point, a token embedding is no longer used directly for prediction. It:

- serves as the **starting point of the entire deep computation graph**;
- enters multiple self-attention and feed-forward layers;
- indirectly affects final predictions after many transformations.

### 3.2 A Fundamental Change in the Training Objective

In Transformers, embeddings are **not learned through the local task of “predict the context word.”** They are shaped by language-model objectives:

- **GPT** (autoregressive language model):

$$
\max \sum_t \log P(x_t \mid x_{<t})
$$

- **BERT** (masked language model):

$$
\max \sum_{t \in \text{mask}} \log P(x_t \mid x_{\setminus t})
$$

### 3.3 Gradient Propagation Path

The update path for an embedding is:

$$
\text{loss} \rightarrow \text{output layer} \rightarrow \text{Transformer layers} \rightarrow \text{input embedding}
$$

When a token appears in the input, its embedding vector:

1. participates in self-attention Q/K/V computation;
2. affects contextual representations;
3. indirectly affects final prediction probabilities;
4. receives gradients during backpropagation and is updated.

**This shares Word2Vec's underlying principle:** any embedding parameter on the loss computation path is updated by gradient descent. If input embeddings and output weights are tied, they can also receive gradients through the output loss. The source of an embedding gradient is:

> **the loss of predicting a token somewhere in the sequence, backpropagated through multiple Transformer layers.**

---

## The Key Distinction: Context-Free Embeddings and Contextual Representations

This is the most easily confused and most important point when connecting Word2Vec and Transformers.

### 4.1 What Is Actually Context-Dependent in a Transformer?

In a Transformer:

- **The token embedding table itself remains context-free.**

$$
E_{\text{token}}[\text{bank}] \quad \text{is always the same vector}
$$

- **What changes with context is the hidden state at every Transformer layer.**

```
h_l^(t) = f_l( h_(l-1)^(1:t) )
```

Therefore:

- **embedding** ≈ the initial word representation, similar to Word2Vec output;
- **hidden states** ≈ dynamic context-dependent representations.

### 4.2 Comparative Summary

| Property | Word2Vec | Transformer |
|----------|----------|-------------|
| Learnable embedding? | Yes | Yes |
| Contextual embedding-table entry? | No | No |
| Final semantic representation | Embedding itself | Top-layer hidden state |
| Learning signal | Local context prediction | Sequence modeling |
| Embedding’s role | End product of training | Starting point for deep computation |
---

## Weight Tying: From Two Tables to a Unified Design

Some Transformers, particularly many language models, use **weight tying**:

$$
W_{\text{out}} = E_{\text{token}}^\top
$$

Here $W_{\text{out}}$ is the output Softmax weight matrix.

This can be understood as:

- a generalization of whether Word2Vec input and output tables share weights;
- an explicit sharing constraint in Transformers;
- a way to reduce parameter count and improve generalization.

This shows that Word2Vec's two-table design is not accidental, but one instance of a broader modeling choice.

---

## A Unified Principle: The Loss Function Shapes Embeddings

Putting Word2Vec and Transformers together gives a structured account.

### 6.1 Common Ground

1. Embeddings are learnable parameters in both model families.
2. Embedding updates in both come from the loss of a prediction task.
3. Both are shaped indirectly by gradient descent, not predefined semantic containers.

### 6.2 Differences

1. **Prediction-target complexity:** local context versus a global sequence.
2. **Context modeling:** fixed window versus multi-layer self-attention.
3. **Final product:** Word2Vec ends at the embedding layer; Transformers begin there.
4. **Semantic representation:** Word2Vec uses embeddings directly; Transformers use hidden states transformed through many layers.

### 6.3 Evolution in One Sentence

This evolution can be summarized in one sentence:

> **In Word2Vec, an embedding is the final learning target;**
> **in Transformers, an embedding is the start of deep reasoning.**

More specifically:

- **Word2Vec:** embedding ≈ the direct modeling result of corpus co-occurrence structure.
- **Transformer:** embedding ≈ a parameterized entrance for underlying lexical information; real semantic composition occurs in multi-layer self-attention.

They nevertheless share one principle:

> **An embedding is a parameter indirectly shaped by a loss function through gradient descent, not a predefined semantic container.**

---

## Summary

Understanding the evolution of embeddings from Word2Vec to Transformers requires recognizing:

1. **The mathematical nature remains:** both are learnable parameter matrices updated by backpropagation.
2. **The training objective advances:** from local context prediction to global sequence modeling.
3. **The functional role changes:** from final output to computation starting point.
4. **Context modeling deepens:** Transformer context dependence comes from hidden states, not the embedding table itself.
5. **Design choices continue:** the input/output-table relationship is an important modeling decision in both families.

This evolution is not a rupture, but a natural extension toward more complex tasks under one unified optimization principle.
