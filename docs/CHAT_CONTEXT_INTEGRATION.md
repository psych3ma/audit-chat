# `/chat` 엔드포인트 Context 통합 구현

**작성일**: 2026-02-12  
**목적**: 엔티티-관계 추출 결과를 `/chat`의 context로 활용하도록 구현

---

## 📋 구현 내용

### 변경사항

**파일**: `backend/routers/chat.py`

**변경 전**:
- 사용자 메시지를 그대로 LLM에 전달
- 엔티티-관계 정보 활용 없음

**변경 후**:
- 사용자 메시지에서 시나리오 추출
- 엔티티-관계 추출 (`extract_relationships`)
- 추출 결과를 context로 구성하여 프롬프트에 포함
- Neo4j에 저장 (선택적)

---

## 🔄 구현된 흐름

```
[chat] 시나리오 입력
  ↓
[llm_1st] 엔티티-관계 추출 (extract_relationships)
  ↓
추출 결과를 context로 구성
  ↓
[llm_2nd] Context 포함하여 LLM 호출 (get_llm_response)
  ↓
응답 반환
  ↓
Neo4j에 저장 (선택적)
```

---

## 💻 코드 구조

### 1. 엔티티-관계 추출

```python
# 사용자 메시지에서 시나리오 추출
scenario_text = user_messages[-1].content.strip()

# 엔티티-관계 추출 (llm_1st)
rel_map = await extract_relationships(scenario_text)
```

### 2. Context 구성

```python
rel_map_json = rel_map.model_dump_json(indent=2)
context = f"""다음은 입력된 시나리오에서 추출한 엔티티-관계 정보입니다:

{rel_map_json}

이 정보를 참고하여 답변해주세요. 엔티티와 관계를 명확히 언급하고, 구체적인 분석을 제공해주세요."""
```

### 3. 프롬프트 구성

```python
system_message = {
    "role": "system",
    "content": "당신은 감사 독립성 검토 전문가입니다. 제공된 엔티티-관계 정보를 활용하여 시나리오를 분석하고 답변하세요."
}

enhanced_messages = [
    system_message,
    {"role": "user", "content": context + "\n\n시나리오: " + scenario_text}
]
```

### 4. Neo4j 저장

```python
try:
    trace_id = hashlib.md5(scenario_text.encode()).hexdigest()[:8].upper()
    save_independence_map_to_neo4j(trace_id, rel_map)
except Exception:
    pass  # Neo4j 미연결 시 무시
```

---

## ✅ 구현 완료 사항

- [x] 엔티티-관계 추출 통합
- [x] Context 구성 및 프롬프트 포함
- [x] Neo4j 저장 (선택적)
- [x] 에러 처리
- [x] 기존 대화 기록 유지

---

## 🎯 효과

### Before
- 사용자 메시지를 그대로 LLM에 전달
- 엔티티-관계 정보 활용 없음
- 구조화된 정보 부족

### After
- 엔티티-관계 정보를 context로 활용
- 더 정확하고 구조화된 답변 가능
- Neo4j에 저장되어 재사용 가능

---

## 📝 참고사항

1. **성능**: 매 요청마다 엔티티-관계 추출 수행 (향후 캐싱 고려)
2. **비용**: 추출 단계 추가로 비용 증가 가능
3. **Neo4j**: 선택적 저장 (연결 실패 시 무시)

---

**구현 완료일**: 2026-02-12  
**상태**: ✅ 구현 완료
