# LLMs for Backend Engineers

[![Read Online](https://img.shields.io/badge/Read%20Online-LLMs%20for%20Backend%20Engineers-16a34a?style=flat-square&logo=googlechrome&logoColor=white&maxAge=0)](https://kingson4wu.github.io/LLMs-for-Backend-Engineers/book/)
[![GitHub](https://img.shields.io/badge/GitHub-kingson4wu/LLMs-for-Backend-Engineers-24292e?style=flat-square&logo=github&logoColor=white)](https://github.com/kingson4wu/LLMs-for-Backend-Engineers)

一本帮助后端工程师从工程视角理解大型语言模型的书稿。不讲模型原理推导，讲系统设计和工程权衡；不讲学术理论，讲运行机制和实际限制；不讲工具罗列，讲架构原则和模式判断。

<table>
  <tr>
    <td align="center" valign="top" width="50%">
      <a href="https://kingson4wu.github.io/LLMs-for-Backend-Engineers/book/">
        <img src="./book/assets/cover.svg" alt="LLMs for Backend Engineers" width="280">
      </a>
      <br>
      <strong>LLMs for Backend Engineers</strong>
      <br>
      <a href="https://kingson4wu.github.io/LLMs-for-Backend-Engineers/book/">在线阅读</a>
    </td>
  </tr>
</table>

本书的核心立场：

> 把 LLM 当作**概率系统**来理解，而不是当作"推理实体"。

后端工程师每天都在和数学打交道——处理金额时要做精度归一化、设计限流算法时要分析收敛性、配置超时重试时要理解指数退避。这些看似和 AI 无关的工作，背后其实是同一套数学思维。本书从这套思维出发，帮你建立起对 LLM 工作方式的直觉。

## 三层内容架构

本书按技术栈层次分为三层，由底向上建立知识体系：

### 第一层：数学与机器学习基础

与具体模型无关的数学与机器学习基础概念。按依赖顺序排列：
AI数学精要 → 向量点积与夹角 → Softmax → 激活函数 → 感知机 → 交叉熵损失 → 反向传播 → 梯度消失与爆炸 → LayerNorm → Embedding 原理

### 第二层：LLM 内部机制

深入 LLM 的内部工作原理。按依赖顺序排列：
Embedding 演化 → Transformer 架构 → Attention 机制 → Token 生成与采样 → 微调与蒸馏 → 优化器选择 → AI系统工程实践

### 第三层：LLM 与外部系统的连接

LLM 如何与外部世界交互：
RAG 与知识库、外部工具调用

## 目标读者

- 有工程背景但无 AI 基础的后端工程师
- 想要理解 LLM 内部原理的开发者
- 对 LLM 应用架构感兴趣的架构师
- 想要从系统层面思考 LLM 的任何人

## 阅读建议

- 无 ML 背景 → 从第一层开始，按顺序阅读
- 有 ML 基础 → 从第二层开始，按顺序阅读
- 关注应用落地 → 从第三层开始，按需补充第二层前置知识

## 本地构建

```bash
cd book
npm install
npm run build
python3 ../tools/book-kit/build_honkit.py
```

最终输出在 `book/_book/`。

详细构建说明见 [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)。

---

<sub>Keywords: Large Language Models, Backend Engineering, LLM Architecture, Transformer, Attention, RAG, Agent System, Engineering Practices</sub>
