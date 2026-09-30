# 参与改进 / Contributing

欢迎内容勘误、双语对齐复核、示例和阅读体验改进。提交问题时注明文章 URL、语言、原文片段、期望修改；排版问题附浏览器、屏幕宽度和截图。请勿把 API key 或个人笔记上传到 issue。

## 内容规范

- 中文原稿在 `book/chapters/`，按四个核心部分、扩展阅读与附录组织；保持描述性文件名与稳定文章 ID。
- 一篇文件只保留一个一级标题。新增文章同步 `book/catalog.json`；目前中英两版均已公开阅读，还需同步两版正文、目录与对齐状态，并分别生成两版 SUMMARY。不能只增加单语言条目而留下不完整的已发布对应版本。
- 工程类比需注明适用边界，避免将概率行为描述为确定性保证。
- 数学使用 Markdown 数学语法，代码使用明确语言的 fenced block；图像有可读 alt，不用图片代替可选中的正文。
- 链接优先指向本书相对路径；跨章链接保留扩展名或已支持的省略形式，不写死当前部署域名。
- 图像、字体与引用记录来源；不要复制参考项目的作者身份或未经核对的素材。

## 双语对齐

中英文按对应文章路径维护；英文位于 `book/translations/en/`，术语表为 `glossary.md`。两版保留相同的公式、示例结构和可执行代码语义；技术含义优先于逐字对应。

`status.json` 记录每篇中英文对应文章的对齐 hash 与复核状态。任一版本改变时校验失败，应同步更新另一版本后再更新 hash；文章数量或标题一致本身不能证明内容已对齐。

`editions.json` 的 `published` 表示该版纳入网站和发行清单，不表示已经部署；发布前仍须完成本节所列的中英文对齐与构建验证。

## 提交前验证

以下命令从仓库根目录开始；先按 [本地开发指南](LOCAL_DEVELOPMENT.md) 安装 Python、Pandoc 和 librsvg。Python 测试会实际生成中文 HTML/EPUB，并刷新 `book/exported/zh-Hans/`，不是纯静态检查。

```bash
python3 -m unittest discover -s tests -v
python3 tools/book-kit/validate_book.py --check-links
python3 tools/book-kit/validate_book.py --locale en --check-links
python3 tools/book-kit/check_translations.py
cd web
npm ci
npm run check
npm test
npm run build
npm run check:deployment
```

出版变更另需 Markdown/HTML/EPUB/PDF 样张验收；具体命令见 [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)。每次提交围绕一个逻辑变更，使用简洁祈使句，如 `Fix EPUB chapter navigation`。

## 权利与来源

提交内容须由贡献者有权提交，并保留必要的来源与归属说明。项目尚未声明内容或代码许可证；提交不应擅自添加许可证或改变权利声明。
