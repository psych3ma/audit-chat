"""독립성 검토 엔진: 관계 추출, 독립성 분석, Mermaid 생성, Neo4j 저장.

Colab과 동일한 2단계(관계 추출 → 독립성 분석). 구조적 출력은 llm_structured 공통 레이어 사용."""
import hashlib
import re
from openai import AsyncOpenAI

from backend.config import get_settings
from backend.models.independence import AnalysisResult, IndependenceMap, LegalRefItem
from backend.services.llm_structured import chat_completion_structured
from backend.utils.law_registry import get_law_url


def _enrich_legal_ref_urls(analysis: AnalysisResult) -> AnalysisResult:
    """legal_references에 url이 없으면 법령 레지스트리(CSV 기반)로 URL 보강."""
    if not analysis.legal_references:
        return analysis
    enriched = []
    for ref in analysis.legal_references:
        url = ref.url or get_law_url(ref.name.strip())
        enriched.append(LegalRefItem(name=ref.name, url=url))
    return analysis.model_copy(update={"legal_references": enriched})


# 프롬프트 (Colab 기반 + 보고서 품질·언어 일관성 보강)
class _PromptTemplates:
    EXTRACTION_SYSTEM = """You are an expert at extracting structured relationships from Korean audit scenarios.
Output only valid JSON with this exact structure (no markdown, no explanation):
{"entities": [{"id": "string (alphanumeric)", "label": "string", "name": "string"}], "connections": [{"source_id": "string", "target_id": "string", "rel_type": "string"}]}
Use Korean for "label" and "rel_type" when the scenario is in Korean (e.g. rel_type: 소속, 감사대상, 직계가족, 대표이사)."""

    ANALYSIS_SYSTEM = """You are a Senior Partner in the Quality Control department of a Korean accounting firm.
Assess auditor independence based on the Korean External Audit Act and Ethics Code.

Rules:
1. Base your assessment strictly on the Scenario and the Relationship Map. In key_issues and considerations, cite specific entity names and relationship types from the map (e.g. person names, firm names, rel_type).
2. Write all of the following in Korean only: key_issues, considerations, suggested_safeguards, legal_references. Do not use English for these fields.
3. considerations: Write a clear paragraph of at least 2–4 sentences explaining the independence threat and your reasoning. Be concrete.
4. key_issues: List concrete issues that reference the scenario and the Relationship Map; avoid one-line generic statements.

Output only valid JSON with: "status" (one of: 수임 불가, 안전장치 적용 시 수임 가능, 수임 가능), "risk_level", "key_issues" (array of strings, Korean), "legal_references" (array of strings e.g. ["공인회계사법 제21조"] or objects with "name" and optional "url"), "considerations" (string, Korean, 2–4 sentences), "suggested_safeguards" (array of strings, Korean). No markdown, no explanation."""

    ANALYSIS_USER = "Scenario: {scenario}\n\nRelationship Map: {map_json}\n\nUsing the entities and relationships in the map above, provide your assessment in JSON only. Refer to specific entities and rel_type in your key_issues and considerations."

    @staticmethod
    def analysis_user(scenario: str, map_json: str) -> str:
        return _PromptTemplates.ANALYSIS_USER.format(scenario=scenario, map_json=map_json)


def _get_openai_client() -> AsyncOpenAI:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
    return AsyncOpenAI(api_key=settings.openai_api_key)


async def extract_relationships(scenario_text: str) -> IndependenceMap:
    settings = get_settings()
    client = _get_openai_client()
    return await chat_completion_structured(
        client,
        model=settings.independence_extraction_model,
        messages=[
            {"role": "system", "content": _PromptTemplates.EXTRACTION_SYSTEM},
            {"role": "user", "content": scenario_text},
        ],
        temperature=settings.independence_temperature_structured,
        response_model=IndependenceMap,
    )


async def analyze_independence(scenario_text: str, rel_map: IndependenceMap) -> AnalysisResult:
    settings = get_settings()
    client = _get_openai_client()
    user_prompt = _PromptTemplates.analysis_user(
        scenario_text, rel_map.model_dump_json(indent=2)
    )
    return await chat_completion_structured(
        client,
        model=settings.independence_analysis_model,
        messages=[
            {"role": "system", "content": _PromptTemplates.ANALYSIS_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        temperature=settings.independence_temperature_creative,
        response_model=AnalysisResult,
    )


def build_mermaid_graph(rel_map: IndependenceMap) -> str:
    """Colab ReportGenerator.build_mermaid_graph와 동일 형식."""
    lines = ["graph LR"]
    for entity in rel_map.entities:
        clean_name = re.sub(r"[^가-힣a-zA-Z0-9\s]", "", entity.name)
        lines.append(f'    {entity.id}["{clean_name}<br/>({entity.label})"]')
    for conn in rel_map.connections:
        rel_type = (conn.rel_type or "RELATES").replace('"', "'")[:30]
        lines.append(f'    {conn.source_id} -- "{rel_type}" --> {conn.target_id}')
    return "\n".join(lines)


def save_independence_map_to_neo4j(trace_id: str, rel_map: IndependenceMap) -> None:
    """독립성 검토 결과(엔티티·관계)를 Neo4j에 저장. 실행(trace_id)별로 서브그래프 분리."""
    from backend.database import get_neo4j_session

    with get_neo4j_session() as session:
        for entity in rel_map.entities:
            session.run(
                """
                CREATE (n:IndependenceEntity {trace_id: $trace_id, id: $id, label: $label, name: $name})
                """,
                trace_id=trace_id,
                id=entity.id,
                label=entity.label,
                name=entity.name,
            )
        for conn in rel_map.connections:
            session.run(
                """
                MATCH (a:IndependenceEntity {trace_id: $trace_id, id: $source_id})
                MATCH (b:IndependenceEntity {trace_id: $trace_id, id: $target_id})
                CREATE (a)-[:RELATION {rel_type: $rel_type}]->(b)
                """,
                trace_id=trace_id,
                source_id=conn.source_id,
                target_id=conn.target_id,
                rel_type=conn.rel_type or "RELATES",
            )


async def run_independence_review(scenario: str, save_to_neo4j: bool = True) -> dict:
    """추출 → 분석 → Mermaid 생성. 선택 시 Neo4j 저장."""
    trace_id = hashlib.md5(scenario.encode()).hexdigest()[:8].upper()
    rel_map = await extract_relationships(scenario)
    analysis = await analyze_independence(scenario, rel_map)
    analysis = _enrich_legal_ref_urls(analysis)
    mermaid_code = build_mermaid_graph(rel_map)
    if save_to_neo4j:
        try:
            save_independence_map_to_neo4j(trace_id, rel_map)
        except Exception:
            pass  # Neo4j 미연결 시 무시
    return {
        "trace_id": trace_id,
        "rel_map": rel_map.model_dump(),
        "analysis": analysis.model_dump(),
        "mermaid_code": mermaid_code,
    }
