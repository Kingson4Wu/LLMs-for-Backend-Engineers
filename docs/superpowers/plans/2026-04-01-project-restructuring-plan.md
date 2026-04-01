# 项目全面重构实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 重构文档侧边栏为三层架构，重写入口页面，固化写作标准，审视全部现有文章。

**Architecture:** 按三层技术栈（数学基础 → LLM内部机制 → 外部系统连接）重组侧边栏分类；入口页面改为三层导航；新增 CONTRIBUTING.md 固化风格标准；审视并修正全部现有文章中的格式与语气问题。

**Tech Stack:** Docusaurus, TypeScript (sidebars.ts)

---

## 文件变更总览

```
修改: documentation/sidebars.ts          # 三层侧边栏结构
修改: documentation/docs/intro.md         # 改为三层导航入口
修改: documentation/docs/chapters/chapter1.md  # 三层结构入口
新建: documentation/CONTRIBUTING.md       # 写作标准
审视: documentation/docs/math_foundations/  # 全部8篇
审视: documentation/docs/advanced_transformer/ # 全部6篇
审视: documentation/docs/embeddings/     # 全部2篇
审视: documentation/docs/chapters/vector_concepts/ # 1篇
审视: documentation/docs/chapters/chapter4.md
```

---

## 第一阶段：固化标准

### Task 1: 创建 CONTRIBUTING.md

**Files:**
- Create: `documentation/CONTRIBUTING.md`

- [ ] **Step 1: 写入 CONTRIBUTING.md**

```markdown
# 贡献指南

## 写作标准

**风格底线（不可违背）：**
1. **语气中性** — 无主观评价、无情绪化词汇（"小儿科"、"废话"、"震惊"等）
2. **受众意识** — 假设读者是写了5年代码但从没接触过AI的后端工程师
3. **直觉优先** — 先建立工程感知，数学形式化作为补充而非门槛

**结构建议（按需调整，不强制套用）：**
- 问题先行：为什么需要这个概念
- 原理展开：工程直觉 + 类比
- 形式化（可选）：数学定义 / 代码示例
- 小结（推荐）：核心要点
- 延伸阅读（推荐）：内部链接 + 外部论文

**核心原则：新文章混入现有文章后，读者不应能分辨出作者不同。**

## 文章分类规则

按三层架构分类：

- **第一层：数学与机器学习基础** — 与具体模型无关的基础概念
- **第二层：LLM 内部机制** — Transformer、Attention、生成过程等
- **第三层：LLM 与外部系统的连接** — RAG、外部工具调用等

详见 [三层架构设计](../docs/superpowers/specs/2026-04-01-project-restructuring-design.md)。

## 文章排序规则

同层文章按前置依赖排序（见侧边栏顺序）。新增文章时，确认其依赖已在同层前置位置存在。

## 格式规范

- 数学公式使用 Unicode 数学符号（÷ × · Σ √ ≤ ≥ ← → θ π λ）而非 LaTeX 命令
- Markdown 标题层级清晰，最高为 `##`
- 代码块注明语言类型
```

- [ ] **Step 2: 提交**

```bash
git add documentation/CONTRIBUTING.md
git commit -m "docs: add CONTRIBUTING.md with writing standards

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 第二阶段：侧边栏重构

### Task 2: 重构 sidebars.ts 为三层结构

**Files:**
- Modify: `documentation/sidebars.ts`

- [ ] **Step 1: 用新三层结构替换原有分类**

将现有 `sidebars.ts` 中的 `bookSidebar` 数组内容替换为：

```typescript
const sidebars: SidebarsConfig = {
  bookSidebar: [
    'intro',
    // ========== 第一层：数学与机器学习基础 ==========
    {
      type: 'category',
      label: '第一层：数学与机器学习基础',
      items: [
        'math_foundations/ai-math-essentials',
        'chapters/vector_concepts/dot_product_angle',
        'math_foundations/softmax',
        'math_foundations/activation-functions',
        'math_foundations/perceptron-learning',
        'math_foundations/cross-entropy',
        'math_foundations/backpropagation',
        'math_foundations/vanishing-exploding-gradients',
        'math_foundations/layer-norm',
        'embeddings/from-onehot-to-embedding',
      ],
    },
    // ========== 第二层：LLM 内部机制 ==========
    {
      type: 'category',
      label: '第二层：LLM 内部机制',
      items: [
        'embeddings/embedding-evolution',
        'advanced_transformer/transformer_architecture',
        'advanced_transformer/attention_mechanism',
        'advanced_transformer/llm_generation',
        'advanced_transformer/fine-tuning-and-distillation',
        'advanced_transformer/optimizer-selection',
        'advanced_transformer/ai_engineering_practices',
      ],
    },
    // ========== 第三层：LLM 与外部系统的连接 ==========
    {
      type: 'category',
      label: '第三层：LLM 与外部系统的连接',
      items: [
        'chapters/chapter4',
        {
          type: 'link',
          label: '外部工具调用（待补充）',
          href: '#',
        },
      ],
    },
  ],
};
```

- [ ] **Step 2: 验证 Docusaurus 构建**

```bash
cd documentation && npm run build 2>&1 | tail -20
```
预期：构建成功，无错误

- [ ] **Step 3: 提交**

```bash
git add documentation/sidebars.ts
git commit -m "refactor: restructure sidebars.ts into three-layer taxonomy

- Layer 1: Math & ML foundations (10 articles)
- Layer 2: LLM internal mechanisms (7 articles)
- Layer 3: LLM ↔ external systems (2 items)

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 第三阶段：入口页面重构

### Task 3: 重写 intro.md

**Files:**
- Modify: `documentation/docs/intro.md`

- [ ] **Step 1: 写入新 intro.md**

将文件内容替换为（保留原有导航信息，去除免责声明）：

```markdown
---
sidebar_label: '简介'
sidebar_position: 1
---

# LLMs for Backend Engineers

欢迎阅读《LLMs for Backend Engineers》。本书旨在帮助后端工程师从工程视角理解大型语言模型的原理、实现和最佳实践——不是为了训练模型，而是为了在实际系统中用好模型。

## 三层内容架构

本书按技术栈层次分为三层，由底向上学习：

### 第一层：数学与机器学习基础

与具体模型无关的基础概念。按依赖顺序排列：
- AI数学精要 → 向量点积与夹角 → Softmax → 激活函数 → 感知机 → 交叉熵损失 → 反向传播 → 梯度消失与爆炸 → LayerNorm → Embedding 原理

### 第二层：LLM 内部机制

深入 LLM 的内部工作原理。按依赖顺序排列：
- Embedding 演化 → Transformer 架构 → Attention 机制 → Token 生成与采样 → 微调与蒸馏 → 优化器选择 → AI系统工程实践

### 第三层：LLM 与外部系统的连接

LLM 如何与外部世界交互：
- RAG 与知识库
- 外部工具调用（待补充）

## 目标读者

- 有工程背景但无 AI 基础的后端工程师
- 想要理解 LLM 内部原理的开发者
- 对 LLM 应用架构感兴趣的架构师

## 阅读建议

如果完全没有机器学习背景，**从第一层开始**——那里建立的直觉会让你在阅读后续章节时事半功倍。如果已有基础，可以直接跳到最感兴趣的部分。

## 设计哲学

把 LLM 当作**概率系统**来理解，而不是当作"推理实体"。模型不"思考"，模型只是在一个巨大的概率空间里找最可能的下一步。这种视角会让你对 LLM 的能力、局限和工程权衡有更清醒的判断。

## 参与贡献

参见 [CONTRIBUTING.md](../CONTRIBUTING.md)。
```

- [ ] **Step 2: 提交**

```bash
git add documentation/docs/intro.md
git commit -m "refactor: rewrite intro.md with three-layer navigation

- Remove disclaimer
- Add three-layer architecture overview
- Update reading path guidance

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

### Task 4: 重写 chapter1.md

**Files:**
- Modify: `documentation/docs/chapters/chapter1.md`

- [ ] **Step 1: 写入新 chapter1.md**

将文件内容替换为：

```markdown
---
sidebar_label: '第一章: 三层内容架构'
sidebar_position: 1
---

# 第一章: 三层内容架构

本章介绍本书的内容组织方式。三层架构的设计原则是：**按技术栈层次而非主题分组**，由底向上建立知识体系。

## 三层结构

### 第一层：数学与机器学习基础

与具体模型无关的数学与机器学习基础概念。包括：向量运算、Softmax、激活函数、感知机、交叉熵损失、反向传播、梯度消失与爆炸、LayerNorm、Embedding 原理。

这些概念是理解第二层和第三层的前置知识。

### 第二层：LLM 内部机制

深入 LLM 的内部工作原理。包括：Embedding 在上下文中的演化、Transformer 架构、Attention 机制、Token 生成与采样、微调与蒸馏、优化器选择、AI系统工程实践。

理解第二层内容后，你将能从工程视角解释 LLM 为什么产生当前的输出。

### 第三层：LLM 与外部系统的连接

LLM 与外部世界的交互方式。包括：RAG 与知识库、外部工具调用（待补充）。

这一层面向实际系统集成，是将 LLM 落地为可用服务的工程基础。

## 阅读路径建议

```
无 ML 背景 → 从第一层开始，按顺序阅读
有 ML 基础 → 从第二层开始，按顺序阅读
关注应用落地 → 从第三层开始，按需补充第二层前置知识
```

## 内容状态说明

部分章节仍在补充中。每篇文章右上角标注有更新状态。
```

- [ ] **Step 2: 提交**

```bash
git add documentation/docs/chapters/chapter1.md
git commit -m "refactor: rewrite chapter1.md as three-layer architecture entry

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

（Task 5 已删除：chapter2/3/5/6 不再保留，原有框架性章节结构已被三层架构替代）

## 第四阶段：审视全部现有文章

审视范围覆盖以下目录所有 `.md` 文件：

```
documentation/docs/math_foundations/       8篇
documentation/docs/advanced_transformer/  6篇
documentation/docs/embeddings/            2篇
documentation/docs/chapters/vector_concepts/  1篇
documentation/docs/chapters/chapter4.md   1篇
```

审视标准（三项全部检查）：

| 检查项 | 处理方式 |
|--------|---------|
| 主观修辞 | 删除情绪化词汇（"小儿科"、"废话"、"震惊"等）|
| LaTeX损坏 | 将 `frac`、`cdot` 等无反斜杠命令转为 Unicode 符号 |
| 结构完整性 | 确认存在 `## 小结` 和 `## 延伸阅读`，如缺失则补充 |

### Task 6: 审视 math_foundations 全部8篇

**Files:**
- Review: `documentation/docs/math_foundations/softmax.md`
- Review: `documentation/docs/math_foundations/activation-functions.md`
- Review: `documentation/docs/math_foundations/cross-entropy.md`
- Review: `documentation/docs/math_foundations/perceptron-learning.md`
- Review: `documentation/docs/math_foundations/backpropagation.md`
- Review: `documentation/docs/math_foundations/vanishing-exploding-gradients.md`
- Review: `documentation/docs/math_foundations/layer-norm.md`
- Review: `documentation/docs/math_foundations/ai-math-essentials.md`

- [ ] **Step 1: 逐一读取并修正**

对每篇文章：
1. 全文扫描情绪化词汇，替换为中性表达
2. 扫描 `$...$` 中的 LaTeX 命令，修复损坏的命令（`\frac` → `÷`，`\cdot` → `·`，`\sum` → `Σ` 等）
3. 确认文末有 `## 小结` 和 `## 延伸阅读`；如缺失，在文末补充
4. 如有修改则追加 commit（每篇一个 commit）

- [ ] **Step 2: 批量提交（如有多篇修改）**

```bash
git add documentation/docs/math_foundations/
git commit -m "docs: review math_foundations for tone, LaTeX, structure

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

### Task 7: 审视 advanced_transformer 全部6篇

**Files:**
- Review: `documentation/docs/advanced_transformer/transformer_architecture.md`
- Review: `documentation/docs/advanced_transformer/attention_mechanism.md`
- Review: `documentation/docs/advanced_transformer/llm_generation.md`
- Review: `documentation/docs/advanced_transformer/fine-tuning-and-distillation.md`
- Review: `documentation/docs/advanced_transformer/optimizer-selection.md`
- Review: `documentation/docs/advanced_transformer/ai_engineering_practices.md`

- [ ] **Step 1: 逐一读取并修正**（同上三项检查）

- [ ] **Step 2: 批量提交**

```bash
git add documentation/docs/advanced_transformer/
git commit -m "docs: review advanced_transformer for tone, LaTeX, structure

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

### Task 8: 审视 embeddings 全部2篇 + vector_concepts 1篇 + chapter4

**Files:**
- Review: `documentation/docs/embeddings/from-onehot-to-embedding.md`
- Review: `documentation/docs/embeddings/embedding-evolution.md`
- Review: `documentation/docs/chapters/vector_concepts/dot_product_angle.md`
- Review: `documentation/docs/chapters/chapter4.md`

- [ ] **Step 1: 逐一读取并修正**（同上三项检查）

- [ ] **Step 2: 批量提交**

```bash
git add \
  documentation/docs/embeddings/ \
  documentation/docs/chapters/vector_concepts/ \
  documentation/docs/chapters/chapter4.md
git commit -m "docs: review embeddings, vector_concepts, chapter4 for tone, LaTeX, structure

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```

---

## 第五阶段：最终验证

### Task 9: 构建验证

- [ ] **Step 1: 运行 Docusaurus 构建**

```bash
cd documentation && npm run build 2>&1 | tail -30
```
预期：构建成功，输出中无 error

- [ ] **Step 2: 提交**

```bash
git add -A
git commit -m "chore: verify build passes after restructuring

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
```
