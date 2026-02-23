# UX 검토: 3단계 프로그레스 인디케이터

> 검토 대상: 로딩 중 표시되는 단계별 문구 + (1/3) + 점 3개  
> 관점: UX 전문가

---

## 적용된 내용 (구현 기준)

다음 항목은 `static/audit-chat-pwc.html`에 반영된 상태다.

| 구분 | 적용 내용 |
|------|-----------|
| **데이터** | `WORKFLOW_STEPS` 배열(name, desc) + `WORKFLOW_STEP_DELAYS_MS` [4000, 11000] — 단계 수·문구·타이밍 SSOT |
| **표시** | 한 번에 한 단계만 노출, 단계명 / 설명 두 줄 분리, (n/3) + 점 3개 |
| **색상** | 단계명·설명·(1/3) 모두 `--gray-500`(눈에 보이는 회색), 검정 사용 안 함 |
| **인터랙션** | 현재 단계 점에 `progress-dot-pulse` 애니메이션 |
| **접근성** | 컨테이너에 `aria-live="polite"`, `aria-atomic="true"`, `role="status"`; 단계 전환 시 `aria-label`에 "n/3 단계명. 설명" 갱신 |
| **Reduced motion** | `@media (prefers-reduced-motion: reduce)` 시 `.progress-dots span.active`의 `animation: none` |

---

## ✅ 잘 된 부분

| 항목 | 평가 |
|------|------|
| **정보 위계** | 단계명(진하게·회색) → 설명(회색) → (1/3)·점 순으로 시선 유도 적절 |
| **한 번에 한 단계** | 3문구 동시 노출이 아니라 현재 단계만 표시해 인지 부하 낮음 |
| **진행 명확성** | (1/3)으로 “몇 단계 중 몇 번째인지” 숫자로 명시, 점은 시각적 보조 |
| **두 줄 분리** | “단계명 / 설명” 분리로 스캔과 이해가 쉬움 |
| **회색 톤** | 검정 대신 `--gray-500` 사용으로 대화 버블과 구분되며 눈에 보이는 회색으로 진행 상태 전달 |
| **인터랙션 신호** | active 점의 pulse 애니메이션으로 “진행 중” 느낌 제공 (reduced-motion 시 비활성화) |

---

## 🟡 개선 권장

| 우선순위 | 항목 | 내용 | 권장 / 상태 |
|---------|------|------|------|
| P1 | **접근성** | 스크린리더 사용자에게 단계 전환 인지 | ✅ 적용: `aria-live="polite"`, `aria-atomic="true"`, `role="status"`, 단계 전환 시 `aria-label` 갱신 |
| P1 | **Reduced motion** | 애니메이션 민감 사용자 | ✅ 적용: `prefers-reduced-motion: reduce` 시 active 점 `animation: none` |
| P2 | **(1/3)과 점 중복** | 같은 정보를 숫자·점 두 가지로 표시 | 유지 권장. 숫자는 명시적, 점은 빠른 시각 인지에 도움 |
| P2 | **설명 길이** | 2단계 문구가 한 줄에 길어 작은 뷰포트에서 줄바꿈 많을 수 있음 | 필요 시 `max-width`·`line-height`로 가독성만 점검 |
| P3 | **완료 순간** | 응답 도착 시 프로그레스가 곧바로 사라짐 | 선택적으로 “완료” 0.3초 표시 후 카드로 전환 가능 (과하지 않게) |

---

## 🔴 주의할 점

- **타이밍은 추정치**  
  실제 백엔드 단계와 무관하게 4초·11초로 전환되므로, “2단계인데 아직 1단계 문구” 같은 불일치 가능성은 있음.  
  사용자 인지만 놓고 보면 “대략적인 진행 감”을 주는 수준으로 이해하는 것이 좋음.

- **첫 진입**  
  첫 검토 시 “이게 뭔가?” 느낌을 줄 수 있으므로, 빈 상태/첫 사용 시 짧은 도움말(예: “시나리오를 입력하면 AI가 단계별로 검토합니다”)이 이미 있다면 유지 권장.

---

## 권장 코드 수정 (접근성·Reduced motion) — ✅ 적용됨

1. **컨테이너에 `aria-live`**  
   `.workflow-progress`에 `aria-live="polite"`, `aria-atomic="true"`, `role="status"` 적용. `setProgressStep()` 호출 시 `aria-label`을 "n/3 단계명. 설명"으로 갱신해 스크린리더가 단계 전환을 인지함.

2. **Reduced motion**  
   `@media (prefers-reduced-motion: reduce)` 내에서 `.workflow-progress .progress-dots span.active`에 `animation: none` 적용됨.

---

## 종합

- **목적(진행 감·단계 인지·인지 부하 감소)** 에 맞게 잘 설계되어 있음.  
- **접근성(aria-live, aria-label, reduced motion)** 이 반영된 상태로, 회계법인 클라이언트용으로 무난한 수준.
