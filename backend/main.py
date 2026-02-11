"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.database import Neo4jDriver
from backend.routers import health, chat, graph


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

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(graph.router)


@app.get("/")
def root():
    return {
        "service": "Audit Chat API",
        "docs": "/docs",
        "health": "/health",
    }
