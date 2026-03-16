from aiogram import Bot, Dispatcher
from aiogram.types import Update
from fastapi import FastAPI, Header, HTTPException, Request, status

from app.config import BotConfig
from app.logging_setup import get_logger

logger = get_logger(__name__)


def create_app(bot: Bot, dp: Dispatcher, config: BotConfig) -> FastAPI:
    app = FastAPI(title="aiogram-template webhook", docs_url=None, redoc_url=None)

    @app.post(config.webhook_path)
    async def webhook(
        request: Request,
        x_telegram_bot_api_secret_token: str | None = Header(default=None),
    ) -> dict[str, str]:
        if x_telegram_bot_api_secret_token != config.webhook_secret.get_secret_value():
            logger.warning("webhook.bad_secret")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        body = await request.json()
        update = Update.model_validate(body)
        await dp.feed_update(bot=bot, update=update)
        return {"ok": "true"}

    @app.get("/healthz")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
