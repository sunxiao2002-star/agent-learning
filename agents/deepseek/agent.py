"""DeepSeek Agent 实现，继承 Agent 基类。"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from agents import Agent

from .client import ChatConfig, DeepSeekClient


class DeepSeekAgent(Agent):
    """基于 DeepSeek API 的 Agent 实现。

    封装 API 调用，提供统一的 run() 接口，支持流式和非流式输出。
    """

    def __init__(
        self,
        api_key: str | None = None,
        config: ChatConfig | None = None,
        system_prompt: str = "你是一个 helpful 的 AI 助手。",
    ) -> None:
        self.client = DeepSeekClient(api_key=api_key, config=config)
        self.system_prompt = system_prompt

    @property
    def name(self) -> str:
        return "deepseek"

    def run(self, message: str) -> str:
        """单轮对话（非流式）。

        Args:
            message: 用户输入内容

        Returns:
            模型生成的回复文本
        """
        return self.client.chat(message, system_prompt=self.system_prompt)

    def run_stream(self, message: str) -> Generator[str, None, None]:
        """单轮对话（流式）。

        Args:
            message: 用户输入内容

        Yields:
            模型生成的文本片段
        """
        yield from self.client.chat_stream(message, system_prompt=self.system_prompt)

    def run_with_history(self, message: str) -> str:
        """多轮对话（非流式），自动维护上下文历史。"""
        return self.client.chat_with_history(message, system_prompt=self.system_prompt)

    def run_with_history_stream(self, message: str) -> Generator[str, None, None]:
        """多轮对话（流式），自动维护上下文历史。"""
        yield from self.client.chat_with_history_stream(
            message, system_prompt=self.system_prompt
        )

    def reset(self) -> None:
        """清空对话历史。"""
        self.client.reset_history()

    def to_dict(self) -> dict[str, Any]:
        """将 Agent 状态序列化为字典。"""
        return {
            "name": self.name,
            "system_prompt": self.system_prompt,
            "history": [
                {"role": m.role, "content": m.content} for m in self.client.history
            ],
        }
