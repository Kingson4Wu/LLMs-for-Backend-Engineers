# 项目全面重构设计方案

## 目标

将 `LLMs-for-Backend-Engineers` 打造成对后端工程师中立、专业的 LLM 知识库。重构范围：侧边栏分类、文章排序、框架性章节定位、新文章写作标准。不新增内容文章。

---

## 一、三层内容分类架构

### 分类原则

按**技术栈层次**而非主题分组：

- **第一层**：LLM 依赖的数学与机器学习基础（与具体模型无关）
- **第二层**：LLM 内部机制（Transformer、Attention、生成过程等）
- **第三层**：LLM 与外部系统的连接（RAG、外部工具调用）

---

### 第一层：数学与机器学习基础

| # | 文章 | 路径 | 前置依赖 |
|---|---|---|---|
| 1 | AI数学精要（模块入口） | math_foundations/ai-math-essentials.md | 无 |
| 2 | 向量点积与夹角 | chapters/vector_concepts/dot_product_angle.md | 无 |
| 3 | Softmax | math_foundations/softmax.md | 向量运算 |
| 4 | 激活函数 | math_foundations/activation-functions.md | Softmax、概率基础 |
| 5 | 感知机与神经网络学习 | math_foundations/perceptron-learning.md | 线性代数、激活函数 |
| 6 | 交叉熵损失 | math_foundations/cross-entropy.md | 概率论 |
| 7 | 反向传播 | math_foundations/backpropagation.md | 感知机、损失函数 |
| 8 | 梯度消失与爆炸 | math_foundations/vanishing-exploding-gradients.md | 反向传播 |
| 9 | LayerNorm | math_foundations/layer-norm.md | 归一化、梯度 |
| 10 | Embedding 原理 | embeddings/from-onehot-to-embedding.md | 神经网络基础 |

**排序原则：前置依赖驱动。**

---

### 第二层：LLM 内部机制

| # | 文章 | 路径 | 前置依赖 |
|---|---|---|---|
| 1 | Embedding 演化 | embeddings/embedding-evolution.md | Embedding 原理 |
| 2 | Transformer 架构 | advanced_transformer/transformer_architecture.md | Embedding 演化 |
| 3 | Attention 机制 | advanced_transformer/attention_mechanism.md | Transformer 架构 |
| 4 | Token 生成与采样 | advanced_transformer/llm_generation.md | Attention 机制 |
| 5 | 微调与蒸馏 | advanced_transformer/fine-tuning-and-distillation.md | Transformer 架构 |
| 6 | 优化器选择 | advanced_transformer/optimizer-selection.md | 反向传播、训练过程 |

**排序原则：从表示层到计算层，从全局视图到核心组件。**

---

### 第三层：LLM 与外部系统的连接

| # | 文章 | 路径 | 前置依赖 |
|---|---|---|---|
| 1 | RAG 与知识库 | chapters/chapter4.md | 第二层全部 |
| 2 | 外部工具调用（MCP等） | （待补充） | 第二层全部 |

**排序原则：从被动查询到主动操作。**

---

## 二、侧边栏重构

将 `docs/sidebar.ts` 从按目录平铺改为按三层架构组织：

```typescript
// 重构后的侧边栏结构
'第一层：数学与机器学习基础',
  'AI数学精要',
  '向量点积与夹角',
  'Softmax',
  '激活函数',
  '感知机与神经网络学习',
  '交叉熵损失',
  '反向传播',
  '梯度消失与爆炸',
  'LayerNorm',
  'Embedding 原理',

'第二层：LLM 内部机制',
  'Embedding 演化',
  'Transformer 架构',
  'Attention 机制',
  'Token 生成与采样',
  '微调与蒸馏',
  '优化器选择',

'第三层：LLM 与外部系统的连接',
  'RAG 与知识库',
  '外部工具调用（待补充）',
```

`intro.md` 同步更新，移除开篇免责声明，改为三层架构导航。

---

## 三、框架性章节处理

以下章节目前为占位符，统一改为"内容补充中"标注：

- `chapter2.md` → 提示工程（内容补充中）
- `chapter3.md` → 后端集成（内容补充中）
- `chapter5.md` → 性能监控（内容补充中）
- `chapter6.md` → 未来趋势（内容补充中）

---

## 四、现有文章内容审视

| 问题类型 | 检测关键词 | 处理方式 |
|---------|-----------|---------|
| 主观性修辞 | "小儿科"、"废话"、"小儿科"等 | 删除 |
| LaTeX 语法损坏 | `frac`、`cdot` 等无反斜杠的公式命令 | 转为 Unicode 数学符号 |
| 文章结构不完整 | 无 `## 小结` 或 `## 延伸阅读` | 补充 |
| 章节缺少收尾 | 正文结束后无过渡直接结束 | 添加过渡句或小结 |

---

## 五、新文章写作标准

**风格底线（不可违背）：**
1. **语气中性** — 无主观评价、无情绪化词汇（"小儿科"、"废话"、"震惊"等）
2. **受众意识** — 假设读者是写了5年代码但从没接触过AI的后端工程师
3. **直觉优先** — 先建立工程感知，数学形式化作为补充而非门槛

**结构建议（按需调整，不强制套用）：**
- 问题先行：为什么需要这个概念
- 原理展开：工程直觉 + 类比
- 形式化（可选）：数学定义 / 代码示例
- 小结（推荐）：核心要点
- 延伸阅读（推荐）：内部链接 + 外部论文

**核心原则：新文章混入现有文章后，读者不应能分辨出作者不同。**

---

## 六、文件清单

### 修改文件

| 文件 | 操作 |
|------|------|
| docs/sidebar.ts | 重构为三层结构 |
| docs/intro.md | 更新为三层导航 |
| docs/chapters/chapter1.md | 改为三层结构入口 |
| docs/chapters/chapter2-6.md | 改为"内容补充中"占位 |
| docs/CONTRIBUTING.md | 新建：写作标准文档 |

### 审视文件（无需改名）

| 文件 | 审视重点 |
|------|---------|
| docs/math_foundations/*.md | LaTeX、主观修辞、结构完整性 |
| docs/advanced_transformer/*.md | LaTeX、主观修辞、结构完整性 |
| docs/embeddings/*.md | LaTeX、主观修辞、结构完整性 |
| docs/chapters/vector_concepts/*.md | LaTeX、主观修辞、结构完整性 |
| docs/chapters/chapter4.md | LaTeX、主观修辞、结构完整性 |

---

## 七、执行顺序

1. 创建 `CONTRIBUTING.md`（写作标准固化）
2. 重构 `sidebar.ts`（三层结构落地）
3. 更新 `intro.md` 和 `chapter1.md`（入口页面）
4. 更新 chapter2-6 为占位状态
5. 审视全部现有文章（LaTeX、主观修辞、结构）
6. 提交全部变更
