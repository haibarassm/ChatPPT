import random
from typing import List, Tuple, Literal
from data_structures import SlideContent
from logger import LOG


# 定义布局方向类型
LayoutDirection = Literal['horizontal', 'vertical', 'neutral']


def get_text_density(slide_content: SlideContent) -> int:
    """
    计算文本密度（字符总数）。
    用于判断文字内容的多少。
    """
    total_chars = 0
    for point in slide_content.bullet_points:
        total_chars += len(point.get('text', ''))
    return total_chars


def get_content_layout_preference(slide_content: SlideContent) -> LayoutDirection:
    """
    根据内容特征返回首选的布局方向。

    返回：
    - 'horizontal': 左右布局（适合内容多，需要横向分栏）
    - 'vertical': 上下布局（适合内容少，图片在上/下）
    - 'neutral': 无特别偏好

    决策逻辑：
    1. 有图片的情况：
       - 内容密集（文字 > 200字 或 要点 > 6个）→ horizontal（左右分栏）
       - 内容稀疏 → vertical（上下布局）
    2. 纯文字的情况：
       - 文字 > 300字 → horizontal（两栏文字）
       - 文字 < 150字 → vertical（居中大字）
       - 中等 → neutral
    """
    has_image = bool(slide_content.image_path)
    text_density = get_text_density(slide_content)
    bullet_count = len(slide_content.bullet_points)

    if has_image:
        # 有图片的情况
        if text_density > 200 or bullet_count > 3:
            return 'horizontal'  # 内容多，左右分栏
        else:
            return 'vertical'    # 内容少，上下布局
    else:
        # 纯文字的情况
        if text_density > 300:
            return 'horizontal'  # 文字多，两栏布局
        elif text_density < 150:
            return 'vertical'    # 文字少，居中布局
        else:
            return 'neutral'


# 定义 content_type 对应的权重
CONTENT_TYPE_WEIGHTS = {
    'Title': 1,
    'Content': 2,
    'Picture': 4
}

def calculate_layout_encoding(layout_name: str) -> int:
    """
    根据 layout_name 计算其编码值。
    移除编号部分和方向标记（horizontal/vertical），只对类型进行编码。
    """
    # 移除方向标记
    cleaned_name = layout_name.replace(', horizontal', '').replace(',horizontal', '')
    cleaned_name = cleaned_name.replace(', vertical', '').replace(',vertical', '')

    # 按 ',' 分割
    parts = cleaned_name.split(', ')
    base_name = ' '.join(part.split()[0] for part in parts)  # 只保留类型部分，移除编号

    # 计算权重和
    weight_sum = sum(CONTENT_TYPE_WEIGHTS.get(part, 0) for part in base_name.split())

    return weight_sum


def calculate_content_encoding(slide_content: SlideContent) -> int:
    """
    根据 SlideContent 的成员情况计算其编码值。
    如果有 title、bullet_points 和真实存在的 image_path，则根据这些成员生成编码。

    注意：image_path 必须真实存在文件才会计入 Picture 权重。
    """
    import os

    encoding = 0
    if slide_content.title:
        encoding += CONTENT_TYPE_WEIGHTS['Title']
    if slide_content.bullet_points:
        encoding += CONTENT_TYPE_WEIGHTS['Content']
    # 只有当图片路径存在且文件真实存在时，才计入 Picture 权重
    if slide_content.image_path:
        # 构建绝对路径并检查文件是否存在
        image_full_path = os.path.join(os.getcwd(), slide_content.image_path)
        if os.path.exists(image_full_path):
            encoding += CONTENT_TYPE_WEIGHTS['Picture']
        else:
            LOG.debug(f"图片文件不存在，不使用图片布局: {image_full_path}")

    return encoding


# 通用的布局策略类，使用参数化的方式实现不同布局策略的功能。
class LayoutStrategy:
    """
    通用布局策略类，通过参数化方式来选择适合的布局组。

    布局命名规范：原有名称后加 `,horizontal` 或 `,vertical` 后缀
    例如：`Title, Content, Picture 2, horizontal` 或 `Title, Content, Picture 2, vertical`

    两阶段选择策略：
    1. 第一阶段：根据元素类型（Title/Content/Picture）筛选布局组
    2. 第二阶段：根据内容特征选择 horizontal 或 vertical 方向
    """
    def __init__(self, layout_group: List[Tuple[int, str]]):
        self.layout_group = layout_group  # 布局组成员，存储可选布局

        # 根据布局名称后缀分类
        self.horizontal_layouts = []  # 左右布局
        self.vertical_layouts = []    # 上下布局
        self.neutral_layouts = []     # 无方向标记的布局

        for layout_id, layout_name in layout_group:
            # 根据布局名称后缀分类
            if ', horizontal' in layout_name or ',horizontal' in layout_name:
                self.horizontal_layouts.append((layout_id, layout_name))
            elif ', vertical' in layout_name or ',vertical' in layout_name:
                self.vertical_layouts.append((layout_id, layout_name))
            else:
                self.neutral_layouts.append((layout_id, layout_name))

    def get_layout(self, slide_content: SlideContent) -> Tuple[int, str]:
        """
        根据 SlideContent 内容选择合适的布局。

        两阶段选择：
        1. 获取内容的首选布局方向（horizontal/vertical/neutral）
        2. 在对应方向的布局池中随机选择
        """
        # 获取内容的首选布局方向
        preference = get_content_layout_preference(slide_content)

        # 根据偏好选择布局池
        if preference == 'horizontal' and self.horizontal_layouts:
            return random.choice(self.horizontal_layouts)
        elif preference == 'vertical' and self.vertical_layouts:
            return random.choice(self.vertical_layouts)
        else:
            # 中性偏好或对应方向无可用布局，从全部布局中随机选择
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