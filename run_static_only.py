"""
Neo4j 없이 정적 파일만 서빙 (neo4j import 시 segfault 등 환경 이슈 회피).
웹앱 UI만 확인할 때 사용: python run_static_only.py
API(/independence/*, /chat/* 등)는 이 서버에서는 동작하지 않습니다.
"""
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

STATIC_DIR = Path(__file__).resolve().parent / "static"
app = FastAPI(title="Audit Chat (Static Only)")

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def root():
    pwc = STATIC_DIR / "audit-chat-pwc.html"
    if pwc.is_file():
        return RedirectResponse(url="/static/audit-chat-pwc.html", status_code=302)
    return {"message": "static/audit-chat-pwc.html not found"}

@app.get("/ready")
def ready():
    return {"status": "ok"}

if __name__ == "__main__":
    port = int(__import__("os").environ.get("API_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
