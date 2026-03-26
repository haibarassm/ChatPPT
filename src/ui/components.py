"""
UI组件定义
"""

import gradio as gr
from .styles import GITHUB_THEME, HEADER_HTML, FOOTER_HTML


def create_header():
    """创建页面头部"""
    return gr.HTML(HEADER_HTML)


def create_footer():
    """创建页面底部"""
    return gr.HTML(FOOTER_HTML)


def create_input_section():
    """创建输入组件"""
    user_input = gr.Textbox(
        label="📝 描述您想要生成的PPT内容",
        placeholder="例如: 制作一份关于GitHub Sentinel的PPT...",
        lines=12,
        max_lines=20,
        show_label=True
    )
    return user_input


def create_output_section():
    """创建输出组件"""
    gr.Markdown("### 📊 生成结果")

    status_output = gr.Textbox(
        label="状态",
        value="等待生成...",
        interactive=False,
        lines=3
    )

    ppt_download = gr.File(
        label="📥 下载PPT",
        file_count="single",
        interactive=False
    )

    return status_output, ppt_download
