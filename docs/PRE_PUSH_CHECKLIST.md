# GitHub 푸시 전 체크리스트 (복원 포인트)

푸시 직전에 아래를 한 번씩 확인하세요.

## 0. (선택) Cursor AI 공동협업 트레일러 제거

Cursor에서 커밋하면 `Co-authored-by: Cursor …` 가 메시지에 붙는 걸 막고 싶다면, **한 번만** 아래 실행:

```bash
cp scripts/git-hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

이후 Cursor로 커밋해도 해당 줄은 자동으로 제거됩니다. 터미널에서 `git commit` 할 때는 원래부터 붙지 않습니다.

## 1. 비밀값·환경 파일 미포함

```bash
git status
```

- **포함되면 안 되는 것**: `.env`, `venv/`, `.env.local`, `*.log`
- `.env`가 목록에 보이면:
  ```bash
  git rm --cached .env
  git commit -m "chore: remove .env from tracking"
  ```

## 2. .gitignore 동작 확인

```bash
git check-ignore -v .env
# → .gitignore:30:.env    .env  (같이 나오면 OK)

git check-ignore -v venv
# → .gitignore:24:venv/   venv  (같이 나오면 OK)
```

## 3. 커밋할 파일만 스테이징

```bash
git add .
git status
# 다시 한번 .env, venv 없음 확인
```

## 4. 커밋 & 푸시

```bash
git commit -m "chore: CTO 검토 후 복원 포인트 (Streamlit+FastAPI+Neo4j+Mermaid+LLM)"
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

## 5. (선택) 복원용 태그

```bash
git tag restore-point-$(date +%Y-%m-%d)
git push origin --tags
```

이후 문제 생기면: `git checkout restore-point-YYYY-MM-DD` 또는 해당 커밋 해시로 복원.
