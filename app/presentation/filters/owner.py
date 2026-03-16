from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery, TelegramObject

from app.config import get_config


class IsOwnerFilter(BaseFilter):
    async def __call__(self, event: TelegramObject) -> bool:
        owner_id = get_config().bot.owner_id

        if isinstance(event, Message):
            return event.from_user is not None and event.from_user.id == owner_id

        if isinstance(event, CallbackQuery):
            return event.from_user.id == owner_id

        return False
