# From One-Hot to Embeddings: How Discrete Tokens Become Vectors

In natural-language-processing tasks, neural networks usually need to convert discrete symbols, such as words or tokens, into continuous numerical representations. This raises a central question: **how can discrete words be represented as numerical vectors in a way that reflects differences in their meaning and use**?

Word embeddings are a systematic answer to this question. They first map discrete IDs to learnable continuous representations. In early models, these representations can be learned by predicting co-occurrence, while in Transformers they are the starting point for later contextual computation. Skip-gram and Negative Sampling provide an example of why vectors emerge from a corpus.

---

## One-Hot Representation: Direct Encoding of Discrete Symbols

The most direct way to represent a word is one-hot encoding.

Let the vocabulary size be $V$. Each word then corresponds to a $V$-dimensional vector, with 1 only at the position for that word and 0 everywhere else. For example, suppose the vocabulary is:

$$
[\text{I},\ \text{love},\ \text{you},\ \text{China},\ \text{Beijing}]
$$

Then the one-hot representation of “Beijing” is:

$$
[0,\ 0,\ 0,\ 0,\ 1]
$$

One-hot has the advantages of being simple in form, uniquely identifying a token, and requiring no training. But its shortcomings are equally clear:

* Vector dimensionality grows linearly with the vocabulary, making it difficult to scale.
* The representation is highly sparse, with low computational and storage efficiency.
* It contains no semantic information; the similarity between different words is always 0.

Therefore, one-hot can serve only as an **indexing mechanism**, not as a semantic representation.

---

## The Core Idea of Distributed Representations

### The Basic Assumption of Distributed Representations

Distributed representations rest on a classic assumption:

> A word's meaning can be characterized by the distribution of its contexts.

Under this idea, a word is no longer represented by one isolated dimension, but by a low-dimensional, dense, continuous vector. Words with similar meanings should also have nearby vectors in space.

### Two Ways to Build Distributed Representations

There are two main approaches to building distributed representations of words:

1. **Count-based methods**

   * Typical examples: LSA, SVD of co-occurrence matrices, and PMI / PPMI.
   * Idea: first count co-occurrence frequencies between words and contexts, then obtain low-dimensional representations through matrix factorization.
   * Characteristics: they rely on global statistics and have a clear mathematical structure, but scale less well on large corpora.

2. **Prediction-based methods**

   * Typical examples: Word2Vec (Skip-gram / CBOW).
   * Idea: turn “learning word vectors” into a prediction task, then learn vector parameters by minimizing a loss function.
   * Characteristics: they can be trained online, scale well, and work effectively in practice.

GloVe lies between the two routes: it uses global co-occurrence statistics as input and then learns vectors through weighted regression, so it cannot simply be classified as a neural prediction method.

**The embedding-learning mechanism discussed below belongs to the second category: prediction-based methods.**

---

## A Formal Definition of Embeddings

In a neural-network framework, an embedding can be formalized as a learnable lookup mapping:

* Vocabulary size: $V$.
* Vector dimension: $d$.
* Embedding matrix: $E \in \mathbb{R}^{V \times d}$.

For any word or token, an embedding layer can be understood as:
**using the word's ID to retrieve its corresponding row from the matrix as that word's vector representation.**

Embedding parameters are not set manually. They are learned from data through downstream training objectives and gradient descent.

---

## Skip-gram and Negative Sampling: From a Corpus to a Training Objective

### Constructing Training Examples

Given a token sequence:

$$
[t_0,\ t_1,\ \dots,\ t_{N-1}]
$$

Let the window size be $w$. For each position $i$, construct training pairs:

* Center word: $c = t_i$.
* Context words: $o = t_{i-j},\ t_{i+j}$, where $1 \le j \le w$.

This constructs many positive pairs $(c, o)$ from the raw corpus.

---

### Input and Output Vector Tables

Skip-gram maintains two independent embedding tables:

* **Input vector table**: used for center words.
* **Output vector table**: used for context or candidate words.

For any word ID $i$ in the vocabulary:

* The input vector table provides its vector when it is used as a center word.
* The output vector table provides its vector when it is used as a candidate context word.

The two vectors use the same vocabulary index, but their parameters are independent and their statistical roles differ.

---

### Scoring Function and Probability Modeling

In Skip-gram, the model assigns a **matching score** to a “center word + candidate word” pair.

This score can be understood as:
**how similar the center-word vector and candidate-word vector are in vector space.**

The model then maps this score to a value between 0 and 1, representing the probability that the candidate word is truly in the center word's context.

---

## Loss Function and the Mechanism That Learns Vectors

### The Negative Sampling Training Objective

For a real center-word–context-word pair $(c, o)$, the Negative Sampling objective has two parts:

1. **Positive-example objective**
   Make the matching score between center word $c$ and real context word $o$ larger.

2. **Negative-example objective**
   Randomly sample several words unrelated to $c$ as negative examples,
   and make the matching scores between $c$ and those negative examples smaller.

During training, the model treats “real context” as the positive class and “random words” as the negative class,
computes binary log loss for each pair, and adds these losses for optimization.

---

### Why One Update Affects Several Kinds of Vectors

It is important to emphasize:
**input vectors and output vectors are not trained separately; one training objective drives them at the same time.**

In one training step:

* The input vector of the center word is updated.
* The output vector of the real context word is updated.
* The output vector of every negative sample is also updated.

Geometrically, training is equivalent to:

* Pulling the center-word vector closer to the real context vector in space.
* Pushing the center-word vector away from random negative-sample vectors.

---

## Why Two Vector Tables Are Needed

The fundamental reason for an input table and an output table is that **the same word has two different functions in the training objective**:

* As a center word: it generates an intermediate representation to predict surrounding words.
* As a candidate word: it is matched against the center-word representation to decide whether it is real context.

These two roles are asymmetric in language statistics. Forcing them to share one parameter set adds an unnecessary constraint and weakens the model's ability to fit the true co-occurrence structure.

After training, practice commonly uses vectors from the input table as final word-vector representations, because they more stably reflect a word's location in semantic space.

---

## A Minimal PyTorch Example

The following is an **extremely small Skip-gram + Negative Sampling implementation** that retains only the core mechanisms:

* Separate input and output vectors.
* Positive and negative examples jointly drive parameter updates.

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

V, D = 3, 2   # Example: eat / apple / Beijing

class SGNS(nn.Module):
    def __init__(self):
        super().__init__()
        self.in_emb = nn.Embedding(V, D)
        self.out_emb = nn.Embedding(V, D)

    def forward(self, center, pos, neg):
        v = self.in_emb(center)
        u_pos = self.out_emb(pos)
        u_neg = self.out_emb(neg)

        pos_loss = -F.logsigmoid(torch.sum(v * u_pos, dim=1))
        neg_loss = -F.logsigmoid(-torch.sum(v * u_neg, dim=1))

        return (pos_loss + neg_loss).mean()
```

This example shows that:

* One loss function acts on several kinds of vectors at the same time.
* Each update touches only the vector rows used by the current example.

---

## Summary

* One-hot is only a discrete index and contains no semantics.
* The goal of distributed representations is to use low-dimensional dense vectors to characterize patterns of word use.
* Distributed representations can be built through count-based methods or prediction-based methods.
* Skip-gram + Negative Sampling turns word-vector learning into a problem of distinguishing positive and negative examples.
* One training objective drives learning for both input and output vectors.
* Through iterative updates over many examples, the semantic structure of words naturally forms in vector space.
