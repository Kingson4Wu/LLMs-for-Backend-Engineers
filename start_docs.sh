#!/bin/bash

# LLMs for Backend Engineers 电子书本地开发启动脚本
# 用途：快速启动Docusaurus开发服务器以预览电子书

set -e  # 遇到错误时退出

# 脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 项目根目录 (documentation目录)
PROJECT_DIR="$SCRIPT_DIR/documentation"

echo "LLMs for Backend Engineers 电子书开发服务器启动脚本"
echo "===================================================="

# 检查是否已安装node和npm
if ! command -v node &> /dev/null; then
    echo "错误: 未找到 node。请先安装 Node.js。"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "错误: 未找到 npm。请先安装 Node.js。"
    exit 1
fi

# 检查是否在正确目录
if [ ! -d "$PROJECT_DIR" ] || [ ! -f "$PROJECT_DIR/package.json" ]; then
    echo "错误: 未找到 documentation 目录或 package.json 文件。"
    echo "请在项目根目录下运行此脚本。"
    exit 1
fi

echo "进入文档目录: $PROJECT_DIR"
cd "$PROJECT_DIR"

echo "启动 Docusaurus 开发服务器..."
echo "访问地址: http://localhost:3000"
echo "按 Ctrl+C 停止服务器。"

# 处理参数
PORT=3000
INSTALL_DEPS=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --install)
            INSTALL_DEPS=true
            shift
            ;;
        --port=*)
            PORT="${1#--port=}"
            shift
            ;;
        -p)
            PORT="$2"
            shift 2
            ;;
        -h|--help)
            echo "用法: $0 [选项]"
            echo "选项:"
            echo "  --install     安装/重新安装依赖"
            echo "  --port=PORT   指定端口 (默认: 3000)"
            echo "  -p PORT       指定端口 (默认: 3000)"
            echo "  -h, --help   显示此帮助信息"
            exit 0
            ;;
        *)
            echo "未知选项: $1"
            echo "用法: $0 [--install] [--port=PORT] [-p PORT] [-h]"
            exit 1
            ;;
    esac
done

if [ "$INSTALL_DEPS" = true ]; then
    echo "正在安装依赖..."
    npm install
    echo "依赖安装完成。"
elif [ ! -d "node_modules" ]; then
    echo "正在安装依赖..."
    npm install
    echo "依赖安装完成。"
else
    echo "检测到 node_modules 目录，跳过依赖安装。"
fi

echo "使用端口: $PORT"

# 启动开发服务器
npx docusaurus start --port "$PORT"