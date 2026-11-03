# 감사 독립성 검토 AI — 프론트엔드 (일반 제출용)

`core.html`(레이아웃·로직) + `theme.css`(디자인 토큰) + `brand.json`(이름·로고·문구·예시)로 구성됩니다.
**이 디렉터리에는 PwC 파일을 두지 않습니다.** PwC는 `../internal/pwc/` 전용입니다.

## 1. package.json 스크립트 (빌드 전 확인)

| 스크립트 | 용도 | 산출물 |
|---|---|---|
| `npm run build` | **일반 제출용 (기본)** | `../static/independence-review.html` + `dist/…` |
| `npm run build:pwc` | 내부 PwC 전용 | `../internal/pwc/dist/independence-review.pwc.html` |
| `npm run build:all` | 일반 + PwC | 위 둘 다 |
| `npm test` | jsdom 스모크 | — |

```bash
# 외부에 내보내는 산출물만 필요할 때
node build.mjs
# 또는 (static/ 동기화 포함)
npm run build
```

- 테마·브랜드·로고·Mermaid를 인라인해 `file://`로도 동작합니다.
- `--mermaid cdn` / `local` / `inline`(기본) 선택 가능.
- 빌드는 Mermaid 해시 검증 + **다른 브랜드 문자열 혼입 검사**를 하며, 실패 시 파일을 만들지 않습니다.
- `web/`에 `brand.pwc.json` 등이 있으면 일반 빌드가 실패합니다(유출 방지).

## 2. 개발

```bash
python3 -m http.server 8000
# http://localhost:8000/core.html
```

| 파일 | 역할 |
|---|---|
| `core.html` | 마크업·로직. 색상/브랜드 문구 하드코딩 금지 |
| `theme.css` | 기본 토큰(Graphite sky) |
| `brand.json` | 일반 브랜드 |
| `vendor/mermaid.min.js` | Mermaid 10.9.8 (+ `.sha384`) |

새 공개 브랜드: `brand.acme.json` + (선택) `theme.acme.css` → `node build.mjs --brand acme`.
고객사 전용·내부 전용 브랜드는 `web/` 밖(`internal/<id>/`)에 두고 `--brand-dir`로 빌드하세요.

## 3. API

`/independence/extract` → `/analyze` → `/report` 순 POST (요청당 60초).
`?api=`는 localhost 또는 `brand.api.allowedOrigins`만 허용.

## 4. 테스트

```bash
npm install && npm test
npm run test:contrast
npm run build && npm run qa:browser
```

## 5. 배포 패키지 규칙

- **외부 제출**: `static/independence-review.html` (또는 `web/` 일반 소스)만.
- **넣지 말 것**: `internal/pwc/**`, `brand.pwc.json`, `theme.pwc.css`, `*.pwc.html`, PwC 로고.
- 서버에서 PwC를 열려면 `SERVE_INTERNAL_PWC=1` + `npm run build:pwc`.
