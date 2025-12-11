import logging
from fastapi import APIRouter
from backend.repositories.sql_databases import conversations_repo

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/conversations")
async def get_conversation_by_conversation_id(conversation_id: str, session_id: str):
    logger.info(f"Fetching history for conversation_id: {conversation_id} and session_id: {session_id}")
    messages = conversations_repo.get_messages_by_conversation_id(conversation_id, session_id)
    return {"messages": messages}

@router.get("/conversations/{session_id}")
async def get_conversations_by_session(session_id: str):
    logger.info(f"Fetching all conversations for session_id: {session_id}")
    conversations = conversations_repo.get_conversations_by_session_id(session_id)
    return {"conversations": conversations}

@router.post("/conversations/create")
async def create_conversation(session_id: str, title: str):
    logger.info(f"Creating new conversation for session_id: {session_id} with title: {title}")
    conversation_id = conversations_repo.create_conversation(session_id, title)
    return {"conversation_id": conversation_id, "title": title}

@router.delete("/conversations/{session_id}/{conversation_id}")
async def delete_conversation(conversation_id: str, session_id: str):
    logger.info(f"Deleting conversation_id: {conversation_id} for session_id: {session_id}")
    conversations_repo.delete_conversation(conversation_id, session_id)
    return {"message": "Conversation deleted successfully"}

@router.delete("/conversations/{session_id}")
async def delete_all_conversations(session_id: str):
    logger.info(f"Deleting all conversations for session_id: {session_id}")
    conversations_repo.delete_all_conversations(session_id)
    return {"message": "All conversations deleted successfully"}

@router.put("/conversations")
async def update_conversation_title(session_id: str, conversation_id: str, title: str):
    logger.info(f"Updating conversation_id: {conversation_id} with title: {title}")
    conversations_repo.update_conversation_title(conversation_id, session_id, title)
    return {"message": "Conversation updated successfully"}