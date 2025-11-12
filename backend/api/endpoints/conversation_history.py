import logging
from fastapi import APIRouter
from backend.api.schemas import ConversationHistoryRequest
from backend.repositories.conversation_repo import conversations_repository

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/get_history")
async def get_history(history_request: ConversationHistoryRequest):
    logger.info(f"Fetching history for conversation_id: {history_request.conversation_id}")
    messages = conversations_repository.get_messages_by_conversation_id(
        history_request.conversation_id,
        history_request.session_id
    )
    return {"messages": messages}

@router.get("/conversations/{session_id}")
async def get_conversations(session_id: str):
    logger.info(f"Fetching all conversations for session_id: {session_id}")
    conversations = conversations_repository.get_conversations_by_session_id(session_id)
    return {"conversations": conversations}