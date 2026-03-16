from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.application.dto.user import UserResponseDTO
from app.presentation.keyboards.callbacks import (
    OwnerPanelMenuCallback,
    OwnerPanelUserActionCallback,
    OwnerPanelUserOpenCallback,
    OwnerPanelUsersPageCallback,
)
from app.ui import UI


def owner_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=UI.buttons.users_list,
        callback_data=OwnerPanelUsersPageCallback(page=1),
    )
    builder.button(
        text=UI.buttons.close,
        callback_data=OwnerPanelMenuCallback(action="close"),
    )
    builder.adjust(1)
    return builder.as_markup()


def owner_users_keyboard(
    users: list[UserResponseDTO],
    page: int,
    total_pages: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for user in users:
        builder.button(
            text=user.full_name,
            callback_data=OwnerPanelUserOpenCallback(
                telegram_id=user.telegram_id,
            ),
        )

    if total_pages > 1:
        if page > 1:
            builder.button(
                text="«",
                callback_data=OwnerPanelUsersPageCallback(page=page - 1),
            )
        builder.button(
            text=f"{page}/{total_pages}",
            callback_data=OwnerPanelUsersPageCallback(page=page),
        )
        if page < total_pages:
            builder.button(
                text="»",
                callback_data=OwnerPanelUsersPageCallback(page=page + 1),
            )

    builder.button(
        text=UI.buttons.back,
        callback_data=OwnerPanelMenuCallback(action="back"),
    )
    builder.adjust(1)
    return builder.as_markup()


def owner_user_keyboard(
    user: UserResponseDTO,
    page: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text=UI.buttons.user_unban if user.is_banned else UI.buttons.user_ban,
        callback_data=OwnerPanelUserActionCallback(
            action="unban" if user.is_banned else "ban",
            telegram_id=user.telegram_id,
        ),
    )
    builder.button(
        text=UI.buttons.back,
        callback_data=OwnerPanelUsersPageCallback(page=page),
    )
    builder.adjust(1)
    return builder.as_markup()
