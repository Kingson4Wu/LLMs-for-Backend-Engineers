# 数学基础模块实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 为 LLMs-for-Backend-Engineers 项目搭建数学基础模块，迁移并改写 11 篇参考博客文章，贯穿 3 个阶段。

**Architecture:** 纯文档项目，基于 Docusaurus。源文章来自 `kingson4wu.github.io.zh`，改写后放入 `documentation/docs/` 下新目录。侧边栏配置在 `sidebars.ts` 中更新。

**Tech Stack:** Docusaurus v3.9.2, TypeScript, Markdown

---

## 阶段概览

| 阶段 | 文章数 | 目录 |
|---|---|---|
| Phase 1: 数学基础线 | 8 | `docs/math_foundations/` |
| Phase 2: Embedding 桥接线 | 2 | `docs/embeddings/` |
| Phase 3: Transformer 深化 | 1 | `docs/advanced_transformer/` |

---

## 全局说明

**改写模板**（适用于每篇文章）：

```
## 本章要解决什么问题
   1~2段直觉/类比，工程比喻

## 这个工具/机制是怎么工作的
   简化流程描述 + ASCII 示意图（可选）

## 形式化（可选，附注）
   核心公式 + 1~2行代码示例

## 本章小结
   一句话总结，读者能带走的核心理解

## 延伸阅读
   指向本模块或其他模块的相关文章
```

**验证命令**（每个阶段完成后执行）：
```bash
cd documentation
npm run build
# 预期：build 成功，无 error
```

---

## Task 1: 初始化目录结构

**Files:**
- Create: `documentation/docs/math_foundations/`
- Create: `documentation/docs/embeddings/`

- [ ] **Step 1: 创建目录**

```bash
mkdir -p documentation/docs/math_foundations
mkdir -p documentation/docs/embeddings
```

---

## Task 2: Phase 1 — 数学基础线（8篇）

**源文件前缀:** `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/`

**Files:**
- Create: `documentation/docs/math_foundations/ai-math-essentials.md`
- Create: `documentation/docs/math_foundations/softmax.md`
- Create: `documentation/docs/math_foundations/activation-functions.md`
- Create: `documentation/docs/math_foundations/cross-entropy.md`
- Create: `documentation/docs/math_foundations/perceptron-learning.md`
- Create: `documentation/docs/math_foundations/backpropagation.md`
- Create: `documentation/docs/math_foundations/vanishing-exploding-gradients.md`
- Create: `documentation/docs/math_foundations/layer-norm.md`
- Modify: `documentation/sidebars.ts`（在 `基础概念` 之后插入 `数学基础` 分类）

---

### Task 2.1: ai-math-essentials.md

**源文件:** `AI数学精要.md`

- [ ] **Step 1: 读取源文件**

Read `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/AI数学精要.md`

- [ ] **Step 2: 改写内容**

按改写模板重构，定位为整个数学模块的入口/地图页。用段落介绍本模块涵盖哪些内容、它们之间的依赖关系、建议阅读顺序。

- [ ] **Step 3: 写入文件**

Write to `documentation/docs/math_foundations/ai-math-essentials.md`

- [ ] **Step 4: 提交**

```bash
cd /Users/kingsonwu/programming/kingson4wu/LLMs-for-Backend-Engineers
git add documentation/docs/math_foundations/ai-math-essentials.md
git commit -m "docs: add AI数学精要 as math module entry point"
```

---

### Task 2.2: softmax.md

**源文件:** `Softmax：从直觉到本质.md`

- [ ] **Step 1: 读取源文件**

Read `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/Softmax：从直觉到本质.md`

- [ ] **Step 2: 改写内容**

按改写模板重构。重点：softmax 把一组任意实数转成概率分布。直觉：就像后端系统里的"权重路由"——把多个分数归一化后决定选中哪个选项。在 Attention 机制中的作用要特别说明。

- [ ] **Step 3: 写入文件**

Write to `documentation/docs/math_foundations/softmax.md`

- [ ] **Step 4: 添加交叉引用**

在文章末尾 `延伸阅读` 中添加指向 `activation-functions.md`（因为 softmax 可看作一种激活函数）和 `backpropagation.md` 的链接。

- [ ] **Step 5: 提交**

```bash
git add documentation/docs/math_foundations/softmax.md
git commit -m "docs: add Softmax article to math foundations"
```

---

### Task 2.3: activation-functions.md

**源文件:** `激活函数的本质原理与作用.md`

- [ ] **Step 1: 读取源文件**

Read `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/激活函数的本质原理与作用.md`

- [ ] **Step 2: 改写内容**

按改写模板重构。直觉：激活函数就像 API 网关里的"条件路由"——决定一个请求是否放行/触发后续逻辑。重点讲清楚 Sigmoid、ReLU、Tanh 三种最常见的激活函数，不需要罗列全部。工程比喻要贯穿全程。

- [ ] **Step 3: 写入文件**

Write to `documentation/docs/math_foundations/activation-functions.md`

- [ ] **Step 4: 添加交叉引用**

在 `延伸阅读` 中添加指向 `perceptron-learning.md` 和 `vanishing-exploding-gradients.md` 的链接。

- [ ] **Step 5: 提交**

```bash
git add documentation/docs/math_foundations/activation-functions.md
git commit -m "docs: add activation functions article to math foundations"
```

---

### Task 2.4: cross-entropy.md

**源文件:** `交叉熵损失与最大似然估计：完全理解指南.md`

- [ ] **Step 1: 读取源文件**

Read `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/交叉熵损失与最大似然估计：完全理解指南.md`

- [ ] **Step 2: 改写内容**

按改写模板重构。直觉：交叉熵就像后端系统里的"对账日志"——衡量模型预测结果和真实结果的差距，差距越大 loss 越高。重心放在"最大似然估计"这个核心思想上，不要陷入 KL 散度的数学推导。

- [ ] **Step 3: 写入文件**

Write to `documentation/docs/math_foundations/cross-entropy.md`

- [ ] **Step 4: 添加交叉引用**

在 `延伸阅读` 中添加指向 `softmax.md`（softmax 通常和交叉熵配合使用）和 `backpropagation.md` 的链接。

- [ ] **Step 5: 提交**

```bash
git add documentation/docs/math_foundations/cross-entropy.md
git commit -m "docs: add cross-entropy article to math foundations"
```

---

### Task 2.5: perceptron-learning.md

**源文件:** `感知机与神经网络如何学习并逼近复杂函数.md`

- [ ] **Step 1: 读取源文件**

Read `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/感知机与神经网络如何学习并逼近复杂函数.md`

- [ ] **Step 2: 改写内容**

按改写模板重构。直觉：从一个最简单的"判断规则"出发，解释神经网络如何通过调整参数来逼近复杂函数。工程比喻：就像后端工程师调配置参数，只不过这里是自动化的、用梯度来调。

- [ ] **Step 3: 写入文件**

Write to `documentation/docs/math_foundations/perceptron-learning.md`

- [ ] **Step 4: 添加交叉引用**

在 `延伸阅读` 中添加指向 `activation-functions.md` 和 `backpropagation.md` 的链接。

- [ ] **Step 5: 提交**

```bash
git add documentation/docs/math_foundations/perceptron-learning.md
git commit -m "docs: add perceptron learning article to math foundations"
```

---

### Task 2.6: backpropagation.md

**源文件:** `链式法则与反向传播：从直觉到结构理解.md`

- [ ] **Step 1: 读取源文件**

Read `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/链式法则与反向传播：从直觉到结构理解.md`

- [ ] **Step 2: 改写内容**

按改写模板重构。直觉：反向传播就像分布式系统里的"故障溯源"——从最终结果往回追查每个环节分别要负多少责任。链式法则是工具，反向传播是应用。重点讲清楚"梯度"在每个节点上是怎么传回去的。

- [ ] **Step 3: 写入文件**

Write to `documentation/docs/math_foundations/backpropagation.md`

- [ ] **Step 4: 添加交叉引用**

在 `延伸阅读` 中添加指向 `vanishing-exploding-gradients.md`、`layer-norm.md`、`cross-entropy.md` 的链接。

- [ ] **Step 5: 提交**

```bash
git add documentation/docs/math_foundations/backpropagation.md
git commit -m "docs: add backpropagation article to math foundations"
```

---

### Task 2.7: vanishing-exploding-gradients.md

**源文件:** `从0理解梯度消失与梯度爆炸.md`

- [ ] **Step 1: 读取源文件**

Read `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/从0理解梯度消失与梯度爆炸.md`

- [ ] **Step 2: 改写内容**

按改写模板重构。直觉：梯度消失就像日志链路越传越弱、最终没人记得最初发生了什么；梯度爆炸就像错误无限放大、某一步突然崩掉。重点讲清楚这两种问题的成因，以及残差连接（Residual Connection）是如何解决深层网络梯度消失的。现有 `draft/残差连接.md` 的核心内容可以提炼整合进来。

- [ ] **Step 3: 写入文件**

Write to `documentation/docs/math_foundations/vanishing-exploding-gradients.md`

- [ ] **Step 4: 添加交叉引用**

在 `延伸阅读` 中添加指向 `layer-norm.md` 和 `backpropagation.md` 的链接。

- [ ] **Step 5: 提交**

```bash
git add documentation/docs/math_foundations/vanishing-exploding-gradients.md
git commit -m "docs: add vanishing/exploding gradients article to math foundations"
```

---

### Task 2.8: layer-norm.md

**源文件:** `LayerNorm解析.md`

- [ ] **Step 1: 读取源文件**

Read `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/LayerNorm解析.md`

- [ ] **Step 2: 改写内容**

按改写模板重构。直觉：LayerNorm 就像对一组数值做"归一化处理"——和后端系统中对金额字段做 scale、或者对日志数据做标准化类似。核心是"对单个样本的所有特征做均值归一化"，要和 BatchNorm 对比讲清楚区别（Transformer 用 LayerNorm 而不是 BatchNorm 的原因）。

- [ ] **Step 3: 写入文件**

Write to `documentation/docs/math_foundations/layer-norm.md`

- [ ] **Step 4: 添加交叉引用**

在 `延伸阅读` 中添加指向 `transformer_architecture.md`（Transformer 架构中 LayerNorm 的位置）的链接。

- [ ] **Step 5: 提交**

```bash
git add documentation/docs/math_foundations/layer-norm.md
git commit -m "docs: add LayerNorm article to math foundations"
```

---

### Task 2.9: 更新 sidebars.ts

**Files:**
- Modify: `documentation/sidebars.ts`

- [ ] **Step 1: 读取当前 sidebars.ts**

Read `documentation/sidebars.ts`

- [ ] **Step 2: 在"基础概念"之后插入"数学基础"分类**

在 `基础概念` 分类之后、`实践应用` 之前，插入：

```typescript
{
  type: 'category',
  label: '数学基础',
  items: [
    'math_foundations/ai-math-essentials',
    'math_foundations/softmax',
    'math_foundations/activation-functions',
    'math_foundations/cross-entropy',
    'math_foundations/perceptron-learning',
    'math_foundations/backpropagation',
    'math_foundations/vanishing-exploding-gradients',
    'math_foundations/layer-norm',
  ],
},
```

- [ ] **Step 3: 验证构建**

```bash
cd documentation
npm run build
# 预期：build 成功，无 error
```

- [ ] **Step 4: 提交**

```bash
git add documentation/sidebars.ts
git commit -m "docs: add 数学基础 sidebar category with 8 articles"
```

---

## Task 3: Phase 2 — Embedding 桥接线（2篇）

**源文件前缀:** `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/`

**Files:**
- Create: `documentation/docs/embeddings/from-onehot-to-embedding.md`
- Create: `documentation/docs/embeddings/embedding-evolution.md`
- Modify: `documentation/sidebars.ts`（在"实践应用"下的"向量与嵌入基础"中增加 2 篇，或新建 `embeddings/` 分类）

---

### Task 3.1: from-onehot-to-embedding.md

**源文件:** `从One-hot到Embedding：词的分布式表示.md`

- [ ] **Step 1: 读取源文件**

Read `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/从One-hot到Embedding：词的分布式表示.md`

- [ ] **Step 2: 改写内容**

按改写模板重构。直觉：从"用唯一 ID 标记每个词"（One-hot）到"用向量表示词"（Embedding），就像从"用枚举类型标记请求类型"到"用特征向量标记用户画像"——后者能捕捉语义相似性。核心讲清楚 Embedding 的维度、语义空间、相似度计算（点积/余弦）。

- [ ] **Step 3: 写入文件**

Write to `documentation/docs/embeddings/from-onehot-to-embedding.md`

- [ ] **Step 4: 添加交叉引用**

在 `延伸阅读` 中添加指向 `math_foundations/softmax.md`（点积+Softmax是相似度计算的核心）和 `embeddings/embedding-evolution.md` 的链接。

- [ ] **Step 5: 提交**

```bash
git add documentation/docs/embeddings/from-onehot-to-embedding.md
git commit -m "docs: add One-hot to Embedding article"
```

---

### Task 3.2: embedding-evolution.md

**源文件:** `从Word2Vec到Transformer：Embedding在不同模型中的角色演化.md`

- [ ] **Step 1: 读取源文件**

Read `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/从Word2Vec到Transformer：Embedding在不同模型中的角色演化.md`

- [ ] **Step 2: 改写内容**

按改写模板重构。直觉：Embedding 的角色从 Word2Vec 的"查表"到 Transformer 的"动态生成"，就像后端缓存从"静态缓存"到"实时计算缓存"。重点讲清楚 Embedding 在 RNN、CNN、Transformer 中的不同角色和演进原因。

- [ ] **Step 3: 写入文件**

Write to `documentation/docs/embeddings/embedding-evolution.md`

- [ ] **Step 4: 添加交叉引用**

在 `延伸阅读` 中添加指向 `math_foundations/ai-math-essentials.md`、`advanced_transformer/transformer_architecture.md` 的链接。

- [ ] **Step 5: 提交**

```bash
git add documentation/docs/embeddings/embedding-evolution.md
git commit -m "docs: add Embedding evolution article"
```

---

### Task 3.3: 更新 sidebars.ts

**Files:**
- Modify: `documentation/sidebars.ts`

- [ ] **Step 1: 读取当前 sidebars.ts**

Read `documentation/sidebars.ts`

- [ ] **Step 2: 在"实践应用"下的"向量与嵌入基础"中替换 items**

将现有：

```typescript
{
  type: 'category',
  label: '向量与嵌入基础',
  items: ['chapters/vector_concepts/dot_product_angle'],
},
```

替换为：

```typescript
{
  type: 'category',
  label: '向量与嵌入基础',
  items: [
    'chapters/vector_concepts/dot_product_angle',
    'embeddings/from-onehot-to-embedding',
    'embeddings/embedding-evolution',
  ],
},
```

- [ ] **Step 3: 验证构建**

```bash
cd documentation
npm run build
# 预期：build 成功，无 error
```

- [ ] **Step 4: 提交**

```bash
git add documentation/sidebars.ts
git commit -m "docs: add 2 Embedding articles to sidebar"
```

---

## Task 4: Phase 3 — Transformer 深化（1篇 + 审视现有）

**源文件前缀:** `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/`

**Files:**
- Create: `documentation/docs/advanced_transformer/optimizer-selection.md`
- Modify: `documentation/sidebars.ts`（在 Transformer深度解析 分类末尾添加 optimizer-selection）
- Modify: `documentation/docs/advanced_transformer/transformer_architecture.md`（添加交叉引用指向 math_foundations 和 embeddings）

---

### Task 4.1: optimizer-selection.md

**源文件:** `Transformer训练中的优化器选择.md`

- [ ] **Step 1: 读取源文件**

Read `/Users/kingsonwu/programming/kingson4wu/kingson4wu.github.io.zh/source/_posts/Transformer训练中的优化器选择.md`

- [ ] **Step 2: 改写内容**

按改写模板重构。直觉：优化器就是梯度下降的"执行策略"——SGD、Momentum、Adam 就像不同的重试策略，各有优劣。重点讲清楚 Adam 为什么是 Transformer 训练的主流选择，以及它和 SGD 的取舍。适合有后端性能调优经验的工程师理解。

- [ ] **Step 3: 写入文件**

Write to `documentation/docs/advanced_transformer/optimizer-selection.md`

- [ ] **Step 4: 添加交叉引用**

在 `延伸阅读` 中添加指向 `math_foundations/backpropagation.md` 和 `math_foundations/vanishing-exploding-gradients.md` 的链接。

- [ ] **Step 5: 提交**

```bash
git add documentation/docs/advanced_transformer/optimizer-selection.md
git commit -m "docs: add optimizer selection article"
```

---

### Task 4.2: 审视现有 Transformer 文章，补充交叉引用

**Files:**
- Read: `documentation/docs/advanced_transformer/transformer_architecture.md`
- Read: `documentation/docs/advanced_transformer/attention_mechanism.md`

- [ ] **Step 1: 读取现有文章**

Read `documentation/docs/advanced_transformer/transformer_architecture.md`
Read `documentation/docs/advanced_transformer/attention_mechanism.md`

- [ ] **Step 2: 在 transformer_architecture.md 添加指向 math_foundations 的引用**

在 LayerNorm 相关段落添加指向 `math_foundations/layer-norm.md` 的链接。
在 Feed-Forward Network 相关段落添加指向 `math_foundations/activation-functions.md` 的链接。

- [ ] **Step 3: 在 attention_mechanism.md 添加指向 math_foundations 的引用**

在 Softmax 段落添加指向 `math_foundations/softmax.md` 的链接。
在 Scaled Dot-Product Attention 段落添加指向 `math_foundations/dot_product_angle.md`（现有向量章节）的链接。

- [ ] **Step 4: 提交**

```bash
git add documentation/docs/advanced_transformer/transformer_architecture.md documentation/docs/advanced_transformer/attention_mechanism.md
git commit -m "docs: add cross-references from Transformer articles to math foundations"
```

---

### Task 4.3: 更新 sidebars.ts

**Files:**
- Modify: `documentation/sidebars.ts`

- [ ] **Step 1: 读取当前 sidebars.ts**

Read `documentation/sidebars.ts`

- [ ] **Step 2: 在 Transformer深度解析 分类末尾添加 optimizer-selection**

在 `'advanced_transformer/ai_engineering_practices'` 之后添加 `'advanced_transformer/optimizer-selection'`。

- [ ] **Step 3: 验证构建**

```bash
cd documentation
npm run build
# 预期：build 成功，无 error
```

- [ ] **Step 4: 提交**

```bash
git add documentation/sidebars.ts
git commit -m "docs: add optimizer-selection to Transformer sidebar"
```

---

## Task 5: 最终验证

- [ ] **Step 1: 运行完整构建**

```bash
cd documentation
npm run build
# 预期：build 成功，无 error
```

- [ ] **Step 2: 检查所有新增文件是否在 sidebars 中正确注册**

遍历 `math_foundations/`、`embeddings/`、`optimizer-selection.md`，确认都在 `sidebars.ts` 中有对应条目。

- [ ] **Step 3: 最终提交（如有遗漏修改）**

```bash
git status
git add -A
git commit -m "docs: complete math foundations and embeddings modules"
```

---

## 完成后状态

所有 11 篇文章迁移改写完成，侧边栏配置完整，站点构建成功。数学基础线打通，读者可以从 `math_foundations/ai-math-essentials.md` 入口，按依赖关系或按兴趣阅读各模块。

---

## 计划自检

- [ ] **Spec 覆盖检查：** 清单上的 11 篇文章（8+2+1）和 sidebars 更新均有对应 Task
- [ ] **Placeholder 检查：** 无 TBD/TODO，每步都有具体文件名和命令
- [ ] **交叉引用：** 每篇文章末尾都有 `延伸阅读` 指向相关模块
- [ ] **sidebars.ts：** 3 处修改（Phase 1、Phase 2、Phase 3）均有 Task 覆盖
