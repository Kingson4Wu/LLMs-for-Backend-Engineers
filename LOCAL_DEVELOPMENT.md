# 本地开发指南

本书使用 [Honkit](https://honkit.net/) 构建。

## 环境要求

- Node.js 18+（推荐：20）
- npm 9+

## 快速开始

```bash
cd book
npm install
npm run serve
```

打开 http://localhost:4000

## 构建

### 使用 npm

```bash
cd book
npm run build
```

输出到 `book/_book/`。

### 使用 Python 工具链

```bash
python3 tools/book-kit/build_honkit.py
```

Python 工具链会自动：
- 将源文件复制到临时暂存目录
- 为共享资源（assets/、styles/、diagrams/）创建符号链接
- 运行 Honkit 构建
- 输出到 `book/_book/`

### 清理

```bash
npm run clean
```

## 项目结构

```
book/
├── book.json           # Honkit 配置
├── package.json       # Node.js 依赖
├── SUMMARY.md          # 书籍导航目录
├── index.md            # 导读
├── preface.md          # 前言
├── README.md           # README（Honkit 根文件）
├── styles/
│   ├── website.css     # 网站样式
│   └── pdf.css         # PDF 样式
├── assets/
│   └── cover.svg       # 书籍封面
├── chapters/            # 章节内容
│   ├── part1-math-foundations/    # 第一层：数学基础
│   ├── part2-llm-internal/       # 第二层：LLM 内部机制
│   └── part3-llm-external/       # 第三层：外部系统
└── locales/            # 国际化文件

tools/book-kit/
├── build_honkit.py     # Honkit 构建脚本
└── book_meta.py        # 书籍元数据工具

.github/workflows/
└── deploy-docs.yml     # GitHub Pages 部署
```

## 部署

推送到 `main` 分支，GitHub Actions 将自动构建并部署到 GitHub Pages。

## 归档说明

旧的 Docusaurus 文档已移至 `archived-docusaurus/` 目录。
