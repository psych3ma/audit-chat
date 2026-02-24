# Audit Chat — 감사 독립성 검토 AI

**감사 시나리오**를 넣으면 인물·회사·관계를 분석하고, **수임 가능 여부와 위험도**를 정리해 주는 웹 앱입니다.  
(Streamlit·FastAPI·Neo4j·LLM 기반)

---

## 이 앱으로 할 수 있는 것

- 시나리오 텍스트 입력 → 관계 추출 → 독립성 분석 → **결론·관계도·법령 링크**가 담긴 리포트 확인
- PwC 스타일 UI(`/` 또는 `/static/audit-chat-pwc.html`)에서 예시 시나리오로 바로 체험 가능  
  (이 UI는 **백엔드(예: 8001)** 에서만 제공됩니다. Streamlit(8502)에서는 안 뜨므로, Streamlit 홈의 "감사 독립성 UI 열기" 링크나 `http://localhost:8001/` 로 접속하세요.)

---

## 실행 방법 (공통)

1. **Python 3.9+** (권장 3.11) 설치 후, 프로젝트 폴더에서 터미널을 연다.
2. **최초 1회만** 환경 준비:
   ```bash
   make venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   cp .env.example .env       # 필요 시 .env 안에 API 키·DB 주소 등 편집
   ```
3. **실행**:
   ```bash
   ./run.sh
   ```
4. 브라우저에서 **백엔드**: `http://localhost:8000` (또는 `.env`의 `API_PORT`), **API 문서**: `/docs`  
   (Streamlit 프론트는 `http://localhost:8501` 등으로 안내됨)

**Neo4j 없이 화면만 보고 싶을 때**: `python run_static_only.py` → 동일 포트로 HTML만 제공 (검토 API는 동작하지 않음).

**"검토 요청 연결에 실패했습니다. Not Found"가 나올 때**: 지금 연 페이지가 **정적 전용 서버**라서 검토 API가 없음.  
→ **해결 1**: `./run.sh` 실행 후 **http://localhost:8001** (또는 `.env`의 `API_PORT`) 로 접속.  
→ **해결 2**: 백엔드를 8001에서 따로 띄운 뒤, 정적 서버로 연 경우 주소에 **`?api=http://localhost:8001`** 를 붙여서 다시 열기 (예: `http://localhost:9090?api=http://localhost:8001`).

---

## 아키텍처 (구성 원칙)

- **역할 분리**: 사용자가 보는 **화면(프론트)** 과 **계산·저장을 맡는 서버(백엔드)** 를 나눠 두어, 화면 변경과 분석 로직 변경을 서로 덜 건드리게 했습니다.
- **데이터 흐름**:  
  **시나리오 입력** → **프론트(HTML/Streamlit)** → **백엔드 API** → **관계 추출·독립성 분석(LLM)** + **관계 저장(Neo4j)** → **리포트·관계도(Mermaid)** 로 돌려줌.
- **확장·협업**: 새 기능은 API 경로와 서비스만 추가하면 되고, 프론트/백엔드/DB를 다른 팀이 나눠 담당하기 쉽게 구성했습니다. 상세 다이어그램·레이어 설명은 **`docs/ARCHITECTURE.md`** 참고.

---

## 프로젝트 구조 (요약)

| 구분 | 폴더/파일 | 설명 |
|------|------------|------|
| 백엔드 | `backend/` | API·DB·분석 로직 (FastAPI) |
| 프론트 | `frontend/`, `static/` | Streamlit 앱, PwC 감사 독립성 HTML UI |
| 설정 | `.env.example`, `requirements.txt` | 환경 변수 예시, 패키지 목록 |
| 실행 | `run.sh`, `run_static_only.py` | 전체 앱 실행 / 정적 UI만 실행 |

상세 구조·아키텍처는 **`docs/ARCHITECTURE.md`** 참고.

---

## 기술 스택

| 역할 | 기술 |
|------|------|
| 화면·입력 | Streamlit, HTML(정적 UI) |
| API·서버 | FastAPI |
| DB·관계 저장 | Neo4j |
| 관계도 시각화 | Mermaid |
| 분석·요약 | LLM (OpenAI 등) |

---

## 개발·운영 참고

- **설정**: 비밀값·DB 주소는 `.env`에만 두고, 저장소에는 올리지 않음 (`.gitignore`). 새 환경은 `.env.example`을 복사해 사용.
- **문서**: `docs/ARCHITECTURE.md` (시스템 구성·API·모듈 설명).
- **Git 푸시 전**: `git status`로 `.env`·`venv/`가 포함되지 않았는지 확인. API 키·DB 비밀번호가 코드·README에 없어야 함.
- **커밋 메시지**: Cursor 사용 시 `Co-authored-by` 제거가 필요하면 `scripts/git-hooks/commit-msg`를 `.git/hooks/`에 복사해 사용.
