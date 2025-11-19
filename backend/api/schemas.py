from pydantic import BaseModel
from typing import Optional


class UserQueryRequest(BaseModel):
    query: str  # The query string provided by the user
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None


class ConversationHistoryRequest(BaseModel):
    conversation_id: str
    session_id: str
