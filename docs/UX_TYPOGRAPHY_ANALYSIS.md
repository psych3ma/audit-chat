# 타이포그래피 시스템 분석 및 표준화 제안

**작성일**: 2026-02-12  
**작성자**: UX Writer 관점  
**목적**: 현재 코드에서 사용 중인 텍스트 크기를 조사하고, 정보 위계별 일관성 있는 타이포그래피 시스템 제안

---

## 1. 현재 텍스트 크기 사용 현황

### 1.1 CSS 변수 정의 (`:root`)

| 변수명 | 크기 | 문제점 |
|--------|------|--------|
| `--fs-xs` | 13px | ✅ 표준 스케일 내 |
| `--fs-sm` | 14px | ✅ 표준 스케일 내 |
| `--fs-base` | 15px | ✅ 표준 스케일 내 (기본 본문) |
| `--fs-md` | 17px | ⚠️ `--fs-xl`과 중복 |
| `--fs-lg` | 18px | ✅ 표준 스케일 내 |
| `--fs-xl` | 17px | ⚠️ `--fs-md`와 중복 |
| `--fs-2xl` | 26px | ✅ 표준 스케일 내 |
| `--chip-desc-size` | 16px | ⚠️ 표준 스케일 외부 |
| `--chip-source-size` | 12px | ⚠️ 표준 스케일 외부 |

**주요 문제점**:
- `--fs-md`와 `--fs-xl`이 동일한 17px로 중복 정의됨
- 칩 관련 크기(`--chip-desc-size`, `--chip-source-size`)가 표준 스케일에 포함되지 않음
- 12px, 16px가 표준 스케일에 없어 일관성 저하

---

### 1.2 정보 위계별 사용 현황

#### 📌 **Level 1: 메인 헤딩 (Hero/Page Title)**
| 사용 위치 | 현재 크기 | 변수 | 빈도 |
|----------|----------|------|------|
| `.empty-title` | 26px | `--fs-2xl` | 1회 |
| `.report-verdict` | 26px | `--fs-2xl` | 1회 |

**특징**: 가장 큰 크기, 페이지/섹션의 핵심 메시지

---

#### 📌 **Level 2: 서브 헤딩 (Section Title)**
| 사용 위치 | 현재 크기 | 변수 | 빈도 |
|----------|----------|------|------|
| `.empty-sub` | 17px | `--fs-xl` | 1회 |
| `.user-bubble` | 17px | `--fs-xl` | 1회 |
| `.assistant-bubble` | 17px | `--fs-xl` | 1회 |
| `textarea` | 17px | `--fs-xl` | 1회 |
| `.header-service` | 17px | `--fs-xl` | 1회 |
| `.reset-btn` | 17px | `--fs-md` | 1회 |
| `.opinion-text` | 17px | `--fs-md` | 1회 |
| `.graph-skeleton` | 17px | `--fs-md` | 1회 |

**특징**: 
- 17px로 통일되어 있으나 변수가 `--fs-xl`과 `--fs-md`로 혼재
- 사용 빈도가 높음 (8회)

---

#### 📌 **Level 3: 본문 텍스트 (Body Text)**
| 사용 위치 | 현재 크기 | 변수 | 빈도 |
|----------|----------|------|------|
| `.empty-eyebrow` | 15px | `--fs-base` | 1회 |
| `.section-title` | 15px | `--fs-base` | 2회 |
| `.law-box` | 15px | `--fs-base` | 1회 |
| `.box-item` | 15px | `--fs-base` | 1회 |
| `.input-hint` | 15px | `--fs-base` | 1회 |
| `.post-chips-label` | 15px | `--fs-base` | 1회 |
| `.independence-report` 관련 | 15px | `--fs-base` | 5회 |

**특징**: 
- 가장 많이 사용되는 크기 (12회 이상)
- 기본 본문 텍스트로 적절

---

#### 📌 **Level 4: 강조 본문 (Emphasized Body)**
| 사용 위치 | 현재 크기 | 변수 | 빈도 |
|----------|----------|------|------|
| `.chip-text` | 16px | `--chip-desc-size` | 1회 |
| `.post-chip-text` | 16px | `--chip-desc-size` | 1회 |

**특징**: 
- 칩 설명 텍스트에만 사용
- 표준 스케일에 없어 일관성 저하

---

#### 📌 **Level 5: 작은 텍스트 (Small Text)**
| 사용 위치 | 현재 크기 | 변수 | 빈도 |
|----------|----------|------|------|
| `.powered-by` | 14px | `--fs-sm` | 1회 |
| `.header-badge` | 14px | `--fs-sm` | 1회 |
| `.chip-label` | 14px | `--fs-sm` | 1회 |
| `.report-id` | 14px | `--fs-sm` | 1회 |
| `.report-risk-label` | 14px | `--fs-sm` | 1회 |
| `.box-title` | 14px | `--fs-sm` | 1회 |
| `.box-item::before` | 14px | `--fs-sm` | 1회 |
| `.progress-step-line` | 14px | `--fs-sm` | 1회 |
| `.post-chip-label` | 14px | `--fs-sm` | 1회 |
| JavaScript 에러 메시지 | 14px | `--fs-sm` | 3회 |

**특징**: 
- 라벨, 메타 정보, 보조 텍스트에 사용
- 사용 빈도 높음 (11회 이상)

---

#### 📌 **Level 6: 매우 작은 텍스트 (Extra Small)**
| 사용 위치 | 현재 크기 | 변수 | 빈도 |
|----------|----------|------|------|
| `.flow-edge-label` | 13px | `--fs-xs` | 1회 |
| `.progress-desc` | 13px | `calc(--fs-sm - 1px)` | 1회 |
| JavaScript 에러 상세 | 13px | `--fs-xs` | 1회 |

**특징**: 
- 차트/다이어그램 라벨, 프로그레스 설명에 사용
- `calc(--fs-sm - 1px)` 같은 임시 계산식 사용

---

#### 📌 **Level 7: 특수 크기 (Special Cases)**
| 사용 위치 | 현재 크기 | 변수 | 빈도 | 문제점 |
|----------|----------|------|------|--------|
| `.chip-arrow` | 12px | `--chip-source-size` | 1회 | 표준 스케일 외부 |
| `.law-link-icon` | ~12.75px | `0.85em` | 1회 | 상대 단위 혼재 |
| 리포트 헤더 h2 | 16px | `1rem` (하드코딩) | 1회 | JavaScript 인라인 |

**특징**: 
- 하드코딩 및 상대 단위 혼재
- 표준화 필요

---

#### 📌 **Level 8: 특수 요소 (Special Elements)**
| 사용 위치 | 현재 크기 | 변수 | 빈도 |
|----------|----------|------|------|
| `.risk-pill` | 18px | `--fs-lg` | 1회 |
| `.flow-node` | 18px | `--fs-lg` | 1회 |
| `.flow-arrow` | 18px | `--fs-lg` | 1회 |

**특징**: 
- 인터랙티브 요소, 다이어그램 노드에 사용
- 적절한 크기

---

## 2. 문제점 분석

### 2.1 구조적 문제

1. **중복 정의**
   - `--fs-md` (17px) = `--fs-xl` (17px) → 혼란 야기

2. **표준 스케일 외부 변수**
   - `--chip-desc-size` (16px), `--chip-source-size` (12px)가 표준 스케일에 없음
   - 일관성 저하 및 유지보수 어려움

3. **임시 계산식 사용**
   - `calc(var(--fs-sm) - 1px)` → 명확한 의도 부족

4. **하드코딩 및 상대 단위 혼재**
   - `1rem`, `0.85em` 등 CSS 변수 미사용

### 2.2 정보 위계 문제

1. **명확한 역할 정의 부족**
   - 같은 크기(17px)를 서로 다른 변수로 사용
   - 정보 위계와 크기 매핑이 불명확

2. **의미론적 네이밍 부재**
   - `--fs-*` 형식만 사용, 용도별 네이밍 없음

---

## 3. 표준화 제안 방안

### 방안 1: 정보 위계 중심 표준화 (권장)

**핵심 원칙**: 정보 위계에 따라 명확한 역할을 부여하고, 각 역할에 대응하는 크기를 표준화

#### 3.1.1 표준 타이포그래피 스케일 재정의

```css
:root {
  /* === 정보 위계별 타이포그래피 스케일 === */
  
  /* Level 1: Hero/Page Title */
  --fs-hero: 26px;           /* 메인 페이지 타이틀 */
  
  /* Level 2: Section Heading */
  --fs-heading: 20px;        /* 섹션 제목 (현재 없음, 새로 추가) */
  
  /* Level 3: Subheading/Body Large */
  --fs-subheading: 17px;     /* 서브 헤딩, 강조 본문 */
  
  /* Level 4: Body Text (기본) */
  --fs-body: 15px;           /* 기본 본문 텍스트 */
  
  /* Level 5: Body Medium */
  --fs-body-medium: 16px;    /* 칩 설명 등 강조 본문 */
  
  /* Level 6: Small Text */
  --fs-small: 14px;          /* 라벨, 메타 정보 */
  
  /* Level 7: Extra Small */
  --fs-xs: 13px;            /* 차트 라벨, 보조 정보 */
  
  /* Level 8: Micro Text */
  --fs-micro: 12px;         /* 출처, 아이콘 텍스트 */
  
  /* === 레거시 호환성 (기존 코드 유지) === */
  --fs-2xl: var(--fs-hero);
  --fs-xl: var(--fs-subheading);
  --fs-lg: 18px;            /* 특수 요소용 유지 */
  --fs-md: var(--fs-subheading);
  --fs-base: var(--fs-body);
  --fs-sm: var(--fs-small);
  
  /* === 컴포넌트별 특수 크기 (표준 스케일 기반) === */
  --chip-desc-size: var(--fs-body-medium);
  --chip-source-size: var(--fs-micro);
}
```

#### 3.1.2 정보 위계별 사용 가이드

| 위계 | 크기 | 변수 | 사용 예시 | 폰트 웨이트 |
|------|------|------|----------|------------|
| **Hero** | 26px | `--fs-hero` | 페이지 메인 타이틀, 리포트 결론 | 800-900 |
| **Heading** | 20px | `--fs-heading` | 섹션 제목 (새로 추가) | 700 |
| **Subheading** | 17px | `--fs-subheading` | 서브 타이틀, 입력 필드, 버튼 | 500-600 |
| **Body** | 15px | `--fs-body` | 기본 본문 텍스트 | 400 |
| **Body Medium** | 16px | `--fs-body-medium` | 칩 설명, 강조 본문 | 500 |
| **Small** | 14px | `--fs-small` | 라벨, 메타 정보, 보조 텍스트 | 400-700 |
| **Extra Small** | 13px | `--fs-xs` | 차트 라벨, 프로그레스 설명 | 400-500 |
| **Micro** | 12px | `--fs-micro` | 출처, 아이콘 텍스트 | 400 |

#### 3.1.3 적용 예시

```css
/* Before */
.empty-title { font-size: var(--fs-2xl); }           /* 26px */
.empty-sub { font-size: var(--fs-xl); }            /* 17px */
.chip-text { font-size: var(--chip-desc-size); }   /* 16px */
.chip-arrow { font-size: var(--chip-source-size); } /* 12px */

/* After */
.empty-title { font-size: var(--fs-hero); }         /* 26px */
.empty-sub { font-size: var(--fs-subheading); }     /* 17px */
.chip-text { font-size: var(--fs-body-medium); }   /* 16px */
.chip-arrow { font-size: var(--fs-micro); }         /* 12px */
```

**장점**:
- ✅ 정보 위계가 명확히 드러남
- ✅ 새로운 개발자도 쉽게 이해 가능
- ✅ 레거시 호환성 유지 (`--fs-*` 변수 유지)
- ✅ 표준 스케일 확장 (12px, 16px, 20px 추가)

**단점**:
- ⚠️ 변수 수가 증가 (하지만 의미론적 명확성 확보)

---

### 방안 2: 최소화 중심 표준화

**핵심 원칙**: 기존 변수를 최대한 활용하고, 중복만 제거

#### 3.2.1 표준 타이포그래피 스케일 재정의

```css
:root {
  /* === 표준 스케일 (8단계) === */
  --fs-micro: 12px;    /* 새로 추가 */
  --fs-xs: 13px;
  --fs-sm: 14px;
  --fs-base: 15px;
  --fs-md: 16px;       /* 17px → 16px로 변경, 칩 설명과 통일 */
  --fs-lg: 18px;
  --fs-xl: 17px;       /* 유지 (서브 헤딩용) */
  --fs-2xl: 26px;
  
  /* === 컴포넌트별 크기 (표준 스케일 기반) === */
  --chip-desc-size: var(--fs-md);      /* 16px */
  --chip-source-size: var(--fs-micro); /* 12px */
}
```

#### 3.2.2 사용 가이드

| 크기 | 변수 | 사용 예시 |
|------|------|----------|
| 26px | `--fs-2xl` | Hero 타이틀 |
| 18px | `--fs-lg` | 특수 요소 (risk pill, flow node) |
| 17px | `--fs-xl` | 서브 헤딩, 입력 필드, 버튼 |
| 16px | `--fs-md` | 칩 설명, 강조 본문 |
| 15px | `--fs-base` | 기본 본문 |
| 14px | `--fs-sm` | 라벨, 메타 정보 |
| 13px | `--fs-xs` | 차트 라벨 |
| 12px | `--fs-micro` | 출처, 아이콘 텍스트 |

**장점**:
- ✅ 변수 수 최소화
- ✅ 기존 코드 변경 최소화
- ✅ `--fs-md`를 16px로 변경하여 칩 설명과 통일

**단점**:
- ⚠️ `--fs-md` 변경 시 영향 범위 확인 필요
- ⚠️ 정보 위계가 변수명에 드러나지 않음

---

### 방안 3: 하이브리드 접근 (권장 대안)

**핵심 원칙**: 정보 위계 변수 + 레거시 호환 변수 병행

#### 3.3.1 표준 타이포그래피 스케일 재정의

```css
:root {
  /* === 정보 위계별 변수 (새로 추가, 권장 사용) === */
  --fs-hero: 26px;
  --fs-heading: 20px;        /* 새로 추가 */
  --fs-subheading: 17px;
  --fs-body: 15px;
  --fs-body-medium: 16px;
  --fs-label: 14px;
  --fs-caption: 13px;
  --fs-micro: 12px;
  
  /* === 레거시 호환 변수 (기존 코드 유지) === */
  --fs-2xl: var(--fs-hero);
  --fs-xl: var(--fs-subheading);
  --fs-lg: 18px;
  --fs-md: var(--fs-subheading);  /* 17px 유지 */
  --fs-base: var(--fs-body);
  --fs-sm: var(--fs-label);
  --fs-xs: var(--fs-caption);
  
  /* === 컴포넌트별 크기 (정보 위계 변수 기반) === */
  --chip-desc-size: var(--fs-body-medium);
  --chip-source-size: var(--fs-micro);
}
```

**장점**:
- ✅ 정보 위계 명확화
- ✅ 레거시 코드 호환성 유지
- ✅ 점진적 마이그레이션 가능
- ✅ 새로운 코드는 정보 위계 변수 사용 권장

**단점**:
- ⚠️ 변수 수가 많아짐 (하지만 명확성 확보)

---

## 4. 권장 사항

### 4.1 즉시 적용 가능한 개선

1. **중복 제거**
   ```css
   /* --fs-md와 --fs-xl 통일 */
   --fs-md: 17px;
   --fs-xl: var(--fs-md);  /* 또는 반대 */
   ```

2. **표준 스케일 확장**
   ```css
   --fs-micro: 12px;  /* 새로 추가 */
   --chip-source-size: var(--fs-micro);
   ```

3. **임시 계산식 제거**
   ```css
   /* Before */
   font-size: calc(var(--fs-sm) - 1px);
   
   /* After */
   font-size: var(--fs-xs);  /* 13px */
   ```

4. **하드코딩 제거**
   ```css
   /* JavaScript에서 */
   /* Before */
   '<h2 style="font-size:1rem;">'
   
   /* After */
   '<h2 style="font-size:var(--fs-body-medium);">'  /* 또는 CSS 클래스 사용 */
   ```

### 4.2 단계적 마이그레이션 전략

**Phase 1 (즉시)**: 중복 제거 및 표준 스케일 확장
- `--fs-md`와 `--fs-xl` 통일
- `--fs-micro` 추가
- 임시 계산식 제거

**Phase 2 (단기)**: 정보 위계 변수 추가
- `--fs-hero`, `--fs-subheading`, `--fs-body-medium` 등 추가
- 레거시 변수와 매핑

**Phase 3 (중기)**: 점진적 마이그레이션
- 새로운 코드는 정보 위계 변수 사용
- 기존 코드는 레거시 변수 유지

**Phase 4 (장기)**: 레거시 변수 제거 (선택사항)
- 모든 코드를 정보 위계 변수로 전환

---

## 5. 최종 권장안: 방안 1 (정보 위계 중심)

### 5.1 최종 표준 스케일

```css
:root {
  /* === 정보 위계별 타이포그래피 스케일 === */
  --fs-hero: 26px;           /* Hero/Page Title */
  --fs-heading: 20px;        /* Section Heading (새로 추가) */
  --fs-subheading: 17px;     /* Subheading/Body Large */
  --fs-body-medium: 16px;    /* Body Medium (칩 설명 등) */
  --fs-body: 15px;           /* Body Text (기본) */
  --fs-label: 14px;          /* Label/Meta */
  --fs-caption: 13px;        /* Caption/Chart Label */
  --fs-micro: 12px;          /* Micro/Source */
  
  /* === 레거시 호환성 === */
  --fs-2xl: var(--fs-hero);
  --fs-xl: var(--fs-subheading);
  --fs-lg: 18px;             /* 특수 요소용 */
  --fs-md: var(--fs-subheading);
  --fs-base: var(--fs-body);
  --fs-sm: var(--fs-label);
  --fs-xs: var(--fs-caption);
  
  /* === 컴포넌트별 크기 === */
  --chip-desc-size: var(--fs-body-medium);
  --chip-source-size: var(--fs-micro);
}
```

### 5.2 사용 가이드라인

1. **새로운 코드 작성 시**: 정보 위계 변수 사용 (`--fs-hero`, `--fs-subheading` 등)
2. **기존 코드**: 레거시 변수 유지 (`--fs-2xl`, `--fs-xl` 등)
3. **컴포넌트별 크기**: 표준 스케일 기반으로 정의

### 5.3 예상 효과

- ✅ **일관성**: 모든 텍스트 크기가 표준 스케일에 포함
- ✅ **명확성**: 정보 위계가 변수명에 드러남
- ✅ **유지보수성**: 중복 제거 및 명확한 역할 정의
- ✅ **확장성**: 새로운 크기 추가 시 표준 스케일 확장
- ✅ **호환성**: 기존 코드와의 호환성 유지

---

## 6. 참고 자료

- 현재 코드: `static/audit-chat-pwc.html`
- 관련 문서: `docs/DESIGN_PROGRESS_HANDOFF.md`, `docs/UX_LAYOUT_COMPREHENSIVE_REVIEW.md`

---

**다음 단계**: 개발팀과 협의하여 방안 1 적용 여부 결정 및 마이그레이션 계획 수립
