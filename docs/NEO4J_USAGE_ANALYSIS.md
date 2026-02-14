# Neo4j 활용 방식 분석

**작성일**: 2026-02-12  
**목적**: Neo4j의 현재 사용 방식 및 잠재적 활용 방안 분석

---

## 📊 현재 Neo4j 활용 상태

### 1. 저장 (Write) - `/independence` 파이프라인

**위치**: `backend/services/independence_service.py`

```python
def save_independence_map_to_neo4j(trace_id: str, rel_map: IndependenceMap) -> None:
    """독립성 검토 결과(엔티티·관계)를 Neo4j에 저장. 실행(trace_id)별로 서브그래프 분리."""
```

**저장 내용**:
- **노드**: `IndependenceEntity` (trace_id, id, label, name)
- **엣지**: `RELATION` (rel_type)
- **구조**: `trace_id`별로 서브그래프 분리

**저장 시점**:
- `/independence/review` (일괄 호출)
- `/independence/report` (3단계 보고서 생성)

**호출 흐름**:
```
run_independence_review() 
  → build_independence_report() 
    → save_independence_map_to_neo4j() (save_to_neo4j=True일 때)
```

---

### 2. 조회 (Read) - `/graph` 엔드포인트

**위치**: `backend/routers/graph.py`

```python
@router.get("/mermaid")
def get_graph_as_mermaid():
    """Neo4j 그래프를 Mermaid 형식으로 반환."""
```

**조회 내용**:
- 전체 그래프 조회 (`MATCH (n)-[r]->(m)`)
- LIMIT 50
- Mermaid 형식으로 변환

**사용 위치**:
- Streamlit UI에서 그래프 시각화
- 독립성 검토와는 별개의 기능

---

## 🔍 현재 활용 방식의 특징

### 장점

1. **데이터 영속성**: 독립성 검토 결과가 Neo4j에 저장되어 재사용 가능
2. **그래프 시각화**: `/graph/mermaid`로 전체 그래프 조회 가능
3. **trace_id 분리**: 각 검토 실행별로 서브그래프 분리

### 제한사항

1. **`/chat`에서 미활용**: Neo4j에 저장된 엔티티-관계 정보가 `/chat`의 context로 활용되지 않음
2. **전체 그래프 조회**: 특정 시나리오나 trace_id 기반 조회 없음
3. **Context 재사용 없음**: 저장된 데이터를 LLM context로 활용하지 않음

---

## 💡 잠재적 활용 방안

### 옵션 1: `/chat`에서 Neo4j 조회하여 Context 활용

**접근**: 사용자 입력 시나리오와 유사한 기존 검토 결과를 Neo4j에서 조회

```python
@router.post("/completions")
async def chat_completion(request: ChatRequest):
    # 1. Neo4j에서 유사한 시나리오의 엔티티-관계 조회
    similar_rel_map = await find_similar_scenario_in_neo4j(request.messages[-1].content)
    
    # 2. Context 구성
    if similar_rel_map:
        context = f"유사한 시나리오의 엔티티-관계 정보: {similar_rel_map}"
        # ... context를 프롬프트에 포함
```

**장점**:
- 기존 데이터 재사용
- 비용 절감 (중복 추출 방지)
- 일관성 유지

**단점**:
- 유사도 검색 로직 필요
- 시나리오 매칭 복잡도

### 옵션 2: 세션 기반 Neo4j 조회

**접근**: 같은 세션에서 이전에 저장한 결과를 조회

```python
@router.post("/completions")
async def chat_completion(request: ChatRequest, session_id: str):
    # 1. 세션의 최근 trace_id로 Neo4j 조회
    rel_map = await get_rel_map_by_trace_id(session_id)
    
    # 2. Context 활용
    if rel_map:
        context = f"이전 검토 결과: {rel_map}"
        # ...
```

**장점**:
- 세션별 컨텍스트 유지
- 구현 간단

**단점**:
- 세션 관리 필요
- 첫 요청 시 데이터 없음

### 옵션 3: Neo4j를 Context Store로 활용

**접근**: Neo4j를 엔티티-관계 정보의 중앙 저장소로 활용

```python
# 1. 시나리오 입력 시 Neo4j에서 조회
rel_map = await get_or_extract_rel_map(scenario_text)

# 2. Context로 활용
context = build_context_from_neo4j(rel_map)

# 3. LLM 호출
reply = get_llm_response(messages=[..., context])
```

**장점**:
- 중앙 집중식 데이터 관리
- 재사용성 극대화
- 확장성 우수

**단점**:
- Neo4j 의존성 증가
- 복잡도 증가

---

## 📋 현재 상태 요약

| 항목 | 상태 | 비고 |
|------|------|------|
| **저장** | ✅ 구현됨 | `/independence` 파이프라인에서 저장 |
| **조회** | ✅ 구현됨 | `/graph/mermaid`에서 전체 그래프 조회 |
| **Context 활용** | ❌ 미구현 | `/chat`에서 Neo4j 데이터 활용 안 함 |
| **세션 연동** | ❌ 미구현 | 세션별 데이터 조회 없음 |
| **유사도 검색** | ❌ 미구현 | 유사 시나리오 검색 없음 |

---

## 🎯 권장사항

### 즉시 활용 가능: 옵션 2 (세션 기반)

**이유**:
1. 구현 간단
2. 기존 Neo4j 인프라 활용
3. 사용자 의도(엔티티-관계를 context로 활용) 구현

### 향후 개선: 옵션 3 (Context Store)

**이유**:
1. 확장성 우수
2. 데이터 재사용 극대화
3. 비용 절감

---

## ✅ 결론

**현재 상태**:
- Neo4j는 **저장소**로만 활용됨
- `/chat`에서 Neo4j 데이터를 **context로 활용하지 않음**
- `/graph`는 **시각화 전용**으로 사용됨

**잠재력**:
- Neo4j에 저장된 엔티티-관계 정보를 `/chat`의 context로 활용 가능
- 세션 기반 또는 유사도 기반 조회로 구현 가능
- 사용자 의도(엔티티-관계를 context로 활용) 구현 가능

---

**검토 완료일**: 2026-02-12  
**상태**: ⚠️ Neo4j 활용 잠재력 있음 (현재는 저장/조회만, context 활용 없음)
