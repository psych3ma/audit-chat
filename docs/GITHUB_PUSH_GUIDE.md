# GitHub 푸시 안내

아래 순서대로 터미널에서 실행하세요. 프로젝트 루트에서 진행합니다.

---

## 1. 비밀값 제외 확인 (필수)

```bash
git status
```

**`.env` 또는 `venv/` 가 목록에 있으면 안 됩니다.**

- 있으면:
  ```bash
  git rm --cached .env
  git commit -m "chore: remove .env from tracking"
  ```

**.gitignore 동작 확인 (선택):**
```bash
git check-ignore -v .env
git check-ignore -v venv
```
→ 각각 `.gitignore` 규칙이 나오면 정상.

---

## 2. 스테이징

```bash
git add .
git status
```
→ 다시 한번 `.env`, `venv/` 가 없어야 함.

---

## 3. 커밋

```bash
git commit -m "chore: CTO 검토 후 체크포인트 (감사 독립성 검토·법령 레지스트리·GenAI 프롬프트 보강)"
```

원하면 메시지만 바꿔서 사용해도 됩니다.

---

## 4. GitHub에 푸시

### 4-1. 처음 저장소 연결하는 경우

1. GitHub에서 새 저장소(Repository) 생성 (예: `audit-chat`). **README/ .gitignore 추가하지 말고** 빈 저장소로 만듭니다.

2. 아래에서 `YOUR_USERNAME` / `YOUR_REPO` 를 본인 계정·저장소 이름으로 바꿉니다.

```bash
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

### 4-2. 이미 remote가 있는 경우

```bash
git push origin main
```

(또는 현재 브랜치가 `main`이면 `git push` 만 해도 됨.)

---

## 5. (선택) 복원용 태그

나중에 이 시점으로 돌아오고 싶을 때를 위해 태그를 남깁니다.

```bash
git tag restore-point-$(date +%Y-%m-%d)
git push origin --tags
```

복원 시: `git checkout restore-point-YYYY-MM-DD` 또는 해당 커밋 해시 사용.

---

## 한 번에 복사용 (이미 remote 있음, 태그 없음)

```bash
git status
git add .
git status
git commit -m "chore: CTO 검토 후 체크포인트 (감사 독립성 검토·법령 레지스트리·GenAI 프롬프트 보강)"
git push origin main
```

**주의:** `git status`에서 `.env`, `venv/` 가 보이면 먼저 `git rm --cached .env` 하고 별도 커밋한 뒤 위 순서를 진행하세요.
