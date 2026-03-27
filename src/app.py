"""
ChatPPT Gradio应用主入口 - 聊天界面版本
"""

import gradio as gr
from typing import List, Tuple, Optional
from pathlib import Path

from config import Config
from services import FileService, LLMService, FormatterService, PPTService
from ui import create_header, create_footer

# 初始化服务
config = Config()
file_service = FileService()
llm_service = LLMService(config)
formatter_service = FormatterService(llm_service.llm)
ppt_service = PPTService()


def process_message(message: dict, history: List) -> Tuple[str, List]:
    """处理用户消息并生成回复

    Args:
        message: 用户消息（多模态格式，包含text和files）
        history: 聊天历史（新格式：包含role和content的字典列表）

    Returns:
        (回复消息, 更新后的历史记录)
    """
    # 从多模态消息中提取文本和文件
    text = message.get("text", "")
    files = message.get("files", [])

    if not text and not files:
        reply = "❌ 请输入内容或上传文件"
        # 转换为Chatbot支持的格式
        user_content = text if text else "（上传了文件）"
        history.append({"role": "user", "content": user_content})
        history.append({"role": "assistant", "content": reply})
        return reply, history

    try:
        # 构建处理进度消息
        processing_msg = "⏳ 正在处理您的请求..."

        # 处理上传的文件
        if files:
            file_count = len(files)
            file_types = set()
            for f in files:
                if isinstance(f, str):
                    ext = Path(f).suffix.lower()
                else:
                    ext = Path(f.name).suffix.lower() if hasattr(f, 'name') else ''
                if ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp']:
                    file_types.add("图片")
                elif ext in ['.xlsx', '.xls', '.csv']:
                    file_types.add("表格")
                elif ext in ['.txt', '.md']:
                    file_types.add("文本")

            file_info = file_service.process_files(files)
            file_desc = f"、".join(file_types)
            processing_msg += f"\n\n📎 已接收 {file_count} 个文件（{file_desc}）"
        else:
            file_info = {"images": [], "content": ""}

        # 调用LLM进行格式转换
        markdown_content = formatter_service.format_to_markdown(
            text or "请根据上传的文件内容生成PPT",
            file_info
        )

        # 生成PPT
        status_msg, ppt_path = ppt_service.generate_from_markdown(markdown_content)

        # 构建回复消息
        if ppt_path:
            ppt_name = Path(ppt_path).name
            reply = f"""✅ **PPT生成成功！**

**文件名：** {ppt_name}

**生成详情：**
{status_msg}

💡 您可以在下方下载框中下载生成的PPT文件。"""
        else:
            reply = f"""❌ **生成失败**

{status_msg}

💡 请检查您的输入或文件格式是否正确。"""

        # 构建用户消息内容（添加文件信息）
        if files:
            file_info_text = f"\n\n📎 附件：{len(files)} 个文件"
            user_content = text + file_info_text
        else:
            user_content = text

        # 更新历史记录（转换为Chatbot支持的格式）
        history.append({"role": "user", "content": user_content})
        history.append({"role": "assistant", "content": reply})

        return reply, history

    except Exception as e:
        import traceback
        error_detail = traceback.format_exc()
        error_msg = f"""❌ **处理失败**

**错误信息：** {str(e)}

💡 可能的原因：
- 上传的文件格式不支持
- LLM服务连接失败
- 输入内容格式不正确

请检查后重试。"""
        user_content = text if text else "（上传了文件）"
        history.append({"role": "user", "content": user_content})
        history.append({"role": "assistant", "content": error_msg})
        return error_msg, history


def create_ui():
    """创建Gradio聊天UI"""

    with gr.Blocks(title="ChatPPT - AI驱动的PPT生成工具",theme=gr.themes.Base()) as app:

        # 头部
        create_header()

        gr.Markdown("### 💬 对话生成PPT")
        gr.Markdown("告诉我您想要什么主题的PPT，或者点击📎上传文件，我会为您生成")

        # 使用说明
        gr.Markdown("""
        **使用方式：**
        - 📝 输入文字描述您想要的PPT主题
        - 📎 点击左侧📎按钮上传文件（支持图片、Excel、CSV、文本等）
        - 📂 支持同时上传多个文件
        - 🚀 点击生成按钮即可获得PPT
        """)

        # 聊天界面
        chatbot = gr.Chatbot(
            label="对话历史",
            height=350,
            show_label=True
        )

        # 多模态输入框（支持文本和文件）
        msg_input = gr.MultimodalTextbox(
            label="输入消息",
            placeholder="输入您想要生成的PPT主题，例如：制作一份关于人工智能的PPT\n\n💡 提示：可以点击左侧📎按钮上传图片、表格等文件作为参考",
            show_label=True,
            container=True,
            lines=3,
            file_count="multiple",  # 支持多文件上传
            file_types=["image", ".xlsx", ".xls", ".csv", ".txt", ".md"]  # 支持的文件类型
        )

        with gr.Row():
            submit_btn = gr.Button("🚀 生成PPT", variant="primary", size="lg", scale=2)
            clear_btn = gr.Button("🔄 清空对话", variant="secondary", size="lg", scale=1)

        # 示例说明
        gr.Examples(
            examples=[
                [{"text": "帮我生成一份关于人工智能发展历程的PPT"}],
                [{"text": "制作一份公司季度汇报PPT"}],
                [{"text": "生成一份产品介绍PPT，突出核心功能"}],
            ],
            inputs=msg_input,
            label="💡 示例提示"
        )

        # 下载区域（显示最新生成的PPT）
        ppt_download = gr.File(
            label="📥 下载最新PPT",
            file_count="single",
            interactive=False
        )

        # 使用State存储当前PPT路径
        ppt_state = gr.State(value=None)

        # 底部
        create_footer()

        # 绑定事件
        def handle_submit(message, history, current_ppt):
            """处理提交"""
            if not message:
                return history, None, None, current_ppt

            reply, updated_history = process_message(message, history)

            # 尝试从outputs目录获取最新的PPT文件
            ppt_path = None
            if "✅ PPT生成成功" in reply:
                try:
                    import glob
                    import os
                    ppt_files = glob.glob("outputs/*.pptx")
                    if ppt_files:
                        # 获取最新修改的文件
                        ppt_path = max(ppt_files, key=os.path.getmtime)
                except:
                    pass

            # 返回更新后的历史、新PPT路径、清空输入框、更新状态
            return updated_history, ppt_path, None, ppt_path

        submit_btn.click(
            fn=handle_submit,
            inputs=[msg_input, chatbot, ppt_state],
            outputs=[chatbot, ppt_download, msg_input, ppt_state]
        )

        msg_input.submit(
            fn=handle_submit,
            inputs=[msg_input, chatbot, ppt_state],
            outputs=[chatbot, ppt_download, msg_input, ppt_state]
        )

        clear_btn.click(
            fn=lambda: ([], None, None, None),
            outputs=[chatbot, ppt_download, msg_input, ppt_state]
        )

    return app


if __name__ == "__main__":
    app = create_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )
