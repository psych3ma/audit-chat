"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.config import get_settings
from backend.database import Neo4jDriver
from backend.routers import health, chat, graph, independence


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    Neo4jDriver.close()


app = FastAPI(
    title="Audit Chat API",
    description="Streamlit + FastAPI + Neo4j + Mermaid + LLM",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 준비 완료: run.sh 대기용
@app.get("/ready")
def ready():
    return {"status": "ok"}

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(graph.router)
app.include_router(independence.router)

# 정적 파일: 감사 독립성 UI
STATIC_DIR = Path(__file__).resolve().parent.parent / "static"
if STATIC_DIR.is_dir():
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
def root():
    """감사 독립성 UI로 리다이렉트. internal-control.html 없으면 audit-chat-pwc.html."""
    internal_control = STATIC_DIR / "internal-control.html"
    pwc_html = STATIC_DIR / "audit-chat-pwc.html"
    if internal_control.is_file():
        return RedirectResponse(url="/static/internal-control.html", status_code=302)
    if pwc_html.is_file():
        return RedirectResponse(url="/static/audit-chat-pwc.html", status_code=302)
    return {
        "service": "Audit Chat API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/pwc")
def pwc_ui():
    """감사 독립성 UI (audit-chat-pwc.html) — /chat/completions API 연동."""
    pwc_html = STATIC_DIR / "audit-chat-pwc.html"
    if pwc_html.is_file():
        return RedirectResponse(url="/static/audit-chat-pwc.html", status_code=302)
    return {"error": "audit-chat-pwc.html not found", "static_dir": str(STATIC_DIR)}
