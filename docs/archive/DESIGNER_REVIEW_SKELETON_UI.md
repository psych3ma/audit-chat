# 스켈레톤 UI 디자인 검토 및 개선안

**작성일**: 2026-02-12  
**작성자**: 디자이너 전문가 관점  
**검토 대상**: 스켈레톤 UI의 시각적 피드백 및 로딩 상태 표현

---

## 현재 문제 분석

### 발견된 문제점

1. **빈 화면 같은 느낌**
   - 단순한 회색 박스만 표시
   - 로딩 중임을 명확히 전달하지 못함
   - 정적인 느낌 (애니메이션이 미묘함)

2. **시각적 피드백 부족**
   - 단순한 opacity 펄스만 있음
   - 진행 중임을 암시하는 효과 부족
   - 사용자가 "멈춤" 상태로 오해할 수 있음

3. **브랜드 일관성**
   - 현재 스켈레톤이 너무 단조로움
   - 실제 콘텐츠와의 연결감 부족

---

## 디자인 원칙 분석

### 1. 로딩 상태의 시각적 표현

**핵심 가치**:
- 진행 중임을 명확히 전달
- 사용자의 기대치 설정
- 자연스러운 전환 준비

**현재 부족한 점**:
- 정적인 느낌
- 진행 중임을 암시하는 효과 부족

### 2. Shimmer 효과의 역할

**Shimmer 효과의 목적**:
- 로딩 중임을 시각적으로 전달
- 빈 화면이 아닌 "준비 중" 상태임을 암시
- 사용자의 시선을 유도하여 대기 시간 인지 감소

**적용 방법**:
- 그라데이션이 움직이는 효과
- 미묘하지만 명확한 움직임
- 브랜드 색상 활용

### 3. 스켈레톤의 구조적 표현

**원칙**:
- 실제 콘텐츠의 구조를 반영
- 칩의 내부 구조를 미리 보여줌
- 레이아웃 시프트 방지

---

## 개선 방안

### 옵션 A: Shimmer 효과 추가 (권장)

**원칙**: 그라데이션이 움직이는 Shimmer 효과로 진행 중임을 명확히 전달

#### 1. Shimmer 애니메이션
- 좌에서 우로 움직이는 그라데이션
- 미묘하지만 명확한 움직임
- 브랜드 색상(빨간색 계열) 활용

#### 2. 스켈레톤 구조 개선
- 칩의 실제 구조 반영 (라벨, 텍스트, 출처 영역)
- 더 구체적인 형태

**장점**:
- 진행 중임을 명확히 전달
- 시각적으로 풍부함
- 빈 화면이 아닌 느낌

**단점**:
- 약간의 CSS 복잡도 증가

---

### 옵션 B: 그라데이션 배경 + 펄스

**원칙**: 정적 그라데이션 배경 + opacity 펄스

- 배경에 미묘한 그라데이션
- opacity 펄스 유지
- 단순하지만 효과적

**장점**:
- 구현 간단
- 성능 우수

**단점**:
- Shimmer보다 덜 역동적

---

## 디자이너 권장사항

### 최종 권장안: 옵션 A (Shimmer 효과)

**이유**:

1. **명확한 로딩 상태 전달**
   - 움직이는 효과로 진행 중임을 명확히 전달
   - 빈 화면이 아닌 "준비 중" 상태

2. **시각적 풍부함**
   - 단조로운 회색 박스에서 벗어남
   - 사용자의 시선을 유도

3. **브랜드 일관성**
   - 브랜드 색상(빨간색 계열) 활용
   - 실제 콘텐츠와의 연결감

---

## 구현 가이드라인

### 1. Shimmer 효과 CSS

```css
/* Shimmer 효과를 위한 그라데이션 */
.chip-skeleton {
  background: var(--subtle);
  background-image: linear-gradient(
    90deg,
    var(--subtle) 0%,
    rgba(173, 27, 2, 0.08) 50%,
    var(--subtle) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
  position: relative;
  overflow: hidden;
}

@keyframes skeleton-shimmer {
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
}

/* 칩 스켈레톤 내부 구조 반영 */
.chip-skeleton::before {
  content: '';
  position: absolute;
  top: var(--space-lg);
  left: var(--space-xl);
  width: 60px;
  height: 12px;
  background: rgba(173, 27, 2, 0.15);
  border-radius: var(--space-xs);
}

.chip-skeleton::after {
  content: '';
  position: absolute;
  top: calc(var(--space-lg) + 20px);
  left: var(--space-xl);
  right: var(--space-xl);
  height: 16px;
  background: rgba(0, 0, 0, 0.08);
  border-radius: var(--space-xs);
}
```

### 2. 스켈레톤 구조 개선

```css
/* 칩 스켈레톤: 실제 칩 구조 반영 */
.chip-skeleton {
  /* Shimmer 효과 */
  background: linear-gradient(
    90deg,
    var(--subtle) 0%,
    rgba(173, 27, 2, 0.06) 50%,
    var(--subtle) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer var(--skeleton-animation-duration) ease-in-out infinite;
  
  /* 내부 구조 힌트 */
  position: relative;
}

/* 칩 내부 구조를 반영한 플레이스홀더 */
.chip-skeleton::before {
  /* 라벨 영역 */
  content: '';
  position: absolute;
  top: var(--space-lg);
  left: var(--space-xl);
  width: 60px;
  height: 12px;
  background: rgba(173, 27, 2, 0.12);
  border-radius: var(--space-xs);
}

.chip-skeleton::after {
  /* 텍스트 영역 */
  content: '';
  position: absolute;
  top: calc(var(--space-lg) + 20px);
  left: var(--space-xl);
  right: var(--space-xl);
  height: 16px;
  background: rgba(0, 0, 0, 0.06);
  border-radius: var(--space-xs);
}
```

---

## 사용자 경험 개선 효과

### Before (현재)
- 단순한 회색 박스
- 정적인 느낌
- 빈 화면 같은 느낌
- 로딩 중임을 명확히 전달하지 못함

### After (개선 후)
- Shimmer 효과로 진행 중임을 명확히 전달
- 시각적으로 풍부함
- 실제 콘텐츠 구조를 반영
- "준비 중" 상태임을 명확히 전달

---

## 디자인 원칙 준수

1. **명확성**: 진행 중임을 명확히 전달
2. **일관성**: 브랜드 색상 활용
3. **미니멀리즘**: 과도하지 않은 효과
4. **접근성**: 애니메이션은 미묘하지만 명확

---

## 결론

**권장 접근 방식**:
- ✅ Shimmer 효과 추가 (그라데이션 움직임)
- ✅ 스켈레톤 구조 개선 (실제 콘텐츠 구조 반영)
- ✅ 브랜드 색상 활용 (빨간색 계열)
- ✅ 미묘하지만 명확한 애니메이션

이 접근 방식은 **로딩 중임을 명확히 전달**하며, 빈 화면이 아닌 "준비 중" 상태임을 시각적으로 표현합니다.
