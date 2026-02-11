"""Chat / LLM endpoints."""
from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatMessage, ChatRequest
from backend.services.llm_service import get_llm_response

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/completions")
def chat_completion(request: ChatRequest):
    """LLM 채팅 완성. Streamlit 등에서 호출."""
    try:
        reply = get_llm_response(
            messages=[{"role": m.role, "content": m.content} for m in request.messages],
            stream=request.stream,
        )
        return {"message": ChatMessage(role="assistant", content=reply)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
