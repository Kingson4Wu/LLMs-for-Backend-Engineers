
# LLMs for Backend Engineers

## 本地开发

本文档介绍如何在本地启动和开发《LLMs for Backend Engineers》电子书项目。

### 快速启动

项目提供了便捷的启动脚本：

**Linux/macOS:**
```bash
./start_docs.sh
```

**Windows:**
双击运行 `start_docs.bat`

启动后，电子书将可以通过 `http://localhost:3000/` 访问。

如需更多信息，请查看 [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)。

## 部署到 GitHub Pages

本项目支持将电子书部署到 GitHub Pages。

### 部署步骤

1. 构建项目：
```bash
cd documentation
npm run build
```

2. 部署到 GitHub Pages：
```bash
# 使用用户名部署
GIT_USER=<username> npm run deploy

# 或使用 SSH 方式
USE_SSH=true npm run deploy

# 或使用 GitHub Token
GITHUB_TOKEN=<token> npm run deploy
```

对于此项目，部署命令为：
```bash
GIT_USER=kingson4wu npm run deploy
```

部署后，电子书将在 `https://kingson4wu.github.io/LLMs-for-Backend-Engineers/` 可访问。

*A clear and practical guide to large language models*

## Overview

This book is written for **backend engineers** who want to understand Large Language Models (LLMs) from an **engineering perspective**.

It focuses on explaining **how LLMs actually work**, how they are used in real systems, and what their practical limitations are — without academic overload or hype-driven narratives.

No prior AI or machine learning background is required.

---

## Target Audience

This book is intended for:

* Backend engineers and system developers
* Software engineers integrating LLMs into production systems
* Engineers curious about LLMs but frustrated by vague or superficial explanations
* Developers who want to reason about LLMs as **systems**, not magic APIs

---

## What This Book Covers

* Core concepts behind LLMs (tokens, Transformer, attention, training, inference)
* Why LLMs behave the way they do
* Capability boundaries and common failure modes
* Retrieval-Augmented Generation (RAG) explained from first principles
* Tools, function calling, agents, and workflows — what’s real and what’s recycled
* Architectural patterns for LLM-based systems
* Engineering trade-offs in performance, cost, latency, and reliability

The emphasis is on **understanding and reasoning**, not memorization.

---

## What This Book Avoids

* Heavy mathematical derivations
* Academic paper walkthroughs
* Prompt “tricks” and copy-paste recipes
* Over-marketed AI concepts without technical substance

The goal is clarity, not evangelism.

---

## Structure

The book is roughly organized as:

1. What LLMs are — and what they are not
2. How LLMs generate language
3. Why LLMs seem intelligent (and where that illusion breaks)
4. Retrieval, tools, and agent-like systems
5. Designing real-world LLM applications
6. Pitfalls, myths, and common misunderstandings

Each section builds intuition progressively, using concrete examples and engineering analogies.

---

## Status

This project is a **work in progress**.

Content may be revised, reordered, or expanded as the system-level understanding evolves.

Thoughtful feedback and technical discussion are welcome.

---

## Design Philosophy

> Treat LLMs as probabilistic systems, not reasoning entities.

This book approaches LLMs the way backend engineers approach databases, caches, or distributed systems:
with skepticism, precision, and an emphasis on failure modes.

---


