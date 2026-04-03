"""
测试图片建议和插入功能（JSON 格式）
"""
import unittest
import os
import sys

# 添加 src 目录到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from image_advisor import ImageAdvisor


class TestImageAdvisorJSON(unittest.TestCase):
    """测试图片建议功能（JSON 格式）"""

    def setUp(self):
        """设置测试"""
        self.prompt_file = "./prompts/image_advisor.txt"

    def test_extract_json_keywords(self):
        """测试提取 JSON 格式关键词"""
        advisor = ImageAdvisor(self.prompt_file)

        # JSON 格式响应
        json_response = '''```json
{
  "什么是深度学习？": "neural network visualization",
  "深度学习的基本原理": "deep learning architecture",
  "应用领域": "AI applications"
}
```'''

        keywords = advisor.get_keywords(json_response)

        # 验证结果
        self.assertEqual(len(keywords), 3)
        self.assertEqual(keywords["什么是深度学习？"], "neural network visualization")
        self.assertEqual(keywords["深度学习的基本原理"], "deep learning architecture")
        self.assertEqual(keywords["应用领域"], "AI applications")

        print(f"✓ JSON 关键词提取成功: {keywords}")

    def test_extract_plain_json_keywords(self):
        """测试提取纯 JSON 格式关键词（无代码块）"""
        advisor = ImageAdvisor(self.prompt_file)

        # 纯 JSON 响应（无 markdown 代码块）
        plain_json = '''{
  "幻灯片1": "test keyword 1",
  "幻灯片2": "test keyword 2"
}'''

        keywords = advisor.get_keywords(plain_json)

        # 验证结果
        self.assertEqual(len(keywords), 2)
        self.assertEqual(keywords["幻灯片1"], "test keyword 1")
        self.assertEqual(keywords["幻灯片2"], "test keyword 2")

        print(f"✓ 纯 JSON 关键词提取成功: {keywords}")

    def test_extract_legacy_format_keywords(self):
        """测试兼容旧格式（方括号）"""
        advisor = ImageAdvisor(self.prompt_file)

        # 旧格式响应
        legacy_response = '''[幻灯片1]: test keyword 1
[幻灯片2]: test keyword 2
[幻灯片3]: test keyword 3'''

        keywords = advisor.get_keywords(legacy_response)

        # 验证结果
        self.assertEqual(len(keywords), 3)
        self.assertEqual(keywords["幻灯片1"], "test keyword 1")

        print(f"✓ 旧格式关键词提取成功: {keywords}")

    def test_insert_images_to_markdown(self):
        """测试图片插入到 markdown"""
        advisor = ImageAdvisor(self.prompt_file)

        # 测试 markdown 内容
        markdown_content = """# 测试演示

## 什么是深度学习？
这是深度学习的基本介绍。

## 深度学习的基本原理
这是原理部分。

## 应用领域
这是应用部分。"""

        # 图片映射
        image_pair = {
            "什么是深度学习？": "images/test1.jpg",
            "应用领域": "images/test3.jpg"
        }

        # 插入图片
        result = advisor.insert_images(markdown_content, image_pair)

        # 验证结果
        self.assertIn("![什么是深度学习？](images/test1.jpg)", result)
        self.assertIn("![应用领域](images/test3.jpg)", result)
        # 未匹配的标题不应该有图片
        self.assertNotIn("深度学习的基本原理", result.split("## 深度学习的基本原理")[1].split("##")[0])

        print(f"✓ 图片插入测试通过")
        print(f"  插入的图片: 2/3")
        print(f"  结果预览:\n{result}")

    def test_extract_complex_json(self):
        """测试复杂的 JSON 格式"""
        advisor = ImageAdvisor(self.prompt_file)

        # 包含特殊字符的 JSON
        complex_json = '''```json
{
  "深度学习：基础与应用": "deep learning fundamentals and applications",
  "CNN vs RNN": "convolutional vs recurrent neural networks comparison",
  "自动驾驶技术": "autonomous driving technology"
}
```'''

        keywords = advisor.get_keywords(complex_json)

        # 验证结果
        self.assertEqual(len(keywords), 3)
        self.assertIn("深度学习：基础与应用", keywords)

        print(f"✓ 复杂 JSON 提取成功: {keywords}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
