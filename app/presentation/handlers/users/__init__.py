from aiogram import Router

from app.presentation.handlers.users.help import router as help_router
from app.presentation.handlers.users.start import router as start_router

router = Router(name="users")
router.include_router(start_router)
router.include_router(help_router)

__all__ = ["router"]
