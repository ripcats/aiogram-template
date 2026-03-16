class DomainError(Exception):
    ...


class UserNotFoundError(DomainError):
    def __init__(self, telegram_id: int) -> None:
        super().__init__(f"User {telegram_id} not found")
        self.telegram_id = telegram_id


class AlreadyBannedError(DomainError):
    def __init__(self, telegram_id: int) -> None:
        super().__init__(f"User {telegram_id} is already banned")
        self.telegram_id = telegram_id


class NotBannedError(DomainError):
    def __init__(self, telegram_id: int) -> None:
        super().__init__(f"User {telegram_id} is not banned")
        self.telegram_id = telegram_id
