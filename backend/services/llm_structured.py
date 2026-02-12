"""
구조적 LLM 응답(Structured Output) 공통 레이어.

CTO 관점 — 유지보수/확장성/일관성:
- openai 1.12에는 client.beta.chat.completions.parse()가 없어, create + json_object + 수동 파싱 사용.
- 모든 구조적 출력 요청은 이 모듈을 통일 사용 → SDK/API 변경 시 이 파일만 수정.
- 신규 구조적 엔드포인트 추가 시 chat_completion_structured() 재사용.
"""
import json
from typing import TypeVar

from openai import AsyncOpenAI, RateLimitError
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def parse_json_content(content: str) -> dict:
    """마크다운 코드블록 제거 후 JSON 파싱. LLM이 ```json ... ``` 으로 감쌀 때 대응."""
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
    """RateLimitError 시 지수 백오프, 기타 예외 시 1초 후 재시도."""
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
    """
    JSON 모드로 채팅 완성 후 Pydantic 모델로 검증 반환.

    openai 1.12 호환: client.chat.completions.create(response_format={"type": "json_object"}) 사용.
    추후 SDK에 chat.completions.parse() 지원 시 이 함수 내부만 교체하면 됨.
    """
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
