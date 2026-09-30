
from fastapi import APIRouter

from routes import posts, users

api_router = APIRouter(prefix="/api")

api_router.include_router(users.router,tags=["users"])
api_router.include_router(posts.router,tags=["posts"])