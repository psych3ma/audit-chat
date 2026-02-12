# CTO 관점 — GitHub 체크포인트 전 검토

체크포인트(커밋/푸시) 직전 CTO 관점에서의 요약 검토입니다.  
*(최종 갱신: 독립성 검토·법령 레지스트리·GenAI 프롬프트 보강 반영)*

---

## 1. 보안 (필수 확인)

### 1.1 비밀값·환경 파일
| 항목 | 상태 | 비고 |
|------|------|------|
| `.env` in `.gitignore` | ✅ | `.gitignore:30` 에 `.env` 존재 |
| `git check-ignore .env` | ✅ | 정상 무시됨 |
| **푸시 전 확인** | **필수** | 아래 명령으로 한 번 더 확인 |

```bash
git status
# → .env, venv/ 가 목록에 없어야 함. 있으면:
git rm --cached .env
git commit -m "chore: remove .env from tracking"
```

- **절대 커밋하면 안 되는 것**: `.env`, `venv/`, `.env.local`, `*.log`, `.streamlit/secrets.toml`
- **로컬 `.env`** 에는 실제 API 키·DB 비밀번호·**LAW_GO_KR_OC**(국가법령정보센터 API 키) 등이 있으므로, 이 파일은 **절대** 커밋하지 마세요.
- **과거에 .env를 한 번이라도 커밋했다면**: 해당 저장소에서 키 노출 이력이 있으므로, **OPENAI_API_KEY**, **NEO4J_PASSWORD**, **LAW_GO_KR_OC** 재발급·변경 권장.

### 1.2 설정 관리
- 비밀값은 모두 `backend/config.py` → `.env` 로 일원화. 코드에 하드코딩 없음.
- `.env.example` 에는 플레이스홀더만 있고 실제 키 없음.

---

## 2. 구조·품질

| 영역 | 평가 | 비고 |
|------|------|------|
| **아키텍처** | ✅ | Backend(FastAPI) / Frontend(Streamlit) / Static(HTML) 분리, 라우터·서비스·모델 구조 |
| **설정** | ✅ | `pydantic-settings` + `.env`, `get_settings()` 일관 사용. LAW_GO_KR_OC, law_csv_path 포함 |
| **API** | ✅ | `/health`, `/ready`, `/independence/review`, `/pwc` 등. 독립성 검토 → 엔티티/관계 추출 → 분석 → 법령 URL 보강 |
| **정적 UI** | ✅ | `audit-chat-pwc.html` — 감사 독립성 검토, 관계도(Mermaid)·보고서·근거 법령 링크 |
| **법령 URL** | ✅ | `backend/utils/law_registry.py` 단일 소스, CSV(법령검색목록.csv) 기반, 조문 링크(한글 경로) 지원 |
| **문서** | ✅ | README, PRE_PUSH_CHECKLIST, CTO_MAINTENANCE, 법령검색목록-URL-검토, GENAI_INDEPENDENCE_REVIEW 등 |
| **TODO/FIXME** | ✅ | Python 코드에 미등록 이슈 없음 |

---

## 3. 의존성

- **requirements.txt**: 버전 고정으로 재현성 확보.
- **주의**: `streamlit==1.29.0`, `langchain==0.1.9` 등 구버전 — 추후 보안/기능 필요 시 업그레이드 계획만 문서에 남겨두면 됨.

---

## 4. 알려진 이슈·레거시

- **internal-control.html**: 레거시. 현재 없음. Root(/)는 `audit-chat-pwc.html` 로 리다이렉트하도록 정리됨. (참고: `docs/LEGACY-internal-control.md`)
- **.env.example**: 기본 포트가 8000/8501. 실제 로컬은 8001/8502 사용 가능 — README나 주석에 “필요 시 API_PORT, STREAMLIT_PORT 변경” 안내 있으면 충분.

---

## 5. 체크포인트 전 최종 체크리스트

푸시 **직전**에 아래만 실행해 보세요.

```bash
# 1) .env 미포함 확인
git status
git check-ignore -v .env

# 2) 스테이징 후 다시 확인
git add .
git status
# .env, venv/ 여전히 없어야 함

# 3) (선택) 로컬 실행 한 번
./run.sh
# → http://localhost:8001/ , http://localhost:8502/ 동작 확인 후 Ctrl+C
```

---

## 6. CTO 결론

| 항목 | 판단 |
|------|------|
| **체크포인트 진행** | ✅ **진행 가능** — 구조·설정·문서·보안 설계 적절. |
| **필수 조건** | 푸시 전 `git status`로 `.env`·`venv/` 미포함 반드시 확인. |
| **권장** | `docs/PRE_PUSH_CHECKLIST.md` 순서대로 한 번 수행 후 푸시. |

커밋 메시지 예시:
```text
chore: CTO 검토 후 체크포인트 (감사 독립성 검토·법령 레지스트리·GenAI 프롬프트 보강)
```
