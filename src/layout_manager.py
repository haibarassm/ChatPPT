import random
from typing import List, Tuple
from data_structures import SlideContent
from logger import LOG


def estimate_content_height(slide_content: SlideContent) -> int:
    """
    估算幻灯片内容的相对高度（用于布局选择）。

    返回值说明：
    - 1-3: 内容较少，适合简单布局
    - 4-7: 内容中等，适合标准布局
    - 8+: 内容较多，需要大空间或两栏布局

    计算规则：
    - 每个要点计 1 分
    - 每个层级增加 0.5 分
    - 长文本（超过 30 字）额外计 0.5 分
    """
    score = 0
    for point in slide_content.bullet_points:
        # 基础分：每个要点 1 分
        score += 1
        # 层级加成
        score += point.get('level', 0) * 0.5
        # 长文本加成
        if len(point.get('text', '')) > 30:
            score += 0.5

    return int(score)


def get_content_category(slide_content: SlideContent) -> str:
    """
    根据内容量和类型返回内容类别。

    返回：
    - 'minimal': 内容极少（1-2 个要点，无层级）
    - 'light': 内容较少（2-4 个要点，少量层级）
    - 'medium': 内容中等（4-7 个要点，或有多层级）
    - 'heavy': 内容较多（7+ 个要点，或复杂层级）
    """
    height_score = estimate_content_height(slide_content)
    bullet_count = len(slide_content.bullet_points)

    # 检查是否有复杂层级
    has_deep_levels = any(p.get('level', 0) > 1 for p in slide_content.bullet_points)

    if bullet_count <= 2 and not has_deep_levels:
        return 'minimal'
    elif bullet_count <= 4 and not has_deep_levels:
        return 'light'
    elif bullet_count <= 7 or (bullet_count <= 5 and has_deep_levels):
        return 'medium'
    else:
        return 'heavy'

# 定义 content_type 对应的权重
CONTENT_TYPE_WEIGHTS = {
    'Title': 1,
    'Content': 2,
    'Picture': 4
}

def calculate_layout_encoding(layout_name: str) -> int:
    """
    根据 layout_name 计算其编码值。
    移除编号部分，只对类型进行编码，顺序无关。
    """
    # 移除 layout_name 中的编号部分，并按 ',' 分割
    parts = layout_name.split(', ')
    base_name = ' '.join(part.split()[0] for part in parts)  # 只保留类型部分，移除编号

    # 计算权重和
    weight_sum = sum(CONTENT_TYPE_WEIGHTS.get(part, 0) for part in base_name.split())

    return weight_sum


def calculate_content_encoding(slide_content: SlideContent) -> int:
    """
    根据 SlideContent 的成员情况计算其编码值。
    如果有 title、bullet_points 和 image_path，则根据这些成员生成编码。
    """
    encoding = 0
    if slide_content.title:
        encoding += CONTENT_TYPE_WEIGHTS['Title']
    if slide_content.bullet_points:
        encoding += CONTENT_TYPE_WEIGHTS['Content']
    if slide_content.image_path:
        encoding += CONTENT_TYPE_WEIGHTS['Picture']
    
    return encoding


# 通用的布局策略类，使用参数化的方式实现不同布局策略的功能。
class LayoutStrategy:
    """
    通用布局策略类，通过参数化方式来选择适合的布局组。
    `get_layout` 方法根据 SlideContent 内容和布局映射来返回合适的布局ID和名称。
    """
    def __init__(self, layout_group: List[Tuple[int, str]]):
        self.layout_group = layout_group  # 布局组成员，存储可选布局

    def get_layout(self, slide_content: SlideContent) -> Tuple[int, str]:
        """
        根据 SlideContent 内容和布局名称选择合适的布局。

        布局选择逻辑：
        - 优先选择适合内容量的布局（根据布局名称中的关键字）
        - "Two Content" -> 适合中等/大量内容
        - "Comparison" -> 适合对比类内容
        - "Vertical" -> 适合长文本
        """
        content_category = get_content_category(slide_content)

        # 根据内容类别和布局名称进行更细致的选择
        if content_category in ['medium', 'heavy']:
            # 优先选择两栏或大空间布局
            preferred_layouts = []
            for layout_id, layout_name in self.layout_group:
                name_lower = layout_name.lower()
                # 优先选择包含 "two content", "comparison", "vertical" 等关键字的布局
                if any(keyword in name_lower for keyword in ['two content', 'comparison', 'vertical', 'blank']):
                    preferred_layouts.append((layout_id, layout_name))

            if preferred_layouts:
                return random.choice(preferred_layouts)

        # 默认随机选择
        return random.choice(self.layout_group)

# 布局管理器类，负责根据 SlideContent 自动选择合适的布局策略。
class LayoutManager:
    """
    布局管理器根据 SlideContent 的内容（如标题、要点和图片）自动选择合适的布局策略，并随机选择一个布局。
    """
    def __init__(self, layout_mapping: dict):
        self.layout_mapping = layout_mapping  # 布局映射配置
        
        # 初始化布局策略，提前为所有布局创建策略并存储在字典中
        self.strategies = {
            1: self._create_strategy(1),  # 仅 Title
            3: self._create_strategy(3),  # Title + Content
            5: self._create_strategy(5),  # Title + Picture
            7: self._create_strategy(7)   # Title + Content + Picture
        }

        # 打印调试信息
        LOG.debug(f"LayoutManager 初始化完成:\n {self}")

    def __str__(self):
        """
        打印 LayoutManager 的调试信息，包括所有布局策略及其对应的布局组。
        """
        output = []
        output.append("LayoutManager 状态:")
        for encoding, strategy in self.strategies.items():
            layout_group = strategy.layout_group
            output.append(f"  编码 {encoding}: {len(layout_group)} 个布局")
            for layout_id, layout_name in layout_group:
                output.append(f"    - Layout ID: {layout_id}, Layout Name: {layout_name}")
        return "\n".join(output)

    def assign_layout(self, slide_content: SlideContent) -> Tuple[int, str]:
        """
        根据 SlideContent 的成员情况计算编码，并选择对应的布局策略。
        """
        # 计算 SlideContent 的编码
        encoding = calculate_content_encoding(slide_content)

        # 根据编码获取对应的布局策略
        strategy = self.strategies.get(encoding)
        if not strategy:
            raise ValueError(f"没有找到对应的布局策略，编码: {encoding}")

        # 使用对应的策略获取合适的布局
        return strategy.get_layout(slide_content)

    def _create_strategy(self, layout_type: int) -> LayoutStrategy:
        """
        根据布局类型创建通用的布局策略，并生成布局组，记录布局组的 debug 信息。
        """
        layout_group = [
            (layout_id, layout_name) for layout_name, layout_id in self.layout_mapping.items() 
            if calculate_layout_encoding(layout_name) == layout_type
        ]

        # Debug 级别日志输出，查看各个布局组的详细情况
        # LOG.debug(f"创建 {layout_type} 编码对应的布局组，共 {len(layout_group)} 个布局: {layout_group}")

        return LayoutStrategy(layout_group)