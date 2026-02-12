"""독립성 검토 API (감사 수임 독립성)."""
from fastapi import APIRouter, HTTPException

from backend.models.independence import IndependenceReviewRequest
from backend.services.independence_service import run_independence_review

router = APIRouter(prefix="/independence", tags=["independence"])


@router.post("/review")
async def post_independence_review(body: IndependenceReviewRequest):
    """감사 시나리오 입력 → 관계 추출(GPT-4o-mini) → 독립성 분석(GPT-4o) → Mermaid + Neo4j 저장."""
    try:
        result = await run_independence_review(body.scenario.strip(), save_to_neo4j=True)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
