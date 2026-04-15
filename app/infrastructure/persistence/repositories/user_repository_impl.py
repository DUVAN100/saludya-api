from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.output.i_user_repository import IUserRepository
from app.domain.entities.user import User
from app.domain.value_objects.email import Email
from app.domain.value_objects.user_role import UserRole
from app.infrastructure.persistence.models.user_model import UserModel


class UserRepositoryImpl(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, user: User) -> User:
        model = _to_model(user)
        self._session.add(model)
        await self._session.flush()   # obtiene id generado sin hacer commit
        return _to_entity(model)

    async def find_by_id(self, user_id: UUID) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def find_by_email(self, email: str) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def exists_by_email(self, email: str) -> bool:
        result = await self._session.execute(
            select(UserModel.id).where(UserModel.email == email)
        )
        return result.scalar_one_or_none() is not None

    async def update(self, user: User) -> User:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one()
        model.email = user.email.value
        model.password_hash = user.password_hash
        model.role = user.role.value
        model.is_active = user.is_active
        model.updated_at = user.updated_at
        await self._session.flush()
        return _to_entity(model)


# ── Mappers ───────────────────────────────────────────────────────────────────

def _to_model(user: User) -> UserModel:
    return UserModel(
        id=user.id,
        email=user.email.value,
        password_hash=user.password_hash,
        role=user.role.value,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _to_entity(model: UserModel) -> User:
    return User(
        id=model.id,
        email=Email(model.email),
        password_hash=model.password_hash,
        role=UserRole(model.role),
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )