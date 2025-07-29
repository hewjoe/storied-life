"""
Main API router for version 1 endpoints.
"""

from fastapi import APIRouter

from app.api.v1.endpoints import auth
# from app.api.v1.endpoints import legacies, stories, users, chat

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
# TODO: Uncomment these as the schemas and services are implemented
# api_router.include_router(users.router, prefix="/users", tags=["users"])
# api_router.include_router(legacies.router, prefix="/legacies", tags=["legacies"])
# api_router.include_router(stories.router, prefix="/stories", tags=["stories"])
# api_router.include_router(chat.router, prefix="/chat", tags=["ai-chat"])

@api_router.get("/status")
async def api_status():
    """API status endpoint."""
    return {
        "status": "active",
        "message": "Storied Life API v1 is running",
        "version": "0.1.0"
    } 