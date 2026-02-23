# UI 프로토타입 검토: audit-chat-prototype.html

## 1. 구조 요약

| 영역 | 내용 |
|------|------|
| **헤더** | 로고(⚖) + "감사 독립성 AI 분석" + Beta 뱃지 |
| **빈 상태** | 아이콘, "시나리오를 입력해주세요", 4개 제안 칩(지분/가족/비감사/전직) |
| **채팅** | 사용자 말풍선(우측, 빨강) + 리포트 카드(좌측, 2단 레이아웃) |
| **입력** | textarea + 전송 버튼, Enter 전송, placeholder |

---

## 2. 장점

- **다크 톤**: `#0f0f13` 배경, `#e63946` 포인트로 가독성·브랜딩 일관됨.
- **리포트 카드**: 좌(관계 지형도 + 주요 이슈) / 우(법규 + 검토 의견 + 안전장치) 구분이 명확함.
- **제안 칩**: 시나리오 예시로 첫 사용 진입이 쉬움.
- **타이핑 인디케이터**: 3점 바운스로 “분석 중” 피드백이 분명함.
- **반응형 고려**: `max-width`, `grid` 등으로 대화/카드 너비 제한.

---

## 3. 현재 동작 (목업)

- **실제 API 호출 없음.** `sendMessage()` → `detectScenario(text)`로 키워드 매칭 후 `scenarios` 객체에서 고정 데이터 선택 → 1.8초 뒤 카드 렌더.
- **시나리오 키**: `default` / `family` / `nonaudit` / `former` 4종.
- **프론트만으로 동작하는 시연용 프로토타입**으로 이해하면 됨.

---

## 4. 백엔드 연동 시 매핑

우리 API `POST /independence/review` 응답과 프로토의 “리포트 카드” 필드 매핑:

| 프로토 필드 | API 응답 |
|-------------|----------|
| REVIEW ID | `trace_id` |
| verdict (수임 불가/가능) | `analysis.status` |
| 위험도 | `analysis.risk_level` |
| 관계 지형도 (flow nodes) | `rel_map.entities` + `rel_map.connections` 또는 `mermaid_code` |
| 주요 이슈 | `analysis.key_issues` |
| 적용 기준 | `analysis.legal_references` |
| 검토 의견 | `analysis.considerations` |
| 권고 안전장치 | `analysis.suggested_safeguards` |

- **상태 3종**: API는 `수임 불가` / `안전장치 적용 시 수임 가능` / `수임 가능`. 프로토는 현재 **red / green** 두 가지만 있음 → **안전장치 적용 시 수임 가능**용 **orange(또는 amber)** 헤더 스타일 추가 권장.

---

## 5. 연동 시 수정·보완 사항

1. **API 호출**
   - `setTimeout(…, 1800)` 제거 후 `fetch('http://localhost:8001/independence/review', { method: 'POST', body: JSON.stringify({ scenario: text }) })` 등으로 교체.
   - 응답으로 위 표처럼 `trace_id`, `rel_map`, `analysis`, `mermaid_code` 넣어 카드 구성.

2. **관계 지형도**
   - **옵션 A**: `mermaid_code`를 그대로 사용 → Mermaid.js로 렌더 (프로토의 “flow-node” 리스트 대신).
   - **옵션 B**: `rel_map.entities` + `rel_map.connections`로 기존처럼 노드/화살표 리스트를 직접 만들어 flow-diagram 유지.

3. **XSS 방지**
   - 사용자 입력·API 응답을 카드에 넣을 때 **텍스트 이스케이프** (또는 `textContent`/안전한 템플릿). 현재는 `scenarios` 고정 데이터라 위험 적지만, 실 API 연동 시 필수.

4. **에러·빈 응답**
   - API 실패 시 에러 메시지 표시, `analysis`/`rel_map` 없을 때 대체 문구 또는 스켈레톤 처리 권장.

5. **CORS**
   - HTML을 `file://` 또는 다른 origin에서 열면 브라우저가 `localhost:8001` 호출을 막을 수 있음. 실제 연동 시 같은 origin에서 서빙하거나, 백엔드 CORS에 해당 origin 추가 필요.

---

## 6. Streamlit과의 관계

- 이 HTML은 **독립 정적 페이지**이므로:
  - **방안 1**: FastAPI에서 이 HTML을 정적 파일로 서빙하고, 같은 페이지에서 JS로 `/independence/review` 호출.
  - **방안 2**: Streamlit에서 “독립성 검토” 화면을 이 프로토와 **동일한 레이아웃/색상**으로 다시 구현 (컴포넌트 + `st.markdown`/HTML).
  - **방안 3**: Streamlit 앱에 `iframe`으로 이 HTML 페이지를 넣고, 필요 시 `postMessage` 등으로 시나리오만 넘겨서 사용.

프로토를 “그대로” 쓸지, Streamlit으로 “재구현”할지 정하면 위 매핑과 5번 항목만 반영하면 됨.

---

# UI 프로토타입 검토: audit-chat-pwc.html (삼일PwC — 내부통제 AI 검토)

## 1. 구조 요약

| 영역 | 내용 |
|------|------|
| **헤더** | PwC 로고(이미지) + "내부통제 검토 AI" + Beta 뱃지 + **↩ 새 분석** 버튼(분석 후 표시) |
| **빈 상태** | eyebrow "Internal Control Review", 제목, 부제, **6개 제안 칩** (대출 전결/순환근무/직무 겸직/신입 보증/모범 인센티브/대손 보고) |
| **채팅** | 사용자 말풍선(우측, 검정) + 리포트 카드(좌측) + **리포트 하단 "다른 시나리오를 선택하세요" 칩 6개** |
| **입력** | **readonly** textarea + 전송 버튼. placeholder: "위 예시 버튼을 선택하면 시나리오가 입력됩니다" |

- **도메인**: 감사 **독립성**이 아니라 **내부통제(Internal Control)** 시나리오 검토 (은행 규제·COSO·직무분리 등).

---

## 2. 장점

- **라이트 톤**: `--bg: #fafaf8`, `--surface: #ffffff`, `--red: #ad1b02` 등 PwC 계열 톤으로 첫 번째 프로토(다크)와 차별화.
- **헤더**: 로고 + 서비스명 + **새 분석** 버튼으로 대화 초기화가 명확함.
- **리포트 카드**: 첫 번째와 동일한 2단(관계 지형도 + 이슈 \| 법규 + 의견 + 안전장치). **accent-bar**(red→orange→amber→yellow 그라데이션)로 시인성 강화.
- **위험도 pills**: `risk-high`(노랑 배경), `risk-medium`(반투명 흰색)로 구분.
- **결과 후 플로우**: 리포트 아래 "다른 시나리오를 선택하세요" 칩으로 **연속 시나리오 분석** UX 제공.
- **입력 제한**: textarea **readonly**로 “칩으로만 시나리오 선택”하는 시연/데모 시나리오에 적합.

---

## 3. 현재 동작 (목업)

- **실제 API 호출 없음.** `detectScenario(text)` 키워드 매칭 → `scenarios` 6종(loan, rotation, duties, hiring, incentive, baddebt) 중 하나 선택 → 1.8초 뒤 카드 + post-chips 렌더.
- **verdict 값**: "통제 미흡" / "중요한 취약점" / "통제 보완 필요" / "통제 적절" (denied=red, approved=green만 사용).
- **로고**: `header-brand img`의 `src`가 긴 base64 데이터(플레이스홀더). 실제 서비스 시 로고 이미지 경로로 교체 필요.

---

## 4. 첫 번째 프로토(감사 독립성)와의 차이

| 항목 | audit-chat-prototype (독립성) | audit-chat-pwc (내부통제) |
|------|-------------------------------|----------------------------|
| 테마 | 다크 | 라이트 (PwC 톤) |
| 입력 | 자유 입력 + 칩 | **readonly**, 칩으로만 입력 |
| 시나리오 수 | 4 | 6 |
| verdict | 수임 불가/가능 | 통제 미흡/취약점/보완 필요/적절 |
| 결과 후 | 없음 | "다른 시나리오 선택" 칩 + 새 분석 버튼 |
| 백엔드 | 독립성 API (`/independence/review`) | **별도 내부통제 API 필요** (현재 프로젝트에는 없음) |

---

## 5. 연동 시 참고

- **백엔드**: 현재 audit-chat 프로젝트는 **감사 독립성** API만 있음. 이 UI를 쓰려면 **내부통제 전용** 엔드포인트(예: 시나리오 → 통제 적절성·기준·개선안 분석)와 응답 스키마가 따로 필요함.
- **응답 매핑**: verdict → `status`, 위험도 → `risk_level`, 관계 지형도 → flow nodes 또는 Mermaid, 이슈/법규/의견/안전장치 → 각각 리스트·문자열 필드로 매핑하면 됨. (필드명은 내부통제 API 설계에 맞춰 조정.)
- **readonly 해제**: 실서비스에서 사용자가 직접 문장을 입력하게 하려면 textarea의 `readonly` 제거 및 placeholder 문구 수정.
- **로고**: `header-brand img`의 `src`를 실제 에셋 경로 또는 CDN URL로 변경.
- **XSS**: 실 API 연동 시 사용자/API 텍스트는 이스케이프 후 삽입 (동일).

---

## 6. 정리

- **audit-chat-prototype.html**: 감사 **독립성** 시나리오, 다크 UI, 자유 입력 + 칩. → 현재 **`/independence/review`** 와 바로 매핑 가능.
- **audit-chat-pwc.html**: **내부통제** 시나리오, 라이트 UI, 칩 전용 입력, 결과 후 연속 시나리오. → **내부통제용 백엔드**가 있으면 동일한 리포트 카드 구조로 연동 가능.
