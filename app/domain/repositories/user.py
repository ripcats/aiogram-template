from abc import ABC, abstractmethod

from app.domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None: ...

    @abstractmethod
    async def get_all(self, limit: int = 50, offset: int = 0) -> list[User]: ...

    @abstractmethod
    async def save(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, telegram_id: int) -> None: ...

    @abstractmethod
    async def exists(self, telegram_id: int) -> bool: ...

    @abstractmethod
    async def count(self) -> int: ...
