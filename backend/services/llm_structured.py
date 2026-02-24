"""
구조적 LLM 응답(Structured Output) 공통 레이어.
create + json_object + 수동 파싱 사용. 구조적 출력 요청은 이 모듈을 통일 사용.
"""
import json
from typing import TypeVar

from openai import AsyncOpenAI, RateLimitError
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def parse_json_content(content: str) -> dict:
    """코드블록 제거 후 JSON 파싱."""
    if not content or not content.strip():
        raise ValueError("Empty model response")
    text = content.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines)
    return json.loads(text)


async def call_with_retry(func, max_retries: int = 3):
    """재시도 (RateLimitError: 지수 백오프, 기타: 1초)."""
    import asyncio

    for attempt in range(max_retries):
        try:
            return await func()
        except RateLimitError:
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                raise
        except Exception:
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            else:
                raise


async def chat_completion_structured(
    client: AsyncOpenAI,
    *,
    model: str,
    messages: list[dict],
    temperature: float,
    response_model: type[T],
    max_retries: int = 3,
) -> T:
    """JSON 모드로 완성 후 Pydantic 검증 반환."""
    async def _call():
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        if not content:
            raise ValueError("Empty completion response")
        data = parse_json_content(content)
        return response_model.model_validate(data)

    return await call_with_retry(_call, max_retries=max_retries)
