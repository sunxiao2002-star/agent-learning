"""DeepSeek API 客户端封装。

提供可复用的 DeepSeekClient 类，支持：
- 单轮/多轮对话
- 流式输出（默认开启）
- 自动重试与错误处理
- 对话历史持久化
"""

from __future__ import annotations

import json
import os
import sys
import time
from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path

from openai import APIError, OpenAI, RateLimitError


@dataclass
class ChatMessage:
    """单条对话消息。"""

    role: str
    content: str

    def to_dict(self) -> dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class ChatConfig:
    """对话配置参数。"""

    model: str = "deepseek-v4-pro"
    base_url: str = "https://api.deepseek.com"
    temperature: float = 0.7
    max_tokens: int | None = None
    stream: bool = True
    max_retries: int = 3
    retry_delay: float = 2.0


class DeepSeekClient:
    """DeepSeek API 客户端。

    Args:
        api_key: DeepSeek API 密钥，默认从环境变量 DEEPSEEK_API_KEY 读取
        config: 对话配置，默认使用 ChatConfig 默认值
    """

    def __init__(
        self,
        api_key: str | None = None,
        config: ChatConfig | None = None,
    ) -> None:
        self.api_key = api_key or os.environ.get("DEEPSEEK_API_KEY", "")
        if not self.api_key:
            raise ValueError("未提供 API Key，请设置 DEEPSEEK_API_KEY 环境变量")

        self.config = config or ChatConfig()
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.config.base_url,
        )
        self.history: list[ChatMessage] = []

    def chat(
        self,
        message: str,
        system_prompt: str | None = None,
        **kwargs,
    ) -> str:
        """发送单轮对话请求（非流式）。

        Args:
            message: 用户输入内容
            system_prompt: 可选的系统提示词
            **kwargs: 覆盖 config 中的参数，如 temperature、max_tokens

        Returns:
            模型生成的回复文本
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        return self._call_api(messages, **kwargs)

    def chat_stream(
        self,
        message: str,
        system_prompt: str | None = None,
        **kwargs,
    ) -> Generator[str, None, None]:
        """发送单轮对话请求（流式）。

        Yields:
            模型生成的文本片段
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": message})

        yield from self._call_api_stream(messages, **kwargs)

    def chat_with_history(
        self,
        message: str,
        system_prompt: str | None = None,
        save_history: bool = True,
        **kwargs,
    ) -> str:
        """发送多轮对话请求，自动维护上下文历史（非流式）。

        Args:
            message: 用户输入内容
            system_prompt: 可选的系统提示词，仅在首次调用时生效
            save_history: 是否将本轮对话保存到历史记录
            **kwargs: 覆盖 config 中的参数

        Returns:
            模型生成的回复文本
        """
        if system_prompt and not self.history:
            self.history.append(ChatMessage("system", system_prompt))

        self.history.append(ChatMessage("user", message))
        messages = [m.to_dict() for m in self.history]

        reply = self._call_api(messages, **kwargs)

        if save_history:
            self.history.append(ChatMessage("assistant", reply))

        return reply

    def chat_with_history_stream(
        self,
        message: str,
        system_prompt: str | None = None,
        save_history: bool = True,
        **kwargs,
    ) -> Generator[str, None, None]:
        """发送多轮对话请求，自动维护上下文历史（流式）。

        Yields:
            模型生成的文本片段
        """
        if system_prompt and not self.history:
            self.history.append(ChatMessage("system", system_prompt))

        self.history.append(ChatMessage("user", message))
        messages = [m.to_dict() for m in self.history]

        reply_parts: list[str] = []
        for part in self._call_api_stream(messages, **kwargs):
            reply_parts.append(part)
            yield part

        if save_history:
            self.history.append(ChatMessage("assistant", "".join(reply_parts)))

    def reset_history(self) -> None:
        """清空对话历史。"""
        self.history.clear()

    def save_history_to_file(self, path: str | Path) -> None:
        """将对话历史保存到 JSON 文件。"""
        data = [{"role": m.role, "content": m.content} for m in self.history]
        Path(path).write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def load_history_from_file(self, path: str | Path) -> None:
        """从 JSON 文件加载对话历史。"""
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        self.history = [ChatMessage(m["role"], m["content"]) for m in raw]

    def _build_params(self, messages: list[dict], **kwargs) -> dict:
        """构建 API 请求参数。"""
        return {
            "model": kwargs.get("model", self.config.model),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "stream": kwargs.get("stream", self.config.stream),
        }

    def _call_api(self, messages: list[dict], **kwargs) -> str:
        """调用 API（非流式，带重试）。"""
        params = self._build_params(messages, **kwargs)
        params["stream"] = False

        last_error: Exception | None = None
        for attempt in range(self.config.max_retries):
            try:
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content or ""
            except RateLimitError as e:
                last_error = e
                wait = self.config.retry_delay * (2**attempt)
                print(
                    f"[警告] 速率限制，{wait:.1f}秒后重试...",
                    file=sys.stderr,
                )
                time.sleep(wait)
            except APIError as e:
                last_error = e
                print(f"[警告] API 错误：{e}，正在重试...", file=sys.stderr)
                time.sleep(self.config.retry_delay)

        raise RuntimeError(
            f"请求失败，已重试 {self.config.max_retries} 次。"
        ) from last_error

    def _call_api_stream(
        self,
        messages: list[dict],
        **kwargs,
    ) -> Generator[str, None, None]:
        """调用 API（流式，带重试）。"""
        params = self._build_params(messages, **kwargs)
        params["stream"] = True

        for attempt in range(self.config.max_retries):
            try:
                response = self.client.chat.completions.create(**params)
                for chunk in response:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
                return
            except RateLimitError:
                wait = self.config.retry_delay * (2**attempt)
                print(
                    f"[警告] 速率限制，{wait:.1f}秒后重试...",
                    file=sys.stderr,
                )
                time.sleep(wait)
            except APIError as e:
                print(f"[警告] API 错误：{e}，正在重试...", file=sys.stderr)
                time.sleep(self.config.retry_delay)

        raise RuntimeError(f"流式请求失败，已重试 {self.config.max_retries} 次。")


def demo() -> None:
    """交互式演示：用户输入问题，模型实时回答。"""
    client = DeepSeekClient()

    print("=" * 40)
    print("DeepSeek 交互式对话演示")
    print(f"模型：{client.config.model}")
    print("输入问题后按回车，空行退出")
    print("=" * 40)

    while True:
        try:
            user_input = input("\n你：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break

        if not user_input:
            print("再见！")
            break

        print("助手：", end="", flush=True)
        for part in client.chat_with_history_stream(user_input):
            print(part, end="", flush=True)
        print()


if __name__ == "__main__":
    demo()
