from typing import Literal

from aiogram.filters.callback_data import CallbackData


class OwnerPanelMenuCallback(CallbackData, prefix="panelmenu"):
    action: Literal["close", "back"]


class OwnerPanelUsersPageCallback(CallbackData, prefix="panelusers"):
    page: int = 1


class OwnerPanelUserOpenCallback(CallbackData, prefix="paneluser"):
    telegram_id: int


class OwnerPanelUserActionCallback(CallbackData, prefix="paneluseraction"):
    action: Literal["ban", "unban"]
    telegram_id: int
