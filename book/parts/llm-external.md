# 第三部分：LLM 与外部系统

模型的参数和当前上下文只能决定下一段输出最可能是什么；它不能自己取得最新信息、调用业务系统、获得权限或证明任务完成。本部分从这条边界出发，解释应用怎样把模型生成变成可读取的结构、可执行的请求和可验证的结果。

在[全书的主线图](../index.md#全书的主线图)中，这一部分位于模型计算与服务交付之间：它增加当前证据和可执行动作，却不在运行时改写模型参数。

第一章沿一次交互建立总图。随后依次解释：资料怎样经检索、过滤和重排成为本轮证据；模型怎样提出工具调用；协议怎样使外部能力可发现；Harness、运行时和 Skill 怎样组织多轮任务；以及评测怎样检查最终质量。读完本部分，应能区分模型的提议、程序的执行和环境中的事实。

| 阅读顺序 | 解决的问题 |
| --- | --- |
| [LLM 怎样与外部世界交互：从生成到行动](../chapters/part3-llm-external/llm-external-interaction.md) | 模型生成、程序执行和外部事实之间的责任如何划分？ |
| [RAG 与上下文工程：怎样把证据带入模型](../chapters/part3-llm-external/rag-context-evidence.md) | 哪些资料应进入本轮上下文，怎样避免漏证据、错证据和越权资料？ |
| [Function Calling 与工具调用：机制、区别与本质](../chapters/part3-llm-external/function-calling-tool-use.md) | 模型如何提出结构化调用，程序又如何执行它？ |
| [从 MHS、MCP 到领域能力协议](../chapters/part3-llm-external/mhs-mcp-domain-capability-protocol.md) | 外部能力怎样获得可复用的语义和接口？ |
| [Harness、Agent Runtime 与 Skill：怎样让多轮任务可靠运行](../chapters/part3-llm-external/harness-runtime-skills.md) | 多轮任务怎样保存状态、恢复失败、控制权限并确认终态？ |
| [AI Agent Eval：从评测到业务质量系统](../chapters/part3-llm-external/agent-eval-business-quality-system.md) | 怎样用可重复的证据判断系统是否真的变好？ |
