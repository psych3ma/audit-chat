# 로고 클릭 인터랙션 UX 검토 및 개선안

**작성일**: 2026-02-12  
**작성자**: UX 전문가 관점  
**검토 대상**: 로고 클릭 인터랙션 시각적 피드백

---

## 현재 구현 상태 검토

### 발견된 시각적 요소

1. **호버 시 배경색 변화**
   - 현재: `background-color: rgba(173, 27, 2, 0.05)` (옅은 빨간색 배경)
   - 문제점: 사용자가 "옅은 빨간색 효과 없었으면해"라고 명시

2. **포커스 시 Outline**
   - 현재: `outline: 2px solid var(--red)` (빨간색 테두리)
   - 문제점: 사용자가 "겉에 박스테두리 없었으면해"라고 명시

---

## UX 원칙 분석

### 1. 미니멀리즘 원칙

**핵심 가치**:
- 불필요한 시각적 요소 제거
- 깔끔하고 정제된 인터페이스
- 브랜드 영역의 신뢰성과 전문성 강조

**현재 문제**:
- 호버/포커스 시 과도한 시각적 변화로 인한 시각적 노이즈
- 로고 영역이 "버튼"처럼 보이는 것에 대한 거부감

### 2. 발견 가능성 vs 시각적 침투성

**균형점 찾기**:
- 클릭 가능함을 알리되, 과도하지 않게
- 웹 표준 패턴에 의존 (로고 클릭 = 홈 이동은 일반적)
- 시각적 힌트보다는 **커서 변화**로 충분할 수 있음

### 3. 접근성 고려사항

**키보드 사용자**:
- 포커스 표시는 **필수**이지만, 덜 침투적인 방식으로 가능
- `outline` 대신 `box-shadow` 또는 더 미묘한 방식 고려

---

## 개선 방안

### 옵션 A: 미니멀 접근 (권장)

**원칙**: 최소한의 시각적 변화만 유지

```css
.header-home-trigger {
  /* 기본 스타일 유지 */
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin: 0;
  padding: var(--space-xs) var(--space-sm);
  border: none;
  background: transparent;
  cursor: pointer;
  font: inherit;
  color: inherit;
  text-align: left;
  /* transition 제거 또는 최소화 */
}

.header-home-trigger:hover {
  /* 배경색 변화 제거 */
  /* 커서만 pointer로 충분 */
}

.header-home-trigger:focus-visible {
  /* outline 대신 더 미묘한 방식 */
  outline: none;
  box-shadow: 0 0 0 2px rgba(173, 27, 2, 0.2) inset;
  /* 또는 완전히 제거하고 브라우저 기본 포커스 사용 */
}

.header-home-trigger:active {
  /* 활성 상태도 제거 또는 최소화 */
  opacity: 0.95;
}
```

**장점**:
- 깔끔하고 미니멀한 디자인
- 브랜드 영역의 신뢰성 유지
- 시각적 노이즈 최소화

**단점**:
- 클릭 가능함을 알리는 힌트가 약할 수 있음 (하지만 웹 표준 패턴으로 보완 가능)

---

### 옵션 B: 매우 미묘한 피드백

**원칙**: 거의 보이지 않지만 존재하는 피드백

```css
.header-home-trigger:hover {
  /* 배경색 대신 opacity 미세 조정 */
  opacity: 0.92;
}

.header-home-trigger:focus-visible {
  /* outline 대신 매우 옅은 box-shadow */
  outline: none;
  box-shadow: 0 0 0 1px rgba(173, 27, 2, 0.15) inset;
}
```

**장점**:
- 최소한의 피드백 유지
- 접근성 요구사항 충족

---

### 옵션 C: 완전 제거 (최소한)

**원칙**: 커서 변화만으로 충분

```css
.header-home-trigger {
  /* 기본 스타일만 */
  cursor: pointer;
  /* 호버/포커스 스타일 모두 제거 */
}

.header-home-trigger:hover {
  /* 아무 스타일 없음 */
}

.header-home-trigger:focus-visible {
  /* 브라우저 기본 포커스 사용 */
  /* 또는 outline: none; */
}
```

**장점**:
- 가장 깔끔한 디자인
- 시각적 침투성 제로

**단점**:
- 접근성 측면에서 포커스 표시 부재 가능성
- 키보드 사용자 경험 저하 가능

---

## UX 전문가 권장사항

### 최종 권장안: 옵션 A (미니멀 접근)

**이유**:

1. **웹 표준 패턴 신뢰**
   - 로고 클릭 = 홈 이동은 웹의 보편적 패턴
   - 사용자는 이미 이 패턴을 알고 있음
   - 과도한 시각적 힌트 불필요

2. **브랜드 영역의 신뢰성**
   - 로고 영역은 브랜드 아이덴티티의 핵심
   - "버튼"처럼 보이는 것은 브랜드 가치를 떨어뜨릴 수 있음
   - 미니멀한 접근이 더 전문적

3. **커서 변화로 충분**
   - `cursor: pointer`만으로도 클릭 가능함을 충분히 전달
   - 마우스 호버 시 커서 변화가 가장 직관적

4. **접근성 균형**
   - 키보드 포커스는 유지하되, 덜 침투적인 방식 사용
   - `box-shadow` inset 방식으로 테두리 없이 포커스 표시 가능

---

## 구현 가이드라인

### CSS 수정사항

```css
.header-home-trigger {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin: 0;
  padding: var(--space-xs) var(--space-sm);
  border: none;
  background: transparent;
  cursor: pointer;
  font: inherit;
  color: inherit;
  text-align: left;
  /* transition 제거 - 즉각적인 반응 */
}

/* 호버: 배경색 제거, 커서만 pointer */
.header-home-trigger:hover {
  /* 배경색 변화 없음 */
}

/* 포커스: 테두리 없이 미묘한 내부 그림자 */
.header-home-trigger:focus-visible {
  outline: none;
  box-shadow: 0 0 0 2px rgba(173, 27, 2, 0.15) inset;
  border-radius: var(--space-xs);
}

/* 활성: 최소한의 피드백 */
.header-home-trigger:active {
  opacity: 0.95;
}
```

### CSS 변수 정리

기존에 추가한 `--logo-hover-bg` 변수는 더 이상 사용하지 않으므로 제거 가능:

```css
/* 제거 가능 */
/* --logo-hover-bg: rgba(173, 27, 2, 0.05); */
```

---

## 사용자 피드백 반영

### 요구사항
- ✅ "겉에 박스테두리 없었으면해" → `outline` 제거, `box-shadow` inset 사용
- ✅ "옅은 빨간색 효과 없었으면해" → 호버 배경색 제거

### 유지사항
- ✅ 커서 변화 (`cursor: pointer`) - 클릭 가능함 전달
- ✅ 키보드 접근성 - 포커스 표시 (미묘한 방식)
- ✅ 기능적 동작 - 로고 클릭 시 홈 이동

---

## 예상 효과

### Before (현재)
- 호버 시 옅은 빨간색 배경 표시
- 포커스 시 빨간색 테두리 표시
- 시각적으로 "버튼"처럼 보임

### After (개선 후)
- 호버 시 커서만 변화 (배경색 없음)
- 포커스 시 미묘한 내부 그림자 (테두리 없음)
- 깔끔하고 전문적인 브랜드 영역 유지
- 클릭 가능함은 커서 변화로 전달

---

## UX 원칙 준수

1. **미니멀리즘**: 불필요한 시각적 요소 제거
2. **신뢰성**: 브랜드 영역의 전문성 유지
3. **직관성**: 웹 표준 패턴에 의존
4. **접근성**: 키보드 사용자 지원 (미묘한 방식)
5. **일관성**: 전체 디자인 시스템과 조화

---

## 결론

사용자의 피드백을 반영하여 **미니멀한 접근 방식**을 권장합니다:

- ✅ 호버 배경색 제거
- ✅ 포커스 테두리 제거 (대신 미묘한 내부 그림자)
- ✅ 커서 변화만으로 클릭 가능함 전달
- ✅ 웹 표준 패턴에 의존

이 접근 방식은 더 깔끔하고 전문적인 사용자 경험을 제공하며, 브랜드 영역의 신뢰성을 유지합니다.
