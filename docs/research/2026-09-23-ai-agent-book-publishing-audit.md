# ai-agent-book 出版、多语言与仓库入口专项审计

审计日期：2026-09-23。参考项目：`/Users/kingsonwu/programming/github/ai-agent-book`，commit `22fd9c5041a378ff0019d91fe22fed9482f8b128`。本报告依据本地源码，不代表已核验线上 Release、实际下载成功率或完整构建后的视觉效果。参考仓库未修改。专属网站另见主审计。

## 结论

本文是参考项目的历史源码审计；迁移建议不是当前项目的功能清单。当前项目的实现与验证状态见 [改造与验收记录](2026-09-23-implementation-validation.md)。

值得学习的是“同一正文面向在线阅读、PDF、EPUB，配套明确入口和发布流程”的产品完整性，以及对跨格式真实问题的处理：代码换行、中文字体、SVG 图中文字、封面、目录、电子书外链、RTL。不能直接把它当作无缺陷模板：语言清单和元数据散落在多处，部分下载构建可选失败，结构检查不等于翻译同步，PDF/EPUB 章节收录也不完全一致。

## 1. PDF：独立出版排版，而非直接打印网站

- 中文脚本明确列出引言、十章、后记，经 Pandoc → XeLaTeX → ElegantBook，使用三级目录、章节编号、代码着色、两个 Lua filter、前言样式和独立封面。[build_pdf.sh:15](/Users/kingsonwu/programming/github/ai-agent-book/book/build_pdf.sh:15)、[build_pdf.sh:40](/Users/kingsonwu/programming/github/ai-agent-book/book/build_pdf.sh:40)
- `preamble.tex` 对 Unicode 符号提供回退；代码用 Menlo，并通过 fvextra 自动折行及 tcolorbox 跨页；实验、思考题用两类可跨页提示框；图题强制居中、适配 CJK 字体；章节首页保留页码。[preamble.tex:4](/Users/kingsonwu/programming/github/ai-agent-book/book/preamble.tex:4)、[preamble.tex:75](/Users/kingsonwu/programming/github/ai-agent-book/book/preamble.tex:75)、[preamble.tex:104](/Users/kingsonwu/programming/github/ai-agent-book/book/preamble.tex:104)、[preamble.tex:131](/Users/kingsonwu/programming/github/ai-agent-book/book/preamble.tex:131)、[preamble.tex:172](/Users/kingsonwu/programming/github/ai-agent-book/book/preamble.tex:172)
- 统一深蓝色通过 `structurecolor` 控制。封面为 TikZ 矢量图，带作者、v2.0 与构建日期，可在没有外部图片时重复生成；这种主题和可复现封面思路值得采用，具体 Agent 图案不适合照搬。[preamble.tex:61](/Users/kingsonwu/programming/github/ai-agent-book/book/preamble.tex:61)、[cover.tex:1](/Users/kingsonwu/programming/github/ai-agent-book/book/cover.tex:1)、[cover.tex:108](/Users/kingsonwu/programming/github/ai-agent-book/book/cover.tex:108)
- PDF 图引用与章引用通过匹配中文“图 N-M”“第 N 章”生成 LaTeX 锚点。这是围绕本书手工编号的专用处理，不是通用章节模型。[crossref.lua:16](/Users/kingsonwu/programming/github/ai-agent-book/book/crossref.lua:16)
- 中文正文字体优先 Songti SC / Heiti SC，回退 Noto Sans CJK SC；等宽 Menlo 无相同回退。英文脚本另有 Linux 内存与字体探测修复，说明每语言脚本已发生差异，不能假定统一跨平台。[preamble.tex:49](/Users/kingsonwu/programming/github/ai-agent-book/book/preamble.tex:49)、[preamble.tex:160](/Users/kingsonwu/programming/github/ai-agent-book/book/preamble.tex:160)、[English build_pdf.sh:15](/Users/kingsonwu/programming/github/ai-agent-book/book-en/build_pdf.sh:15)

**迁移建议：**先给当前书建立跨格式排版样本，覆盖数学公式、宽表、长代码、中文图题和引用；当前项目已有 XeLaTeX，应保留这部分能力，再由实际分页效果决定是否调整模板。参考实现的 MacTeX、Apple 字体依赖不应无条件照搬。

## 2. EPUB：真正的可重排电子书

- 统一脚本按语言选择正文文件、书名、作者、文件名及界面词，使用 EPUB 3、MathML、三级目录、按一级标题拆页、Kate 高亮和共享 CSS。[build_epub.sh:30](/Users/kingsonwu/programming/github/ai-agent-book/build_epub.sh:30)、[build_epub.sh:212](/Users/kingsonwu/programming/github/ai-agent-book/build_epub.sh:212)
- 以 PDF 第一页转 JPEG 作封面，意味着“只构建 EPUB”仍需 PDF 先存在，进而继承 TeX/font 的依赖。当前脚本先检查所需 PDF 与章节，不会自动构建 PDF。[build_epub.sh:197](/Users/kingsonwu/programming/github/ai-agent-book/build_epub.sh:197)
- 阿拉伯语、希伯来语输出 RTL；CSS 为代码、公式保留 LTR，区分韩文、阿拉伯文、希伯来文字体；包括深色模式、孤行控制、代码换行、图表、目录样式。[build_epub.sh:193](/Users/kingsonwu/programming/github/ai-agent-book/build_epub.sh:193)、[epub.css:35](/Users/kingsonwu/programming/github/ai-agent-book/epub.css:35)、[epub.css:85](/Users/kingsonwu/programming/github/ai-agent-book/epub.css:85)
- 名为 `flatten_epub_toc.py`，当前行为实际保留嵌套目录、移除显示编号、补扉页和目录项，也修正 RTL。不要仅凭文件名理解实现。[flatten_epub_toc.py:2](/Users/kingsonwu/programming/github/ai-agent-book/flatten_epub_toc.py:2)、[flatten_epub_toc.py:44](/Users/kingsonwu/programming/github/ai-agent-book/flatten_epub_toc.py:44)
- Lua 把实验目录链接改为 GitHub URL，避免引用 EPUB 未打包资源；但正文间 `chapterN.md` 链接被硬编码为中文 `book/` 的 GitHub 链接，英文文件名同样匹配，可能把英文读者带到中文，而且失去离线章间跳转。[epub_external_links.lua:6](/Users/kingsonwu/programming/github/ai-agent-book/epub_external_links.lua:6)
- 本地仅在已安装 EPUBCheck 时校验；CI 明确安装，所以 CI 内属于构建门禁。[build_epub.sh:241](/Users/kingsonwu/programming/github/ai-agent-book/build_epub.sh:241)、[build-latest.yml:103](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/build-latest.yml:103)

**收录边界：**中文版 PDF 与 EPUB 均只列引言、十章和后记，未收录现存 `reference-answers.md`；西班牙语收录 glossary 与 answers，葡萄牙语收录 answers，越南语收录 glossary。它们不是完全一致的跨语言出版清单。[build_pdf.sh:15](/Users/kingsonwu/programming/github/ai-agent-book/book/build_pdf.sh:15)、[build_epub.sh:44](/Users/kingsonwu/programming/github/ai-agent-book/build_epub.sh:44)、[build_epub.sh:74](/Users/kingsonwu/programming/github/ai-agent-book/build_epub.sh:74)、[build_epub.sh:184](/Users/kingsonwu/programming/github/ai-agent-book/build_epub.sh:184)

**迁移建议：**统一章节 manifest 驱动目录与打包，封面独立输出成 SVG/PNG/PDF，避免 EPUB 强依赖 PDF；区分内部章节链接和在线扩展材料链接；EPUBCheck 设为发行必需。

## 3. CI 与发布：发行入口完整，但并非原子发布

- `build-latest.yml` 在 main 内容/打包文件变动和手动触发运行；macOS runner 安装 Pandoc、Poppler、librsvg、EPUBCheck、MacTeX 与字体，缓存字体目录和 TeX tarball；PDF 按语言后台并发，EPUB 顺序构建。[build-latest.yml:8](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/build-latest.yml:8)、[build-latest.yml:83](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/build-latest.yml:83)、[build-latest.yml:194](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/build-latest.yml:194)
- 专门下载 PingFang 并通过 fontconfig 匹配；另扫 PDF 内嵌字体，防止 SVG 中文悄悄回退为日文字形。这是对真实出版质量问题的自动回归保护，但字体流计数不是通用字形正确性证明。[install_apple_fonts.sh:29](/Users/kingsonwu/programming/github/ai-agent-book/.github/scripts/install_apple_fonts.sh:29)、[verify_pdf_fonts.py:16](/Users/kingsonwu/programming/github/ai-agent-book/.github/scripts/verify_pdf_fonts.py:16)
- 只有 canonical 仓库 main 发布，其余运行上传 verification artifact；固定文件名上传已有 `latest` Release，用 `--clobber` 保持下载 URL 稳定。工作流不负责创建 latest，也未见整体 release manifest、校验和或原子切换。[build-latest.yml:244](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/build-latest.yml:244)、[build-latest.yml:254](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/build-latest.yml:254)、[build-latest.yml:293](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/build-latest.yml:293)
- 日本语 PDF 可失败而不阻断；日本语 EPUB、阿拉伯语 EPUB `continue-on-error`，只在文件存在时复制。因此一次 release 更新可能保留上次的可选语言产物；README“所有链接始终指向 main 最新构建”比实现保证更强。[build-latest.yml:203](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/build-latest.yml:203)、[build-latest.yml:233](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/build-latest.yml:233)、[build-latest.yml:288](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/build-latest.yml:288)、[README.md:25](/Users/kingsonwu/programming/github/ai-agent-book/README.md:25)
- 手动指定 ja 验证时，其 PDF 失败仍进入按目录名匹配的非阻断分支；但后续 EPUB 缺失 PDF 通常仍会失败。不能把“focused verification”解读为每阶段全部严格。
- 网站 workflow 对 PR 构建、main 部署，先构建 MkDocs 再构建 Astro，Astro 被并入 `/astro/`；两套网站并存是迁移成本，不是当前项目必须复刻的架构。[deploy-pages.yml:45](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/deploy-pages.yml:45)、[deploy-pages.yml:67](/Users/kingsonwu/programming/github/ai-agent-book/.github/workflows/deploy-pages.yml:67)

**迁移建议：**先建立单语预览/发行流水线，PR 内容校验与网站构建，main 发布网站，tag 发行固定 PDF/EPUB，另可提供滚动版。产物应标注 source commit、语言、版本、构建时间与校验和。不要把读取环境的字体成功与全书排版正确混为一谈。

## 4. 多语言：源码广覆盖，同步治理存在空白

本地目录统计：`book` 加 14 个 `book-*` 共 15 语言目录，各有 10 个正文 chapter Markdown；这说明不是仅翻译界面。不能凭文件存在或字数确认翻译质量、段落覆盖或时效。希伯来语参考答案明确尚未翻译，链接英文。[README.md:44](/Users/kingsonwu/programming/github/ai-agent-book/README.md:44)、[reference-answers.he.md:3](/Users/kingsonwu/programming/github/ai-agent-book/book-he/reference-answers.he.md:3)

| 维度 | 实际情况 |
| --- | --- |
| 正文语言目录 | 15，均有 10 章 |
| PDF main 必需 | 14，日本语可选 |
| EPUB `all` | 13，不含日本语/阿拉伯语 |
| README 结构检查发现语言 | 13，不含希伯来语/葡萄牙语（巴西） |
| 翻译同步程度 | README 承认译文可能滞后；现有检查没有正文 source hash/commit 时效校验 |

- README 除中文外多数正文位于 `docs/<locale>/README.md`，旧根 README 为跳转提示；但 he/ptbr 仍在根，形成两个例外。[README.en.md:1](/Users/kingsonwu/programming/github/ai-agent-book/README.en.md:1)、[README.md:6](/Users/kingsonwu/programming/github/ai-agent-book/README.md:6)
- `check_i18n_consistency.py` 自动扫描 `docs/*/README.md`，只核对表格列数、git clone 条数、学习建议、十章 README 存在、项目数量和中文语言切换栏。未检查正文翻译内容，也未纳入根目录 he/ptbr。2026-09-23 实跑全部通过，发现 13 语言。[check_i18n_consistency.py:81](/Users/kingsonwu/programming/github/ai-agent-book/scripts/check_i18n_consistency.py:81)、[check_i18n_consistency.py:108](/Users/kingsonwu/programming/github/ai-agent-book/scripts/check_i18n_consistency.py:108)、[check_i18n_consistency.py:197](/Users/kingsonwu/programming/github/ai-agent-book/scripts/check_i18n_consistency.py:197)
- 参考答案测试覆盖中文全部章节，但翻译侧重点是第九章，希伯来语明确豁免。[test_reference_answer_coverage.py:16](/Users/kingsonwu/programming/github/ai-agent-book/tests/test_reference_answer_coverage.py:16)
- README 说中文修改合并后统一同步。审查 `.github/workflows` 和 `scripts/` 未发现自动翻译同步流水线；不能推断不存在人工或仓库外流程。`chapter10/book-translation` 是带示例小书的实验，不能当生产译稿同步机制。[README.md:147](/Users/kingsonwu/programming/github/ai-agent-book/README.md:147)、[book-translation/README.md:27](/Users/kingsonwu/programming/github/ai-agent-book/chapter10/book-translation/README.md:27)、[book-translation/README.md:59](/Users/kingsonwu/programming/github/ai-agent-book/chapter10/book-translation/README.md:59)
- EPUB 说明尚列 13 语言，实际脚本已支持 he/ptbr 共 15；多处硬编码语言枚举已造成文档漂移。[EPUB.md:3](/Users/kingsonwu/programming/github/ai-agent-book/EPUB.md:3)、[build_epub.sh:20](/Users/kingsonwu/programming/github/ai-agent-book/build_epub.sh:20)

**迁移建议：**当前项目先中文主版 + 英文真实译文；locale 元数据统一登记。区分界面翻译、正文翻译、图片翻译、README 翻译。每篇译文保存稳定文章 ID、原文 commit/hash、译文状态（draft/reviewed/stale）；未完成版本明确提示和降级，不用语言按钮数量代表多语言完成度。

## 5. README 与贡献入口

README 首屏依次提供定位、语言、在线/下载、版本变更，再以五列表格表达章节主题、核心、正文及实验入口；后续有学习建议、安装、FAQ、贡献、贡献者、许可。其好处是读者不必理解目录结构便能开始。[README.md:1](/Users/kingsonwu/programming/github/ai-agent-book/README.md:1)、[README.md:61](/Users/kingsonwu/programming/github/ai-agent-book/README.md:61)、[README.md:122](/Users/kingsonwu/programming/github/ai-agent-book/README.md:122)

当前项目可采用同样的信息优先级：一句话定位 → 适合谁/前置知识 → 在线阅读与可靠下载 → 三层知识架构 → 推荐路线 → 本地构建 → 贡献/勘误。无需照搬赞助商、API 供应商推荐、Star History、实验列表或 15 语言入口。书籍面向后端工程师，应强调每篇内容的工程问题和阅读产出。

注意 README 标注 109 个正文实验，而结构脚本统计出 119 个项目表行，两者统计对象不同（正文实验 vs 含外部轨道/附加项目的列表），本报告不把它直接认定为错误。迁移时应让宣传数字可追溯到统一内容索引，避免类似口径歧义。

## 6. 许可与复用边界

源码根 LICENSE 标识 Apache License 2.0；README 也说明子项目可能有各自许可。[LICENSE:1](/Users/kingsonwu/programming/github/ai-agent-book/LICENSE:1)、[README.md:309](/Users/kingsonwu/programming/github/ai-agent-book/README.md:309)

这是源码事实记录，不是对全部图像、字体、依赖再发布权的法律结论。优先借鉴结构与实现思路；若实际复制代码、样式、图像或模板，应逐文件记录来源并保留对应许可/归属。作者署名、社区译者、封面图案、固定书名和 GitHub URL 均需替换为当前项目自己的元数据。

## 7. 检查执行与限制

- 已实跑 `python3 scripts/check_i18n_consistency.py`：通过，13 语言。
- 已核对全部 15 语言目录都有 10 章，遍历 PDF 构建清单、EPUB 语言分支与工作流发布分支；检查参考仓库 git status 为空。
- 尝试运行现有 EPUB/参考答案 pytest 测试，环境缺少 pytest，未运行成功；未将此写为通过，也未安装或修改参考仓库依赖。
- 未运行整书 PDF/EPUB 构建、未验证真实阅读器、未对全书译文人工审校、未核验线上 Release，因此字体视觉质量和下载可用性仍需下一阶段专项验收。
