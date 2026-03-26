import re
from typing import Optional

from data_structures import PowerPoint
from slide_builder import SlideBuilder
from layout_manager import LayoutManager
from logger import LOG  # 引入日志模块


def _extract_bullet_text(line: str) -> Optional[str]:
    """
    从一行文本中提取要点内容，支持多种格式：
    - **文本**：内容
    - - 内容
    - * 内容
    - 1. 内容
    - · 内容
    """
    line = line.strip()

    # 空行跳过
    if not line:
        return None

    # 格式1: **粗体**：内容 (如：**饮食**：营养均衡)
    bold_pattern = re.compile(r'^\*\*([^*]+)\*\*[：:]\s*(.*)$')
    match = bold_pattern.match(line)
    if match:
        title = match.group(1).strip()
        content = match.group(2).strip()
        return f"{title}：{content}" if content else title

    # 格式2: - 内容
    if line.startswith('- '):
        return line[2:].strip()

    # 格式3: * 内容
    if line.startswith('* '):
        return line[2:].strip()

    # 格式4: 数字列表 (如：1. 内容)
    numbered_pattern = re.compile(r'^\d+[\.\、]\s*(.*)$')
    match = numbered_pattern.match(line)
    if match:
        return match.group(1).strip()

    # 格式5: · 内容 (中文点)
    if line.startswith('· '):
        return line[2:].strip()

    # 格式6: 纯粗体 **内容**
    if line.startswith('**') and line.endswith('**'):
        return line[2:-2].strip()

    return None


# 解析输入文本，生成 PowerPoint 数据结构
def parse_input_text(input_text: str, layout_manager: LayoutManager) -> PowerPoint:
    """
    解析输入的文本并转换为 PowerPoint 数据结构。自动为每张幻灯片分配适当的布局。

    支持的格式：
    - 标题：# 主标题、## 幻灯片标题
    - 列表：**标题**：内容、- 内容、* 内容、1. 内容、· 内容
    - 图片：![描述](路径)
    """
    lines = input_text.split('\n')
    presentation_title = ""
    slides = []
    slide_builder: Optional[SlideBuilder] = None

    # 幻灯片标题匹配
    slide_title_pattern = re.compile(r'^##\s+(.*)')
    # 图片匹配
    image_pattern = re.compile(r'!\[.*?\]\((.*?)\)')

    for line in lines:
        original_line = line
        line = line.strip()

        # 跳过空行
        if not line:
            continue

        # 主标题 (用作 PowerPoint 的标题和文件名)
        if line.startswith('# ') and not line.startswith('##'):
            presentation_title = line[2:].strip()

            # 创建第一张幻灯片，使用 "Title Only" 布局
            first_slide_builder = SlideBuilder(layout_manager)
            first_slide_builder.set_title(presentation_title)
            slides.append(first_slide_builder.finalize())

        # 幻灯片标题
        elif line.startswith('## '):
            match = slide_title_pattern.match(line)
            if match:
                title = match.group(1).strip()

                # 如果有当前幻灯片，生成并添加到幻灯片列表中
                if slide_builder:
                    slides.append(slide_builder.finalize())

                # 创建新的 SlideBuilder
                slide_builder = SlideBuilder(layout_manager)
                slide_builder.set_title(title)

        # 图片插入
        elif line.startswith('![') and slide_builder:
            match = image_pattern.match(line)
            if match:
                image_path = match.group(1).strip()
                slide_builder.set_image(image_path)

        # 尝试提取为列表项
        else:
            bullet_text = _extract_bullet_text(original_line)
            if bullet_text and slide_builder:
                slide_builder.add_bullet_point(bullet_text)

    # 为最后一张幻灯片分配布局并添加到列表中
    if slide_builder:
        slides.append(slide_builder.finalize())

    # 返回 PowerPoint 数据结构以及演示文稿标题
    return PowerPoint(title=presentation_title, slides=slides), presentation_title

