# 생성형 AI 전문가 관점 플로우 검토

**작성일**: 2026-02-12  
**검토자**: 생성형 AI 전문가 관점  
**목적**: 의도된 플로우 vs 현재 구현 비교 및 개선 방안 제시

---

## 📋 의도된 플로우

```
Step1: 사용자 입력 후 Neo4j 조회
  ├─ trace_id 없는 경우 → Step2로 이동
  └─ trace_id 있는 경우 → Step3로 이동

Step2: LLM 통해 [엔티티-관계] 추출 후 Neo4j 저장

Step3: 독립성 여부 판단을 위한 LLM 검색 시
  ├─ [엔티티-관계]를 context로 활용
  └─ [감사 독립성 및 수임 가능 여부 관련 법령 조회]를 context로 활용

Step4: [엔티티-관계]와 Step3 답변 활용하여
  └─ Mermaid 통해 관계도 및 이슈 지점 시각화
```

---

## 🔍 현재 구현 상태 분석

### Step1: Neo4j 조회

**의도**: 사용자 입력 후 trace_id 기반 Neo4j 조회

**현재 구현**: ❌ **미구현**
- Neo4j 조회 로직 없음
- trace_id 기반 조회 함수 없음
- 항상 Step2로 이동 (추출 수행)

**코드 위치**: `backend/routers/chat.py`
```python
# 현재: 항상 추출 수행
rel_map = await extract_relationships(scenario_text)
```

---

### Step2: 엔티티-관계 추출 및 저장

**의도**: LLM으로 엔티티-관계 추출 후 Neo4j 저장

**현재 구현**: ✅ **부분 구현**
- 엔티티-관계 추출: ✅ 구현됨 (`extract_relationships`)
- Neo4j 저장: ✅ 구현됨 (`save_independence_map_to_neo4j`)

**문제점**:
- Step1에서 Neo4j 조회 없이 항상 추출 수행
- 중복 추출 가능성 (같은 시나리오에 대해)

---

### Step3: 독립성 판단 LLM 호출

**의도**: 
- [엔티티-관계]를 context로 활용 ✅
- [법령 조회]를 context로 활용 ❌

**현재 구현**: ⚠️ **부분 구현**

**엔티티-관계 활용**: ✅
```python
context = f"""다음은 입력된 시나리오에서 추출한 엔티티-관계 정보입니다:
{rel_map_json}
이 정보를 참고하여 답변해주세요..."""
```

**법령 조회 활용**: ❌ **미구현**
- 법령 정보가 context에 포함되지 않음
- 법령은 분석 **후** URL 보강만 수행 (`_enrich_legal_ref_urls`)
- LLM 호출 **전**에 법령 정보를 context로 제공하지 않음

**현재 법령 처리**:
```python
# independence_service.py
# 법령은 분석 결과에 포함되지만, LLM 호출 전 context로 활용 안 함
analysis = await analyze_independence(scenario, rel_map)  # 법령 정보 없이 호출
analysis = _enrich_legal_ref_urls(analysis)  # 분석 후 URL만 보강
```

---

### Step4: Mermaid 시각화

**의도**: 엔티티-관계와 Step3 답변 활용하여 Mermaid 생성

**현재 구현**: ❌ **미구현**
- `/chat` 엔드포인트에서 Mermaid 생성 없음
- `build_mermaid_graph` 함수는 있지만 `/chat`에서 호출 안 함
- 응답에 mermaid_code 포함 안 함

**코드 위치**: `backend/services/independence_service.py`
```python
# build_mermaid_graph 함수는 존재하지만
# /chat 엔드포인트에서 호출되지 않음
```

---

## 📊 비교 분석

| Step | 의도 | 현재 구현 | 일치 여부 |
|------|------|-----------|----------|
| **Step1** | Neo4j 조회 (trace_id 기반) | ❌ 미구현 | ❌ |
| **Step2** | 엔티티-관계 추출 + 저장 | ✅ 부분 구현 | ⚠️ |
| **Step3** | 엔티티-관계 + 법령을 context로 활용 | ⚠️ 부분 구현 (법령 없음) | ⚠️ |
| **Step4** | Mermaid 시각화 | ❌ 미구현 | ❌ |

---

## ⚠️ 발견된 문제점

### 문제 1: Neo4j 조회 로직 부재

**현재**: 항상 엔티티-관계 추출 수행
**의도**: trace_id 기반 Neo4j 조회 후 재사용

**영향**:
- 중복 추출로 인한 비용 증가
- 동일 시나리오에 대한 일관성 부족
- 성능 저하

### 문제 2: 법령 정보가 Context에 포함되지 않음

**현재**: 법령은 분석 후 URL 보강만 수행
**의도**: LLM 호출 전에 법령 정보를 context로 제공

**영향**:
- LLM이 법령 정보를 참고하지 못함
- 법령 기반 판단 정확도 저하 가능
- 법령 조회가 "사후 처리"로만 작동

### 문제 3: Mermaid 시각화 미포함

**현재**: `/chat` 응답에 mermaid_code 없음
**의도**: 관계도 및 이슈 지점 시각화 포함

**영향**:
- 시각적 표현 부족
- 사용자 경험 저하

---

## 💡 개선 방안

### 방안 A: 의도된 플로우 완전 구현 (권장)

#### Step1: Neo4j 조회 함수 추가

```python
def get_rel_map_from_neo4j(trace_id: str) -> IndependenceMap | None:
    """trace_id로 Neo4j에서 엔티티-관계 조회."""
    from backend.database import get_neo4j_session
    
    with get_neo4j_session() as session:
        # 엔티티 조회
        entity_result = session.run(
            """
            MATCH (n:IndependenceEntity {trace_id: $trace_id})
            RETURN n.id AS id, n.label AS label, n.name AS name
            """,
            trace_id=trace_id
        )
        entities = [dict(r) for r in entity_result]
        
        if not entities:
            return None
        
        # 관계 조회
        conn_result = session.run(
            """
            MATCH (a:IndependenceEntity {trace_id: $trace_id})-[r:RELATION]->(b:IndependenceEntity {trace_id: $trace_id})
            RETURN a.id AS source_id, b.id AS target_id, r.rel_type AS rel_type
            """,
            trace_id=trace_id
        )
        connections = [dict(r) for r in conn_result]
        
        return IndependenceMap(entities=entities, connections=connections)
```

#### Step2: 법령 정보를 Context에 포함

```python
def get_relevant_laws_for_context() -> str:
    """감사 독립성 관련 주요 법령 정보를 context로 제공."""
    # 법령검색목록.csv에서 관련 법령 조회
    # 또는 주요 법령 하드코딩
    laws = [
        "공인회계사법 제21조 (감사인의 독립성)",
        "공인회계사 윤리기준",
        "회계감사기준",
        # ...
    ]
    return "\n".join([f"- {law}" for law in laws])
```

#### Step3: `/chat` 엔드포인트 수정

```python
@router.post("/completions")
async def chat_completion(request: ChatRequest):
    scenario_text = user_messages[-1].content.strip()
    trace_id = hashlib.md5(scenario_text.encode()).hexdigest()[:8].upper()
    
    # Step1: Neo4j 조회
    rel_map = get_rel_map_from_neo4j(trace_id)
    
    # Step2: 없으면 추출 및 저장
    if not rel_map:
        rel_map = await extract_relationships(scenario_text)
        save_independence_map_to_neo4j(trace_id, rel_map)
    
    # Step3: 법령 정보 조회
    laws_context = get_relevant_laws_for_context()
    
    # Context 구성
    context = f"""엔티티-관계 정보:
{rel_map.model_dump_json(indent=2)}

관련 법령:
{laws_context}

이 정보를 참고하여 독립성 여부를 판단해주세요."""
    
    # LLM 호출
    reply = get_llm_response(messages=[..., context])
    
    # Step4: Mermaid 생성
    # 분석 결과에서 vulnerable_connections 추출 필요
    # (현재는 구조화된 분석 없이 일반 채팅이므로, 
    #  분석 단계 추가 필요 또는 응답에서 추출)
    mermaid_code = build_mermaid_graph(rel_map, vulnerable_connections=None)
    
    return {
        "message": ChatMessage(role="assistant", content=reply),
        "mermaid_code": mermaid_code,
        "rel_map": rel_map.model_dump()
    }
```

---

### 방안 B: 하이브리드 접근 (구조화된 분석 포함)

**접근**: `/chat`에서 구조화된 분석도 수행

```python
# Step3: 구조화된 분석 수행
analysis = await analyze_independence(scenario_text, rel_map)

# 법령 정보를 context로 활용 (분석 전)
laws_context = get_relevant_laws_for_context()
enhanced_context = f"{context}\n\n관련 법령:\n{laws_context}"

# 일반 채팅 + 구조화된 분석 결과 활용
reply = get_llm_response(messages=[..., enhanced_context])

# Step4: Mermaid 생성 (vulnerable_connections 포함)
mermaid_code = build_mermaid_graph(rel_map, analysis.vulnerable_connections)
```

**장점**:
- 구조화된 분석 결과 활용
- vulnerable_connections로 정확한 시각화
- 법령 기반 판단 가능

**단점**:
- 비용 증가 (추출 + 분석)
- 응답 시간 증가

---

## 🎯 권장 방안

### 즉시 구현 권장: 방안 A (의도된 플로우 완전 구현)

**이유**:
1. 의도된 플로우와 일치
2. Neo4j 재사용으로 비용 절감
3. 법령 정보를 context로 활용하여 정확도 향상
4. Mermaid 시각화로 사용자 경험 개선

### 추가 고려: 방안 B (구조화된 분석 포함)

**이유**:
1. vulnerable_connections로 정확한 이슈 지점 표시
2. 더 정확한 독립성 판단
3. 구조화된 응답 제공

---

## 📝 구현 체크리스트

### 필수 구현 항목

- [ ] **Step1**: Neo4j 조회 함수 구현 (`get_rel_map_from_neo4j`)
- [ ] **Step1**: trace_id 기반 분기 로직 추가
- [ ] **Step3**: 법령 정보 조회 함수 구현 (`get_relevant_laws_for_context`)
- [ ] **Step3**: 법령 정보를 context에 포함
- [ ] **Step4**: Mermaid 생성 및 응답에 포함

### 선택 구현 항목

- [ ] 구조화된 분석 통합 (방안 B)
- [ ] vulnerable_connections 추출 및 활용
- [ ] 법령 정보 캐싱

---

## ✅ 결론

### 현재 구현 상태

| 항목 | 상태 |
|------|------|
| **의도된 플로우 구현** | ⚠️ 부분 구현 (약 40%) |
| **Neo4j 조회** | ❌ 미구현 |
| **법령 Context 활용** | ❌ 미구현 |
| **Mermaid 시각화** | ❌ 미구현 |

### 개선 필요사항

1. **Neo4j 조회 로직 추가** (최우선)
2. **법령 정보를 Context에 포함** (중요)
3. **Mermaid 생성 및 응답 포함** (중요)
4. **구조화된 분석 통합** (선택)

---

**검토 완료일**: 2026-02-12  
**상태**: ⚠️ 의도된 플로우와 현재 구현 불일치 (개선 필요)
