# LLM 生成机制：从输入到下一个 Token

我们在聊天界面里看到一句问题和一段回答，模型处理的却是一串数字。要理解生成，先沿着一次请求走完：文字怎样进入模型，模型输出什么，下一步又从哪里开始。

本节以常见的自回归、Decoder-only 文本模型为例。这是一类重要架构，不是所有语言模型的唯一定义；Encoder-Decoder 模型也能生成文本。

## 从文字到模型输入

### Token、编号与向量是三件事

Tokenizer 把文本切成模型词表中的单位，再转换为编号。一个 token 可能对应一个词、词的一部分、标点或字节片段，不能把 token 数直接当作汉字数或单词数。

下面只示意步骤，编号和切分不是某个真实模型的结果：

```text
文本：查订单
  ↓ 分词与编号
[查] [订单] → [31, 208]
  ↓ 查 Embedding 表
向量 e31、向量 e208
  ↓ 在模型层中结合位置与上下文进行计算
每个位置的上下文表示
```

编号只是词表索引，208 并不比 31 “语义更大”。Embedding 才把离散编号映射为可计算的向量；后续层再根据上下文不断改变表示。输入表示与上下文表示的区别见 [Embedding 的角色演化](embedding-evolution.md)。

### 聊天消息怎样成为序列

对话接口通常保存带角色的消息，例如用户问题、助手回答和工具结果。服务端按模型的聊天模板，将这些消息组织成带边界标记的输入。概念上可以写成：

```text
[指令] 简要解释错误原因
[用户] 请求返回 403，可能是什么问题？
[助手] ...从这里继续生成...
```

这里的标签只是示意。实际特殊标记由模型格式决定，不能用任意字符串替代。角色与边界帮助模型识别谁说了什么；它们也不等于程序层面的权限检查。[Hugging Face 的聊天模板文档](https://huggingface.co/docs/transformers/main/en/chat_templating)展示了消息如何转换为 token 序列。

## 一步生成究竟做什么

给定当前序列，模型计算最后一个位置的隐藏表示，再通过输出投影得到词表上每个候选 token 的分数，称为 logits。Softmax 将分数转换为概率分布，解码策略从中选择一个 token。

```text
已有输入 → Transformer → 最后位置的表示
                              ↓
                        全词表 logits
                              ↓
                       解码策略选择 token
                              ↓
                  追加到序列，开始下一步
```

可写成条件概率：

$$
p_\theta(x_{t+1}\mid x_1,\ldots,x_t)
$$

其中 $\theta$ 是模型参数。普通生成过程中，变化的是输入序列和中间计算状态；参数通常保持不变。词表上的高概率表示模型倾向这样续写，不是“这个事实有同样高的概率为真”。

输出的停止也有具体机制：模型生成结束标记，或者运行程序触发长度、停止字符串等限制。回答被截断和模型判断已经答完，不是同一件事。

## 为什么训练能并行，生成却有先后依赖

训练时，样本中的后续 token 已经给定。假设训练序列被简化为 `[I, love, coding, EOS]`，一次前向计算可以同时计算多个位置的预测，再与各自的目标比较：

```text
已知前缀 I              → 目标 love
已知前缀 I love         → 目标 coding
已知前缀 I love coding  → 目标 EOS
```

因果 Mask 阻止某个位置读取后面的答案，保证这个位置的表示只依赖允许看到的前缀。并行的是已知样本上多个位置的计算，模型没有预先生成未知未来。

推理时，下一步输入包含刚刚选出的 token，所以普通自回归解码需要逐步推进。若刚才选了 “love”，下一步条件就与选了 “like” 不同。推测解码等方法可以批量提出和验证候选，改善执行效率，但不能把训练时已知目标与推理时未知输出混为一谈。

## Prefill、Decode 与 KV Cache

### 首次处理输入，与之后逐步生成

**Prefill** 处理已经给定的输入序列，并建立计算状态；随后 **Decode** 在该状态上继续生成。由此可以区分等待第一个输出 token 的时间，和之后每个 token 的生成间隔。

以输入 `[A, B, C]` 为例：

```text
Prefill：处理 A、B、C → 用 C 的输出预测 D
Decode：将 D 送入模型 → 用 D 的输出预测 E
Decode：将 E 送入模型 → 用 E 的输出预测下一个 token
```

预测 D 时，D 还没有被选出来，不能先计算 D 的表示。选出 D 并把它送回模型，是下一步的工作。

### 缓存保存了什么

在因果注意力中，追加 D 不会改变 A、B、C 原本能看到的前缀。因此，在模型与计算条件兼容时，可以复用各层已经算出的历史 Key、Value，而无需重新计算整个旧前缀。这就是 KV Cache 的核心。

KV Cache 是因果解码可以利用的**运行时计算状态**：它利用模型已有的注意力计算，但不定义 Transformer 架构，也不等于应用保存的长期记忆。将模型、训练与运行时分层的整体地图见 [Transformer 架构](transformer-architecture.md)。

新位置的 Query 仍要与允许访问的历史 Key 计算匹配，并聚合 Value。缓存省掉重复计算，不会让长上下文的读取免费；缓存本身也占用内存。具体机制可参考 [Transformers 缓存说明](https://huggingface.co/docs/transformers/main/en/cache_explanation)。

修改前缀会改变后续位置所依赖的信息，不能无条件复用变动点之后的旧缓存。跨请求的前缀缓存进一步复用共同输入的计算，实际匹配、保留和计费方式由服务实现决定。

KV Cache 是计算状态，不是可长期检索的用户档案。删掉缓存通常意味着重算；删掉应用保存的历史资料则可能意味着再也无法提供那段信息。这一区别在 [LLM 怎样与外部世界交互](../part3-llm-external/llm-external-interaction.md) 中继续展开。

## 采样策略：怎样从分布中选一个 Token

### Temperature：改变分布的集中程度

对于 logits $z_i$ 和正温度 $T$：

$$
p_i(T)=\frac{\exp(z_i/T)}{\sum_j\exp(z_j/T)}
$$

温度降低，分布通常更集中；温度升高，分布更平缓。假设 $T=1$ 时三个候选的概率是 `[0.6, 0.3, 0.1]`，将温度改为 $0.5$ 相当于将这些概率平方后重新归一化，约为 `[0.783, 0.196, 0.022]`。

这改变的是选择倾向，没有为答案增加事实依据。低温度也可能稳定地生成错误答案。公式不适用于 $T=0$；接口中的零温度通常另作贪心解码等特殊处理。

### Top-K 与 Top-P：缩小候选集合

Top-K 只保留概率最高的 K 个候选。Top-P 按概率从高到低累加，保留达到阈值所需的最小前缀，再在保留集合中重新归一化。

例如概率为 `[0.6, 0.3, 0.1]`，Top-P 为 0.8，则保留前两个候选，它们重新归一化为约 `[0.667, 0.333]`。候选数随分布变化，而不是固定为两个。

多个过滤器组合时，应用顺序会影响结果。下面的示例明确选择“温度 → Top-K → 归一化 → Top-P”；不是所有服务都采用完全相同的组合规则。

### 随机采样、贪心与 Beam Search

| 方法 | 选择方式 | 需要理解的边界 |
| --- | --- | --- |
| 随机采样 | 按候选概率抽取 | 多样性增加，不等于事实性增加 |
| 贪心解码 | 每步选最高分候选 | 给定同样 logits 时选择确定；不保证答案正确或整个服务完全可复现 |
| Beam Search | 保留有限条高分序列继续扩展 | 搜索的是序列评分，不保证全局最优，更不保证真实世界正确 |

Beam Search 维护多条候选会增加计算和状态开销，不能直接把它等同于某个 API 的固定计费倍数。关于概率截断与生成质量的研究，可参阅 [The Curious Case of Neural Text Degeneration](https://arxiv.org/abs/1904.09751)。

### 一个最小采样示例

下面只处理可表示为 float32 有限值的一维 logits，返回 token 编号。为了便于观察机制，它不实现批量生成、停止标记和缓存。需要 PyTorch。

```python
import torch

def sample_next_token(logits, temperature=1.0, top_k=0, top_p=1.0):
    if logits.ndim != 1 or logits.numel() == 0:
        raise ValueError("logits must be a nonempty vector")
    scores = logits.float()
    if not torch.isfinite(scores).all():
        raise ValueError("logits must be finite in float32")
    if not 0 < temperature < float("inf"):
        raise ValueError("temperature must be positive and finite")
    if not isinstance(top_k, int) or top_k < 0 or not 0 < top_p <= 1:
        raise ValueError("invalid top_k or top_p")

    scores = (scores - scores.max()) / temperature
    scores, indices = torch.sort(scores, descending=True)
    if top_k > 0:
        scores, indices = scores[:top_k], indices[:top_k]
    probs = torch.softmax(scores, dim=-1)

    # Keep the token that first reaches the cumulative threshold.
    keep = torch.cumsum(probs, dim=-1) - probs < top_p
    keep[0] = True
    probs, indices = probs[keep], indices[keep]
    probs = probs / probs.sum()
    return indices[torch.multinomial(probs, 1).item()].item()
```

即使关闭 Top-K，也要先排序，才能按累计概率解释 Top-P。将概率最高的 token 放在词表的最后一位，便能检查这件事是否做对。

## 中间推理步骤为什么可能有帮助

“逐 token 生成”描述输出机制，本身不能证明模型具备或不具备某种推理能力。考虑一个简单任务：比较两个订单合计金额。模型可以直接输出结论，也可以先写出各订单的金额、求和，再比较。

后一种路径将中间结果加入后续上下文，给分步处理提供了空间。[Chain-of-Thought 论文](https://arxiv.org/abs/2201.11903)研究了示范中间步骤对推理任务的影响。这不是“多写字就一定更准确”：中间步骤可能错，后续也可能继续沿用错误。

还应区分三种增加推理时计算的方式：

- 沿一条路径生成更多中间步骤。
- 生成多个候选，再比较或验证。
- 使用外部工具取得新的证据或执行结果。

它们增加的计算、信息和选择机会不同。重试若没有识别正确结果的方法，只是得到了更多答案。可见的推理文本也不能被当作全部内部计算的忠实记录；某个产品是否展示它，属于额外的产品与接口选择。

## 本节小结

一次生成把当前输入映射为下一 token 的分布，解码策略选出 token，再继续计算。训练改变参数，上下文改变条件，缓存复用计算，采样改变选择方式。把这些变化分开，才能理解“模型为什么这样回答”，并进一步判断需要补资料、改训练，还是借助外部工具。

## 延伸阅读

- [模型的能力是怎样训练出来的](model-training-lifecycle.md)
- [Softmax](../part1-math-foundations/softmax.md)
- [LLM 怎样与外部世界交互](../part3-llm-external/llm-external-interaction.md)
- [Attention Is All You Need](https://arxiv.org/abs/1706.03762) — 注意力架构与因果约束的基础
