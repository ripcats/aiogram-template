from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from app.application.interfaces.cache import ICacheService
from app.logging_setup import get_logger
from app.runtime_config import get_runtime_config
from app.ui import UI

logger = get_logger(__name__)
runtime_config = get_runtime_config()


class RateLimitMiddleware(BaseMiddleware):
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

        cache: ICacheService = await container.get(ICacheService)
        key = f"rl:{event.from_user.id}"

        count = await cache.increment(key)
        if count == 1:
            await cache.expire(key, runtime_config.rate_limit.window_seconds)

        if count > runtime_config.rate_limit.limit:
            logger.warning("rate_limit.exceeded", telegram_id=event.from_user.id, count=count)
            await event.answer(UI.common.errors.rate_limit)  # type: ignore[attr-defined]
            return None

        return await handler(event, data)
