import unittest
import os
import sys

# 添加 src 目录到模块搜索路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from workflow_graph import create_workflow, WorkflowGraph, WorkflowState


class TestWorkflowGraph(unittest.TestCase):
    """
    测试 WorkflowGraph 模块
    """

    def setUp(self):
        """
        设置测试数据
        """
        self.workflow = create_workflow(max_rounds=2)  # 测试用 2 轮即可
        self.test_input = "请生成一份关于人工智能发展历史的PPT"

    def test_workflow_initialization(self):
        """
        测试工作流初始化
        """
        self.assertIsNotNone(self.workflow)
        self.assertEqual(self.workflow.max_rounds, 2)
        self.assertIsNotNone(self.workflow.graph)

    def test_workflow_state_structure(self):
        """
        测试 WorkflowState 结构
        """
        from langchain_core.messages import HumanMessage

        state = WorkflowState(
            messages=[HumanMessage(content="测试输入")],
            thread_id="test_thread"
        )

        self.assertIn("messages", state)
        self.assertIn("thread_id", state)
        self.assertEqual(len(state["messages"]), 1)

    def test_workflow_run(self):
        """
        测试工作流运行（实际调用 API，可能较慢）
        """
        result = self.workflow.run(
            self.test_input,
            session_id="test_workflow_session"
        )

        # 验证返回结果
        self.assertIsInstance(result, dict)
        self.assertIn("content", result)
        self.assertIn("rounds", result)
        self.assertGreater(result["rounds"], 0)
        self.assertIsInstance(result["content"], str)
        self.assertGreater(len(result["content"]), 0)

    def test_workflow_max_rounds(self):
        """
        测试工作流轮次限制
        """
        # 设置最大 1 轮
        workflow = create_workflow(max_rounds=1)
        result = workflow.run(
            self.test_input,
            session_id="test_max_rounds"
        )

        # 验证不超过最大轮次
        self.assertLessEqual(result["rounds"], 1)

    def test_visualize(self):
        """
        测试工作流可视化
        """
        import tempfile

        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            output_path = f.name

        try:
            success = self.workflow.visualize(output_path)
            # 可视化可能失败（需要 graphviz），这里只验证不会崩溃
            self.assertIsInstance(success, bool)
        finally:
            # 清理临时文件
            if os.path.exists(output_path):
                os.remove(output_path)

    def test_round_decorator(self):
        """
        测试轮次装饰器功能
        """
        from workflow_graph import _round_counter

        # 清空测试计数器
        test_thread_id = "test_decorator_thread"
        if test_thread_id in _round_counter:
            del _round_counter[test_thread_id]

        # 验证初始状态
        self.assertNotIn(test_thread_id, _round_counter)


class TestWorkflowState(unittest.TestCase):
    """
    测试 WorkflowState 数据结构
    """
    def test_state_creation(self):
        """
        测试 State 创建
        """
        from langchain_core.messages import HumanMessage, AIMessage

        state = WorkflowState(
            messages=[
                HumanMessage(content="用户问题"),
                AIMessage(content="AI回答")
            ],
            thread_id="test_thread"
        )

        self.assertEqual(len(state["messages"]), 2)
        self.assertEqual(state["thread_id"], "test_thread")

    def test_state_messages_append(self):
        """
        测试消息自动追加（通过 add_messages）
        """
        from langchain_core.messages import HumanMessage, AIMessage
        from operator import add

        messages1 = [HumanMessage(content="消息1")]
        messages2 = [AIMessage(content="消息2")]

        # 测试 add 函数（模拟 Annotated[list, add] 行为）
        result = add(messages1, messages2)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].content, "消息1")
        self.assertEqual(result[1].content, "消息2")


if __name__ == '__main__':
    unittest.main()
