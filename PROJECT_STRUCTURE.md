# ChatPPT 项目结构

## 📁 目录结构

```
ChatPPT/
├── app.py                  # 主入口文件（简洁，仅104行）
├── config.json             # 配置文件（支持LLM切换）
├── requirements.txt        # 依赖列表
├── .env.example            # 环境变量示例
├── start.sh / start.bat    # 启动脚本
│
├── services/               # 业务逻辑层
│   ├── __init__.py
│   ├── file_service.py     # 文件处理服务
│   ├── llm_service.py      # LLM调用服务（LangChain）
│   └── ppt_service.py      # PPT生成服务
│
├── ui/                     # 界面层
│   ├── __init__.py
│   ├── styles.py           # GitHub风格CSS
│   └── components.py       # UI组件
│
├── src/                    # 核心PPT生成逻辑
│   ├── config.py           # 配置管理（已更新支持LLM）
│   ├── data_structures.py  # 数据结构
│   ├── input_parser.py     # Markdown解析
│   ├── ppt_generator.py    # PPT生成
│   ├── layout_manager.py   # 布局管理
│   └── ...
│
├── prompts/                # Prompt模板
│   └── formatter.txt       # 格式化Prompt
│
├── inputs/                 # 输入文件示例
├── outputs/                # 生成的PPT输出
├── uploads/                # 上传文件存储
└── templates/              # PPT模板
```

## 🏗️ 架构设计

### 分层架构

```
┌─────────────────────────────────────────┐
│           app.py (主入口)                │
│         仅负责组装和启动                  │
└─────────────────┬───────────────────────┘
                  │
    ┌─────────────┴─────────────┐
    │                           │
┌───▼────────┐          ┌──────▼──────┐
│   ui/      │          │  services/  │
│ 界面层     │          │  业务逻辑层  │
│            │          │             │
│ - styles   │          │ - file      │
│ - components│         │ - llm       │
└────────────┘          │ - ppt       │
                ┌───────┴──────────┐
                │                  │
          ┌─────▼─────┐     ┌─────▼──────┐
          │   src/    │     │ LangChain  │
          │  核心逻辑  │     │   + LLM    │
          └───────────┘     └────────────┘
```

## 🔧 模块说明

### app.py (主入口)
- **职责**: 组装UI、初始化服务、绑定事件
- **代码量**: ~100行
- **特点**: 简洁清晰，易于维护

### services/ (业务逻辑层)
- **file_service.py**: 处理文件上传，支持图片/表格/文本
- **llm_service.py**: 使用LangChain调用LLM，支持多种provider
- **ppt_service.py**: 封装PPT生成逻辑

### ui/ (界面层)
- **styles.py**: GitHub风格CSS样式
- **components.py**: 可复用的UI组件

### src/ (核心逻辑)
- 原有的PPT生成逻辑，保持不变

## 🔐 安全设计

### API密钥管理
```python
# 优先级: 环境变量 > 配置文件
api_key = os.getenv("API_KEY") or config.get("api_key")
```

### 环境隔离
- `.env` 文件已加入 `.gitignore`
- 提供 `.env.example` 作为模板
- 支持多种环境变量配置

## 🚀 启动流程

```
1. 加载配置 (config.json)
   ↓
2. 初始化服务
   - FileService: 文件处理
   - LLMService: 根据provider选择LLM
   - PPTService: PPT生成
   ↓
3. 创建UI (Gradio)
   - 加载样式
   - 组装组件
   - 绑定事件
   ↓
4. 启动服务 (http://localhost:7860)
```

## 🔄 LLM切换机制

### config.json配置
```json
{
  "llm": {
    "provider": "siliconflow",  // 支持: siliconflow, ollama, openai
    "model": "Qwen/Qwen2.5-7B-Instruct",
    "temperature": 0.7
  }
}
```

### 初始化逻辑
```python
if provider == "siliconflow":
    # 使用硅基流动
elif provider == "ollama":
    # 使用本地Ollama
elif provider == "openai":
    # 使用OpenAI
```

## 📦 依赖管理

### 核心依赖
- `gradio`: Web界面
- `langchain`: LLM框架
- `langchain-openai`: OpenAI兼容接口
- `langchain-ollama`: Ollama本地模型
- `python-pptx`: PPT生成
- `pandas`: 表格处理

## 🎯 使用方式

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑.env填入API密钥

# 3. 启动应用
python app.py
# 或使用启动脚本
./start.sh  # Linux/Mac
start.bat   # Windows
```

## ✨ 特性

- ✅ **模块化**: 清晰的分层架构
- ✅ **可扩展**: 易于添加新的LLM provider
- ✅ **安全性**: API密钥优先从环境变量读取
- ✅ **易维护**: 代码职责单一，结构清晰
- ✅ **用户友好**: GitHub风格界面，支持多种文件格式
