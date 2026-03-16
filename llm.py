"""
LLM 客户端 — OpenAI 兼容 API，支持流式输出
"""

from openai import OpenAI
from typing import Generator, Optional


def create_client(api_key: str, base_url: str) -> OpenAI:
    return OpenAI(api_key=api_key, base_url=base_url)


def stream_analysis(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_content: str,
    temperature: float = 0.1,
    max_tokens: int = 16000,
) -> Generator[str, None, None]:
    """
    流式调用 LLM 进行论文分析。
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        stream=True,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    for chunk in response:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


def run_analysis(
    client: OpenAI,
    model: str,
    system_prompt: str,
    user_content: str,
    temperature: float = 0.1,
    max_tokens: int = 16000,
) -> str:
    """
    非流式调用，返回完整结果。
    """
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_content},
        ],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content or ""
