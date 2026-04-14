# Repository Guidelines

## 项目结构

本书使用 Honkit 构建，书籍内容在 `book/` 目录下：

- `book/book.json` — Honkit 书籍配置
- `book/SUMMARY.md` — 书籍目录导航
- `book/chapters/` — 章节内容（按三层架构组织）
- `book/styles/` — 样式文件
- `book/assets/` — 图片和封面
- `book/locales/` — 国际化文件
- `tools/book-kit/` — Python 构建工具

不要将 `_book/`、`_build/` 或 `node_modules/` 视为源代码，它们是生成的、可丢弃的。

## 构建命令

### 使用 npm

```bash
cd book
npm install
npm run build    # 构建到 book/_book/
npm run serve    # 本地预览
npm run clean    # 清理构建产物
```

### 使用 Python 工具链

```bash
python3 tools/book-kit/build_honkit.py              # 构建
python3 tools/book-kit/build_honkit.py --clean       # 清理后重建
```

## 书籍元数据

在 `book/book.json` 中管理元数据：

- `release_date` — 正式发布日期
- `language` — 语言代码（`zh-Hans` 或 `en`）
- `cover_image` — 封面图片路径
- `title_page_lines` — PDF/打印版标题页附加信息

## 内容组织

章节内容在 `book/chapters/` 下按三层架构组织：

```
book/chapters/
├── part1-math-foundations/    # 第一层：数学与机器学习基础
├── part2-llm-internal/       # 第二层：LLM 内部机制
└── part3-llm-external/      # 第三层：LLM 与外部系统的连接
```

每篇文章使用描述性文件名（如 `softmax.md`、`attention-mechanism.md`），并保持 `SUMMARY.md` 与实际阅读顺序一致。

## 样式规范

- 页面最大宽度：900px（通过 `book/styles/website.css` 控制）
- 图片居中，最大宽度 100%
- 字体渲染优化：`text-rendering: optimizeLegibility`

## GitHub Actions

- `main` 分支推送后自动构建并部署到 GitHub Pages
- 触发路径：`book/**`
- 部署目录：`book/_book/`

## Commit 规范

使用简洁的祈使句 commit 信息，例如：

- `Add AI math foundations chapter`
- `Restructure book to Honkit format`
- `Fix build output directory`

保持 commit 专注于单一逻辑变更。
