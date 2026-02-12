# 기여 가이드 (Contributing Guide)

프로젝트 기여 및 GitHub 운영 가이드입니다.

---

## 1. 개발 환경 설정

```bash
# 가상환경 생성 + 의존성 설치
make venv
source venv/bin/activate

# 환경변수 설정
cp .env.example .env
# .env 편집: OPENAI_API_KEY 등 입력

# 실행
./run.sh
```

---

## 2. 브랜치 전략

| 브랜치 | 용도 |
|--------|------|
| `main` | 안정 버전 |
| `develop` | 개발 통합 |
| `feature/*` | 새 기능 |
| `bugfix/*` | 버그 수정 |
| `hotfix/*` | 긴급 수정 |

**상세**: [`ARCHITECTURE.md`](./ARCHITECTURE.md) § 9. Git 브랜치 전략 참조

---

## 3. 커밋 규칙

### 3.1 커밋 타입

| 타입 | 설명 |
|------|------|
| `feat` | 새 기능 |
| `fix` | 버그 수정 |
| `docs` | 문서 |
| `refactor` | 리팩토링 |
| `style` | 코드 포맷 |
| `test` | 테스트 |
| `chore` | 빌드/설정 |

### 3.2 커밋 메시지 예시

```
feat: 새 시나리오 추가 (2018 CPA 기출)
fix: 법령 URL 인코딩 오류 수정
docs: 아키텍처 다이어그램 추가
```

### 3.3 (선택) Cursor AI 트레일러 제거

Cursor에서 커밋 시 `Co-authored-by: Cursor …` 제거:

```bash
cp scripts/git-hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

---

## 4. 푸시 전 체크리스트

### 4.1 비밀값 확인 (필수)

```bash
git status
```

**포함되면 안 되는 것**: `.env`, `venv/`, `*.log`

만약 `.env`가 보이면:
```bash
git rm --cached .env
git commit -m "chore: remove .env from tracking"
```

### 4.2 .gitignore 동작 확인

```bash
git check-ignore -v .env   # .gitignore 규칙 출력되면 OK
git check-ignore -v venv   # .gitignore 규칙 출력되면 OK
```

### 4.3 스테이징 및 커밋

```bash
git add .
git status          # .env, venv 없음 재확인
git commit -m "feat: 기능 설명"
```

---

## 5. GitHub 푸시

### 5.1 처음 저장소 연결

```bash
git remote add origin https://github.com/USERNAME/REPO.git
git branch -M main
git push -u origin main
```

### 5.2 이후 푸시

```bash
git push origin main
```

---

## 6. 복원 포인트 (태그)

중요 시점에 태그 생성:

```bash
git tag restore-point-$(date +%Y-%m-%d)
git push origin --tags
```

복원 시:
```bash
git checkout restore-point-YYYY-MM-DD
```

---

## 7. 빠른 참조 (한 번에 복사)

```bash
# 상태 확인
git status

# 스테이징 + 커밋 + 푸시
git add .
git status
git commit -m "chore: 설명"
git push origin main
```

---

*이전 문서: GITHUB_PUSH_GUIDE.md, PRE_PUSH_CHECKLIST.md를 통합*
