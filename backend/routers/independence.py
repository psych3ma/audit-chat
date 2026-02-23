"""독립성 검토 API (감사 수임 독립성). 단계별 엔드포인트로 실제 진행률 연동 (docs/WORKFLOW_STEP_CODE_MAPPING.md)."""
from fastapi import APIRouter, HTTPException

from backend.models.independence import (
    AnalysisResult,
    IndependenceMap,
    IndependenceReviewRequest,
    AnalyzeStepRequest,
    ReportStepRequest,
)
from backend.services.independence_service import (
    extract_relationships,
    analyze_independence,
    build_independence_report,
    get_independence_map_from_neo4j,
    get_trace_id,
    run_independence_review,
)

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
    """감사 시나리오 입력 → 관계 추출(GPT-4o-mini) → 독립성 분석(GPT-4o) → Mermaid + Neo4j 저장. (일괄 호출용)"""
    try:
        result = await run_independence_review(body.scenario.strip(), save_to_neo4j=True)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=_normalize_error_detail(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=_normalize_error_detail(e))


@router.post("/extract")
async def post_extract(body: IndependenceReviewRequest):
    """1단계: 관계 추출. Neo4j 캐시 있으면 재사용, 없으면 LLM 추출. 프로그레스 1→2 전환은 이 응답 수신 시점에 수행."""
    try:
        scenario_stripped = body.scenario.strip()
        trace_id = get_trace_id(scenario_stripped)
        rel_map = get_independence_map_from_neo4j(trace_id)
        if rel_map is None:
            rel_map = await extract_relationships(scenario_stripped)
        return {"rel_map": rel_map.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=_normalize_error_detail(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=_normalize_error_detail(e))


@router.post("/analyze")
async def post_analyze(body: AnalyzeStepRequest):
    """2단계: 독립성 분석. 프로그레스 2→3 전환은 이 응답 수신 시점에 수행."""
    try:
        rel_map = IndependenceMap.model_validate(body.rel_map)
        analysis = await analyze_independence(body.scenario.strip(), rel_map)
        return {"analysis": analysis.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=_normalize_error_detail(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=_normalize_error_detail(e))


@router.post("/report")
async def post_report(body: ReportStepRequest):
    """3단계: 보고서 생성(법령 URL 보강, Mermaid, Neo4j). 완료 시 프론트에서 카드 렌더."""
    try:
        rel_map = IndependenceMap.model_validate(body.rel_map)
        analysis = AnalysisResult.model_validate(body.analysis)
        result = build_independence_report(
            body.scenario.strip(), rel_map, analysis, save_to_neo4j=True
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=_normalize_error_detail(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=_normalize_error_detail(e))
