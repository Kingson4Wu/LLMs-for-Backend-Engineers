@echo off
REM LLMs for Backend Engineers 电子书本地开发启动脚本 (Windows)
REM 用途：快速启动Docusaurus开发服务器以预览电子书

setlocal enabledelayedexpansion

echo LLMs for Backend Engineers 电子书开发服务器启动脚本
echo ====================================================

REM 检查是否已安装node
node --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 node。请先安装 Node.js。
    pause
    exit /b 1
)

REM 检查是否已安装npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到 npm。请先安装 Node.js。
    pause
    exit /b 1
)

REM 设置项目目录
set "PROJECT_DIR=%~dp0documentation"

REM 检查项目目录和package.json
if not exist "%PROJECT_DIR%" (
    echo 错误: 未找到 documentation 目录。
    pause
    exit /b 1
)

if not exist "%PROJECT_DIR%\package.json" (
    echo 错误: 未找到 package.json 文件。
    pause
    exit /b 1
)

echo 进入文档目录: %PROJECT_DIR%
cd /d "%PROJECT_DIR%"

REM 安装依赖（如果需要）
if not exist "node_modules" (
    echo 正在安装依赖...
    npm install
    if errorlevel 1 (
        echo 依赖安装失败。
        pause
        exit /b 1
    )
    echo 依赖安装完成。
) else (
    echo 检测到 node_modules 目录，跳过依赖安装。
)

echo 启动 Docusaurus 开发服务器...
echo 访问地址: http://localhost:3000
echo 按 Ctrl+C 停止服务器。

REM 启动开发服务器
npm run start