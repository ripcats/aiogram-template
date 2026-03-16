import pytest

from app.domain.entities.user import User
from app.domain.exceptions.user import AlreadyBannedError, NotBannedError


@pytest.fixture
def user() -> User:
    return User(
        telegram_id=111222333,
        username="evgeny",
        first_name="Evgeny",
        last_name="Gerber",
    )


class TestUserEntity:
    def test_full_name(self, user: User) -> None:
        assert user.full_name == "Evgeny Gerber"

    def test_full_name_no_last(self) -> None:
        u = User(telegram_id=1, username=None, first_name="Ivan", last_name=None)
        assert u.full_name == "Ivan"

    def test_mention_with_username(self, user: User) -> None:
        assert user.mention == "@evgeny"

    def test_mention_no_username(self) -> None:
        u = User(telegram_id=1, username=None, first_name="Ivan", last_name=None)
        assert u.mention == "Ivan"

    def test_ban(self, user: User) -> None:
        user.ban()
        assert user.is_banned is True

    def test_ban_twice_raises(self, user: User) -> None:
        user.ban()
        with pytest.raises(AlreadyBannedError):
            user.ban()

    def test_unban(self, user: User) -> None:
        user.ban()
        user.unban()
        assert user.is_banned is False

    def test_unban_not_banned_raises(self, user: User) -> None:
        with pytest.raises(NotBannedError):
            user.unban()
