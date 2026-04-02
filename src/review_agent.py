"""
Review Agent 模块
负责对生成的内容进行审查和挑刺
"""

from abc import ABC
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from langchain_core.runnables.history import RunnableWithMessageHistory
from logger import LOG
from chat_history import get_session_history


class ReviewAgent(ABC):
    """
    审查 Agent，对内容进行质量审查，支持消息历史
    """
    def __init__(self, prompt_file="./prompts/review_agent.txt", session_id=None):
        """
        初始化审查 Agent

        参数:
            prompt_file: 提示词文件路径
            session_id: 会话ID
        """
        self.prompt_file = prompt_file
        self.session_id = session_id if session_id else "review_session"
        self.prompt = self.load_prompt()
        self.create_review_agent()

    def load_prompt(self):
        """
        从文件加载系统提示语

        返回:
            str: 提示词内容
        """
        try:
            with open(self.prompt_file, "r", encoding="utf-8") as file:
                return file.read().strip()
        except FileNotFoundError:
            LOG.error(f"找不到提示文件 {self.prompt_file}!")
            raise

    def create_review_agent(self):
        """
        初始化审查 Agent，包括系统提示和消息历史记录
        """
        # 创建聊天提示模板，包括系统提示和消息占位符
        system_prompt = ChatPromptTemplate.from_messages([
            ("system", self.prompt),
            MessagesPlaceholder(variable_name="messages"),
        ])

        # 初始化模型
        self.model = ChatOpenAI(
            model="Pro/deepseek-ai/DeepSeek-V3.2",
            temperature=0.3,
            max_tokens=4096,
        )

        # 组合链
        self.agent = system_prompt | self.model

        # 将审查 Agent 与消息历史记录关联
        self.agent_with_history = RunnableWithMessageHistory(
            self.agent,
            get_session_history
        )

    def review(self, content, session_id=None, original_query=None):
        """
        审查内容

        参数:
            content: 待审查的内容
            session_id: 会话ID
            original_query: 原始用户查询（可选，用于上下文）

        返回:
            dict: 包含审查结果的字典
                - issues: 问题列表
                - suggestions: 改进建议
                - raw_response: 原始响应
        """
        if session_id is None:
            session_id = self.session_id

        # 构建审查输入
        if original_query:
            input_text = f"""Original user query: {original_query}

Please review the following generated PPT content:

```
{content}
```

Please output the review results strictly according to the required format."""
        else:
            input_text = f"""Please review the following generated PPT content:

```
{content}
```

Please output the review results strictly according to the required format."""

        LOG.info("正在进行内容审查...")
        response = self.agent_with_history.invoke(
            [HumanMessage(content=input_text)],
            {"configurable": {"session_id": session_id}}
        )

        # 解析审查结果
        result = self._parse_review_response(response.content)
        LOG.info("审查完成")

        return result

    def _parse_review_response(self, response):
        """
        解析审查响应

        参数:
            response: 审查 Agent 的原始响应

        返回:
            dict: 解析后的结构化数据
        """
        import re

        result = {
            "issues": [],
            "suggestions": "",
            "raw_response": response
        }

        # 提取总体建议
        suggestions_match = re.search(r'\[Overall Recommendations?\]\s*(.*?)(?=\n\[|\Z|$)',
                                      response, re.DOTALL | re.IGNORECASE)
        if suggestions_match:
            result["suggestions"] = suggestions_match.group(1).strip()

        # 提取问题列表
        issue_section = re.search(r'\[Issue List?\](.*?)(?=\[Overall Recommendations?\]|$)',
                                  response, re.DOTALL | re.IGNORECASE)
        if issue_section:
            issue_text = issue_section.group(1)
            # 简单分割问题
            issues = re.split(r'\n\s*\d+\.', issue_text)
            result["issues"] = [i.strip() for i in issues if i.strip()]

        return result

    def get_feedback_prompt(self, review_result, original_content):
        """
        根据审查结果生成反馈提示，用于传递给 chatbot 进行改进

        参数:
            review_result: 审查结果字典
            original_content: 原始内容

        返回:
            str: 反馈提示
        """
        prompt = """The following is the review feedback on your previously generated content:

【Main Issues】
"""

        if review_result['issues']:
            for i, issue in enumerate(review_result['issues'][:5], 1):  # 最多5个问题
                prompt += f"{i}. {issue}\n"
        else:
            prompt += "No obvious issues found\n"

        if review_result['suggestions']:
            prompt += f"\n【Improvement Suggestions】\n{review_result['suggestions']}\n"

        prompt += """

Based on the above feedback, please regenerate the improved PPT content. Requirements:
1. Maintain the original format (at least 10 slides)
2. Make modifications addressing the identified issues
3. Maintain content integrity and logical flow

Please output the complete improved PPT content directly, without explanation."""

        return prompt


# 便捷函数
def create_review_agent():
    """创建 ReviewAgent 实例"""
    return ReviewAgent()
