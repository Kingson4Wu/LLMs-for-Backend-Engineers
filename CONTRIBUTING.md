# 参与改进 / Contributing

欢迎内容勘误、英文审校、示例和阅读体验改进。提交问题时注明文章 URL、语言、原文片段、期望修改；排版问题附浏览器、屏幕宽度和截图。请勿把 API key 或个人笔记上传到 issue。

## 内容规范

- 中文原稿在 `book/chapters/`，按三层依赖结构组织；保持描述性文件名与稳定文章 ID。
- 一篇文件只保留一个一级标题。新增文章同步 `book/catalog.json`；目前中英两版均已公开阅读，还需同步英文正文、目录与翻译状态，并分别生成两版 SUMMARY。不能只增加中文条目而留下不完整的已发布译本。
- 工程类比需注明适用边界，避免将概率行为描述为确定性保证。
- 数学使用 Markdown 数学语法，代码使用明确语言的 fenced block；图像有可读 alt，不用图片代替可选中的正文。
- 链接优先指向本书相对路径；跨章链接保留扩展名或已支持的省略形式，不写死当前部署域名。
- 图像、字体与引用记录来源；不要复制参考项目的作者身份或未经核对的素材。

## 英文翻译

英文按中文文章路径镜像到 `book/translations/en/`。术语表为 `glossary.md`。保留公式、示例结构和可执行代码语义；技术含义优先于逐字对应。

`status.json` 明确区分 `reviewed-by-agent` 与 `human-reviewed`，不得把机器检查标成人工审校。原文改变时校验失败，应更新翻译后再更新 hash。文章数量或标题一致不代表翻译质量已获保证。

`editions.json` 的 `published` 表示该版纳入网站和发行清单，不表示已部署上线或经过人工审校。目前网站的英文审校提示为整版文案；即使个别文章改为 `human-reviewed`，整版仍保留“待人工审校”，不能仅修改状态文件就宣称全书已完成审校。

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

出版变更另需 HTML/EPUB/PDF 样张验收；具体命令见 [LOCAL_DEVELOPMENT.md](LOCAL_DEVELOPMENT.md)。每次提交围绕一个逻辑变更，使用简洁祈使句，如 `Fix EPUB chapter navigation`。

## 许可状态

书籍内容与源码均按 [MIT License](LICENSE) 发布。贡献内容须由贡献者有权按同一许可证提交，并保留必要的来源与归属说明。
