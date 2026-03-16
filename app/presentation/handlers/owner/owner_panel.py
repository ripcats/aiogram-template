from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from dishka.integrations.aiogram import FromDishka

from app.application.dto.user import UserResponseDTO
from app.application.interfaces.cache import ICacheService
from app.application.use_cases.manage_users import (
    BanUserUseCase,
    GetUsersListUseCase,
    UnbanUserUseCase,
)
from app.config import get_config
from app.logging_setup import get_logger
from app.presentation.error_handling import handle_callback_error, handle_message_error
from app.presentation.keyboards.callbacks import (
    OwnerPanelMenuCallback,
    OwnerPanelUserActionCallback,
    OwnerPanelUserOpenCallback,
    OwnerPanelUsersPageCallback,
)
from app.presentation.keyboards.owner import (
    owner_menu_keyboard,
    owner_user_keyboard,
    owner_users_keyboard,
)
from app.runtime_config import get_runtime_config
from app.ui import UI

logger = get_logger(__name__)

router = Router(name="owner_panel")
runtime_config = get_runtime_config()
PANEL_PAGE_KEY_PREFIX = "owner_panel_page"


def _panel_page_cache_key(telegram_id: int) -> str:
    return f"{PANEL_PAGE_KEY_PREFIX}:{telegram_id}"


async def _clear_panel_message(
    cache: ICacheService,
    telegram_id: int,
) -> None:
    await cache.delete(_panel_page_cache_key(telegram_id))


async def _store_current_page(
    cache: ICacheService,
    telegram_id: int,
    page: int,
) -> None:
    await cache.set(_panel_page_cache_key(telegram_id), page)


async def _get_current_page(
    cache: ICacheService,
    telegram_id: int,
) -> int:
    page = await cache.get(_panel_page_cache_key(telegram_id))
    return page if isinstance(page, int) and page > 0 else 1


async def _load_users_page(
    get_users: GetUsersListUseCase,
    page: int,
) -> tuple[list[UserResponseDTO], int]:
    page_size = runtime_config.owner_panel.users_per_page
    result = await get_users.execute(limit=page_size, offset=(page - 1) * page_size)
    total_pages = max(1, (result.total + page_size - 1) // page_size)
    return result.users, total_pages


async def _find_user(
    get_users: GetUsersListUseCase,
    telegram_id: int,
) -> UserResponseDTO | None:
    result = await get_users.execute(limit=200, offset=0)
    return next((user for user in result.users if user.telegram_id == telegram_id), None)


def _menu_text() -> str:
    return f"{UI.owner.panel.title}\n\n{UI.owner.panel.subtitle}"


def _users_text(users: list[UserResponseDTO]) -> str:
    if users:
        return UI.owner.panel.users_list_title
    return f"{UI.owner.panel.users_list_title}\n\n{UI.owner.panel.users_list_empty}"


def _user_text(user: UserResponseDTO) -> str:
    status = (
        UI.owner.panel.user_status_banned
        if user.is_banned
        else UI.owner.panel.user_status_active
    )
    return UI.owner.panel.user_info.format(
        telegram_id=user.telegram_id,
        full_name=user.full_name,
        mention=user.mention,
        status=status,
    )


@router.message(Command("panel"))
async def cmd_panel(
    message: Message,
    cache: FromDishka[ICacheService],
) -> None:
    if message.from_user is None:
        return

    try:
        await message.answer(
            _menu_text(),
            reply_markup=owner_menu_keyboard(),
        )
        await _store_current_page(cache, message.from_user.id, 1)
        logger.info("cmd.panel", telegram_id=message.from_user.id)
    except Exception:
        await handle_message_error(message, "cmd.panel.failed")


@router.callback_query(OwnerPanelMenuCallback.filter(F.action == "back"))
async def show_menu(
    callback: CallbackQuery,
) -> None:
    try:
        if callback.message is None:
            return
        await callback.message.edit_text(
            _menu_text(),
            reply_markup=owner_menu_keyboard(),
        )
        await callback.answer()
    except Exception:
        await handle_callback_error(callback, "owner.menu.failed")


@router.callback_query(OwnerPanelUsersPageCallback.filter())
async def show_users(
    callback: CallbackQuery,
    callback_data: OwnerPanelUsersPageCallback,
    get_users: FromDishka[GetUsersListUseCase],
    cache: FromDishka[ICacheService],
) -> None:
    try:
        if callback.message is None:
            return

        users, total_pages = await _load_users_page(get_users, callback_data.page)
        page = min(max(1, callback_data.page), total_pages)
        if page != callback_data.page:
            users, total_pages = await _load_users_page(get_users, page)
        await _store_current_page(cache, callback.from_user.id, page)

        await callback.message.edit_text(
            _users_text(users),
            reply_markup=owner_users_keyboard(users, page, total_pages),
        )
        await callback.answer()
    except Exception:
        await handle_callback_error(callback, "owner.users.failed")


@router.callback_query(OwnerPanelUserOpenCallback.filter())
async def show_user(
    callback: CallbackQuery,
    callback_data: OwnerPanelUserOpenCallback,
    get_users: FromDishka[GetUsersListUseCase],
    cache: FromDishka[ICacheService],
) -> None:
    try:
        if callback.message is None:
            return

        user = await _find_user(get_users, callback_data.telegram_id)
        if user is None:
            await callback.answer(UI.owner.panel.user_not_found, show_alert=True)
            return

        current_page = await _get_current_page(cache, callback.from_user.id)
        await callback.message.edit_text(
            _user_text(user),
            reply_markup=owner_user_keyboard(user, current_page),
        )
        await callback.answer()
    except Exception:
        await handle_callback_error(callback, "owner.user.failed")


@router.callback_query(OwnerPanelUserActionCallback.filter())
async def handle_user_action(
    callback: CallbackQuery,
    callback_data: OwnerPanelUserActionCallback,
    get_users: FromDishka[GetUsersListUseCase],
    ban_user: FromDishka[BanUserUseCase],
    unban_user: FromDishka[UnbanUserUseCase],
    cache: FromDishka[ICacheService],
) -> None:
    try:
        if callback.message is None:
            return

        if callback_data.action == "ban" and callback_data.telegram_id == get_config().bot.owner_id:
            await callback.answer(UI.owner.panel.owner_ban_forbidden, show_alert=True)
            return

        if callback_data.action == "ban":
            await ban_user.execute(callback_data.telegram_id)
            logger.info("owner.ban", target=callback_data.telegram_id)
            await callback.answer(UI.callback_answers.action_banned)
        else:
            await unban_user.execute(callback_data.telegram_id)
            logger.info("owner.unban", target=callback_data.telegram_id)
            await callback.answer(UI.callback_answers.action_unbanned)

        user = await _find_user(get_users, callback_data.telegram_id)
        if user is None:
            await callback.answer(UI.owner.panel.user_not_found, show_alert=True)
            return

        current_page = await _get_current_page(cache, callback.from_user.id)
        await callback.message.edit_text(
            _user_text(user),
            reply_markup=owner_user_keyboard(user, current_page),
        )
    except Exception:
        await handle_callback_error(callback, "owner.action.failed")


@router.callback_query(OwnerPanelMenuCallback.filter(F.action == "close"))
async def close_panel(
    callback: CallbackQuery,
    cache: FromDishka[ICacheService],
) -> None:
    try:
        if callback.message is not None:
            await callback.message.delete()
        await _clear_panel_message(cache, callback.from_user.id)
        await callback.answer()
    except Exception:
        await handle_callback_error(callback, "owner.close.failed")
