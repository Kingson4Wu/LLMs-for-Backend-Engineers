# 优化器选择：从 SGD 到 AdamW

## 本章要解决什么问题

训练神经网络，本质上是一个优化问题：给定损失函数 L(theta)，找到一组参数 theta 使其最小化。

反向传播告诉我们"往哪个方向走"——梯度指向损失下降最快的方向。

但梯度无法回答：**每个参数该走多快？**

这就像分布式系统中的重试策略：所有请求都失败了，错误信息告诉你"换个方向"，但没说"换多大的步子"。SGD、Momentum、Adam，本质上是不同的"重试策略"——它们对同样的梯度信号，给出截然不同的执行动作。

## 这个工具/机制是怎么工作的

### SGD：统一步长，最简单，也最脆弱

```python
theta = theta - lr * gradient  # 所有参数用同一个学习率
```

SGD 的隐含假设是：**所有参数的几何性质相似，可以一刀切。**

这个假设在深度学习中几乎不成立。以 Transformer 为例，Embedding 参数每步只有极少数 token 被激活（梯度稀疏），而 FFN 权重几乎每步都有梯度。统一步长，要么让稀疏参数原地踏步，要么让密集参数震荡发散。

```
损失函数等高线（示意）：

     陡峭方向（FFN）
         |
    x <- 震荡
     \   /
      \ /  <- SGD 在峡谷中左右横跳
        -> 平缓方向（Embedding）
```

### Momentum：用惯性平滑震荡

```python
velocity = momentum * velocity + gradient
theta = theta - lr * velocity
```

物理类比：一个球在损失曲面滚动。沿主方向持续加速，横向震荡相互抵消。

Momentum 改进了**方向稳定性**，但仍没有解决**步长的合理性**——所有参数依然共享同一个有效学习率。

### Adam：参数级自适应学习率

Adam 的核心思想是：**每个参数都应该有自己的"油门"**。

它维护两个统计量：
- **一阶矩 m_t**：梯度的指数移动平均（类似 Momentum）
- **二阶矩 v_t**：梯度平方的指数移动平均（记录每个参数的梯度历史）

```python
m = beta1 * m + (1 - beta1) * gradient        # 一阶矩
v = beta2 * v + (1 - beta2) * (gradient ** 2) # 二阶矩

theta = theta - lr * m / (sqrt(v) + epsilon)   # 自适应步长
```

**自适应机制**：
- 某参数持续有大梯度 → v_t 大 → 步长自动变小（防止震荡）
- 某参数梯度稀疏 → v_t 小 → 步长相对变大（避免停滞）

### AdamW：修正 Adam 的正则化语义

Adam 的 L2 正则存在一个问题：正则项梯度被 sqrt(v_t) 缩放后，不同参数的实际正则化强度不一致。

AdamW 的解法是将 weight decay 从梯度计算中**解耦**，直接作用在参数上：

```python
theta = theta - lr * m / (sqrt(v) + epsilon) - lr * weight_decay * theta
```

结果：所有参数受到一致的衰减比例，泛化性能更稳定。

### Warmup：给训练初期一个保护期

训练开始时，梯度分布极不稳定，Adam 的二阶矩估计尚未收敛，此时用完整学习率可能导致数值爆炸。

Warmup 在前 N 步线性提升学习率，给模型"热身"时间：

```
学习率
  ^
  |          ___________
  |         /
  |        /
  |_______/________________> 训练步数
        warmup 阶段
```

这不是玄学，是**降低对不可靠统计量的依赖**。

### 演化链总结

```
SGD        -> 问题：统一步长导致震荡
  +- Momentum        -> 改进：平滑方向，但步长仍统一
      +- Adam        -> 突破：参数级自适应步长
          +- AdamW  -> 修正：解耦 weight decay
              +- Warmup -> 保护：渐进式启动
```

## 形式化（附注）

**Adam 更新规则（偏置修正后）**：

```
theta_{t+1} = theta_t - lr * (m_hat_t / (sqrt(v_hat_t) + eps))
```

其中：
- m_hat_t = m_t / (1 - beta1^t)：一阶矩偏置修正
- v_hat_t = v_t / (1 - beta2^t)：二阶矩偏置修正
- beta1 = 0.9, beta2 = 0.999, eps = 1e-8

**PyTorch 使用示例**：

```python
import torch.optim as optim

# Transformer 训练的标准配置
optimizer = optim.AdamW(
    model.parameters(),
    lr=1e-4,
    weight_decay=0.1,
    betas=(0.9, 0.999)
)

# 带 Warmup 的学习率调度（通常配合 linear_warmup + cosine_decay）
```

## 本章小结

AdamW + Warmup 是 Transformer 训练的主流选择：AdamW 的自适应机制解决了不同参数梯度尺度差异大的问题，Warmup 则保护了训练初期的数值稳定性。

## 延伸阅读

- [反向传播：梯度是如何计算的](../part1-math-foundations/backpropagation) —— 理解梯度的来源
- [梯度消失与梯度爆炸：训练深层的核心障碍](../part1-math-foundations/vanishing-exploding-gradients) —— 理解为什么优化器选择直接影响深层网络的训练可行性
