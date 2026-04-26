"""Agent 管理包。

提供 Agent 抽象基类和注册表，用于统一管理 AI Agent 实现。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Agent(ABC):
    """Agent 抽象基类。所有 Agent 必须继承此类并实现 run 方法。"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Agent 唯一标识名。"""
        ...

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """执行 Agent 的核心逻辑。"""
        ...


class AgentRegistry:
    """Agent 注册表，统一管理所有已注册的 Agent。"""

    def __init__(self) -> None:
        self._agents: dict[str, Agent] = {}

    def register(self, agent: Agent) -> None:
        """注册一个 Agent。"""
        self._agents[agent.name] = agent

    def get(self, name: str) -> Agent:
        """根据名称获取 Agent。"""
        if name not in self._agents:
            raise KeyError(f"Agent '{name}' 未注册")
        return self._agents[name]

    def list(self) -> list[str]:
        """返回所有已注册的 Agent 名称列表。"""
        return list(self._agents.keys())

    def run(self, name: str, *args, **kwargs) -> Any:
        """按名称执行指定 Agent。"""
        return self.get(name).run(*args, **kwargs)
