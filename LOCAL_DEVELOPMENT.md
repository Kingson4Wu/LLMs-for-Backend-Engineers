# 本地开发指南

本文档介绍如何在本地启动和开发《LLMs for Backend Engineers》电子书项目。

## 环境要求

- Node.js (版本 20.0 或更高)
- npm (随 Node.js 自动安装)
- Git (用于版本控制)

## 快速启动

项目提供了便捷的启动脚本，以简化本地开发流程。

### Linux/macOS

运行以下命令启动开发服务器：

```bash
./start_docs.sh
```

如需强制重新安装依赖，请使用：

```bash
./start_docs.sh --install
```

如需指定端口，请使用：

```bash
./start_docs.sh --port=3001
# 或
./start_docs.sh -p 3001
```

获取帮助信息：

```bash
./start_docs.sh --help
```

启动后，电子书将可以通过 `http://localhost:3000/` 访问。

macOS用户也可以直接使用npx命令启动（需要先cd到documentation目录）：

```bash
cd documentation && npx docusaurus start
```

### Windows

双击运行 `start_docs.bat` 文件，或在命令提示符中运行：

```cmd
start_docs.bat
```

## 手动启动

如果需要手动启动，可以按以下步骤操作：

1. 进入文档目录：
```bash
cd documentation
```

2. 安装依赖（首次运行或更新后需要）：
```bash
npm install
```

3. 启动开发服务器：
```bash
npm run start
```

服务器将在 `http://localhost:3000` 上运行。

## 开发命令

项目支持以下开发命令：

- `npm start` - 启动开发服务器
- `npm run build` - 构建静态文件用于生产部署
- `npm run serve` - 本地预览构建的静态文件
- `npm run swizzle` - 自定义 Docusaurus 组件

## 目录结构

- `documentation/` - Docusaurus 项目主目录
  - `docs/` - 文档源文件
    - `chapters/` - 电子书主章节
    - `advanced_transformer/` - Transformer深度解析章节
  - `src/` - 自定义组件和样式
  - `static/` - 静态资源文件
  - `docusaurus.config.ts` - 站点配置
  - `sidebars.ts` - 侧边栏导航配置

## 故障排除

### 依赖安装问题

如果遇到依赖安装问题，请尝试：
1. 清除 npm 缓存：`npm cache clean --force`
2. 删除 node_modules 目录和 package-lock.json
3. 重新运行 `npm install`

### 端口冲突

如果 3000 端口被占用，Docusaurus 会自动尝试其他端口，如 3001、3002 等。

### 构建错误

如果遇到构建错误，请检查：
1. Node.js 版本是否满足要求
2. 依赖是否正确安装
3. 配置文件语法是否正确

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进电子书内容。

### 添加新章节

1. 在 `docs/` 目录下创建新的 Markdown 文件
2. 在 `sidebars.ts` 中添加新章节到导航栏
3. 使用适当的 front matter：

```markdown
---
sidebar_label: '章节标题'
sidebar_position: 位置编号
---

# 章节标题

内容...
```

## 联系方式

如遇到问题，请提交 Issue 或通过 GitHub 联系项目维护者。