"""
Agent 工厂模块
提供创建各类 Agent 的公共方法
"""

from abc import ABC, abstractmethod
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, SystemMessage
from logger import LOG


class BaseAgent(ABC):
    """
    Agent 基类，提供公共创建方法
    """
    def __init__(self, prompt_file=None, model_name="Pro/deepseek-ai/DeepSeek-V3.2",
                 temperature=0.7, max_tokens=4096):
        """
        初始化 Agent

        参数:
            prompt_file: 提示词文件路径
            model_name: 模型名称
            temperature: 温度参数
            max_tokens: 最大token数
        """
        self.prompt_file = prompt_file
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.prompt = None

        if prompt_file:
            self.prompt = self.load_prompt()

        self.model = self._create_model()
        self.chain = None

        if self.prompt:
            self.chain = self._create_chain()

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

    def _create_model(self):
        """
        创建模型实例

        返回:
            ChatOpenAI: 模型实例
        """
        return ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )

    def _create_chain(self, use_messages_placeholder=False):
        """
        创建提示链

        参数:
            use_messages_placeholder: 是否使用消息历史占位符

        返回:
            chain: 提示链
        """
        if use_messages_placeholder:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.prompt),
                MessagesPlaceholder(variable_name="messages"),
            ])
        else:
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.prompt),
                ("human", "{input}"),
            ])

        return prompt | self.model

    @abstractmethod
    def invoke(self, **kwargs):
        """
        调用 Agent 的抽象方法，子类需要实现
        """
        pass

    def __call__(self, *args, **kwargs):
        """支持直接调用"""
        return self.invoke(**kwargs)


class SimpleAgent(BaseAgent):
    """
    简单 Agent，不需要消息历史
    """
    def __init__(self, prompt_file, model_name="Pro/deepseek-ai/DeepSeek-V3.2",
                 temperature=0.7, max_tokens=4096):
        super().__init__(prompt_file, model_name, temperature, max_tokens)

    def invoke(self, input_text):
        """
        调用 Agent

        参数:
            input_text: 输入文本

        返回:
            str: Agent 的响应内容
        """
        response = self.chain.invoke({"input": input_text})
        LOG.debug(f"[{self.__class__.__name__}] {response.content}")
        return response.content
