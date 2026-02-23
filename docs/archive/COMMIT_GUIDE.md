# GitHub 커밋 가이드

**작성일**: 2026-02-12  
**목적**: 타이포그래피 시스템 표준화 및 Empty state 텍스트 변경 커밋

---

## 변경사항 요약

### 1. 타이포그래피 시스템 표준화 (CTO 리뷰 반영)

#### CSS 변수 변경
- ✅ `--fs-micro: 12px` 추가
- ✅ `--fs-md: 17px` → `16px` 변경
- ✅ `--fs-lg: 18px` → `17px` 변경
- ✅ `--fs-xl: 17px` → `18px` 변경
- ✅ 컴포넌트별 변수 제거 (`--chip-desc-size`, `--chip-source-size`)

#### 사용처 변경
- ✅ `.chip-text`: `var(--fs-lg)` → `var(--fs-md)` (16px)
- ✅ `.chip-arrow`: `var(--fs-base)` → `var(--fs-micro)` (12px)
- ✅ `.post-chip-text`: `var(--fs-md)` 유지 (16px)
- ✅ `.progress-desc`: `calc(var(--fs-sm) - 1px)` → `var(--fs-xs)` (13px)
- ✅ `.law-link-icon`: `0.85em` → `var(--fs-micro)` (12px)
- ✅ JavaScript 인라인: `1rem` → `var(--fs-md)` (16px)

### 2. Empty State 텍스트 변경

- ✅ Eyebrow: "감사 독립성 검토" → "AI 기반 감사 독립성 검토"
- ✅ Title: "감사 독립성 시나리오를 AI로 검토해보세요" → "수임 검토 시 복잡한 이해관계 구조를 한눈에 파악하세요"
- ✅ Subtitle: "수임 가능성, 주요 이슈, 권고 안전장치 검토를 지원합니다." → "잠재적 독립성 이슈 포인트를 선제적으로 확인할 수 있습니다."

### 3. 문서 추가

- ✅ `docs/UX_TYPOGRAPHY_ANALYSIS.md` - UX Writer 관점 분석
- ✅ `docs/CTO_TYPOGRAPHY_REVIEW.md` - CTO 관점 검토 및 최적화 방안
- ✅ `docs/COPY_ALTERNATIVES_EMPTY_STATE.md` - Empty state 텍스트 대안
- ✅ `docs/DESIGN_EMPTY_STATE_LAYOUT_FIX.md` - Empty state 레이아웃 수정
- ✅ `docs/UX_LAYOUT_COMPREHENSIVE_REVIEW.md` - 전체 레이아웃 리뷰
- ✅ `docs/UX_SPACING_TITLE_CHIPS.md` - 제목-칩 간격 조정

---

## 커밋 방법

### 옵션 1: 단일 커밋 (권장)

```bash
# 변경된 파일 확인
git status

# 모든 변경사항 스테이징
git add static/audit-chat-pwc.html
git add docs/

# 커밋
git commit -m "refactor: 타이포그래피 시스템 표준화 및 Empty state 텍스트 변경

- 타이포그래피 표준 스케일 재정의 (8단계)
  - --fs-micro (12px) 추가
  - --fs-md: 17px → 16px
  - --fs-lg: 18px → 17px
  - --fs-xl: 17px → 18px
  - 컴포넌트별 변수 제거 (--chip-desc-size, --chip-source-size)
- 사용처 변경 (6곳)
  - calc() 제거, 하드코딩 제거
- Empty state 텍스트 업데이트
  - Eyebrow, Title, Subtitle 변경
- 문서 추가
  - 타이포그래피 분석 및 리뷰 문서
  - UX/디자인 관련 문서

Refs: docs/CTO_TYPOGRAPHY_REVIEW.md"

# GitHub에 푸시
git push origin main
```

### 옵션 2: 분리 커밋 (선택사항)

```bash
# 1. 타이포그래피 시스템 변경만 커밋
git add static/audit-chat-pwc.html
git commit -m "refactor: 타이포그래피 시스템 표준화

- 표준 스케일 재정의 (8단계)
- 변수 개수 감소: 9개 → 8개
- 중복 제거 및 일관성 확보

Refs: docs/CTO_TYPOGRAPHY_REVIEW.md"

# 2. Empty state 텍스트 변경 커밋
git add static/audit-chat-pwc.html
git commit -m "feat: Empty state 텍스트 업데이트

- Eyebrow, Title, Subtitle 변경
- 사용자 경험 개선

Refs: docs/COPY_ALTERNATIVES_EMPTY_STATE.md"

# 3. 문서 추가 커밋
git add docs/
git commit -m "docs: 타이포그래피 및 UX 관련 문서 추가

- 타이포그래피 분석 및 리뷰 문서
- UX/디자인 관련 문서"

# GitHub에 푸시
git push origin main
```

---

## 커밋 메시지 가이드

### 커밋 타입
- `refactor`: 코드 리팩토링 (타이포그래피 시스템 변경)
- `feat`: 새로운 기능 (Empty state 텍스트 변경)
- `docs`: 문서 추가/수정

### 커밋 메시지 구조
```
<type>: <제목>

<본문>
- 변경사항 1
- 변경사항 2

Refs: <관련 문서>
```

---

## 확인 사항

커밋 전 확인:
- [ ] 린터 오류 없음
- [ ] 변경사항이 의도한 대로 적용됨
- [ ] 문서가 올바르게 추가됨

커밋 후 확인:
- [ ] GitHub에 정상적으로 푸시됨
- [ ] 변경사항이 올바르게 반영됨

---

## 롤백 방법 (필요시)

```bash
# 마지막 커밋 취소 (변경사항 유지)
git reset --soft HEAD~1

# 마지막 커밋 취소 (변경사항 삭제)
git reset --hard HEAD~1

# 특정 파일만 되돌리기
git restore static/audit-chat-pwc.html
```

---

## 참고 자료

- 타이포그래피 분석: `docs/UX_TYPOGRAPHY_ANALYSIS.md`
- CTO 리뷰: `docs/CTO_TYPOGRAPHY_REVIEW.md`
- 변경된 파일: `static/audit-chat-pwc.html`
