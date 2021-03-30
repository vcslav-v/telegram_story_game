"""Routes."""
from fastapi import APIRouter

from data_base.local_routes import chapter, message, story, telegram_user

routes = APIRouter()

routes.include_router(telegram_user.router, prefix='/telegram_user')
routes.include_router(story.router, prefix='/story')
routes.include_router(chapter.router, prefix='/chapter')
routes.include_router(message.router, prefix='/message')
