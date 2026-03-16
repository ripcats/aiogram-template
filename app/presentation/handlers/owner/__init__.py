from aiogram import Router

from app.presentation.handlers.owner.owner_panel import router as owner_panel_router

router = Router(name="owner")
router.include_router(owner_panel_router)

__all__ = ["router"]
