"""
FastAPI 백엔드 호출용 클라이언트.
환경 변수 또는 기본값으로 API URL 사용.
"""
import os
from typing import Any

import httpx

# 백엔드 기본 URL (run.sh와 동일 포트)
API_BASE = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT = 30.0


def _url(path: str) -> str:
    return f"{API_BASE.rstrip('/')}{path}"


def get_health() -> dict[str, Any]:
    """헬스 체크."""
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.get(_url("/health"))
        r.raise_for_status()
        return r.json()


def post_chat(messages: list[dict[str, str]], stream: bool = False) -> dict[str, Any]:
    """채팅 완성 요청."""
    with httpx.Client(timeout=60.0) as client:
        r = client.post(
            _url("/chat/completions"),
            json={"messages": messages, "stream": stream},
        )
        r.raise_for_status()
        return r.json()


def get_graph_mermaid() -> dict[str, Any]:
    """그래프 Mermaid 코드 조회."""
    with httpx.Client(timeout=TIMEOUT) as client:
        r = client.get(_url("/graph/mermaid"))
        r.raise_for_status()
        return r.json()
