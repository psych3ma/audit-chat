"""독립성 검토 API (감사 수임 독립성)."""
from fastapi import APIRouter, HTTPException

from backend.models.independence import IndependenceReviewRequest
from backend.services.independence_service import run_independence_review

router = APIRouter(prefix="/independence", tags=["independence"])


def _normalize_error_detail(e: Exception) -> str:
    """사용자에게 보여줄 에러 메시지 정리 (API 키/OpenAI/파싱 구분)."""
    msg = str(e).strip()
    if not msg:
        return "서버 오류가 발생했습니다."
    if "OPENAI_API_KEY" in msg or "api_key" in msg.lower():
        return "OPENAI_API_KEY가 .env에 설정되지 않았거나 유효하지 않습니다. .env 파일을 확인하세요."
    if "authentication" in msg.lower() or "invalid_api_key" in msg.lower() or "incorrect api key" in msg.lower():
        return "OpenAI API 키가 올바르지 않습니다. .env의 OPENAI_API_KEY를 확인하세요."
    if "rate" in msg.lower() or "limit" in msg.lower():
        return "OpenAI 요청 한도 초과입니다. 잠시 후 다시 시도하세요."
    return msg[:500]


@router.post("/review")
async def post_independence_review(body: IndependenceReviewRequest):
    """감사 시나리오 입력 → 관계 추출(GPT-4o-mini) → 독립성 분석(GPT-4o) → Mermaid + Neo4j 저장."""
    try:
        result = await run_independence_review(body.scenario.strip(), save_to_neo4j=True)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=_normalize_error_detail(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=_normalize_error_detail(e))
