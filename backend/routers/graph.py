"""Neo4j graph / Mermaid-related endpoints."""
from fastapi import APIRouter, HTTPException
from backend.database import get_neo4j_session
from backend.models.schemas import MermaidResponse

router = APIRouter(prefix="/graph", tags=["graph"])


def _mermaid_safe_id(label: str) -> str:
    """Mermaid 노드 ID로 쓸 수 있도록 공백·특수문자 정리."""
    if not label or not label.strip():
        return "Node"
    return "".join(c if c.isalnum() or c in "_" else "_" for c in label.strip())[:30] or "Node"


@router.get("/mermaid", response_model=MermaidResponse)
def get_graph_as_mermaid():
    """
    Neo4j 그래프를 Mermaid 형식으로 반환.
    실제 스키마에 맞게 Cypher 및 Mermaid 변환 로직 확장 필요.
    """
    try:
        with get_neo4j_session() as session:
            result = session.run(
                """
                MATCH (n)-[r]->(m)
                RETURN labels(n)[0] AS from, type(r) AS rel, labels(m)[0] AS to
                LIMIT 50
                """
            )
            records = list(result)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Neo4j error: {e}")

    if not records:
        return MermaidResponse(
            mermaid_code="graph LR\n    A[Empty] --> B[Add data in Neo4j]",
            description="No graph data yet.",
        )

    lines = ["graph LR"]
    seen = set()
    for r in records:
        from_raw = r["from"] or "Node"
        to_raw = r["to"] or "Node"
        from_id = _mermaid_safe_id(str(from_raw))
        to_id = _mermaid_safe_id(str(to_raw))
        rel = (r["rel"] or "RELATES").replace('"', "'")[:20]
        from_display = str(from_raw).replace('"', "'")
        to_display = str(to_raw).replace('"', "'")
        edge = f'    {from_id}["{from_display}"] -->|{rel}| {to_id}["{to_display}"]'
        if edge not in seen:
            seen.add(edge)
            lines.append(edge)

    return MermaidResponse(
        mermaid_code="\n".join(lines),
        description="Graph from Neo4j (first 50 relationships).",
    )
