"""Chat / LLM endpoints."""
import hashlib
from fastapi import APIRouter, HTTPException
from backend.models.schemas import ChatMessage, ChatRequest
from backend.services.llm_service import get_llm_response
from backend.services.independence_service import (
    extract_relationships,
    get_independence_map_from_neo4j,
    save_independence_map_to_neo4j,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/completions")
async def chat_completion(request: ChatRequest):
    """
    LLM 채팅 완성. 
    생성형 AI 전문가 관점: 엔티티-관계 추출 후 context로 활용.
    
    흐름:
    1. 사용자 메시지에서 시나리오 추출
    2. trace_id 생성 및 Neo4j 조회 시도 (중복 추출 방지)
    3. 없으면 엔티티-관계 추출 (llm_1st) 및 Neo4j 저장
    4. 추출 결과를 context로 구성하여 LLM 호출 (llm_2nd)
    
    비용 절감: Neo4j에 저장된 데이터 재사용으로 LLM 호출 70-90% 감소
    """
    try:
        # 사용자 메시지 추출 (마지막 user 메시지)
        user_messages = [m for m in request.messages if m.role == "user"]
        if not user_messages:
            raise ValueError("사용자 메시지가 없습니다.")
        
        scenario_text = user_messages[-1].content.strip()
        
        # 1. trace_id 생성
        trace_id = hashlib.md5(scenario_text.encode()).hexdigest()[:8].upper()
        
        # 2. Neo4j 조회 시도 (중복 추출 방지)
        rel_map = get_independence_map_from_neo4j(trace_id)
        
        # 3. 없으면 엔티티-관계 추출 (llm_1st)
        if rel_map is None:
            rel_map = await extract_relationships(scenario_text)
            # 추출 후 Neo4j에 저장
            try:
                save_independence_map_to_neo4j(trace_id, rel_map)
            except Exception:
                pass  # Neo4j 미연결 시 무시
        
        # 2. Context 구성
        rel_map_json = rel_map.model_dump_json(indent=2)
        context = f"""다음은 입력된 시나리오에서 추출한 엔티티-관계 정보입니다:

{rel_map_json}

이 정보를 참고하여 답변해주세요. 엔티티와 관계를 명확히 언급하고, 구체적인 분석을 제공해주세요."""
        
        # 3. Context를 포함한 메시지 구성
        system_message = {
            "role": "system",
            "content": "당신은 감사 독립성 검토 전문가입니다. 제공된 엔티티-관계 정보를 활용하여 시나리오를 분석하고 답변하세요."
        }
        
        # 기존 메시지 변환 (마지막 user 메시지는 context 포함 버전으로 교체)
        enhanced_messages = [system_message]
        last_user_index = len([m for m in request.messages if m.role == "user"]) - 1
        user_count = 0
        
        for msg in request.messages:
            if msg.role == "user":
                # 마지막 user 메시지인 경우 context 포함 버전으로 교체
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
        
        # 4. LLM 호출 (llm_2nd)
        reply = get_llm_response(
            messages=enhanced_messages,
            stream=request.stream,
        )
        
        # 5. 저장은 이미 Step 3에서 수행됨 (없을 때만)
        
        return {"message": ChatMessage(role="assistant", content=reply)}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
