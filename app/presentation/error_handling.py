from aiogram.types import CallbackQuery, Message

from app.logging_setup import get_logger
from app.ui import UI

logger = get_logger(__name__)


async def handle_message_error(message: Message, action: str) -> None:
    telegram_id = message.from_user.id if message.from_user is not None else None
    logger.exception(action, telegram_id=telegram_id)
    await message.answer(UI.common.errors.unknown)  # type: ignore[attr-defined]


async def handle_callback_error(callback: CallbackQuery, action: str) -> None:
    logger.exception(action, telegram_id=callback.from_user.id)
    await callback.answer(UI.common.errors.unknown, show_alert=True)  # type: ignore[attr-defined]
