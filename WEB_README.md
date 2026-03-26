# ChatPPT Web界面

基于Gradio的ChatPPT Web应用，支持上传文件并自动生成PPT。

## 功能特性

- 📝 **文本输入**: 直接描述想要生成的PPT内容
- 📎 **文件上传**: 支持图片、Excel、CSV、文本文件
- 🤖 **AI格式化**: 使用LangChain + LLM自动转换为PPT大纲格式
- 📊 **PPT生成**: 基于python-pptx自动生成演示文稿
- 🎨 **GitHub风格**: 简洁美观的界面设计

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

复制`.env.example`到`.env`并填入你的API密钥：

```bash
cp .env.example .env
```

编辑`.env`文件，填入你的API密钥：

```env
# 硅基流动 API Key (推荐国内用户)
SILICONFLOW_API_KEY=your_api_key_here

# 或使用OpenAI
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. 配置LLM提供商

编辑`config.json`，选择你想要的LLM提供商：

```json
{
  "llm": {
    "provider": "siliconflow",  // 可选: siliconflow, ollama, openai
    "model": "Qwen/Qwen2.5-7B-Instruct"
  }
}
```

支持的提供商：
- **siliconflow**: 硅基流动（国内推荐，性价比高）
- **ollama**: 本地运行Ollama模型
- **openai**: OpenAI官方API

### 4. 启动应用

**Linux/Mac:**
```bash
chmod +x start.sh
./start.sh
```

**Windows:**
```bash
start.bat
```

**或直接运行:**
```bash
python app.py
```

应用将在 `http://localhost:7860` 启动。

## 使用说明

1. **输入内容**: 在文本框中描述你想要生成的PPT内容
2. **上传文件**（可选）:
   - 图片: PNG, JPG, GIF等
   - 表格: Excel, CSV
   - 文档: TXT, Markdown
3. **点击生成**: 点击"生成PPT"按钮
4. **下载结果**: 在右侧下载生成的PPT文件

## 项目结构

```
ChatPPT/
├── app.py              # 主入口文件
├── config.json         # 配置文件
├── requirements.txt    # 依赖列表
├── .env.example        # 环境变量示例
├── services/           # 业务逻辑服务
│   ├── file_service.py    # 文件处理
│   ├── llm_service.py     # LLM调用
│   └── ppt_service.py     # PPT生成
├── ui/                 # UI组件
│   ├── styles.py          # 样式定义
│   └── components.py      # UI组件
└── src/                # 核心PPT生成逻辑
```

## 安全说明

- API密钥优先从环境变量读取，确保安全
- `.env`文件已加入`.gitignore`，不会被提交
- 请勿在公共代码仓库中提交包含真实密钥的配置文件

## 常见问题

**Q: 如何切换LLM提供商？**
A: 编辑`config.json`中的`llm.provider`字段，支持`siliconflow`、`ollama`、`openai`。

**Q: Ollama如何使用？**
A: 先安装并启动Ollama，然后拉取模型：`ollama pull qwen2.5:7b`

**Q: 支持哪些文件格式？**
A: 图片(PNG/JPG/GIF)、表格(XLSX/XLS/CSV)、文本(TXT/MD)

## 许可证

[MIT License](LICENSE)
