# Neo4j ERExtractionTemplate vs EntityRelationExtractor 비교 분석

**작성일**: 2026-02-12  
**검토자**: 지식그래프 및 AI 전문가 관점  
**목적**: Neo4j의 `ERExtractionTemplate()`과 `EntityRelationExtractor` 비교 분석 및 현재 서비스에 더 적합한 방식 제안

---

## 📋 비교 대상

### 1. ERExtractionTemplate
- **타입**: 프롬프트 템플릿 클래스 (`neo4j_graphrag.generation.prompts`)
- **역할**: LLM에 전달할 프롬프트를 생성하는 템플릿
- **위치**: `neo4j_graphrag` Python 라이브러리

### 2. EntityRelationExtractor
- **타입**: 실제 추출 컴포넌트 (Neo4j LLM Knowledge Graph Builder)
- **역할**: 텍스트에서 엔티티와 관계를 추출하는 실행 컴포넌트
- **위치**: Neo4j LLM Knowledge Graph Builder 애플리케이션 (`llm-graph-transformer`)

---

## 🔍 상세 비교 분석

### A. ERExtractionTemplate 분석

#### 1. 구조 및 사용법

```python
from neo4j_graphrag.generation.prompts import ERExtractionTemplate

prompt_template = ERExtractionTemplate()
prompt = prompt_template.format(
    schema='',           # 노드/관계 타입 스키마 정의
    text='...',          # 추출할 텍스트
    examples=''          # Few-shot 예시 (선택적)
)
```

#### 2. 프롬프트 내용

```
You are a top-tier algorithm designed for extracting
information in structured formats to build a knowledge graph.

Extract the entities (nodes) and specify their type from the following text.
Also extract the relationships between these nodes.

Return result as JSON using the following format:
{"nodes": [ {"id": "0", "label": "Person", "properties": {"name": "John"}} ],
"relationships": [{"type": "KNOWS", "start_node_id": "0", "end_node_id": "1", 
"properties": {"since": "2024-08-01"}} ] }

Use only the following nodes and relationships (if provided):
{schema}

Assign a unique ID (string) to each node, and reuse it to define relationships.
Do respect the source and target node types for relationship and
the relationship direction.

Do not return any additional information other than the JSON in it.

Examples:
{examples}

Input text:

{text}
```

#### 3. 출력 형식

```json
{
  "nodes": [
    {
      "id": "0",
      "label": "Person",
      "properties": {"name": "John"}
    }
  ],
  "relationships": [
    {
      "type": "KNOWS",
      "start_node_id": "0",
      "end_node_id": "1",
      "properties": {"since": "2024-08-01"}
    }
  ]
}
```

#### 4. 특징

**장점**:
- ✅ **유연한 스키마 정의**: `schema` 파라미터로 노드/관계 타입 제한 가능
- ✅ **Few-shot 학습 지원**: `examples` 파라미터로 예시 제공 가능
- ✅ **표준화된 출력 형식**: Neo4j GraphRAG 표준 형식 준수
- ✅ **관계 속성 지원**: 관계에 `properties` 추가 가능 (예: `since`, `since_date`)
- ✅ **방향성 명시**: `start_node_id`, `end_node_id`로 관계 방향 명확히 표현

**단점**:
- ⚠️ **프롬프트만 제공**: 실제 추출 로직은 별도 구현 필요
- ⚠️ **LLM 호출 직접 관리**: 템플릿 생성 후 LLM API 호출은 개발자가 직접 처리
- ⚠️ **에러 핸들링 없음**: JSON 파싱, 검증 로직 별도 구현 필요

---

### B. EntityRelationExtractor 분석

#### 1. 구조 및 사용법

**Neo4j LLM Knowledge Graph Builder**는 완전한 애플리케이션으로 제공:
- 온라인 서비스 (Neo4j Labs)
- 로컬 배포 가능 (Docker Compose)
- FastAPI 백엔드 + LangChain 통합

#### 2. 구현 방식

- **모듈**: `llm-graph-transformer` (LangChain 통합)
- **프로세스**:
  1. 문서 업로드 → Document 노드 생성
  2. 텍스트 청킹 (LangChain loaders)
  3. 임베딩 계산 및 저장
  4. `llm-graph-transformer` 또는 `diffbot-graph-transformer`로 추출
  5. 엔티티/관계를 그래프에 저장

#### 3. 지원 LLM 모델

- OpenAI (GPT-3.5, GPT-4o)
- VertexAI (Gemini 1.0, 1.5)
- Diffbot
- Anthropic (Claude)
- AWS Bedrock
- OpenAI API 호환 모델 (Ollama, Groq, Fireworks)
- Qwen

#### 4. 특징

**장점**:
- ✅ **완전한 파이프라인**: 문서 업로드부터 그래프 저장까지 자동화
- ✅ **다양한 LLM 지원**: 여러 LLM 프로바이더 통합
- ✅ **LangChain 통합**: 표준화된 추출 파이프라인
- ✅ **스키마 정의 UI**: 웹 UI로 노드/관계 타입 정의 가능
- ✅ **에러 핸들링 내장**: 파이프라인 레벨에서 처리
- ✅ **Neo4j 직접 저장**: 추출 결과를 자동으로 Neo4j에 저장

**단점**:
- ⚠️ **무거운 의존성**: 전체 애플리케이션 배포 필요
- ⚠️ **커스터마이징 제한**: 내부 구현 수정 어려움
- ⚠️ **현재 서비스와 형식 불일치**: 출력 형식이 현재 `IndependenceMap`와 다름
- ⚠️ **추가 인프라 필요**: 별도 서비스 운영 필요

---

### C. 현재 서비스의 추출 방식

#### 1. 현재 구현

**파일**: `backend/services/independence_service.py`

```python
class _PromptTemplates:
    EXTRACTION_SYSTEM = """You are an expert at extracting structured relationships from Korean audit scenarios.
Output only valid JSON with this exact structure (no markdown, no explanation):
{"entities": [{"id": "string (alphanumeric)", "label": "string", "name": "string"}], 
"connections": [{"source_id": "string", "target_id": "string", "rel_type": "string"}]}
Use Korean for "label" and "rel_type" when the scenario is in Korean 
(e.g. rel_type: 소속, 감사대상, 직계가족, 대표이사)."""

async def extract_relationships(scenario_text: str) -> IndependenceMap:
    return await chat_completion_structured(
        client,
        model=settings.independence_extraction_model,  # GPT-4o-mini
        messages=[
            {"role": "system", "content": _PromptTemplates.EXTRACTION_SYSTEM},
            {"role": "user", "content": scenario_text},
        ],
        response_model=IndependenceMap,  # Pydantic 모델로 검증
    )
```

#### 2. 출력 형식

```python
class IndependenceMap(BaseModel):
    entities: list[Entity]  # {"id", "label", "name"}
    connections: list[Connection]  # {"source_id", "target_id", "rel_type"}
```

#### 3. 특징

**장점**:
- ✅ **도메인 특화**: 감사 독립성 시나리오에 최적화
- ✅ **한국어 지원**: 한국어 레이블/관계 타입 명시적 처리
- ✅ **Pydantic 검증**: 타입 안전성 및 자동 검증
- ✅ **경량 구현**: 단순한 LLM 호출만 필요
- ✅ **현재 아키텍처와 통합**: 기존 코드와 완벽 호환

**단점**:
- ⚠️ **스키마 제한 없음**: 노드/관계 타입 제한 불가
- ⚠️ **Few-shot 예시 없음**: 예시 기반 학습 미지원
- ⚠️ **관계 속성 없음**: 관계에 추가 속성 저장 불가

---

## 📊 비교표

| 항목 | ERExtractionTemplate | EntityRelationExtractor | 현재 서비스 |
|------|---------------------|------------------------|------------|
| **타입** | 프롬프트 템플릿 | 완전한 추출 파이프라인 | 커스텀 프롬프트 + LLM 호출 |
| **스키마 제한** | ✅ 지원 (`schema` 파라미터) | ✅ 지원 (UI/설정) | ❌ 미지원 |
| **Few-shot 예시** | ✅ 지원 (`examples` 파라미터) | ⚠️ 제한적 | ❌ 미지원 |
| **관계 속성** | ✅ 지원 (`properties`) | ✅ 지원 | ❌ 미지원 |
| **한국어 특화** | ❌ 일반적 | ❌ 일반적 | ✅ 명시적 지원 |
| **도메인 특화** | ❌ 범용 | ❌ 범용 | ✅ 감사 독립성 특화 |
| **Pydantic 검증** | ❌ 별도 구현 필요 | ❌ 별도 구현 필요 | ✅ 내장 |
| **에러 핸들링** | ❌ 별도 구현 필요 | ✅ 내장 | ✅ `chat_completion_structured` |
| **Neo4j 통합** | ❌ 별도 구현 필요 | ✅ 자동 저장 | ✅ `save_independence_map_to_neo4j` |
| **의존성** | 낮음 (`neo4j_graphrag`) | 높음 (전체 애플리케이션) | 낮음 (OpenAI만) |
| **커스터마이징** | ✅ 높음 (프롬프트 수정 가능) | ⚠️ 낮음 (내부 구현) | ✅ 높음 (완전 제어) |
| **출력 형식** | `nodes`/`relationships` | `nodes`/`relationships` | `entities`/`connections` |

---

## 🎯 현재 서비스에 더 적합한 방식 분석

### 1. ERExtractionTemplate의 장점 활용 방안

**ERExtractionTemplate의 핵심 장점**:
1. **스키마 제한**: 노드/관계 타입을 명시적으로 제한 가능
2. **Few-shot 예시**: 예시를 통한 추출 품질 향상
3. **관계 속성**: 관계에 추가 메타데이터 저장 가능

**현재 서비스에 적용 가능한 개선**:

#### 방안 1: ERExtractionTemplate 프롬프트 구조 차용

```python
class _PromptTemplates:
    EXTRACTION_SYSTEM = """You are an expert at extracting structured relationships from Korean audit scenarios.

Extract the entities (nodes) and specify their type from the following text.
Also extract the relationships between these nodes.

Return result as JSON using the following format:
{"entities": [{"id": "string", "label": "string", "name": "string"}], 
"connections": [{"source_id": "string", "target_id": "string", "rel_type": "string"}]}

Use only the following node labels (if provided):
{schema}

Examples:
{examples}

Input text:

{text}"""
```

**개선점**:
- ✅ 스키마 제한 추가 가능
- ✅ Few-shot 예시 지원 가능
- ✅ 현재 출력 형식 유지 (`entities`/`connections`)

#### 방안 2: 관계 속성 지원 추가

```python
class Connection(BaseModel):
    source_id: str
    target_id: str
    rel_type: str
    properties: dict[str, Any] | None = None  # 추가: 관계 속성
```

**활용 예시**:
- `소속` 관계에 `since: "2024-01-01"` 속성 추가
- `감사대상` 관계에 `period: "2023"` 속성 추가

---

### 2. EntityRelationExtractor의 장점 활용 방안

**EntityRelationExtractor의 핵심 장점**:
1. **완전한 파이프라인**: 문서 → 청킹 → 추출 → 저장 자동화
2. **다양한 LLM 지원**: 여러 프로바이더 통합

**현재 서비스에 적용 가능성**:
- ⚠️ **낮음**: 현재 서비스는 단순한 시나리오 텍스트 입력만 필요
- ⚠️ **과도한 복잡성**: 문서 업로드, 청킹 등 불필요한 기능
- ⚠️ **형식 불일치**: 출력 형식 변환 필요

**결론**: EntityRelationExtractor는 현재 서비스에 **과도한 복잡성**을 추가하며, 핵심 가치가 낮음.

---

## 💡 최종 권장사항

### ✅ 권장: ERExtractionTemplate의 프롬프트 구조 차용

**이유**:
1. **스키마 제한**: 감사 독립성 도메인의 노드/관계 타입을 명시적으로 제한 가능
   - 예: `회계법인`, `공인회계사`, `피감사회사` 등만 허용
   - 잘못된 추출 방지 (예: `Person` 대신 `공인회계사` 사용)

2. **Few-shot 예시**: 고품질 추출 예시 제공으로 정확도 향상
   - 예: "김 회계사는 A회계법인에 소속되어 있다" → `소속` 관계 추출

3. **관계 속성**: 관계에 추가 메타데이터 저장 가능
   - 예: `소속` 관계에 `since`, `position` 속성 추가

4. **현재 아키텍처 유지**: 기존 코드 구조와 완벽 호환
   - 출력 형식은 `entities`/`connections` 유지
   - Pydantic 검증 유지

### ❌ 비권장: EntityRelationExtractor 도입

**이유**:
1. **과도한 복잡성**: 문서 업로드, 청킹 등 불필요한 기능
2. **형식 불일치**: 출력 형식 변환 필요 (`nodes`/`relationships` → `entities`/`connections`)
3. **추가 인프라**: 별도 서비스 운영 필요
4. **한국어/도메인 특화 부족**: 현재 프롬프트의 한국어 특화 장점 상실

---

## 🔧 구체적 구현 제안

### Phase 1: 스키마 제한 추가

```python
class _PromptTemplates:
    # 감사 독립성 도메인 스키마 정의
    AUDIT_SCHEMA = """
    Node labels: 회계법인, 공인회계사, 감사인, 피감사회사, 감사대상회사, 
                 회사, 인물, 배우자, 직계가족, 가족, 임원, 이사, 대표이사, 재무이사
    
    Relationship types: 소속, 감사대상, 직계가족, 배우자, 대표이사, 재무이사, 
                        이사, 임원, 지배, 투자, 자문, 거래
    """
    
    EXTRACTION_SYSTEM = f"""You are an expert at extracting structured relationships from Korean audit scenarios.

Extract the entities (nodes) and specify their type from the following text.
Also extract the relationships between these nodes.

Return result as JSON using the following format:
{{"entities": [{{"id": "string", "label": "string", "name": "string"}}], 
"connections": [{{"source_id": "string", "target_id": "string", "rel_type": "string"}}]}}

Use only the following node labels and relationship types:
{_PromptTemplates.AUDIT_SCHEMA}

Use Korean for "label" and "rel_type" when the scenario is in Korean 
(e.g. rel_type: 소속, 감사대상, 직계가족, 대표이사).

Assign a unique ID (string) to each node, and reuse it to define relationships.
Do not return any additional information other than the JSON."""
```

### Phase 2: Few-shot 예시 추가

```python
class _PromptTemplates:
    EXTRACTION_EXAMPLES = """
    Example 1:
    Input: "김 회계사는 A회계법인에 소속되어 있으며, B㈜의 감사를 담당하고 있다."
    Output: {
      "entities": [
        {"id": "e1", "label": "공인회계사", "name": "김 회계사"},
        {"id": "e2", "label": "회계법인", "name": "A회계법인"},
        {"id": "e3", "label": "피감사회사", "name": "B㈜"}
      ],
      "connections": [
        {"source_id": "e1", "target_id": "e2", "rel_type": "소속"},
        {"source_id": "e1", "target_id": "e3", "rel_type": "감사대상"}
      ]
    }
    """
    
    EXTRACTION_SYSTEM = f"""...
    
Examples:
{_PromptTemplates.EXTRACTION_EXAMPLES}

Input text:

{{text}}"""
```

### Phase 3: 관계 속성 지원 (선택적)

```python
class Connection(BaseModel):
    source_id: str
    target_id: str
    rel_type: str
    properties: dict[str, Any] | None = None  # 추가
```

---

## 📝 결론

### ERExtractionTemplate vs EntityRelationExtractor

| 비교 항목 | 승자 |
|----------|------|
| **현재 서비스 적합성** | ✅ **ERExtractionTemplate** |
| **구현 복잡도** | ✅ **ERExtractionTemplate** (낮음) |
| **커스터마이징** | ✅ **ERExtractionTemplate** (높음) |
| **도메인 특화** | ✅ **현재 서비스** (이미 최적화됨) |
| **파이프라인 완성도** | ✅ **EntityRelationExtractor** (높지만 불필요) |

### 최종 권장사항

1. **ERExtractionTemplate의 프롬프트 구조를 차용**하여 현재 프롬프트 개선
   - 스키마 제한 추가
   - Few-shot 예시 추가
   - 관계 속성 지원 (선택적)

2. **EntityRelationExtractor는 도입하지 않음**
   - 과도한 복잡성
   - 현재 서비스 요구사항과 불일치

3. **현재 아키텍처 유지**
   - Pydantic 검증 유지
   - 출력 형식 유지 (`entities`/`connections`)
   - 한국어 특화 유지

---

**다음 단계**: Phase 1 (스키마 제한 추가)부터 구현을 시작할까요?
