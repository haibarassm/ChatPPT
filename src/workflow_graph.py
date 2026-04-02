"""
Langraph 工作流模块
实现 Chatbot 和 Review Agent 的循环工作流
"""

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import BaseMessage
from operator import add
from functools import wraps

from logger import LOG
from chatbot import ChatBot
from review_agent import ReviewAgent
from chat_history import clear_history_keep_last


# 用于存储轮次计数（作为全局状态）
_round_counter = {}


def round_decorator(node_name: str, increment: bool = True):
    """
    轮次计数装饰器

    参数:
        node_name: 节点名称，用于日志标识
        increment: 是否增加轮次计数（默认 True）
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, state: WorkflowState, *args, **kwargs):
            # 获取或初始化计数器
            thread_id = state.get("thread_id", "default")
            if thread_id not in _round_counter:
                _round_counter[thread_id] = 0

            # 获取当前轮次
            current_round = _round_counter[thread_id]

            # 根据是否增加计数来决定显示的 round
            # increment=True（chatbot）：显示 current_round + 1
            # increment=False（review）：显示 current_round（因为计数器已被 chatbot 增加）
            display_round = current_round + 1 if increment else current_round

            # 执行节点函数
            LOG.info(f"[Round {display_round}] {node_name} 正在执行...")

            # 如果不增加计数（如 review），传入 current_round（和 chatbot 同轮）
            # 因为 review 执行时计数器已被 chatbot 增加，所以需要 -1
            if not increment:
                round_to_pass = max(0, current_round - 1)
            else:
                round_to_pass = current_round

            result = func(self, state, current_round=round_to_pass, *args, **kwargs)

            # 只在指定节点增加计数（默认增加）
            if increment:
                _round_counter[thread_id] += 1

            return result
        return wrapper
    return decorator


class WorkflowState(TypedDict):
    """
    工作流状态定义（精简版）
    """
    # 消息列表（使用 add_messages 自动追加）
    messages: Annotated[list[BaseMessage], add]
    # 线程ID（用于轮次计数、会话管理）
    thread_id: str


class WorkflowGraph:
    """
    工作流图类，管理 Chatbot 和 Review Agent 的交互
    """
    def __init__(self, chatbot_prompt_file="./prompts/chatbot.txt",
                 max_rounds=5):
        """
        初始化工作流

        参数:
            chatbot_prompt_file: Chatbot 提示词文件路径
            max_rounds: 最大循环轮次
        """
        self.max_rounds = max_rounds
        self.chatbot = ChatBot(prompt_file=chatbot_prompt_file)
        self.review_agent = ReviewAgent()
        self.graph = self._build_graph()

    @round_decorator("Chatbot")
    def _chatbot_node(self, state: WorkflowState, current_round: int = 0) -> WorkflowState:
        """
        Chatbot 节点：生成内容

        参数:
            state: 当前工作流状态
            current_round: 当前轮次（由装饰器传入）

        返回:
            WorkflowState: 更新后的状态
        """
        from langchain_core.messages import AIMessage

        messages = state.get("messages", [])

        # 如果是第一轮，使用原始用户输入（第一条消息）；否则使用最后一条审查反馈
        if current_round == 0:
            user_input = messages[0].content if messages else ""
        else:
            # 获取最后一条审查反馈
            user_input = messages[-1].content if messages else ""

        # 调用 chatbot 生成内容
        content = self.chatbot.chat_with_history(
            user_input,
            session_id=state["thread_id"]
        )

        LOG.info(f"[Round {current_round + 1}] Chatbot 内容生成完成")

        # 返回新的消息（会被 add_messages 自动追加）
        return {"messages": [AIMessage(content=content)]}

    @round_decorator("ReviewAgent", increment=False)
    def _review_node(self, state: WorkflowState, current_round: int = 0) -> WorkflowState:
        """
        Review Agent 节点：审查内容并生成反馈

        参数:
            state: 当前工作流状态
            current_round: 当前轮次（由装饰器传入）

        返回:
            WorkflowState: 更新后的状态
        """
        from langchain_core.messages import AIMessage

        # 获取最后一条 AI 消息进行审查
        messages = state.get("messages", [])
        if not messages:
            LOG.warning("没有消息可审查")
            return {}

        last_message = messages[-1]
        content_to_review = last_message.content

        # 获取原始用户输入（第一条消息）
        original_query = messages[0].content if messages else ""

        # 审查内容
        review_result = self.review_agent.review(
            content_to_review,
            session_id=state["thread_id"],
            original_query=original_query
        )

        # 打印审查反馈结果（使用 current_round + 1，和装饰器日志一致）
        LOG.info(f"[Round {current_round + 1}] 审查反馈:")
        if review_result.get('issues'):
            for i, issue in enumerate(review_result['issues'][:3], 1):
                LOG.info(f"  问题{i}: {issue}")
        if review_result.get('suggestions'):
            LOG.info(f"  改进建议: {review_result['suggestions']}")
        print(f"\n[Round {current_round + 1}] 审查反馈:")
        if review_result.get('issues'):
            for i, issue in enumerate(review_result['issues'][:3], 1):
                print(f"  问题{i}: {issue}")
        if review_result.get('suggestions'):
            print(f"  改进建议: {review_result['suggestions']}")

        # 生成反馈（给 chatbot 的改进意见）
        feedback = self.review_agent.get_feedback_prompt(
            review_result,
            content_to_review
        )

        LOG.info(f"[Round {current_round + 1}] 审查完成，反馈已生成")

        # 返回新的消息（会被 add_messages 自动追加）
        return {"messages": [AIMessage(content=feedback)]}

    def router(self, state: WorkflowState) -> Literal["chatbot", "end"]:
        """
        路由函数（条件边）：判断是否继续循环

        参数:
            state: 当前工作流状态

        返回:
            str: 下一个节点的名称 ("chatbot" 或 "end")
        """
        # 检查轮次限制
        thread_id = state.get("thread_id", "default")
        current_round = _round_counter.get(thread_id, 0)

        if current_round >= self.max_rounds:
            LOG.info(f"达到最大轮次限制 ({self.max_rounds})，结束循环")
            # 清空该会话的历史记录，只保留最后一次对话
            self._clear_history_keep_last(state)
            # 注意：不在 router 中清空计数器，让 run 方法获取轮次后再清空
            return "end"

        # 继续循环，进入 chatbot
        return "chatbot"

    def _clear_history_keep_last(self, state: WorkflowState):
        """
        清空会话历史，只保留最后一次对话（用户问题+AI回答）

        参数:
            state: 当前工作流状态
        """
        messages = state.get("messages", [])
        if not messages:
            return

        # 获取原始用户输入（第一条消息）
        user_input = messages[0].content if messages else ""

        # 获取最后一条 AI 回复
        last_ai_message = None
        for msg in reversed(messages):
            if hasattr(msg, 'content') and msg.content:
                last_ai_message = msg.content
                break

        if last_ai_message:
            clear_history_keep_last(
                state["thread_id"],
                user_input,
                last_ai_message
            )
            LOG.info(f"已保留会话 {state['thread_id']} 的最后一次对话")

    def _build_graph(self) -> StateGraph:
        """
        构建工作流图

        返回:
            StateGraph: 构建好的图
        """
        # 创建状态图
        graph = StateGraph(WorkflowState)

        # 添加节点
        graph.add_node("chatbot", self._chatbot_node)
        graph.add_node("review", self._review_node)

        # 设置入口点（使用 START）
        graph.add_edge(START, "chatbot")

        # 添加边
        graph.add_edge("chatbot", "review")
        # 条件边：review 后通过 router 判断去向
        graph.add_conditional_edges(
            "review",
            self.router,  # router 函数
            {
                "chatbot": "chatbot",
                "end": END
            }
        )

        # 编译图（带内存保存）
        memory = MemorySaver()
        return graph.compile(checkpointer=memory)

    def visualize(self, output_path: str = "workflow_graph.png"):
        """
        可视化工作流图并保存为图片

        参数:
            output_path: 输出图片路径

        返回:
            bool: 是否成功保存
        """
        try:
            png_data = self.graph.get_graph().draw_mermaid_png()
            if png_data:
                with open(output_path, "wb") as f:
                    f.write(png_data)
                LOG.info(f"工作流图已保存至: {output_path}")
                return True
            return False
        except Exception as e:
            LOG.error(f"生成图表失败: {e}")
            return False

    def run(self, user_input: str, session_id: str = "default") -> dict:
        """
        运行工作流

        参数:
            user_input: 用户输入
            session_id: 会话ID

        返回:
            dict: 最终结果
        """
        from langchain_core.messages import HumanMessage

        LOG.info(f"开始工作流，会话ID: {session_id}")

        # 初始化状态（精简版）
        initial_state = WorkflowState(
            messages=[HumanMessage(content=user_input)],
            thread_id=session_id
        )

        # 运行图
        config = {"configurable": {"thread_id": session_id}}
        result = self.graph.invoke(initial_state, config)

        # 获取最终内容
        messages = result.get("messages", [])
        final_content = ""
        if messages:
            # 获取倒数第二条消息（最后一条是审查反馈）
            for msg in reversed(messages):
                if hasattr(msg, 'content') and msg.content and not msg.content.startswith("The following is the review feedback"):
                    final_content = msg.content
                    break

        # 获取最终轮次
        thread_id = session_id
        final_rounds = _round_counter.get(thread_id, 0)

        # 清空计数器（为下次运行做准备）
        if thread_id in _round_counter:
            del _round_counter[thread_id]

        return {
            "content": final_content,
            "rounds": final_rounds
        }


# 便捷函数
def create_workflow(chatbot_prompt_file="./prompts/chatbot.txt", max_rounds=5):
    """
    创建工作流实例

    参数:
        chatbot_prompt_file: Chatbot 提示词文件路径
        max_rounds: 最大循环轮次

    返回:
        WorkflowGraph: 工作流实例
    """
    return WorkflowGraph(chatbot_prompt_file, max_rounds)


if __name__ == "__main__":
    # 测试代码
    workflow = create_workflow(max_rounds=3)

    # 可视化图表并保存
    # print("正在生成工作流图表...")
    # if workflow.visualize("workflow_graph.png"):
    #     print("图表已保存至: workflow_graph.png")
    # else:
    #     print("图表生成失败（可能需要安装 graphviz）")

    # 运行测试
    test_input = "请生成一份关于人工智能发展历史的PPT"
    result = workflow.run(test_input, session_id="test_session")

    print("\n" + "="*50)
    print(f"工作流完成，共 {result['rounds']} 轮")
    print("="*50 + "\n")

    print(result['content'])
