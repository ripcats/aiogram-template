from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class User:
    telegram_id: int
    username: str | None
    first_name: str
    last_name: str | None
    is_bot: bool = False
    is_banned: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def full_name(self) -> str:
        parts = [self.first_name]
        if self.last_name:
            parts.append(self.last_name)
        return " ".join(parts)

    @property
    def mention(self) -> str:
        return f"@{self.username}" if self.username else self.full_name

    def ban(self) -> None:
        from app.domain.exceptions.user import AlreadyBannedError
        if self.is_banned:
            raise AlreadyBannedError(self.telegram_id)
        self.is_banned = True
        self.updated_at = datetime.now(UTC)

    def unban(self) -> None:
        from app.domain.exceptions.user import NotBannedError
        if not self.is_banned:
            raise NotBannedError(self.telegram_id)
        self.is_banned = False
        self.updated_at = datetime.now(UTC)
