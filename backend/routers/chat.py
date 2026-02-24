"""Chat / LLM endpoints."""
from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatMessage, ChatRequest
from backend.services.llm_service import get_llm_response
from backend.services.independence_service import (
    extract_relationships,
    get_independence_map_from_neo4j,
    get_trace_id,
    save_independence_map_to_neo4j,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/completions")
async def chat_completion(request: ChatRequest):
    """
    LLM 채팅 완성. 시나리오에서 엔티티-관계를 추출해 context로 활용.
    흐름: 시나리오 추출 → trace_id로 Neo4j 조회 → 없으면 추출 후 저장 → context 포함해 LLM 호출.
    """
    try:
        user_messages = [m for m in request.messages if m.role == "user"]
        if not user_messages:
            raise ValueError("사용자 메시지가 없습니다.")
        scenario_text = user_messages[-1].content.strip()

        trace_id = get_trace_id(scenario_text)
        rel_map = get_independence_map_from_neo4j(trace_id)
        if rel_map is None:
            rel_map = await extract_relationships(scenario_text)
            try:
                save_independence_map_to_neo4j(trace_id, rel_map)
            except Exception:
                pass

        rel_map_json = rel_map.model_dump_json(indent=2)
        context = f"""다음은 입력된 시나리오에서 추출한 엔티티-관계 정보입니다:

{rel_map_json}

이 정보를 참고하여 답변해주세요. 엔티티와 관계를 명확히 언급하고, 구체적인 분석을 제공해주세요."""

        system_message = {
            "role": "system",
            "content": "당신은 감사 독립성 검토 전문가입니다. 제공된 엔티티-관계 정보를 활용하여 시나리오를 분석하고 답변하세요."
        }
        enhanced_messages = [system_message]
        last_user_index = len([m for m in request.messages if m.role == "user"]) - 1
        user_count = 0
        for msg in request.messages:
            if msg.role == "user":
                if user_count == last_user_index and msg.content.strip() == scenario_text:
                    enhanced_messages.append({
                        "role": "user",
                        "content": context + "\n\n시나리오: " + scenario_text
                    })
                else:
                    enhanced_messages.append({"role": msg.role, "content": msg.content})
                user_count += 1
            else:
                enhanced_messages.append({"role": msg.role, "content": msg.content})

        reply = get_llm_response(
            messages=enhanced_messages,
            stream=request.stream,
        )
        return {"message": ChatMessage(role="assistant", content=reply)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
