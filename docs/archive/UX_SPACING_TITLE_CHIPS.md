# 제목과 시나리오 칩 간격 조정 요청

## 📋 개요

**작성일**: 2026-02-12  
**작성자**: UX 전문가  
**검토자**: CTO  
**대상**: 개발팀  
**우선순위**: 중  
**버전**: 2.0 (CTO 검토 반영)  
**이슈**: 제목 영역과 시나리오 칩 사이의 수직 간격이 과도하여 시각적 연결성이 떨어짐

---

## 🎯 문제 분석

### 현재 상황

**시각적 문제**:
- 제목/서브타이틀과 시나리오 칩 사이에 과도한 여백 존재
- 두 요소가 시각적으로 분리되어 보여 관련성이 약해 보임
- 사용자가 제목을 읽고 칩을 찾는 데 인지적 부담 증가

**기술적 원인**:
1. `.empty-sub`의 `margin-bottom: 40px` (하드코딩)
2. `.suggestion-grid`의 `margin-top: auto` (하단 정렬을 위한 auto 마진)
3. 두 요소의 조합으로 인해 실제 간격이 예상보다 훨씬 큼

### UX 원칙 위반

| 원칙 | 현재 상태 | 이상적 상태 |
|------|----------|------------|
| **시각적 그룹핑** | 제목과 칩이 분리되어 보임 | 제목과 칩이 하나의 콘텐츠 블록으로 인식 |
| **인지적 부담** | 사용자가 두 요소의 연결을 파악하기 어려움 | 자연스러운 흐름으로 이해 가능 |
| **스캔 효율성** | 시선 이동 거리가 과도함 | 적절한 간격으로 빠른 스캔 가능 |
| **시각적 계층** | 간격이 너무 커서 계층 구조가 불명확 | 명확한 계층 구조 유지 |

---

## 📐 권장 간격 기준

### UX 가이드라인

**제목과 인터랙티브 요소 간 적절한 간격**:
- **최소 간격**: 32px (시각적 연결성 유지)
- **권장 간격**: 40px - 56px (명확한 구분 + 연결성)
- **최대 간격**: 64px (과도한 분리)

**현재 추정 간격**: 약 80px+ (과도함)

### 시각적 계층 구조

```
┌─────────────────────────────────┐
│  [Eyebrow]                      │
│  [Title]                         │
│  [Subtitle]                      │
│                                  │
│  ← 적절한 간격 (40-56px)        │
│                                  │
│  ┌─────┐ ┌─────┐ ┌─────┐       │
│  │칩 1 │ │칩 2 │ │칩 3 │       │
│  └─────┘ └─────┘ └─────┘       │
│                                  │
└─────────────────────────────────┘
```

---

## ✅ 해결 방안

### 옵션 1: 고정 마진 사용 (권장)

**목표**: 제목과 칩 사이에 적절한 고정 간격 설정

**변경 사항**:
1. `.empty-sub`의 `margin-bottom`을 CSS 변수 기반으로 조정
2. `.suggestion-grid`의 `margin-top: auto` 제거
3. `.suggestion-grid`에 고정 `margin-top` 적용

**CSS 수정**:

**원칙**: CSS 변수 활용, 8px 그리드 시스템 준수, 반응형 대응

```css
/* CSS 변수 추가 (:root에 정의) */
:root {
  /* Empty state 간격 설정 - 8px 그리드 시스템 준수 */
  --empty-title-chip-gap: 48px;  /* 6 * 8px: 제목과 칩 사이 권장 간격 */
  --empty-title-chip-gap-mobile: 40px;  /* 5 * 8px: 모바일 간격 */
}

.empty-sub {
  font-size: var(--fs-xl);
  color: var(--muted);
  margin-bottom: var(--empty-title-chip-gap);  /* 하드코딩 제거, CSS 변수 사용 */
  line-height: 1.7;
}

.suggestion-grid {
  display: grid;
  gap: var(--space-md);
  width: 100%;
  max-width: 1040px;
  margin-top: 0;  /* auto 제거: 명시적으로 0으로 설정 */
}

/* 반응형: 모바일에서 간격 조정 */
@media (max-width: 768px) {
  .empty-sub {
    margin-bottom: var(--empty-title-chip-gap-mobile);
  }
}
```

**장점**:
- ✅ 예측 가능한 간격
- ✅ CSS 변수로 유지보수 용이
- ✅ 시각적 연결성 개선
- ✅ 반응형 대응 가능

---

### 옵션 2: 상대적 간격 사용

**목표**: 제목 크기에 비례한 간격 설정

**CSS 수정**:
```css
.empty-sub {
  font-size: var(--fs-xl);
  color: var(--muted);
  margin-bottom: calc(var(--fs-2xl) * 1.5);  /* 제목 크기의 1.5배 */
  line-height: 1.7;
}

.suggestion-grid {
  display: grid;
  gap: var(--space-md);
  width: 100%;
  max-width: 1040px;
  margin-top: 0;
}
```

**장점**:
- ✅ 제목 크기와 비례하여 조화로움
- ✅ 반응형에서도 일관된 비율 유지

**단점**:
- ⚠️ 계산식이 복잡할 수 있음

---

### 옵션 3: 그리드 컨테이너 래핑 (고급)

**목표**: 제목과 칩을 하나의 콘텐츠 그룹으로 묶기

**HTML 구조 변경**:
```html
<div class="empty-state" id="emptyState">
  <div class="empty-content">
    <div class="empty-eyebrow">감사 독립성 검토</div>
    <div class="empty-title">감사 독립성 시나리오를 AI로 검토해보세요</div>
    <div class="empty-sub">수임 가능성, 주요 이슈, 권고 안전장치 검토를 지원합니다.</div>
    <div class="suggestion-grid" id="scenarioChips"></div>
  </div>
</div>
```

**CSS 수정**:
```css
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;  /* 중앙 정렬 복원 */
  padding: calc(var(--space-2xl) * 2) var(--space-xl) var(--space-2xl);
  text-align: center;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 1040px;
  width: 100%;
}

.empty-sub {
  margin-bottom: var(--empty-title-chip-gap);
}

.suggestion-grid {
  margin-top: 0;
}
```

**장점**:
- ✅ 제목과 칩을 하나의 그룹으로 명확히 묶음
- ✅ 중앙 정렬 유지 가능
- ✅ 구조적으로 더 명확함

**단점**:
- ⚠️ HTML 구조 변경 필요
- ⚠️ 기존 레이아웃 로직 수정 필요

---

## 🎨 최종 권장안

### 추천: 옵션 1 (고정 마진 사용)

**이유**:
1. **최소 변경**: HTML 구조 변경 없이 CSS만 수정
2. **명확성**: 간격 값이 명시적이고 이해하기 쉬움
3. **유지보수성**: CSS 변수로 관리하여 일관성 유지
4. **효과적**: 문제를 가장 간단하게 해결

**구현**:

**CTO 검토 반영**: CSS 변수, 8px 그리드 시스템, 반응형 대응

```css
:root {
  /* Empty state 간격 설정 - 8px 그리드 시스템 준수 */
  --empty-title-chip-gap: 48px;  /* 6 * 8px: 데스크톱 간격 */
  --empty-title-chip-gap-mobile: 40px;  /* 5 * 8px: 모바일 간격 */
}

.empty-sub {
  font-size: var(--fs-xl);
  color: var(--muted);
  margin-bottom: var(--empty-title-chip-gap);  /* 하드코딩 제거 */
  line-height: 1.7;
}

.suggestion-grid {
  display: grid;
  gap: var(--space-md);
  width: 100%;
  max-width: 1040px;
  margin-top: 0;  /* auto 제거: 명시적 설정 */
}

/* 반응형 대응 */
@media (max-width: 768px) {
  .empty-sub {
    margin-bottom: var(--empty-title-chip-gap-mobile);
  }
}
```

---

## 📏 간격 값 검증

### 권장 간격: 48px

**근거**:
- **8px 그리드 시스템**: `48px = 6 * 8px` (일관된 스케일)
- **시각적 테스트**: 제목과 칩이 연결되어 보이면서도 명확히 구분됨
- **접근성**: 충분한 간격으로 스캔 가능성 확보
- **반응형**: 모바일에서도 적절한 간격 유지

### 대안 값

| 값 | 효과 | 권장 상황 |
|----|------|----------|
| **40px** | 더 타이트한 연결감 | 콘텐츠가 많을 때 |
| **48px** | 균형잡힌 간격 (권장) | 일반적인 경우 |
| **56px** | 여유로운 간격 | 여백을 강조하고 싶을 때 |

---

## 🔍 추가 고려사항

### 반응형 대응

**모바일 환경**:
- 간격을 약간 줄여도 무방 (40px 정도)
- 화면 공간이 제한적이므로 타이트한 레이아웃 선호

**CSS 예시**:

**CTO 검토 반영**: 별도 CSS 변수 사용으로 명확성 향상

```css
:root {
  --empty-title-chip-gap: 48px;  /* 데스크톱 */
  --empty-title-chip-gap-mobile: 40px;  /* 모바일: 별도 변수로 관리 */
}

.empty-sub {
  margin-bottom: var(--empty-title-chip-gap);
}

@media (max-width: 768px) {
  .empty-sub {
    margin-bottom: var(--empty-title-chip-gap-mobile);  /* 계산식 대신 명시적 변수 사용 */
  }
}
```

**CTO 관점 개선사항**:
- ✅ 계산식(`calc()`) 대신 별도 변수 사용으로 가독성 향상
- ✅ 모바일 간격도 8px 그리드 시스템 준수 (40px = 5 * 8px)
- ✅ 유지보수성: 간격 변경 시 변수만 수정하면 됨

### 시각적 계층 유지

**중요**: 간격 조정 후에도 다음을 유지해야 함:
- ✅ 제목 영역의 상단 여백 (현재 `padding-top` 유지)
- ✅ 칩 그리드의 하단 여백 (입력 영역과의 간격)
- ✅ 전체 레이아웃의 균형감

---

## 🔧 CTO 검토 사항

### 확장성 (Scalability)
- ✅ **CSS 변수 활용**: 간격 값 변경 시 한 곳만 수정하면 전체 반영
- ✅ **8px 그리드 시스템**: 일관된 스케일로 확장 가능
- ✅ **반응형 대응**: 모바일/태블릿/데스크톱 각각 최적화된 간격 제공
- ✅ **재사용성**: 다른 empty state에도 동일한 변수 적용 가능

### 유지보수성 (Maintainability)
- ✅ **하드코딩 제거**: `40px` → CSS 변수 사용
- ✅ **명시적 변수**: 계산식 대신 별도 변수로 가독성 향상
- ✅ **일관성**: 기존 spacing scale과 동일한 패턴 유지
- ✅ **문서화**: CSS 변수명으로 의도 명확히 전달

### 코드 품질 (Code Quality)
- ✅ **명확한 네이밍**: `--empty-title-chip-gap`으로 용도 명확
- ✅ **반응형 분리**: 모바일/데스크톱 간격을 별도 변수로 관리
- ✅ **예측 가능성**: `margin-top: auto` 제거로 레이아웃 동작 예측 가능

---

## 📝 구현 체크리스트

### CSS 수정
- [ ] `:root`에 `--empty-title-chip-gap: 48px` 변수 추가 (8px 그리드 시스템)
- [ ] `:root`에 `--empty-title-chip-gap-mobile: 40px` 변수 추가
- [ ] `.empty-sub`의 `margin-bottom: 40px` → `var(--empty-title-chip-gap)` 변경
- [ ] `.suggestion-grid`의 `margin-top: auto` 제거, `margin-top: 0` 설정
- [ ] 반응형 미디어 쿼리 추가 (모바일 간격 적용)

### 테스트 항목

**기능 테스트**
- [ ] 데스크톱에서 제목과 칩 간격 확인 (48px)
- [ ] 모바일에서 간격 확인 (40px)
- [ ] 시각적 연결성 확인 (제목과 칩이 하나의 그룹으로 보이는지)
- [ ] 전체 레이아웃 균형 확인 (상단/하단 여백 유지)

**확장성 테스트**
- [ ] CSS 변수 변경 시 전체 반영 확인
- [ ] 다른 empty state에도 동일 패턴 적용 가능한지 확인

**반응형 테스트**
- [ ] 다양한 화면 크기에서 테스트 (320px, 768px, 1024px, 1440px)
- [ ] 브레이크포인트 전환 시 간격 변화 확인

---

## 🎯 기대 효과

### Before (현재)
- ❌ 제목과 칩이 시각적으로 분리되어 보임
- ❌ 사용자가 두 요소의 연결을 파악하기 어려움
- ❌ 불필요한 스크롤 발생 가능

### After (개선 후)
- ✅ 제목과 칩이 하나의 콘텐츠 블록으로 인식
- ✅ 자연스러운 시선 흐름으로 사용성 개선
- ✅ 시각적 계층 구조가 명확해짐
- ✅ 전체적인 레이아웃 균형감 향상

---

## 📚 참고 자료

### 관련 문서
- `docs/DESIGN_EMPTY_STATE_LAYOUT_FIX.md`: 레이아웃 고정 관련 문서
- `docs/UX-copy-review-request.md`: UX 문구 검토 문서

### UX 원칙
- **8px 그리드 시스템**: 일관된 간격 스케일 유지
- **시각적 계층**: 관련 요소는 가까이, 불관련 요소는 멀리
- **인지적 부담 최소화**: 불필요한 시선 이동 제거

---

## 🔍 CTO 검토 요약

### 주요 개선사항
1. ✅ **CSS 변수 기반**: 하드코딩 제거, 유지보수성 향상
2. ✅ **8px 그리드 시스템**: `48px = 6 * 8px`, `40px = 5 * 8px` (일관된 스케일)
3. ✅ **반응형 대응**: 모바일/데스크톱 별도 변수로 명확한 관리
4. ✅ **명시적 설정**: `margin-top: auto` 제거로 예측 가능한 레이아웃
5. ✅ **확장성**: 다른 empty state에도 동일 패턴 적용 가능

### 구현 우선순위
1. **높음**: CSS 변수 추가 및 간격 조정 (핵심 기능)
2. **중간**: 반응형 대응 (사용자 경험 개선)

---

## 💬 문의

UX 관련 문의: UX 전문가  
기술 구현 관련 문의: 개발팀  
아키텍처 관련 문의: CTO
