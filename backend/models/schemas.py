"""Pydantic schemas for API request/response."""
from typing import Literal, Optional

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(default_factory=list, max_length=100)
    stream: bool = False


class MermaidResponse(BaseModel):
    mermaid_code: str
    description: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = "ok"
    neo4j_connected: bool = False
