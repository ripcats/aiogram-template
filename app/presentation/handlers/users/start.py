from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from dishka.integrations.aiogram import FromDishka

from app.application.dto.user import RegisterUserDTO
from app.application.use_cases.register_user import RegisterUserUseCase
from app.logging_setup import get_logger
from app.presentation.error_handling import handle_message_error
from app.ui import UI

logger = get_logger(__name__)

router = Router(name="users_start")


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    register_user: FromDishka[RegisterUserUseCase],
) -> None:
    if message.from_user is None:
        return

    try:
        user = await register_user.execute(
            RegisterUserDTO(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                is_bot=message.from_user.is_bot,
            )
        )
        logger.info("cmd.start", telegram_id=user.telegram_id)
        await message.answer(
            UI.common.start.welcome.format(full_name=user.full_name)  # type: ignore[attr-defined]
        )
    except Exception:
        await handle_message_error(message, "cmd.start.failed")
