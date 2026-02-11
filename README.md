# Audit Chat Application

Streamlit + FastAPI + Neo4j + Mermaid + LLM 기반 웹 애플리케이션

## CTO 관점 검토 요약

- **관심사 분리**: Backend(FastAPI/Neo4j/LLM) ↔ Frontend(Streamlit/UI) 분리, `api_client`로 API 통신 일원화
- **설정**: `pydantic-settings` + `.env` 기반 설정, `config.get_settings()`로 일관된 접근
- **확장성**: `routers/`, `services/`, `models/` 구조로 엔드포인트·비즈니스 로직·스키마 추가 용이
- **운영**: 헬스체크(`/health`), CORS 설정, Lifespan에서 Neo4j 드라이버 정리
- **보안**: 비밀값은 `.env`에만 두고 `.gitignore`로 제외, `.env.example`로 템플릿 제공

## 아키텍처

```
audit-chat/
├── backend/          # FastAPI 백엔드
│   ├── main.py
│   ├── database.py
│   ├── models/
│   ├── routers/
│   ├── services/
│   └── utils/
├── frontend/         # Streamlit 프론트엔드
│   ├── app.py
│   ├── api_client.py
│   ├── components/
│   └── pages/
├── .env.example
├── .env                 # 로컬만 사용, 미커밋 (.gitignore)
├── requirements.txt
├── run.sh
├── Makefile              # make venv | install | run | clean
├── .python-version       # 권장 Python 버전 (pyenv 등)
└── scripts/
    └── setup_venv.sh     # 가상환경 일괄 설정
```

## 가상환경 (CTO 권장)

- **Python**: 3.9+ (권장 3.11, `.python-version` 참고)
- **한 번에 설정**: 스크립트가 venv 생성 + 버전 검사 + 의존성 설치 + import 검증까지 수행

```bash
# 방법 1: 스크립트로 일괄 설정 (권장)
chmod +x scripts/setup_venv.sh
./scripts/setup_venv.sh
# 또는 특정 인터프리터: ./scripts/setup_venv.sh python3.11

# 방법 2: Makefile
make venv
```

활성화 후 실행:

```bash
source venv/bin/activate   # Windows: venv\Scripts\activate
cp .env.example .env       # 최초 1회, 필요 시 편집
./run.sh                   # 또는 make run
```

| Makefile 타깃 | 설명 |
|---------------|------|
| `make venv`   | 가상환경 생성 + 의존성 설치 |
| `make install`| 이미 있는 venv에 의존성만 설치 |
| `make run`    | 백엔드+프론트 실행 |
| `make clean`  | venv 및 캐시 삭제 |

## 빠른 시작

```bash
make venv
source venv/bin/activate
cp .env.example .env
./run.sh
```

## 기술 스택

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: Neo4j
- **Visualization**: Mermaid
- **AI**: LLM

---

## GitHub 저장 (복원 포인트)

이 상태를 **복원 포인트**로 두고 이후 작업이 꼬이면 이 커밋으로 돌아올 수 있도록 푸시할 수 있다.

### 푸시 전 체크리스트

| 확인 항목 | 명령/조치 |
|-----------|-----------|
| `.env` 미커밋 | `git status`에 `.env`가 없어야 함. 있으면 `git rm --cached .env` 후 커밋 |
| 비밀값 없음 | `OPENAI_API_KEY`, `NEO4J_PASSWORD` 등이 코드/README에 없어야 함 |
| 동작 확인 | `make venv` → `./run.sh` 후 로컬에서 한 번 실행해 보기 |

```bash
git init
git add .
git status   # .env, venv/ 이 포함되지 않았는지 확인
git commit -m "chore: CTO 검토 후 복원 포인트 (Streamlit+FastAPI+Neo4j+Mermaid+LLM)"
git remote add origin <your-repo-url>
git push -u origin main
```

상세 코드 검토 내용은 **`docs/CODE_REVIEW.md`** 참고.

### Cursor에서 커밋 시 "공동협업(Cursor AI)" 트레일러 제거

Cursor가 커밋 메시지에 자동으로 넣는 `Co-authored-by: Cursor …` 를 빼고 싶다면, **최초 1회**:

```bash
cp scripts/git-hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

설치 후 Cursor에서 커밋해도 해당 트레일러는 저장 전에 제거됩니다.
