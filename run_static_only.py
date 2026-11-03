"""Neo4j 없이 정적 파일만 서빙. UI 확인용. API는 미동작."""
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
import os
import uvicorn

ROOT = Path(__file__).resolve().parent
STATIC_DIR = ROOT / "static"
GENERAL_UI = STATIC_DIR / "independence-review.html"

app = FastAPI(title="Audit Chat (Static Only)")

if STATIC_DIR.is_dir():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def root():
    if not GENERAL_UI.is_file():
        return {
            "message": "static/independence-review.html not found",
            "hint": "cd web && npm run build",
        }
    url = "/static/independence-review.html"
    backend_url = os.environ.get("BACKEND_URL", "").strip().rstrip("/")
    if backend_url:
        url = url + "?api=" + backend_url
    return RedirectResponse(url=url, status_code=302)


@app.get("/ready")
def ready():
    return {"status": "ok"}


if __name__ == "__main__":
    port = int(os.environ.get("API_PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)
