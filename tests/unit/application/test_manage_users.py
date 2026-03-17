from unittest.mock import AsyncMock

import pytest

from app.application.use_cases.manage_users import BanUserUseCase, UnbanUserUseCase
from app.domain.entities.user import User
from app.domain.exceptions.user import AlreadyBannedError, NotBannedError, UserNotFoundError
from app.domain.repositories.user import IUserRepository


def make_user(*, is_banned: bool = False) -> User:
    return User(
        telegram_id=999,
        username="test",
        first_name="Test",
        last_name=None,
        is_banned=is_banned,
    )


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock(spec=IUserRepository)


class TestBanUserUseCase:
    async def test_bans_active_user(self, repo: AsyncMock) -> None:
        user = make_user(is_banned=False)
        repo.get_user.return_value = user
        repo.save_user.return_value = User(
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_banned=True,
        )
        result = await BanUserUseCase(repo).execute(999)
        assert result.is_banned is True

    async def test_raises_if_already_banned(self, repo: AsyncMock) -> None:
        repo.get_user.return_value = make_user(is_banned=True)
        with pytest.raises(AlreadyBannedError):
            await BanUserUseCase(repo).execute(999)

    async def test_raises_if_not_found(self, repo: AsyncMock) -> None:
        repo.get_user.return_value = None
        with pytest.raises(UserNotFoundError):
            await BanUserUseCase(repo).execute(999)


class TestUnbanUserUseCase:
    async def test_unbans_banned_user(self, repo: AsyncMock) -> None:
        user = make_user(is_banned=True)
        repo.get_user.return_value = user
        repo.save_user.return_value = User(
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_banned=False,
        )
        result = await UnbanUserUseCase(repo).execute(999)
        assert result.is_banned is False

    async def test_raises_if_not_banned(self, repo: AsyncMock) -> None:
        repo.get_user.return_value = make_user(is_banned=False)
        with pytest.raises(NotBannedError):
            await UnbanUserUseCase(repo).execute(999)
