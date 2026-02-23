# Empty State 레이아웃 시프트 문제 해결 (디자이너 관점)

**작성일**: 2026-02-12  
**작성자**: 디자이너 관점  
**목적**: 새로고침 시 Empty State 텍스트가 혼자 화면 가운데 있다가 시나리오 칩 로드 후 원위치로 이동하는 레이아웃 시프트 문제 해결

---

## 문제 분석

### 현재 문제점

1. **레이아웃 시프트 (Layout Shift)**
   - 새로고침 시 Empty State 텍스트만 먼저 렌더링되어 화면 중앙에 표시됨
   - 시나리오 칩이 JavaScript로 동적 생성되어 늦게 로드됨
   - 칩이 로드되면 텍스트가 위로 이동하여 원래 위치로 돌아감
   - 사용자 경험 저하: 콘텐츠가 "튀는" 현상 발생

2. **원인 분석**
   - `.empty-state`가 `justify-content: center`로 설정되어 있음
   - `.suggestion-grid`가 비어있을 때는 높이가 0이어서 공간을 차지하지 않음
   - `renderScenarioChips()`가 `DOMContentLoaded`에서 실행되어 로딩 지연 발생

3. **시각적 영향**
   - 텍스트가 중앙에 있다가 위로 이동하는 "점프" 현상
   - 레이아웃 불안정성으로 인한 사용자 혼란
   - 전문성 저하 인상

---

## 디자인 솔루션

### 핵심 원칙

1. **레이아웃 고정**: 텍스트와 칩의 위치를 처음부터 고정
2. **스켈레톤 UI**: 로딩 중에는 시각적 플레이스홀더 표시
3. **부드러운 전환**: 스켈레톤에서 실제 콘텐츠로 자연스러운 전환

### 디자인 가이드라인

#### 1. 레이아웃 구조

```
┌─────────────────────────────────┐
│         Header                  │
├─────────────────────────────────┤
│                                 │
│    Empty State Container        │
│    (flex-start 정렬)            │
│                                 │
│    ┌─────────────────────┐     │
│    │  Eyebrow Text        │     │
│    │  Title Text          │     │
│    │  Subtitle Text       │     │
│    └─────────────────────┘     │
│                                 │
│    ┌─────────────────────┐     │
│    │  Suggestion Grid     │     │
│    │  (고정 높이 유지)     │     │
│    │                       │     │
│    │  [스켈레톤 칩들]      │     │
│    │  → [실제 칩들]        │     │
│    └─────────────────────┘     │
│                                 │
├─────────────────────────────────┤
│         Input Area              │
└─────────────────────────────────┘
```

#### 2. 스켈레톤 UI 디자인

**시각적 특징**:
- 실제 칩과 동일한 크기와 레이아웃
- 옅은 회색 배경 (`--subtle` 또는 `--gray-50`)
- 부드러운 펄스 애니메이션 (opacity 변화)
- 실제 칩의 `min-height`와 동일한 높이 유지

**애니메이션**:
- 펄스 효과: opacity 0.4 → 0.6 → 0.4 (1.5초 주기)
- 부드러운 전환: ease-in-out
- 실제 콘텐츠 로드 시 페이드아웃

#### 3. 레이아웃 고정 전략

**CSS 변경사항**:
- `.empty-state`: `justify-content: center` → `flex-start`
- `.suggestion-grid`: 최소 높이 설정 또는 스켈레톤으로 공간 확보
- 텍스트와 칩 사이 간격: 명시적 `margin-bottom` 설정

---

## 개발자 전달 사항

### 1. CSS 변경사항

#### `.empty-state` 수정
```css
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;  /* center → flex-start 변경 */
  padding: var(--empty-state-padding-top) var(--space-xl) var(--empty-state-padding-bottom);
  text-align: center;
}
```

#### `.empty-sub` 수정
```css
.empty-sub {
  font-size: var(--fs-xl);
  color: var(--muted);
  margin-bottom: var(--empty-title-chip-gap);  /* 명시적 간격 설정 */
  line-height: 1.7;
}
```

#### `.suggestion-grid` 수정
```css
.suggestion-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);  /* 또는 JavaScript에서 동적 설정 */
  gap: var(--space-md);
  width: 100%;
  max-width: 1040px;
  margin-top: 0;  /* auto 제거 */
  min-height: 120px;  /* 최소 높이 설정 (칩 1개 높이) */
}
```

#### 스켈레톤 UI 추가
```css
/* 스켈레톤 칩 스타일 */
.chip-skeleton {
  background: var(--subtle);
  border: 1.5px solid var(--border);
  border-radius: var(--space-md);
  padding: var(--space-lg) var(--space-xl);
  min-height: 120px;  /* 실제 칩과 동일한 높이 */
  opacity: 0.4;
  animation: skeleton-pulse 1.5s ease-in-out infinite;
  pointer-events: none;  /* 클릭 방지 */
}

@keyframes skeleton-pulse {
  0%, 100% {
    opacity: 0.4;
  }
  50% {
    opacity: 0.6;
  }
}
```

### 2. JavaScript 변경사항

#### 스켈레톤 칩 생성 함수 추가
```javascript
/**
 * 스켈레톤 칩 생성 (로딩 중 표시)
 */
function showSkeletonChips() {
  const grid = document.getElementById("scenarioChips");
  if (!grid) return;
  
  const skeletonCount = SCENARIOS.length;  // 실제 칩 개수와 동일
  grid.innerHTML = "";
  
  for (let i = 0; i < skeletonCount; i++) {
    const skeleton = document.createElement("div");
    skeleton.className = "chip-skeleton";
    grid.appendChild(skeleton);
  }
  
  // 그리드 컬럼 수 동적 설정
  grid.style.gridTemplateColumns = `repeat(${skeletonCount}, 1fr)`;
}
```

#### 시나리오 칩 렌더링 함수 수정
```javascript
/**
 * 시나리오 칩 렌더링 (스켈레톤 제거 후 실제 칩 표시)
 */
function renderScenarioChips() {
  const grid = document.getElementById("scenarioChips");
  if (!grid) return;
  
  // 스켈레톤 제거
  grid.innerHTML = "";
  
  // 실제 칩 생성
  SCENARIOS.forEach((d) => {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.dataset.text = d.text;
    chip.onclick = function () {
      fillInput(this.dataset.text);
    };
    chip.innerHTML =
      '<div class="chip-label">' +
      d.label +
      "</div>" +
      '<div class="chip-text">' +
      d.shortText +
      "</div>" +
      '<div class="chip-arrow">출처: ' +
      d.source +
      "</div>";
    grid.appendChild(chip);
  });
  
  // 그리드 컬럼 수 동적 설정
  grid.style.gridTemplateColumns = `repeat(${SCENARIOS.length}, 1fr)`;
}
```

#### 초기화 로직 수정
```javascript
/**
 * 시나리오 칩 초기화 (스켈레톤 → 실제 칩 순서)
 */
function initScenarioChips() {
  // 1. 즉시 스켈레톤 표시
  showSkeletonChips();
  
  // 2. 다음 프레임에서 실제 칩 렌더링
  requestAnimationFrame(() => {
    renderScenarioChips();
  });
}

// DOMContentLoaded 이벤트 수정
document.addEventListener("DOMContentLoaded", function () {
  initScenarioChips();  // renderScenarioChips() 대신 사용
  initInputMode();
  // ... 기타 초기화 코드
});
```

### 3. CSS 변수 추가 (선택사항)

```css
:root {
  /* Empty state 간격 설정 */
  --empty-state-padding-top: 64px;
  --empty-state-padding-bottom: 64px;
  --empty-title-chip-gap: 48px;  /* 제목과 칩 사이 간격 */
  
  /* 스켈레톤 UI 설정 */
  --skeleton-opacity-min: 0.4;
  --skeleton-opacity-max: 0.6;
  --skeleton-animation-duration: 1.5s;
}
```

---

## 구현 체크리스트

### CSS
- [ ] `.empty-state`의 `justify-content`를 `flex-start`로 변경
- [ ] `.empty-sub`에 명시적 `margin-bottom` 설정
- [ ] `.suggestion-grid`에 `min-height` 설정
- [ ] `.chip-skeleton` 스타일 추가
- [ ] `@keyframes skeleton-pulse` 애니메이션 추가

### JavaScript
- [ ] `showSkeletonChips()` 함수 추가
- [ ] `renderScenarioChips()` 함수 수정 (스켈레톤 제거 로직)
- [ ] `initScenarioChips()` 함수 추가
- [ ] `DOMContentLoaded`에서 `initScenarioChips()` 호출

### 테스트
- [ ] 새로고침 시 레이아웃 시프트 없음 확인
- [ ] 스켈레톤 UI가 즉시 표시되는지 확인
- [ ] 실제 칩이 로드될 때 부드러운 전환 확인
- [ ] 모바일 반응형 레이아웃 확인

---

## 예상 효과

### Before (현재)
1. 새로고침 → 텍스트만 중앙에 표시
2. JavaScript 실행 → 칩 생성
3. 칩 로드 → 텍스트가 위로 이동 (레이아웃 시프트)

### After (개선 후)
1. 새로고침 → 텍스트 + 스켈레톤 칩 즉시 표시 (고정 위치)
2. JavaScript 실행 → 실제 칩 생성
3. 실제 칩 표시 → 스켈레톤 페이드아웃 (부드러운 전환)

---

## 디자인 원칙 준수

1. **일관성**: 레이아웃이 처음부터 고정되어 일관된 경험 제공
2. **피드백**: 스켈레톤 UI로 로딩 상태를 명확히 전달
3. **안정성**: 레이아웃 시프트 제거로 안정적인 사용자 경험
4. **전문성**: 부드러운 전환으로 전문적인 느낌 유지

---

## 참고 자료

- 현재 코드: `static/audit-chat-pwc.html`
- 관련 이슈: 레이아웃 시프트 (CLS - Cumulative Layout Shift)
- 웹 표준: [Web Vitals - CLS](https://web.dev/cls/)

---

**다음 단계**: 개발팀과 협의하여 구현 및 테스트 진행
