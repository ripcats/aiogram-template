from abc import ABC, abstractmethod
from typing import Any


class ICacheService(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any | None: ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl_seconds: int | None = None) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def exists(self, key: str) -> bool: ...

    @abstractmethod
    async def increment(self, key: str, amount: int = 1) -> int: ...

    @abstractmethod
    async def expire(self, key: str, ttl_seconds: int) -> None: ...

    @abstractmethod
    async def ttl(self, key: str) -> int | None: ...
