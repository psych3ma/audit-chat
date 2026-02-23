# 포트폴리오용 코드 정리 — CTO 검토

**검토 관점**: 확장성, 유지보수성, 협업·코드 품질  
**목적**: 코드 실행에 불필요한 파일·주석 정리, 공식 문서 위주 구성

---

## 1. 실행에 필수인 항목

| 구분 | 경로 | 비고 |
|------|------|------|
| 백엔드 | `backend/` | FastAPI, 라우터, 서비스, 모델, utils |
| 프론트엔드 | `frontend/`, `static/` | Streamlit 앱, PwC HTML UI |
| 설정 | `requirements.txt`, `.env.example`, `.python-version` | 의존성·환경 템플릿 |
| 실행 | `run.sh`, `run_static_only.py` | 앱 실행 진입점 |
| 스크립트 | `scripts/setup_venv.sh`, `scripts/kill_ports.sh` | 가상환경·포트 정리 |

**참고**: `.env`는 로컬 전용·미커밋(.gitignore). 실행 시 `.env.example`을 복사해 사용.

---

## 2. 실행에 불필요한 파일 (정리 대상)

### 2.1 문서 — 내부 검토·일회성 (archive 권장)

코드 실행·빌드와 무관한 내부 리뷰·요청서. `docs/archive/`로 이동 시 포트폴리오는 공식 문서만 유지.

| 파일 | 사유 |
|------|------|
| `CTO_REVIEW_REQUEST_FAILURE.md` | 검토 요청 실패 원인 분석 (내부) |
| `CTO_SCENARIO_CHIP_CONSISTENCY_REVIEW.md` | 시나리오 칩 일관성 검토 |
| `CTO_NEO4J_QUERY_REVIEW.md` | Neo4j 쿼리 검토 |
| `CTO_PHASE1_COST_ANALYSIS.md` | 비용 분석 |
| `CTO_LAW_JSON_STORAGE_REVIEW.md` | 법령 JSON 저장 검토 |
| `CTO_PRE_COMMIT_REVIEW.md` | pre-commit 검토 |
| `CTO_REVIEW_CHIP_TEXT_TRUNCATION.md` | 칩 말줄임 검토 |
| `CTO_REVIEW_PROGRESS_BUBBLE_TEXT.md` | 프로그레스 버블 검토 |
| `CTO_REVIEW_SKELETON_COLOR.md` | 스켈레톤 색상 검토 |
| `CTO_REVIEW_SHIMMER_EFFECT.md` | Shimmer 효과 검토 |
| `CTO_PROGRESSIVE_RENDERING.md` | 점진적 렌더링 검토 |
| `CTO_REVIEW_LOADING_STATE.md` | 로딩 상태 검토 |
| `CTO_REVIEW_UX_MINIMAL_APPROACH.md` | UX 미니멀 검토 |
| `CTO_REVIEW_LOGO_CLICK.md` | 로고 클릭 검토 |
| `CTO_EMPTY_STATE_LAYOUT_REVIEW.md` | Empty state 레이아웃 검토 |
| `CTO_TYPOGRAPHY_REVIEW.md` | 타이포그래피 검토 |
| `CTO_REVIEW.md` | CTO 종합 리뷰 (요약본은 README 등에 반영 가능) |
| `DESIGNER_REVIEW_SKELETON_COLOR.md` | 디자이너 스켈레톤 색상 |
| `DESIGNER_REVIEW_SKELETON_UI.md` | 디자이너 스켈레톤 UI |
| `UX_REVIEW_LOADING_STATE.md` | UX 로딩 상태 |
| `UX_REVIEW_LOGO_INTERACTION.md` | UX 로고 상호작용 |
| `UX_REVIEW_PROGRESS.md` | UX 프로그레스 |
| `UX_TYPOGRAPHY_ANALYSIS.md` | UX 타이포 분석 |
| `UX_LAYOUT_COMPREHENSIVE_REVIEW.md` | UX 레이아웃 종합 |
| `UX_SPACING_TITLE_CHIPS.md` | UX 간격 검토 |
| `UX-copy-review-request.md` | UX 카피 수정 요청 |
| `DESIGN_EMPTY_STATE_LAYOUT_FIX.md` | Empty state 수정 |
| `DESIGN_EMPTY_STATE_LAYOUT_FIX_V2.md` | Empty state 수정 v2 |
| `COPY_ALTERNATIVES_EMPTY_STATE.md` | Empty state 카피 대안 |
| `CODE_REVIEW_CTO.md` | 코드 리뷰 (내부) |
| `AI_EXPERT_ARCHITECTURE_REVIEW.md` | AI 아키텍처 리뷰 |
| `GENAI_EXPERT_COST_ACCURACY_REVIEW.md` | GenAI 비용·정확도 |
| `GENAI_EXPERT_FLOW_REVIEW.md` | GenAI 플로우 리뷰 |
| `GENAI_EXPERT_ARCHITECTURE_REVIEW.md` | GenAI 아키텍처 |
| `GENAI_INDEPENDENCE_REVIEW.md` | GenAI 독립성 검토 (기능 설명은 ARCHITECTURE에 통합 가능) |
| `UI_PROTOTYPE_REVIEW.md` | UI 프로토타입 검토 |
| `IMPACT_WORKFLOW_PROGRESS.md` | 워크플로우 영향 (WORKFLOW_* 와 중복 가능) |
| `COMMIT_GUIDE.md` | 커밋 가이드 (CONTRIBUTING에 통합 권장) |
| `법령검색목록-URL-검토.md` | 법령 URL 검토 (내부) |
| `DESIGN_QA_회계법인제출용.md` | 제출용 디자인 QA (포트폴리오 시 유지 여부 선택) |

### 2.2 문서 — 유지 (공식·코드 참조)

| 파일 | 사유 |
|------|------|
| `docs/README.md` | 문서 인덱스 |
| `docs/ARCHITECTURE.md` | 시스템 아키텍처 (공식) |
| `docs/CONTRIBUTING.md` | 기여·Git 가이드 (공식) |
| `docs/WORKFLOW_STEP_CODE_MAPPING.md` | 코드에서 참조 (`backend/routers/independence.py`, `independence_service.py`, `audit-chat-pwc.html`) |
| `docs/WORKFLOW_3STEPS.md` | 3단계 워크플로우 설명 |
| `docs/DESIGN_PROGRESS_HANDOFF.md` | 프로그레스 UI handoff (HTML 주석 참조) |
| `docs/RELATIONSHIP_PROPERTIES_METADATA.md` | 관계·메타데이터 (Neo4j/독립성 검토 참고) |
| `docs/STEP1_STEP2_STATUS.md` | Step1/Step2 구현 상태 (기술 문서) |
| `docs/NEO4J_FALLBACK_EXPLANATION.md` | Neo4j 폴백 동작 설명 |
| `docs/TEST_RESULTS_NEO4J_QUERY.md` | Neo4j 쿼리 테스트 결과 |
| `docs/NEO4J_USAGE_ANALYSIS.md` | Neo4j 사용 분석 |
| `docs/CHAT_CONTEXT_INTEGRATION.md` | 채팅 컨텍스트 연동 |
| `docs/LAW_HTML_INTEGRATION_REVIEW.md` | 법령 HTML 연동 검토 |
| `docs/ERExtractionTemplate_VS_EntityRelationExtractor.md` | 추출 템플릿 비교 |
| `docs/TYPOGRAPHY_STANDARDIZATION.md` | 타이포 표준화 |
| `docs/PORTFOLIO_CLEANUP.md` | 본 정리 문서 |

### 2.3 데이터·기타

| 경로 | 사유 |
|------|------|
| `data/law/html/*.html` | 법령 원문 HTML. 실행 시 사용 안 함 (`law_registry`는 `법령검색목록.csv` 사용). 포트폴리오 최소화 시 삭제·별도 보관 가능. |
| `scripts/git-hooks/commit-msg` | Git 훅. 협업 시 유용, 단일 개발 포트폴리오에서는 선택. |

---

## 3. 정리할 주석 (선택)

- **유지 권장**: 설정·SSOT·API 진입점 설명, `docs/...` 참조. (예: `API_BASE_URL`, `WORKFLOW_STEP_CODE_MAPPING.md` 참조)
- **정리 권장**: 과도한 인라인 설명(이미 코드로 드러나는 내용), 내부용 TODO/FIXME, “레거시 호환” 등 반복 문구는 한 곳으로 모으면 유지보수에 유리.

### 3.1 `static/audit-chat-pwc.html`

| 위치(대략) | 내용 | 권장 |
|------------|------|------|
| CSS 변수 주석 | `/* 레거시 호환 */` 반복 | 필요 시 한 곳에만 “레거시 별칭” 설명 |
| 칩/스켈레톤 | “칩 내부 구조 반영”, “Shimmer 효과는 배경에만” 등 | 요약해 블록 단위 1개로 통합 가능 |
| JS 상단 | `CTO 검토 — 설정 및 운영` 등 | “API·워크플로우 설정” 수준으로 짧게 유지 |
| `d.text /* shortText → text */` | 이미 SSOT 정리됨 | 유지 |

### 3.2 `backend/`

- 모듈·클래스 docstring: “공식” 한 줄 + 필요 시 `docs/...` 참조만 두면 충분.
- `# urllib.parse.quote 제거 - law.go.kr...` 등 구현 이유는 한 줄로 유지해도 무방.

---

## 4. 정리 결과 (적용 시)

- **docs/archive/** 에 2.1 목록 이동 → 실행·빌드 불변, 포트폴리오는 공식 문서만 노출.
- **docs/README.md** → archive 안내 추가, “공식 문서 위주” 구조로 수정.
- **data/law/html** → 삭제하지 않고 README에 “참조용 데이터, 최소 배포 시 제외 가능” 명시만 해도 됨.
- 주석은 3절 권장에 따라 최소한만 정리해 확장성·유지보수성 유지.

이 문서는 포트폴리오용 정리의 공식 기준으로 사용할 수 있음.
