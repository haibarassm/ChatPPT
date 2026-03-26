"""
布局管理器
负责根据幻灯片内容自动选择合适的布局策略
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from data_structures import SlideContent
from logger import LOG


class PlaceholderType(Enum):
    """占位符类型枚举"""
    TITLE = 0           # 标题
    BODY = 1            # 正文内容
    PICTURE = 2         # 图片
    CHART = 3           # 图表
    TABLE = 4           # 表格
    DATE = 5            # 日期
    FOOTER = 6          # 页脚
    HEADER = 7          # 页眉
    OBJECT = 8          # 对象
    CENTER_TITLE = 10   # 居中标题
    SUBTITLE = 11       # 副标题
    VERTICAL_TITLE = 12 # 垂直标题
    ORGANIZATION_CHART = 15  # 组织结构图


@dataclass
class PlaceholderSpec:
    """占位符规格定义"""
    type: PlaceholderType
    required: bool = True
    min_index: int = 0
    max_index: int = 99


@dataclass
class LayoutSpec:
    """布局规格定义"""
    name: str
    id: int
    placeholders: List[PlaceholderSpec]
    description: str = ""


class LayoutValidator:
    """布局验证器"""

    # 标准布局规格定义
    STANDARD_LAYOUTS = {
        "Title Only": LayoutSpec(
            name="Title Only",
            id=0,
            placeholders=[PlaceholderSpec(type=PlaceholderType.TITLE)],
            description="仅包含标题"
        ),
        "Title and Content": LayoutSpec(
            name="Title and Content",
            id=1,
            placeholders=[
                PlaceholderSpec(type=PlaceholderType.TITLE),
                PlaceholderSpec(type=PlaceholderType.BODY)
            ],
            description="标题和正文内容"
        ),
        "Title and Picture": LayoutSpec(
            name="Title and Picture",
            id=2,
            placeholders=[
                PlaceholderSpec(type=PlaceholderType.TITLE),
                PlaceholderSpec(type=PlaceholderType.PICTURE)
            ],
            description="标题和图片"
        ),
        "Title, Content, and Picture": LayoutSpec(
            name="Title, Content, and Picture",
            id=3,
            placeholders=[
                PlaceholderSpec(type=PlaceholderType.TITLE),
                PlaceholderSpec(type=PlaceholderType.BODY),
                PlaceholderSpec(type=PlaceholderType.PICTURE)
            ],
            description="标题、正文和图片"
        ),
        "Two Content": LayoutSpec(
            name="Two Content",
            id=4,
            placeholders=[
                PlaceholderSpec(type=PlaceholderType.TITLE),
                PlaceholderSpec(type=PlaceholderType.BODY),
                PlaceholderSpec(type=PlaceholderType.BODY)
            ],
            description="标题和两个正文区域"
        ),
        "Comparison": LayoutSpec(
            name="Comparison",
            id=5,
            placeholders=[
                PlaceholderSpec(type=PlaceholderType.TITLE),
                PlaceholderSpec(type=PlaceholderType.BODY),
                PlaceholderSpec(type=PlaceholderType.BODY)
            ],
            description="对比布局"
        )
    }

    @classmethod
    def validate_layout_mapping(cls, layout_mapping: dict) -> Tuple[bool, List[str]]:
        """
        验证布局映射配置是否有效

        Args:
            layout_mapping: 布局名称到ID的映射

        Returns:
            (是否有效, 错误信息列表)
        """
        errors = []

        for layout_name, layout_id in layout_mapping.items():
            if layout_name not in cls.STANDARD_LAYOUTS:
                errors.append(f"未知的布局名称: {layout_name}")
            elif not isinstance(layout_id, int) or layout_id < 0:
                errors.append(f"布局ID必须是非负整数: {layout_name} -> {layout_id}")

        # 检查是否有重复的ID
        ids = list(layout_mapping.values())
        if len(ids) != len(set(ids)):
            errors.append("存在重复的布局ID")

        return len(errors) == 0, errors

    @classmethod
    def get_layout_spec(cls, layout_name: str) -> Optional[LayoutSpec]:
        """获取布局规格"""
        return cls.STANDARD_LAYOUTS.get(layout_name)

    @classmethod
    def check_placeholder_compatibility(cls, layout_name: str, content: SlideContent) -> bool:
        """
        检查布局是否与内容兼容

        Args:
            layout_name: 布局名称
            content: 幻灯片内容

        Returns:
            是否兼容
        """
        spec = cls.get_layout_spec(layout_name)
        if not spec:
            return False

        # 检查需要的占位符
        has_content = content.bullet_points and len(content.bullet_points) > 0
        has_image = content.image_path and len(str(content.image_path).strip()) > 0

        # 检查是否有足够的占位符
        body_count = sum(1 for p in spec.placeholders if p.type == PlaceholderType.BODY)
        picture_count = sum(1 for p in spec.placeholders if p.type == PlaceholderType.PICTURE)

        # 验证是否满足内容需求
        if has_content and body_count == 0:
            return False
        if has_image and picture_count == 0:
            return False

        return True


# ============================================================================
# 布局策略
# ============================================================================

class LayoutStrategy(ABC):
    """
    抽象布局策略基类
    所有布局策略都需要继承该类，并实现 get_layout 方法。
    """

    def __init__(self, fallback_layout: str = "Title Only"):
        """
        初始化布局策略

        Args:
            fallback_layout: 失败时的后备布局
        """
        self.fallback_layout = fallback_layout

    @abstractmethod
    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        """
        根据幻灯片内容返回合适的布局ID和名称

        Args:
            slide_content: 幻灯片内容
            layout_mapping: 布局名称到ID的映射

        Returns:
            (布局ID, 布局名称)
        """
        pass

    def _get_fallback_layout(self, layout_mapping: dict) -> Tuple[int, str]:
        """获取后备布局"""
        layout_id = layout_mapping.get(self.fallback_layout, 0)
        return layout_id, self.fallback_layout


class TitleOnlyStrategy(LayoutStrategy):
    """仅标题布局策略"""

    def __init__(self):
        super().__init__(fallback_layout="Title Only")

    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title Only'
        layout_id = layout_mapping.get(layout_name, 0)
        LOG.debug(f"使用布局: {layout_name} (ID: {layout_id})")
        return layout_id, layout_name


class TitleAndContentStrategy(LayoutStrategy):
    """标题和内容布局策略"""

    def __init__(self):
        super().__init__(fallback_layout="Title Only")

    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title and Content'
        layout_id = layout_mapping.get(layout_name, 1)

        # 如果映射中没有这个布局，使用后备
        if layout_id == layout_mapping.get("Title Only", 0):
            return self._get_fallback_layout(layout_mapping)

        LOG.debug(f"使用布局: {layout_name} (ID: {layout_id})")
        return layout_id, layout_name


class TitleAndPictureStrategy(LayoutStrategy):
    """标题和图片布局策略"""

    def __init__(self):
        super().__init__(fallback_layout="Title Only")

    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title and Picture'
        layout_id = layout_mapping.get(layout_name, 2)

        # 如果映射中没有这个布局，使用后备
        if layout_id == layout_mapping.get("Title Only", 0):
            return self._get_fallback_layout(layout_mapping)

        LOG.debug(f"使用布局: {layout_name} (ID: {layout_id})")
        return layout_id, layout_name


class TitleContentAndPictureStrategy(LayoutStrategy):
    """标题、内容和图片布局策略"""

    def __init__(self):
        super().__init__(fallback_layout="Title and Content")

    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Title, Content, and Picture'
        layout_id = layout_mapping.get(layout_name, 3)

        # 如果映射中没有这个布局，尝试使用 Title and Content
        if layout_id == layout_mapping.get("Title Only", 0):
            fallback_name = "Title and Content"
            layout_id = layout_mapping.get(fallback_name, 1)
            LOG.debug(f"布局 {layout_name} 不可用，使用后备: {fallback_name} (ID: {layout_id})")
            return layout_id, fallback_name

        LOG.debug(f"使用布局: {layout_name} (ID: {layout_id})")
        return layout_id, layout_name


class TwoColumnStrategy(LayoutStrategy):
    """双栏布局策略"""

    def __init__(self):
        super().__init__(fallback_layout="Title and Content")

    def get_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        layout_name = 'Two Content'
        layout_id = layout_mapping.get(layout_name, 4)

        # 如果映射中没有这个布局，使用 Title and Content
        if layout_id == layout_mapping.get("Title Only", 0):
            fallback_name = "Title and Content"
            layout_id = layout_mapping.get(fallback_name, 1)
            LOG.debug(f"布局 {layout_name} 不可用，使用后备: {fallback_name} (ID: {layout_id})")
            return layout_id, fallback_name

        LOG.debug(f"使用布局: {layout_name} (ID: {layout_id})")
        return layout_id, layout_name


# ============================================================================
# 布局组
# ============================================================================

@dataclass
class LayoutGroup:
    """布局组 - 包含多个候选布局"""
    name: str
    strategies: List[LayoutStrategy]
    description: str = ""

    def select_best_layout(self, slide_content: SlideContent, layout_mapping: dict) -> Tuple[int, str]:
        """
        从布局组中选择最佳的布局

        Args:
            slide_content: 幻灯片内容
            layout_mapping: 布局映射

        Returns:
            (布局ID, 布局名称)
        """
        for strategy in self.strategies:
            try:
                return strategy.get_layout(slide_content, layout_mapping)
            except Exception as e:
                LOG.warning(f"布局策略 {strategy.__class__.__name__} 失败: {e}")
                continue

        # 所有策略都失败，返回第一个策略的后备布局
        return self.strategies[0]._get_fallback_layout(layout_mapping)


# ============================================================================
# 布局管理器
# ============================================================================

class LayoutManager:
    """
    布局管理器
    根据幻灯片内容自动选择合适的布局策略
    """

    def __init__(self, layout_mapping: dict):
        """
        初始化布局管理器

        Args:
            layout_mapping: 布局名称到ID的映射
        """
        # 验证布局映射
        is_valid, errors = LayoutValidator.validate_layout_mapping(layout_mapping)
        if not is_valid:
            LOG.warning(f"布局映射配置有误: {errors}")
            LOG.warning("将使用默认布局映射")

        self.layout_mapping = layout_mapping

        # 定义策略
        self.strategies = {
            'Title Only': TitleOnlyStrategy(),
            'Title and Content': TitleAndContentStrategy(),
            'Title and Picture': TitleAndPictureStrategy(),
            'Title, Content, and Picture': TitleContentAndPictureStrategy(),
            'Two Content': TwoColumnStrategy(),
        }

        # 定义布局组
        self.layout_groups = {
            'content_only': LayoutGroup(
                name="仅内容",
                strategies=[TitleAndContentStrategy()],
                description="用于只有文本内容的幻灯片"
            ),
            'content_with_image': LayoutGroup(
                name="内容+图片",
                strategies=[
                    TitleContentAndPictureStrategy(),
                    TitleAndPictureStrategy(),
                    TitleAndContentStrategy()
                ],
                description="用于有内容和图片的幻灯片，按优先级降序选择"
            ),
            'image_only': LayoutGroup(
                name="仅图片",
                strategies=[TitleAndPictureStrategy()],
                description="用于只有图片的幻灯片"
            ),
            'minimal': LayoutGroup(
                name="最小化",
                strategies=[TitleOnlyStrategy()],
                description="用于只有标题的幻灯片"
            )
        }

    def assign_layout(self, slide_content: SlideContent) -> Tuple[int, str]:
        """
        根据幻灯片内容自动选择最合适的布局

        Args:
            slide_content: 幻灯片内容

        Returns:
            (布局ID, 布局名称)
        """
        # 检查是否有有效的图片路径
        has_image = slide_content.image_path and len(str(slide_content.image_path).strip()) > 0
        # 检查是否有要点
        has_bullets = slide_content.bullet_points and len(slide_content.bullet_points) > 0

        # 根据内容选择布局组
        if has_image and has_bullets:
            # 既有图片又有要点
            group = self.layout_groups['content_with_image']
            LOG.debug(f"幻灯片 '{slide_content.title}': 有图片, 有{len(slide_content.bullet_points)}个要点 -> 使用布局组: {group.name}")
            return group.select_best_layout(slide_content, self.layout_mapping)

        elif has_image:
            # 只有图片
            group = self.layout_groups['image_only']
            LOG.debug(f"幻灯片 '{slide_content.title}': 有图片, 无要点 -> 使用布局组: {group.name}")
            return group.select_best_layout(slide_content, self.layout_mapping)

        elif has_bullets:
            # 只有要点
            group = self.layout_groups['content_only']
            LOG.debug(f"幻灯片 '{slide_content.title}': 有{len(slide_content.bullet_points)}个要点, 无图片 -> 使用布局组: {group.name}")
            return group.select_best_layout(slide_content, self.layout_mapping)

        else:
            # 只有标题
            group = self.layout_groups['minimal']
            LOG.debug(f"幻灯片 '{slide_content.title}': 无图片, 无要点 -> 使用布局组: {group.name}")
            return group.select_best_layout(slide_content, self.layout_mapping)

    def get_available_layouts(self) -> List[str]:
        """获取所有可用的布局名称"""
        return list(self.strategies.keys())

    def get_layout_groups(self) -> Dict[str, LayoutGroup]:
        """获取所有布局组"""
        return self.layout_groups
