from aiogram import Dispatcher

from app.presentation.middlewares.ban import BanMiddleware
from app.presentation.middlewares.rate_limit import RateLimitMiddleware


def setup_middlewares(dp: Dispatcher) -> None:
    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(BanMiddleware())


__all__ = ["setup_middlewares"]
