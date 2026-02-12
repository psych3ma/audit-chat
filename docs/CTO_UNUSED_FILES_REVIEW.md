# CTO 관점 — 미사용·불필요 파일 검토

프로젝트 내 **사용되지 않거나 불필요한 파일·패키지·의존성**을 CTO 관점에서 정리했습니다.

---

## 1. 삭제/정리 권장 (Unused)

### 1.1 빈 패키지 — `backend/utils/`
| 항목 | 내용 |
|------|------|
| **위치** | `backend/utils/` (파일: `__init__.py` 만 존재, 내용은 `# Utils package`) |
| **사용처** | 없음. 코드베이스 어디에서도 `backend.utils` 또는 `from backend.utils` import 없음. |
| **권장** | **삭제 권장.** 공통 유틸이 생기면 그때 다시 `backend/utils/` 생성해도 됨. |

```bash
# 삭제 시
rm -rf backend/utils
```

---

### 1.2 미사용 의존성 — `requirements.txt`

| 패키지 | 용도 | 사용 여부 | 권장 |
|--------|------|-----------|------|
| **langchain** | LLM 체인/래퍼 | ❌ 코드에서 import/사용 없음 | 제거 권장 |
| **langchain-openai** | LangChain OpenAI 연동 | ❌ 사용 없음 | 제거 권장 |
| **requests** | HTTP 클라이언트 | ❌ 사용 없음 (프로젝트는 `httpx`만 사용) | 제거 권장 |

- **유지해도 되는 경우**: 곧 LangChain 기반 기능을 도입할 예정이면 그때까지 남겨둘 수 있음.  
- **정리 시**: 위 세 줄을 `requirements.txt`에서 제거 후 `pip install -r requirements.txt`로 재설치·동작 확인.

---

## 2. 선택적 정리 (Optional)

### 2.1 문서 — `docs/UI_PROTOTYPE_REVIEW.md`
| 항목 | 내용 |
|------|------|
| **내용** | **audit-chat-prototype.html** 에 대한 UI 검토 (다크 톤, 시나리오 칩, 목업 동작 등). |
| **현재 저장소** | `audit-chat-prototype.html` 파일 **없음**. `static/`에는 `audit-chat-pwc.html` 만 존재. |
| **권장** | 프로토타입 이력·설계 참고용으로 보관해도 됨. **레거시 문서로 간주하고 정리(삭제 또는 `docs/archive/` 이동)** 해도 무방. |

---

### 2.2 서비스 패키지 re-export — `backend/services/__init__.py`
| 항목 | 내용 |
|------|------|
| **내용** | `from backend.services.llm_service import get_llm_response` 만 re-export. |
| **사용처** | `backend/routers/chat.py` 는 `from backend.services.llm_service import get_llm_response` 로 **직접** import. `from backend.services import ...` 사용처 없음. |
| **권장** | 유지해도 무해. 나중에 `from backend.services import get_llm_response, run_independence_review` 형태로 통일하고 싶다면 그때 `__init__.py`에 추가하면 됨. **삭제 필수 아님.** |

---

## 3. 유지 권장 (참고용·필수)

| 항목 | 비고 |
|------|------|
| **docs/CODE_REVIEW.md** | 전반 코드 품질·보안 검토. 유지 권장. |
| **docs/LEGACY-internal-control.md** | `internal-control.html` 레거시 설명. main.py의 `/` 리다이렉트 로직 이해에 유용. 유지 권장. |
| **docs/PRE_PUSH_CHECKLIST.md** | 푸시 전 체크리스트. 유지 권장. |
| **docs/CTO_CHECKPOINT_REVIEW.md** | 체크포인트 전 CTO 검토. 유지 권장. |
| **scripts/git-hooks/commit-msg** | 선택 설치 훅. 문서화된 용도 있음. 유지 권장. |
| **scripts/kill_ports.sh, setup_venv.sh** | run.sh·Makefile에서 사용. 필수. |
| **Makefile, docker-compose.yml, .env.example** | 빌드·실행·설정 템플릿. 필수. |

---

## 4. 요약 액션

| 우선순위 | 액션 | 위험도 |
|----------|------|--------|
| 1 | **backend/utils/** 삭제 (빈 패키지) | 낮음 |
| 2 | **requirements.txt** 에서 `langchain`, `langchain-openai`, `requests` 제거 (미사용 의존성) | 낮음 (제거 후 `pip install -r requirements.txt` 및 실행 테스트 권장) |
| 3 | **docs/UI_PROTOTYPE_REVIEW.md** — 보관 vs 삭제/archive 는 팀 정책에 따라 결정 | 없음 |

위 1·2 반영 후 `./run.sh` 및 Streamlit/API/Neo4j 동작을 한 번씩 확인하면 됩니다.
