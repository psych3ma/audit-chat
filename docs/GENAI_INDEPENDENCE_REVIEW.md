# 생성형 AI 전문가 관점 — 독립성 검토 기능 검토

Colab 노트북(Independence Review System)과 동일한 기능이 **정상 작동하도록** 구현되었는지 검토한 결과입니다.

---

## 1. Colab vs 현재 구현 대조

| 항목 | Colab | 현재 구현 | 일치 |
|------|--------|-----------|------|
| **모델** | EXTRACTION=gpt-4o-mini, ANALYSIS=gpt-4o | config 동일 | ✅ |
| **Temperature** | STRUCTURED=0.0, CREATIVE=0.3 | config 동일 | ✅ |
| **데이터 모델** | AuditEntity, Relationship, IndependenceMap, AnalysisResult, IndependenceStatus | backend.models.independence 동일 | ✅ |
| **프롬프트** | EXTRACTION_SYSTEM, ANALYSIS_SYSTEM, ANALYSIS_USER | _PromptTemplates 동일 문구 | ✅ |
| **흐름** | extract_relationships → analyze_independence → 리포트 | run_independence_review 동일 | ✅ |
| **재시도** | RateLimitError 시 2^attempt sleep, 기타 1초 | _call_with_retry 동일 | ✅ |
| **Mermaid** | build_mermaid_graph (graph LR, entity id/label/name, conn -- "rel_type" -->) | build_mermaid_graph 동일 형식 | ✅ |
| **trace_id** | md5(scenario)[:8].upper() | 동일 | ✅ |
| **Structured Output** | `client.beta.chat.completions.parse(response_format=Pydantic)` | ❌ openai 1.12에 beta.parse 없음 → **create + json_object + 수동 파싱**으로 대체 | ⚠️ 동작 동일 목표 |

---

## 2. 생성형 AI 관점 검토

### 2.1 구조적 출력(Structured Output)

- **Colab**: `response_format=IndependenceMap` / `AnalysisResult` 로 스키마 강제.
- **현재**: openai 1.12 호환을 위해 `response_format={"type": "json_object"}` + 시스템 프롬프트에 JSON 구조 명시 + `_parse_json_content()` 후 `Model.model_validate(data)`.
- **평가**: 스키마 강제는 프롬프트로 보완. 일부 응답이 스키마를 벗어나면 `model_validate` 시 ValidationError → 재시도로 완화. **정상 작동 가능**.

### 2.2 프롬프트

- 추출: "Output only valid JSON with this exact structure..." 로 entities/connections 형식 명시.
- 분석: status 후보(수임 불가 / 안전장치 적용 시 수임 가능 / 수임 가능), risk_level, key_issues, considerations, suggested_safeguards 등 요청.
- **평가**: Colab과 동일한 역할·의도 유지. JSON 전용 지시로 파싱 안정성 확보.

### 2.3 상태 정규화

- `AnalysisResult.status`: Colab과 동일한 `normalize_status` (한글/영문 키워드 → IndependenceStatus) 적용.
- **평가**: 모델이 문자열로 반환해도 Enum으로 정규화됨.

### 2.4 에러·재시도

- RateLimitError: 지수 백오프.
- 기타 예외: 1초 후 재시도.
- **평가**: Colab과 동일한 전략.

---

## 3. 수정 사항 요약 (정상 작동을 위해 반영된 내용)

1. **API 호출**: `client.beta.chat.completions.parse()` 제거 → `client.chat.completions.create(..., response_format={"type": "json_object"})` 사용.
2. **파싱**: `response.choices[0].message.content` → `_parse_json_content()` (마크다운 코드블록 제거 후 `json.loads`) → `IndependenceMap.model_validate()` / `AnalysisResult.model_validate()`.
3. **프롬프트**: 시스템 프롬프트에 JSON 구조 설명 추가로 스키마 준수 유도.

---

## 4. 결론

- **로직·모델·프롬프트·흐름·Mermaid**: Colab과 동일하게 구현되어 있음.
- **Structured Output**: openai 1.12 환경에 맞게 `create` + JSON 모드 + 수동 검증으로 대체했으며, 생성형 AI 관점에서 **동일 기능이 정상 작동하도록 구현된 상태**로 판단됨.
- **권장**: 추후 openai SDK에서 `chat.completions.parse()`(비-beta)를 지원하는 버전으로 올리면, 동일 Pydantic 스키마로 다시 `parse` 전환하면 스키마 강제력이 더 높아짐.

---

## 5. 엔티티/관계 반영 및 답변 품질 검토 (보고서 내용 생성)

### 5.1 현재 흐름

1. **추출**: `extract_relationships(scenario)` → `IndependenceMap` (entities, connections).
2. **분석**: `analyze_independence(scenario, rel_map)` 에서 유저 메시지가 `"Scenario: {scenario}\n\nRelationship Map: {map_json}\n\nProvide assessment in JSON only."` 로 전달됨.
3. **결론**: 관계 맵(엔티티 id/name/label, 연결 source_id/target_id/rel_type)은 **분석 단계에 전달되고 있음**.

### 5.2 문제점

| 현상 | 원인 |
|------|------|
| **엔터리로 짧게 답함** | 분석 프롬프트에 “구체적으로”, “2~4문장”, “concrete” 등 **길이·구체성 지시가 없음**. |
| **영어/한국어 뒤섞임** | **출력 언어(한국어만) 지정이 없음**. 모델이 key_issues/considerations를 영어로 줄여서 내는 경우 발생. |
| **관계 맵을 덜 반영** | “Relationship Map을 반드시 활용하여 서술하라”, “엔티티명·관계 유형을 구체적으로 인용하라”는 **grounding 지시가 없음**. |

### 5.3 해결 방안 (적용됨)

1. **분석 시스템 프롬프트 보강**
   - **언어**: `key_issues`, `considerations`, `suggested_safeguards`, `legal_references` 는 **모두 한국어로만** 작성하도록 명시.
   - **Grounding**: 판단은 **반드시 시나리오와 Relationship Map에 기반**하며, 주요 이슈·검토 의견에는 **맵에 나온 엔티티 이름·관계 유형(rel_type)을 구체적으로 인용**하도록 지시.
   - **길이·구체성**: `considerations`는 **2문장 이상의 단락**으로 독립성 위협과 판단 이유를 서술, `key_issues`는 **구체적 사실**을 나열하도록 지시.

2. **추출 단계 rel_type 한국어 권장**
   - 관계 유형(`rel_type`)을 **한국어**(예: 소속, 감사대상, 직계가족, 대표이사)로 내도록 하면, 관계도와 보고서 문구가 일치하고 한국어 출력과도 정렬됨.

3. **구조 유지**
   - JSON 스키마·필드명은 그대로 두고, **프롬프트 문구만** 위 내용으로 보강하여 기존 파이프라인과 호환 유지.
