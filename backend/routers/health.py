"""Health check endpoints."""
from fastapi import APIRouter
from backend.database import verify_connection
from backend.models.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        neo4j_connected=verify_connection(),
    )
