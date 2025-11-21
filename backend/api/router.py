from fastapi import APIRouter
from backend.api.endpoints import agent, conversation_history, conversations

api_router = APIRouter()

# Include all the sub-routers
api_router.include_router(agent.router, tags=["Agent"])
api_router.include_router(conversation_history.router, tags=["History"])
api_router.include_router(conversations.router, tags=["Conversations"])
api_router.include_router(agent.router, tags=["Health"])
