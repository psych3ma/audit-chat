# 문서 인덱스 (Documentation Index)

---

## 📋 문서 현황

| 문서 | 설명 | 대상 |
|------|------|------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | 시스템 아키텍처, Mermaid 다이어그램 | 개발자/CTO |
| [CTO_REVIEW.md](./CTO_REVIEW.md) | CTO 관점 종합 리뷰 | CTO |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | 기여 가이드, Git 운영 | 개발자 |
| [DESIGN_QA_회계법인제출용.md](./DESIGN_QA_회계법인제출용.md) | 디자인 QA (제출용) | 디자이너 |

---

## 📁 기능 문서

| 문서 | 설명 |
|------|------|
| [GENAI_INDEPENDENCE_REVIEW.md](./GENAI_INDEPENDENCE_REVIEW.md) | 독립성 검토 기능 (GenAI) |
| [AI_EXPERT_ARCHITECTURE_REVIEW.md](./AI_EXPERT_ARCHITECTURE_REVIEW.md) | AI 전문가 아키텍처 리뷰 |
| [법령검색목록-URL-검토.md](./법령검색목록-URL-검토.md) | 법령 URL 생성 로직 |

---

## 📁 기타

| 문서 | 설명 | 상태 |
|------|------|------|
| [UI_PROTOTYPE_REVIEW.md](./UI_PROTOTYPE_REVIEW.md) | UI 프로토타입 검토 | 참조용 |
| [UX-copy-review-request.md](./UX-copy-review-request.md) | UX 카피 수정 요청 | 참조용 |

---

## 📊 제출용 필수 문서

회계법인 포트폴리오 제출 시:

| 문서 | 이유 |
|------|------|
| `README.md` (루트) | 프로젝트 개요 |
| `docs/ARCHITECTURE.md` | 기술 아키텍처 |
| `docs/DESIGN_QA_회계법인제출용.md` | 디자인 품질 |

---

## 🗂️ 최종 구조

```
docs/
├── README.md                       # 이 인덱스
├── ARCHITECTURE.md                 # 아키텍처 (필수)
├── CTO_REVIEW.md                   # CTO 리뷰 (통합)
├── CONTRIBUTING.md                 # 기여 가이드 (통합)
├── DESIGN_QA_회계법인제출용.md      # 디자인 QA
├── GENAI_INDEPENDENCE_REVIEW.md    # 독립성 검토 기능
├── AI_EXPERT_ARCHITECTURE_REVIEW.md # AI 아키텍처 리뷰
├── 법령검색목록-URL-검토.md         # 법령 URL 로직
├── UI_PROTOTYPE_REVIEW.md          # UI 검토 (참조)
└── UX-copy-review-request.md       # UX 카피 (참조)
```

---

## 🔄 정리 결과

| 액션 | 대상 | 결과 |
|------|------|------|
| ✅ 삭제 | `LEGACY-internal-control.md` | 레거시 |
| ✅ 삭제 | `CTO_UNUSED_FILES_REVIEW.md` | 일회성 |
| ✅ 통합 | CTO 문서 4개 → `CTO_REVIEW.md` | 중복 제거 |
| ✅ 통합 | Git 가이드 2개 → `CONTRIBUTING.md` | 중복 제거 |

**15개 → 10개** (5개 정리)
