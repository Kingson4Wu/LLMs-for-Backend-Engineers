# 全书地图

本书面向后端工程师，目标是建立对基于 Transformer 的生成式 AI 的整体理解。它不试图覆盖所有 AI 技术，也不把训练框架、模型源码或单一厂商 API 当作主线。

```text
数学与机器学习基础
        ↓
模型怎样形成能力，并把 token 变成下一步生成
        ↓
模型怎样取得证据、提出行动，并在外部环境中完成任务
        ↓
模型怎样被调度、观测和交付为可靠服务
```

## 四部分各回答什么问题

| 部分 | 核心问题 | 主要章节 |
| --- | --- | --- |
| 数学与机器学习基础 | 信息怎样成为向量，误差怎样推动参数更新？ | 向量与 Embedding、Softmax、非线性、交叉熵、反向传播、梯度稳定性 |
| LLM 内部原理 | 参数怎样形成能力，Transformer 怎样把上下文变成下一个 token？ | 训练、适配、Embedding 演化、Transformer、生成、多语言与多模态 |
| LLM 与外部系统 | 模型怎样获得当前事实、提出行动并完成可验证任务？ | 提示词与结构化输出、RAG、工具、MCP、Runtime、Eval |
| LLM 基础设施 | 一次生成怎样受到显存、并发、调度和服务治理约束？ | 推理执行、容量与 KV Cache、控制面 |

## 从问题定位章节

| 如果问题是 | 先读 | 再连接到 |
| --- | --- | --- |
| Token、向量、相似度和概率各是什么关系？ | `from-onehot-to-embedding`、`dot-product-angle`、`softmax` | `cross-entropy`、`embedding-evolution` |
| 参数为什么能从样本中学到能力？ | `ai-math-foundations`、`perceptron-learning`、`backpropagation` | `model-training-lifecycle`、`optimizer-selection` |
| 为什么 Transformer 替代 RNN，Attention 到底计算什么？ | `rnn-to-transformer`、`transformer-architecture` | `softmax-gradient-scaling`、`residual-connections`、`layer-norm` |
| 一段提示怎样变成回答，为什么每次结果可能不同？ | `llm-generation` | `llm-inference-nondeterminism` |
| RAG、上下文、工具调用和 Agent 的职责怎样区分？ | `llm-external-interaction`、`rag-context-evidence` | `function-calling-tool-use`、`harness-runtime-skills`、`agent-eval-business-quality-system` |
| MCP、Skill、Harness 和 Agent Runtime 分别位于哪里？ | `llm-external-interaction` | `mhs-mcp-domain-capability-protocol`、`harness-runtime-skills` |
| 为什么 LLM 服务不只是部署一个 HTTP 接口？ | `llm-infrastructure` | `inference-performance-capacity`、`serving-control-plane` |
| 图像、语音和视频怎样进入或离开模型？ | `multimodal-models` | `llm-generation`、`llm-external-interaction` |

章节 ID 对应 `../book/catalog.json`，具体原文位于 `../book/chapters/`。遇到概念边界不清时，应优先回到原文的定义、数据流与小结，而不是只依赖目录标签。

## 可选学习路径

### 建立全局模型

`导读` → `AI 的数学与机器学习基础：一张全景图` → `模型的能力是怎样训练出来的` → `Transformer 架构：从数据流理解` → `LLM 生成机制：从输入到下一个 Token` → `LLM 怎样与外部世界交互：从生成到行动` → `LLM 基础设施：模型怎样成为可靠服务`

适合先获得端到端结构，再按实际问题补数学或工程细节。

### 从后端系统经验进入

`LLM 怎样与外部世界交互：从生成到行动` → `RAG 与上下文工程：怎样把证据带入模型` → `Function Calling 与工具调用：机制、区别与本质` → `Harness、Agent Runtime 与 Skill：怎样让多轮任务可靠运行` → `AI Agent Eval：从评测到业务质量系统` → `LLM 基础设施：模型怎样成为可靠服务`

适合已经在设计服务、工作流、权限或质量闭环的读者；需要理解模型内部机制时，再回到 Transformer 和生成章节。

### 从 Transformer 原理进入

`从 One-hot 到 Embedding：离散 Token 怎样成为向量` → `Softmax：怎样把分数变成概率` → `激活函数：非线性从哪里来` → `反向传播：误差怎样传回每个参数` → `从 RNN 到 Transformer：序列建模的结构性转变` → `Transformer 架构：从数据流理解` → `LLM 生成机制：从输入到下一个 Token`

适合需要建立模型计算直觉的读者。交叉熵、优化器、缩放点积、残差和 LayerNorm 在遇到相应疑问时继续深入即可。
