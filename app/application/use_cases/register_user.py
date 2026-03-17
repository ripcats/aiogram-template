from app.application.dto.user import RegisterUserDTO, UserResponseDTO
from app.domain.entities.user import User
from app.domain.repositories.user import IUserRepository
from app.logging_setup import get_logger

logger = get_logger(__name__)


class RegisterUserUseCase:
    def __init__(self, user_repo: IUserRepository) -> None:
        self._repo = user_repo

    async def execute(self, dto: RegisterUserDTO) -> UserResponseDTO:
        existing = await self._repo.get_user(dto.telegram_id)
        if existing is not None:
            logger.debug("user.exists", telegram_id=dto.telegram_id)
            return _to_response(existing)

        user = User(
            telegram_id=dto.telegram_id,
            username=dto.username,
            first_name=dto.first_name,
            last_name=dto.last_name,
            is_bot=dto.is_bot,
        )
        saved = await self._repo.save_user(user)
        logger.info("user.registered", telegram_id=saved.telegram_id)
        return _to_response(saved)


def _to_response(user: User) -> UserResponseDTO:
    return UserResponseDTO(
        telegram_id=user.telegram_id,
        username=user.username,
        full_name=user.full_name,
        mention=user.mention,
        is_banned=user.is_banned,
    )
