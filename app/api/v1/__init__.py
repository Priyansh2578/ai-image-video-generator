from .auth import router as auth_router
from .users import router as users_router
from .videos import router as videos_router
from .images import router as images_router

__all__ = [
    "auth_router",
    "users_router",
    "videos_router",
    "images_router"
]
