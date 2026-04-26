#!/usr/bin/env python3
"""DeepSeek 交互式命令行聊天工具。

支持多轮对话、上下文历史、流式输出、快捷命令。

使用方法：
    export DEEPSEEK_API_KEY=your-key
    python examples/deepseek_cli.py

快捷命令（输入后按回车）：
    /quit 或 /q    退出程序
    /reset 或 /r   清空对话历史
    /save <路径>   保存对话历史到 JSON 文件
    /load <路径>   从 JSON 文件加载对话历史
    /history       查看当前对话历史
    /stream on     开启流式输出
    /stream off    关闭流式输出
"""

from __future__ import annotations

import os
import sys

from deepseek_client import ChatConfig, DeepSeekClient


def print_help() -> None:
    print(
        "\n快捷命令：\n"
        "  /quit, /q      退出\n"
        "  /reset, /r     清空历史\n"
        "  /save <路径>   保存历史\n"
        "  /load <路径>   加载历史\n"
        "  /history       查看历史\n"
        "  /stream on|off 切换流式输出\n"
        "  /help, /h      显示此帮助\n"
    )


def main() -> None:
    """主函数：交互式聊天循环。"""
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")
    if not api_key:
        print("错误：未设置 DEEPSEEK_API_KEY 环境变量", file=sys.stderr)
        print("请执行：export DEEPSEEK_API_KEY='your-key'", file=sys.stderr)
        sys.exit(1)

    config = ChatConfig(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro"),
        stream=False,
    )
    client = DeepSeekClient(api_key=api_key, config=config)

    system_prompt = os.environ.get(
        "DEEPSEEK_SYSTEM_PROMPT",
        "你是一个 helpful 的 AI 助手。",
    )

    print("=" * 50)
    print("DeepSeek 交互式聊天工具")
    print(f"模型：{config.model}")
    print("输入 /help 查看快捷命令")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            continue

        # 解析快捷命令
        if user_input.startswith("/"):
            parts = user_input.split(maxsplit=1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""

            if cmd in ("/quit", "/q"):
                print("再见！")
                break

            if cmd in ("/reset", "/r"):
                client.reset_history()
                print("[系统] 对话历史已清空。")
                continue

            if cmd == "/save":
                path = arg or "chat_history.json"
                client.save_history_to_file(path)
                print(f"[系统] 历史已保存到：{path}")
                continue

            if cmd == "/load":
                if not arg:
                    print("[系统] 用法：/load <文件路径>")
                    continue
                client.load_history_from_file(arg)
                print(f"[系统] 历史已从 {arg} 加载。")
                continue

            if cmd == "/history":
                if not client.history:
                    print("[系统] 暂无对话历史。")
                else:
                    for msg in client.history:
                        role = (
                            "系统"
                            if msg.role == "system"
                            else ("你" if msg.role == "user" else "助手")
                        )
                        print(
                            f"  [{role}] {msg.content[:80]}{'...' if len(msg.content) > 80 else ''}"
                        )
                continue

            if cmd == "/stream":
                if arg == "on":
                    client.config.stream = True
                    print("[系统] 流式输出已开启。")
                elif arg == "off":
                    client.config.stream = False
                    print("[系统] 流式输出已关闭。")
                else:
                    print(
                        f"[系统] 当前流式输出：{'开启' if client.config.stream else '关闭'}"
                    )
                continue

            if cmd in ("/help", "/h"):
                print_help()
                continue

            print(f"[系统] 未知命令：{cmd}，输入 /help 查看帮助。")
            continue

        # 发送对话请求
        try:
            if client.config.stream:
                print("助手：", end="", flush=True)
                for part in client.chat_with_history_stream(
                    user_input,
                    system_prompt=system_prompt if not client.history else None,
                ):
                    print(part, end="", flush=True)
                print()
            else:
                reply = client.chat_with_history(
                    user_input,
                    system_prompt=system_prompt if not client.history else None,
                )
                print(f"助手：{reply}")
        except Exception as e:
            print(f"[错误] {e}", file=sys.stderr)

    # 退出时自动保存历史
    if client.history:
        client.save_history_to_file("chat_history_auto.json")
        print("[系统] 对话历史已自动保存到 chat_history_auto.json")


if __name__ == "__main__":
    main()
