from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr, computed_field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotConfig(BaseSettings):
    token: SecretStr
    owner_id: int
    webhook_host: str | None = None
    webhook_path: str = "/webhook"
    webhook_secret: SecretStr | None = None

    @computed_field  # type: ignore[misc]
    @property
    def webhook_url(self) -> str | None:
        if self.webhook_host is None:
            return None
        return f"{self.webhook_host}{self.webhook_path}"

    model_config = SettingsConfigDict(env_prefix="bot_", case_sensitive=True)


class ServerConfig(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8080

    model_config = SettingsConfigDict(env_prefix="server_", case_sensitive=True)


class PostgresConfig(BaseSettings):
    host: str = "postgres"
    port: int = 5432
    user: str = "bot"
    password: SecretStr = SecretStr("botpass")
    db: str = "botdb"

    @computed_field  # type: ignore[misc]
    @property
    def dsn(self) -> str:
        return (
            f"postgresql+asyncpg://{self.user}:{self.password.get_secret_value()}"
            f"@{self.host}:{self.port}/{self.db}"
        )

    model_config = SettingsConfigDict(env_prefix="postgres_", case_sensitive=True)


class RedisConfig(BaseSettings):
    host: str = "redis"
    port: int = 6379
    db: int = 0
    password: SecretStr | None = None

    @computed_field  # type: ignore[misc]
    @property
    def dsn(self) -> str:
        auth = f":{self.password.get_secret_value()}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"

    model_config = SettingsConfigDict(env_prefix="redis_", case_sensitive=True)


class Config(BaseSettings):
    bot_mode: Literal["dev", "prod"] = "dev"
    log_level: str = "INFO"

    bot: BotConfig = Field(default_factory=BotConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)
    postgres: PostgresConfig = Field(default_factory=PostgresConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)

    @model_validator(mode="after")
    def validate_webhook_in_prod(self) -> "Config":
        if self.bot_mode == "dev":
            return self
        missing: list[str] = []
        if self.bot.webhook_host is None:
            missing.append("bot_webhook_host")
        if self.bot.webhook_secret is None:
            missing.append("bot_webhook_secret")
        if missing:
            raise ValueError(f"bot_mode=prod requires: {', '.join(missing)}")
        return self

    model_config = SettingsConfigDict(
        env_prefix="",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )


@lru_cache(maxsize=1)
def get_config() -> Config:
    return Config()
