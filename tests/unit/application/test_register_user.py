from unittest.mock import AsyncMock

import pytest

from app.application.dto.user import RegisterUserDTO
from app.application.use_cases.register_user import RegisterUserUseCase
from app.domain.entities.user import User
from app.domain.repositories.user import IUserRepository


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock(spec=IUserRepository)


@pytest.fixture
def dto() -> RegisterUserDTO:
    return RegisterUserDTO(
        telegram_id=111222333,
        username="evgeny",
        first_name="Evgeny",
        last_name="Gerber",
    )


@pytest.fixture
def use_case(repo: AsyncMock) -> RegisterUserUseCase:
    return RegisterUserUseCase(repo)


class TestRegisterUserUseCase:
    async def test_new_user_is_saved(
        self, use_case: RegisterUserUseCase, repo: AsyncMock, dto: RegisterUserDTO
    ) -> None:
        repo.get_by_telegram_id.return_value = None
        repo.save.return_value = User(
            telegram_id=dto.telegram_id,
            username=dto.username,
            first_name=dto.first_name,
            last_name=dto.last_name,
        )
        result = await use_case.execute(dto)
        repo.save.assert_awaited_once()
        assert result.telegram_id == dto.telegram_id

    async def test_existing_user_not_saved_again(
        self, use_case: RegisterUserUseCase, repo: AsyncMock, dto: RegisterUserDTO
    ) -> None:
        repo.get_by_telegram_id.return_value = User(
            telegram_id=dto.telegram_id,
            username=dto.username,
            first_name=dto.first_name,
            last_name=dto.last_name,
        )
        result = await use_case.execute(dto)
        repo.save.assert_not_awaited()
        assert result.telegram_id == dto.telegram_id
