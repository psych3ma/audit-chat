# CTO 전문가 관점 — 프로젝트 검토

검토 일자 기준 전체 구조·보안·의존성·운영·기술 부채를 정리한 문서입니다.

---

## 1. 아키텍처·구조

| 항목 | 평가 | 비고 |
|------|------|------|
| **계층 분리** | ✅ 양호 | Backend(FastAPI) / Frontend(Streamlit) / Static(HTML) 명확히 분리 |
| **백엔드 구조** | ✅ 양호 | `routers/` → `services/` → `models/`, `config`·`database` 일원화 |
| **API 설계** | ✅ 양호 | `/health`, `/ready`, `/chat/completions`, `/independence/review`, `/graph/mermaid` 등 역할 분리 |
| **설정 관리** | ✅ 양호 | `pydantic-settings` + `.env`, `get_settings()` 캐시 사용 |
| **진입점** | ✅ 양호 | `main.py` lifespan에서 Neo4j 정리, CORS·정적 파일·리다이렉트 일괄 처리 |

**결론**: 확장·유지보수에 유리한 구조. 신규 라우트·서비스 추가 시 패턴만 따르면 됨.

---

## 2. 보안

| 항목 | 상태 | 권장 사항 |
|------|------|-----------|
| **비밀값** | ✅ | `.env`만 사용, `.gitignore`에 포함. 코드 내 하드코딩 없음. |
| **CORS** | ✅ | `cors_origins`로 제한. 프로덕션 배포 시 `.env`에 실제 도메인만 명시할 것. |
| **에러 노출** | ⚠️ | 500 시 `detail`로 메시지 반환 → 사용자 노출 가능. 프로덕션에서는 일반화 메시지 + 서버 로그에만 상세 기록 권장. |
| **입력 검증** | ✅ | Pydantic 스키마(`min_length`, `Literal` 등)로 요청 검증. |

**주의**: `.env.example`이 비어 있거나 훼손된 상태면 신규 환경 세팅 시 실수 가능. 템플릿(키 이름·주석) 복구 권장.

---

## 3. 의존성·라이브러리

| 항목 | 평가 | 조치 |
|------|------|------|
| **버전 고정** | ✅ | `requirements.txt` 버전 지정으로 재현성 확보. |
| **openai==1.12.0** | ✅ 대응 완료 | `beta.chat.completions.parse()` 미지원 → **구조적 출력은 `backend/services/llm_structured.py`에서 create + json_object + Pydantic 검증으로 통일.** |
| **미사용 패키지** | ⚠️ | `langchain`, `langchain-openai`, `requests` 사용처 없음. 제거 시 의존성·설치 시간 감소. |
| **구버전** | ⚠️ | streamlit 1.29, fastapi 0.109 등. 보안·기능 필요 시 단계적 업그레이드 계획 권장. |

**구조적 출력 정책** (유지보수·확장성·일관성):

- **단일 추상화**: 모든 구조적 LLM 응답은 `llm_structured.chat_completion_structured()` 사용. SDK/API 변경 시 해당 모듈만 수정.
- **상세**: `docs/CTO_MAINTENANCE.md` 참고.

---

## 4. 운영·배포

| 항목 | 상태 | 비고 |
|------|------|------|
| **헬스체크** | ✅ | `/health`(Neo4j 포함), `/ready`(run.sh 대기용) 제공. |
| **실행 스크립트** | ✅ | `run.sh`(백엔드+프론트 동시 기동), `scripts/kill_ports.sh`, `Makefile`(venv/install/run/clean). |
| **Neo4j** | ✅ | `docker-compose.yml`로 로컬 Neo4j 구성 가능. Neo4j 실패 시 독립성 검토는 Neo4j 저장만 스킵하고 API는 동작하도록 처리됨. |
| **로그·모니터링** | ⚠️ | 구조화된 로깅·메트릭 미도입. 프로덕션 전에 `log_level`, 요청/에러 로그, (선택) 메트릭 엔드포인트 도입 권장. |

---

## 5. 기술 부채·리스크

| 우선순위 | 내용 | 영향 |
|----------|------|------|
| ~~**P0**~~ | ~~독립성 검토: beta.parse → 1.12 호환~~ | ✅ `llm_structured` 도입으로 해결 |
| **P1** | `.env.example` 복구 | 온보딩·배포 시 설정 누락 위험 |
| **P2** | 미사용 의존성 제거(langchain, langchain-openai, requests) | 혼란·불필요 설치 감소 |
| **P2** | `backend/utils/` 빈 패키지 삭제 또는 실제 유틸 사용 | 레포 정리 (선택) |
| **P3** | 500 에러 시 프로덕션용 일반화 메시지 + 로그 분리 | 보안·UX |

---

## 6. 문서·온보딩

| 항목 | 상태 |
|------|------|
| **README** | ✅ 아키텍처, Makefile, 빠른 시작, 기술 스택 정리됨. |
| **docs/** | ✅ CODE_REVIEW, CTO_CHECKPOINT_REVIEW, PRE_PUSH_CHECKLIST, LEGACY 등으로 의사결정·체크리스트 남음. |
| **.env.example** | ❌ 현재 비어 있음. 최소한 변수 목록·주석 복구 권장. |

---

## 7. CTO 결론 및 권장 순서

- **전체**: 아키텍처·보안 설계·설정 일원화는 양호. **독립성 검토 API**가 현재 라이브러리 버전과 맞지 않아 500이 발생하는 것이 가장 큰 이슈.
- **즉시**: `independence_service`에서 OpenAI 호출을 **openai 1.12에서 지원하는 방식**으로 변경 (A안 또는 B안).
- **단기**: `.env.example` 복구, (선택) 미사용 의존성·빈 패키지 정리.
- **중기**: 프로덕션 배포 시 에러 메시지 정책, 로깅·모니터링, CORS·환경별 설정 점검.

이 문서는 `docs/CTO_EXPERT_REVIEW.md`로 두고, 위 조치 반영 시 검토 일자·P0/P1 처리 여부만 갱신해도 됨.
