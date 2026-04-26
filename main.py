#!/usr/bin/env python3
"""Agent Learning 项目入口文件。

支持直接运行，无需使用 python -m：
    python3 main.py                    启动 DeepSeek 交互式 CLI
    python3 main.py --agent deepseek   同上（显式指定）

注意：
    - 确保已设置 DEEPSEEK_API_KEY 环境变量
    - 或已将密钥写入 ~/.zshrc 等 shell 配置文件
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _add_project_root_to_path() -> None:
    """将项目根目录加入 sys.path，确保包导入正常。"""
    project_root = Path(__file__).parent.resolve()
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))


def run_deepseek_agent() -> None:
    """运行 DeepSeek 交互式 CLI。"""
    _add_project_root_to_path()

    from agents.deepseek.cli import main

    main()


def run_skill(name: str, args: list[str]) -> None:
    """按名称运行指定 Skill。"""
    _add_project_root_to_path()

    from skills import SkillRegistry

    registry = SkillRegistry()

    if name == "md-to-html":
        from skills.md_to_html import MdToHtmlSkill

        registry.register(MdToHtmlSkill())
        return registry.run(name, *args)

    print(f"未知 Skill：{name}", file=sys.stderr)
    sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    """主入口。"""
    parser = argparse.ArgumentParser(description="Agent Learning 入口")
    parser.add_argument(
        "--agent",
        default="deepseek",
        choices=["deepseek"],
        help="指定要运行的 Agent（默认：deepseek）",
    )
    parser.add_argument(
        "--skill",
        default=None,
        help="指定要运行的 Skill（如 md-to-html）",
    )
    parser.add_argument(
        "skill_args",
        nargs="*",
        help="传递给 Skill 的参数",
    )
    args = parser.parse_args(argv)

    if args.skill:
        run_skill(args.skill, args.skill_args)
    elif args.agent == "deepseek":
        run_deepseek_agent()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
