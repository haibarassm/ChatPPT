"""
格式化服务
将用户输入和文件内容转换为PPT大纲格式的markdown
"""

import os
from pathlib import Path
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage

from logger import LOG


class FormatterService:
    """格式化服务类 - 负责将输入转换为PPT大纲格式"""

    def __init__(self, llm, prompt_file: str = "prompts/formatter.txt"):
        """初始化格式化服务

        Args:
            llm: LangChain LLM实例
            prompt_file: prompt模板文件路径
        """
        self.llm = llm
        self.prompt_file = prompt_file
        self._formatter_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        """从文件加载formatter prompt"""
        if not os.path.exists(self.prompt_file):
            raise FileNotFoundError(f"Prompt文件不存在: {self.prompt_file}")

        try:
            with open(self.prompt_file, 'r', encoding='utf-8') as f:
                prompt = f.read()
            LOG.info(f"已加载prompt文件: {self.prompt_file}")
            return prompt
        except Exception as e:
            raise IOError(f"读取prompt文件失败: {e}")

    def reload_prompt(self):
        """重新加载prompt文件（用于调试）"""
        self._formatter_prompt = self._load_prompt()
        LOG.info("Prompt已重新加载")

    def format_to_markdown(self, user_input: str, file_info: dict) -> str:
        """调用LLM将输入转换为markdown格式

        Args:
            user_input: 用户输入
            file_info: 文件信息，包含content和images

        Returns:
            格式化后的markdown字符串
        """

        # 构建上下文信息 - 优先处理图片
        context_parts = []

        # 先处理图片（确保图片信息总是放在前面）
        if file_info.get("images"):
            images = file_info.get('images', [])
            if images:
                # 确保路径使用正斜杠，并为每张图片编号
                normalized_paths = [Path(img).as_posix() if isinstance(img, str) else str(img) for img in images]
                image_list = "\n".join([f"{i+1}. {path}" for i, path in enumerate(normalized_paths)])
                context_parts.append(f"【可用图片文件】（共{len(images)}张，请在相关幻灯片中使用）:\n{image_list}")
                LOG.debug(f"提供图片路径给LLM: {normalized_paths}")

        # 再处理文本内容
        if file_info.get("content"):
            context_parts.append(f"【其他内容】:\n{file_info['content']}")

        context = "\n\n".join(context_parts) if context_parts else "无"

        # 构建用户消息
        user_message = f"""用户输入:
{user_input}

{context}

**重要提示**:
- 如果【可用图片文件】中有提供图片，请将这些图片合理分配到相关的幻灯片中
- 每张幻灯片最多使用一张图片
- 请务必使用【可用图片文件】中列出的完整路径，不要省略或修改路径
- 图片语法应放在幻灯片要点的最后

请按照上述格式要求转换为markdown。"""

        try:
            messages = [
                SystemMessage(content=self._formatter_prompt),
                HumanMessage(content=user_message)
            ]

            response = self.llm.invoke(messages)
            result = response.content

            # 记录LLM返回的内容用于调试
            LOG.debug(f"LLM返回的markdown:\n{result}")

            return result

        except Exception as e:
            LOG.error(f"LLM调用失败: {e}")
            return f"错误: LLM调用失败 - {str(e)}"

    @property
    def prompt(self) -> str:
        """获取当前使用的prompt"""
        return self._formatter_prompt
