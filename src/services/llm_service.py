"""
LLM服务
使用LangChain框架，支持Ollama、硅基流动、OpenAI

环境变量说明：
- OPENAI_API_KEY: API密钥（硅基流动和OpenAI共用）
- OPENAI_API_BASE: API基础URL（可选，硅基流动需设置为 https://api.siliconflow.cn/v1）
- OLLAMA_BASE_URL: Ollama服务地址（可选，默认 http://localhost:11434）
"""

import os
from typing import Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

from config import Config
from logger import LOG


class LLMService:
    """LLM服务类 - 使用LangChain框架"""

    # 硅基流动默认base_url
    SILICONFLOW_BASE_URL = "https://api.siliconflow.cn/v1"

    # Ollama默认base_url
    OLLAMA_BASE_URL = "http://localhost:11434"

    def __init__(self, config: Optional[Config] = None):
        """初始化LLM服务

        Args:
            config: 配置对象，如果为None则使用默认配置
        """
        self.config = config or Config()
        self._llm: Optional[BaseChatModel] = None
        self._initialize_llm()

    def _initialize_llm(self):
        """根据配置初始化LLM"""

        provider = self.config.llm_provider.lower()

        if provider == "siliconflow":
            self._init_siliconflow()
        elif provider == "ollama":
            self._init_ollama()
        elif provider == "openai":
            self._init_openai()
        else:
            raise ValueError(f"不支持的LLM提供商: {provider}，请使用: siliconflow, ollama, 或 openai")

        LOG.info(f"LLM初始化完成: provider={provider}, model={self._llm.model}")

    def _init_siliconflow(self):
        """初始化硅基流动（使用OpenAI兼容接口）"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("请设置 OPENAI_API_KEY 环境变量")

        # 从环境变量获取base_url，如果没有则使用默认值
        base_url = os.getenv("OPENAI_API_BASE", self.SILICONFLOW_BASE_URL)

        self._llm = ChatOpenAI(
            model=self.config.llm_model,
            base_url=base_url,
            api_key=api_key,
            temperature=self.config.llm_temperature
        )

    def _init_ollama(self):
        """初始化Ollama（本地运行）"""
        base_url = os.getenv("OLLAMA_BASE_URL", self.OLLAMA_BASE_URL)

        self._llm = ChatOllama(
            model=self.config.llm_model or "llama3.1:8b",
            base_url=base_url,
            temperature=self.config.llm_temperature
        )

    def _init_openai(self):
        """初始化OpenAI"""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("请设置 OPENAI_API_KEY 环境变量")

        # OpenAI支持自定义base_url
        base_url = os.getenv("OPENAI_API_BASE")

        kwargs = {
            "model": self.config.llm_model,
            "api_key": api_key,
            "temperature": self.config.llm_temperature
        }

        # 如果设置了base_url则传入
        if base_url:
            kwargs["base_url"] = base_url

        self._llm = ChatOpenAI(**kwargs)

    @property
    def llm(self) -> BaseChatModel:
        """获取底层LLM实例"""
        return self._llm

    def chat(self, message: str, system_prompt: Optional[str] = None) -> str:
        """简单的聊天接口

        Args:
            message: 用户消息
            system_prompt: 系统提示词（可选）

        Returns:
            LLM回复
        """
        messages = []

        if system_prompt:
            messages.append(SystemMessage(content=system_prompt))

        messages.append(HumanMessage(content=message))

        try:
            response = self._llm.invoke(messages)
            return response.content
        except Exception as e:
            LOG.error(f"LLM调用失败: {e}")
            return f"错误: LLM调用失败 - {str(e)}"
