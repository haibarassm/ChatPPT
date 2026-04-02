from langchain_core.chat_history import (
    BaseChatMessageHistory,  # 基础聊天消息历史类
    InMemoryChatMessageHistory,  # 内存中的聊天消息历史类
)

# 用于存储会话历史的字典
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    """
    获取指定会话ID的聊天历史。如果该会话ID不存在，则创建一个新的聊天历史实例。

    参数:
        session_id (str): 会话的唯一标识符

    返回:
        BaseChatMessageHistory: 对应会话的聊天历史对象
    """
    if session_id not in store:
        # 如果会话ID不存在于存储中，创建一个新的内存聊天历史实例
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]


def clear_history_keep_last(session_id: str, user_input: str, ai_output: str):
    """
    清空会话历史，只保留最后一次对话（用户问题+AI回答）

    参数:
        session_id (str): 会话的唯一标识符
        user_input (str): 用户的原始输入
        ai_output (str): AI的最终输出
    """
    from langchain_core.messages import HumanMessage, AIMessage

    if session_id in store:
        # 清空历史
        store[session_id].clear()

        # 保留最后一次对话
        store[session_id].add_messages([
            HumanMessage(content=user_input),
            AIMessage(content=ai_output)
        ])