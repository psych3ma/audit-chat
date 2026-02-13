# 독립성 검토 3단계 — 단계별 코드 매칭 (생성형 AI 전문가 관점)

> 목적: 프로그레스 UI 단계 전환을 **실제 실행 구간**과 맞추기 위한 매핑 문서.  
> 하드코딩된 타이머 제거 후, 단계별 API 완료 시점에 `setProgressStep(n)` 호출.

---

## 1. 단계 ↔ 백엔드 코드 매칭

| UI 단계 | 표출 문구 | 백엔드 실행 구간 | 파일:함수(라인) |
|--------|-----------|------------------|------------------|
| **1단계** | (1/3) 관계 추출 | 1차 LLM: 시나리오 → 엔티티·관계 맵 | `independence_service.py`: `extract_relationships(scenario)` 호출 ~ 완료 |
| **2단계** | (2/3) 독립성 분석 | 2차 LLM: 맵 + 시나리오 → 수임 여부, 이슈, 안전장치, 법령 | `independence_service.py`: `analyze_independence(scenario, rel_map)` 호출 ~ 완료 |
| **3단계** | (3/3) 보고서 생성 | 법령 URL 보강, Mermaid 생성, (선택) Neo4j 저장 | `independence_service.py`: `_enrich_legal_ref_urls(analysis)` + `build_mermaid_graph(...)` + `save_independence_map_to_neo4j(...)` |

**실제 코드 흐름** (`run_independence_review`):

```text
rel_map = await extract_relationships(scenario)   # ← 1단계 완료 시점
analysis = await analyze_independence(scenario, rel_map)  # ← 2단계 완료 시점
analysis = _enrich_legal_ref_urls(analysis)
mermaid_code = build_mermaid_graph(rel_map, analysis.vulnerable_connections)
save_independence_map_to_neo4j(...)  # ← 3단계 완료 시점 (위 블록 전체)
return { trace_id, rel_map, analysis, mermaid_code }
```

---

## 2. 프론트 진행률 연동 방식

- **기존**: 단일 `POST /independence/review` + 클라이언트 타이머(`WORKFLOW_STEP_DELAYS_MS`)로 1→2→3 전환 → **실제 진행과 불일치**.
- **변경**: 백엔드를 **단계별 엔드포인트**로 분리하고, 프론트에서 순차 호출 후 **각 응답 수신 시** `setProgressStep(n)` 호출.

| 단계 | API | 프론트 동작 |
|------|-----|-------------|
| 1 | `POST /independence/extract` | 요청 전 `setProgressStep(0)` → 응답 수신 시 `setProgressStep(1)` |
| 2 | `POST /independence/analyze` (scenario + rel_map) | 요청 전 이미 1 → 응답 수신 시 `setProgressStep(2)` |
| 3 | `POST /independence/report` (scenario + rel_map + analysis) | 요청 전 이미 2 → 응답 수신 시 카드 렌더 + `done()` |

이렇게 하면 **각 단계가 실행 완료된 직후**에만 프로그레스가 넘어가므로, 표출 속도 하드코딩 없이 실제 진행률과 일치한다.

---

## 3. 생성형 AI 전문가 관점 요약

- **1단계**: 입력(시나리오) → 구조화(추출). 코드: `extract_relationships` 한 번의 LLM 호출.
- **2단계**: 구조 + 맥락 → 판단(분석). 코드: `analyze_independence` 한 번의 LLM 호출.
- **3단계**: 판단 결과 → 사용자용 출력(보고서). 코드: `_enrich_legal_ref_urls` + `build_mermaid_graph` + Neo4j 저장.

단계별 엔드포인트는 위 세 블록과 1:1로 대응하며, 프론트는 각 응답 수신 시점에만 단계를 올린다.

---

## 4. 구현 상태 (CTO 체크)

| 구분 | 구현 |
|------|------|
| 백엔드 | `POST /independence/extract`, `/analyze`, `/report` 노출. `POST /review`는 기존 호환용 유지. |
| 서비스 | `build_independence_report()` 분리로 3단계만 재사용. `run_independence_review()`는 extract → analyze → build_independence_report 호출. |
| 프론트 | 단일 fetch 제거, extract → analyze → report 순차 호출. 각 응답 시 `setProgressStep(1|2)` 후 다음 요청. 타이머(`WORKFLOW_STEP_DELAYS_MS`) 제거. |
| 하드코딩 | 단계 전환 시점 = API 완료 시점만 사용. 매직넘버 없음. |

---

## 4. 구현 요약

| 구분 | 구현 |
|------|------|
| 백엔드 | `POST /independence/extract` → `POST /independence/analyze` → `POST /independence/report` (기존 `POST /review`는 일괄 호출용 유지) |
| 서비스 | `build_independence_report()` 분리로 3단계만 담당, `run_independence_review()`는 extract → analyze → build_report 순 호출 |
| 프론트 | `WORKFLOW_STEP_DELAYS_MS` 제거, extract 응답 후 `setProgressStep(1)` → analyze 응답 후 `setProgressStep(2)` → report 응답 후 카드 렌더 + `done()` |
