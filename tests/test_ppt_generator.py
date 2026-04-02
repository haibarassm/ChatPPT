import unittest
import os
import sys
from pptx import Presentation

# 添加 src 目录到模块搜索路径，以便可以导入 src 目录中的模块
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from data_structures import PowerPoint, Slide, SlideContent
from ppt_generator import generate_presentation, insert_image_centered_in_placeholder

class TestPPTGenerator(unittest.TestCase):
    """
    测试 ppt_generator 模块的 generate_presentation 函数，验证生成的 PowerPoint 文件内容是否符合预期。
    """

    def setUp(self):
        """
        设置测试数据和输出路径。
        """
        # 定义输入 PowerPoint 数据结构
        self.powerpoint_data = PowerPoint(
            title="ChatPPT Demo",
            slides=[
                Slide(
                    layout_id=1,
                    layout_name="Title 1",
                    content=SlideContent(title="ChatPPT Demo")
                ),
                Slide(
                    layout_id=2,
                    layout_name="Title, Content 0",
                    content=SlideContent(
                        title="2024 业绩概述",
                        bullet_points=[
                            {"text": "总收入增长15%", "level": 0},
                            {"text": "市场份额扩大至30%", "level": 0}
                        ]
                    )
                ),
                Slide(
                    layout_id=8,
                    layout_name="Title, Content, Picture 2",
                    content=SlideContent(
                        title="业绩图表",
                        bullet_points=[{"text": "OpenAI 利润不断增加", "level": 0}],
                        image_path="images/performance_chart.png"
                    )
                ),
                Slide(
                    layout_id=8,
                    layout_name="Title, Content, Picture 2",
                    content=SlideContent(
                        title="新产品发布",
                        bullet_points=[
                            {"text": "产品A: **特色功能介绍**", "level": 0},
                            {"text": "增长潜力巨大", "level": 1},
                            {"text": "新兴市场", "level": 1},
                            {"text": "**非洲**市场", "level": 2},
                            {"text": "**东南亚**市场", "level": 2},
                            {"text": "产品B: 市场定位", "level": 0}
                        ],
                        image_path="images/forecast.png"
                    )
                )
            ]
        )

        self.template_path = "templates/SimpleTemplate.pptx"  # 假设存在模板文件
        self.output_path = "outputs/test_presentation.pptx"  # 定义输出文件路径

    def test_generate_presentation(self):
        """
        测试 generate_presentation 函数生成的 PowerPoint 文件是否符合预期。
        """
        # 调用函数生成 PowerPoint 演示文稿
        generate_presentation(self.powerpoint_data, self.template_path, self.output_path)

        # 检查输出文件是否存在
        self.assertTrue(os.path.exists(self.output_path), "输出 PowerPoint 文件未找到。")

        # 打开生成的 PowerPoint 文件并验证内容
        prs = Presentation(self.output_path)
        
        # 检查演示文稿标题
        self.assertEqual(prs.core_properties.title, self.powerpoint_data.title)

        # 检查幻灯片数量
        self.assertEqual(len(prs.slides), len(self.powerpoint_data.slides))

        # 验证每张幻灯片的内容
        for idx, slide_data in enumerate(self.powerpoint_data.slides):
            slide = prs.slides[idx]

            # 验证幻灯片标题
            self.assertEqual(slide.shapes.title.text, slide_data.content.title)

            # 验证项目符号列表内容
            bullet_points = [shape.text_frame.text for shape in slide.shapes if shape.has_text_frame and shape != slide.shapes.title]
            expected_bullets = [point["text"].replace("**", "") for point in slide_data.content.bullet_points]
            for bullet, expected in zip(bullet_points, expected_bullets):
                self.assertIn(expected, bullet)

            # 验证图片路径（如果存在）
            if slide_data.content.image_path:
                images = [shape for shape in slide.shapes if shape.shape_type == 13]  # 13 为图片形状类型
                self.assertGreater(len(images), 0, f"幻灯片 {idx + 1} 应该包含图片，但未找到。")

    def test_missing_image_layout_selection(self):
        """
        测试当图片不存在时，系统会自动选择不含图片的布局。
        """
        # 需要通过 SlideBuilder 来测试布局选择逻辑
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
        from slide_builder import SlideBuilder
        from layout_manager import LayoutManager, calculate_content_encoding
        from template_manager import load_template, get_layout_mapping

        # 加载模板
        template = load_template("templates/SimpleTemplate.pptx")
        layout_mapping = get_layout_mapping(template)
        layout_manager = LayoutManager(layout_mapping)

        # 创建一个不存在的图片路径
        non_existent_image = "images/this_image_does_not_exist_12345.png"

        # 创建 SlideContent
        content = SlideContent(
            title="测试幻灯片",
            bullet_points=[{"text": "测试内容", "level": 0}],
            image_path=non_existent_image  # 不存在的图片
        )

        # 验证编码计算
        encoding = calculate_content_encoding(content)
        # 应该是 3 (Title + Content)，而不是 7 (Title + Content + Picture)
        self.assertEqual(encoding, 3, "图片不存在时，编码应该是 3 (Title + Content)")

        # 使用 SlideBuilder 构建幻灯片
        builder = SlideBuilder(layout_manager)
        builder.set_title(content.title)
        for point in content.bullet_points:
            builder.add_bullet_point(point["text"], point["level"])
        builder.set_image(content.image_path)

        slide = builder.finalize()

        # 验证选择的布局不应该是带图片的布局
        # 检查 layout_name 是否不包含 "Picture"
        self.assertNotIn("Picture", slide.layout_name,
                         f"图片不存在时，不应该选择带图片的布局，实际选择: {slide.layout_name}")

        print(f"✓ 测试通过：图片不存在时，自动选择了不含图片的布局: {slide.layout_name}")

    def test_existing_image_layout_selection(self):
        """
        测试当图片存在时，系统会选择含图片的布局。
        """
        # 需要通过 SlideBuilder 来测试布局选择逻辑
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
        from slide_builder import SlideBuilder
        from layout_manager import LayoutManager, calculate_content_encoding
        from template_manager import load_template, get_layout_mapping

        # 加载模板
        template = load_template("templates/SimpleTemplate.pptx")
        layout_mapping = get_layout_mapping(template)
        layout_manager = LayoutManager(layout_mapping)

        # 创建一个存在的图片路径
        existing_image = "images/performance_chart.png"

        # 创建 SlideContent
        content = SlideContent(
            title="测试幻灯片",
            bullet_points=[{"text": "测试内容", "level": 0}],
            image_path=existing_image  # 存在的图片
        )

        # 验证编码计算
        encoding = calculate_content_encoding(content)
        # 应该是 7 (Title + Content + Picture)
        self.assertEqual(encoding, 7, "图片存在时，编码应该是 7 (Title + Content + Picture)")

        # 使用 SlideBuilder 构建幻灯片
        builder = SlideBuilder(layout_manager)
        builder.set_title(content.title)
        for point in content.bullet_points:
            builder.add_bullet_point(point["text"], point["level"])
        builder.set_image(content.image_path)

        slide = builder.finalize()

        # 验证选择的布局应该是带图片的布局
        self.assertIn("Picture", slide.layout_name,
                      f"图片存在时，应该选择带图片的布局，实际选择: {slide.layout_name}")

        print(f"✓ 测试通过：图片存在时，选择了含图片的布局: {slide.layout_name}")

    def test_insert_image_placeholder_with_valid_image(self):
        """
        测试当图片存在时，insert_image_centered_in_placeholder 函数是否正确工作。
        """
        # 创建一个临时测试图片
        from PIL import Image as PILImage
        import tempfile

        test_image_path = "images/test_temp_image.png"
        try:
            # 创建一个简单的测试图片
            img = PILImage.new('RGB', (100, 100), color='red')
            img.save(test_image_path)

            # 创建一个带有图片 placeholder 的幻灯片
            prs = Presentation(self.template_path)
            # 找到一个有图片 placeholder 的 layout
            layout = None
            for lay in prs.slide_layouts:
                # 检查是否有图片 placeholder
                for placeholder in lay.placeholders:
                    if placeholder.placeholder_format.type == 18:
                        layout = lay
                        break
                if layout:
                    break

            if layout:
                slide = prs.slides.add_slide(layout)

                # 调用函数插入图片
                insert_image_centered_in_placeholder(slide, test_image_path)

                # 验证图片被插入
                images = [shape for shape in slide.shapes if shape.shape_type == 13]
                self.assertGreater(len(images), 0, "图片应该被成功插入")

                # 验证 placeholder 被删除
                placeholders = [shape for shape in slide.placeholders if shape.placeholder_format.type == 18]
                self.assertEqual(len(placeholders), 0, "图片插入后，placeholder 应该被删除")

                print("✓ 测试通过：图片存在时，图片被正确插入，placeholder 被删除")

        finally:
            # 清理测试图片
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

    def tearDown(self):
        """
        清理生成的文件。
        """
        if os.path.exists(self.output_path):
            os.remove(self.output_path)

if __name__ == "__main__":
    unittest.main()
