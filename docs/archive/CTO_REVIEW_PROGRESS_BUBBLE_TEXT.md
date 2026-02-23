# 진행중 버블 텍스트 스타일 수정 - CTO 검토

**작성일**: 2026-02-12  
**작성자**: CTO 관점  
**검토 대상**: 진행중 버블의 텍스트 폰트 크기 및 굵기 수정

---

## 검토 개요

사용자가 요청한 진행중 버블의 텍스트 스타일 변경을 기술적 관점에서 검토하고, CSS 변수 활용 및 일관성을 고려하여 적용합니다.

---

## 1. 현재 상태 분석

### 현재 스타일

**1열 (`.progress-step-line`)**: 
- `font-size: var(--fs-sm)` → **14px**
- `font-weight: 600` (semi-bold)
- 예시: "(2/3) 독립성 분석"

**2열 (`.progress-desc`)**:
- `font-size: var(--fs-xs)` → **12px**
- `font-weight: 400` (regular)
- 예시: "추출된 구조를 바탕으로 수임 가능성과 위험을 판단하고 있습니다."

---

## 2. 요청사항 분석

### 사용자 요구사항

- **1열**: 기존 font-size → **16px (bold)**
- **2열**: 기존 font-size → **16px**

### 기술적 해석

- 1열: `font-size: 16px`, `font-weight: 700` (bold)
- 2열: `font-size: 16px`, `font-weight: 400` (regular, 유지)

---

## 3. CSS 변수 활용 방안

### 현재 CSS 변수

```css
--fs-base: 16px;  /* 16px에 해당하는 변수 */
```

### 권장 적용

**1열 (`.progress-step-line`)**:
- `font-size: var(--fs-base)` → 16px (CSS 변수 활용)
- `font-weight: 700` → bold

**2열 (`.progress-desc`)**:
- `font-size: var(--fs-base)` → 16px (CSS 변수 활용)
- `font-weight: 400` → regular (유지)

---

## 4. 기술적 검토

### ✅ 승인 권고

요청사항은 **기술적으로 타당하며, CSS 변수를 활용하여 일관성 있게 적용 가능**합니다.

### 장점

1. **CSS 변수 활용**: `--fs-base` 사용으로 유지보수성 향상
2. **일관성**: 다른 16px 텍스트와 동일한 변수 사용
3. **가독성 향상**: 14px/12px → 16px로 더 읽기 쉬움
4. **정보 위계 명확화**: 1열 bold로 단계명 강조

### 고려사항

- `line-height` 조정 필요 여부 확인 (현재 1.4, 1.45)
- 두 줄 모두 16px로 통일되어 시각적 균형 확인 필요

---

## 5. 적용 방안

### CSS 수정

```css
.workflow-progress .progress-step-line {
  font-size: var(--fs-base);  /* 14px → 16px */
  line-height: 1.4;
  color: var(--gray-500);
  font-weight: 700;  /* 600 → 700 (bold) */
}

.workflow-progress .progress-desc {
  font-size: var(--fs-base);  /* 12px → 16px */
  line-height: 1.45;
  color: var(--gray-500);
  font-weight: 400;  /* 유지 */
  white-space: nowrap;
}
```

---

## 6. 최종 권장사항

### ✅ 즉시 적용 권장

1. **CSS 변수 활용**: `--fs-base` 사용
2. **폰트 크기**: 두 줄 모두 16px로 통일
3. **폰트 굵기**: 1열 700 (bold), 2열 400 (regular)

---

**검토 완료일**: 2026-02-12  
**승인 상태**: ✅ 승인 및 적용 권장
