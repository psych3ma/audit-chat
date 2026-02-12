# CTO 코드 리뷰 리포트

> 검토일: 2026-02-12  
> 검토 범위: Backend (Python), Frontend (HTML/CSS/JS)  
> 관점: 하드코딩, 확장성, 유지보수성, 협업

---

## 📊 요약

| 카테고리 | Backend | Frontend | 총계 |
|---------|---------|----------|------|
| 하드코딩 | 10 | 7 | 17 |
| 확장성 | 5 | 3 | 8 |
| 유지보수 | 6 | 5 | 11 |
| 협업/문서화 | 7 | 4 | 11 |
| **총계** | **28** | **19** | **47** |

---

## 🔴 P0: Critical (즉시 수정)

### 1. Magic Numbers 하드코딩

#### Backend
| 파일 | 라인 | 현재 | 권장 |
|------|------|------|------|
| `services/independence_service.py` | 144 | `[:20]` | `REL_TYPE_MAX_LENGTH = 20` |
| `services/independence_service.py` | 181 | `[:8]` | `TRACE_ID_LENGTH = 8` |
| `routers/graph.py` | 28 | `LIMIT 50` | `GRAPH_QUERY_LIMIT = 50` |
| `routers/graph.py` | 13 | `[:30]` | `MERMAID_NODE_ID_MAX_LENGTH = 30` |
| `routers/independence.py` | 21 | `[:500]` | `ERROR_MESSAGE_MAX_LENGTH = 500` |

#### Frontend
| 파일 | 라인 | 현재 | 권장 |
|------|------|------|------|
| `audit-chat-pwc.html` | 1180 | `120` (textarea height) | `TEXTAREA_MAX_HEIGHT = 120` |
| `audit-chat-pwc.html` | 1233 | `1800` (fallback delay) | `FALLBACK_DELAY_MS = 1800` |
| `audit-chat-pwc.html` | 1460 | `50` (scroll delay) | `SCROLL_DELAY_MS = 50` |

**수정 방안:**
```python
# backend/config.py 추가
class Settings(BaseSettings):
    # ... 기존 설정 ...
    
    # Limits
    rel_type_max_length: int = 20
    trace_id_length: int = 8
    graph_query_limit: int = 50
    mermaid_node_id_max_length: int = 30
    error_message_max_length: int = 500
```

---

### 2. 외부 서비스 URL 하드코딩

| 파일 | 라인 | URL | 용도 |
|------|------|-----|------|
| `utils/law_registry.py` | 17 | `https://www.law.go.kr` | 법령 조문 링크 |
| `utils/law_registry.py` | 19 | `https://www.law.go.kr/LSW/lsInfoP.do` | 법령 본문 링크 |
| `audit-chat-pwc.html` | 1276 | `https://mermaid.ink/img/` | Mermaid 다이어그램 |

**수정 방안:**
```python
# backend/config.py
law_go_kr_base_url: str = "https://www.law.go.kr"
law_go_kr_lsinfo_url: str = "https://www.law.go.kr/LSW/lsInfoP.do"

# .env.example
# LAW_GO_KR_BASE_URL=https://www.law.go.kr
# MERMAID_SERVICE_URL=https://mermaid.ink/img/
```

---

### 3. LLM 프롬프트 하드코딩

| 파일 | 라인 | 프롬프트 |
|------|------|---------|
| `services/independence_service.py` | 41-48 | `EXTRACTION_SYSTEM` |
| `services/independence_service.py` | 50-58 | `ANALYSIS_SYSTEM` |

**수정 방안:**
```
backend/
└── prompts/
    ├── extraction_system.txt
    └── analysis_system.txt
```

또는 `config.py`에 경로 설정:
```python
extraction_prompt_path: str = "prompts/extraction_system.txt"
analysis_prompt_path: str = "prompts/analysis_system.txt"
```

---

## 🟡 P1: High (단기 개선)

### 4. Frontend 단일 파일 구조

**현재:**
```
static/audit-chat-pwc.html (1,473줄)
```

**권장:**
```
static/
├── audit-chat.html          # HTML 구조만
├── css/
│   └── audit-chat.css       # 스타일
└── js/
    ├── config.js            # 상수/설정
    ├── i18n.js              # 다국어 텍스트
    ├── scenarios.js         # 시나리오 데이터
    └── app.js               # 비즈니스 로직
```

**영향:** 협업 시 충돌 감소, 코드 리뷰 용이

---

### 5. i18n (다국어) 미지원

**현재:** 30+ 개소에 한국어 하드코딩
```javascript
// 산재된 한국어 문자열
'감사 독립성 검토 AI'
'수임 불가'
'관계도 로드 실패'
'검토 결론'
```

**권장:**
```javascript
// js/i18n.js
const I18N = {
  ko: {
    header: {
      service: '감사 독립성 검토 AI',
      poweredBy: 'Powered by Samil',
      reset: '초기화',
      beta: 'Beta'
    },
    empty: {
      eyebrow: '감사 독립성 검토',
      title: '감사 독립성 시나리오를 AI로 검토해보세요',
      subtitle: '수임 가능성, 주요 이슈, 권고 안전장치 검토를 지원합니다.'
    },
    report: {
      conclusion: '검토 결론',
      issues: '주요 이슈',
      safeguards: '권고 안전장치',
      legalBasis: '근거 법령',
      relationshipDiagram: '이해관계 구조'
    },
    status: {
      denied: '수임 불가',
      conditional: '안전장치 적용 시 수임 가능',
      approved: '수임 가능'
    },
    errors: {
      graphLoadFailed: '관계도 로드 실패',
      connectionFailed: '검토 요청 연결에 실패했습니다'
    }
  }
};

const t = (key) => {
  const keys = key.split('.');
  return keys.reduce((obj, k) => obj?.[k], I18N.ko) || key;
};
```

---

### 6. 타입 힌트 누락/불완전

| 파일 | 라인 | 현재 | 권장 |
|------|------|------|------|
| `routers/graph.py` | 9 | `def _mermaid_safe_id(label: str)` | `-> str` 추가 |
| `routers/graph.py` | 17 | `def get_graph_as_mermaid()` | `-> MermaidResponse` 추가 |
| `services/independence_service.py` | 179 | `-> dict` | `-> IndependenceReviewResult` (TypedDict) |
| `database.py` | 32 | `-> Generator` | `-> Generator[Session, None, None]` |

---

## 🟢 P2: Medium (점진적 개선)

### 7. 중복 로직

**현재:**
```javascript
// buildReportCard() - 40줄
// buildIndependenceReportCard() - 87줄
// 유사한 HTML 생성 로직 중복
```

**권장:**
```javascript
function buildReportSection(title, content, className) { ... }
function buildReportHeader(status, riskLevel, color) { ... }
function buildReportBody(sections) { ... }
```

---

### 8. 전역 상태 관리

**현재:**
```javascript
var isLoading = false;
var inputMode = 'chip';
```

**권장:**
```javascript
const App = {
  state: {
    isLoading: false,
    inputMode: 'chip'  // 'chip' | 'free'
  },
  setState(key, value) {
    this.state[key] = value;
    this.render();
  }
};
```

---

### 9. Mermaid Shape Map 하드코딩

**현재:** `services/independence_service.py:116-131`
```python
shape_map = {
    "회계법인": ("[[", "]]"),
    "감사인": ("[[", "]]"),
    # ... 15개 항목
}
```

**권장:**
```yaml
# config/mermaid_shapes.yaml
회계법인: ["[[", "]]"]
감사인: ["[[", "]]"]
공인회계사: ["([", "])"]
# ...
```

---

### 10. JSDoc/Docstring 미비

**Backend 누락:**
- `routers/graph.py:_mermaid_safe_id()`
- `routers/chat.py` 모듈 docstring

**Frontend 누락:**
- `fillInput()`
- `detectScenario()`
- `scrollToMessage()`
- `buildIndependenceReportCard()`

---

### 11. CSS 변수 미사용 색상

| 라인 | 현재 | 권장 |
|------|------|------|
| 76 | `background: #ffffff;` | `var(--surface)` |
| 96 | `background: #ddd;` | `var(--gray-200)` |
| 525, 540, 544 | `#ccc` | `var(--gray-300)` |
| 638 | `#b0aba6` | `var(--muted)` |
| 849 | `#f0f4f8` | `var(--conclusion-bg)` 정의 필요 |
| 850 | `#5c6bc0` | `var(--conclusion-border)` 정의 필요 |

---

### 12. 에러 핸들링 불일치

| 파일 | 현재 | 권장 |
|------|------|------|
| `routers/independence.py` | 상세 에러 정규화 | 유지 |
| `routers/chat.py` | `str(e)` 반환 | 동일 패턴 적용 |
| `services/independence_service.py:189` | `except: pass` | 로깅 추가 |

---

## ✅ 잘 된 부분

1. **CSS 변수 체계** - Typography/Spacing 스케일 잘 정의됨
2. **Pydantic 모델** - 데이터 검증 구조화
3. **SCENARIOS 배열** - 확장 가능한 구조
4. **법령 레지스트리** - CSV 기반 유연한 구조
5. **환경변수 분리** - `.env` / `.env.example` 패턴

---

## 📋 수정 우선순위

| 순서 | 항목 | 파일 | 예상 시간 |
|------|------|------|----------|
| 1 | Magic numbers → config.py | backend/config.py | 30분 |
| 2 | 외부 URL → config | config.py, law_registry.py | 20분 |
| 3 | 타입 힌트 보강 | routers/*.py, services/*.py | 30분 |
| 4 | CSS 변수 정리 | audit-chat-pwc.html | 15분 |
| 5 | JSDoc 추가 | audit-chat-pwc.html | 30분 |
| 6 | i18n 객체 도입 | audit-chat-pwc.html | 45분 |
| 7 | 파일 분리 (선택) | static/ | 60분 |

---

## 체크포인트 후 진행 순서

```bash
# 1. 현재 상태 커밋
git add -A
git commit -m "chore: pre-refactor checkpoint - CTO review baseline"

# 2. 리팩토링 브랜치 생성
git checkout -b refactor/cto-review-fixes

# 3. P0 수정 후 커밋
git commit -m "refactor: extract magic numbers to config"

# 4. P1 수정 후 커밋
git commit -m "refactor: add type hints and improve documentation"

# 5. 메인 머지
git checkout main
git merge refactor/cto-review-fixes
```
