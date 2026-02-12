# Audit Chat Architecture

회계법인 제출용 포트폴리오 시스템 아키텍처 문서입니다.

---

## 1. Mermaid 전문가 검토

### 현재 구현 (`build_mermaid_graph`)

| 항목 | 현재 상태 | 평가 |
|------|----------|------|
| 다이어그램 타입 | `graph TD` (Flowchart Top-Down) | ✅ 관계 계층 표현에 적합 |
| 노드 모양 | 엔티티 유형별 shape 매핑 | ✅ 시각적 구분 명확 |
| 엣지 문법 | `-->｜rel｜` (표준) | ✅ mermaid.ink 완전 지원 |
| 한글 라벨 | `<br/>` 줄바꿈 + 클린업 | ✅ URL 인코딩 안정 |
| classDef/style | 미사용 | ⚠️ mermaid.ink 부분 지원, 현재 방식 권장 |

**개선 불필요** — 현재 flowchart 구현은 mermaid.ink 렌더링에 최적화되어 있음.

---

## 2. 시스템 아키텍처

### 2.1 Architecture Diagram (Mermaid v11.1.0+)

> ⚠️ `architecture-beta`는 Mermaid v11.1.0+ 필요. GitHub/일부 렌더러 미지원 시 2.2 Flowchart 버전 사용.

```mermaid
architecture-beta
    group user(cloud)[사용자]
    group frontend(server)[프론트엔드]
    group backend(server)[백엔드 FastAPI]
    group services(database)[서비스 레이어]
    group external(internet)[외부 서비스]

    service browser(internet)[브라우저] in user

    service static_html(disk)[audit-chat-pwc.html] in frontend
    service streamlit(server)[Streamlit App] in frontend

    service fastapi(server)[FastAPI] in backend
    service router_independence(disk)[/independence] in backend
    service router_chat(disk)[/chat] in backend
    service router_graph(disk)[/graph] in backend

    service independence_svc(database)[independence_service] in services
    service llm_structured(database)[llm_structured] in services
    service llm_service(database)[llm_service] in services
    service law_registry(disk)[law_registry] in services

    service openai(cloud)[OpenAI API] in external
    service neo4j(database)[Neo4j] in external
    service law_go_kr(internet)[law.go.kr] in external

    browser:R --> L:static_html
    browser:R --> L:streamlit

    static_html:B --> T:fastapi
    streamlit:B --> T:fastapi

    fastapi:B --> T:router_independence
    fastapi:B --> T:router_chat
    fastapi:B --> T:router_graph

    router_independence:R --> L:independence_svc
    router_chat:R --> L:llm_service
    router_graph:R --> L:neo4j

    independence_svc:R --> L:llm_structured
    independence_svc:R --> L:law_registry
    independence_svc:B --> T:neo4j

    llm_structured:B --> T:openai
    llm_service:B --> T:openai
    law_registry:B --> T:law_go_kr
```

### 2.2 Architecture Diagram (Flowchart 호환 버전)

```mermaid
flowchart TB
    subgraph User["👤 사용자"]
        Browser[브라우저]
    end

    subgraph Frontend["📱 프론트엔드"]
        StaticHTML["audit-chat-pwc.html<br/>(제출용)"]
        Streamlit["Streamlit App<br/>(실험용)"]
    end

    subgraph Backend["⚙️ 백엔드 FastAPI"]
        FastAPI[FastAPI Server]
        subgraph Routers["라우터"]
            R1["/independence"]
            R2["/chat"]
            R3["/graph"]
        end
    end

    subgraph Services["🔧 서비스 레이어"]
        IndepSvc["independence_service<br/>추출→분석→Mermaid"]
        LLMStruct["llm_structured<br/>구조적 출력"]
        LLMSvc["llm_service<br/>일반 채팅"]
        LawReg["law_registry<br/>법령 URL"]
    end

    subgraph External["🌐 외부 서비스"]
        OpenAI[(OpenAI API)]
        Neo4j[(Neo4j)]
        LawGoKr[law.go.kr]
        MermaidInk[mermaid.ink]
    end

    Browser --> StaticHTML
    Browser --> Streamlit
    StaticHTML --> FastAPI
    Streamlit --> FastAPI
    
    FastAPI --> R1
    FastAPI --> R2
    FastAPI --> R3
    
    R1 --> IndepSvc
    R2 --> LLMSvc
    R3 --> Neo4j
    
    IndepSvc --> LLMStruct
    IndepSvc --> LawReg
    IndepSvc -.-> Neo4j
    
    LLMStruct --> OpenAI
    LLMSvc --> OpenAI
    LawReg -.-> LawGoKr
    
    StaticHTML -.-> MermaidInk

    style User fill:#e3f2fd
    style Frontend fill:#fff3e0
    style Backend fill:#f3e5f5
    style Services fill:#e8f5e9
    style External fill:#fce4ec
```

---

## 3. 레이어별 구성요소

### 3.1 진입로 (Entry Points)

| 구성요소 | 파일 | 용도 |
|----------|------|------|
| **정적 UI** | `static/audit-chat-pwc.html` | 회계법인 제출용 단일 페이지 |
| **Streamlit** | `frontend/app.py` | 내부 실험/데모용 멀티페이지 |

### 3.2 백엔드 (FastAPI)

| 라우터 | 엔드포인트 | 역할 |
|--------|-----------|------|
| `independence` | `POST /independence/review` | 독립성 검토 파이프라인 |
| `chat` | `POST /chat/completions` | 일반 채팅 (비구조화) |
| `graph` | `GET /graph/mermaid` | Neo4j → Mermaid 변환 |
| `health` | `GET /health` | 헬스체크 |

### 3.3 서비스 레이어

| 서비스 | 역할 |
|--------|------|
| `independence_service` | 추출 → 분석 → 법령보강 → Mermaid → Neo4j |
| `llm_structured` | 구조적 출력 (Pydantic + JSON 모드) |
| `llm_service` | 일반 채팅 (비구조화) |
| `law_registry` | 법령 URL 생성 (CSV 기반) |

### 3.4 외부 서비스

| 서비스 | 용도 |
|--------|------|
| **OpenAI API** | GPT-4o-mini (추출), GPT-4o (분석) |
| **Neo4j** | 엔티티/관계 저장, 그래프 조회 |
| **law.go.kr** | 법령 조문 링크 (사용자 클릭 시) |
| **mermaid.ink** | 관계도 이미지 렌더링 |

---

## 4. 독립성 검토 파이프라인 (Flowchart)

```mermaid
flowchart TD
    subgraph Client["클라이언트"]
        A[사용자 시나리오 입력]
    end

    subgraph Backend["백엔드"]
        B[POST /independence/review]
        C[extract_relationships]
        D[analyze_independence]
        E[_enrich_legal_ref_urls]
        F[build_mermaid_graph]
        G[save_to_neo4j]
    end

    subgraph External["외부"]
        H[(OpenAI GPT-4o-mini)]
        I[(OpenAI GPT-4o)]
        J[(Neo4j)]
        K[법령검색목록.csv]
    end

    A --> B
    B --> C
    C -->|IndependenceMap| D
    D -->|AnalysisResult| E
    E --> F
    F --> G

    C -.->|구조적 출력| H
    D -.->|구조적 출력| I
    E -.->|법령명 매칭| K
    G -.->|저장| J

    style A fill:#e3f2fd
    style B fill:#fff3e0
    style H fill:#f3e5f5
    style I fill:#f3e5f5
    style J fill:#e8f5e9
```

---

## 5. 시퀀스 다이어그램

### 5.1 독립성 검토 전체 흐름

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 사용자
    participant F as 📱 Frontend<br/>(HTML/Streamlit)
    participant R as ⚙️ Router<br/>(/independence)
    participant S as 🔧 Service<br/>(independence_service)
    participant L1 as 🤖 GPT-4o-mini<br/>(추출)
    participant L2 as 🤖 GPT-4o<br/>(분석)
    participant LR as 📜 law_registry
    participant N as 🗄️ Neo4j
    participant M as 🖼️ mermaid.ink

    U->>F: 시나리오 입력
    F->>R: POST /independence/review<br/>{scenario}
    
    rect rgb(240, 248, 255)
        Note over R,S: 파이프라인 시작
        R->>S: run_independence_review(scenario)
        
        Note over S,L1: Step 1: 관계 추출
        S->>L1: extract_relationships()<br/>system: 구조화 지시<br/>user: 시나리오
        L1-->>S: IndependenceMap<br/>{entities, connections}
        
        Note over S,L2: Step 2: 독립성 분석
        S->>L2: analyze_independence()<br/>system: 분석 지시<br/>user: 시나리오 + rel_map
        L2-->>S: AnalysisResult<br/>{status, key_issues, legal_refs}
        
        Note over S,LR: Step 3: 법령 URL 보강
        S->>LR: get_law_url(법령명)
        LR-->>S: URL (법령 조문 링크)
        
        Note over S: Step 4: Mermaid 생성
        S->>S: build_mermaid_graph(rel_map)
        
        Note over S,N: Step 5: Neo4j 저장 (선택)
        S--)N: save_independence_map()
    end
    
    S-->>R: {trace_id, rel_map,<br/>analysis, mermaid_code}
    R-->>F: JSON Response
    
    rect rgb(255, 248, 240)
        Note over F,M: 클라이언트 렌더링
        F->>M: mermaid.ink/img/{base64}
        M-->>F: PNG 이미지
        F->>F: buildIndependenceReportCard()
    end
    
    F-->>U: 리포트 카드 표시<br/>(관계도 + 분석결과 + 법령링크)
```

### 5.2 LLM 구조적 출력 상세

```mermaid
sequenceDiagram
    autonumber
    participant S as Service
    participant LS as llm_structured
    participant OAI as OpenAI API

    S->>LS: chat_completion_structured()<br/>model, messages, response_model
    
    rect rgb(245, 245, 255)
        Note over LS: Pydantic → JSON Schema 변환
        LS->>LS: response_model.model_json_schema()
    end
    
    rect rgb(255, 250, 245)
        Note over LS,OAI: API 호출 (재시도 로직 포함)
        LS->>OAI: chat.completions.create()<br/>response_format: json_schema
        
        alt 성공
            OAI-->>LS: JSON 응답
        else RateLimitError
            OAI--xLS: 429 Too Many Requests
            LS->>LS: 지수 백오프 대기
            LS->>OAI: 재시도 (최대 3회)
            OAI-->>LS: JSON 응답
        else 기타 오류
            OAI--xLS: Error
            LS->>LS: 1초 대기 후 재시도
        end
    end
    
    rect rgb(245, 255, 245)
        Note over LS: Pydantic 검증
        LS->>LS: response_model.model_validate_json()
    end
    
    LS-->>S: Pydantic 모델 인스턴스
```

### 5.3 프론트엔드 렌더링 흐름

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 사용자
    participant UI as 🖥️ UI
    participant JS as 📜 JavaScript
    participant API as ⚙️ Backend API
    participant MI as 🖼️ mermaid.ink

    U->>UI: 시나리오 칩 클릭
    UI->>JS: fillInput(text)
    JS->>UI: textarea 업데이트
    U->>UI: 전송 버튼 클릭
    
    rect rgb(240, 240, 255)
        Note over JS: 로딩 상태
        JS->>UI: typing indicator 표시
        JS->>UI: 버튼 비활성화
    end
    
    JS->>API: fetch(POST /independence/review)
    API-->>JS: JSON {trace_id, analysis, mermaid_code}
    
    rect rgb(255, 250, 240)
        Note over JS,UI: 리포트 카드 생성
        JS->>JS: buildIndependenceReportCard(data)
        JS->>UI: 스켈레톤 로더 삽입
        JS->>UI: 카드 DOM 추가 (fade-in)
    end
    
    rect rgb(240, 255, 240)
        Note over JS,MI: 그래프 이미지 로드
        JS->>JS: mermaidToImgUrl(code)
        JS->>MI: new Image().src = url
        MI-->>JS: onload 이벤트
        JS->>UI: 스켈레톤 → 이미지 교체 (fade-in)
    end
    
    JS->>UI: scrollToMessage(reportCard)
    JS->>UI: typing indicator 제거
    U->>UI: 리포트 확인
```

### 5.4 법령 URL 생성 흐름

```mermaid
sequenceDiagram
    autonumber
    participant S as independence_service
    participant LR as law_registry
    participant CSV as 법령검색목록.csv
    participant User as 👤 사용자 (브라우저)

    Note over LR,CSV: 앱 시작 시 1회 로드
    LR->>CSV: 파일 읽기
    CSV-->>LR: 법령명, 법령MST(lsiSeq)
    LR->>LR: _registry 딕셔너리 구축<br/>{정규화된_법령명: lsiSeq}

    Note over S,LR: 분석 결과 보강
    S->>LR: get_law_url("공인회계사법 제21조")
    
    rect rgb(250, 250, 255)
        LR->>LR: 법령명 정규화<br/>"공인회계사법" + "제21조"
        LR->>LR: _registry에서 lsiSeq 조회
        alt 조문 지정됨
            LR->>LR: 조문 URL 생성<br/>law.go.kr/법령/{법령명}/{조문}
        else 조문 없음
            LR->>LR: 전체 URL 생성<br/>law.go.kr/법령/{법령명}
        end
    end
    
    LR-->>S: URL 문자열
    S->>S: legal_references[].url = URL
    
    Note over User: 사용자 클릭 시
    User->>User: <a href="URL"> 클릭
    User->>User: 새 탭에서 law.go.kr 열림
```

---

## 6. 데이터 흐름

```
시나리오 (str)
    │
    ▼
┌─────────────────────────────┐
│  extract_relationships      │ ──► LLM (GPT-4o-mini)
│  → IndependenceMap          │     구조적 출력
│    { entities, connections }│
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  analyze_independence       │ ──► LLM (GPT-4o)
│  → AnalysisResult           │     구조적 출력
│    { status, key_issues,    │     (rel_map 참조)
│      legal_references, ... }│
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  _enrich_legal_ref_urls     │ ──► law_registry
│  → legal_references[].url   │     CSV → URL 생성
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  build_mermaid_graph        │ ──► Mermaid 문자열
│  → mermaid_code             │     (flowchart TD)
└─────────────────────────────┘
    │
    ▼
┌─────────────────────────────┐
│  Response                   │
│  { trace_id, rel_map,       │
│    analysis, mermaid_code } │
└─────────────────────────────┘
```

---

## 7. 파일 구조

```
audit-chat/
├── backend/
│   ├── main.py                 # FastAPI 앱 진입점
│   ├── config.py               # 설정 (Settings, .env)
│   ├── database.py             # Neo4j 드라이버
│   ├── routers/
│   │   ├── independence.py     # 독립성 검토 API
│   │   ├── chat.py             # 채팅 API
│   │   ├── graph.py            # 그래프 API
│   │   └── health.py           # 헬스체크
│   ├── services/
│   │   ├── independence_service.py  # 핵심 파이프라인
│   │   ├── llm_structured.py        # 구조적 LLM
│   │   └── llm_service.py           # 일반 LLM
│   ├── models/
│   │   ├── independence.py     # IndependenceMap, AnalysisResult
│   │   └── schemas.py          # 기타 스키마
│   └── utils/
│       └── law_registry.py     # 법령 URL 생성
├── frontend/
│   ├── app.py                  # Streamlit 앱
│   └── pages/                  # 멀티페이지
├── static/
│   └── audit-chat-pwc.html     # 제출용 정적 UI
├── 법령검색목록.csv             # 법령 데이터
├── requirements.txt
└── .env                        # 환경변수 (비공개)
```

---

## 8. 기술 스택

| 카테고리 | 기술 |
|----------|------|
| **Backend** | FastAPI, Pydantic, uvicorn |
| **Frontend** | HTML/CSS/JS (정적), Streamlit |
| **LLM** | OpenAI GPT-4o, GPT-4o-mini |
| **Database** | Neo4j (그래프) |
| **Visualization** | Mermaid.js (mermaid.ink) |
| **Configuration** | pydantic-settings, python-dotenv |

---

## 9. Git 브랜치 전략 (GitGraph)

### 9.1 프로젝트 개발 히스토리

```mermaid
gitGraph
    commit id: "init" tag: "v0.1.0"
    commit id: "fastapi-setup"
    
    branch feature/llm-structured
    checkout feature/llm-structured
    commit id: "pydantic-models"
    commit id: "llm-structured-output"
    checkout main
    merge feature/llm-structured id: "merge-llm" tag: "v0.2.0"
    
    branch feature/independence
    checkout feature/independence
    commit id: "extract-relationships"
    commit id: "analyze-independence"
    commit id: "mermaid-graph"
    checkout main
    merge feature/independence id: "merge-indep" tag: "v0.3.0"
    
    branch feature/law-registry
    checkout feature/law-registry
    commit id: "csv-parser"
    commit id: "url-generator"
    checkout main
    merge feature/law-registry id: "merge-law"
    
    branch feature/static-ui
    checkout feature/static-ui
    commit id: "html-layout"
    commit id: "scenarios-ssot"
    commit id: "loading-skeleton"
    checkout main
    merge feature/static-ui id: "merge-ui" tag: "v1.0.0" type: HIGHLIGHT
    
    commit id: "docs-architecture"
    commit id: "ready-submit" tag: "제출용"
```

### 9.2 권장 브랜치 전략 (Git Flow Lite)

```mermaid
gitGraph
    commit id: "stable" tag: "v1.0.0"
    
    branch develop
    checkout develop
    commit id: "dev-base"
    
    branch feature/new-scenario
    checkout feature/new-scenario
    commit id: "add-scenario-data"
    commit id: "update-prompts"
    checkout develop
    merge feature/new-scenario id: "merge-scenario"
    
    branch feature/ui-enhancement
    checkout feature/ui-enhancement
    commit id: "responsive-layout"
    commit id: "dark-mode"
    checkout develop
    merge feature/ui-enhancement id: "merge-ui"
    
    checkout main
    merge develop id: "release" tag: "v1.1.0" type: HIGHLIGHT
    
    branch hotfix/critical-bug
    checkout hotfix/critical-bug
    commit id: "fix-bug" type: REVERSE
    checkout main
    merge hotfix/critical-bug id: "hotfix" tag: "v1.1.1"
    
    checkout develop
    merge main id: "sync-hotfix"
```

### 9.3 기능별 브랜치 명명 규칙

| 브랜치 타입 | 패턴 | 예시 |
|------------|------|------|
| **Feature** | `feature/{기능명}` | `feature/new-scenario` |
| **Bugfix** | `bugfix/{이슈번호}` | `bugfix/issue-42` |
| **Hotfix** | `hotfix/{설명}` | `hotfix/critical-bug` |
| **Release** | `release/v{버전}` | `release/v1.2.0` |
| **Docs** | `docs/{문서명}` | `docs/architecture` |

### 9.4 커밋 타입 가이드

```mermaid
gitGraph TB:
    commit id: "feat: 새 기능" type: HIGHLIGHT
    commit id: "fix: 버그 수정" type: REVERSE
    commit id: "docs: 문서 추가"
    commit id: "refactor: 리팩토링"
    commit id: "style: 코드 포맷"
    commit id: "test: 테스트 추가"
    commit id: "chore: 빌드/설정"
```

### 9.5 릴리즈 플로우

```mermaid
%%{init: { 'theme': 'base', 'gitGraph': {'mainBranchName': 'production'}} }%%
gitGraph
    commit id: "v1.0.0" tag: "production"
    
    branch staging
    checkout staging
    commit id: "qa-ready"
    
    branch develop
    checkout develop
    commit id: "feature-a"
    commit id: "feature-b"
    
    checkout staging
    merge develop id: "staging-merge"
    commit id: "qa-pass" type: HIGHLIGHT
    
    checkout production
    merge staging id: "deploy" tag: "v1.1.0" type: HIGHLIGHT
    
    checkout develop
    commit id: "continue-dev"
```

---

## 10. Mermaid 다이어그램 요약

| 섹션 | 다이어그램 타입 | 용도 |
|------|----------------|------|
| 2.1 | `architecture-beta` | 시스템 아키텍처 (v11.1.0+) |
| 2.2 | `flowchart TB` | 시스템 아키텍처 (호환) |
| 4 | `flowchart TD` | 독립성 검토 파이프라인 |
| 5.1 | `sequenceDiagram` | 전체 흐름 |
| 5.2 | `sequenceDiagram` | LLM 구조적 출력 |
| 5.3 | `sequenceDiagram` | 프론트엔드 렌더링 |
| 5.4 | `sequenceDiagram` | 법령 URL 생성 |
| 9.1 | `gitGraph` | 개발 히스토리 |
| 9.2 | `gitGraph` | 브랜치 전략 |
| 9.4 | `gitGraph TB:` | 커밋 타입 가이드 |
| 9.5 | `gitGraph` | 릴리즈 플로우 |

---

*이 문서는 아키텍처 변경 시 함께 갱신해야 합니다.*
