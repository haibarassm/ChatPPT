@echo off
REM ChatPPT Windows启动脚本

echo 🚀 启动 ChatPPT...

REM 检查虚拟环境
if not exist ".venv" (
    echo ❌ 虚拟环境不存在，请先运行: python -m venv .venv
    pause
    exit /b 1
)

REM 激活虚拟环境
echo 📦 激活虚拟环境...
call .venv\Scripts\activate.bat

REM 安装依赖
echo 📥 安装依赖...
pip install -r requirements.txt

REM 检查环境变量
if not exist ".env" (
    echo ⚠️  未找到.env文件，请先配置API密钥
    echo 💡 复制.env.example到.env并填入你的API密钥
    pause
    exit /b 1
)

REM 启动应用
echo 🎯 启动Gradio应用...
python src/app.py

pause
