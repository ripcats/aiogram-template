from app.application.interfaces.cache import ICacheService
from app.domain.repositories.user import IUserRepository
from app.runtime_config import get_runtime_config

runtime_config = get_runtime_config()


class BanCacheService:
    def __init__(self, cache: ICacheService, user_repo: IUserRepository) -> None:
        self._cache = cache
        self._user_repo = user_repo

    async def is_banned(self, telegram_id: int) -> bool:
        key = self._build_key(telegram_id)
        cached = await self._cache.get(key)
        if isinstance(cached, bool):
            await self._refresh_ttl_if_needed(key)
            return cached

        user = await self._user_repo.get_by_telegram_id(telegram_id)
        is_banned = bool(user and user.is_banned)
        await self._cache.set(
            key,
            is_banned,
            ttl_seconds=runtime_config.ban_cache.ttl_seconds,
        )
        return is_banned

    async def sync_if_cached(self, telegram_id: int, is_banned: bool) -> None:
        key = self._build_key(telegram_id)
        if await self._cache.exists(key):
            await self._cache.set(
                key,
                is_banned,
                ttl_seconds=runtime_config.ban_cache.ttl_seconds,
            )

    async def _refresh_ttl_if_needed(self, key: str) -> None:
        ttl = await self._cache.ttl(key)
        if (
            ttl is not None
            and ttl <= runtime_config.ban_cache.refresh_threshold_seconds
        ):
            await self._cache.expire(
                key,
                ttl + runtime_config.ban_cache.refresh_extension_seconds,
            )

    @staticmethod
    def _build_key(telegram_id: int) -> str:
        return f"{runtime_config.ban_cache.key_prefix}:{telegram_id}"
