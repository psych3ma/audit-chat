"""독립성 검토 엔진: 관계 추출, 독립성 분석, Mermaid 생성, Neo4j 저장."""
import hashlib
import re
from openai import AsyncOpenAI, RateLimitError

from backend.config import get_settings
from backend.models.independence import AnalysisResult, IndependenceMap

# 프롬프트 (Colab과 동일)
class _PromptTemplates:
    EXTRACTION_SYSTEM = """You are an expert at extracting structured relationships from Korean audit scenarios.
Output only the structured data in JSON format."""

    ANALYSIS_SYSTEM = """You are a Senior Partner in the Quality Control department of a Korean accounting firm.
Assess auditor independence based on the Korean External Audit Act and Ethics Code."""

    @staticmethod
    def analysis_user(scenario: str, map_json: str) -> str:
        return f"Scenario: {scenario}\n\nRelationship Map: {map_json}\n\nProvide assessment in JSON."


async def _call_with_retry(func, max_retries: int = 3):
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


async def extract_relationships(scenario_text: str) -> IndependenceMap:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    extraction_model = settings.independence_extraction_model
    analysis_model = settings.independence_analysis_model

    async def _extract():
        response = await client.beta.chat.completions.parse(
            model=extraction_model,
            messages=[
                {"role": "system", "content": _PromptTemplates.EXTRACTION_SYSTEM},
                {"role": "user", "content": scenario_text},
            ],
            temperature=0.0,
            response_format=IndependenceMap,
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Failed to parse extraction response")
        return parsed

    return await _call_with_retry(_extract)


async def analyze_independence(scenario_text: str, rel_map: IndependenceMap) -> AnalysisResult:
    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    analysis_model = settings.independence_analysis_model

    user_prompt = _PromptTemplates.analysis_user(
        scenario_text, rel_map.model_dump_json(indent=2)
    )

    async def _analyze():
        response = await client.beta.chat.completions.parse(
            model=analysis_model,
            messages=[
                {"role": "system", "content": _PromptTemplates.ANALYSIS_SYSTEM},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            response_format=AnalysisResult,
        )
        parsed = response.choices[0].message.parsed
        if parsed is None:
            raise ValueError("Failed to parse analysis response")
        return parsed

    return await _call_with_retry(_analyze)


def build_mermaid_graph(rel_map: IndependenceMap) -> str:
    lines = ["graph LR"]
    for entity in rel_map.entities:
        clean_name = re.sub(r"[^가-힣a-zA-Z0-9\s]", "", entity.name)
        lines.append(f'    {entity.id}["{clean_name}<br/>({entity.label})"]')
    for conn in rel_map.connections:
        safe_rel = (conn.rel_type or "RELATES").replace('"', "'")[:30]
        lines.append(f'    {conn.source_id} -->|"{safe_rel}"| {conn.target_id}')
    return "\n".join(lines)


def save_independence_map_to_neo4j(trace_id: str, rel_map: IndependenceMap) -> None:
    """독립성 검토 결과(엔티티·관계)를 Neo4j에 저장."""
    from backend.database import get_neo4j_session

    with get_neo4j_session() as session:
        for entity in rel_map.entities:
            session.run(
                """
                MERGE (n:IndependenceEntity {id: $id})
                SET n.label = $label, n.name = $name, n.trace_id = $trace_id
                """,
                id=entity.id,
                label=entity.label,
                name=entity.name,
                trace_id=trace_id,
            )
        for conn in rel_map.connections:
            session.run(
                """
                MATCH (a:IndependenceEntity {id: $source_id})
                MATCH (b:IndependenceEntity {id: $target_id})
                CREATE (a)-[:RELATION {trace_id: $trace_id, rel_type: $rel_type}]->(b)
                """,
                source_id=conn.source_id,
                target_id=conn.target_id,
                rel_type=conn.rel_type or "RELATES",
                trace_id=trace_id,
            )


async def run_independence_review(scenario: str, save_to_neo4j: bool = True) -> dict:
    """추출 → 분석 → Mermaid 생성. 선택 시 Neo4j 저장."""
    trace_id = hashlib.md5(scenario.encode()).hexdigest()[:8].upper()
    rel_map = await extract_relationships(scenario)
    analysis = await analyze_independence(scenario, rel_map)
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
