# 시나리오 칩 일관성 개선 검토 (CTO 관점)

**작성일**: 2026-02-12  
**검토자**: CTO 전문가 관점  
**목적**: 홈 화면과 채팅 중 시나리오 칩의 일관성 확보 및 확장성/유지보수성 개선

---

## 🔍 현재 상태 분석

### 홈 화면 시나리오 칩 (`renderScenarioChips`)

**위치**: 라인 1434-1460

**구현**:
```javascript
function renderScenarioChips() {
  // ...
  chip.innerHTML =
    '<div class="chip-label">' + d.label + '</div>' +
    '<div class="chip-text">' + d.text + '</div>' +  // ✅ 원문 사용
    '<div class="chip-arrow">출처: ' + d.source + '</div>';
}
```

**CSS**:
```css
.chip-text {
  /* ... */
  display: -webkit-box;
  -webkit-line-clamp: 3;  /* ✅ 말줄임 처리 적용 */
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

**상태**: ✅ **완성** (원문 + 말줄임)

---

### 채팅 중 시나리오 칩 (`buildPostChips`)

**위치**: 라인 2291-2314

**구현**:
```javascript
function buildPostChips() {
  // ...
  chip.innerHTML =
    '<div class="post-chip-label">' + d.label + '</div>' +
    '<div class="post-chip-text">' + d.shortText + '</div>';  // ❌ 요약 사용
}
```

**CSS**:
```css
.post-chip-text {
  font-size: var(--fs-md);
  color: var(--text);
  line-height: 1.4;
  /* ❌ 말줄임 처리 없음 */
}
```

**상태**: ❌ **미완성** (요약 + 말줄임 없음)

---

## ⚠️ 문제점 분석

### 1. 코드 중복 (DRY 원칙 위반)

**중복 코드**:
- 시나리오 칩 렌더링 로직이 두 곳에 분산
- 비슷한 HTML 구조를 각각 생성
- 스타일도 분리되어 있음 (`.chip-text` vs `.post-chip-text`)

**영향**:
- 수정 시 두 곳 모두 변경 필요
- 버그 발생 시 두 곳 모두 수정 필요
- 유지보수 비용 증가

---

### 2. 일관성 부족

**데이터 소스 불일치**:
- 홈 화면: `d.text` (원문)
- 채팅 중: `d.shortText` (요약)

**스타일 불일치**:
- 홈 화면: 말줄임 처리 (`-webkit-line-clamp: 3`)
- 채팅 중: 말줄임 처리 없음

**영향**:
- 사용자 경험 불일치
- 디자인 일관성 저하

---

### 3. 확장성 문제

**현재 구조**:
- 시나리오 칩 스타일 변경 시 두 곳 수정 필요
- 새로운 칩 타입 추가 시 중복 코드 증가
- 테스트 시 두 함수 모두 테스트 필요

---

## 💡 개선 방안

### 방안 A: 공통 함수로 통합 (권장)

**전략**: 시나리오 칩 생성 로직을 공통 함수로 추출

**구현**:
```javascript
/**
 * 시나리오 칩 생성 (공통 함수)
 * CTO 관점: DRY 원칙 준수, 확장성/유지보수성 향상
 */
function createScenarioChip(scenario, options = {}) {
  const {
    useFullText = true,      // 원문 사용 여부
    showSource = false,       // 출처 표시 여부
    className = 'chip',       // CSS 클래스명
    textClassName = 'chip-text'  // 텍스트 CSS 클래스명
  } = options;
  
  const chip = document.createElement('div');
  chip.className = className;
  chip.dataset.text = scenario.text;
  
  const label = document.createElement('div');
  label.className = className.replace('chip', 'chip-label');
  label.textContent = scenario.label;
  
  const text = document.createElement('div');
  text.className = textClassName;
  text.textContent = useFullText ? scenario.text : scenario.shortText;
  
  chip.appendChild(label);
  chip.appendChild(text);
  
  if (showSource) {
    const arrow = document.createElement('div');
    arrow.className = className.replace('chip', 'chip-arrow');
    arrow.textContent = '출처: ' + scenario.source;
    chip.appendChild(arrow);
  }
  
  return chip;
}
```

**사용 예시**:
```javascript
// 홈 화면
function renderScenarioChips() {
  const grid = document.getElementById("scenarioChips");
  grid.innerHTML = "";
  SCENARIOS.forEach((d) => {
    const chip = createScenarioChip(d, {
      useFullText: true,
      showSource: true,
      className: 'chip',
      textClassName: 'chip-text'
    });
    chip.onclick = () => fillInput(d.text);
    grid.appendChild(chip);
  });
}

// 채팅 중
function buildPostChips() {
  const wrap = document.createElement("div");
  wrap.className = "post-chips";
  // ...
  SCENARIOS.forEach((d) => {
    const chip = createScenarioChip(d, {
      useFullText: true,  // ✅ 원문 사용
      showSource: false,
      className: 'post-chip',
      textClassName: 'post-chip-text'
    });
    chip.addEventListener("click", () => fillInput(d.text));
    grid.appendChild(chip);
  });
}
```

**장점**:
- ✅ DRY 원칙 준수
- ✅ 일관성 확보
- ✅ 확장성 향상
- ✅ 유지보수성 향상

---

### 방안 B: CSS 클래스 통합 (간단한 방법)

**전략**: CSS 클래스를 통합하여 스타일 일관성 확보

**구현**:
```css
/* 공통 스타일 */
.chip-text,
.post-chip-text {
  font-size: var(--fs-md);
  color: var(--text);
  line-height: 1.45;
  font-weight: 500;
  
  /* 말줄임 처리 (공통) */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

**JavaScript 수정**:
```javascript
// buildPostChips에서 d.shortText → d.text 변경
chip.innerHTML =
  '<div class="post-chip-label">' + d.label + '</div>' +
  '<div class="post-chip-text">' + d.text + '</div>';  // ✅ 원문 사용
```

**장점**:
- ✅ 간단한 수정
- ✅ CSS 일관성 확보

**단점**:
- ⚠️ 코드 중복은 여전히 존재

---

## 🎯 CTO 권장 방안

### 단계적 접근

**Phase 1: 즉시 수정 (CSS 통합 + 데이터 소스 통일)**
- `.post-chip-text`에 말줄임 CSS 추가
- `buildPostChips`에서 `d.shortText` → `d.text` 변경
- **예상 시간**: 10분

**Phase 2: 리팩토링 (공통 함수 추출)**
- `createScenarioChip` 공통 함수 구현
- 두 함수에서 공통 함수 사용
- **예상 시간**: 30분

---

## 📋 구현 계획

### 즉시 수정 (Phase 1)

**1. CSS 수정**:
```css
.post-chip-text {
  font-size: var(--fs-md);
  color: var(--text);
  line-height: 1.4;
  
  /* 말줄임 처리 추가 */
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}
```

**2. JavaScript 수정**:
```javascript
// buildPostChips 함수에서
chip.innerHTML =
  '<div class="post-chip-label">' + d.label + '</div>' +
  '<div class="post-chip-text">' + d.text + '</div>';  // d.shortText → d.text
```

---

## ✅ 검증 체크리스트

- [ ] `.post-chip-text`에 말줄임 CSS 적용
- [ ] `buildPostChips`에서 `d.text` 사용 확인
- [ ] 홈 화면과 채팅 중 칩 스타일 일관성 확인
- [ ] 반응형 레이아웃에서도 정상 작동 확인

---

## 🎯 결론

**현재 상태**:
- 홈 화면: ✅ 원문 + 말줄임
- 채팅 중: ❌ 요약 + 말줄임 없음

**개선 방안**:
- Phase 1: CSS 통합 + 데이터 소스 통일 (즉시 적용)
- Phase 2: 공통 함수 추출 (리팩토링)

**권장**: Phase 1부터 즉시 적용하여 일관성 확보
