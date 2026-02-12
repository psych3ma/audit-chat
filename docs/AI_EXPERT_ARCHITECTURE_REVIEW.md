# AI 전문가 관점 — 큰 그림 및 구성요소·흐름 검토

전체 아키텍처와 구성요소 배치, 그들 간 데이터/제어 흐름을 정리한 문서입니다.

---

## 1. 큰 그림 (레이어별)

```
┌─────────────────────────────────────────────────────────────────────────┐
│  사용자                                                                   │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  진입로 (2종)                                                             │
│  • 정적 UI:  브라우저 → FastAPI /static → audit-chat-pwc.html             │
│  • Streamlit: 브라우저 → Streamlit(frontend/app.py) → 메뉴(홈/독립성/채팅/그래프) │
└─────────────────────────────────────────────────────────────────────────┘
         │
         │  (독립성 검토 시) POST /independence/review { scenario }
         │  (채팅 시)       POST /chat/completions { messages }
         │  (그래프 시)     GET  /graph/mermaid
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  백엔드 (FastAPI)                                                         │
│  • 라우터: health, chat, graph, independence                              │
│  • 설정: get_settings() → .env (API 키, Neo4j, LAW_GO_KR_OC, law_csv_path) │
└─────────────────────────────────────────────────────────────────────────┘
         │
         ├── 독립성 검토 파이프라인
         │      extract_relationships(scenario)  ──► LLM(구조화) → IndependenceMap
         │      analyze_independence(scenario, rel_map) ──► LLM(구조화) → AnalysisResult
         │      _enrich_legal_ref_urls(analysis) ──► law_registry.get_law_url() → URL 보강
         │      build_mermaid_graph(rel_map)     ──► Mermaid 문자열
         │      save_independence_map_to_neo4j   ──► (선택) Neo4j
         │
         ├── 채팅 ──► llm_service.get_llm_response (비구조화)
         ├── 그래프 ──► get_neo4j_session() → Cypher → Mermaid
         └── 법령 URL ──► law_registry ← config.law_csv_path, 법령검색목록.csv
         │
         ▼
┌─────────────────────────────────────────────────────────────────────────┐
│  외부/자원                                                                │
│  • OpenAI API (구조적 출력: llm_structured / 일반: llm_service)            │
│  • Neo4j (독립성 엔티티 저장, 그래프 조회)                                 │
│  • 법령검색목록.csv (로컬), law.go.kr (사용자 링크만, API 호출 없음)        │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 구성요소 배치 적절성

| 레이어 | 구성요소 | 역할 | 배치 평가 |
|--------|----------|------|-----------|
| **진입로** | `audit-chat-pwc.html` | 회계법인 제출용 단일 페이지, 시나리오 입력 → 리포트(관계도·의견·근거 법령) | ✅ 정적 UI가 동일 백엔드 `/independence/review` 호출로 일원화 |
| | `frontend/app.py` | Streamlit 멀티페이지(홈/독립성/채팅/그래프), 헬스 표시 | ✅ 독립성·채팅·그래프가 각각 대응 API와 1:1 |
| **라우터** | `independence` | POST /independence/review → run_independence_review | ✅ 단일 책임 |
| | `chat` | POST /chat/completions → llm_service | ✅ |
| | `graph` | GET /graph/mermaid → Neo4j → Mermaid | ✅ |
| **서비스** | `independence_service` | 추출 → 분석 → 법령 URL 보강 → Mermaid → (Neo4j 저장) | ✅ 파이프라인 한 곳에서 제어 |
| | `llm_structured` | 구조적 출력 공통 레이어(JSON 모드 + Pydantic 검증) | ✅ 추출/분석이 동일 API 사용, 확장 시 재사용 |
| | `llm_service` | 일반 채팅 (비구조화) | ✅ 채팅만 사용, 구조화와 분리 |
| **유틸** | `law_registry` | CSV 로드, 법령명 정규화, 조문/전체 URL 생성 | ✅ 법령 URL 단일 소스, 설정(law_csv_path)만 의존 |
| **설정** | `config` | .env → Settings, get_settings() | ✅ 모든 서비스/DB/법령이 여기만 참조 |
| **영속** | `database` | Neo4j 드라이버, get_neo4j_session() | ✅ lifespan에서 종료, independence·graph만 사용 |

**결론**: 레이어별로 역할이 나뉘어 있고, “구조적 LLM / 일반 LLM / 법령 URL / DB”가 각각 한 곳에 모여 있어 **구성요소 배치는 적절**합니다.

---

## 3. 구성요소 간 데이터·제어 흐름

### 3.1 독립성 검토 (핵심 파이프라인)

| 순서 | 출발 | 도착 | 데이터/제어 | 검증 |
|------|------|------|-------------|------|
| 1 | 클라이언트(정적/Streamlit) | Router `POST /independence/review` | `{ scenario }` | ✅ 요청 본문 일치 |
| 2 | Router | `run_independence_review(scenario)` | scenario 문자열 | ✅ |
| 3 | run_independence_review | `extract_relationships(scenario)` | scenario | ✅ |
| 4 | extract_relationships | `llm_structured.chat_completion_structured(..., response_model=IndependenceMap)` | 프롬프트 + 시나리오 | ✅ 구조화 1단계 |
| 5 | LLM | IndependenceMap (entities, connections) | rel_map | ✅ Pydantic 검증 |
| 6 | run_independence_review | `analyze_independence(scenario, rel_map)` | scenario + rel_map | ✅ 맵이 분석에 전달됨 |
| 7 | analyze_independence | `chat_completion_structured(..., response_model=AnalysisResult)` | 시나리오 + **Relationship Map JSON** | ✅ 프롬프트에 맵 반영 |
| 8 | LLM | AnalysisResult (status, key_issues, considerations, legal_references, …) | analysis | ✅ |
| 9 | run_independence_review | `_enrich_legal_ref_urls(analysis)` | analysis | ✅ |
| 10 | _enrich_legal_ref_urls | `law_registry.get_law_url(ref.name)` | 법령 표기 문자열 | ✅ config·CSV 경로 연동 |
| 11 | run_independence_review | `build_mermaid_graph(rel_map)` | rel_map | ✅ 관계도와 리포트 일치 |
| 12 | run_independence_review | `save_independence_map_to_neo4j(trace_id, rel_map)` | (선택) | ✅ 실패 시 무시, 파이프라인 계속 |
| 13 | run_independence_review | return `{ trace_id, rel_map, analysis, mermaid_code }` | 응답 일원화 | ✅ |
| 14 | 클라이언트 | UI 렌더 | trace_id, 관계도 이미지, 주요 이슈·검토 의견·권고 안전장치·근거 법령 | ✅ 정적 HTML/Streamlit 각자 렌더 |

**요약**: 시나리오 → 추출(엔티티/관계) → **추출 결과가 분석 프롬프트에 그대로 전달** → 분석(한국어·grounding 지시 반영) → 법령 URL 보강 → Mermaid·Neo4j·응답까지 **데이터가 끊기지 않고 이어짐**. 구성요소 간 **오가는 흐름이 올바릅니다**.

### 3.2 설정·부가 자원

| 출발 | 도착 | 내용 |
|------|------|------|
| .env | get_settings() | OPENAI_API_KEY, NEO4J_*, LAW_GO_KR_OC, law_csv_path 등 |
| get_settings() | independence_service | 모델명, temperature, API 키(OpenAI 클라이언트) |
| get_settings() | law_registry.get_registry() | law_csv_path (또는 기본 프로젝트 루트 CSV) |
| get_settings() | database.Neo4jDriver | neo4j_uri, user, password |
| 법령검색목록.csv | law_registry._build_registry() | 법령명 → 법령MST (lsiSeq) |

**결론**: 설정과 CSV가 한 방향으로만 참조되고, 순환 없이 잘 이어집니다.

### 3.3 채팅·그래프 (보조 기능)

- **채팅**: Streamlit → POST /chat/completions → llm_service → OpenAI (비구조화). 독립성 파이프라인과 분리되어 있어 **흐름 충돌 없음**.
- **그래프**: Streamlit → GET /graph/mermaid → Neo4j Cypher (MATCH (n)-[r]->(m)) → Mermaid. 독립성 검토에서 저장한 IndependenceEntity/RELATION도 동일 Neo4j에 있으면 그래프에 포함 가능. **의도된 공유**.

---

## 4. 경계·일관성 점검

| 항목 | 상태 | 비고 |
|------|------|------|
| 구조적 출력 경로 | ✅ | 추출·분석만 `llm_structured` 사용, 채팅은 `llm_service` — 역할 분리 명확 |
| 엔티티/관계 반영 | ✅ | rel_map이 analyze_independence 유저 메시지에 포함, 프롬프트에 “Relationship Map 기반 서술” 명시 |
| 법령 URL | ✅ | independence_service만 `get_law_url` 호출, law_registry가 단일 소스 |
| 비밀/설정 | ✅ | 코드에 하드코딩 없음, config + .env 일원화 |
| 에러 전달 | ✅ | independence 라우터에서 _normalize_error_detail로 사용자 메시지 일원화 |
| 진입로 이원화 | ⚠️ | 정적 HTML과 Streamlit 두 진입로가 동일 API 사용 — 기능은 동일. 정적은 “제출용”, Streamlit은 “내부·실험용” 등 용도만 문서에 명시하면 충분 |

---

## 5. AI 전문가 관점 결론

| 질문 | 답변 |
|------|------|
| **큰 그림이 잡혀 있는가?** | ✅ 사용자 → 진입로(정적/Streamlit) → FastAPI → 서비스/LLM/법령/DB → 외부 자원으로 레이어가 분리되어 있고, 핵심은 “독립성 검토 파이프라인” 한 줄로 설명 가능. |
| **구성요소가 적절한 위치에 있는가?** | ✅ 라우터·서비스·구조화 레이어·법령 레지스트리·설정·DB가 각각 한 곳에 모여 있고, 중복 없음. |
| **구성요소 간에 잘 오가고 있는가?** | ✅ 시나리오 → 추출 → **맵 → 분석** → 법령 보강 → Mermaid·Neo4j·응답까지 데이터가 끊기지 않음. 설정·CSV·에러 처리도 단방향·일관되게 연결됨. |

**권장 유지 사항**

- 독립성 검토는 “추출 → 분석(맵 반영) → 법령 보강 → Mermaid·Neo4j” 순서를 유지.
- 구조적 출력 추가 시 `llm_structured`만 확장하고, 법령 링크 필요 시 `law_registry.get_law_url`만 사용.
- 진입로가 두 가지(정적/Streamlit)인 것은 유지하되, README 등에 “정적: 제출용, Streamlit: 내부/실험용” 정도로 용도만 명시해 두면 좋음.

이 문서는 아키텍처나 진입로/라우터 변경 시 함께 갱신하는 것을 권장합니다.
