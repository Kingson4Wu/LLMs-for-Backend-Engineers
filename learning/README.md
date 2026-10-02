# 用 AI 学习这本书

推荐把 LLM 当作基于书稿的交互导师，而不是让它做一次性总结。它应帮助你定位章节、解释因果、提出反例、检验理解，并把所有关键结论回链到可核对的书稿。

## 推荐路径：一段提示词，完整 Markdown 书稿

打开[中文首页](https://kingson4wu.github.io/Understanding-LLMs/zh-Hans/)，复制唯一的学习提示词，粘贴给 Codex、Claude、ChatGPT、DeepSeek 或其他能下载文件的 AI。提示词要求 AI 先下载完整 Markdown 书稿再开始讲解，避免把临时生成的总结当作依据；它还要求 AI 概括四个部分、标注章节和图、区分证据与推断，并一次只讲一个概念、检验一次理解。

若所用 AI 不能下载链接文件，可从[下载页](https://kingson4wu.github.io/Understanding-LLMs/zh-Hans/downloads/)取得同语言书稿后交给它。Markdown 是默认的完整学习版本；EPUB 和 print HTML 仍供更适合这些格式的工具或阅读器使用。固定版式 PDF 仅随带版本的 [GitHub Release](https://github.com/Kingson4Wu/Understanding-LLMs/releases) 发布。

对于能自主抓取网页资料的 AI，可先提供公开的[AI 学习入口](https://kingson4wu.github.io/Understanding-LLMs/ai-learning/zh-Hans.md)；它链接完整书稿、学习索引、学习契约和全书地图。站点根目录的 `llms.txt` 也会列出两种语言的入口。

## 本地源码路径

### Clone + Codex（逐图、公式和源码核对时更合适）

在仓库根目录启动 Codex。它会读取 `AGENTS.md`；先要求它阅读本文件、[全书地图](BOOK_MAP.md)、[学习索引](index.json)和所选语言的学习契约：[中文](LEARNING_CONTRACT.zh-Hans.md) / [English](LEARNING_CONTRACT.en.md)。中英文是严格对齐的对应版本，应优先读取学习者选择的同语言书稿。

## 学习产物属于学习者

如需保存问题、概念图或复习队列，复制 [WORKSPACE_TEMPLATE](WORKSPACE_TEMPLATE) 为 `learning/workspace/`。该目录被 Git 忽略，不属于书稿或发布内容。

## 从工程问题开始

适合已经遇到具体问题的读者。问题可以来自设计、排障、评审或技术判断，例如：

- “长上下文、RAG 和工具调用分别解决什么问题，应该怎样取舍？”
- “为什么 Prefill 和 Decode 的容量特征不同？”
- “从输入 token 到工具执行，一次请求实际经历了哪些层？”

助手应先定位问题位于全书链路的哪里，再解释机制、约束和相邻概念；需要时回到对应书稿，而不是只给出脱离上下文的结论。

## 按书学习

也可以直接说明目标、已有经验和可投入的时间，例如：

> 我有后端和分布式系统经验，想建立 Transformer 与推理服务的整体模型。请根据本书安排学习路径，并在每一段用问题检验我的理解。

学习不必从第一章线性开始。`BOOK_MAP.md` 给出了不同问题的入口、必要前置和可选路径；助手可以据此调整顺序和深度。

## 文件的职责

| 文件 | 用途 |
| --- | --- |
| [BOOK_MAP.md](BOOK_MAP.md) | 四部分、章节关系、问题入口与学习路径 |
| [DIALOGUE_LEARNING.md](DIALOGUE_LEARNING.md) | 对话解释、追问、引用与事实边界 |
| [AI_ENTRY.zh-Hans.md](AI_ENTRY.zh-Hans.md) | 发布到网站的中文机器学习入口 |
| `../book/` | 可核对的书稿原文、目录与图表 |

这里不包含 MCP、Skill、启动脚本或隐藏提示词。它们会把学习方式绑定到特定工具，也容易把开放的讨论变成执行预设流程；需要工具、代码或外部资料时，由当前问题决定。
