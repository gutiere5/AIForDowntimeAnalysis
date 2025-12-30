import logging
import uuid
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from agents.main_agent import MainAgent
from agents.llm_models.model_registry import DEFAULT_MODEL_ID, ALLOWED_MODEL_IDS
from agents.utils.schemas import RequestContext

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/agent/query")
async def agent_query(query: str, session_id: str, conversation_id: str = None, model_id: str = None):
    logger.info(f"Received user request: {query} for session_id: {session_id} and conversation_id: {conversation_id}")

    resolved_model_id = model_id or DEFAULT_MODEL_ID
    if resolved_model_id not in ALLOWED_MODEL_IDS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Unsupported model_id",
                "model_id": resolved_model_id,
                "allowed_model_ids": sorted(ALLOWED_MODEL_IDS),
            },
        )

    main_agent = MainAgent(model_id=resolved_model_id)

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
