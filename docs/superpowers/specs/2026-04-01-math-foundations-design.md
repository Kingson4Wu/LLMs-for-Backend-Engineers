# 数学基础模块搭建设计方案

## 目标

为有工程背景但无 AI 基础的后端工程师，搭建一条从零到能理解 LLM 内部原理的路径。内容以**模块独立**组织，每模块从"解决什么问题"出发，用直觉和类比建立感知，公式作为补充。

## 内容结构

```
documentation/docs/
  math_foundations/           # 数学基础模块（新建）
  ├── ai-math-essentials.md            # AI数学精要 — 模块入口/地图页
  ├── softmax.md                      # Softmax
  ├── activation-functions.md         # 激活函数
  ├── cross-entropy.md                # 交叉熵损失与最大似然估计
  ├── perceptron-learning.md           # 感知机与神经网络如何学习
  ├── backpropagation.md              # 链式法则与反向传播
  ├── vanishing-exploding-gradients.md # 梯度消失与梯度爆炸
  └── layer-norm.md                   # LayerNorm

  embeddings/                  # Embedding 桥接模块（新建）
  ├── from-onehot-to-embedding.md     # 从One-hot到Embedding
  └── embedding-evolution.md           # 从Word2Vec到Transformer

  advanced_transformer/        # 进阶模块（补充）
  └── optimizer-selection.md            # 新增：Transformer训练中的优化器选择

  chapters/                    # 现有章节（局部调整）
  ├── chapter1.md … chapter6.md         # 审视现有章节，按需补充引用指向新模块
  └── vector_concepts/dot_product_angle.md  # 现有，保留
```

## 内容迁移清单

### Phase 1：数学基础线（8篇）

| 文章 | 来源 | 放置位置 |
|---|---|---|
| AI数学精要 | 参考博客 | math_foundations/ai-math-essentials.md |
| Softmax：从直觉到本质 | 参考博客 | math_foundations/softmax.md |
| 激活函数的本质原理与作用 | 参考博客 | math_foundations/activation-functions.md |
| 交叉熵损失与最大似然估计：完全理解指南 | 参考博客 | math_foundations/cross-entropy.md |
| 感知机与神经网络如何学习并逼近复杂函数 | 参考博客 | math_foundations/perceptron-learning.md |
| 链式法则与反向传播：从直觉到结构理解 | 参考博客 | math_foundations/backpropagation.md |
| 从0理解梯度消失与梯度爆炸 | 参考博客 | math_foundations/vanishing-exploding-gradients.md |
| LayerNorm解析 | 参考博客 | math_foundations/layer-norm.md |

### Phase 2：Embedding 桥接线（2篇）

| 文章 | 来源 | 放置位置 |
|---|---|---|
| 从One-hot到Embedding：词的分布式表示 | 参考博客 | embeddings/from-onehot-to-embedding.md |
| 从Word2Vec到Transformer：Embedding在不同模型中的角色演化 | 参考博客 | embeddings/embedding-evolution.md |

### Phase 3：Transformer 深化（1篇）

| 文章 | 来源 | 放置位置 |
|---|---|---|
| Transformer训练中的优化器选择 | 参考博客 | advanced_transformer/optimizer-selection.md |

## 改写原则

每篇文章统一使用以下结构：

```
## 本章要解决什么问题
   直觉/类比/工程比喻，工程师能共鸣的比喻

## 这个工具/机制是怎么工作的
   简化示意图（ASCII 或流程描述）

## 形式化（可选，附注）
   公式 + 1~2 行代码示例，读者想深入再看
```

**写作风格：**
- 直觉优先，公式辅助
- 不要求读者能推公式，但读完后能用一句话解释这个机制在做什么
- 每个概念都连接到后端工程师已有的知识（缓存、分库分表、限流等）
- 添加与其他模块的交叉引用

## 执行阶段

- **Phase 1**：数学基础线（8篇），新建 `math_foundations/`
- **Phase 2**：Embedding 桥接线（2篇），新建 `embeddings/`
- **Phase 3**：Transformer 深化（审视现有 + 新增 optimizer 篇）

## 待确认

- draft/ 目录内容本次不处理，专注填满数学基础线后再决定
