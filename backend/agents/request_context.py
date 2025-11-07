from dataclasses import dataclass
from typing import Optional


@dataclass
class RequestContext:
    """
    A data class to hold all relevant context for a single request.
    This object is passed through the layers of the application.
    """
    session_id: str
    conversation_id: Optional[str] = None