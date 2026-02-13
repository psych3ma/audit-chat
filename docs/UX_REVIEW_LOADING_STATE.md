# 페이지 로딩 상태 UX 검토 및 개선안

**작성일**: 2026-02-12  
**작성자**: UX 전문가 관점  
**검토 대상**: 새로고침 시 요소들이 제각각 나타나는 문제

---

## 현재 문제 분석

### 발견된 문제점

1. **요소별 로딩 순서 불일치**
   - 헤더, 타이틀, 서브타이틀, 시나리오 칩이 각각 다른 시점에 나타남
   - 사용자에게 "깜빡거림" 또는 "불안정한" 느낌 제공

2. **스켈레톤 UI 부족**
   - 시나리오 칩만 스켈레톤 UI가 있음
   - 타이틀, 서브타이틀 등 텍스트 요소는 스켈레톤 없음
   - 헤더 로고 이미지 로딩 시 스켈레톤 없음

3. **스켈레톤 표시 시간 부족**
   - `requestAnimationFrame`으로 즉시 렌더링되어 스켈레톤이 거의 보이지 않음
   - 사용자가 로딩 상태를 인지하기 어려움

4. **Cumulative Layout Shift (CLS)**
   - 요소가 순차적으로 나타나면서 레이아웃이 흔들림
   - 사용자 경험 저하

---

## UX 원칙 분석

### 1. 일관된 로딩 경험

**핵심 가치**:
- 모든 요소가 동일한 패턴으로 로딩
- 사용자가 예측 가능한 로딩 순서 경험
- 시각적 안정성 제공

**현재 문제**:
- 요소별로 다른 로딩 방식
- 예측 불가능한 나타남 순서

### 2. 스켈레톤 UI의 역할

**스켈레톤 UI의 목적**:
- 로딩 중임을 명확히 전달
- 최종 레이아웃을 미리 보여줌 (레이아웃 시프트 방지)
- 사용자의 기대치 설정

**현재 부족한 점**:
- 일부 요소만 스켈레톤 적용
- 스켈레톤 표시 시간이 너무 짧음

### 3. 인지적 부하 감소

**원칙**:
- 로딩 상태를 명확히 표시
- 불필요한 깜빡임 제거
- 부드러운 전환 효과

---

## 개선 방안

### 옵션 A: 전체 스켈레톤 UI 적용 (권장)

**원칙**: 모든 주요 요소에 스켈레톤 UI 적용

#### 1. 헤더 스켈레톤
- 로고 이미지 로딩 전 스켈레톤 표시
- 텍스트 영역 스켈레톤

#### 2. Empty State 스켈레톤
- 타이틀 스켈레톤
- 서브타이틀 스켈레톤
- 시나리오 칩 스켈레톤 (기존 유지)

#### 3. 최소 로딩 시간 보장
- 스켈레톤을 최소 300-500ms 표시
- 너무 빠른 전환은 사용자가 인지하지 못함

**장점**:
- 일관된 로딩 경험
- 레이아웃 시프트 방지
- 전문적인 느낌

**단점**:
- 약간의 추가 개발 시간
- CSS 코드 증가

---

### 옵션 B: 핵심 요소만 스켈레톤

**원칙**: 가장 눈에 띄는 요소만 스켈레톤 적용

- 시나리오 칩만 스켈레톤 (현재 상태)
- 타이틀/서브타이틀은 즉시 표시

**장점**:
- 구현 간단
- 빠른 적용 가능

**단점**:
- 일관성 부족
- 여전히 깜빡임 발생 가능

---

## UX 전문가 권장사항

### 최종 권장안: 옵션 A (전체 스켈레톤 UI)

**이유**:

1. **일관된 사용자 경험**
   - 모든 요소가 동일한 패턴으로 로딩
   - 사용자가 예측 가능한 경험

2. **시각적 안정성**
   - 레이아웃 시프트 최소화
   - 전문적인 느낌

3. **로딩 상태 명확화**
   - 사용자가 로딩 중임을 명확히 인지
   - 불필요한 혼란 방지

---

## 구현 가이드라인

### 1. CSS 스켈레톤 스타일 추가

```css
/* 텍스트 스켈레톤 */
.text-skeleton {
  background: var(--subtle);
  border-radius: var(--space-xs);
  height: 1.2em;
  opacity: var(--skeleton-opacity-min);
  animation: skeleton-pulse var(--skeleton-animation-duration) ease-in-out infinite;
  margin-bottom: var(--space-sm);
}

.text-skeleton.title {
  height: 1.5em;
  width: 60%;
  margin: 0 auto var(--space-md);
}

.text-skeleton.subtitle {
  height: 1.3em;
  width: 80%;
  margin: 0 auto var(--empty-title-chip-gap);
}

/* 로고 스켈레톤 */
.logo-skeleton {
  width: 120px;
  height: 28px;
  background: var(--subtle);
  border-radius: var(--space-xs);
  opacity: var(--skeleton-opacity-min);
  animation: skeleton-pulse var(--skeleton-animation-duration) ease-in-out infinite;
}
```

### 2. HTML 구조 수정

```html
<!-- 헤더 스켈레톤 (초기 상태) -->
<div class="header" id="header">
  <div class="header-skeleton" id="headerSkeleton">
    <div class="logo-skeleton"></div>
    <div class="text-skeleton" style="width: 200px;"></div>
  </div>
  <!-- 실제 헤더 내용 (로딩 후 표시) -->
  <button class="header-home-trigger" id="headerContent" style="display: none;">
    <!-- 실제 내용 -->
  </button>
</div>

<!-- Empty State 스켈레톤 (초기 상태) -->
<div class="empty-state" id="emptyState">
  <div class="empty-state-skeleton" id="emptyStateSkeleton">
    <div class="text-skeleton title"></div>
    <div class="text-skeleton subtitle"></div>
    <div class="suggestion-grid" id="scenarioChips">
      <!-- 스켈레톤 칩 (기존 로직 사용) -->
    </div>
  </div>
  <!-- 실제 내용 (로딩 후 표시) -->
  <div class="empty-state-content" id="emptyStateContent" style="display: none;">
    <!-- 실제 내용 -->
  </div>
</div>
```

### 3. JavaScript 로딩 로직 수정

```javascript
/**
 * 전체 페이지 로딩 시퀀스
 * 1. 스켈레톤 표시
 * 2. 최소 로딩 시간 보장 (300-500ms)
 * 3. 실제 콘텐츠 렌더링
 * 4. 스켈레톤 제거 및 콘텐츠 표시
 */
function initPageLoad() {
  // 1. 스켈레톤 표시
  showAllSkeletons();
  
  // 2. 최소 로딩 시간 보장
  const minLoadTime = 400; // ms
  const startTime = performance.now();
  
  // 3. 실제 콘텐츠 준비
  Promise.all([
    initScenarioChips(),
    initHeader(),
    initEmptyState()
  ]).then(() => {
    // 4. 최소 로딩 시간 확인 후 전환
    const elapsed = performance.now() - startTime;
    const remainingTime = Math.max(0, minLoadTime - elapsed);
    
    setTimeout(() => {
      hideAllSkeletons();
      showAllContent();
    }, remainingTime);
  });
}

function showAllSkeletons() {
  // 헤더 스켈레톤
  document.getElementById('headerSkeleton')?.style.display = 'flex';
  document.getElementById('headerContent')?.style.setProperty('display', 'none');
  
  // Empty State 스켈레톤
  document.getElementById('emptyStateSkeleton')?.style.display = 'block';
  document.getElementById('emptyStateContent')?.style.setProperty('display', 'none');
  
  // 시나리오 칩 스켈레톤
  const grid = document.getElementById("scenarioChips");
  if (grid) {
    showSkeletonChips(grid, SCENARIOS.length);
  }
}

function hideAllSkeletons() {
  // 헤더
  document.getElementById('headerSkeleton')?.style.setProperty('display', 'none');
  document.getElementById('headerContent')?.style.setProperty('display', 'flex');
  
  // Empty State
  document.getElementById('emptyStateSkeleton')?.style.setProperty('display', 'none');
  document.getElementById('emptyStateContent')?.style.setProperty('display', 'block');
}

function showAllContent() {
  // 실제 콘텐츠는 이미 렌더링되어 있음
  // 스켈레톤만 제거하면 됨
}
```

---

## 사용자 경험 개선 효과

### Before (현재)
- 요소들이 제각각 나타남
- 깜빡거림 발생
- 불안정한 느낌
- 레이아웃 시프트 발생

### After (개선 후)
- 일관된 로딩 순서
- 부드러운 전환
- 안정적인 느낌
- 레이아웃 시프트 최소화
- 전문적인 사용자 경험

---

## 성능 고려사항

### 최소 로딩 시간 설정

**권장값**: 300-500ms

**이유**:
- 너무 짧으면 (100ms 미만): 사용자가 스켈레톤을 인지하지 못함
- 너무 길면 (1000ms 이상): 불필요한 대기 시간

**적용 방법**:
- `performance.now()`로 실제 로딩 시간 측정
- 최소 시간과 실제 시간 중 더 큰 값 사용

---

## 접근성 고려사항

### 스켈레톤 UI 접근성

1. **ARIA 속성**
   ```html
   <div class="empty-state-skeleton" aria-busy="true" aria-label="콘텐츠 로딩 중">
   ```

2. **스크린 리더**
   - 스켈레톤은 `aria-hidden="true"` 설정
   - 로딩 상태는 `aria-live` 영역으로 알림

---

## 구현 우선순위

### Phase 1: 핵심 개선 (즉시 적용)
1. ✅ 시나리오 칩 스켈레톤 최소 표시 시간 보장
2. ✅ Empty State 타이틀/서브타이틀 스켈레톤 추가

### Phase 2: 전체 개선 (선택적)
3. 헤더 로고 스켈레톤 추가
4. 전체 로딩 시퀀스 통합

---

## 결론

**권장 접근 방식**:
- ✅ 전체 스켈레톤 UI 적용
- ✅ 최소 로딩 시간 보장 (300-500ms)
- ✅ 일관된 로딩 순서
- ✅ 부드러운 전환 효과

이 접근 방식은 **일관되고 전문적인 사용자 경험**을 제공하며, 레이아웃 시프트를 최소화합니다.
