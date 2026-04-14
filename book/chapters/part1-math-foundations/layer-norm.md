# LayerNorm：数值纪律

## 本节要解决什么问题

后端工程师对"标准化"不陌生：处理金额时统一精度（分、角、元），处理日志时对时间戳和数值字段做归一化（减去均值除以标准差）。这些操作的目的只有一个：**消除量纲差异，让不同规模的数据可以在同一个尺度上比较**。

LayerNorm（Layer Normalization，层归一化）做的也是同样的事：把每个 token 在某一层的表示向量，标准化到一个稳定的数值范围内。只不过它的作用域更精确——**只归一化单个 token 的所有特征维度**，不涉及 batch 中的其他样本。

在 Transformer 中，LayerNorm 是和残差连接配套使用的数值稳定组件。没有它，深层的 Transformer 几乎无法训练。

## 这个工具/机制是怎么工作的

### 核心操作：对单个 token 的向量做归一化

在 Transformer 中，每个 token 在某一层被表示为一个 d 维向量：x = (x1, x2, ..., xd)

LayerNorm 做的三件事：

```
第 1 步：计算均值
μ = (x₁ + x₂ + ... + x_d) / d

第 2 步：计算方差
σ² = [(x₁-μ)² + (x₂-μ)² + ... + (x_d-μ)²] / d

第 3 步：标准化 + 仿射变换
LN(x)_i = γ × (x_i - μ) / √(σ² + ε) + β
```

其中 γ 和 β 是可学习的参数（默认为 γ=1, β=0）。

### 直观理解：把向量"拉回原点"

```text
标准化前：x = [1000, 1001, 999]   ← 数值很大，但相对差异很小
标准化后：  = [1.0, 0.0, -1.0]   ← 均值为 0，方差为 1
```

归一化之后，向量的均值约为 0、标准差约为 1。无论上一层输出的数值有多大、多不稳定，归一化后都会被"拉回到"一个稳定的坐标系中。

γ 和 β 的作用是：模型可以学习"我需要保留多少原始尺度信息"，而不是被强制归一化。

### 为什么 Transformer 特别需要 LayerNorm

Transformer 有三层结构叠加，每个都天然有数值失控的风险：

**1. Attention 是无约束的加权求和**

Attention 把多个 value 向量按注意力权重加权求和。如果某个 head 的输出数值偏大，它会主导后续计算；如果某个维度数值偏大，它会压制其他维度。没有内在机制约束输出的数值范围。

**2. 残差连接会层层累加**

第 l+1 层输出 = 第 l 层输出 + 第 l 层变换

残差保证信息通路，但每次新信息都累加到旧表示上，数值会随层数持续漂移。100 层之后，最底层的表示可能已经被叠加了 100 次。

**3. Softmax 对尺度极其敏感**

Attention 中的 Softmax，只在一个窄范围内工作正常：
- 输入太大 → 趋近 one-hot（梯度 ≈ 0）
- 输入太小 → 趋近均匀分布（注意力失去焦点）

三者叠加，没有 LayerNorm 的 Transformer 在数值上几乎必然崩溃。

### LayerNorm 在 Transformer 中的位置

Pre-LN Transformer（现代大模型标准做法）的结构：

```
输入 x
  │
  ├─→ LayerNorm(x)
  │       │
  │       ▼
  │    Self-Attention(x)
  │       │
  │       ▼
  │      x + Attention(x)   ← 残差连接
  │       │
  │       ▼
  ├─→ LayerNorm(...)
  │       │
  │       ▼
  │    Feed-Forward Network
  │       │
  │       ▼
  │      x + FFN(x)         ← 残差连接
  │       │
  └───────┘
```

职责分工：
- **Attention**：管信息交流（看谁）
- **Residual**：管信息传承（保自己）
- **LayerNorm**：管数值纪律（稳自己）

### LayerNorm vs BatchNorm：为什么 Transformer 用前者

BatchNorm 在计算机视觉中几乎是标配，但在自然语言处理（Transformer）中不适用，根本原因在于 batch 本身的性质差异：

| 维度 | BatchNorm | LayerNorm |
|------|-----------|-----------|
| 归一化方向 | 跨 batch 内所有样本 | 单个样本内所有特征 |
| 看其他样本？ | 是 | 否 |
| batch 稳定？ | 否（句子长短不一，padding 多）| 完全无关 |
| 推理 batch=1 时 | 数值偏移（统计量不稳定）| 无影响 |

**NLP 场景的核心矛盾**：Transformer 的 Attention 本身就是让 token 之间交互的机制，如果在归一化阶段引入"其他样本对当前样本的影响"，就破坏了 Attention 的语义逻辑——LayerNorm 保证每个 token 在归一化时只看自己。

## 形式化

LayerNorm 公式：LN(x) = γ ⊙ (x - μ) / √(σ² + ε) + β

其中：
- μ = Σ xi / d（均值）
- σ² = Σ(xi - μ)² / d（方差）
- ε：防止除零的小常数
- γ, β：可学习的缩放和平移参数

## 本节小结

LayerNorm 对单个 token 的特征向量做均值-方差归一化，是 Transformer 维持数值稳定的核心机制。它不看 batch、不看其他 token，只负责"把自己的数值状态拉回正常范围"，与 Attention（信息交流）、残差连接（信息传承）共同构成 Transformer 稳定训练的三驾马车。

## 延伸阅读

- [Transformer 架构](../part2-llm-internal/transformer-architecture) — LayerNorm 在 Pre-LN 和 Post-LN 两种位置安排下的对比，以及它们各自对训练稳定性的影响
