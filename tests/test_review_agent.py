import unittest
import os
import sys

# 添加 src 目录到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from review_agent import ReviewAgent


class TestReviewAgent(unittest.TestCase):
    """
    测试 ReviewAgent 模块
    """

    def setUp(self):
        """
        设置测试数据
        """
        self.review_agent = ReviewAgent()
        self.sample_content = """# 人工智能发展历史

## 早期探索
- 图灵测试：判断机器是否具有智能
- 达特茅斯会议：人工智能诞生

## 专家系统时代
- 专家系统的兴起
- 知识工程的发展"""

    def test_review_agent_initialization(self):
        """
        测试 ReviewAgent 初始化
        """
        self.assertIsNotNone(self.review_agent)
        self.assertIsNotNone(self.review_agent.agent)

    def test_review_content(self):
        """
        测试内容审查功能
        """
        result = self.review_agent.review(
            self.sample_content,
            session_id="test_session",
            original_query="生成人工智能发展历史的PPT"
        )

        # 验证返回结果包含必要字段
        self.assertIsInstance(result, dict)
        self.assertIn("issues", result)
        self.assertIn("suggestions", result)
        self.assertIn("raw_response", result)

    def test_parse_review_response(self):
        """
        测试审查响应解析功能
        """
        # 模拟审查响应
        mock_response = """[Review Results]
Overall Score: 75

[Issue List]
1. [Structure]: Slide 2 lacks enough detail
   - Location: Slide 2
   - Improvement Suggestion: Add more specific examples

2. [Content]: Missing statistics
   - Location: Slide 3
   - Improvement Suggestion: Include relevant data

[Overall Recommendations]
Focus on adding more concrete examples and data support.

[Needs Rewrite]
No"""

        result = self.review_agent._parse_review_response(mock_response)

        self.assertIn("issues", result)
        self.assertIn("suggestions", result)

    def test_get_feedback_prompt(self):
        """
        测试生成反馈提示功能
        """
        mock_review_result = {
            "issues": [
                "Issue 1: Content lacks detail",
                "Issue 2: Missing examples"
            ],
            "suggestions": "Add more concrete examples throughout",
            "raw_response": "Mock response"
        }

        feedback = self.review_agent.get_feedback_prompt(
            mock_review_result,
            self.sample_content
        )

        self.assertIsInstance(feedback, str)
        self.assertIn("feedback", feedback.lower())
        self.assertIn("Issue 1", feedback)
        self.assertIn("Add more concrete examples", feedback)


if __name__ == '__main__':
    unittest.main()
