# 점진적 렌더링 (Progressive Rendering) - CTO 검토 및 적용

**작성일**: 2026-02-12  
**작성자**: CTO 관점  
**검토 대상**: 사용자 피드백 - 빈 화면 없이 점진적 렌더링

---

## 사용자 피드백 분석

### 핵심 요구사항

1. **빈 화면 방지**: 새로고침 시 전혀 렌더링 안된 모습이 나오면 안 됨
2. **점진적 렌더링**: 빠른 요소는 즉시 표시, 느린 요소만 스켈레톤 처리
3. **"한번에"의 의미**: 모든 요소가 동시에 늦게 뜨는 것이 아니라, 각 요소가 준비되는 대로 표시

### 현재 문제점

**Before (현재 구현)**:
- 모든 콘텐츠를 스켈레톤으로 가림
- 정적 콘텐츠(타이틀, 서브타이틀)도 숨김
- 새로고침 시 빈 화면(스켈레톤만) 표시
- 사용자 경험 저하

**After (개선 방안)**:
- 정적 콘텐츠는 즉시 표시
- 동적 콘텐츠만 스켈레톤 처리
- 각 요소가 준비되는 대로 개별 전환
- 빈 화면 없음

---

## 기술적 개선 방안

### 1. HTML 구조 변경

**원칙**: 정적 콘텐츠는 즉시 표시, 동적 콘텐츠만 스켈레톤

```html
<div class="empty-state" id="emptyState">
  <!-- 정적 콘텐츠: 즉시 표시 -->
  <div class="empty-eyebrow">AI 기반 감사 독립성 검토</div>
  <div class="empty-title">수임 검토 시 복잡한 이해관계 구조를 한눈에 파악하세요</div>
  <div class="empty-sub">
    잠재적 독립성 이슈 포인트를 선제적으로 확인할 수 있습니다.
  </div>
  
  <!-- 동적 콘텐츠: 스켈레톤 → 실제 콘텐츠 -->
  <div class="suggestion-grid" id="scenarioChipsContainer">
    <!-- 스켈레톤 (초기) -->
    <div class="suggestion-grid" id="scenarioChipsSkeleton"></div>
    <!-- 실제 칩 (로딩 후) -->
    <div class="suggestion-grid" id="scenarioChips" style="display: none;"></div>
  </div>
</div>
```

### 2. JavaScript 로직 변경

**원칙**: 점진적 렌더링, 개별 전환

```javascript
/**
 * 점진적 렌더링 초기화
 * 정적 콘텐츠는 즉시 표시, 동적 콘텐츠만 스켈레톤 처리
 */
function initPageLoad() {
  // 정적 콘텐츠는 이미 HTML에 표시되어 있음
  
  // 동적 콘텐츠(시나리오 칩)만 스켈레톤 처리
  showChipSkeleton();
  
  // 시나리오 칩 렌더링 및 전환
  initScenarioChips();
}

/**
 * 시나리오 칩 스켈레톤 표시
 */
function showChipSkeleton() {
  const skeletonGrid = document.getElementById('scenarioChipsSkeleton');
  const chipGrid = document.getElementById('scenarioChips');
  
  if (skeletonGrid && SCENARIOS && SCENARIOS.length > 0) {
    skeletonGrid.style.display = 'grid';
    if (chipGrid) chipGrid.style.display = 'none';
    showSkeletonChips(skeletonGrid, SCENARIOS.length);
  }
}

/**
 * 시나리오 칩 스켈레톤 제거 및 실제 칩 표시
 */
function hideChipSkeleton() {
  const skeletonGrid = document.getElementById('scenarioChipsSkeleton');
  const chipGrid = document.getElementById('scenarioChips');
  
  if (skeletonGrid) skeletonGrid.style.display = 'none';
  if (chipGrid) chipGrid.style.display = 'grid';
}
```

---

## 성능 및 UX 개선 효과

### Before (현재)
- 새로고침 시 빈 화면 (스켈레톤만)
- 모든 콘텐츠가 동시에 나타남
- 사용자 혼란

### After (개선 후)
- 정적 콘텐츠 즉시 표시
- 동적 콘텐츠만 스켈레톤 처리
- 점진적 렌더링으로 자연스러운 전환
- 빈 화면 없음

---

## 구현 우선순위

### Phase 1: 핵심 개선 (즉시 적용)
1. ✅ HTML 구조 변경 (정적 콘텐츠 즉시 표시)
2. ✅ JavaScript 로직 변경 (점진적 렌더링)
3. ✅ 스켈레톤 범위 축소 (칩만 처리)

---

**검토 완료일**: 2026-02-12  
**승인 상태**: ✅ 승인 및 즉시 적용 권장
