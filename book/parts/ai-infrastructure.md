# 第四部分：LLM 基础设施

LLM 基础设施不是“几张 GPU”，而是让模型能够被加载、调用、扩展、观测和稳定交付的整套运行系统。本部分先沿一次请求建立从模型计算到硬件与集群的全景，再分别讨论最常见的性能容量问题，以及把模型变成可运营服务的控制面。

在[全书的主线图](../index.md#全书的主线图)中，这一部分承接前面的模型调用和外部系统，把它们放进受容量、延迟、成本和可靠性共同约束的运行环境。

| 阅读顺序 | 解决的问题 |
| --- | --- |
| [LLM 基础设施：模型怎样成为可靠服务](../chapters/part4-serving-runtime/llm-infrastructure.md) | 一次调用经过哪些层，延迟、成本与可靠性由谁共同决定？ |
| [推理服务的性能与容量：延迟、吞吐与 KV Cache 怎样互相制约](../chapters/part4-serving-runtime/inference-performance-capacity.md) | 为什么会慢、排队或显存不足，容量又该怎样判断？ |
| [推理服务的控制面：路由、扩缩容与可靠交付](../chapters/part4-serving-runtime/serving-control-plane.md) | 流量怎样找到合适实例，服务怎样扩展、发布、回退与恢复？ |
