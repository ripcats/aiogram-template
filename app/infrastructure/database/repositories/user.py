from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities.user import User
from app.domain.repositories.user import IUserRepository
from app.infrastructure.database.models.user import UserModel


class SqlAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_user(self, telegram_id: int) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def list_users(self, limit: int = 50, offset: int = 0) -> list[User]:
        result = await self._session.execute(
            select(UserModel)
            .order_by(UserModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [_to_entity(m) for m in result.scalars().all()]

    async def save_user(self, user: User) -> User:
        stmt = (
            insert(UserModel)
            .values(
                telegram_id=user.telegram_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                is_bot=user.is_bot,
                is_banned=user.is_banned,
                created_at=user.created_at,
                updated_at=datetime.now(UTC),
            )
            .on_conflict_do_update(
                index_elements=["telegram_id"],
                set_={
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                    "is_banned": user.is_banned,
                    "updated_at": datetime.now(UTC),
                },
            )
            .returning(UserModel)
        )
        result = await self._session.execute(stmt)
        return _to_entity(result.scalar_one())

    async def delete(self, telegram_id: int) -> None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.telegram_id == telegram_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)

    async def exists(self, telegram_id: int) -> bool:
        result = await self._session.execute(
            select(UserModel.telegram_id).where(UserModel.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none() is not None

    async def count_users(self) -> int:
        result = await self._session.execute(select(func.count(UserModel.id)))
        return result.scalar_one()


def _to_entity(model: UserModel) -> User:
    return User(
        telegram_id=model.telegram_id,
        username=model.username,
        first_name=model.first_name,
        last_name=model.last_name,
        is_bot=model.is_bot,
        is_banned=model.is_banned,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )
