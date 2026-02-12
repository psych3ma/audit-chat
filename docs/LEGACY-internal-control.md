# CTO 관점: internal-control.html 레거시 검토

## 1. 현재 상태

| 항목 | 내용 |
|------|------|
| **internal-control.html** | `static/` 디렉터리에 **존재하지 않음**. (과거에 audit-chat-pwc.html 복사본으로 운영되다 제거된 것으로 추정) |
| **static/ 디렉터리** | `audit-chat-pwc.html` 단일 파일만 존재. |
| **백엔드 의존성** | `GET /` → `internal_control.is_file()` 시 `/static/internal-control.html`로 302 리다이렉트. 파일 없으면 JSON 응답. |
| **실제 진입점** | `GET /pwc` → `/static/audit-chat-pwc.html` (백엔드 연동됨). |

## 2. 레거시 이슈 요약

### 2.1 불일치
- **Root(/)**: 존재하지 않는 `internal-control.html`을 가정 → 현재는 API 정보 JSON만 반환.
- **사용자 기대**: “내부통제 AI 검토” 랜딩이 `/`에 있다고 가정할 수 있음.

### 2.2 중복 UI 이력
- **internal-control.html**: 동일 도메인의 “내부통제 AI 검토” UI였으나, 백엔드 API 호출 없이 **클라이언트 시나리오만** 사용하는 버전으로 추정.
- **audit-chat-pwc.html**: 동일 콘셉트 UI + **POST /chat/completions** 연동, 실패 시 로컬 시나리오 폴백. CTO 설정(API_BASE_URL, USE_BACKEND_API) 반영.

### 2.3 기술 부채
- **이름 혼재**: `internal-control` vs `audit-chat-pwc` → 팀 내에서 “어느 게 메인 UI인지” 혼동 가능.
- **Root 동작**: 레거시 파일명에 묶여 있어, 실제 제공 중인 UI와 연결되지 않음.

## 3. CTO 권고 사항

### 3.1 단기 (즉시 적용 권장)
1. **Root(/) 정리**  
   - `internal-control.html`이 없으므로, **`/`는 `audit-chat-pwc.html`로 리다이렉트**하도록 변경.  
   - 사용자는 `GET /` 만으로 내부통제 UI에 도달.

2. **레거시 참조 제거**  
   - `main.py`에서 `internal-control.html` 조건 분기 제거.  
   - 단일 정적 UI(`audit-chat-pwc.html`) 기준으로 root·라우트 정리.

### 3.2 중기 (선택)
- **internal-control.html 재도입 불필요**  
  - 기능·디자인이 `audit-chat-pwc.html`에 흡수된 상태.  
  - 필요 시 `audit-chat-pwc.html`을 “내부통제 검토” 전용 단일 진입점으로 유지하고, 파일명만 `internal-control.html`로 변경하는 리네이밍은 가능(호출처 일괄 수정 필요).

### 3.3 보안·운영
- **정적 파일**: HTML/CSS/JS만 서빙, 민감 정보 미포함.  
- **API 연동**: `audit-chat-pwc.html`은 동일 오리진 또는 설정된 `API_BASE_URL`로만 요청. CORS는 백엔드 설정에 따름.  
- **에러 처리**: API 실패 시 로컬 시나리오 폴백으로 가용성 유지.

## 4. 결론

- **internal-control.html**은 현재 코드베이스에 없는 **레거시 진입점**이며, 백엔드는 여전히 해당 파일을 가정하고 있어 **불일치**가 있음.
- **권고**: Root(/)를 `audit-chat-pwc.html`로 리다이렉트하고, `internal-control.html` 참조를 제거하여 단일 UI·단일 진입점으로 정리하는 것이 CTO 관점에서 적절함.
