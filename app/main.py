import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import (
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
    BotCommandScopeDefault,
)
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisStorage
from aiogram_dialog import setup_dialogs
from dishka import make_async_container
from dishka.integrations.aiogram import setup_dishka

from app.config import Config, get_config
from app.infrastructure.cache.redis import build_redis
from app.infrastructure.database.engine import build_engine
from app.infrastructure.database.models.user import Base
from app.infrastructure.ioc.providers import create_providers
from app.logging_setup import get_logger, setup_logging
from app.presentation.middlewares import setup_middlewares
from app.presentation.routers import setup_routers

logger = get_logger(__name__)


async def _build_dispatcher(config: Config) -> tuple[Bot, Dispatcher]:
    redis = build_redis(config.redis)
    storage = RedisStorage(
        redis=redis,
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )

    bot = Bot(
        token=config.bot.token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=storage)

    setup_middlewares(dp)

    container = make_async_container(*create_providers())
    setup_dishka(container=container, router=dp, auto_inject=True)

    setup_routers(dp)
    setup_dialogs(dp)

    dp["_redis"] = redis
    dp["_container"] = container
    return bot, dp


async def _ensure_database_schema(config: Config) -> None:
    engine = build_engine(config.postgres)
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
    finally:
        await engine.dispose()


async def _clear_bot_commands(bot: Bot) -> None:
    scopes = (
        BotCommandScopeDefault(),
        BotCommandScopeAllPrivateChats(),
        BotCommandScopeAllGroupChats(),
        BotCommandScopeAllChatAdministrators(),
    )
    for scope in scopes:
        await bot.delete_my_commands(scope=scope)


async def _run_polling(bot: Bot, dp: Dispatcher) -> None:
    logger.info("mode.polling")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await _shutdown(bot, dp)


async def _run_webhook(bot: Bot, dp: Dispatcher, config: Config) -> None:
    import hypercorn.asyncio
    from hypercorn.config import Config as HypercornConfig

    from app.presentation.webhook import create_app

    webhook_url = config.bot.webhook_url
    webhook_secret = config.bot.webhook_secret
    if webhook_url is None or webhook_secret is None:
        raise RuntimeError("Webhook config is required when bot_mode=prod")

    await bot.set_webhook(
        url=webhook_url,
        secret_token=webhook_secret.get_secret_value(),
        drop_pending_updates=True,
    )
    logger.info("webhook.set", url=webhook_url)

    app = create_app(bot=bot, dp=dp, config=config.bot)

    hc = HypercornConfig()
    hc.bind = [f"{config.server.host}:{config.server.port}"]
    hc.accesslog = "-"

    logger.info("server.start", host=config.server.host, port=config.server.port)
    try:
        await hypercorn.asyncio.serve(app, hc)  # type: ignore[arg-type]
    finally:
        await bot.delete_webhook()
        await _shutdown(bot, dp)


async def _shutdown(bot: Bot, dp: Dispatcher) -> None:
    redis = dp.get("_redis")
    container = dp.get("_container")
    if container is not None:
        await container.close()
    if redis is not None:
        await redis.aclose()
    await bot.session.close()
    logger.info("shutdown.complete")


async def main() -> None:
    config = get_config()
    setup_logging(config)
    await _ensure_database_schema(config)
    bot, dp = await _build_dispatcher(config)
    await _clear_bot_commands(bot)
    if config.bot_mode == "dev":
        await _run_polling(bot, dp)
    else:
        await _run_webhook(bot, dp, config)


if __name__ == "__main__":
    asyncio.run(main())
