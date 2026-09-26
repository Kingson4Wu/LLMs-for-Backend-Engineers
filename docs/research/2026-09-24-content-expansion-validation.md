# 内容补充与验证记录

日期：2026-09-24。范围：执行已确认的[选题方案](2026-09-24-content-scope-and-reference-selection.md)，先补内容，保留现有三层分类。此次为本地书稿更新，未提交、推送或部署。

## 完成内容

新增四篇中英正文：

- [训练全景](../../book/chapters/part2-llm-internal/model-training-lifecycle.md)：用同一个瓶数问题对比预训练、SFT、偏好与奖励信号。
- [上下文与记忆](../../book/chapters/part3-llm-external/context-and-memory.md)：追踪两轮对话的信息来源、外部保存与读取、压缩损失。
- [工具调用与 Agent](../../book/chapters/part3-llm-external/tool-calling-and-agents.md)：库存查询与计算轨迹、执行边界、反馈循环，简述多 Agent、MCP 和 Skill。
- [多模态概览](../../book/chapters/part2-llm-internal/multimodal-models.md)：可选阅读，比较文本中介与多模态表示，区分观察、解释、动作。

扩写生成、RAG 与能力边界；同步修订 Transformer 和微调蒸馏中与新增解释相冲突的表述。保留既有文章 ID 和文件路径，目录现为 22 篇正文加 2 篇前置文档。导读、前言、中英 README、SUMMARY、翻译术语与状态、首页概念标签均已同步。

本轮修改的原理以原始论文和官方说明为参考，就近列于正文。参考项目仅启发选题，没有复制其具体产品表现、实验结果或训练配置。英文继续标识 AI 辅助、代理审校，不宣称人工审校。

## 内容复核

独立范围复核通过：符合全局原理定位，未扩成框架、训练或部署教程。

独立技术与双语复核通过：训练目标、生成顺序、缓存、检索与重排、外部执行以及中英文限定条件一致。复核发现的采样示例 float64 转 float32 溢出边界已通过转换后有限值检查和适用范围说明处理。

全部 24 对目录文档的标题层级、围栏类型和 Python AST 对齐。更新英文后刷新原文 SHA256；hash 用于识别版本，不证明技术或语言质量。

## 实际运行验证

- 中英 `validate_book.py --check-links`：各 22 篇正文、2 篇前置文档，通过。
- `check_translations.py`：覆盖范围、顺序与原文 hash 通过。
- Python 既有测试：12 项通过；Node 测试：5 项通过。
- `astro check`：0 errors、0 warnings、17 项既有 hints。
- 网站构建与 `check:deployment`：80 页、3625 个本地引用，通过项目子路径检查。
- 中英采样代码实际运行（PyTorch 2.6.0）：关闭 Top-K 时的排序、Top-K=1、单 token 词表、温度与 Top-P 非法值、空/二维/非有限输入、float32 溢出检查通过；温度示例数值核对通过。
- 中英独立 HTML、EPUB、PDF 均生成成功。PDF 使用草稿元数据，中文 112 页、英文 121 页；没有触发缺字门禁。导出保留未提交来源状态，不视作正式发行。
- EPUBCheck 5.4.0：两版均 0 fatal、0 error、0 warning。
- 既有 Chromium 阅读检查：公式、字体、主题、字号、专注模式、笔记备份、语言隔离、双语搜索、历史锚点、手机和无 JavaScript 阅读均通过。
- 新正文专用 Chromium 检查：9 篇新增/修订文章 × 中英两版 × 1440/390px，共 36 个页面尺寸组合通过；无横向页面溢出、KaTeX 错误或浏览器脚本错误。两版首页显示 22 篇，搜索 DPO 均命中新训练篇。

PDF 样张抽看中文训练篇、英文工具篇，手机样张抽看中文训练篇。新章节均能从 PDF 文本与目录中检出。样张抽看不等于对所有纸页逐页出版校对。

## 本地复核材料

- 浏览器截图：`web/review/content-expansion/`（生成目录，不纳入源代码）。
- 网站构建日志：`/tmp/llms-content-web-build.log`。
- 阅读检查日志：`/tmp/llms-content-browser.log`。
- PDF 日志：`/tmp/llms-content-zh-pdf.log`、`/tmp/llms-content-en-pdf.log`。
- 新正文显示检查：`/tmp/llms-content-pages.py`。最初脚本误在首页寻找只存在于阅读页的搜索按钮，修正测试入口后复跑；没有因此修改产品逻辑。

## 范围边界

没有调整三层分类，没有把本次补充扩成全书基础数学审校。初版英文审校记录中的其他基础例子仍可在后续独立修订；本次技术通过结论针对新增和改写范围。
