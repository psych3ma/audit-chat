"""
FastAPI 백엔드 호출용 클라이언트.
환경 변수 또는 .env 기반으로 API URL 사용.
"""
import os
from pathlib import Path
from typing import Any

import httpx

# 프로젝트 루트 .env 로드 (Streamlit 단독 실행 시에도 포트 일치)
try:
    from dotenv import load_dotenv
    _root = Path(__file__).resolve().parent.parent
    load_dotenv(_root / ".env")
except Exception:
    pass

_api_port = os.getenv("API_PORT", "8000")
API_BASE = os.getenv("API_BASE_URL") or f"http://localhost:{_api_port}"
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


def post_independence_review(scenario: str) -> dict[str, Any]:
    """독립성 검토: 시나리오 → 관계 추출 + 독립성 분석 + Mermaid."""
    with httpx.Client(timeout=120.0) as client:
        r = client.post(
            _url("/independence/review"),
            json={"scenario": scenario},
        )
        r.raise_for_status()
        return r.json()
