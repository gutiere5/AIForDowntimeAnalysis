# app/api/router.py
from fastapi import APIRouter
from backend.api.endpoints import agent, conversation_history, logs

api_router = APIRouter()

# Include all the sub-routers
api_router.include_router(agent.router, tags=["Agent"])
api_router.include_router(conversation_history.router, tags=["History"])
api_router.include_router(logs.router, tags=["Logs"])