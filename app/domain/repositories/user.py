from abc import ABC, abstractmethod

from app.domain.entities.user import User


class IUserRepository(ABC):
    @abstractmethod
    async def get_user(self, telegram_id: int) -> User | None: ...

    @abstractmethod
    async def list_users(self, limit: int = 50, offset: int = 0) -> list[User]: ...

    @abstractmethod
    async def save_user(self, user: User) -> User: ...

    @abstractmethod
    async def delete(self, telegram_id: int) -> None: ...

    @abstractmethod
    async def exists(self, telegram_id: int) -> bool: ...

    @abstractmethod
    async def count_users(self) -> int: ...
