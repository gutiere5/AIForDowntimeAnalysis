import logging
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from backend.agents.main_agent import MainAgent
from backend.agents.utils.schemas import RequestContext

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/agent/query")
async def agent_query(query: str, session_id: str, conversation_id: str = None):
    logger.info(f"Received user request: {query} for session_id: {session_id} and conversation_id: {conversation_id}")
    main_agent = MainAgent(name="MainAgent")

    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    context = RequestContext(
        session_id = session_id,
        conversation_id = conversation_id or str(uuid.uuid4())
    )

    return StreamingResponse(
        main_agent.process_query(query, context),
        media_type="text/event-stream"
    )
