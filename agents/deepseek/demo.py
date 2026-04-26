"""DeepSeek V4-Pro 调用示例。

使用方法：
    1. 复制 .env.example 为 .env，填入你的 DEEPSEEK_API_KEY
    2. 运行：python -m agents.deepseek.demo

注意：
    - 不要将真实 API Key 写入代码或提交到仓库
    - .env 文件已被 .gitignore 排除
"""

import os
import sys

from openai import OpenAI


def get_client() -> OpenAI:
    """初始化 DeepSeek 客户端，从环境变量读取配置。"""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        print("错误：未设置 DEEPSEEK_API_KEY 环境变量", file=sys.stderr)
        print("请执行：export DEEPSEEK_API_KEY='your-api-key'", file=sys.stderr)
        sys.exit(1)

    base_url = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    return OpenAI(api_key=api_key, base_url=base_url)


def chat_completion(
    client: OpenAI,
    messages: list[dict[str, str]],
    model: str = "deepseek-v4-pro",
    stream: bool = True,
) -> str:
    """发送聊天请求并返回回复内容。

    Args:
        client: OpenAI 客户端实例
        messages: 消息列表，格式为 [{"role": "user", "content": "..."}, ...]
        model: 模型名称，默认 deepseek-v4-pro
        stream: 是否使用流式输出

    Returns:
        模型生成的回复文本
    """
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        stream=stream,
    )

    if stream:
        content_parts = []
        print("助手：", end="", flush=True)
        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content:
                part = chunk.choices[0].delta.content
                print(part, end="", flush=True)
                content_parts.append(part)
        print()
        return "".join(content_parts)

    return response.choices[0].message.content


def main() -> None:
    """主函数：演示单次对话。"""
    client = get_client()
    model = os.environ.get("DEEPSEEK_MODEL", "deepseek-v4-pro")

    messages = [
        {"role": "system", "content": "你是一个 helpful 的 AI 助手。"},
        {"role": "user", "content": "你好，请简单介绍一下 DeepSeek V4-Pro 的特点。"},
    ]

    print(f"使用模型：{model}\n")

    # 流式输出（默认开启）
    print("--- 流式输出 ---")
    chat_completion(client, messages, model=model, stream=True)


def run() -> None:
    """Agent 风格的统一入口。"""
    main()


if __name__ == "__main__":
    run()
