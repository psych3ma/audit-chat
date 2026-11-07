"""독립성 검토: 관계 추출, 독립성 분석, Mermaid 생성, Neo4j 저장. 구조적 출력은 llm_structured 사용."""
import hashlib
import logging
import re
from openai import AsyncOpenAI

from backend.config import get_settings
from backend.models.independence import AnalysisResult, IndependenceMap, LegalRefItem, VulnerableConnection
from backend.services.llm_structured import chat_completion_structured
from backend.utils.law_registry import resolve_reference_url

logger = logging.getLogger(__name__)


def get_trace_id(scenario: str) -> str:
    """시나리오 MD5 해시 8자리. Neo4j 캐시 키(trace_id)."""
    return hashlib.md5(scenario.encode()).hexdigest()[:8].upper()


def _enrich_legal_ref_urls(analysis: AnalysisResult) -> AnalysisResult:
    """legal_references URL 보강: CSV/조문 → 표준 맵. 없으면 텍스트만."""
    if not analysis.legal_references:
        return analysis
    enriched = []
    no_url_items = []
    for ref in analysis.legal_references:
        name = ref.name.strip()
        url = resolve_reference_url(name, ref.url)
        enriched.append(LegalRefItem(name=name, url=url))
        if not url:
            no_url_items.append(name)
    if no_url_items:
        logger.info("URL 미생성 (CSV·표준 맵에 없음, 텍스트만 표시): %s", no_url_items)
    return analysis.model_copy(update={"legal_references": enriched})



# 프롬프트
class _PromptTemplates:
    EXTRACTION_SYSTEM = """당신은 한국 회계감사 독립성 시나리오에서 인물·법인과 그 관계를 추출하는 그래프 데이터 전문가입니다.
설명이나 마크다운(```json) 없이 아래 JSON 구조만 정확히 출력하세요:
{"entities": [{"id": "e1", "label": "구분명", "name": "고유명칭"}], "connections": [{"source_id": "e1", "target_id": "e2", "rel_type": "관계명"}]}

[필수 추출 규칙]
1. 엔티티(entities) 추출:
   - 시나리오에 등장하는 실제 주체(회계법인, 공인회계사, 감사대상회사, 자회사, 임원, 사원, 친족, 주주 등)만 엔티티로 등록하세요.
   - "label"에는 역할/분류(예: "공인회계사", "회계법인", "회사", "비영리법인", "사원", "임원", "친족", "주주")를 적고, "name"에는 고유 이름(예: "이언변 공인회계사", "전북㈜", "한국회계법인")을 적으세요.
   - 소송사건, 채용면접, 평가업무 같은 '사건'이나 '행위'는 절대 엔티티로 만들지 마세요.

2. 관계(connections) 방향 및 셀프 루프(Self-Loop) 절대 금지:
   - 모든 관계는 반드시 서로 다른 두 엔티티(`source_id` != `target_id`)를 연결해야 합니다. **어떠한 경우에도 `source_id`와 `target_id`가 같은 값(예: 회사 -> 회사)이 되어서는 안 됩니다.**
   - 감사인이 회사를 위해 수행한 행위나 관여(외부감사, 소송대변/소송관여, 채용면접관여, 가치평가용역, 감사보수의존 등)는 반드시 **감사인(`source_id`)에서 해당 회사(`target_id`)로 향하는 연결선**으로 만드세요.
     * 올바른 예: `{"source_id": "공인회계사_ID", "target_id": "회사_ID", "rel_type": "외부감사인"}`, `{"source_id": "공인회계사_ID", "target_id": "회사_ID", "rel_type": "소송대변"}`
     * 잘못된 예(절대 금지): `{"source_id": "회사_ID", "target_id": "회사_ID", "rel_type": "소송관여"}`

3. 복합 지배구조 및 친족 관계 포함:
   - 모자회사 지분보유(`지분보유`), 회계법인 간 합병(`흡수합병`), 회계법인 소속(`소속사원`), 임원 재직(`대표이사`, `CFO`), 가족 관계(`친형`, `배우자`, `직계가족`) 등 시나리오의 모든 연결고리를 빠짐없이 추출하세요.
"""

    ANALYSIS_SYSTEM = """당신은 한국 회계법인 심리실(Quality Control) 총괄 파트너입니다.
제공된 시나리오와 관계도(Relationship Map)를 바탕으로 감사인의 독립성을 검토하고, 설명이나 마크다운 없이 오직 유효한 JSON만 출력하세요.

### 1. 근거 법령(`legal_references`) 표기 절대 규칙 (링크 자동 생성용)
시스템이 법령 링크를 생성하려면 `legal_references` 배열의 `"name"` 값은 **아래 허용된 조문 명칭과 글자 하나 틀리지 않고 정확히 일치**해야 합니다.
- **절대 금지**: `"공인회계사법 - 감사인의 독립성"`, `"공인회계사법 - 독립성 관련 규정"`, `"공인회계사 윤리기준"`처럼 하이픈(`-`)이나 설명이 붙은 문구는 **절대 출력하지 마세요.** 또한 `"제1항"`, `"제2호"` 같은 세부 항·호도 절대 붙이지 마세요.
- **감사인 주체별 필수 선택 조문**:
  1) 감사인이 **회계법인**인 경우: 반드시 **`"공인회계사법 제33조"`**를 포함하세요. (회계법인 자체의 지분 보유, 합병으로 인한 지분 승계, 보수 의존도, 소속 사원이나 그 친족[친형 등]과 피감사회사 임원[CFO 등] 간의 관계 등 회계법인 관련 모든 독립성 검토의 기본 준거 조문입니다. 회계법인이 감사인일 때는 절대 제21조를 쓰지 마세요.)
  2) 감사인이 **개인 공인회계사(예: OO 공인회계사)**인 경우: 반드시 **`"공인회계사법 제21조"`**를 포함하세요. (개인 회계사의 소송사건 관여/대변, 채용면접 참여/추천, 지분 보유 등 개인 감사인 관련 모든 독립성 검토의 기본 준거 조문입니다.)
  3) **외부감사 직무 및 비감사용역 관련 추가 조문**: 외부감사인으로서 비감사용역(가치평가용역, 자문 등) 수행, 경영진 역할 수행(채용면접 관여 등), 소송 대변(소송사건 관여) 등이 관련된 경우 위 1) 또는 2) 조문과 함께 **`"외부감사법 제9조"`**를 추가로 배열에 넣으세요.

### 2. 회계감사 법리 및 판정(`status`) 일관성 기준
시나리오와 관계도에 등장하는 엔티티 명칭과 `rel_type`을 `considerations`와 `key_issues`에 구체적으로 명시하고, 공인회계사 윤리기준의 5대 위협(이기적 위협, 자기검토 위협, 변호 위협, 유착 위협, 압력 위협) 및 경영진 역할 수행 금지 원칙을 적용하여 아래와 같이 일관되게 판정하세요:

1) **`"수임 불가"` (`risk_level: "높음"`)로 판정해야 하는 경우**:
   - **지분 보유 및 합병 승계**: 감사인(또는 피합병 회계법인)이 피감사회사 지분을 보유한 상태에서 합병 등으로 이를 승계하는 경우 (이기적 위협 및 법정 결격).
   - **가치평가용역 수행**: 모회사가 자회사 사업부를 인수할 때 가치평가를 수행하고 감사를 맡는 등 재무제표에 영향을 미치는 평가용역을 수행하는 경우 (자기검토 위협).
   - **소송사건 관여/대변**: 주주 손해배상청구소송 등에서 피감사회사의 입장을 대변하거나 소송에 관여하는 경우 (변호 위협).
   - **채용면접 참여/추천**: 피감사회사의 회계부서 직원 채용면접에 참여하여 후보자를 선발·추천하는 경우 (경영진 역할 수행 및 자기검토/유착 위협).
   - *수임 불가 시 `suggested_safeguards` 작성 규칙*: "내부 지침 강화" 같은 사후 대책이 아니라, **"감사계약 체결 전 보유 지분 전량 처분"**, **"해당 소송사건 대변/채용관여/평가용역의 즉시 중단 또는 당기 외부감사 수임 거절(사임)"** 등 위협을 원천 제거하는 사전 전제조건만 구체적인 주체명과 함께 작성하세요.

2) **`"안전장치 적용 시 수임 가능"` (`risk_level: "중간"` 또는 `"높음"`)으로 판정해야 하는 경우**:
   - **비관여 사원의 형제자매(친형 등)가 피감사회사(비영리법인 포함) CFO/임원인 경우**: `"공인회계사법 제33조"`를 준거 조문으로 검토하되, 감사업무에 관여하지 않는 사원의 형제자매(친형)가 임원인 경우는 법인 전체의 법정 절대적 결격사유에 해당하지 않음을 명시하세요. 다만 윤리기준상 유착 위협이 존재하므로 **"해당 사원의 감사업무팀 및 의사결정 완전 배제와 정보차단벽(Chinese Wall) 설치"**, **"독립적인 심리실 사전 품질관리검토(EQCR) 수행"**을 안전장치로 제시하여 `"안전장치 적용 시 수임 가능"`으로 판정하세요.
   - **감사보수 비중 과다(예: 연매출 대비 30%)**: 특정 고객 감사보수 의존도가 높아 이기적 위협 및 압력 위협이 발생하므로, **"감사보고서 발행 전 독립적인 심리실 품질관리검토(EQCR) 또는 외부 품질관리검토 수행"**, **"차기 이후 보수 의존도 축소 방안 마련"**을 안전장치로 제시하여 `"안전장치 적용 시 수임 가능"`으로 판정하세요.

3) **`"수임 가능"` (`risk_level: "낮음"`)으로 판정해야 하는 경우**:
   - 법정 직무제한이나 윤리기준상 유의미한 위협이 없는 경우 (`suggested_safeguards`는 빈 배열 `[]`).

### 3. 출력 JSON 스키마 (이 구조와 허용값만 출력할 것)
{
  "considerations": "한국어 2~4문장. 적용 법조문(공인회계사법 제21조/제33조, 외부감사법 제9조)과 공인회계사 윤리기준상 구체적 위협(이기적/자기검토/변호/유착/압력 위협, 경영진 역할 수행 등), 그리고 수임 가능 여부에 대한 명확한 법리적 결론을 서술하세요.",
  "key_issues": [
    "관계도의 구체적인 엔티티 이름과 rel_type을 인용하여 법리적·윤리적 쟁점을 상세히 서술한 문장"
  ],
  "vulnerable_connections": [
    {
      "source_id": "관계도에 존재하는 정확한 source_id",
      "target_id": "관계도에 존재하는 정확한 target_id",
      "reason": "이 연결 관계가 독립성 위협을 유발하거나 전달하는 구체적인 이유"
    }
  ],
  "legal_references": [
    {
      "name": "반드시 '공인회계사법 제33조', '공인회계사법 제21조', '외부감사법 제9조' 중 해당하는 정확한 조문명만 기입 (하이픈 '-' 및 부가 설명 절대 금지)"
    }
  ],
  "risk_level": "높음 | 중간 | 낮음 중 택1",
  "status": "수임 불가 | 안전장치 적용 시 수임 가능 | 수임 가능 중 택1",
  "suggested_safeguards": [
    "수임 불가 시 수임 거절/사전 처분 등 원천 해소 조건, 안전장치 적용 시 수임 가능일 때 업무 배제/품질관리검토 등 구체적 안전장치"
  ]
}"""

    ANALYSIS_USER = "Scenario: {scenario}\n\nRelationship Map: {map_json}\n\n위 시나리오와 관계도를 바탕으로 JSON만 출력하세요. legal_references.name에는 하이픈(-)이나 설명 없이 반드시 '공인회계사법 제33조', '공인회계사법 제21조', '외부감사법 제9조'와 같이 정확한 조문명만 넣으세요."

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


def _mermaid_node_text(name: str, label: str) -> str:
    """노드에 보일 문구. 상자 모양은 label로 따로 고르므로 여기서는 글자만 만든다.

    이름 끝이 유형과 같으면 유형 줄을 생략한다. 예: 민국회계법인 + 회계법인.
    유형이 이름에 없으면 이름 아래 한 줄로 둔다. 예: 이언변 + 공인회계사.
    """
    clean_name = re.sub(r"[^가-힣a-zA-Z0-9\s]", "", name or "").strip()
    clean_label = re.sub(r"[^가-힣a-zA-Z0-9\s]", "", label or "").strip()
    if not clean_label:
        return clean_name
    if not clean_name:
        return clean_label
    name_key = re.sub(r"\s+", "", clean_name).casefold()
    label_key = re.sub(r"\s+", "", clean_label).casefold()
    if name_key.endswith(label_key):
        return clean_name
    return f"{clean_name}<br>{clean_label}"


def build_mermaid_graph(
    rel_map: IndependenceMap,
    vulnerable_connections: list[VulnerableConnection] | None = None
) -> str:
    """Mermaid flowchart TD. 직교(linear), 라벨 따옴표, 취약 엔티티만 파스텔 keyNode."""
    lines = [
        "%%{init: {\"flowchart\": {\"curve\": \"linear\"}}}%%",
        "flowchart TD",
    ]
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

    # 중성 파스텔: 취약 핵심만. PwC 레드/dash 사용 금지.
    lines.append("    classDef normalNode fill:#ffffff,stroke:#64748b,stroke-width:1px,color:#111827")
    lines.append("    classDef keyNode fill:#eef2ff,stroke:#64748b,stroke-width:2px,color:#111827")

    for entity in rel_map.entities:
        label = entity.label or ""
        open_s, close_s = shape_map.get(label, ("[", "]"))
        node_text = _mermaid_node_text(entity.name, label)
        node_class = "keyNode" if entity.id in vulnerable_entities else "normalNode"
        lines.append(f'    {entity.id}{open_s}"{node_text}"{close_s}:::{node_class}')

    for conn in rel_map.connections:
        raw_rel = (conn.rel_type or "관계").strip()[:40]
        rel = raw_rel.replace('"', "'").replace("\n", " ")
        is_vulnerable = (conn.source_id, conn.target_id) in vulnerable_set
        if is_vulnerable:
            lines.append(f'    {conn.source_id} -. "[!] {rel}" .-> {conn.target_id}')
        else:
            lines.append(f'    {conn.source_id} -->|"{rel}"| {conn.target_id}')

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
