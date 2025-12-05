from dataclasses import dataclass
from typing import List, Literal
from pydantic import BaseModel, Field

@dataclass
class RequestContext:
    """
    A data class to hold all relevant context for a single request.
    This object is passed through the layers of the application.
    """
    session_id: str
    conversation_id: str

class ChatMessage(BaseModel):
    """A single message in a conversation."""
    role: Literal["system", "user", "assistant", "tool"]
    content: str

class ConversationHistory(BaseModel):
    """A list of messages representing a conversation."""
    messages: List[ChatMessage] = Field(..., description="The list of messages in the conversation.")

    def to_list(self) -> List[dict]:
        """Converts the conversation history to a list of dictionaries."""
        return [msg.model_dump() for msg in self.messages]