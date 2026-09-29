# Part I: Mathematics and Machine Learning Foundations

Language models do not sit outside the laws of mathematics and machine learning. This part is organized around three questions: how information becomes vectors, how scores become probabilities, and how error changes parameters. Together they form one continuous computation chain:

On [the book’s main map](../index.md#the-books-main-map), this part is the start of learnable computation: it establishes the language of symbols, scores, and error used by later training and inference.

**tokens and context → vector representations → scores and probabilities → loss → gradient updates to parameters**

This chain explains how discrete symbols enter computation, how a model chooses among candidate outputs, and how training writes error back into parameters.

| Group | What to understand | Where to begin |
| --- | --- | --- |
| Overview and representation | How AI becomes an optimization problem and how discrete symbols become vectors | [AI math and machine learning](../chapters/part1-math-foundations/ai-math-foundations.md), one-hot and embeddings, dot products |
| Scores and choices | How scores become probabilities and why nonlinearity is necessary | Softmax and activation functions |
| Learning and stability | How error produces an update direction and why deep training becomes unstable | Perceptrons, cross-entropy, backpropagation, and gradients |

Read in catalog order or enter through the needed mechanism: representation chapters explain discrete symbols and vector relationships, probability chapters explain selection, and learning chapters explain parameter updates and training stability. By the end of this part, you should be able to explain why parameters can represent relationships and why training can change them along an error signal.
