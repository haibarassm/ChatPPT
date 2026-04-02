import unittest
import os
import sys

# 添加 src 目录到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from content_utils import extract_text_from_content


class TestContentUtils(unittest.TestCase):
    """测试 content_utils 模块的文本提取功能"""

    def test_extract_text_from_string(self):
        """测试从字符串提取文本"""
        content = "直接是字符串内容"
        result = extract_text_from_content(content)
        self.assertEqual(result, "直接是字符串内容")

    def test_extract_text_from_gradio_format(self):
        """测试从 gradio 6.10.0 格式提取文本"""
        content = [
            {"text": "第一段文本", "type": "text"},
            {"text": "第二段文本", "type": "text"}
        ]
        result = extract_text_from_content(content, context="test_gradio")
        expected = "第一段文本\n第二段文本"
        self.assertEqual(result, expected)

    def test_extract_text_from_nested_content(self):
        """测试从嵌套 content 字段提取文本"""
        content = [
            {"content": [{"text": "嵌套文本1"}, {"text": "嵌套文本2"}]}
        ]
        result = extract_text_from_content(content, context="test_nested")
        expected = "嵌套文本1\n嵌套文本2"
        self.assertEqual(result, expected)

    def test_extract_text_from_dict_with_text(self):
        """测试从带 text 字段的字典提取"""
        content = {"text": "字典中的文本"}
        result = extract_text_from_content(content)
        self.assertEqual(result, "字典中的文本")

    def test_extract_text_from_dict_with_content(self):
        """测试从带 content 字段的字典提取"""
        content = {"content": "内容字段"}
        result = extract_text_from_content(content)
        self.assertEqual(result, "内容字段")

    def test_extract_text_from_empty_list(self):
        """测试从空列表提取"""
        content = []
        result = extract_text_from_content(content)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
