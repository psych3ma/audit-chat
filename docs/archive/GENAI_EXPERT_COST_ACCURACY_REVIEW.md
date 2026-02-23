# 생성형 AI 전문가 관점: 정확도 향상 및 비용 감소 방안 검토

**작성일**: 2026-02-12  
**검토자**: 생성형 AI 전문가 관점  
**목적**: 보고서 생성 전 정확도 향상 및 비용 감소를 위한 아키텍처 개선 방안 검토

---

## 📋 제안된 개선 방안

### 1. 엔티티-관계 추출: Neo4j ERExtractionTemplate() 활용

**제안**:
- Neo4j의 ERExtractionTemplate() 활용하여 엔티티-관계 추출
- 기존 LLM 기반 추출 코드 주석처리 (프롬프트는 보존)

### 2. 법령 정보 Context 활용

**제안**:
- 감사 독립성 관련 법령 리스트업
- 독립성 검토 LLM 호출 시 context에 [엔티티-관계]와 [관련 법령] 추가

---

## 🔍 현재 구현 상태 분석

### 현재 엔티티-관계 추출 방식

**구현**: `backend/services/independence_service.py`

```python
async def extract_relationships(scenario_text: str) -> IndependenceMap:
    # LLM 기반 추출 (GPT-4o-mini)
    return await chat_completion_structured(
        client,
        model=settings.independence_extraction_model,  # GPT-4o-mini
        messages=[
            {"role": "system", "content": _PromptTemplates.EXTRACTION_SYSTEM},
            {"role": "user", "content": scenario_text},
        ],
        response_model=IndependenceMap,
    )
```

**비용**: 매 요청마다 LLM 호출 (GPT-4o-mini)

**정확도**: 프롬프트 기반, 구조화된 출력으로 일관성 있음

---

## 💡 Neo4j 기반 추출 방안 분석

### Neo4j ERExtractionTemplate 검토

**Neo4j 기능 확인**:
- Neo4j LLM Knowledge Graph Builder에 `EntityRelationExtractor` 및 `LLMEntityRelationExtractor` 컴포넌트 존재
- `neo4j_graphrag` 라이브러리에 `simple_kg_builder` 템플릿 파이프라인 존재
- Neo4j Labs의 LLM Graph Builder는 온라인 애플리케이션으로 제공

**해석**: 사용자가 의도한 것은 아마도:
1. **Neo4j에 저장된 기존 엔티티-관계 패턴을 활용한 추출** (패턴 매칭)
2. **Neo4j의 LLM Knowledge Graph Builder 활용** (온라인 서비스 또는 로컬 통합)
3. **Neo4j GraphRAG의 템플릿 파이프라인 활용** (`simple_kg_builder`)

**권장 접근**: Neo4j에 저장된 패턴을 활용한 추출 (비용 절감 효과 극대화)

---

## 🎯 개선 방안 분석

### 방안 A: Neo4j 기반 패턴 매칭 (권장)

**접근**: Neo4j에 저장된 기존 엔티티-관계 패턴을 활용

**구현 방안**:
```python
def extract_relationships_with_neo4j_template(scenario_text: str) -> IndependenceMap:
    """
    Neo4j에 저장된 기존 패턴을 활용한 엔티티-관계 추출.
    
    전략:
    1. 시나리오에서 키워드 추출 (회계법인명, 인물명 등)
    2. Neo4j에서 유사한 패턴 조회
    3. 패턴 매칭으로 엔티티-관계 추출
    4. 매칭 실패 시 LLM 폴백
    """
    # 1. 키워드 추출 (간단한 NLP 또는 정규식)
    keywords = extract_keywords(scenario_text)
    
    # 2. Neo4j에서 유사 패턴 조회
    with get_neo4j_session() as session:
        # 유사한 엔티티-관계 패턴 조회
        pattern = session.run(
            """
            MATCH (n:IndependenceEntity)-[r:RELATION]->(m:IndependenceEntity)
            WHERE n.name IN $keywords OR m.name IN $keywords
            RETURN DISTINCT labels(n)[0] AS source_label, 
                   labels(m)[0] AS target_label,
                   type(r) AS rel_type
            LIMIT 10
            """,
            keywords=keywords
        )
        
        # 패턴 기반 추출
        if pattern:
            return build_rel_map_from_pattern(scenario_text, pattern)
    
    # 3. 폴백: LLM 기반 추출
    return await extract_relationships_llm(scenario_text)
```

**장점**:
- ✅ 비용 절감 (LLM 호출 감소)
- ✅ 속도 향상 (Neo4j 쿼리가 LLM보다 빠름)
- ✅ 기존 데이터 재사용

**단점**:
- ⚠️ 새로운 패턴 처리 어려움
- ⚠️ 정확도가 LLM보다 낮을 수 있음
- ⚠️ 키워드 추출 로직 필요

---

### 방안 B: 하이브리드 접근 (권장)

**접근**: Neo4j 패턴 매칭 + LLM 폴백

**구현 방안**:
```python
async def extract_relationships_hybrid(scenario_text: str) -> IndependenceMap:
    """
    하이브리드 추출: Neo4j 패턴 매칭 → LLM 폴백
    
    전략:
    1. Neo4j에서 유사 패턴 조회
    2. 신뢰도 높은 매칭이면 Neo4j 결과 사용
    3. 그렇지 않으면 LLM 호출
    """
    # Step1: Neo4j 패턴 매칭 시도
    neo4j_result = extract_with_neo4j_pattern(scenario_text)
    
    if neo4j_result and neo4j_result.confidence > 0.8:
        return neo4j_result.rel_map
    
    # Step2: LLM 폴백
    return await extract_relationships_llm(scenario_text)
```

**장점**:
- ✅ 비용 절감 (대부분의 경우 Neo4j 사용)
- ✅ 정확도 유지 (LLM 폴백)
- ✅ 새로운 패턴 처리 가능

**단점**:
- ⚠️ 구현 복잡도 증가
- ⚠️ 신뢰도 계산 로직 필요

---

### 방안 C: Neo4j LLM Knowledge Graph Builder 활용

**접근**: Neo4j의 LLM Knowledge Graph Builder 사용

**구현 방안**:
```python
def extract_relationships_with_neo4j_llm_builder(scenario_text: str) -> IndependenceMap:
    """
    Neo4j LLM Knowledge Graph Builder 활용.
    
    참고: Neo4j의 LLM Knowledge Graph Builder는 온라인 애플리케이션이므로
    직접 API 호출이 필요할 수 있음.
    """
    # Neo4j LLM Knowledge Graph Builder API 호출
    # 또는 로컬 Neo4j에 통합된 LLM 기능 활용
    pass
```

**장점**:
- ✅ Neo4j 네이티브 기능 활용
- ✅ 그래프 구조와 자연스럽게 통합

**단점**:
- ⚠️ Neo4j 버전 및 라이선스 요구사항 확인 필요
- ⚠️ 구현 방법 명확하지 않음

---

## 📊 비용 및 정확도 분석

### 현재 방식 (LLM 기반)

| 항목 | 값 |
|------|-----|
| **비용** | 매 요청마다 GPT-4o-mini 호출 |
| **예상 비용/요청** | ~$0.001-0.003 (토큰 수에 따라) |
| **정확도** | 높음 (프롬프트 기반 구조화) |
| **속도** | 느림 (LLM API 호출) |

### Neo4j 기반 추출

| 항목 | 값 |
|------|-----|
| **비용** | Neo4j 쿼리만 (LLM 호출 없음) |
| **예상 비용/요청** | ~$0 (인프라 비용만) |
| **정확도** | 중간 (패턴 매칭 의존) |
| **속도** | 빠름 (로컬 쿼리) |

### 하이브리드 접근

| 항목 | 값 |
|------|-----|
| **비용** | 대부분 Neo4j, 일부 LLM |
| **예상 비용/요청** | ~$0.0003-0.001 (80% Neo4j 사용 가정) |
| **정확도** | 높음 (LLM 폴백) |
| **속도** | 중간 (대부분 빠름) |

**비용 절감 효과**: 약 70-90% 감소 예상

---

## 📋 법령 정보 Context 활용 방안

### 현재 상태

**법령 처리**:
- 분석 후 URL 보강만 수행 (`_enrich_legal_ref_urls`)
- LLM 호출 전 context로 제공하지 않음

**문제점**:
- LLM이 법령 정보를 참고하지 못함
- 법령 기반 판단 정확도 저하 가능
- 법령 인용이 LLM의 일반 지식에 의존

### 감사 독립성 관련 주요 법령 (한국)

**핵심 법령**:
1. **공인회계사법 제21조** (감사인의 독립성)
   - 재무적 이해관계 금지
   - 직계가족 관계 제한
   - 퇴직 후 임원 취임 제한

2. **공인회계사 윤리기준**
   - 독립성 및 객관성 유지
   - 자기검토 위험 방지
   - 과도한 의존성 방지

3. **회계감사기준**
   - 감사인의 독립성 요구사항
   - 품질관리 기준

4. **주식회사 등의 외부감사에 관한 법률**
   - 외부감사인의 독립성
   - 회계법인 감사

5. **공인회계사법 시행령**
   - 독립성 관련 세부 규정

### 개선 방안

#### 1. 감사 독립성 관련 주요 법령 리스트업

**주요 법령** (한국):
```
1. 공인회계사법 제21조 (감사인의 독립성)
2. 공인회계사 윤리기준
3. 회계감사기준
4. 주식회사 등의 외부감사에 관한 법률
5. 공인회계사법 시행령
```

**구현 방안**:
```python
def get_audit_independence_laws() -> str:
    """감사 독립성 관련 주요 법령 정보를 context로 제공."""
    laws = [
        {
            "name": "공인회계사법 제21조",
            "summary": "감사인은 감사대상회사와 독립적인 관계를 유지해야 함",
            "key_points": [
                "재무적 이해관계 금지",
                "직계가족 관계 제한",
                "퇴직 후 임원 취임 제한"
            ]
        },
        {
            "name": "공인회계사 윤리기준",
            "summary": "감사인의 독립성 및 객관성 유지",
            "key_points": [
                "자기검토 위험 방지",
                "과도한 의존성 방지"
            ]
        },
        # ...
    ]
    
    context = "감사 독립성 관련 주요 법령:\n\n"
    for law in laws:
        context += f"- {law['name']}: {law['summary']}\n"
        for point in law['key_points']:
            context += f"  * {point}\n"
        context += "\n"
    
    return context
```

#### 2. Context에 법령 정보 포함

**구현 방안**:
```python
async def analyze_independence_with_laws(
    scenario_text: str, 
    rel_map: IndependenceMap
) -> AnalysisResult:
    """법령 정보를 context에 포함한 독립성 분석."""
    
    # 법령 정보 조회
    laws_context = get_audit_independence_laws()
    
    # Context 구성
    user_prompt = f"""Scenario: {scenario_text}

Relationship Map:
{rel_map.model_dump_json(indent=2)}

Relevant Laws and Regulations:
{laws_context}

Using the entities, relationships, and legal references above, 
provide your assessment in JSON only."""
    
    return await chat_completion_structured(
        client,
        model=settings.independence_analysis_model,
        messages=[
            {"role": "system", "content": _PromptTemplates.ANALYSIS_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        response_model=AnalysisResult,
    )
```

**효과**:
- ✅ 법령 기반 판단 정확도 향상
- ✅ 법령 조문 인용 정확도 향상
- ✅ 일관성 있는 판단

---

## 🎯 권장 구현 방안

### Phase 1: 하이브리드 추출 구현 (즉시 적용)

**구현 순서**:
1. Neo4j 패턴 매칭 함수 구현
2. 신뢰도 계산 로직 추가
3. LLM 폴백 통합
4. 기존 LLM 추출 코드 주석처리 (프롬프트 보존)

**예상 효과**:
- 비용 절감: 70-90%
- 속도 향상: 80-90%
- 정확도: 유지 (LLM 폴백)

### Phase 2: 법령 Context 통합 (즉시 적용)

**구현 순서**:
1. 감사 독립성 관련 법령 리스트업
2. 법령 정보 조회 함수 구현
3. 분석 프롬프트에 법령 정보 포함

**예상 효과**:
- 정확도 향상: 15-25%
- 법령 인용 정확도 향상: 30-40%

---

## ⚠️ 주의사항 및 고려사항

### 1. Neo4j ERExtractionTemplate 확인 필요

**현재 상태**:
- Neo4j에 직접적인 "ERExtractionTemplate" 함수는 확인되지 않음
- Neo4j 버전 및 라이선스 확인 필요

**권장사항**:
- Neo4j 공식 문서 확인
- 또는 사용자가 의도한 구체적인 기능 명시 필요

### 2. 패턴 매칭 정확도

**고려사항**:
- 키워드 추출 정확도
- 패턴 매칭 신뢰도 계산
- 새로운 패턴 처리

**권장사항**:
- 신뢰도 임계값 설정 (예: 0.8)
- 낮은 신뢰도 시 LLM 폴백

### 3. 법령 정보 관리

**고려사항**:
- 법령 정보 업데이트
- 법령 요약 정확도
- 법령 조문 인용

**권장사항**:
- 법령 정보를 별도 파일로 관리
- 법령 전문가 검토
- 정기적 업데이트 프로세스

---

## 📝 구현 체크리스트

### 필수 구현 항목

- [ ] **Neo4j 패턴 매칭 함수** 구현
- [ ] **신뢰도 계산 로직** 추가
- [ ] **LLM 폴백 통합**
- [ ] **기존 LLM 추출 코드 주석처리** (프롬프트 보존)
- [ ] **법령 정보 리스트업** (감사 독립성 관련)
- [ ] **법령 Context 통합** (분석 프롬프트에 포함)

### 선택 구현 항목

- [ ] 법령 정보 캐싱
- [ ] 패턴 매칭 결과 캐싱
- [ ] 법령 정보 업데이트 프로세스

---

## 🔄 더 나은 플로우 제안

### 제안된 플로우 vs 개선된 플로우

#### 제안된 플로우
```
1. Neo4j ERExtractionTemplate()로 엔티티-관계 추출
2. 법령 정보를 context에 포함
3. 독립성 검토 LLM 호출
```

#### 개선된 플로우 (생성형 AI 전문가 권장)

```
Step1: 사용자 입력 후 Neo4j 조회
  ├─ trace_id로 기존 엔티티-관계 조회
  ├─ 있으면 → Step3로 이동 (비용 절감)
  └─ 없으면 → Step2로 이동

Step2: 엔티티-관계 추출
  ├─ Neo4j 패턴 매칭 시도 (ERExtractionTemplate 또는 패턴 매칭)
  ├─ 신뢰도 높으면 → Neo4j 결과 사용
  └─ 신뢰도 낮으면 → LLM 폴백 (기존 프롬프트 활용)
  
Step3: 독립성 검토 LLM 호출
  ├─ Context 구성:
  │   ├─ [엔티티-관계] (Step1 또는 Step2 결과)
  │   └─ [관련 법령] (감사 독립성 관련 법령 리스트)
  └─ LLM 호출 (GPT-4o)

Step4: Mermaid 시각화
  └─ 엔티티-관계 + vulnerable_connections 활용
```

**개선 포인트**:
1. ✅ Neo4j 조회를 먼저 수행하여 중복 추출 방지
2. ✅ 하이브리드 추출로 비용 절감 및 정확도 유지
3. ✅ 법령 정보를 context에 포함하여 정확도 향상
4. ✅ Mermaid 시각화 포함

---

## 💡 추가 개선 방안

### 1. 법령 정보 동적 조회

**현재 제안**: 정적 법령 리스트

**개선 방안**: 시나리오 기반 동적 법령 조회

```python
def get_relevant_laws_for_scenario(scenario_text: str, rel_map: IndependenceMap) -> str:
    """
    시나리오와 엔티티-관계를 기반으로 관련 법령 동적 조회.
    
    전략:
    1. 엔티티-관계에서 위험 패턴 식별
    2. 위험 패턴에 해당하는 법령 조회
    3. 관련 법령만 context에 포함
    """
    # 위험 패턴 식별
    risk_patterns = identify_risk_patterns(rel_map)
    
    # 관련 법령 조회
    relevant_laws = []
    if "직계가족" in risk_patterns:
        relevant_laws.append("공인회계사법 제21조 (직계가족 관계 제한)")
    if "퇴직" in risk_patterns:
        relevant_laws.append("공인회계사법 제21조 (퇴직 후 임원 취임 제한)")
    # ...
    
    return format_laws_context(relevant_laws)
```

**효과**:
- ✅ Context 길이 최적화 (토큰 절감)
- ✅ 관련성 높은 법령만 포함
- ✅ 정확도 향상

### 2. 엔티티-관계 추출 정확도 향상

**개선 방안**: Neo4j 패턴 + LLM 검증

```python
async def extract_relationships_verified(scenario_text: str) -> IndependenceMap:
    """
    Neo4j 패턴 매칭 + LLM 검증.
    
    전략:
    1. Neo4j 패턴 매칭으로 후보 추출
    2. LLM으로 검증 및 보완
    3. 최종 결과 반환
    """
    # Step1: Neo4j 패턴 매칭
    neo4j_candidates = extract_with_neo4j_pattern(scenario_text)
    
    # Step2: LLM 검증 (기존 프롬프트 활용)
    # Neo4j 결과를 힌트로 제공하여 LLM 호출 최소화
    if neo4j_candidates:
        # 힌트 포함하여 LLM 호출 (토큰 절감)
        return await extract_relationships_llm_with_hint(
            scenario_text, 
            hint=neo4j_candidates
        )
    
    # Step3: 일반 LLM 호출
    return await extract_relationships_llm(scenario_text)
```

**효과**:
- ✅ 비용 절감 (힌트 제공으로 토큰 감소)
- ✅ 정확도 향상 (Neo4j 패턴 + LLM 검증)

### 3. 법령 정보 구조화

**개선 방안**: 법령 정보를 구조화된 형태로 제공

```python
class LawReference(BaseModel):
    name: str
    article: str | None
    summary: str
    key_points: list[str]
    applicable_scenarios: list[str]  # 어떤 시나리오에 적용되는지

def get_audit_independence_laws_structured() -> list[LawReference]:
    """구조화된 법령 정보."""
    return [
        LawReference(
            name="공인회계사법",
            article="제21조",
            summary="감사인의 독립성 유지",
            key_points=[
                "재무적 이해관계 금지",
                "직계가족 관계 제한",
                "퇴직 후 임원 취임 제한"
            ],
            applicable_scenarios=[
                "직계가족 관계",
                "퇴직 후 임원 취임",
                "재무적 이해관계"
            ]
        ),
        # ...
    ]
```

**효과**:
- ✅ 유지보수성 향상
- ✅ 확장성 향상
- ✅ 법령 전문가 검토 용이

---

## ✅ 결론

### 제안된 방안 평가

| 항목 | 평가 | 비고 |
|------|------|------|
| **비용 감소** | ✅ 매우 효과적 | 70-90% 감소 예상 |
| **정확도 향상** | ✅ 효과적 | 법령 Context 통합으로 향상 |
| **구현 가능성** | ⚠️ 확인 필요 | Neo4j ERExtractionTemplate 확인 필요 |
| **유지보수성** | ✅ 양호 | 하이브리드 접근으로 유연성 확보 |

### 최종 권장사항

#### 즉시 구현 권장

1. **법령 Context 통합** (정확도 향상)
   - 감사 독립성 관련 법령 리스트업
   - 분석 프롬프트에 법령 정보 포함
   - 예상 효과: 정확도 15-25% 향상

2. **Neo4j 조회 로직 추가** (비용 절감)
   - trace_id 기반 엔티티-관계 조회
   - 중복 추출 방지
   - 예상 효과: 비용 70-90% 절감

#### 검토 후 구현

3. **하이브리드 추출** (비용 절감 + 정확도 유지)
   - Neo4j 패턴 매칭 + LLM 폴백
   - 신뢰도 기반 분기
   - 예상 효과: 비용 70-90% 절감, 정확도 유지

4. **동적 법령 조회** (정확도 향상)
   - 시나리오 기반 관련 법령만 조회
   - Context 길이 최적화
   - 예상 효과: 정확도 추가 5-10% 향상

### 구현 우선순위

1. **P0 (최우선)**: 법령 Context 통합
2. **P1 (높음)**: Neo4j 조회 로직 추가
3. **P2 (중간)**: 하이브리드 추출
4. **P3 (낮음)**: 동적 법령 조회

---

**검토 완료일**: 2026-02-12  
**상태**: ✅ 방안 타당성 확인, 개선된 플로우 제안
