from data_structures import SlideContent, Slide
from layout_manager import LayoutManager

# SlideBuilder 类用于构建单张幻灯片并通过 LayoutManager 自动分配布局
class SlideBuilder:
    def __init__(self, layout_manager: LayoutManager):
        self.layout_manager = layout_manager  # 布局管理器实例
        self.title = ""  # 幻灯片标题
        self.bullet_points = []  # 幻灯片要点列表
        self.image_paths = []  # 幻灯片图片路径列表，支持多张图片
        self.layout_id = None  # 布局ID
        self.layout_name = None  # 布局名称

    def set_title(self, title: str):
        self.title = title  # 设置幻灯片的标题

    def add_bullet_point(self, bullet: str):
        self.bullet_points.append(bullet)  # 添加要点

    def set_image(self, image_path: str):
        """设置图片路径（兼容旧版本的单图片接口）"""
        if image_path:
            self.image_paths = [image_path]

    def add_image(self, image_path: str):
        """添加一张图片到图片列表"""
        if image_path and image_path not in self.image_paths:
            self.image_paths.append(image_path)

    def finalize(self) -> Slide:
        """
        组装并返回最终的 Slide 对象，调用 LayoutManager 自动分配布局。
        """
        # 创建 SlideContent 对象
        content = SlideContent(
            title=self.title,
            bullet_points=self.bullet_points,
            image_paths=self.image_paths
        )

        # 调用 LayoutManager 分配布局
        self.layout_id, self.layout_name = self.layout_manager.assign_layout(content)

        # 返回最终的 Slide 对象
        return Slide(layout_id=self.layout_id, layout_name=self.layout_name, content=content)
