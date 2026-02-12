"""독립성 검토 시스템용 Pydantic 모델 (감사 수임 독립성)."""
import re
from enum import Enum
from typing import Any, List, Union

from pydantic import BaseModel, Field, field_validator


class IndependenceStatus(str, Enum):
    REJECT = "수임 불가"
    CONDITIONAL = "안전장치 적용 시 수임 가능"
    ACCEPT = "수임 가능"


class AuditEntity(BaseModel):
    id: str = Field(..., description="고유 식별자")
    label: str = Field(..., description="주체 유형")
    name: str = Field(..., description="주체 이름")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str):
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("ID must be alphanumeric")
        return v


class Relationship(BaseModel):
    source_id: str
    target_id: str
    rel_type: str


class IndependenceMap(BaseModel):
    entities: List[AuditEntity]
    connections: List[Relationship]


class LegalRefItem(BaseModel):
    """근거 법령 한 건: 표시 문구와 선택적 조문 URL."""
    name: str = Field(..., description="법령·조문 표시명 (예: 공인회계사법 제21조)")
    url: str | None = Field(None, description="조문 URL (있으면 새 창에서 열기)")


def _normalize_legal_ref(v: Any) -> LegalRefItem:
    if isinstance(v, str):
        return LegalRefItem(name=v.strip(), url=None)
    if isinstance(v, dict):
        return LegalRefItem(name=v.get("name", str(v)).strip(), url=v.get("url") or None)
    return LegalRefItem(name=str(v), url=None)


class AnalysisResult(BaseModel):
    status: IndependenceStatus
    risk_level: str
    key_issues: List[str]
    legal_references: List[LegalRefItem] = Field(default_factory=list)
    considerations: str
    suggested_safeguards: List[str] = Field(default_factory=list)

    @field_validator("legal_references", mode="before")
    @classmethod
    def normalize_legal_references(cls, v: Any) -> List[dict]:
        if not v:
            return []
        out = []
        for item in v if isinstance(v, list) else [v]:
            ref = _normalize_legal_ref(item)
            out.append(ref.model_dump())
        return out

    @field_validator("status", mode="before")
    @classmethod
    def normalize_status(cls, v):
        if isinstance(v, str):
            v_lower = v.lower().strip()
            if any(kw in v_lower for kw in ["불가", "reject", "prohibited"]):
                return IndependenceStatus.REJECT
            if any(kw in v_lower for kw in ["조건부", "conditional", "안전장치"]):
                return IndependenceStatus.CONDITIONAL
            if any(kw in v_lower for kw in ["가능", "acceptable", "ok"]):
                return IndependenceStatus.ACCEPT
        return v


class IndependenceReviewRequest(BaseModel):
    scenario: str = Field(..., min_length=1)


class IndependenceReviewResponse(BaseModel):
    trace_id: str
    rel_map: IndependenceMap
    analysis: AnalysisResult
    mermaid_code: str
