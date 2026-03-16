import json
from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel


_JSON_PATH = Path(__file__).resolve().parent.parent / "config.json"


class OwnerPanelConfig(BaseModel):
    users_per_page: int = 2


class RateLimitConfig(BaseModel):
    limit: int = 30
    window_seconds: int = 60


class BanCacheConfig(BaseModel):
    key_prefix: str = "is_banned"
    ttl_seconds: int = 30
    refresh_threshold_seconds: int = 10
    refresh_extension_seconds: int = 10


class RuntimeConfig(BaseModel):
    owner_panel: OwnerPanelConfig = OwnerPanelConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()
    ban_cache: BanCacheConfig = BanCacheConfig()


@lru_cache(maxsize=1)
def get_runtime_config() -> RuntimeConfig:
    with _JSON_PATH.open(encoding="utf-8") as file:
        data = json.load(file)
    return RuntimeConfig.model_validate(data)
