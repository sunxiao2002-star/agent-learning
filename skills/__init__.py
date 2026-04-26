"""Skill 管理包。

提供 Skill 抽象基类和注册表，用于统一管理可复用的功能模块。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Skill(ABC):
    """Skill 抽象基类。所有 Skill 必须继承此类并实现 run 方法。"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Skill 唯一标识名。"""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Skill 功能描述。"""
        ...

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        """执行 Skill 的核心逻辑。"""
        ...


class SkillRegistry:
    """Skill 注册表，统一管理所有已注册的 Skill。"""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        """注册一个 Skill。"""
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        """根据名称获取 Skill。"""
        if name not in self._skills:
            raise KeyError(f"Skill '{name}' 未注册")
        return self._skills[name]

    def list(self) -> list[str]:
        """返回所有已注册的 Skill 名称列表。"""
        return list(self._skills.keys())

    def run(self, name: str, *args, **kwargs) -> Any:
        """按名称执行指定 Skill。"""
        return self.get(name).run(*args, **kwargs)
