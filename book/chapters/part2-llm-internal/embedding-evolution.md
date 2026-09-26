# 从 Word2Vec 到 Transformer：Embedding 的角色演化

在 Skip-gram 与 Negative Sampling 中，Embedding 通过“预测上下文”的目标和损失函数从语料中逐步学习。Transformer 同样从可学习的 Token 向量开始，但这些向量不再是最终产物，而是深层序列计算的起点。两者的差别不在于 Embedding 是否被学习，而在于它由什么目标约束、位于什么计算结构中、承担什么功能。

比较它们时，应看 Embedding 在优化目标和计算图中的位置，而不是只比较模型结构的复杂程度。

---

## 统一视角：Embedding 是可学习的参数表

无论是 Word2Vec 还是 Transformer，embedding 在数学形式上完全一致：

- 都是一个矩阵 $E \in \mathbb{R}^{V \times d}$
- 每个 token id $i$ 对应一行向量 $\mathbf{e}_i = E[i]$
- 向量的数值由随机初始化开始，通过反向传播不断更新

**embedding 并不是「预定义的语义表示」，而是模型参数的一部分**。

两类模型的差异不在于 embedding 「是不是参数」，而在于：

> **embedding 通过什么任务、在什么结构中、被什么损失函数约束。**

---

## Word2Vec 中的 Embedding：直接优化目标

在 Skip-gram + Negative Sampling 中，embedding 具有以下特点：

### 2.1 训练机制
- **直接目标**：区分「真实共现的词对」和「随机词对」
- **损失函数**：只依赖于 $\mathbf{v}_c^\top \mathbf{u}_w$
- **更新驱动**：完全由局部上下文共现统计驱动

### 2.2 核心特征
1. 训练目标是「预测上下文」
2. 上下文窗口是局部的、固定大小的
3. **embedding 本身就是最终产出**（训练完成即可单独使用）
4. **embedding 是上下文无关的**：同一个词始终对应同一个向量

### 2.3 两张表的设计
Word2Vec 显式区分：
- 输入向量表 $E_{\text{in}}$
- 输出向量表 $E_{\text{out}}$

这种设计不是偶然的，而是一个更一般建模选择的特例（我们稍后会在 Transformer 中看到它的推广）。

---

## Transformer 中的 Embedding：深层计算的起点

### 3.1 结构位置的变化

以 GPT/BERT 为例，Transformer 的输入层由三部分组成：

1. **Token Embedding**（词或子词向量）
2. **Position Embedding**（位置信息）
3. （BERT 中还有 Segment Embedding）

它们相加后形成模型的初始输入：

```
h_0 = E_token[x] + E_pos[p] (+ E_seg)
```

从这一刻开始，token embedding 不再直接用于预测，而是：
- 作为**整个深层计算图的起点**
- 被送入多层 self-attention 与前馈网络
- 在多层变换后，间接影响最终的预测结果

### 3.2 训练目标的根本变化

Transformer 中，embedding **不再通过「预测上下文词」这个局部任务来学习**，而是通过语言模型目标：

- **GPT**（自回归语言模型）：
  
$$
\max \sum_t \log P(x_t \mid x_{<t})
$$

- **BERT**（掩码语言模型）：
  
$$
\max \sum_{t \in \text{mask}} \log P(x_t \mid x_{\setminus t})
$$

### 3.3 梯度传播路径

embedding 的更新路径是：

$$
\text{loss} \rightarrow \text{output layer} \rightarrow \text{Transformer layers} \rightarrow \text{input embedding}
$$

当某个 token 出现在输入中时，它的输入 embedding 向量会：
1. 参与 self-attention 的 Q/K/V 计算
2. 影响上下文表示
3. 间接影响最终的预测概率
4. 在反向传播中获得梯度并被更新

**这一点与 Word2Vec 的共同原则一致**：只要 embedding 参数出现在 loss 的计算路径上，就会被梯度下降更新。若输入 embedding 与输出层权重共享，它也可通过输出侧损失获得梯度。embedding 的梯度来源是：

> **预测整个序列中某个 token 的损失，通过多层 Transformer 反向传播而来。**

---

## 关键区分：上下文无关的 Embedding 与上下文相关的表示

这是连接 Word2Vec 与 Transformer 时最容易混淆、也最关键的一点。

### 4.1 Transformer 中真正「上下文相关」的是什么？

在 Transformer 中：

- **Token embedding 表本身仍然是上下文无关的**
  
$$
E_{\text{token}}[\text{bank}] \quad \text{始终是同一个向量}
$$

- **真正随上下文变化的是每一层 Transformer 的 hidden state**
  
```
h_l^(t) = f_l( h_(l-1)^(1:t) )
```

因此：
- **embedding** ≈ 初始词表示（类似 Word2Vec 的输出）
- **hidden states** ≈ 上下文相关的动态表示

### 4.2 对比总结

| 维度 | Word2Vec | Transformer |
|------|----------|-------------|
| embedding 是否可学习 | 是 | 是 |
| embedding 是否上下文相关 | 否 | 否 |
| 最终语义表示 | embedding 本身 | 顶层 hidden state |
| 学习信号来源 | 局部上下文预测 | 全局序列建模 |
| 地位 | 学习的最终目标 | 深层推理的起点 |

---

## 权重共享：从两张表到统一设计

一些 Transformer，尤其是许多语言模型，会采用 **weight tying（权重共享）**：

$$
W_{\text{out}} = E_{\text{token}}^\top
$$

其中 $W_{\text{out}}$ 是输出 softmax 层的权重矩阵。

这可以被理解为：
- Word2Vec 中「输入表/输出表是否共享」的一个推广版本
- Transformer 可显式引入共享约束
- 以减少参数量、提高泛化性

这说明：**Word2Vec 中「两张表」的设计并非偶然，而是一个更一般建模选择的特例。**

---

## 统一原理：Embedding 由损失函数塑造

将 Word2Vec 与 Transformer 统一起来，可以得到以下结构化理解：

### 6.1 共同点
1. Embedding 在两类模型中都是可学习参数
2. Embedding 的更新都来源于预测任务的损失函数
3. Embedding 都是被梯度下降间接塑造的，而非预定义的语义容器

### 6.2 差异点
1. **预测目标复杂度**：局部上下文 vs 全局序列
2. **上下文建模能力**：固定窗口 vs 多层 self-attention
3. **最终产出**：Word2Vec 在 embedding 层「结束」，Transformer 在 embedding 层「开始」
4. **语义表示**：Word2Vec 直接使用 embedding，Transformer 使用经过多层变换的 hidden states

### 6.3 演化总结

用一句话概括这种演化：

> **在 Word2Vec 中，embedding 是学习的最终目标；**  
> **在 Transformer 中，embedding 是深层推理的起点。**

更具体地说：
- **Word2Vec**：embedding ≈ 对语料共现结构的直接建模结果
- **Transformer**：embedding ≈ 底层词汇信息的参数化入口，真正的语义组合发生在多层 self-attention 中

但二者在本质上仍然统一于同一原则：

> **Embedding 是被损失函数通过梯度下降间接塑造的参数，而非预定义的语义容器。**

---

## 小结

理解 embedding 从 Word2Vec 到 Transformer 的演化，关键在于认识到：

1. **数学本质不变**：都是可学习的参数矩阵，都通过反向传播更新
2. **训练目标升级**：从局部上下文预测到全局序列建模
3. **功能定位转变**：从最终输出到计算起点
4. **上下文建模深化**：Transformer 的上下文相关性来自 hidden states，而非 embedding 表本身
5. **设计选择延续**：输入/输出表的关系在两类模型中都是重要的建模决策

这种演化不是断裂的，而是在统一的优化原理下，针对更复杂任务的自然扩展。
