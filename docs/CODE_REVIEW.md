# CTO 코드 검토: Audit Chat

**검토 목적**: GitHub 복원 포인트로 저장하기 전 전반적인 코드 품질·보안·유지보수성 점검.  
**기술 스택**: Streamlit + FastAPI + Neo4j + Mermaid + LLM.

---

## 1. 아키텍처 및 구조

| 항목 | 평가 | 비고 |
|------|------|------|
| 관심사 분리 | ✅ 양호 | Backend(API/DB/LLM) ↔ Frontend(UI) 분리, `api_client`로 API 일원화 |
| 설정 관리 | ✅ 양호 | `pydantic-settings` + `.env`, `backend/config.py`에서 일괄 로드 |
| 라우팅 구조 | ✅ 양호 | `routers/` (health, chat, graph), 추가 엔드포인트 확장 용이 |
| 의존성 | ✅ 양호 | `requirements.txt` 버전 고정, venv + `scripts/setup_venv.sh`로 재현 가능 |

**권장**: 프로덕션 배포 시 설정을 환경별로 나누고 싶다면 `ENV=production` 등으로 분기하거나 별도 설정 파일을 두는 방안 검토.

---

## 2. 보안

| 항목 | 평가 | 조치 |
|------|------|------|
| 비밀값 | ✅ 양호 | `.env`에만 보관, `.gitignore`로 제외, `.env.example`로 템플릿 제공 |
| CORS | ✅ 적용됨 | `CORS_ORIGINS`(기본: localhost:8501, 127.0.0.1:8501). 프로덕션 시 `.env`에 도메인 추가 |
| API 입력 | ✅ 개선됨 | `ChatMessage.role`을 Literal로 제한, `ChatRequest.messages`에 `max_length=100` 적용 |
| Mermaid 출력 | ✅ 개선됨 | Neo4j 라벨의 공백·특수문자·따옴표 정리 후 사용해 삽입/파싱 오류 방지 |

**권장**: 나중에 인증이 필요해지면 FastAPI `Depends()` + JWT/OAuth 등으로 보호 레이어 추가.

---

## 3. 안정성 및 에러 처리

| 항목 | 평가 | 비고 |
|------|------|------|
| Neo4j | ✅ 양호 | `get_neo4j_session()` 컨텍스트 매니저로 세션 정리, `verify_connection()`으로 헬스체크 |
| LLM | ✅ 양호 | API 키 없을 때 안내 메시지 반환, 예외 시 메시지로 반환해 500 과다 노출 방지 |
| Lifespan | ✅ 양호 | FastAPI lifespan에서 `Neo4jDriver.close()` 호출 |
| 프론트 채팅 | ✅ 양호 | API 실패 시 사용자 메시지 1건만 `pop()`하여 히스토리 일관성 유지 |

**권장**: 운영 환경에서는 구조화 로깅(`structlog` 등)과 슬로우 쿼리/타임아웃 모니터링 도입 검토.

---

## 4. 유지보수성

| 항목 | 평가 | 비고 |
|------|------|------|
| 타입/스키마 | ✅ 양호 | Pydantic 스키마로 요청/응답 정의, `Literal`로 role 제한 |
| 코드 위치 | ✅ 양호 | 라우터는 얇게, 비즈니스 로직은 `services/`, 스키마는 `models/`에 분리 |
| 문서화 | ✅ 양호 | README, 가상환경 절차, GitHub 복원 포인트 체크리스트 정리 |
| 실행 경로 | ✅ 양호 | `run.sh`에서 venv 자동 사용, `make venv`/`make run`으로 일관 실행 |

**권장**: 추후 테스트 추가 시 `tests/`에 단위·통합 테스트 두고, CI에서 `make venv` 후 `pytest` 실행 구성.

---

## 5. 이번 검토에서 반영한 수정 사항

1. **`backend/routers/graph.py`**  
   - Neo4j 라벨을 Mermaid 노드 ID/라벨로 쓸 때 공백·특수문자·따옴표 정리 (`_mermaid_safe_id`, 표시용 이스케이프).  
   - 빈 그래프/노드 라벨에 대한 처리 보강.

2. **`backend/models/schemas.py`**  
   - `ChatMessage.role`: `str` → `Literal["user","assistant","system"]`.  
   - `ChatRequest.messages`: `max_length=100` 설정으로 과도한 메시지 수 제한.

3. **`README.md`**  
   - GitHub 복원 포인트용 섹션 추가.  
   - 푸시 전 체크리스트(.env 미커밋, 비밀값 확인, 로컬 실행 확인) 및 예시 명령 정리.

4. **`docs/CODE_REVIEW.md`**  
   - 본 검토 문서 추가. 이후 변경 시 여기에 “검토 일자·변경 요약”만 추가해도 추적 가능.

---

## 6. GitHub 저장 전 최종 확인

- [ ] `git status`에 `.env`, `venv/` 포함 여부 확인
- [ ] 코드/README에 API 키·DB 비밀번호 등 비밀값 없음 확인
- [ ] 로컬에서 `make venv` → `./run.sh` 한 번 실행해 동작 확인
- [ ] 원하면 이 시점 태그 생성: `git tag restore-point-2025-02-12`

이 상태를 기준으로 푸시하면, 이후 작업이 꼬였을 때 이 커밋/태그로 복원하기 좋다.
