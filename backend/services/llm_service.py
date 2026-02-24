"""LLM integration (OpenAI-compatible)."""
from typing import Any
from backend.config import get_settings


def get_llm_response(
    messages: list[dict[str, Any]],
    stream: bool = False,
) -> str:
    """OpenAI 채팅 완성. API 키 없으면 플레이스홀더 반환."""
    settings = get_settings()
    if not settings.openai_api_key:
        return (
            "LLM이 설정되지 않았습니다. .env에 OPENAI_API_KEY를 설정해 주세요. "
            "(현재는 데모 모드입니다.)"
        )

    try:
        from openai import OpenAI

        client = OpenAI(api_key=settings.openai_api_key)
        resp = client.chat.completions.create(
            model=settings.llm_model,
            messages=messages,
            temperature=settings.llm_temperature,
            stream=stream,
        )
        if stream:
            return "".join(
                chunk.choices[0].delta.content or ""
                for chunk in resp
            )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        return f"LLM 오류: {e!s}"
