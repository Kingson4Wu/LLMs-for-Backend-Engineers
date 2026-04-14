# LLMs for Backend Engineers

[中文 README](./README.zh-CN.md)

[![Read Online](https://img.shields.io/badge/Read%20Online-LLMs%20for%20Backend%20Engineers-16a34a?style=flat-square&logo=googlechrome&logoColor=white)](https://kingson4wu.github.io/LLMs-for-Backend-Engineers/)
[![GitHub](https://img.shields.io/badge/GitHub-kingson4wu%2FLLMs--for--Backend--Engineers-24292e?style=flat-square&logo=github&logoColor=white)](https://github.com/kingson4wu/LLMs-for-Backend-Engineers)

A book that helps backend engineers understand large language models from an engineering perspective. No derivations, no theory for its own sake — just system design, trade-offs, how LLMs actually work, and real constraints.

<table>
  <tr>
    <td align="center" valign="top" width="50%">
      <a href="https://kingson4wu.github.io/LLMs-for-Backend-Engineers/">
        <img src="./book/assets/cover.svg" alt="LLMs for Backend Engineers" width="280">
      </a>
      <br>
      <strong>LLMs for Backend Engineers</strong>
      <br>
      <a href="https://kingson4wu.github.io/LLMs-for-Backend-Engineers/">Read online</a> ·
      <a href="https://kingson4wu.github.io/LLMs-for-Backend-Engineers/exported/book.pdf">Download PDF</a>
    </td>
  </tr>
</table>

The core position of this book:

> Understand LLMs as **probabilistic systems**, not as "reasoning entities".

Backend engineers work with math every day — normalizing decimal precision, analyzing convergence in rate-limiting algorithms, understanding exponential backoff for timeouts. These seem unrelated to AI, but they're the same mental toolkit. This book builds intuition for how LLMs actually work.

## Three-Layer Architecture

The book is organized in three layers, building up from foundations:

### Layer 1: Math & Machine Learning Foundations

Concepts independent of any specific model. Read in order:
AI Math Essentials → Dot Product & Vector Angles → Softmax → Activation Functions → Perceptron Learning → Cross-Entropy Loss → Backpropagation → Vanishing & Exploding Gradients → LayerNorm → From One-hot to Embedding

### Layer 2: LLM Internal Mechanisms

Deep dive into how LLMs work internally. Read in order:
Embedding Evolution → Transformer Architecture → Attention Mechanism → Token Generation & Sampling → Fine-tuning & Distillation → Optimizer Selection → AI Engineering Practices

### Layer 3: LLM & External Systems

How LLMs connect to the outside world:
RAG & Knowledge Bases, External Tool Calling

## Who This Book Is For

- Backend engineers with engineering background but no AI experience
- Developers who want to understand LLM internals
- Architects interested in LLM application design
- Anyone who wants to think about LLMs from a systems perspective

## Reading Path

- No ML background → start from Layer 1, read in order
- Have ML background → start from Layer 2, read in order
- Focused on application → start from Layer 3, supplement Layer 2 as needed

## Local Build

```bash
cd book
npm install
npm run build
python3 ../tools/book-kit/build_honkit.py
```

Output goes to `book/_book/`.

See [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md) for full build instructions.

---

<sub>Keywords: Large Language Models, Backend Engineering, LLM Architecture, Transformer, Attention, RAG, Agent System, Engineering Practices</sub>
