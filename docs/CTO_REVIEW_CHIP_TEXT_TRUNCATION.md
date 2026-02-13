# 시나리오 칩 텍스트 표시 방식 변경 - CTO 검토

**작성일**: 2026-02-12  
**작성자**: CTO 관점  
**검토 대상**: 시나리오 칩 2열에서 요약(`shortText`) 대신 원문(`text`) 표시 및 말줄임 처리

---

## 검토 개요

시나리오 칩의 2열(설명 부분)에서 현재 요약 텍스트(`shortText`) 대신 원문(`text`)을 표시하되, 칩 크기를 고려하여 일정 부분에서 잘라서 '...'로 마무리하는 방식으로 변경합니다.

---

## 1. 현재 상태 분석

### 현재 구조

**데이터 구조**:
```javascript
const SCENARIOS = [
  {
    label: "동일 회계법인 내 매수·매각 자문",
    text: "X회계법인은 5개의 사업부(1∼5본부)로 구성되어 있으며...", // 원문 (전체)
    shortText: "X회계법인 1본부 매각자문, 3본부 매수자문 요청", // 요약
    source: "2018_CPA2차_회계감사"
  }
]
```

**현재 렌더링**:
```javascript
'<div class="chip-text">' + d.shortText + '</div>'
```

**CSS 스타일**:
```css
.chip-text {
  font-size: var(--fs-md);  /* 16px */
  color: var(--text);
  line-height: 1.45;
  font-weight: 500;
}
```

---

## 2. 요구사항 분석

### 사용자 요구사항

- **원문 표시**: `shortText` 대신 `text` 사용
- **말줄임 처리**: 칩 크기를 고려하여 일정 부분에서 자르고 '...' 표시
- **예시**: "X회계법인은 5개의 사업부(1∼5본부)로 구성되어 있으며, 주요 업무영역은 인증업무와 재무자문(deal service)업무이다. 현재 1본부의 파트너(사원)인 김 회계사는 A㈜가 보유중인 비상장주식(C)의 매각자문업무를 수행하고 있다. 한편 최근에 3본부의 파트너(사원)인 박 회계사는 B㈜로부터 A㈜가 매각을 추진하고 있는 C주식을 매수하고 싶다는 의향과 함께 매수자문서비스를 제공해 줄 것을 요청받았다."

---

## 3. 기술적 접근 방안

### 옵션 A: CSS 기반 말줄임 (권장)

**방법**: CSS `-webkit-line-clamp` 사용

**장점**:
- 성능 우수 (브라우저 네이티브 처리)
- 반응형 자동 대응
- 구현 간단

**단점**:
- 브라우저 호환성 고려 필요 (최신 브라우저는 지원)

**구현**:
```css
.chip-text {
  display: -webkit-box;
  -webkit-line-clamp: 4;  /* 4줄까지 표시 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.45;
}
```

### 옵션 B: JavaScript 기반 말줄임

**방법**: JavaScript로 문자 수 또는 픽셀 기반 자르기

**장점**:
- 정확한 제어 가능
- 모든 브라우저 호환

**단점**:
- 성능 오버헤드
- 반응형 대응 복잡
- 구현 복잡도 증가

---

## 4. 권장 방안

### ✅ 옵션 A (CSS 기반) 권장

**이유**:
1. **성능**: 브라우저 네이티브 처리로 빠름
2. **반응형**: 자동으로 칩 크기에 맞춰 조정
3. **유지보수성**: CSS만 수정하면 됨
4. **일관성**: 다른 UI 요소와 동일한 패턴

**구현 세부사항**:
- `-webkit-line-clamp: 4` (약 4줄 표시)
- `line-height: 1.45` 유지
- `overflow: hidden` 필수
- `display: -webkit-box` 필수

---

## 5. 브라우저 호환성

### `-webkit-line-clamp` 지원

- ✅ Chrome/Edge: 지원
- ✅ Safari: 지원
- ✅ Firefox: 68+ 지원
- ⚠️ 구형 브라우저: 폴백 필요

### 폴백 전략

구형 브라우저에서는 JavaScript 기반 폴백 제공 가능 (선택사항)

---

## 6. 적용 방안

### JavaScript 수정

```javascript
// shortText → text 변경
'<div class="chip-text">' + d.text + '</div>'
```

### CSS 수정

```css
.chip-text {
  font-size: var(--fs-md);
  color: var(--text);
  line-height: 1.45;
  font-weight: 500;
  
  /* 여러 줄 말줄임 처리 */
  display: -webkit-box;
  -webkit-line-clamp: 4;  /* 4줄까지 표시 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

---

## 7. 최종 권장사항

### ✅ 즉시 적용 권장

1. **데이터 소스 변경**: `shortText` → `text`
2. **CSS 말줄임 적용**: `-webkit-line-clamp` 사용
3. **라인 수 조정**: 4줄 정도로 설정 (칩 크기 고려)

### 📝 추가 고려사항

- 칩 높이(`min-height: var(--chip-min-height)`)와 라인 수 조정 필요
- 실제 표시 확인 후 라인 수 미세 조정 가능

---

## 8. 적용 완료 사항

### JavaScript 변경
- ✅ `renderScenarioChips()` 함수에서 `d.shortText` → `d.text` 변경
- ✅ 원문(`text`) 필드 사용으로 변경

### CSS 변경
- ✅ `.chip-text`에 여러 줄 말줄임 처리 추가
- ✅ `-webkit-line-clamp: 4` 적용 (4줄까지 표시)
- ✅ `overflow: hidden`, `text-overflow: ellipsis` 적용

### 적용 결과
- 원문 텍스트가 칩에 표시됨
- 칩 크기를 고려하여 4줄까지 표시 후 '...'로 말줄임 처리
- 반응형으로 자동 조정됨

---

**검토 완료일**: 2026-02-12  
**승인 상태**: ✅ 승인 및 적용 완료
