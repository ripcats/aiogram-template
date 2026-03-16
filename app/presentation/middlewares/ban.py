from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from app.application.services.ban_cache import BanCacheService
from app.logging_setup import get_logger
from app.ui import UI

logger = get_logger(__name__)


class BanMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message) or event.from_user is None:
            return await handler(event, data)

        container = data.get("dishka_container")
        if container is None:
            return await handler(event, data)

        ban_cache: BanCacheService = await container.get(BanCacheService)
        if await ban_cache.is_banned(event.from_user.id):
            logger.info("ban.blocked", telegram_id=event.from_user.id)
            await event.answer(UI.common.errors.banned)  # type: ignore[attr-defined]
            return None

        return await handler(event, data)
