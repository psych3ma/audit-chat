# 프로그레스 버블 변경 — 의존성/영향도 체크

> 검토일: 2026-02-12  
> 대상: 3단계 프로그레스 UI, `--workflow-bubble-width`, WORKFLOW_STEPS

---

## 결론: **다른 질문/답변·화면에는 영향 없음**

변경 사항은 **독립성 검토 요청 시 로딩 중에만** 쓰이는 프로그레스 버블에만 적용되며, 답변 카드·에러 버블·사용자 버블·다른 API 흐름에는 쓰이지 않습니다.

---

## 1. 사용처 (발생 위치)

| 항목 | 사용 위치 | 비고 |
|------|-----------|------|
| `.typing.workflow-progress` | `sendMessage()` 내부 1곳 | `typing.className = 'typing workflow-progress'` 로만 생성 |
| `WORKFLOW_STEPS` / `WORKFLOW_STEP_DELAYS_MS` | 동일 `sendMessage()` 스코프 | 전역 상수지만 이 함수 안에서만 참조 |
| 버블 가로 너비 | JS에서 `WORKFLOW_STEPS` 3단계 문구 최대 폭 측정 후 설정 (하드코딩 없음) | 다른 컴포넌트 미사용 |
| `.progress-dots-row`, `.progress-step-line`, `.progress-desc` | 위 typing 요소의 innerHTML·querySelector | 프로그레스 버블 내부 전용 |

**정리:** 프로그레스 관련 클래스·변수·상수는 모두 **이 로딩 버블 생성/제거 사이클 안**에서만 사용됩니다.

---

## 2. 다른 UI와의 격리

| UI 요소 | 클래스/역할 | 프로그레스와 충돌 여부 |
|---------|-------------|-------------------------|
| 사용자 말풍선 | `.user-bubble` | 없음 — 별도 클래스 |
| 답변 카드 | `.independence-report` | 없음 — 별도 클래스 |
| 에러 메시지 | `.assistant-bubble.error` | 없음 — 별도 클래스 |
| 시나리오 칩·입력창 등 | 기타 | `.typing`, `.workflow-progress`, `.progress-*` 미사용 |

`.progress-step-line`, `.progress-desc` 등은 **프로그레스 버블 안에서만** 생성·조회되며, 리포트 카드나 다른 템플릿에는 같은 클래스명이 없습니다.

---

## 3. `.typing` 단독 사용 여부

- **과거:** 예전에는 `class="typing"` 만 주고 점 3개만 넣는 구조였을 수 있음.
- **현재:** `typing.className = 'typing workflow-progress'` 로 **항상 두 클래스를 함께** 부여하고 있음.
- **영향:** `.typing` 단독으로 쓰는 코드 경로는 없음.  
  따라서 `.typing.workflow-progress` 에서 `width: var(--workflow-bubble-width)` 를 써도, “typing만 있는” 다른 버블은 없어서 **다른 질문/답변 UI에 영향 없음**.

---

## 4. 백엔드·다른 파일

- **Backend:** `typing` 검색 결과는 Python `from typing import ...` 뿐이며, 프론트 프로그레스 UI와 무관.
- **다른 HTML/JS:** `audit-chat-pwc.html` 외에는 프로그레스/워크플로우 관련 클래스·변수 사용처 없음.

---

## 5. 요약 표

| 체크 항목 | 결과 |
|-----------|------|
| 프로그레스 버블이 다른 메시지/카드에 쓰이는가? | 아니오 — 로딩 중 1회만 생성·제거 |
| `--workflow-bubble-width` 를 다른 컴포넌트가 쓰는가? | 아니오 — `.typing.workflow-progress` 전용 |
| `WORKFLOW_STEPS` / delays 를 다른 흐름이 쓰는가? | 아니오 — `sendMessage()` 내부 전용 |
| `.progress-*` 클래스가 리포트/버블에 중복되는가? | 아니오 — 프로그레스 DOM 전용 |
| 백엔드/다른 페이지에 부수 효과가 있는가? | 아니오 |

**다른 질문/답변 및 다른 화면에는 영향 없으며, 의존성은 해당 로딩 버블로만 한정됩니다.**
