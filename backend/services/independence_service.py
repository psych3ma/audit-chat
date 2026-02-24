"""독립성 검토: 관계 추출, 독립성 분석, Mermaid 생성, Neo4j 저장. 구조적 출력은 llm_structured 사용."""
import hashlib
import logging
import re
from openai import AsyncOpenAI

from backend.config import get_settings
from backend.models.independence import AnalysisResult, IndependenceMap, LegalRefItem, VulnerableConnection
from backend.services.llm_structured import chat_completion_structured
from backend.utils.law_registry import get_law_url, is_valid_law

logger = logging.getLogger(__name__)


def get_trace_id(scenario: str) -> str:
    """시나리오 MD5 해시 8자리. Neo4j 캐시 키(trace_id)."""
    return hashlib.md5(scenario.encode()).hexdigest()[:8].upper()


def _enrich_legal_ref_urls(analysis: AnalysisResult) -> AnalysisResult:
    """legal_references에 url 없으면 CSV 레지스트리로 URL 보강. CSV에 없으면 텍스트만 표시."""
    if not analysis.legal_references:
        return analysis
    enriched = []
    no_url_items = []
    for ref in analysis.legal_references:
        name = ref.name.strip()
        # CSV에 있는 법령만 URL 생성
        if is_valid_law(name):
            url = ref.url or get_law_url(name)
            enriched.append(LegalRefItem(name=name, url=url))
        else:
            # CSV에 없으면 URL 없음
            no_url_items.append(name)
            enriched.append(LegalRefItem(name=name, url=None))
    if no_url_items:
        logger.info(f"URL 미생성 (CSV에 없음, 텍스트만 표시): {no_url_items}")
    return analysis.model_copy(update={"legal_references": enriched})


# 프롬프트
class _PromptTemplates:
    EXTRACTION_SYSTEM = """You are an expert at extracting structured relationships from Korean audit scenarios.
Output only valid JSON with this exact structure (no markdown, no explanation):
{"entities": [{"id": "string (alphanumeric)", "label": "string", "name": "string"}], "connections": [{"source_id": "string", "target_id": "string", "rel_type": "string"}]}
Use Korean for "label" and "rel_type" when the scenario is in Korean (e.g. rel_type: 소속, 감사대상, 직계가족, 대표이사)."""

    ANALYSIS_SYSTEM = """You are a Senior Partner in the Quality Control department of a Korean accounting firm.
Assess auditor independence based on Korean laws and professional standards.

Rules:
1. Base your assessment strictly on the Scenario and the Relationship Map. In key_issues and considerations, cite specific entity names and relationship types from the map (e.g. person names, firm names, rel_type).
2. Write all of the following in Korean only: key_issues, considerations, suggested_safeguards, legal_references. Do not use English for these fields.
3. considerations: Write a clear paragraph of at least 2–4 sentences explaining the independence threat and your reasoning. Be concrete.
4. key_issues: List concrete issues that reference the scenario and the Relationship Map; avoid one-line generic statements.
5. legal_references: You may cite Korean laws (e.g. "공인회계사법 제21조") and professional standards/ethics codes (e.g. "공인회계사 윤리기준", "회계감사기준").
6. vulnerable_connections: IMPORTANT - Identify which specific connections in the Relationship Map cause independence threats. Use the exact source_id and target_id from the map. This will be highlighted in the visualization.

Output only valid JSON with: "status" (one of: 수임 불가, 안전장치 적용 시 수임 가능, 수임 가능), "risk_level", "key_issues" (array of strings, Korean), "legal_references" (array of strings e.g. ["공인회계사법 제21조"] or objects with "name" and optional "url"), "considerations" (string, Korean, 2–4 sentences), "suggested_safeguards" (array of strings, Korean), "vulnerable_connections" (array of objects with "source_id", "target_id", and optional "reason" in Korean - identify the problematic relationships from the map). No markdown, no explanation."""

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


def build_mermaid_graph(
    rel_map: IndependenceMap,
    vulnerable_connections: list[VulnerableConnection] | None = None
) -> str:
    """Mermaid flowchart. 취약 관계는 점선·[!] 라벨로 표시."""
    lines = ["graph TD"]
    vulnerable_set = set()
    vulnerable_entities = set()
    if vulnerable_connections:
        for vc in vulnerable_connections:
            vulnerable_set.add((vc.source_id, vc.target_id))
            vulnerable_entities.add(vc.source_id)
            vulnerable_entities.add(vc.target_id)
    
    shape_map = {
        "회계법인": ("[[", "]]"),
        "감사인": ("[[", "]]"),
        "공인회계사": ("([", "])"),
        "인물": ("([", "])"),
        "회사": ("[", "]"),
        "피감사회사": ("[", "]"),
        "감사대상회사": ("[", "]"),
        "배우자": ("((", "))"),
        "가족": ("((", "))"),
        "직계가족": ("((", "))"),
        "임원": ("(", ")"),
        "이사": ("(", ")"),
        "대표이사": ("(", ")"),
        "재무이사": ("(", ")"),
    }
    
    lines.append("    classDef normalNode fill:#fff,stroke:#333,stroke-width:1px")
    lines.append("    classDef riskyNode fill:#fff5f5,stroke:#c62828,stroke-width:2px,stroke-dasharray:5 5")
    
    # 노드 정의
    for entity in rel_map.entities:
        clean_name = re.sub(r"[^가-힣a-zA-Z0-9\s]", "", entity.name)
        label = entity.label or ""
        open_s, close_s = shape_map.get(label, ("[", "]"))
        node_text = f"{clean_name}<br>{label}" if label else clean_name
        node_class = "riskyNode" if entity.id in vulnerable_entities else "normalNode"
        lines.append(f'    {entity.id}{open_s}"{node_text}"{close_s}:::{node_class}')
    
    # 엣지 정의
    for conn in rel_map.connections:
        raw_rel = (conn.rel_type or "관계").strip()[:20]
        rel = raw_rel.replace('"', "'").replace("\n", " ")
        is_vulnerable = (conn.source_id, conn.target_id) in vulnerable_set
        if is_vulnerable:
            # 취약 관계: 점선 + [!] 라벨
            lines.append(f'    {conn.source_id} -. "[!] {rel}" .-> {conn.target_id}')
        else:
            lines.append(f'    {conn.source_id} ---|"{rel}"| {conn.target_id}')
    
    return "\n".join(lines)


def get_independence_map_from_neo4j(trace_id: str) -> IndependenceMap | None:
    """trace_id로 Neo4j에서 엔티티-관계 조회. 없으면 None."""
    from backend.database import get_neo4j_session
    from backend.models.independence import AuditEntity, Relationship

    try:
        with get_neo4j_session() as session:
            entity_result = session.run(
                """
                MATCH (n:IndependenceEntity {trace_id: $trace_id})
                RETURN n.id AS id, n.label AS label, n.name AS name
                ORDER BY n.id
                """,
                trace_id=trace_id,
            )
            
            entities_data = [record.data() for record in entity_result]
            
            if not entities_data:
                return None
            
            entities = [
                AuditEntity(
                    id=record["id"],
                    label=record["label"],
                    name=record["name"],
                )
                for record in entities_data
            ]
            
            relation_result = session.run(
                """
                MATCH (a:IndependenceEntity {trace_id: $trace_id})-[r:RELATION]->(b:IndependenceEntity {trace_id: $trace_id})
                RETURN a.id AS source_id, b.id AS target_id, r.rel_type AS rel_type
                ORDER BY a.id, b.id
                """,
                trace_id=trace_id,
            )
            
            connections_data = [record.data() for record in relation_result]
            
            connections = [
                Relationship(
                    source_id=record["source_id"],
                    target_id=record["target_id"],
                    rel_type=record["rel_type"] or "RELATES",
                )
                for record in connections_data
            ]
            
            return IndependenceMap(entities=entities, connections=connections)
            
    except Exception:
        return None


def save_independence_map_to_neo4j(trace_id: str, rel_map: IndependenceMap) -> None:
    """엔티티·관계를 Neo4j에 저장 (trace_id별)."""
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


def build_independence_report(
    scenario: str,
    rel_map: IndependenceMap,
    analysis: AnalysisResult,
    save_to_neo4j: bool = True,
) -> dict:
    """3단계: 법령 URL 보강, Mermaid 생성, Neo4j 저장."""
    trace_id = get_trace_id(scenario)
    analysis = _enrich_legal_ref_urls(analysis)
    mermaid_code = build_mermaid_graph(rel_map, analysis.vulnerable_connections)
    if save_to_neo4j:
        try:
            save_independence_map_to_neo4j(trace_id, rel_map)
        except Exception:
            pass
    return {
        "trace_id": trace_id,
        "rel_map": rel_map.model_dump(),
        "analysis": analysis.model_dump(),
        "mermaid_code": mermaid_code,
    }


async def run_independence_review(scenario: str, save_to_neo4j: bool = True) -> dict:
    """캐시 조회 → 추출(필요 시) → 분석 → Mermaid·Neo4j 저장."""
    scenario_stripped = scenario.strip()
    trace_id = get_trace_id(scenario_stripped)
    rel_map = get_independence_map_from_neo4j(trace_id)
    if rel_map is None:
        rel_map = await extract_relationships(scenario_stripped)
    analysis = await analyze_independence(scenario_stripped, rel_map)
    return build_independence_report(scenario_stripped, rel_map, analysis, save_to_neo4j=save_to_neo4j)
