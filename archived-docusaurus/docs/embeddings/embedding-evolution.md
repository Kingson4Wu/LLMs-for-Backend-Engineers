# 从 Word2Vec 到 Transformer：Embedding 的角色演化

## 本章要解决什么问题

在后端系统中，你一定用过缓存。最初级的缓存是**静态预计算缓存**——把查询结果提前算好存进 Redis，用的时候直接读取，缓存命中则返回，缓存失效则回源。这种方式简单可靠，但只能处理完全一致的请求。

后来你可能引入了**实时计算缓存**——同一条数据的缓存可以基于不同查询条件生成不同版本，缓存的"键"不再只是资源 ID，还包含了上下文信息。相同的数据在不同上下文中展现出不同的"版本"，而不是一个静态副本。

**Embedding 的演化走的正是同一条路**：Word2Vec 的 embedding 像静态缓存——训练完成，向量就固定了，任何上下文都用同一个向量。而 Transformer 的 embedding 像实时计算缓存的入口——它是深层推理的起点，最终的语义表示是多层注意力计算后的结果，同一个词在不同上下文中产生不同的 hidden state。

理解这种演化，是理解大语言模型内部机制的关键。

## 这个工具/机制是怎么工作的

### Word2Vec：Embedding 是最终目标

在 Word2Vec（Skip-gram + Negative Sampling）中，embedding 的训练目标是**预测中心词的上下文词**：

```
语料: "北京市政府 召开 会议"

训练任务: 给定"召开"，预测"北京市政府"和"会议"也出现在它附近

正样本: (召开, 北京市政府), (召开, 会议)
负样本: (召开, 随机词)
```

训练完成后，embedding 本身就是最终产出：
- 每个词对应一个固定的向量
- `bank` 这个词无论出现在什么句子中，向量始终不变
- 直接用这个向量做下游任务（分类、聚类、相似度搜索）

**这就像静态缓存：计算一次，到处复用，结果不变。**

```
Embedding 表 E (查表)
  │
  ▼
"bank" -> [0.12, -0.45, 0.78, ...]  # 始终是这个向量
```

### RNN/CNN 时代：Embedding 作为特征提取器

RNN 和 CNN 引入了序列建模和局部特征提取能力。这个阶段 embedding 的定位是：

```
输入层: Embedding (词 -> 固定向量)
  │
  ▼
RNN/CNN 层（序列建模 / 局部特征）
  │
  ▼
全连接层 + Softmax -> 输出
```

embedding 仍然是"上下文无关的固定向量"，但 RNN/CNN 层可以在此基础上做序列建模。embedding 的更新通过整个 RNN/CNN 的反向传播驱动，而不是独立的局部预测任务。

**这开始有点像带失效策略的缓存——向量还是固定的，但下游网络会根据不同输入动态调整中间结果。**

### Transformer：Embedding 是起点，不是终点

到了 Transformer 时代，架构发生了根本性变化：

```
输入: Token Embedding + Position Embedding
  │
  ▼
N 层 Self-Attention + Feed-Forward
  │
  ▼
顶层 Hidden State
  │
  ▼
输出层 -> 预测下一个词 / 掩码词
```

**关键变化**：embedding 不再是最终输出，而是整个深层计算图的起点。

以 GPT（自回归语言模型）为例，训练目标是最大化整个序列的对数似然：给定前 t-1 个词，预测第 t 个词，将所有位置的预测对数概率加总求和并最大化。

以 BERT（掩码语言模型）为例，训练目标是最大化掩码位置的对数似然：给定一个句子中所有未被掩码的词，预测被随机掩码的那个词，将所有被掩码位置的预测对数概率加总求和并最大化。

在两种情况下，embedding 都通过整个序列的预测损失反向传播更新——梯度路径是：

```
loss -> 输出层 -> Transformer 层 -> Input Embedding
```

**最终语义表示不再是 embedding 本身，而是顶层 hidden state。**

### 关键区分：上下文无关 Embedding vs 上下文相关 Hidden State

这是最容易混淆的地方：

```
Word2Vec:    词 -> Embedding -> 直接使用（上下文无关）
Transformer: 词 -> Embedding -> 多层 Attention -> Hidden State -> 使用（上下文相关）
```

在 Transformer 中：
- **Token Embedding 表本身仍然是上下文无关的**：`E["bank"]` 始终是同一个向量
- **真正随上下文变化的是每一层的 hidden state**：

```
bank 在 "river bank" 中:
  Layer 4: [0.1, 0.3, -0.2, ...]   # 河岸含义的表示

bank 在 "bank of China" 中:
  Layer 4: [0.8, -0.1, 0.4, ...]   # 银行含义的表示
```

**这才是 Transformer 能理解"一词多义"的核心机制。**

### 权重共享：从两张表到统一设计

Word2Vec 显式维护两张独立的向量表（输入表 + 输出表），因为同一个词在"作为中心词"和"作为上下文候选词"时承担的功能不同。

Transformer 中广泛使用 **weight tying（权重共享）**：输出层的权重矩阵与 token embedding 共享转置（输出层权重矩阵等于 token embedding 矩阵的转置）。这不是偶然的巧合，而是 Word2Vec "两张表"设计哲学在更大规模模型中的推广——**同一套参数在模型中不同位置复用，减少参数量。**

## 形式化（可选，附注）

### 核心公式

**Transformer 的 Embedding 输入**：

`h_0 = E_token[x] + E_pos[p]`

Token embedding 与 Position embedding 求和，作为第 0 层的输入。

**GPT 自回归损失（自然语言描述版）**：

最大化 `sum_t log P(第t个词 | 前t-1个词)`，即：给定前缀，预测下一个词。

**BERT 掩码损失（自然语言描述版）**：

最大化 `sum_{mask位置} log P(被掩码的词 | 所有其他词)`，即：给定上下文，预测被盖住的词。

### 架构对比

| 维度 | Word2Vec | Transformer |
|------|----------|-------------|
| Embedding 是否可学习 | 是 | 是 |
| Embedding 是否上下文相关 | 否 | 否 |
| 最终语义表示来源 | Embedding 本身 | 顶层 Hidden State |
| 学习信号 | 局部上下文预测 | 全局序列建模 |
| Embedding 的地位 | 学习的最终目标 | 深层推理的起点 |
| 输入/输出向量关系 | 两张独立表 | 权重共享（通常） |

## 本章小结

从 Word2Vec 到 Transformer，Embedding 的本质（可学习的参数矩阵）没有变，但它的角色从"学习的最终目标"转变为"深层推理的起点"——Transformer 中真正的上下文相关表示来自多层 self-attention 后的 hidden state，而非 embedding 表本身。

## 延伸阅读

- [AI 数学基础](../math_foundations/ai-math-essentials) — 理解反向传播如何塑造 embedding 参数
- [Transformer 架构深度解析](../advanced_transformer/transformer_architecture) — Embedding 在 Transformer 中的完整数据流
