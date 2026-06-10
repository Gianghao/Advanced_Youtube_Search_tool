from fastapi import APIRouter
from backend.app.api.routes import auth_router, search_router, video_router, user_router
from backend.app.core.config import settings

api_router = APIRouter()
api_router.include_router(auth_router.router)
api_router.include_router(search_router.router)
api_router.include_router(video_router.router)
api_router.include_router(user_router.router)

# If there were private routes for local testing, they would be included here:
# if settings.ENVIRONMENT == "local":
#     api_router.include_router(private.router)
