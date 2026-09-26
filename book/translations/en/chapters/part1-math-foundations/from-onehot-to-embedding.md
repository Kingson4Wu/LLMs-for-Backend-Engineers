# From One-Hot to Embeddings: How Discrete Tokens Become Vectors

In language tasks, a model starts with discrete symbols such as words and subwords, while neural-network computation happens on continuous numbers. That creates a simple question: how can a discrete token become a numeric vector that still reflects differences in how tokens are used?

An embedding is an answer to that question. It does not put a definition of meaning into a number. Instead, it lets a model learn a parameter table from large amounts of text: tokens that occur in similar contexts can acquire representations that later computation can use. The most direct encoding makes a useful starting point.

## One-Hot: One Position for Each Token

Let a vocabulary contain V tokens. A one-hot representation gives every token a V-dimensional vector, with 1 only at that token's position and 0 everywhere else:

~~~text
Vocabulary: [I, love, you, China, Beijing]

Beijing -> [0, 0, 0, 0, 1]
China   -> [0, 0, 0, 1, 0]
~~~

It answers exactly which vocabulary item is present. It says nothing about the relationship between Beijing and China: two distinct one-hot vectors have dot product 0 and cosine similarity 0. As the vocabulary grows, the vector grows with it, even though almost every position remains 0.

One-hot is therefore best treated as a conceptual model for indexing. Programs normally pass a token ID. If x_i is the one-hot row vector for ID i and E is an embedding matrix, x_i E simply selects row i of E. A framework implements that multiplication as a lookup, without constructing a long sparse vector.

## Learn Relations from Co-Occurrence

People often understand a word through the sentences around it. Apple occurs with eat, fruit, and sweet; banana appears in similar surroundings. Server more often appears with request, deployment, and latency. These co-occurrence patterns give a model material from which to learn representations.

A distributed representation does not reserve one dimension for each word. A shorter dense vector jointly carries many statistical features. Tokens occurring in similar contexts often obtain related representations, but that is a statistical relation under particular data and training objectives. A coordinate is not a word definition, and nearby vectors do not guarantee that two words are interchangeable in every task.

Early word-vector methods followed two common routes. One first counts word-context co-occurrences and then transforms or reduces the matrix. The other writes context prediction as a training objective and directly learns vector parameters. Word2Vec Skip-gram takes the latter route. It makes the path from text to vectors especially visible, which is why it is a useful example here.

## Embedding: A Lookup Table That Learns

Let V be vocabulary size and d be vector dimension. An embedding is a learnable matrix $E \in \mathbb{R}^{V \times d}$: each row belongs to one token, while each column is one numeric dimension of that row's representation.

~~~text
token ID i
   ↓
select row i of E
   ↓
[0.12, -0.45, 0.78, ...]  # d numbers
~~~

At initialization, those numbers usually contain no interpretable structure. Training adjusts them so that they help the model meet its objective. The embedding layer is therefore both plain—a lookup by ID—and important: attention, feed-forward layers, and output prediction all continue from these input representations.

## What Does It Mean for Vectors to Be Close?

Two common comparisons are dot product and cosine similarity:

$$
\text{dot}(a,b)=a \cdot b, \qquad
\cos(a,b)=\frac{a \cdot b}{\lVert a \rVert\lVert b \rVert}
$$

A dot product depends on both vector length and angle. Even when direction stays fixed, making a vector longer raises its dot product. Cosine similarity removes length and compares direction only. A larger dot product can be read directly as closer direction only after normalization or when vector lengths are controlled.

For that reason, “these token vectors are close” has no meaning apart from its context. It says only that a model found a reusable statistical relation at one layer, on one dataset, under one training objective. Continue with [dot products and cosine similarity](dot-product-angle.md) for the geometry behind these scores.

## How Skip-Gram Gets Examples from a Sentence

Take “Beijing is the capital of China.” Use Beijing as a center word and inspect a nearby window. This yields pairs such as Beijing-is and Beijing-China. They tell the model that these tokens occurred together in a local context in this corpus.

Skip-gram has a simple idea: assign a vector to the center word and give it a higher score with genuine context words. Standard training keeps two independent tables:

| Table | What it represents | Common symbol |
| --- | --- | --- |
| Input table | The center token | $v_c$ |
| Output table | A candidate context token | $u_o$ |

The same token has two parameter vectors because predicting surrounding content from a center and being scored as a candidate context are different roles. After training, a system may use the input table, the output table, or a combination; no one table is universally best for every task.

## Negative Sampling: Avoid Comparing the Whole Vocabulary

Comparing every center word with all V vocabulary items would be expensive. Negative sampling keeps an observed context word as a positive example and draws a small number of tokens from a noise distribution as negative examples.

For example, Beijing-China is a positive pair, while Beijing-banana may be a negative example in one update. The negative example does not claim that the words can never occur together. It is a control constructed for training. The model learns to assign observed pairs higher scores and sampled controls lower scores.

For center word c, observed context word o, and k negative samples n_i, one example has loss:

$$
L = -\log \sigma(v_c \cdot u_o)
    - \sum_{i=1}^{k}\log \sigma(-v_c \cdot u_{n_i})
$$

Minimizing the first term raises the dot product for an observed pair. Minimizing the second lowers dot products for sampled negative pairs. Mikolov and colleagues introduced this approximate objective to make Skip-gram training efficient. Their [original paper](https://arxiv.org/abs/1310.4546) also notes that static word vectors do not preserve word order or express every phrase meaning.

## Which Vectors Change in One Update?

For Beijing-China and several negative samples, backpropagation directly gives gradients to three kinds of vectors: the input vector for Beijing, the output vector for China, and output vectors for the sampled negatives. A word absent from that example receives no direct gradient from this lookup.

~~~text
Text corpus
  ↓
Sliding window yields (center, context) pairs
  ↓
Draw a few negative samples
  ↓
Raise scores for observed pairs and lower scores for negative pairs
  ↓
Backpropagation updates the rows accessed in this example
~~~

A batch updates the union of rows used by its examples. This describes gradients directly produced by the loss. Momentum, weight decay, and other optimizer behavior can expand the set of parameters that actually change.

## The Training Loop in a Small Piece of Code

The following code omits corpus loading and the negative-sampling distribution. It keeps only how one batch updates two tables. It uses SGD without weight decay so the code corresponds directly to the loss above.

~~~python
import torch
import torch.nn.functional as F

V, D = 10000, 256

class SGNS(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.in_emb = torch.nn.Embedding(V, D)
        self.out_emb = torch.nn.Embedding(V, D)

    def forward(self, center, positive, negatives):
        v = self.in_emb(center)
        u_pos = self.out_emb(positive)
        u_neg = self.out_emb(negatives)

        positive_loss = -F.logsigmoid((v * u_pos).sum(dim=1))
        negative_scores = (v.unsqueeze(1) * u_neg).sum(dim=-1)
        negative_loss = -F.logsigmoid(-negative_scores).sum(dim=1)
        return (positive_loss + negative_loss).mean()

model = SGNS()
optimizer = torch.optim.SGD(model.parameters(), lr=0.05)

center = torch.tensor([3, 6])
positive = torch.tensor([8, 2])
negatives = torch.tensor([[17, 21, 34], [9, 13, 55]])

loss = model(center, positive, negatives)
optimizer.zero_grad()
loss.backward()
optimizer.step()
~~~

PyTorch Embedding is this kind of lookup module. Sparse-layout gradients require explicit configuration and a compatible optimizer; that affects how a framework executes updates, not the training logic here. The [PyTorch Embedding documentation](https://docs.pytorch.org/docs/stable/generated/torch.nn.Embedding.html) describes the interface.

## From Word Vectors to Transformers

Word2Vec learns one static vector for every token. Apple starts from the same vector in “eat an apple” and “Apple Inc.” A Transformer also starts from an input lookup, but every attention layer rewrites the representation using the other tokens in the current sentence. The hidden state used to predict the next token is therefore contextual, not merely the initial embedding.

That is why Word2Vec remains useful to learn. It separates a larger chain into visible steps: a discrete ID becomes a vector through lookup, a loss and gradient shape the table during training, and later models organize richer computation over those vectors.

## Further Reading

- [Dot Products and Cosine Similarity](dot-product-angle.md) — separating vector length, direction, and score
- [Backpropagation](backpropagation.md) — how loss becomes parameter updates
- [From Word2Vec to Transformers: The Changing Role of Embeddings](../part2-llm-internal/embedding-evolution.md) — how static vectors become contextual representations
