# CTO — 유지보수·확장성·일관성 가이드

구조적 LLM 출력(Structured Output) 및 OpenAI SDK 버전 정책을 정리한 문서입니다.

---

## 1. 구조적 출력(Structured Output) — 단일 추상화

### 1.1 배경

- **Colab**: `client.beta.chat.completions.parse(response_format=Pydantic)` 사용.
- **openai 1.12**: `beta.chat.completions` 미지원 → 해당 호출 시 500 발생.
- **대응**: `client.chat.completions.create(response_format={"type": "json_object"})` + 응답 본문 JSON 파싱 + Pydantic 검증.

### 1.2 일관된 사용처

| 목적 | 사용처 |
|------|--------|
| **공통 레이어** | `backend/services/llm_structured.py` |
| **제공 API** | `chat_completion_structured(client, model=..., messages=..., temperature=..., response_model=PydanticModel)` |
| **유틸** | `parse_json_content(content)`, `call_with_retry(func)` |

**규칙**: 새로운 “구조화된 LLM 응답”이 필요하면 반드시 `llm_structured.chat_completion_structured()`를 사용한다.  
동일 로직을 서비스마다 복사하지 않는다.

### 1.3 SDK/API 변경 시

- openai 패키지 업그레이드 후 `chat.completions.parse()` 등 공식 structured API를 쓰고 싶다면, **`llm_structured.py` 내부만 수정**한다.
- `independence_service` 등 호출부는 `chat_completion_structured(...)` 시그니처를 유지하면 되므로 수정 불필요.

---

## 2. 확장성 — 신규 구조적 엔드포인트 추가

1. **Pydantic 모델** 정의 (`backend/models/`).
2. **프롬프트** 작성 (시스템/유저 메시지, “Output only valid JSON ...” 등 구조 명시).
3. **서비스**에서 `_get_openai_client()`(또는 설정에서 클라이언트 획득) 후 `chat_completion_structured(client, model=..., messages=..., temperature=..., response_model=YourModel)` 호출.
4. **라우터**에서 해당 서비스만 호출하고 응답 반환.

`independence_service`의 `extract_relationships` / `analyze_independence` 패턴을 그대로 재사용하면 됨.

---

## 3. 일관성 체크리스트

| 항목 | 기준 |
|------|------|
| **OpenAI 클라이언트** | API 키는 `get_settings().openai_api_key`에서만 취득. 서비스별로 동일 패턴. |
| **재시도** | 구조적 출력 호출은 `llm_structured.call_with_retry`(또는 `chat_completion_structured` 내부)로 통일. |
| **JSON 파싱** | LLM 응답 문자열 → `parse_json_content()` → `Model.model_validate()`. 마크다운 코드블록 제거는 공통 유틸만 사용. |
| **에러 메시지** | 라우터에서 `_normalize_error_detail(e)` 등으로 사용자 노출 메시지 일원화 (independence 라우터 참고). |

---

## 4. 법령 URL 레지스트리 (단일 소스·확장성)

### 4.1 역할

- **근거 법령** 링크는 **법령검색목록.csv**와 공식 URL 규칙 한 곳에서만 관리한다.
- **사용처**: `independence_service._enrich_legal_ref_urls()` → `law_registry.get_law_url(law_name)` 호출.

### 4.2 규칙

| 항목 | 기준 |
|------|------|
| **소스** | `backend/utils/law_registry.py` — CSV 로드, 법령명 정규화, URL 생성 |
| **URL 형식** | `https://www.law.go.kr/LSW/lsInfoP.do?lsiSeq={법령MST}` (공식 쿼리, docs/법령검색목록-URL-검토.md) |
| **CSV 경로** | `get_settings().law_csv_path` 또는 기본값 `프로젝트루트/법령검색목록.csv` |
| **정규화** | LLM 출력("공인회계사법 제21조") → 조문 제거 후 CSV 법령명 매칭; 약칭은 `ALIASES`만 수정 |

### 4.3 유지보수·확장

- **법령 추가/변경**: CSV(`법령검색목록.csv`) 갱신. 코드 수정 없음.
- **약칭 추가**: `law_registry.ALIASES`에만 추가 (예: "외부감사법" → "주식회사 등의 외부감사에 관한 법률").
- **URL 규칙 변경**: `law_registry.LAW_GO_KR_BASE` 및 쿼리 형식만 수정. 호출부는 `get_law_url()` 시그니처 유지.

**일관성**: 법령 링크가 필요한 다른 서비스/API가 생기면 반드시 `law_registry.get_law_url()`를 사용한다. 서비스별 하드코딩 맵을 두지 않는다.

---

## 5. 문서 갱신

- OpenAI major 버전 업그레이드 또는 structured output 방식 변경 시, 이 문서와 `llm_structured.py` 상단 docstring을 함께 갱신할 것.
- 법령 URL 규칙·CSV 컬럼 변경 시 `docs/법령검색목록-URL-검토.md`와 `law_registry.py` docstring을 함께 갱신할 것.
