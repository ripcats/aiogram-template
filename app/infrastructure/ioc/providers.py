from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.interfaces.cache import ICacheService
from app.application.services.ban_cache import BanCacheService
from app.application.use_cases.manage_users import (
    BanUserUseCase,
    GetUserUseCase,
    GetUsersListUseCase,
    UnbanUserUseCase,
)
from app.application.use_cases.register_user import RegisterUserUseCase
from app.config import Config, PostgresConfig, RedisConfig, get_config
from app.domain.repositories.user import IUserRepository
from app.infrastructure.cache.redis import RedisCacheService, build_redis
from app.infrastructure.database.engine import build_engine, build_session_factory
from app.infrastructure.database.repositories.user import SqlAlchemyUserRepository


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def config(self) -> Config:
        return get_config()

    @provide
    def postgres_config(self, c: Config) -> PostgresConfig:
        return c.postgres

    @provide
    def redis_config(self, c: Config) -> RedisConfig:
        return c.redis


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def engine(self, config: PostgresConfig) -> AsyncEngine:
        return build_engine(config)

    @provide(scope=Scope.APP)
    def session_factory(
        self, engine: AsyncEngine
    ) -> async_sessionmaker[AsyncSession]:
        return build_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession, None]:
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise


class CacheProvider(Provider):
    @provide(scope=Scope.APP)
    def redis(self, config: RedisConfig) -> Redis:  # type: ignore[type-arg]
        return build_redis(config)

    @provide(scope=Scope.REQUEST)
    def cache_service(self, redis: Redis) -> ICacheService:  # type: ignore[type-arg]
        return RedisCacheService(redis)


class RepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def user_repository(self, session: AsyncSession) -> IUserRepository:
        return SqlAlchemyUserRepository(session)


class UseCaseProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def ban_cache(self, cache: ICacheService, repo: IUserRepository) -> BanCacheService:
        return BanCacheService(cache, repo)

    @provide
    def register_user(self, repo: IUserRepository) -> RegisterUserUseCase:
        return RegisterUserUseCase(repo)

    @provide
    def get_users_list(self, repo: IUserRepository) -> GetUsersListUseCase:
        return GetUsersListUseCase(repo)

    @provide
    def get_user(self, repo: IUserRepository) -> GetUserUseCase:
        return GetUserUseCase(repo)

    @provide
    def ban_user(self, repo: IUserRepository, ban_cache: BanCacheService) -> BanUserUseCase:
        return BanUserUseCase(repo, ban_cache)

    @provide
    def unban_user(self, repo: IUserRepository, ban_cache: BanCacheService) -> UnbanUserUseCase:
        return UnbanUserUseCase(repo, ban_cache)


def create_providers() -> list[Provider]:
    return [
        ConfigProvider(),
        DatabaseProvider(),
        CacheProvider(),
        RepositoryProvider(),
        UseCaseProvider(),
    ]
