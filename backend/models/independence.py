"""독립성 검토 시스템용 Pydantic 모델 (감사 수임 독립성)."""
import re
from enum import Enum
from typing import List

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


class AnalysisResult(BaseModel):
    status: IndependenceStatus
    risk_level: str
    key_issues: List[str]
    legal_references: List[str] = Field(default_factory=list)
    considerations: str
    suggested_safeguards: List[str] = Field(default_factory=list)

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
