# PwC 전용 브랜드 (내부 서버만)

이 디렉터리는 **외부 제출·공개 패키지에 포함하지 않습니다.**
일반 제출용은 `web/` + `static/independence-review.html` 만 사용하세요.

## 파일

| 파일 | 역할 |
|---|---|
| `brand.pwc.json` | 삼일PwC 이름·로고·예시 시나리오 |
| `theme.pwc.css` | PwC 토큰 오버라이드 |
| `assets/pwc-logo.jpg` | 로고 |
| `dist/independence-review.pwc.html` | 빌드 산출물 (`npm run build:pwc`) |
| `legacy/audit-chat-pwc.html` | 이전 단일 HTML (참고용, 신규 서빙 대상 아님) |

## 빌드

코어·기본 테마·Mermaid는 `web/` SSOT를 그대로 씁니다.

```bash
cd web
# package.json 안내: build = 일반만, build:pwc = 이 디렉터리 오버레이
npm run build:pwc
```

산출물: `internal/pwc/dist/independence-review.pwc.html`

## 서빙

백엔드에서 `SERVE_INTERNAL_PWC=1` 일 때만 `/pwc` 와 `/internal/pwc` 를 엽니다.
기본값(미설정)에서는 PwC UI가 외부에 노출되지 않습니다.
