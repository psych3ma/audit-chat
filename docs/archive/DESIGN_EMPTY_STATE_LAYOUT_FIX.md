# Empty State 레이아웃 안정화 및 스켈레톤 UI 적용

## 📋 개요

**작성일**: 2026-02-12  
**작성자**: 디자인팀  
**검토자**: CTO  
**대상**: 개발팀  
**우선순위**: 중  
**버전**: 2.0 (CTO 검토 반영)

---

## 🐛 문제 상황

### 현재 동작
1. **새로고침 시**: Empty state 텍스트(eyebrow, title, sub)만 중앙에 표시됨
2. **시나리오 칩 로딩 후**: 텍스트가 위로 이동하며 칩이 나타남
3. **사용자 경험**: 레이아웃이 흔들리며 불안정한 느낌

### 원인 분석
- `empty-state`가 `justify-content: center`로 설정되어 있어, 칩이 없을 때 텍스트가 중앙에 배치됨
- 시나리오 칩이 `DOMContentLoaded`에서 동적으로 렌더링되어 로딩 지연 발생 가능
- 로딩 상태에 대한 시각적 피드백 없음

---

## ✅ 해결 방안

### 1. 레이아웃 고정 (Layout Stability)

**목표**: 텍스트와 칩의 위치를 항상 고정하여 레이아웃 시프트 방지

#### 변경 사항
- `empty-state`의 `justify-content: center` → `justify-content: flex-start`로 변경
- 텍스트 영역은 상단 고정, 칩 영역은 하단 고정
- 칩이 없어도 텍스트 위치는 변하지 않도록 유지

#### CSS 수정

**원칙**: CSS 변수 활용, 하드코딩 최소화

```css
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;  /* center → flex-start */
  padding: calc(var(--space-2xl) * 2) var(--space-xl) var(--space-2xl);
  text-align: center;
}

/* 텍스트 영역 상단 고정 */
.empty-state > .empty-eyebrow,
.empty-state > .empty-title,
.empty-state > .empty-sub {
  /* 기존 스타일 유지 */
}

/* 칩 그리드 영역 */
.suggestion-grid {
  margin-top: auto;  /* 하단 정렬 */
  width: 100%;
  max-width: 1040px;
  /* 그리드 컬럼은 JavaScript에서 동적으로 설정 (SCENARIOS.length 기반) */
}
```

---

### 2. 스켈레톤 UI 적용 (Skeleton Loading)

**목표**: 시나리오 칩 로딩 중 시각적 피드백 제공

#### 디자인 가이드

**스켈레톤 스타일**
- **색상**: `var(--subtle)` 또는 `var(--gray-200)` (옅은 회색)
- **투명도**: `opacity: 0.4` (옅게)
- **애니메이션**: 부드러운 펄스 효과 (선택사항)
- **레이아웃**: 실제 칩과 동일한 크기/간격 유지

**스켈레톤 구조**
- 칩 개수: **`SCENARIOS.length` 기반 동적 생성** (하드코딩 금지)
- 각 칩: 실제 칩과 동일한 `min-height: 120px` (CSS 변수 `--chip-min-height` 사용 권장)
- 그리드: **JavaScript에서 `SCENARIOS.length` 기반으로 동적 설정** (반응형 고려)

#### CSS 예시

**원칙**: CSS 변수 활용, 실제 칩 스타일과 일관성 유지

```css
/* CSS 변수 추가 (:root에 정의) */
:root {
  /* 스켈레톤 UI 설정 */
  --skeleton-opacity-min: 0.4;
  --skeleton-opacity-max: 0.6;
  --skeleton-animation-duration: 1.5s;
  --chip-min-height: 120px;  /* 실제 칩과 동일 */
}

/* 스켈레톤 칩 */
.chip-skeleton {
  background: var(--subtle);
  border: 1.5px solid var(--border);
  border-radius: var(--space-md);
  padding: var(--space-lg) var(--space-xl);
  min-height: var(--chip-min-height);
  opacity: var(--skeleton-opacity-min);
  animation: skeleton-pulse var(--skeleton-animation-duration) ease-in-out infinite;
  /* 접근성: 스크린 리더에서 무시 */
  pointer-events: none;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: var(--skeleton-opacity-min); }
  50% { opacity: var(--skeleton-opacity-max); }
}

/* 스켈레톤 그리드 - grid-template-columns는 JavaScript에서 동적 설정 */
.suggestion-grid.skeleton {
  display: grid;
  /* grid-template-columns는 JavaScript에서 SCENARIOS.length 기반으로 설정 */
  gap: var(--space-md);
  width: 100%;
  max-width: 1040px;
}
```

#### JavaScript 로직

**원칙**: 
- SSOT 준수 (`SCENARIOS` 배열 기반)
- 하드코딩 제거 (칩 개수, 그리드 컬럼 수 동적 계산)
- 에러 처리 및 엣지 케이스 고려
- 성능 최적화 (requestAnimationFrame 활용)
- 접근성 고려 (aria 속성)

```javascript
/**
 * 그리드 컬럼 수 계산 (반응형 고려)
 * @param {number} itemCount - 아이템 개수
 * @returns {string} CSS grid-template-columns 값
 */
function calculateGridColumns(itemCount) {
  // 반응형: 1개면 1열, 2개면 2열, 3개 이상이면 3열
  const columns = Math.min(itemCount, 3);
  return `repeat(${columns}, 1fr)`;
}

/**
 * 스켈레톤 UI 표시
 * SSOT: SCENARIOS.length 기반으로 동적 생성
 */
function showSkeletonChips() {
  const grid = document.getElementById('scenarioChips');
  if (!grid) {
    console.warn('[showSkeletonChips] scenarioChips element not found');
    return;
  }
  
  // SCENARIOS가 비어있으면 스켈레톤 표시하지 않음
  if (!SCENARIOS || SCENARIOS.length === 0) {
    console.warn('[showSkeletonChips] SCENARIOS array is empty');
    return;
  }
  
  grid.className = 'suggestion-grid skeleton';
  grid.style.gridTemplateColumns = calculateGridColumns(SCENARIOS.length);
  grid.setAttribute('aria-busy', 'true');
  grid.setAttribute('aria-label', '시나리오 로딩 중');
  grid.innerHTML = '';
  
  // SCENARIOS.length 기반으로 스켈레톤 칩 생성 (하드코딩 금지)
  for (let i = 0; i < SCENARIOS.length; i++) {
    const skeleton = document.createElement('div');
    skeleton.className = 'chip-skeleton';
    skeleton.setAttribute('aria-hidden', 'true');
    grid.appendChild(skeleton);
  }
}

/**
 * 실제 칩 렌더링
 * SSOT: SCENARIOS 배열 기반 (기존 함수 수정)
 */
function renderScenarioChips() {
  const grid = document.getElementById('scenarioChips');
  if (!grid) {
    console.warn('[renderScenarioChips] scenarioChips element not found');
    return;
  }
  
  // 스켈레톤 제거
  grid.className = 'suggestion-grid';
  grid.removeAttribute('aria-busy');
  grid.removeAttribute('aria-label');
  grid.style.gridTemplateColumns = calculateGridColumns(SCENARIOS.length);
  grid.innerHTML = '';
  
  // 에러 처리: SCENARIOS가 비어있을 경우
  if (!SCENARIOS || SCENARIOS.length === 0) {
    console.warn('[renderScenarioChips] SCENARIOS array is empty');
    return;
  }
  
  SCENARIOS.forEach((d) => {
    const chip = document.createElement('div');
    chip.className = 'chip';
    chip.dataset.text = d.text;
    chip.onclick = function() { fillInput(this.dataset.text); };
    chip.innerHTML = 
      '<div class="chip-label">' + d.label + '</div>' +
      '<div class="chip-text">' + d.shortText + '</div>' +
      '<div class="chip-arrow">출처: ' + d.source + '</div>';
    grid.appendChild(chip);
  });
}

/**
 * 초기화: 스켈레톤 먼저 표시 후 실제 칩 렌더링
 * 성능: requestAnimationFrame 활용하여 리플로우 최소화
 */
function initScenarioChips() {
  // 스켈레톤 즉시 표시
  showSkeletonChips();
  
  // 다음 프레임에서 실제 칩 렌더링 (스켈레톤이 보이도록)
  requestAnimationFrame(() => {
    // 짧은 딜레이로 스켈레톤이 보이도록 (선택사항, 필요시 제거 가능)
    requestAnimationFrame(() => {
      renderScenarioChips();
    });
  });
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
  initScenarioChips();  // 스켈레톤 → 실제 칩 순서로 초기화
  initInputMode();      // 입력 모드 초기화
});
```

**주요 개선사항**:
1. ✅ **SSOT 준수**: `SCENARIOS.length` 기반 동적 생성 (하드코딩 제거)
2. ✅ **반응형 그리드**: `calculateGridColumns()` 함수로 동적 계산
3. ✅ **에러 처리**: grid 없음, SCENARIOS 비어있음 케이스 처리
4. ✅ **성능**: `requestAnimationFrame` 활용, 불필요한 리플로우 최소화
5. ✅ **접근성**: `aria-busy`, `aria-label`, `aria-hidden` 속성 추가
6. ✅ **확장성**: 칩 개수 변경 시 자동 반영 (코드 수정 불필요)

---

## 🎨 디자인 상세

### 레이아웃 구조
```
┌─────────────────────────────────┐
│                                 │
│      [Eyebrow]                  │  ← 상단 고정
│      [Title]                    │
│      [Subtitle]                 │
│                                 │
│                                 │
│   ┌─────┐ ┌─────┐ ┌─────┐     │
│   │칩 1 │ │칩 2 │ │칩 3 │     │  ← 하단 고정
│   └─────┘ └─────┘ └─────┘     │
│                                 │
└─────────────────────────────────┘
```

### 스켈레톤 UI 시각적 표현
- **색상**: `#f4f1ed` (--subtle) 또는 `#e0e0e0` (--gray-200)
- **투명도**: 40% (옅게)
- **애니메이션**: 펄스 효과 (선택사항, 부드럽게)
- **크기**: 실제 칩과 동일

---

## 📝 구현 체크리스트

### CSS 수정
- [ ] `:root`에 스켈레톤 관련 CSS 변수 추가 (`--skeleton-opacity-min`, `--skeleton-opacity-max`, `--chip-min-height`)
- [ ] `.empty-state`의 `justify-content: center` → `flex-start` 변경
- [ ] `.suggestion-grid`에 `margin-top: auto` 추가
- [ ] `.chip-skeleton` 스타일 정의 (CSS 변수 사용)
- [ ] `.skeleton-pulse` 애니메이션 정의 (CSS 변수 사용)

### JavaScript 수정
- [ ] `calculateGridColumns(itemCount)` 함수 추가 (반응형 그리드 계산)
- [ ] `showSkeletonChips()` 함수 추가 (SSOT 기반, 에러 처리 포함)
- [ ] `renderScenarioChips()` 함수 수정 (스켈레톤 제거, 그리드 컬럼 동적 설정)
- [ ] `initScenarioChips()` 함수 추가 (초기화 로직 통합)
- [ ] `DOMContentLoaded`에서 `initScenarioChips()` 호출

### 테스트 항목

**기능 테스트**
- [ ] 새로고침 시 텍스트 위치 고정 확인 (레이아웃 시프트 없음)
- [ ] 스켈레톤 UI 표시 확인 (SCENARIOS.length 개수만큼)
- [ ] 실제 칩 로딩 후 스켈레톤 제거 확인
- [ ] 그리드 컬럼 수가 SCENARIOS.length에 맞게 동적 설정되는지 확인

**엣지 케이스**
- [ ] SCENARIOS가 비어있을 때 (스켈레톤 표시하지 않음)
- [ ] SCENARIOS.length가 1개일 때 (1열 그리드)
- [ ] SCENARIOS.length가 2개일 때 (2열 그리드)
- [ ] SCENARIOS.length가 3개 이상일 때 (3열 그리드)

**성능 테스트**
- [ ] requestAnimationFrame 활용으로 리플로우 최소화 확인
- [ ] 다양한 네트워크 환경에서 테스트 (느린 네트워크 시뮬레이션)

**접근성 테스트**
- [ ] 스크린 리더에서 로딩 상태 인식 확인 (`aria-busy`, `aria-label`)
- [ ] 스켈레톤 칩 클릭 불가 확인 (`pointer-events: none`)

**확장성 테스트**
- [ ] SCENARIOS 배열에 칩 추가 시 자동 반영 확인
- [ ] SCENARIOS 배열에서 칩 제거 시 자동 반영 확인

---

## 🔍 CTO 검토 사항

### 확장성 (Scalability)
- ✅ **SSOT 원칙**: `SCENARIOS` 배열이 단일 소스, 칩 개수 변경 시 자동 반영
- ✅ **동적 그리드**: `calculateGridColumns()` 함수로 반응형 그리드 자동 계산
- ✅ **CSS 변수**: 하드코딩된 값들을 CSS 변수로 관리 (`--chip-min-height`, `--skeleton-opacity-*`)
- ✅ **반응형**: 칩 개수가 1개, 2개, 3개 이상일 때 모두 대응

### 유지보수성 (Maintainability)
- ✅ **하드코딩 제거**: 칩 개수, 그리드 컬럼 수 모두 동적 계산
- ✅ **함수 분리**: `showSkeletonChips()`, `renderScenarioChips()`, `calculateGridColumns()` 분리
- ✅ **에러 처리**: 엣지 케이스 (grid 없음, SCENARIOS 비어있음) 처리
- ✅ **일관성**: 기존 코드 패턴과 일치 (SSOT, 함수 네이밍 컨벤션)

### 성능 (Performance)
- ✅ **requestAnimationFrame**: 리플로우/리페인트 최소화
- ✅ **즉시 피드백**: 스켈레톤은 즉시 표시, 실제 칩은 다음 프레임에서 렌더링
- ✅ **불필요한 작업 제거**: SCENARIOS가 비어있으면 스켈레톤 표시하지 않음

### 접근성 (Accessibility)
- ✅ **ARIA 속성**: `aria-busy="true"`, `aria-label`, `aria-hidden` 추가
- ✅ **스크린 리더**: 로딩 상태를 스크린 리더가 인식할 수 있도록 처리
- ✅ **포인터 이벤트**: 스켈레톤은 `pointer-events: none`으로 클릭 방지

### 테스트 가능성 (Testability)
- ✅ **함수 분리**: 각 함수가 독립적으로 테스트 가능
- ✅ **의존성 명확화**: `SCENARIOS`, `document.getElementById` 등 명시적 의존성
- ✅ **에러 로깅**: `console.warn`으로 디버깅 지원

### 코드 품질 (Code Quality)
- ✅ **JSDoc 주석**: 함수별 설명 및 파라미터 타입 명시
- ✅ **일관된 네이밍**: 기존 코드 컨벤션 준수
- ✅ **단일 책임**: 각 함수가 하나의 책임만 수행

---

## 📌 우선순위

1. **높음**: 레이아웃 고정 (사용자 경험 개선)
2. **높음**: SSOT 기반 동적 생성 (확장성/유지보수성)
3. **중간**: 스켈레톤 UI (시각적 피드백)
4. **중간**: 접근성 개선 (ARIA 속성)

---

## 🔧 구현 시 주의사항

### 필수 사항
1. **하드코딩 금지**: 칩 개수, 그리드 컬럼 수는 모두 `SCENARIOS.length` 기반
2. **SSOT 준수**: `SCENARIOS` 배열이 단일 소스, 다른 곳에서 하드코딩하지 않기
3. **에러 처리**: grid 없음, SCENARIOS 비어있음 케이스 반드시 처리
4. **CSS 변수**: 하드코딩된 값은 CSS 변수로 관리

### 권장 사항
1. **성능**: `requestAnimationFrame` 활용
2. **접근성**: ARIA 속성 추가
3. **로깅**: 에러 발생 시 `console.warn`으로 디버깅 지원

---

## 📚 관련 문서

- `docs/WORKFLOW_STEP_CODE_MAPPING.md`: SSOT 원칙 및 단계별 코드 매칭
- `docs/CODE_REVIEW_CTO.md`: CTO 코드 리뷰 가이드라인
- `static/audit-chat-pwc.html`: 실제 구현 파일 (SCENARIOS 배열 정의 위치)

---

## 💬 문의

디자인 관련 문의: 디자인팀  
기술 구현 관련 문의: 개발팀  
아키텍처 관련 문의: CTO
