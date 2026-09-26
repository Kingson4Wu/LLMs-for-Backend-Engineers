# AI Agent Eval：从评测到业务质量系统

Agent 的质量不能只由最后一句回复判断。它可能调用工具、改变外部状态、在环境中失败，也可能因模型、提示词、工具或运行条件的变化而退化。Eval 的对象因此不是“裸模型”，而是一套能够完成任务、留下轨迹并接受检查的系统。

从工程上看，Agent Eval 延续了测试、验收、质检、审计、风控、人工复核和线上反馈的职责。非确定性的模型执行者让这些判断需要被显性化、自动化和持续校准。本章说明评测单元、评分器、执行轨迹和线上反馈怎样组成业务质量闭环。

传统回归测试主要验证确定性程序的契约：给定输入、依赖版本和预期状态，接口、函数或工作流是否仍产生可接受的结果。Agent Eval 不替代这些测试。工具执行器、权限规则、schema 校验和业务事务仍应通过单元、集成和端到端测试守住确定性边界。

它额外评估的是完整的非确定性任务系统：同一任务在模型、上下文、工具和运行环境共同作用下，能否以可接受的成本和风险达到外部验收条件。这里既要看最终状态，也要保留执行轨迹来归因；对于存在采样或环境波动的任务，还应通过多次 trial 观察通过率、失败模式和成本分布，而不是把单次运行当成稳定结论。

文中的案例主要参考 Anthropic 的公开工程文章，但内容按可迁移的系统职责组织，而不是逐篇摘要；参考资料列在文末。

## 评测对象、证据与评分

先拆开 Agent Eval 所需的工程组件，再把它们放回业务质量体系。

### 1. Eval 评估的不是裸模型，而是完整系统

在 AI agent 场景下，eval 评估的对象不是一个裸模型，而是一个完整系统：

```text
模型 + prompt + 工具 + scaffold + 运行环境 + grader + 任务数据
```

传统 LLM eval 更像这样：

```text
输入 prompt -> 输出回答 -> 判断答案
```

Agent eval 则更接近：

```text
任务 -> 多轮推理 -> 工具调用 -> 环境状态变化 -> 最终结果 -> trace 审计 -> grader 评分
```

所以，一个 agent 在 benchmark 上表现更好，不一定只说明模型更强，也可能是工具设计、prompt、scaffold、资源配置、grader 或运行环境更合适。

[Claude SWE-Bench Performance](https://www.anthropic.com/engineering/swe-bench-sonnet) 就说明了这一点。SWE-bench 评估的是“模型 + agent scaffold”的整体能力。Claude 3.5 Sonnet 的表现不仅来自模型能力，也来自 Bash tool、Edit tool、清晰 prompt 和可迭代执行循环。

这也是很多 AI 评测容易被误读的地方。大家习惯把分数直接归因到模型，但 agentic eval 里的变量太多，分数本身只是系统行为的结果。

![Agent eval 评估模型、prompt、工具、scaffold、运行环境、任务数据、trace 和 grader 组成的完整系统](../../assets/zh/posts/20260804-ai-agent-eval-business-quality-system/agent-eval-system.svg)

*Agent eval 的对象不是裸模型，而是模型、工具、环境、任务和评分逻辑共同组成的系统。*

### 2. Agent eval 的基本组成

[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) 把 eval 拆成几个核心概念：

- **Task**：单个测试任务，有输入和成功标准。
- **Trial**：某个 task 的一次运行。同一任务通常要跑多次，因为 agent 输出有随机性。
- **Grader**：评分逻辑，可以是代码、LLM judge 或人工。
- **Transcript / Trace**：完整执行轨迹，包括消息、工具调用、推理过程和环境变化。
- **Outcome**：最终环境状态，比最终回复更重要。
- **Eval harness**：运行 eval 的基础设施。
- **Agent harness / Scaffold**：让模型成为 agent 的执行框架。
- **Evaluation suite**：围绕某类能力或行为设计的一组任务集合。

这里最关键的区别是：**response 不等于 outcome**。

比如客服 agent 最后说“退款已经处理”，这只是 response。数据库里是否真的生成退款记录，才是 outcome。

这个区别很重要。普通聊天评测很多时候可以只看最终回答，但 agent 会调用工具、修改系统状态、影响业务流程。如果只看最后一句话，就很容易把“说得像完成了”误判成“真的完成了”。

不同任务里的 outcome 形态不一样。客服、订票、代码修改这类任务，outcome 往往体现为环境里的状态变化；研究报告、内容生成、分析总结这类任务，最终交付物本身也可能就是 outcome。关键不是形式，而是不要只看 agent 声称自己完成了什么，要看任务要求的结果是否真的成立。

### 3. Grader 通常不是单层判断

Eval 的 grader 通常有三类。

**代码型 grader** 适合确定性场景，比如单测、静态分析、类型检查、安全扫描、数据库状态检查、工具调用检查。优点是快、便宜、稳定、可复现；缺点是容易僵硬，可能无法覆盖开放式质量。

**模型型 grader** 适合开放式任务，比如 rubric 评分、自然语言断言、pairwise comparison、reference-based evaluation。优点是灵活，能处理主观质量；缺点是非确定、成本更高，而且需要人工校准。

**人工 grader** 适合高价值、高风险、主观性强的任务。人工不是绝对真理，而是当前最可信的校准层，也需要抽检、复核和一致性检查。

成熟 eval 通常不是单一 grader，而是多层判断系统。代码检查负责确定性底线，模型 judge 负责开放式质量判断，人工复核负责校准和处理高风险边界。

从工程角度看，这一点很像传统质量体系。不是所有问题都应该写成自动规则，也不是所有问题都应该交给人看。关键还是分清风险、成本和误判代价。

### 4. Capability eval 和 regression eval 要分开

[Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) 还区分了两类 eval。

**Capability eval** 问的是：

```text
这个 agent 现在能做到什么？
```

它应该包含有挑战的任务，初始通过率不必高，目的是给团队一个持续改进的目标。

**Regression eval** 问的是：

```text
这个 agent 以前能做到的事情，现在还稳定吗？
```

它应该接近 100% 通过，用来防止系统退化。

一个 capability eval 如果被模型长期稳定通过，就可以转化为 regression eval。

这两类 eval 如果混在一起，会带来很大的管理问题。能力评测通过率低是正常的，回归评测通过率低就是事故信号。一个是探索上限，一个是守住下限。指标混用之后，团队很容易既看不出系统有没有进步，也看不出系统有没有退化。

### 5. 高质量 case 来自真实任务和真实失败

高质量 eval 不应该凭空编题，而应该来自真实业务：

- 手工测试中反复检查的行为
- 用户反馈
- bug tracker
- support queue
- 线上事故
- 真实业务流程
- 专家认为不可接受的失败
- 高风险边界场景

Anthropic 的建议是，早期不必追求庞大完美的 eval suite。20 到 50 个高质量 case 就能起步。

任务要足够清楚。理想状态是：

```text
两个领域专家独立判断时，会得到相同的 pass/fail 结论。
```

每个任务最好有 reference solution。它有两个作用：一是证明任务可解，二是验证 grader 没有写错。

这里和传统业务开发非常像。真正有价值的测试用例，往往不是从测试框架里长出来的，而是从真实失败里长出来的。用户投诉、线上事故、人工反复检查的地方，才最应该沉淀成 eval case。

### 6. Trace 阅读是 agent eval 的核心能力

Agent eval 不能只看分数，必须读 trace。

读 trace 是为了判断：

- agent 是真的失败，还是 grader 错了？
- 任务说明是否有歧义？
- agent 有没有找到合理但未被预期的解法？
- 工具是否让 agent 困惑？
- 错误是否来自环境，而不是模型？
- agent 是否绕过了任务本身？
- 成本、token、工具调用是否异常？

[Writing effective tools for AI agents-using AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) 和 [Claude SWE-Bench Performance](https://www.anthropic.com/engineering/swe-bench-sonnet) 都说明，很多性能提升来自读 trace 后发现具体问题：工具描述不清、错误信息不可行动、路径容易搞错、输出太长、参数命名误导模型。

Trace 是 AI agent 的审计日志，也是 eval 迭代的主要依据。

这一点在真实系统里非常关键。分数只能告诉你“哪里可能有问题”，trace 才能告诉你“问题是怎么发生的”。不读 trace 的 eval，很容易退化成看 dashboard 猜原因。

Trace 也有边界。除非安全、合规或业务流程明确要求某些步骤必须发生，否则 grader 不应该默认把某条固定执行路径当成唯一正确路径。Agent 可能找到有效但未被预期的解法，过程检查的价值是审计风险和发现模式，而不是把开放式任务重新写死成脚本。

### 7. 生产级工具设计应该 eval-driven

[Writing effective tools for AI agents-using AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents) 提出一个关键观点：给 agent 的工具不是传统 API，而是确定性系统和非确定性 agent 之间的契约。

好工具通常具备这些特征：

- 围绕高价值工作流设计，而不是机械包装底层 API
- 返回高信号、低噪声、低 token 的上下文
- 命名清晰，有 namespace
- 参数明确，避免歧义
- 错误信息可行动
- 支持过滤、分页、截断
- 避免返回巨大列表、无关 metadata 和难理解的 ID

例如：

```text
search_logs 比 read_logs 更适合 agent
get_customer_context 比 get_customer_by_id + list_transactions + list_notes 更适合 agent
schedule_event 比 list_users + list_events + create_event 更适合 agent
```

工具不是越多越好，而是越贴近 agent 的任务分解方式越好。这一点很容易被低估。

传统 API 面向确定性的程序调用，agent tool 面向非确定性的推理和探索。两者的设计重点不一样。API 可以把底层能力暴露得很细，但 agent tool 更需要把高价值工作流、上下文压缩、错误恢复路径和人类可读语义封装进去。

所以生产级工具设计应该 eval-driven。早期原型可以先做薄一点，但一旦 agent 要稳定处理真实任务，就不能只是先设计一堆工具，然后希望 agent 会用。更可靠的方式是从 trace 里看 agent 在哪里卡住、在哪里误解、在哪里浪费 token，再反过来调整工具边界。

![从运行任务、读取 trace、归因失败、改进系统、更新 case 到回归验证的 eval 迭代闭环](../../assets/zh/posts/20260804-ai-agent-eval-business-quality-system/eval-iteration-loop.svg)

*Eval-driven 的关键不是看一次分数，而是从 trace 里归因失败，再反过来改 prompt、工具、case 和回归套件。*

### 8. Benchmark 分数不是纯模型能力

[Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise) 指出，agentic coding eval 的基础设施本身会改变分数。

在 Terminal-Bench 2.0 上，不同资源配置可以带来最高 6 个百分点的分数差异。原因是 coding agent 会安装依赖、跑测试、运行子进程、写代码、调试、消耗内存和 CPU。

资源太紧，会导致 OOM、pod error、环境失败。资源太松，又可能让 agent 通过重型依赖或暴力策略解决问题，从而改变任务难度。

因此，leaderboard 上几个百分点的差距，可能来自模型能力，也可能来自硬件、内存、时间限制、并发、网络和运行方式。

所以 agent benchmark 很难像传统单轮 QA benchmark 那样简单解释。agent 不是只在文本空间里回答问题，它会进入环境、调用工具、触发副作用。环境一变，任务难度就可能变。

### 9. 开放网络 eval 会遇到 contamination 和 eval awareness

[Eval awareness in Claude Opus 4.6's BrowseComp performance](https://www.anthropic.com/engineering/eval-awareness-browsecomp) 讨论了联网 eval 的可靠性问题。

BrowseComp 是测试模型在网上寻找难找信息的 benchmark。Anthropic 发现两类污染。

第一类是 **contamination**：benchmark 题目、答案或解题过程出现在论文、GitHub、博客、OpenReview 等公开资料里，模型搜索时可能直接撞到答案。

第二类是 **eval awareness**：模型不是偶然撞到答案，而是推断出“这可能是一个 benchmark”，然后反向搜索 benchmark 名称、数据集、代码和 answer key。

多 agent 可能放大这个风险。更多并行搜索、更高 token 消耗、更大探索空间，会增加撞到污染材料或推断出 benchmark 的概率。

这类问题在传统考试和风控里也存在，只是 AI agent 把它放大了。一个会搜索、会推理、会利用上下文的系统，不会老老实实只按出题人设想的路径解题。评测如果依赖开放网络，就必须考虑污染、泄题和绕题。

### 10. AI-resistant technical evaluation 改写了技术评测

[Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations) 讨论的是招聘技术评测。

Anthropic 原来的性能工程 take-home 很成功：候选人在模拟 accelerator 上做优化，任务真实、有深度、有宽分布，能区分强弱。

但随着 Claude 能力提升，这个测试逐渐被模型打穿。作者最后转向更 out-of-distribution 的问题，用类似 Zachtronics 的强约束编程谜题，测试候选人在新奇环境里的推理、工具构建和优化能力。

这带来一个现实权衡。它不是严格规律，但趋势很明显：

```text
越贴近真实工作，越可能被模型基于已有知识解决；
越 AI-resistant，越可能偏离真实工作。
```

AI 时代的技术评测不只是变难，而是要重新平衡真实性、区分度、AI 辅助和可验证性。

这也提醒我们，eval 不是固定不变的。只要系统能力变化，评测本身就会老化。一个过去很有效的评测，可能在新模型出现后失去区分度。评测也需要维护，不只是被执行。

## AI Eval：把业务质量判断变成可运行的系统

把上面这些点放回业务系统里看，我认为 eval 最容易被误解的地方，是把它当成 AI 时代的新测试框架。它当然需要框架和工具，但更核心的是把原来隐性的业务质量判断系统化。

### 1. Eval 是传统质量体系的显性化

从这些文章回到业务系统，我的理解是：AI eval 并不是完全新的方法论。它更像是传统工程和业务系统中这些东西的重新组合：

- 自动化测试
- 回归测试
- 验收标准
- QA checklist
- 业务质检
- 审计流程
- 风控规则
- 人工复核
- 线上监控
- 用户反馈
- 事故复盘

AI agent 出现之后，原来很多靠人类经验、业务流程和人工判断维持的质量控制，需要变成可运行、可记录、可比较、可维护的系统。

因此，AI eval 可以被理解为：

```text
传统业务质量管理在非确定性 agent 时代的显性化、自动化和概率化。
```

它不是完全新东西，但它让旧问题以更高频、更显性的方式出现。

从这个角度看，eval 更像是业务质量系统里可运行、可复现、可比较的一层信号，而不是整个质量体系本身。离线 eval 本质上仍然是有限样本，样本会过时，业务分布会变化，agent 行为也会随着模型、prompt、工具和环境变化而漂移。线上监控、A/B、用户反馈和事故复盘还是不可替代。

![AI eval 位于业务质量系统中，和自动化检查、人工复核、线上反馈、事故复盘共同工作](../../assets/zh/posts/20260804-ai-agent-eval-business-quality-system/business-quality-system.svg)

*Eval 是业务质量系统里可运行、可复现、可比较的一层信号，不是整个质量体系本身。*

### 2. Eval 和传统业务开发一样，核心都是业务抽象

传统业务开发从来不是单纯写代码，而是理解业务流程、设计边界条件、处理异常、定义状态流转、安排人工介入。

AI eval 也是一样。真正困难的不是写 grader，而是回答：

- 什么叫任务完成？
- 什么叫质量好？
- 什么叫不可接受？
- 什么情况必须转人工？
- 什么失败可以容忍？
- 什么行为虽然结果对，但过程不合规？
- 什么边界情况一定要覆盖？

传统业务开发是：

```text
把业务流程变成系统行为。
```

AI eval 是：

```text
把业务判断变成可运行的质量标准。
```

二者本质上依赖同一类能力：理解场景、抽象规则、识别边界、设计反馈闭环。

所以我不太认同把 eval 简单理解成“写测试”。写测试只是表现形式。eval 真正难的是把业务里隐性的判断标准拿出来，让它能运行、能审计、能迭代。

### 3. Eval 的核心资产不是框架，而是真实样本和领域知识

Eval 的真正壁垒不是某个框架，而是业务样本和领域知识。

有价值的 eval 资产通常来自：

- 真实用户请求
- 历史失败案例
- 线上事故
- 客服记录
- 专家判断
- 业务边界
- 高风险场景
- 反例
- 历史规则
- 不可接受行为清单

框架可以复制，但 case 背后的业务记忆、失败经验和行业 know-how 很难复制。

这和传统业务系统完全一样。真正值钱的不是 CRUD 框架，而是那些来自真实业务的异常处理、边界规则和历史经验。

一个团队如果没有真实样本，只靠想象编 eval，很容易得到一个看起来结构完整、实际上没有业务密度的评测系统。它可以跑，也可以出分数，但不一定能反映真实风险。

### 4. “自动化 + 人工确认”是成熟质量系统的基本结构

成熟系统通常不是纯自动，也不是纯人工，而是分层：

```text
高频低风险：自动化判断
高频中风险：自动化 + 抽检
低频高风险：人工确认
新型未知问题：人工处理，之后沉淀为规则或 case
```

人工不是终点，也不是绝对真理。人工是校准层。

更完整的结构是：

```text
自动检查负责规模
人工复核负责校准
线上反馈负责纠偏
事故复盘负责补盲区
```

所谓“eval 套 eval”，本质上不是荒谬，而是复杂质量系统的正常形态。关键不在于有没有多层检查，而在于每一层是否清楚回答：

- 它降低什么风险？
- 它检查什么失败模式？
- 它由谁维护？
- 它什么时候失效？
- 它和其他规则是否冲突？

如果这些问题回答不清楚，多一层 eval 只是多一层噪声。反过来，每一层都有明确职责，多层检查就是正常的质量工程。

### 5. 持续补规则是必然，但会产生 eval debt

业务系统天然会积累规则。风控系统、优惠券系统、权限系统、审批系统、客服系统，最后都会变成：

```text
主流程 + 大量例外 + 历史规则 + 特殊 case + 补丁逻辑
```

AI eval 也是如此。

持续补规则会产生 **eval debt**：

- case 越来越多，但没人清理
- 老 case 已不代表当前业务
- grader 互相冲突
- 为历史 bug 写的规则变成噪声
- 通过率很好，但线上仍然失败
- 团队只会加规则，不会删除、归并、重构

成熟 eval 不是无限堆规则，而是定期归纳和重构：

```text
个案 -> 失败模式 -> 评估维度 -> 可复用规则 -> 回归套件
```

这和传统代码重构、规则系统治理，本质上是一回事。

很多系统后期变难维护，不是因为一开始没有规则，而是因为每次出问题都只加一个局部补丁。eval 也一样。如果不定期整理失败模式，eval suite 最后会变成一堆历史情绪和局部事故的集合。

### 6. AI 的特殊性不是创造了这些问题，而是放大了这些问题

很多所谓 AI eval 的特殊问题，传统复杂系统里本来就存在：

- 非确定性：并发、分布式、缓存、网络、异步任务
- 开放式质量判断：客服质检、内容审核、搜索、推荐、风控
- 环境影响结果：机器配置、依赖版本、测试数据、网络状态
- 规则被绕过：反作弊、黑产、风控攻防、考试泄题
- 人工会错：审核、质检、标注、专家判断都可能出错

AI 的差异不在于问题类型全新，而在于：

```text
这些问题在开放式、多轮且可调用工具的 Agent 应用中出现得更频繁，也更容易直接影响业务结果。
```

这类 Agent 往往包含非确定性、多种可选路径、工具调用或环境探索。它可能在优化目标时走到出题人未预期的路径，甚至利用上下文或规则漏洞；固定工作流则可把其中一部分路径收回到确定性程序中。

所以 AI eval 的新意不在“问题从无到有”，而在“问题密度和暴露面大幅增加”。

这也是为什么很多有复杂业务系统经验的人，反而更容易理解 eval 的工程本质。它不是一个完全陌生的问题，只是以前藏在业务流程、质检流程、测试流程和人工经验里的东西，现在被 agent 放到了台前。

### 7. 懂 AI 原理有帮助，但核心能力仍是清晰思考和业务抽象

做好 eval 的核心能力不是模型炫技，而是：

- 会定义问题
- 会拆业务流程
- 会识别边界条件
- 会设计反例
- 会区分主流程和异常流程
- 会判断什么失败不可接受
- 会把专家经验转成标准
- 会从失败样本里抽象模式
- 会设计自动化和人工复核的分工

懂 AI 原理当然有帮助。比如：

- 知道 LLM judge 会漂移
- 知道 prompt 和工具描述会改变行为
- 知道上下文、token、采样会影响结果
- 知道 agent 可能走捷径
- 知道 benchmark 会被污染
- 知道要读 trace，而不是只看答案

但底层能力仍然是业务抽象、测试思维、逻辑严谨和系统设计。

可以概括为：

```text
业务抽象能力是主体；
AI 技术理解是放大器。
```

在业务 agent、产品 agent 和工作流 agent 里，这个判断尤其明显。模型评测研究、benchmark 设计、统计校准、对抗评测或基础设施评测则是另一类工作，对 AI、统计和实验设计能力的要求会更高。

这也是我觉得 eval 值得工程师重视的原因。它不是一个 AI 新名词，而是会倒逼一个人把业务判断、质量标准和系统边界讲清楚。

### 8. Eval 的目标不是证明正确，而是支持决策

复杂系统里没有绝对确认。无论传统测试还是 AI eval，都不可能证明系统永远正确。

Eval 真正服务的是工程和业务决策：

- 能不能上线？
- 能不能换模型？
- 这个 prompt 改动有没有退化？
- 这个工具设计是否更好？
- 这个 agent 是否可以处理高风险任务？
- 哪些场景必须转人工？
- 哪些失败要优先修？
- leaderboard 上的分数差异是否可信？

因此，eval 的目标不是“确认一切正确”，而是：

```text
用有限样本、有限规则、有限人工判断，持续降低不确定性，让团队能做更可靠的决策。
```

这个目标比“拿高分”更重要。分数只是决策输入，不是决策本身。如果团队不知道一个 eval 分数背后的 case、grader、环境、trace 和误差来源，这个分数本身也会变成新的幻觉。

## 小结

AI eval 不是凭空出现的新范式。

它本质上是传统业务开发中的测试、验收、质检、审计、风控、人工复核、异常处理、线上监控和规则沉淀，在 AI agent 这种非确定性执行者出现后，被重新显性化、自动化和系统化。

它和传统业务开发高度相似，因为核心都不是“写检查代码”，而是理解业务、定义成功、识别失败、处理边界、沉淀规则、组织反馈闭环。

AI 带来的变化不是这些问题从无到有，而是它们被放大：

```text
更非确定
更开放
更依赖环境
更依赖工具
更容易绕规则
更需要 trace
更需要人工校准
更需要持续维护
```

一个好的 eval 系统，本质上不是一个测试脚本集合，而是一个持续演化的业务质量系统。

它的关键资产不是 eval 框架，而是：

```text
真实样本
业务知识
失败模式
专家判断
清晰标准
人工校准
持续维护机制
```

做好 eval 的人不一定必须是最懂模型底层的人，但一定要能清晰提问、严谨抽象、理解业务、识别风险，并把隐性的判断标准转化为可运行、可审计、可迭代的系统。

## 参考资料

本文主要基于以下 Anthropic 工程文章整理：

1. [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
2. [Eval awareness in Claude Opus 4.6's BrowseComp performance](https://www.anthropic.com/engineering/eval-awareness-browsecomp)
3. [Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise)
4. [Designing AI resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)
5. [Claude SWE-Bench Performance](https://www.anthropic.com/engineering/swe-bench-sonnet)
6. [Writing effective tools for AI agents-using AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
