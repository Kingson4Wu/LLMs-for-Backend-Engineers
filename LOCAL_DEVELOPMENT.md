# 本地开发与出版

除明确标注外，每个命令块都从仓库根目录开始执行。Windows 的出版命令建议在 WSL 中执行；`start_docs.bat` 仅用于启动网站，不能代替 Pandoc/TeX 环境。

## 网站

主站使用 Astro；中文原稿保留在 `book/chapters/`。Node.js 22.12+、npm 9.6.5+、Python 3.11+；CI 使用 Node 24 和 Python 3.11。依赖通过锁文件与 `npm ci` 安装。

Inter/Lora 西文字体随网站自托管；中文使用系统字体回退，不要求读者下载整套 CJK 字体，因此不同操作系统的中文观感可能略有差异。网站本身不调用 Python；Python 是内容校验和出版工具的依赖。

```bash
npm --prefix web ci
npm --prefix web run dev
```

默认开发地址为 `http://127.0.0.1:4321/LLMs-for-Backend-Engineers/`，实际端口以终端输出为准。`./start_docs.sh`（或 Windows 的 `start_docs.bat`）也会启动网站；首次缺少依赖时自动执行 `npm ci`，macOS/Linux 可用 `./start_docs.sh --install` 强制重装依赖。开发服务器不生成 Pagefind 索引，验证搜索请使用完整构建：

```bash
npm --prefix web run check
npm --prefix web test
npm --prefix web run build
npm --prefix web run check:deployment
npm --prefix web run preview
```

预览同样访问 `/LLMs-for-Backend-Engineers/`。检查根路径部署：

```bash
SITE_BASE=/ npm --prefix web run build
SITE_BASE=/ npm --prefix web run check:deployment
SITE_BASE=/ npm --prefix web run preview
```

构建、路径检查和预览须使用同一 `SITE_BASE`；回到项目子路径时，清除变量后重新构建。Windows PowerShell 使用 `$env:SITE_BASE='/'` 后执行对应 npm 命令，恢复默认用 `Remove-Item Env:SITE_BASE`。Astro 7 的预览可能在后台运行；可在 `web/` 执行 `npx astro preview stop` 停止预览，再切换配置。

`SITE_PREVIEW=true` 在构建时为主站页面添加 noindex，并写入禁止爬取的 robots.txt；这不是访问控制，也不应视为所有下载文件都能保密。PR 工作流目前只保存构建 artifact，不自动创建公开预览站。`web/dist/` 是生成目录，不修改其中的文件。

笔记备份以“语言 + 文章”为单位导出，只能导回同一语言的同一篇文章；重复笔记 ID 会跳过。数据存在浏览器当前 origin 的 localStorage 中，切换域名、协议或端口不会自动迁移。清理浏览器数据前应导出。阅读位置会优先恢复到最近的小节；旧版仅保存阅读比例的数据仍可使用。笔记备份会保存选文前后上下文与所属小节，正文小幅改动后可重新定位；无法唯一匹配的选文会保留笔记，但不再显示定位高亮。

## 内容与翻译

`book/catalog.json` 是中文篇章顺序与分组的权威索引；`book/editions.json` 定义语言入口。英文目录和正文位于 `book/translations/en/`，同一篇文章的 ID 与相对路径必须一致。语言只有在完整来源可用时才标记 published；它表示纳入网站和发行清单，不等于已部署或人工审校完成。当前为中文原文和英文译文，各含导读、前言与 18 篇正文。

修改篇名时同步正文 H1 和对应语言的 catalog 标题：网站从 H1 取文章标题，旧站导航从 catalog 生成。中英 SUMMARY 都是生成结果，不单独修改。英文术语表和审校记录为仓库辅助文档，不单独编入 20 篇正文；书中链接前往 GitHub，离线打开它们仍需要网络。

```bash
python3 tools/book-kit/validate_book.py --write-summary
python3 tools/book-kit/validate_book.py --locale en --write-summary
python3 tools/book-kit/validate_book.py --check-links
python3 tools/book-kit/validate_book.py --locale en --check-links
python3 tools/book-kit/check_translations.py
python3 tools/book-kit/validate_figures.py
python3 -m unittest discover -s tests -v
```

`--check-links` 需要 Pandoc；Python 测试还需要 librsvg，并会重新生成中文 HTML/EPUB。中文变更后译文 hash 不匹配会失败；应实际同步与审阅译文，然后更新 `status.json`，不可仅覆盖 hash 绕过检查。术语见英文版 `glossary.md`。

两种语言各自的 `book.json` 管理书名、作者、封面、PDF 标题页等。`release_date` 是人工维护的书籍发布日期，并非本次构建日期；实际构建时间见 manifest 的 `built_at`。出版工具按 `--locale` 规范化语言和输出路径，不支持仅通过修改 JSON 的 `outputs` 任意改变输出目录。网站排版在 `web/src/styles/site.css`，HTML/EPUB 排版在 `book/styles/publication.css`，PDF 排版在 Python/LaTeX 模板；`book/styles/website.css`、`pdf.css` 及 `book/locales/` 是旧链路遗留文件，不控制 Astro 主站。

## 打印 HTML、EPUB 与 PDF

三个格式直接读取相同的目录和 Markdown；无需先构建网站。需要 Pandoc 3.x、librsvg（`rsvg-convert`）。PDF 另需 XeLaTeX/ctex 与字体。

Ubuntu / CI：

```bash
sudo apt-get update
sudo apt-get install -y pandoc librsvg2-bin fonts-noto-cjk fonts-noto-core fonts-texgyre texlive-xetex texlive-lang-chinese texlive-latex-extra epubcheck poppler-utils
```

macOS 可使用 Homebrew 安装 `pandoc librsvg`，并自行安装 MacTeX 或 TinyTeX。精简 TeX 环境还需 ctex、xecjk、babel-english、setspace、footnotehyper、fvextra、newunicodechar 等模板依赖；只有 xelatex 可执行文件不代表依赖齐全。XeLaTeX 所在目录须在 PATH（macOS 也会尝试 `/Library/TeX/texbin/xelatex`）。

默认 PDF 字体：macOS 中文 Songti SC、英文 Palatino、代码 Menlo；Linux 中文 Noto Serif CJK SC、英文 TeX Gyre Pagella、代码 Noto Sans Mono。可用 `PDF_MAINFONT`、`PDF_CJK_MAINFONT`、`PDF_MONOFONT` 覆盖默认值；若该语言 `book.json` 的 `pdf` 对象显式指定了字体，则配置优先于环境变量。发行 CI 显式为两版选择 Noto 字体，因此本地默认字体的分页不应当作 CI 页数保证。

```bash
python3 tools/book-kit/build_print_html.py --locale zh-Hans
python3 tools/book-kit/export_epub.py --locale zh-Hans
python3 tools/book-kit/export_book_pdf.py --locale zh-Hans
# 将 zh-Hans 改成 en 可生成英文版
```

结果在 `book/exported/<locale>/`，包括 `book-print.html`、`book.epub`、`book.pdf` 与 `manifest.json`。中间 AST、TeX、封面转换结果留在 `book/_build/`。打印 HTML 内嵌资源，EPUB 内含封面与内部跳转。PDF 不可用时，HTML/EPUB 仍可独立生成。

各产物单独记录 source commit、dirty 状态、源字节摘要与 SHA256。只生成一种格式不会把旧格式冒充为同一次构建；网站复制已有文件，并不自动重建或保证这些文件来自最新书稿。内容或出版工具变更后，应重建对应语言的全部格式，再运行 `npm --prefix web run build` 更新下载页。HTML/EPUB 内部内容与资源可离线阅读，外部参考链接仍需网络。

```bash
epubcheck book/exported/zh-Hans/book.epub
pdffonts book/exported/zh-Hans/book.pdf
```

格式校验不替代视觉验收：至少检查目录、最长代码、宽表、中文图题、公式和最后一篇文章。

## 发布

- PR：检查目录/链接/翻译，测试出版，构建新旧站，验证根路径与 Pages 子路径。
- main：`book/**`、`web/**`、`tools/book-kit/**` 或部署工作流变更时触发，也可手动触发。部署目录为 `web/dist/`，包含 Astro 与 HTML/EPUB，不依赖 TeX；仅 README 的修改不会触发 Pages。
- `v*` tag：触发书籍发行构建；打包器要求 `v` 后紧接数字，例如 `v1.0.0`。生成两种语言全部格式，通过校验后才上传整套 artifact 和创建 Release。PDF 通过这条独立流程提供。

Pages 部署与 Release 发布仅对上游仓库 `kingson4wu/LLMs-for-Backend-Engineers` 启用。fork 自行发布需修改仓库限制、`web/astro.config.mjs` 的站点地址和 base，以及 `web/src/lib/book.mjs`、`web/scripts/postbuild.mjs` 中的仓库/站点 URL；还需将 GitHub Pages 的 Source 设置为 GitHub Actions。

版本打包需要先在干净 checkout 中生成所有已发布语言的三个格式；每种语言内部的源摘要必须一致，文件 SHA256 必须匹配，构建记录的 commit 必须等于当前 HEAD 且 dirty 为 false。不同语言的源摘要不同是正常的：

```bash
python3 tools/book-kit/package_release.py --version v1.0.0
```

`release/` 必须不存在或为空。此命令只打包已有产物，不构建、不创建 tag、不上传；`--version` 仅指定文件名版本标签，tag 对应关系由 tag 触发的工作流和 `gh release create --verify-tag` 保证。结果含版本化文件、总清单与 SHA256SUMS。工作流不覆盖已有 Release，但这不等于开启 GitHub 平台的不可变发行设置。当前有未提交修改的开发目录无法直接作为正式发行来源。

## 旧 Honkit 兼容

旧站保留用于对照与回退。唯一构建入口为 Python 暂存构建，npm 脚本转调同一入口；不再连续执行两遍构建。

```bash
npm --prefix book ci
npm --prefix book run build
npm --prefix book run serve
```

安装依赖后，也可运行 `python3 tools/book-kit/build_honkit.py`。中文输出 `book/_book/`；加 `--locale en` 时输出 `book/_book/en/`。Honkit 固定为 6.2.2，仅保留旧站构建能力，不具备 Astro 的整套阅读交互。新站生成旧章节 `.html` 地址的兼容页，保留 hash；旧根首页升级为专属首页，并兼容已知旧首页章节书签。历史 PDF URL 仅在新站产物包含真实中文 PDF 时生成副本；main 的干净 Pages 构建通常不含 PDF，主入口使用下载页与 Releases。

## 浏览器回归

可在独立 Python 环境安装 Playwright 并安装 Chromium，启动完整构建的预览后运行：

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
# 另一个终端：npm --prefix web run preview -- --port 4322
python3 web/scripts/browser-smoke.py
```

默认检查 `http://127.0.0.1:4322/LLMs-for-Backend-Engineers/`；可用 `BOOK_PREVIEW_URL` 覆盖。脚本使用全新浏览器上下文，不读取个人浏览器数据；检查中英搜索、公式、主题、小节恢复、笔记备份/隔离、旧锚点、手机布局与无 JavaScript 阅读。截图保存在 `web/review/`。
