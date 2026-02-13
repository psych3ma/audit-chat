# Empty State 레이아웃 시프트 문제 해결 (CTO 리뷰)

**작성일**: 2026-02-12  
**작성자**: CTO 관점  
**목적**: 디자이너 제안사항을 CTO 관점에서 검토하고, 유지보수성/확장성/일관성 고려하여 적용

---

## CTO 관점 검토

### 디자이너 제안사항 요약

1. **레이아웃 고정**: `justify-content: center` → `flex-start`
2. **스켈레톤 UI**: 로딩 중 시각적 플레이스홀더 표시
3. **부드러운 전환**: 스켈레톤 → 실제 콘텐츠 자연스러운 전환

### CTO 관점 평가

#### ✅ 유지보수성
- CSS 변수 사용으로 하드코딩 제거
- SSOT 원칙 준수 (SCENARIOS 배열 기반)
- 명확한 함수 분리 (`showSkeletonChips`, `initScenarioChips`)

#### ✅ 확장성
- `SCENARIOS.length` 기반 동적 처리
- 그리드 컬럼 수 자동 계산
- 새로운 시나리오 추가 시 자동 반영

#### ✅ 일관성
- 기존 코드 스타일 유지
- CSS 변수 네이밍 규칙 준수
- 기존 스켈레톤 UI 패턴 재사용 (graph-skeleton 참고)

---

## 최적화 방안

### 1. CSS 변수 통합

기존 CSS 변수와 통합하여 일관성 확보:

```css
:root {
  /* Empty state 간격 설정 - 8px 그리드 시스템 준수 */
  --empty-state-padding-top: 64px;
  --empty-state-padding-bottom: 64px;
  --empty-title-chip-gap: 48px;
  
  /* 스켈레톤 UI 설정 - 기존 패턴 재사용 */
  --skeleton-opacity-min: 0.4;
  --skeleton-opacity-max: 0.6;
  --skeleton-animation-duration: 1.5s;
  
  /* 칩 최소 높이 - 스켈레톤과 실제 칩 공통 사용 */
  --chip-min-height: 120px;
}
```

### 2. 그리드 컬럼 수 동적 계산

`SCENARIOS.length` 기반으로 자동 계산하여 확장성 확보:

```javascript
/**
 * 그리드 컬럼 수 계산 (반응형 고려)
 */
function calculateGridColumns(itemCount) {
  if (itemCount <= 1) return '1fr';
  if (itemCount <= 2) return 'repeat(2, 1fr)';
  if (itemCount <= 3) return 'repeat(3, 1fr)';
  // 4개 이상일 경우 반응형 처리
  return 'repeat(3, 1fr)';  // 기본값
}
```

### 3. 함수 구조 최적화

명확한 책임 분리 및 재사용성 고려:

```javascript
/**
 * 스켈레톤 칩 생성 (로딩 중 표시)
 * @param {HTMLElement} grid - 그리드 컨테이너 요소
 * @param {number} count - 스켈레톤 칩 개수
 */
function showSkeletonChips(grid, count) {
  if (!grid) return;
  
  grid.innerHTML = '';
  for (let i = 0; i < count; i++) {
    const skeleton = document.createElement('div');
    skeleton.className = 'chip-skeleton';
    skeleton.setAttribute('aria-hidden', 'true');  // 접근성
    grid.appendChild(skeleton);
  }
  
  // 그리드 컬럼 수 동적 설정
  grid.style.gridTemplateColumns = calculateGridColumns(count);
}

/**
 * 시나리오 칩 렌더링 (스켈레톤 제거 후 실제 칩 표시)
 * @param {HTMLElement} grid - 그리드 컨테이너 요소
 */
function renderScenarioChips(grid) {
  if (!grid) return;
  
  grid.innerHTML = '';
  
  SCENARIOS.forEach((d) => {
    const chip = document.createElement('div');
    chip.className = 'chip';
    chip.dataset.text = d.text;
    chip.onclick = function () {
      fillInput(this.dataset.text);
    };
    chip.innerHTML =
      '<div class="chip-label">' +
      escapeHtml(d.label) +
      '</div>' +
      '<div class="chip-text">' +
      escapeHtml(d.shortText) +
      '</div>' +
      '<div class="chip-arrow">출처: ' +
      escapeHtml(d.source) +
      '</div>';
    grid.appendChild(chip);
  });
  
  // 그리드 컬럼 수 동적 설정
  grid.style.gridTemplateColumns = calculateGridColumns(SCENARIOS.length);
}

/**
 * 시나리오 칩 초기화 (스켈레톤 → 실제 칩 순서)
 */
function initScenarioChips() {
  const grid = document.getElementById('scenarioChips');
  if (!grid) return;
  
  // 1. 즉시 스켈레톤 표시
  showSkeletonChips(grid, SCENARIOS.length);
  
  // 2. 다음 프레임에서 실제 칩 렌더링 (부드러운 전환)
  requestAnimationFrame(() => {
    renderScenarioChips(grid);
  });
}
```

---

## 최종 적용 방안

### CSS 변경사항

1. **CSS 변수 추가** (기존 변수와 통합)
2. **`.empty-state` 수정**: `justify-content: flex-start`
3. **`.empty-sub` 수정**: 명시적 `margin-bottom`
4. **`.suggestion-grid` 수정**: 동적 그리드 컬럼 (JavaScript에서 설정)
5. **`.chip-skeleton` 추가**: 스켈레톤 UI 스타일

### JavaScript 변경사항

1. **`calculateGridColumns()` 함수 추가**: 그리드 컬럼 수 계산
2. **`showSkeletonChips()` 함수 추가**: 스켈레톤 칩 생성
3. **`renderScenarioChips()` 함수 수정**: 그리드 컬럼 동적 설정 추가
4. **`initScenarioChips()` 함수 추가**: 초기화 로직 통합
5. **`DOMContentLoaded` 수정**: `initScenarioChips()` 호출

---

## 적용 우선순위

### Phase 1: 즉시 적용 (핵심 기능)
- CSS 레이아웃 변경 (레이아웃 시프트 제거)
- 스켈레톤 UI 추가
- 기본 초기화 로직

### Phase 2: 최적화 (확장성/유지보수성)
- 그리드 컬럼 수 동적 계산
- CSS 변수 통합
- 함수 구조 최적화

---

## 리스크 및 대응

### 리스크
1. **시각적 변경**: 레이아웃 정렬 변경으로 인한 시각적 차이
2. **성능**: 스켈레톤 UI 추가로 인한 초기 렌더링 영향 (최소)

### 대응
1. 디자인 팀 사전 검토
2. 성능 테스트 및 최적화

---

## 결론

디자이너 제안사항을 CTO 관점에서 검토한 결과, **유지보수성/확장성/일관성**을 고려한 최적화 방안을 제시했습니다. 특히:

- ✅ **SSOT 원칙 준수**: SCENARIOS 배열 기반 동적 처리
- ✅ **CSS 변수 통합**: 하드코딩 제거 및 일관성 확보
- ✅ **확장성 고려**: 그리드 컬럼 수 자동 계산
- ✅ **기존 패턴 재사용**: graph-skeleton 스타일 참고

**권장사항**: Phase 1과 Phase 2를 모두 적용하여 최적의 솔루션 구현
