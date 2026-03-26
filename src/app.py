"""
ChatPPT Gradio应用主入口
"""

import gradio as gr
from typing import List, Optional

from config import Config
from services import FileService, LLMService, FormatterService, PPTService
from ui import GITHUB_THEME, create_header, create_footer

# 初始化服务
config = Config()
file_service = FileService()
llm_service = LLMService(config)
formatter_service = FormatterService(llm_service.llm)
ppt_service = PPTService()

# 全局状态：累积的文件列表
accumulated_files: List[str] = []


def add_files(new_files: Optional[List]) -> str:
    """添加新文件到累积列表"""
    global accumulated_files

    if not new_files:
        if accumulated_files:
            return f"已选择 {len(accumulated_files)} 个文件"
        return "未选择文件"

    # 处理新文件
    if isinstance(new_files, list):
        for f in new_files:
            if isinstance(f, str):
                file_path = f
            elif hasattr(f, 'name'):
                file_path = f.name
            else:
                continue

            # 避免重复
            if file_path not in accumulated_files:
                accumulated_files.append(file_path)
    elif isinstance(new_files, str):
        if new_files not in accumulated_files:
            accumulated_files.append(new_files)
    elif hasattr(new_files, 'name'):
        if new_files.name not in accumulated_files:
            accumulated_files.append(new_files.name)

    return f"已选择 {len(accumulated_files)} 个文件"


def clear_files():
    """清空文件列表"""
    global accumulated_files
    accumulated_files = []
    return "未选择文件"


def process_and_generate(user_input: str, files, progress=gr.Progress()):
    """处理用户输入并生成PPT的完整流程"""

    global accumulated_files

    # 使用累积的文件列表
    use_files = accumulated_files if accumulated_files else files

    if not user_input and not use_files:
        return "❌ 请输入内容或上传文件", None

    try:
        # 处理上传的文件
        progress(0.1, desc="处理文件...")
        file_info = file_service.process_files(use_files) if use_files else {"images": [], "content": ""}

        # 调用LLM进行格式转换
        progress(0.3, desc="调用AI格式化...")
        markdown_content = formatter_service.format_to_markdown(
            user_input or "请根据上传的文件内容生成PPT",
            file_info
        )

        # 生成PPT
        progress(0.5, desc="生成PPT...")
        status_msg, ppt_path = ppt_service.generate_from_markdown(markdown_content)

        progress(1.0, desc="完成!")

        # 生成后清空文件列表
        accumulated_files = []

        return status_msg, ppt_path

    except Exception as e:
        return f"❌ 处理失败: {str(e)}", None


def clear_all():
    """清空所有内容"""
    global accumulated_files
    accumulated_files = []
    # 返回5个值对应5个输出组件
    return "", None, "未选择文件", "等待生成...", None


def create_ui():
    """创建Gradio UI - 简化布局"""

    with gr.Blocks(title="ChatPPT - AI驱动的PPT生成工具") as app:

        # 头部
        create_header()

        # 主内容行：三列并排
        with gr.Row():
            # 左列：文本输入 (scale=1 确保三列等宽)
            with gr.Column(scale=1):
                gr.Markdown("### 📝 输入")
                user_input = gr.Textbox(
                    label="描述内容",
                    placeholder="例如: 制作一份关于GitHub Sentinel的PPT...",
                    lines=12,
                    max_lines=20,
                    show_label=True
                )

            # 中列：文件操作
            with gr.Column(scale=1):
                gr.Markdown("### 📎 文件")
                gr.Markdown("""
                <div style="font-size: 11px; color: #8b949e;">
                可多次累积<br>支持图片、表格、文档
                </div>
                """)

                file_upload = gr.File(
                    label="选择文件",
                    file_count="multiple",
                    file_types=["image", ".xlsx", ".xls", ".csv", ".txt", ".md"],
                    type="filepath"
                )

                file_status = gr.Textbox(
                    label="状态",
                    value="未选择文件",
                    interactive=False
                )

            # 右列：输出结果
            with gr.Column(scale=1):
                gr.Markdown("### 📊 结果")

                status_output = gr.Textbox(
                    label="生成状态",
                    value="等待生成...",
                    interactive=False,
                    lines=5
                )

                ppt_download = gr.File(
                    label="下载PPT",
                    file_count="single",
                    interactive=False
                )

        # 操作按钮行
        with gr.Row():
            generate_btn = gr.Button("🚀 生成PPT", variant="primary", size="lg", scale=3)
            clear_btn = gr.Button("🔄 清空", variant="secondary", size="lg", scale=1)

        # 底部
        create_footer()

        # 绑定事件
        file_upload.change(
            fn=add_files,
            inputs=file_upload,
            outputs=file_status
        )

        generate_btn.click(
            fn=process_and_generate,
            inputs=[user_input, file_upload],
            outputs=[status_output, ppt_download],
            show_progress="full"
        )

        clear_btn.click(
            fn=clear_all,
            outputs=[user_input, file_upload, file_status, status_output, ppt_download]
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
