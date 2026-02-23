# Neo4j 조회 로직 추가 검토 (CTO 전문가 관점)

**작성일**: 2026-02-12  
**검토자**: CTO 전문가 관점  
**목적**: trace_id 기반 Neo4j 조회 로직 추가로 비용 절감 방안 검토 및 구현

---

## 📋 요구사항

### 목표
1. **trace_id 기반 엔티티-관계 조회**: Neo4j에서 기존 데이터 재사용
2. **중복 추출 방지**: 동일 시나리오에 대한 LLM 호출 제거
3. **비용 절감**: 70-90% 비용 절감 예상

---

## 🔍 현재 상태 분석

### 현재 구현 (`/chat/completions`)

```python
# 현재 흐름
scenario_text = user_messages[-1].content.strip()

# 항상 추출 수행 (LLM 호출)
rel_map = await extract_relationships(scenario_text)  # GPT-4o-mini 호출

# Neo4j 저장 (이후 사용 안 함)
trace_id = hashlib.md5(scenario_text.encode()).hexdigest()[:8].upper()
save_independence_map_to_neo4j(trace_id, rel_map)
```

**문제점**:
- ❌ Neo4j 조회 없이 항상 LLM 호출
- ❌ 동일 시나리오에 대해 중복 추출 발생
- ❌ 저장된 데이터 재사용 안 함

### trace_id 생성 방식

```python
trace_id = hashlib.md5(scenario_text.encode()).hexdigest()[:8].upper()
```

**특징**:
- 시나리오 텍스트의 MD5 해시 (8자리)
- 동일 시나리오 → 동일 trace_id
- **장점**: 간단하고 빠름
- **단점**: 시나리오 텍스트 변경 시 다른 trace_id (공백, 띄어쓰기 등)

---

## 💡 개선 방안

### 1. Neo4j 조회 함수 구현

**함수 시그니처**:
```python
def get_independence_map_from_neo4j(trace_id: str) -> IndependenceMap | None:
    """Neo4j에서 trace_id 기반 엔티티-관계 조회. 없으면 None 반환."""
```

**Cypher 쿼리**:
```cypher
MATCH (n:IndependenceEntity {trace_id: $trace_id})
OPTIONAL MATCH (n)-[r:RELATION]->(m:IndependenceEntity {trace_id: $trace_id})
RETURN n, r, m
```

**구현 전략**:
1. trace_id로 노드 조회
2. 노드가 없으면 `None` 반환
3. 노드가 있으면 엔티티와 관계 재구성
4. `IndependenceMap` 객체로 변환

### 2. `/chat/completions` 흐름 개선

**개선된 흐름**:
```python
# Step1: trace_id 생성
trace_id = hashlib.md5(scenario_text.encode()).hexdigest()[:8].upper()

# Step2: Neo4j 조회 시도
rel_map = get_independence_map_from_neo4j(trace_id)

# Step3: 없으면 추출 수행
if rel_map is None:
    rel_map = await extract_relationships(scenario_text)  # LLM 호출
    save_independence_map_to_neo4j(trace_id, rel_map)  # 저장

# Step4: Context 구성 및 LLM 호출
context = build_context(rel_map)
reply = get_llm_response(...)
```

**비용 절감 효과**:
- **기존**: 매 요청마다 LLM 호출 (GPT-4o-mini)
- **개선**: Neo4j에 있으면 LLM 호출 없음
- **절감률**: 70-90% (재사용률에 따라)

### 3. 에러 핸들링 전략

**Neo4j 미연결 시**:
- 조회 실패 → LLM 추출로 폴백
- 저장 실패 → 무시 (기존과 동일)

**구현**:
```python
try:
    rel_map = get_independence_map_from_neo4j(trace_id)
except Exception:
    rel_map = None  # 폴백: LLM 추출
```

---

## 📊 비용 분석

### LLM 호출 비용 (GPT-4o-mini)

**현재**:
- 매 요청마다 추출: **$0.001-0.003/요청**
- 월 1,000 요청 기준: **$1-3/월**

**개선 후**:
- Neo4j 조회 성공 시: **$0** (LLM 호출 없음)
- Neo4j 조회 실패 시: **$0.001-0.003/요청** (기존과 동일)

**비용 절감**:
- 재사용률 80% 가정: **$0.8-2.4/월** → **$0.2-0.6/월**
- **절감률**: **70-80%**

### Neo4j 조회 비용

**로컬 Neo4j**: **무료**
**클라우드 Neo4j**: 기존 인프라 활용 (추가 비용 없음)

**조회 성능**:
- Neo4j 쿼리: **~10-50ms** (로컬)
- LLM 호출: **~500-2000ms**
- **성능 향상**: **10-200배**

---

## ⚠️ 리스크 및 고려사항

### 1. trace_id 충돌 가능성

**문제**: MD5 해시 8자리 → 충돌 가능성 존재

**확률 계산**:
- 가능한 조합: 16^8 = 4,294,967,296
- 충돌 확률 (생일 문제): ~50% 충돌 시 65,536개 시나리오

**해결 방안**:
- 현재는 충돌 확률 낮음 (실용적)
- 필요 시 16자리로 확장 가능

### 2. 시나리오 텍스트 정규화

**문제**: 공백, 띄어쓰기 차이로 다른 trace_id 생성

**예시**:
- "김 회계사는 A회계법인에 소속되어 있다"
- "김 회계사는 A회계법인에 소속되어있다"

**해결 방안**:
- 텍스트 정규화 후 해시 (공백 제거, 대소문자 통일)
- 또는 시나리오 핵심 내용만 추출하여 해시

**구현**:
```python
def normalize_scenario_text(text: str) -> str:
    """시나리오 텍스트 정규화"""
    # 공백 제거, 대소문자 통일 등
    return re.sub(r'\s+', ' ', text.strip().lower())

trace_id = hashlib.md5(normalize_scenario_text(scenario_text).encode()).hexdigest()[:8].upper()
```

### 3. 데이터 일관성

**문제**: Neo4j에 저장된 데이터와 LLM 추출 결과가 다를 수 있음

**고려사항**:
- LLM 추출 결과는 비결정적일 수 있음
- 동일 시나리오라도 추출 결과가 약간 다를 수 있음

**해결 방안**:
- 현재는 재사용 우선 (비용 절감)
- 필요 시 버전 관리 또는 재추출 옵션 추가 가능

---

## 🎯 구현 계획

### Phase 1: Neo4j 조회 함수 구현

**파일**: `backend/services/independence_service.py`

**함수**:
```python
def get_independence_map_from_neo4j(trace_id: str) -> IndependenceMap | None:
    """Neo4j에서 trace_id 기반 엔티티-관계 조회."""
```

**예상 코드량**: 50-80줄

**시간**: 1-2시간

### Phase 2: `/chat/completions` 수정

**파일**: `backend/routers/chat.py`

**변경사항**:
1. trace_id 먼저 생성
2. Neo4j 조회 시도
3. 없으면 추출 수행
4. 저장 (기존과 동일)

**예상 코드량**: 10-20줄 수정

**시간**: 0.5-1시간

### Phase 3: 테스트 및 검증

**테스트 시나리오**:
1. Neo4j에 없는 시나리오 → 추출 수행
2. Neo4j에 있는 시나리오 → 조회 성공
3. Neo4j 미연결 → 폴백 동작

**시간**: 0.5-1시간

**총 예상 시간**: **2-4시간**

---

## 📝 구현 우선순위

### P0 (최우선)
- ✅ Neo4j 조회 함수 구현
- ✅ `/chat/completions` 수정
- ✅ 에러 핸들링

### P1 (선택적)
- 시나리오 텍스트 정규화
- trace_id 충돌 방지 (16자리 확장)
- 버전 관리 (재추출 옵션)

---

## ✅ CTO 최종 권장사항

### 구현 권장: ✅ **즉시 구현**

**이유**:
1. **비용 절감 효과 큼**: 70-90% 절감
2. **구현 복잡도 낮음**: 2-4시간
3. **리스크 낮음**: 기존 인프라 활용, 폴백 로직 포함
4. **성능 향상**: Neo4j 조회가 LLM 호출보다 10-200배 빠름

### 구현 순서
1. **Neo4j 조회 함수 구현** (P0)
2. **`/chat/completions` 수정** (P0)
3. **테스트 및 검증** (P0)
4. **텍스트 정규화** (P1, 선택적)

---

## 🎯 예상 효과

### 비용 절감
- **LLM 호출**: 70-90% 감소
- **월 비용**: $1-3 → $0.2-0.6 (재사용률 80% 기준)

### 성능 향상
- **응답 시간**: 500-2000ms → 10-50ms (Neo4j 조회 시)
- **처리량**: 10-200배 향상

### 사용자 경험
- **일관성**: 동일 시나리오에 대해 동일 결과
- **속도**: 빠른 응답 시간

---

**검토 완료일**: 2026-02-12  
**상태**: ✅ 구현 권장 (P0)
