from aiogram import Dispatcher, Router

from app.presentation.filters.owner import IsOwnerFilter
from app.presentation.handlers.owner import router as owner_router
from app.presentation.handlers.users import router as users_router

_owner_container = Router(name="owner_container")
_owner_container.message.filter(IsOwnerFilter())
_owner_container.callback_query.filter(IsOwnerFilter())
_owner_container.include_router(owner_router)

ALL_ROUTERS: list[Router] = [
    users_router,
    _owner_container,
]


def setup_routers(dp: Dispatcher) -> None:
    for router in ALL_ROUTERS:
        dp.include_router(router)


__all__ = ["ALL_ROUTERS", "setup_routers"]
