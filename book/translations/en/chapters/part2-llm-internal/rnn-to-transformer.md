# From RNNs to Transformers: A Structural Change in Sequence Modeling

## The Difficulty of Modeling Natural Language

Natural-language processing is difficult not because individual words are unusual objects, but because words must form a meaningful whole. Sentence meaning is often determined jointly by components separated by long distances and constrained by syntax and semantics. A subject and verb may be divided by several clauses, yet their relationship remains essential to understanding the sentence.

Natural-language modeling is therefore fundamentally a sequence-modeling problem: at any position, a model must make sensible use of information from other positions in the sequence, especially information that is distant but semantically decisive.

---

## Separating Representation from Structure: Start with Word Vectors

Before neural networks entered NLP, words were discrete symbols that computers could not directly process. Word-vector models such as word2vec use the distributional hypothesis to map words into continuous vector spaces, placing semantically similar words near one another and providing neural networks with computable input representations.

This solves how to represent a word as a vector: discrete tokens become vectors that can be computed on, compared for similarity, and combined. But a word vector does not understand language structure; it contains no order, dependency, or syntax. At the embedding layer, “dog bites man” and “man bites dog” differ very little. Word vectors are therefore the representation layer, while later sequence models must model structure and dependencies.

---

## RNNs: Expressing a Sequence with State

Recurrent neural networks (RNNs) were among the first neural architectures to handle sequence data systematically. Their central idea is intuitive: treat a sequence as a process that advances in time, use a hidden state to absorb historical information continuously, and determine the next state from both the current input and that history.

The hidden state is treated as “all memory so far,” with sequence information progressively compressed into one vector. This can work well for short sequences with simple dependencies. In natural language, however, the design gradually exposes fundamental limits.

---

## Encoders and the Limits of a Fixed-Length Vector

Early encoder–decoder translation systems made this especially visible: an encoder compressed a variable-length source into a fixed vector before a decoder generated output. This design was attractive in engineering terms: it offered a uniform interface and a simple structure, and seemed to fit the intuition that a sentence has one overall meaning.

But it assumes that a fixed-dimensional vector can retain everything decoding needs for inputs of arbitrary length and complexity. Entities, relations, and hierarchical structure grow with the input, making the fixed-capacity channel a representational and optimization bottleneck in practice; important information can be overwritten or become hard to recover.

---

## LSTMs: A Better Recurrent Memory

As RNNs were applied to longer sentences, more complex translation, and generation, a recurrent problem emerged: they struggled to retain long-distance information reliably. During training, gradients can gradually vanish or explode along long sequences, weakening the influence of early input on later output; at the same time, a fixed-dimensional hidden state is continually overwritten, so important early information is easily lost.

LSTMs (and later GRUs) were proposed in this context. They retain the overall recurrent framework but strengthen the internal memory structure with an explicit memory channel and gates that control writing, retention, and reading. This makes it easier to preserve important information over longer spans during training.

LSTMs still inherit the RNN's structural premise: all history must ultimately pass through a finite-dimensional state, and information is used through sequential access. They substantially ease the training difficulty of “not remembering,” but do not fundamentally change the structural limits of fixed capacity plus sequential transmission.

---

## Recurrent Structural Bottlenecks

The first core problem is limited representational capacity. Hidden-state width is fixed while input length can vary and grow. As new information arrives, important early information can be overwritten and representation capacity can saturate.

The second problem is a long dependency path. A remote dependency must travel through step-by-step state transfer, so its path grows linearly with sequence length. Information passes through many nonlinear transformations before reaching its target, diluting remote signals and worsening the risk of unstable gradients during training.

The third problem is limited access. When an RNN or LSTM needs information from a much earlier token, it cannot read that position directly; it can only rely on the residual trace left by repeated transmission. It is therefore difficult to “look back on demand,” much less retrieve flexibly for different contexts.

---

## CNNs: Parallel Local Pattern Modeling

CNNs are known for parallel efficiency and their ability to capture local patterns. Their use in sequence modeling was motivated by two practical aims: escaping RNNs' strict temporal dependence to improve training and inference parallelism, and using convolutions' strong inductive bias for local n-gram structures to extract short-range patterns efficiently.

In text, CNNs typically use local convolutions for short-range features, then stack layers to expand their view in hopes of covering longer context. This offers a route that can combine speed with local-structure modeling.

---

## Receptive Fields Are Not Dynamic Retrieval

The receptive field is the portion of the input that can affect a position’s representation. An ordinary local convolution can inspect only a limited window; without changing kernel size, stride, or using designs such as dilated convolution, covering greater distance requires more layers. Expansion of the receptive field and transmission paths for remote information remain architectural trade-offs.

More importantly, even if a receptive field theoretically covers a whole sentence, remote information must cross many nonlinear transformations before it reaches a target position. Longer distances usually mean more layers, more attenuation, and further dilution of long-distance contributions.

In addition, a convolutional window is fixed and cannot change whom to inspect according to the current semantic need. Language dependencies are sparse and structured: a word may need one distant subject or antecedent, rather than several nearby words. CNNs' local fixed-window mechanism does not provide this context-dependent selective access.

---

## Long-Distance Dependencies: The Limit of Sequence Modeling

Natural-language dependencies have three notable properties: they are sparse in the whole sequence but crucial when present; their importance does not decay monotonically with distance, but follows syntactic and semantic structure; and they are dynamic, so different positions need different historical information in different contexts.

RNNs, LSTMs, and CNNs share the problem that they use a fixed structure to decide in advance how information will be compressed or propagated: history is compressed into finite state or a local stack passively expands the view. This conflicts fundamentally with the selective and dynamic nature of language dependencies.

---

## Attention: Preserve Positions, Then Select

Attention marked a decisive turn in sequence modeling. Rather than compressing all history into one fixed vector, attention retains intermediate representations at every position and uses learnable weights to select and combine historical information when the current task needs it.

The model no longer relies on one memory state. From the current context, it dynamically decides whom to inspect and by how much. Attention acts as a learnable soft pointer that directly accesses the parts most relevant to a prediction, substantially shortening information paths and easing the bottleneck of fixed-length representations.

---

## Transformer: Global Access and Parallel Computation

Transformers are built on attention. They abandon a time-step-centered recurrent structure and use self-attention to model global dependencies. Any two positions can establish a direct relationship, so dependency-path length no longer grows with sequence length.

Because known input positions no longer depend on the previous time step's hidden state, their attention weights can be computed in parallel. This makes training highly efficient on GPUs and makes large models trained on vast data feasible; autoregressive inference must still generate each unknown next token step by step. Self-attention retains position representations for later layers and selects among them with weights; it does not guarantee lossless preservation of raw information, but it shortens paths for forming dependencies.

---

## Summary

From word vectors to sequence models, the problem moves from how to represent words as vectors to how words form structured meaning. RNNs carry history in recurrent state; LSTMs use gates to improve memory retention; CNNs offer a parallel route based on convolutional stacks and local patterns. Yet they share structural limits: either they compress into fixed-capacity state or rely on fixed windows and passive multilayer propagation, making sparse but important long-distance dependencies hard to access dynamically and directly.

Transformers change that premise. They preserve representations at all positions in each layer and use self-attention to assign dependency weights dynamically, directly accessing important information; computation over known input positions can also run in parallel, making deeper and larger models trainable with large-scale data and compute. This shift from sequential transmission to global access and dynamic selection is the central thread in the evolution of sequence-modeling paradigms.

---

## Key Takeaways

### 1. The Core Problem

Natural language's long-distance dependencies are **sparse, non-monotonic, and dynamic**. These properties fundamentally conflict with the fixed structural assumptions of traditional sequence models.

### 2. Two Paradigms

- **Compression and transmission** (RNN/LSTM): compress history into a fixed-dimensional state, like summarizing an entire book in one sentence.
- **Selective access** (Transformer): retain representations of all positions, dynamically compute attention weights to decide whom to inspect and by how much, then extract weighted information—like retaining the whole book and focusing on relevant chapters when needed.

### 3. Dependency Paths

The shortest dependency path between two positions in one layer is one factor in long-range modeling: RNN/LSTM paths are $O(n)$ in distance; CNN paths depend on kernel, dilation, and depth; global Transformer self-attention has an $O(1)$ path. This describes path length, not computational cost or a guarantee of capability.

### 4. Structural Bottlenecks

- **RNN/LSTM:** fixed capacity versus variable sequences → a representation bottleneck.
- **CNN:** fixed windows versus sparse dependencies → restricted access.
- **Transformer:** global attention → efficient parallelism, with $O(n^2)$ complexity.

### 5. The Paradigm Shift

The shift is from asking “how can compression be improved?” (LSTM's engineering optimization) to “is compression necessary?” (attention's structural innovation). The latter produced the fundamental breakthrough in sequence modeling.
