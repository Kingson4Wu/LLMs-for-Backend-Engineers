# Docusaurus 电子书框架

这是为《LLMs for Backend Engineers》创建的Docusaurus电子书框架。

## 目录结构

- `docs/intro.md` - 电子书简介页面
- `docs/chapters/` - 包含各章节内容
  - `chapter1.md` - LLM基础概念
  - `chapter2.md` - 提示工程(Prompt Engineering)
  - `chapter3.md` - LLM集成到后端服务
  - `chapter4.md` - 数据处理与知识库
  - `chapter5.md` - 性能优化与监控
  - `chapter6.md` - 未来趋势与发展
- `docusaurus.config.ts` - 站点配置文件
- `sidebars.ts` - 侧边栏导航配置

## 开发命令

```bash
cd documentation
npm start # 在开发模式下启动网站
npm run build # 构建静态文件
npm run serve # 本地预览构建的文件
```

## 自定义

要添加新章节：
1. 在`docs/chapters/`目录下创建新的markdown文件
2. 在`sidebars.ts`中更新侧边栏配置

电子书已经在 `http://localhost:3000` 可访问。