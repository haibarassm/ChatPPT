import unittest
import os
import sys
from unittest.mock import Mock, patch, MagicMock, MockOpen
from PIL import Image as PILImage

# 添加 src 目录到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))


class TestImageAdvisor(unittest.TestCase):
    """测试 image_advisor 模块的功能"""

    @patch('image_advisor.minicpm_model')
    @patch('image_advisor.sd3_generator')
    def test_score_image_relevance_mock(self, mock_sd3, mock_minicpm):
        """测试图片相关性评分功能（使用 mock）"""
        # 动态导入（此时 mock 已生效）
        from image_advisor import ImageAdvisor

        advisor = ImageAdvisor("./prompts/image_advisor.txt")

        # 创建一个临时测试图片
        test_image_path = "images/test_relevance.jpg"

        try:
            # 创建测试图片
            img = PILImage.new('RGB', (100, 100), color='blue')
            img.save(test_image_path)

            # 设置 mock 返回值
            mock_chat_response = "这张图片与主题的相关性评分是 85分"
            mock_minicpm.model.chat = MagicMock(return_value=mock_chat_response)

            # 调用评分函数
            score = advisor.score_image_relevance(test_image_path, "测试主题")

            # 验证结果
            self.assertEqual(score, 85)
            print(f"✓ 测试通过：图片相关性评分 = {score}")

        finally:
            # 清理测试图片
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

    @patch('image_advisor.minicpm_model')
    @patch('image_advisor.sd3_generator')
    def test_score_image_relevance_parse_error(self, mock_sd3, mock_minicpm):
        """测试评分解析失败时的默认值"""
        from image_advisor import ImageAdvisor

        advisor = ImageAdvisor("./prompts/image_advisor.txt")

        # 创建一个临时测试图片
        test_image_path = "images/test_relevance_error.jpg"

        try:
            # 创建测试图片
            img = PILImage.new('RGB', (100, 100), color='red')
            img.save(test_image_path)

            # Mock minicpm_model 返回无法解析的响应
            mock_minicpm.model.chat = MagicMock(return_value="无法解析的响应文本")

            # 调用评分函数
            score = advisor.score_image_relevance(test_image_path, "测试主题")

            # 应该返回默认中等分数
            self.assertEqual(score, 50)
            print(f"✓ 测试通过：解析失败时返回默认分数 {score}")

        finally:
            # 清理测试图片
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

    @patch('image_advisor.minicpm_model')
    @patch('image_advisor.sd3_generator')
    def test_score_image_relevance_exception(self, mock_sd3, mock_minicpm):
        """测试评分函数异常时的处理"""
        from image_advisor import ImageAdvisor

        advisor = ImageAdvisor("./prompts/image_advisor.txt")

        # 测试不存在的文件
        score = advisor.score_image_relevance("nonexistent.jpg", "测试主题")

        # 应该返回默认分数并记录错误
        self.assertEqual(score, 50)
        print(f"✓ 测试通过：异常时返回默认分数 {score}")

    @patch('image_advisor.minicpm_model')
    @patch('image_advisor.sd3_generator')
    def test_generate_images_with_relevance_scoring(self, mock_sd3, mock_minicpm):
        """测试带相关性评分的图片生成流程"""
        from image_advisor import ImageAdvisor

        advisor = ImageAdvisor("./prompts/image_advisor.txt")


class TestImageAdvisor(unittest.TestCase):
    """测试 image_advisor 模块的功能"""

    def setUp(self):
        """设置测试数据"""
        self.prompt_file = "./prompts/image_advisor.txt"

    def test_score_image_relevance_mock(self):
        """测试图片相关性评分功能（使用 mock）"""
        advisor = ImageAdvisor(self.prompt_file)

        # 创建一个临时测试图片
        from PIL import Image as PILImage
        test_image_path = "images/test_relevance.jpg"

        try:
            # 创建测试图片
            img = PILImage.new('RGB', (100, 100), color='blue')
            img.save(test_image_path)

            # Mock minicpm_model
            with patch('image_advisor.minicpm_model') as mock_model:
                # 设置 mock 返回值
                mock_chat_response = "这张图片与主题的相关性评分是 85分"
                mock_model.chat = MagicMock(return_value=mock_chat_response)

                # 调用评分函数
                score = advisor.score_image_relevance(test_image_path, "测试主题")

                # 验证结果
                self.assertEqual(score, 85)
                print(f"✓ 测试通过：图片相关性评分 = {score}")

        finally:
            # 清理测试图片
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

    def test_score_image_relevance_parse_error(self):
        """测试评分解析失败时的默认值"""
        advisor = ImageAdvisor(self.prompt_file)

        # 创建一个临时测试图片
        from PIL import Image as PILImage
        test_image_path = "images/test_relevance_error.jpg"

        try:
            # 创建测试图片
            img = PILImage.new('RGB', (100, 100), color='red')
            img.save(test_image_path)

            # Mock minicpm_model 返回无法解析的响应
            with patch('image_advisor.minicpm_model') as mock_model:
                mock_model.chat = MagicMock(return_value="无法解析的响应文本")

                # 调用评分函数
                score = advisor.score_image_relevance(test_image_path, "测试主题")

                # 应该返回默认中等分数
                self.assertEqual(score, 50)
                print(f"✓ 测试通过：解析失败时返回默认分数 {score}")

        finally:
            # 清理测试图片
            if os.path.exists(test_image_path):
                os.remove(test_image_path)

    def test_score_image_relevance_exception(self):
        """测试评分函数异常时的处理"""
        advisor = ImageAdvisor(self.prompt_file)

        # 测试不存在的文件
        score = advisor.score_image_relevance("nonexistent.jpg", "测试主题")

        # 应该返回默认分数并记录错误
        self.assertEqual(score, 50)
        print(f"✓ 测试通过：异常时返回默认分数 {score}")

    def test_generate_images_with_relevance_scoring(self):
        """测试带相关性评分的图片生成流程"""
        advisor = ImageAdvisor(self.prompt_file)

        # Mock content
        markdown_content = """
# 测试演示文稿

## 幻灯片1：测试标题
这是测试内容。

## 幻灯片2：另一个标题
更多测试内容。
"""

        # Mock get_keywords 返回
        with patch.object(advisor, 'get_keywords') as mock_get_keywords:
            mock_get_keywords.return_value = {
                "幻灯片1：测试标题": "测试关键词",
                "幻灯片2：另一个标题": "另一个关键词"
            }

            # Mock get_bing_images 返回
            with patch.object(advisor, 'get_bing_images') as mock_get_images:
                # 模拟返回图片数据
                mock_images = [[
                    {
                        'slide_title': '幻灯片1：测试标题',
                        'query': '测试关键词',
                        'width': 1024,
                        'height': 768,
                        'obj': Mock()  # Mock PIL Image 对象
                    }
                ]]

                mock_get_images.return_value = mock_images

                # Mock score_image_relevance 返回低分（需要生成新图片）
                with patch.object(advisor, 'score_image_relevance') as mock_score:
                    mock_score.return_value = 45  # 低于 60，应该生成新图片

                    # Mock save_image
                    with patch.object(advisor, 'save_image'):
                        # Mock SD3 生成器
                        with patch('image_advisor.get_sd3_generator') as mock_get_sd3:
                            mock_generator = MagicMock()
                            mock_generated_img = MagicMock()
                            mock_generator.generate.return_value = mock_generated_img
                            mock_get_sd3.return_value = mock_generator

                            # 执行测试
                            content_with_images, image_pair = advisor.generate_images(
                                markdown_content,
                                image_directory="test_output"
                            )

                            # 验证结果
                            self.assertIsInstance(content_with_images, str)
                            self.assertIsInstance(image_pair, dict)
                            print("✓ 测试通过：带相关性评分的图片生成流程")

    def test_extract_keywords(self):
        """测试关键词提取功能"""
        advisor = ImageAdvisor(self.prompt_file)

        advice_text = """
[幻灯片1：Hacker News 简介]: Hacker News 首页截图
[幻灯片2：Hacker News 的历史]: 保罗·格雷厄姆 黑客新闻
[幻灯片3：Hacker News 的功能]: Hacker News 界面
        """

        keywords = advisor.get_keywords(advice_text)

        expected = {
            "幻灯片1：Hacker News 简介": "Hacker News 首页截图",
            "幻灯片2：Hacker News 的历史": "保罗·格雷厄姆 黑客新闻",
            "幻灯片3：Hacker News 的功能": "Hacker News 界面"
        }

        self.assertEqual(keywords, expected)
        print("✓ 测试通过：关键词提取功能正常")


if __name__ == "__main__":
    unittest.main()
