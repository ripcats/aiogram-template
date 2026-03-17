from app.application.services.ban_cache import BanCacheService
from app.application.dto.user import UserListDTO, UserResponseDTO
from app.domain.entities.user import User
from app.domain.repositories.user import IUserRepository


class GetUserUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._repo = user_repo

    async def execute(self, telegram_id: int) -> UserResponseDTO | None:
        user = await self._repo.get_user(telegram_id)
        return _to_response(user) if user is not None else None


class GetUsersListUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._repo = user_repo

    async def execute(self, limit: int = 50, offset: int = 0) -> UserListDTO:
        users = await self._repo.list_users(limit=limit, offset=offset)
        total = await self._repo.count_users()
        return UserListDTO(
            users=[_to_response(u) for u in users],
            total=total,
        )


class BanUserUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        ban_cache: BanCacheService | None = None,
    ) -> None:
        self._repo = user_repo
        self._ban_cache = ban_cache

    async def execute(self, telegram_id: int) -> UserResponseDTO:
        from app.domain.exceptions.user import UserNotFoundError
        user = await self._repo.get_user(telegram_id)
        if user is None:
            raise UserNotFoundError(telegram_id)
        user.ban()
        saved = await self._repo.save_user(user)
        if self._ban_cache is not None:
            await self._ban_cache.sync_if_cached(telegram_id, True)
        return _to_response(saved)


class UnbanUserUseCase:
    def __init__(
        self,
        user_repo: IUserRepository,
        ban_cache: BanCacheService | None = None,
    ) -> None:
        self._repo = user_repo
        self._ban_cache = ban_cache

    async def execute(self, telegram_id: int) -> UserResponseDTO:
        from app.domain.exceptions.user import UserNotFoundError
        user = await self._repo.get_user(telegram_id)
        if user is None:
            raise UserNotFoundError(telegram_id)
        user.unban()
        saved = await self._repo.save_user(user)
        if self._ban_cache is not None:
            await self._ban_cache.sync_if_cached(telegram_id, False)
        return _to_response(saved)


def _to_response(user: User) -> UserResponseDTO:
    return UserResponseDTO(
        telegram_id=user.telegram_id,
        username=user.username,
        full_name=user.full_name,
        mention=user.mention,
        is_banned=user.is_banned,
    )
