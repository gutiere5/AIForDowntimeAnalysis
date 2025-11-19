import logging
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.api.schemas import UserQueryRequest
from backend.new_agents.main_agent import MainAgent
from backend.agents.schemas import RequestContext

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/agent_query")
async def agent_query(user_request: UserQueryRequest):
    logger.info(f"Received user request: {user_request.query}")
    main_agent = MainAgent

    if not user_request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    context = RequestContext(
        session_id=user_request.session_id,
        conversation_id=user_request.conversation_id or str(uuid.uuid4())
    )

    return StreamingResponse(
        main_agent.process_query(user_request.query, context),
        media_type="text/event-stream"
    )