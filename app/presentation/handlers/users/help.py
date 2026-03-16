from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.presentation.error_handling import handle_message_error
from app.ui import UI

router = Router(name="users_help")


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    try:
        await message.answer(UI.common.help.text)  # type: ignore[attr-defined]
    except Exception:
        await handle_message_error(message, "cmd.help.failed")
