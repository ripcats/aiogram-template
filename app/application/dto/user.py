from dataclasses import dataclass


@dataclass(frozen=True)
class RegisterUserDTO:
    telegram_id: int
    username: str | None
    first_name: str
    last_name: str | None
    is_bot: bool = False


@dataclass(frozen=True)
class UserResponseDTO:
    telegram_id: int
    username: str | None
    full_name: str
    mention: str
    is_banned: bool


@dataclass(frozen=True)
class UserListDTO:
    users: list[UserResponseDTO]
    total: int
