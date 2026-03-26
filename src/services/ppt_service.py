"""
PPT生成服务
封装PPT生成的核心逻辑
"""

import os
from datetime import datetime

from input_parser import parse_input_text
from ppt_generator import generate_presentation
from layout_manager import LayoutManager
from config import Config
from logger import LOG


class PPTService:
    """PPT生成服务类"""

    def __init__(self):
        self.config = Config()
        self.layout_manager = LayoutManager(self.config.layout_mapping)
        os.makedirs("outputs", exist_ok=True)

    def generate_from_markdown(self, markdown_content: str) -> tuple[str, str]:
        """根据markdown内容生成PPT

        Returns:
            (status_message, ppt_path)
        """
        try:
            # 解析markdown
            powerpoint_data, presentation_title = parse_input_text(
                markdown_content,
                self.layout_manager
            )

            # 生成输出路径
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{presentation_title}_{timestamp}.pptx"
            output_path = os.path.join("outputs", output_filename)

            # 生成PPT
            generate_presentation(
                powerpoint_data,
                self.config.ppt_template,
                output_path
            )

            LOG.info(f"PPT生成成功: {output_path}")

            status = f"✅ PPT生成成功!\n\n文件名: {output_filename}\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            return status, output_path

        except Exception as e:
            LOG.error(f"PPT生成失败: {e}")
            return f"❌ PPT生成失败: {str(e)}", None
