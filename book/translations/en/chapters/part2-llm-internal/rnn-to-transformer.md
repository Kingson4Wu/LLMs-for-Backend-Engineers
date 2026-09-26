# From RNNs to Transformers: A Structural Change in Sequence Modeling

Language is difficult not because a word is an unusual object, but because meaning depends on relations across a sequence. A subject and verb may be separated by clauses; a pronoun may depend on a distant entity. Sequence modeling must therefore use information from positions that can be far away while retaining order and context.

## Representation Is Not Sequence Structure

Word2vec-style embeddings turn discrete tokens into continuous vectors, giving neural networks something they can compute with. They do not themselves encode word order, syntax, or dependencies. At the embedding layer, “dog bites man” and “man bites dog” have nearly the same collection of token vectors. A later sequence model must establish their structure.

## RNNs: History as a Recurrent State

An RNN carries a hidden state forward one position at a time. That state is a running summary of history, updated from the preceding state and current input. It can work for short, simple sequences, but a fixed-width state is a demanding channel for inputs whose length and relational complexity can grow.

Early encoder–decoder translation systems made this especially visible: an encoder compressed a variable-length source into a fixed vector before a decoder generated output. The relevant assumption is not that compression is mathematically impossible, but that one fixed-capacity channel can preserve what decoding needs for arbitrary inputs. With many entities, relations, and levels of structure, important information can be overwritten or become hard to recover.

LSTMs and GRUs improve this recurrent design with explicit memory paths and gates controlling writes, retention, and reads. They make longer dependencies easier to train, but preserve the basic constraints: historical information still passes through finite state, and use of earlier information follows a sequential path.

## The Structural Bottlenecks

RNNs and LSTMs have three related limits. Their state capacity is fixed while sequences vary in length. A distant dependency travels through many intermediate updates, increasing the risk that useful signal is diluted and gradients become unstable. And when a later position needs a particular earlier token, it cannot directly revisit that position; it can only use what remains in the carried state.

CNNs offered a parallel alternative with strong local-pattern bias. A local convolution sees a limited window; deeper stacks, larger kernels, strides, or dilated convolutions expand its receptive field. These are useful design choices, but distant information still crosses multiple transformations, and a fixed local structure cannot choose a remote source dynamically from the current semantic need.

Language dependencies are often sparse, structurally important, and not determined by distance. A model may need a far-away subject rather than several nearby words. Fixed compression and fixed local propagation make that kind of selective access difficult.

## Attention: Preserve Positions, Then Select

Attention changes the premise. Instead of forcing all history into one vector, it retains representations for positions and computes a learned weighting over those relevant to the current computation. Queries describe what a position needs, keys describe what positions offer, and values carry the information to combine. This acts as a learned soft pointer: it does not guarantee lossless preservation, but it creates a direct route for relating positions.

## Transformer: Global Access and Parallel Computation

Transformers build sequence layers from self-attention. Any two visible positions can interact within one layer, so the shortest dependency path does not grow with their distance. Since known input positions do not depend on a prior recurrent state, their attention computations can be organized as parallel matrix operations on hardware such as GPUs.

Order still has to be supplied through a position mechanism; vectors alone have no intrinsic word order. For autoregressive generation, a causal mask prevents a position from reading future tokens. Training over known sequences can be parallel, while inference still generates unknown next tokens sequentially.

Dense attention is not free: its pairwise work and memory grow with sequence length. Its significance is the trade-off it established among direct context interaction, optimization, and parallel hardware—not a claim that long context has no cost.

## Summary

RNNs and LSTMs compress and pass history forward; CNNs propagate local information through a chosen structure. Transformers preserve position-wise representations and use attention for dynamic, direct selection. For a single layer, RNN/LSTM dependency paths scale with distance, CNN paths depend on kernel, dilation, and depth, and global self-attention creates an \(O(1)\) path. That compares information paths, not total computation cost or a guarantee of capability.
