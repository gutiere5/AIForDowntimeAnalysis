from fastapi import APIRouter
from api.endpoints import agent, health, conversations, known_issues

api_router = APIRouter()

# Include all the sub-routers
api_router.include_router(agent.router, tags=["Agent"])
api_router.include_router(conversations.router, tags=["History"])
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(known_issues.router, tags=["Issues"])
