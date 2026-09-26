# Summary

- [导读](index.md)
- [前言](preface.md)

## 数学与机器学习基础

- [AI 的数学与机器学习基础：一张全景图](chapters/part1-math-foundations/ai-math-foundations.md)
- [从 One-hot 到 Embedding：离散 Token 怎样成为向量](chapters/part1-math-foundations/from-onehot-to-embedding.md)
- [点积与余弦相似度：向量怎样表达关系](chapters/part1-math-foundations/dot-product-angle.md)
- [Softmax：怎样把分数变成概率](chapters/part1-math-foundations/softmax.md)
- [激活函数：非线性从哪里来](chapters/part1-math-foundations/activation-functions.md)
- [感知机：参数怎样从误差中更新](chapters/part1-math-foundations/perceptron-learning.md)
- [交叉熵：怎样衡量预测误差](chapters/part1-math-foundations/cross-entropy.md)
- [反向传播：误差怎样传回每个参数](chapters/part1-math-foundations/backpropagation.md)
- [梯度消失与爆炸：深层网络为何难以训练](chapters/part1-math-foundations/vanishing-exploding-gradients.md)

## LLM 内部原理

- [模型的能力是怎样训练出来的](chapters/part2-llm-internal/model-training-lifecycle.md)
- [优化器：梯度怎样成为参数更新](chapters/part2-llm-internal/optimizer-selection.md)
- [微调与蒸馏的本质：函数逼近视角](chapters/part2-llm-internal/fine-tuning-and-distillation.md)
- [从 Word2Vec 到 Transformer：Embedding 的角色演化](chapters/part2-llm-internal/embedding-evolution.md)
- [从 RNN 到 Transformer：序列建模的结构性转变](chapters/part2-llm-internal/rnn-to-transformer.md)
- [Transformer 架构：从数据流理解](chapters/part2-llm-internal/transformer-architecture.md)
- [缩放点积：Softmax 的梯度为什么会变得极端](chapters/part2-llm-internal/softmax-gradient-scaling.md)
- [残差连接：深层网络为什么仍能训练](chapters/part2-llm-internal/residual-connections.md)
- [LayerNorm：怎样保持表示的数值稳定](chapters/part2-llm-internal/layer-norm.md)
- [LLM 生成机制：从输入到下一个 Token](chapters/part2-llm-internal/llm-generation.md)
- [大模型推理的不确定性：从采样到工程实现](chapters/part2-llm-internal/llm-inference-nondeterminism.md)
- [多语言大模型：不同语言怎样共享表示与能力](chapters/part2-llm-internal/multilingual-llms.md)
- [多模态模型：文字之外的信息怎样进入计算](chapters/part2-llm-internal/multimodal-models.md)

## LLM 与外部系统

- [LLM 怎样与外部世界交互：从生成到行动](chapters/part3-llm-external/llm-external-interaction.md)
- [RAG 与上下文工程：怎样把证据带入模型](chapters/part3-llm-external/rag-context-evidence.md)
- [Function Calling 与工具调用：机制、区别与本质](chapters/part3-llm-external/function-calling-tool-use.md)
- [从 MHS、MCP 到领域能力协议](chapters/part3-llm-external/mhs-mcp-domain-capability-protocol.md)
- [Harness、Agent Runtime 与 Skill：怎样让多轮任务可靠运行](chapters/part3-llm-external/harness-runtime-skills.md)
- [AI Agent Eval：从评测到业务质量系统](chapters/part3-llm-external/agent-eval-business-quality-system.md)

## LLM 基础设施

- [LLM 基础设施：模型怎样成为可靠服务](chapters/part4-serving-runtime/llm-infrastructure.md)
- [推理服务的性能与容量：延迟、吞吐与 KV Cache 怎样互相制约](chapters/part4-serving-runtime/inference-performance-capacity.md)
- [推理服务的控制面：路由、扩缩容与可靠交付](chapters/part4-serving-runtime/serving-control-plane.md)

## 扩展阅读

- [“人工智能”一词是否准确：一次关于 AI 概念边界的反思](chapters/appendices/what-ai-really-means.md)
- [AI 能否创造真正的新事物](chapters/appendices/can-ai-create-new-things.md)
- [生成式 AI：概率生成、约束与验证](chapters/appendices/generative-ai-probability-and-innovation.md)

## 附录

- [附录一：推荐学习资料](chapters/appendices/learning-resources.md)
