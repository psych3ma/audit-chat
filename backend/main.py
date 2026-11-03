"""FastAPI application entry point."""
from contextlib import asynccontextmanager
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from backend.config import get_settings
from backend.database import Neo4jDriver
from backend.routers import health, chat, graph, independence


ROOT_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = ROOT_DIR / "static"
INTERNAL_PWC_DIR = ROOT_DIR / "internal" / "pwc"
GENERAL_UI = STATIC_DIR / "independence-review.html"
PWC_UI = INTERNAL_PWC_DIR / "dist" / "independence-review.pwc.html"

# 외부 배포 기본 OFF. 내부 서버에서만 1 로 켠다.
SERVE_INTERNAL_PWC = os.getenv("SERVE_INTERNAL_PWC", "").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}


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

# 외부용 정적 UI (일반 브랜드만)
if STATIC_DIR.is_dir():
    from fastapi.staticfiles import StaticFiles
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# PwC 는 내부 서버 플래그가 켜진 경우에만 마운트 (유출 방지)
if SERVE_INTERNAL_PWC and INTERNAL_PWC_DIR.is_dir():
    from fastapi.staticfiles import StaticFiles
    app.mount(
        "/internal/pwc",
        StaticFiles(directory=str(INTERNAL_PWC_DIR)),
        name="internal_pwc",
    )


@app.get("/")
def root():
    """외부 기본 UI: 일반(independence-review) 단일 HTML."""
    if GENERAL_UI.is_file():
        return RedirectResponse(url="/static/independence-review.html", status_code=302)
    return {
        "service": "Audit Chat API",
        "docs": "/docs",
        "health": "/health",
        "hint": "일반 UI가 없습니다. cd web && npm run build 후 다시 열어주세요.",
    }


@app.get("/pwc")
def pwc_ui():
    """PwC UI — SERVE_INTERNAL_PWC=1 이고 빌드 산출물이 있을 때만."""
    if not SERVE_INTERNAL_PWC:
        return JSONResponse(
            status_code=404,
            content={
                "error": "PwC UI is disabled on this server",
                "hint": "내부 서버에서만 SERVE_INTERNAL_PWC=1 로 활성화하세요.",
            },
        )
    if PWC_UI.is_file():
        return RedirectResponse(
            url="/internal/pwc/dist/independence-review.pwc.html",
            status_code=302,
        )
    return JSONResponse(
        status_code=404,
        content={
            "error": "independence-review.pwc.html not found",
            "hint": "cd web && npm run build:pwc",
        },
    )
