from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.user import User
from domain.repositories.user_repository import IUserRepository
from infrastructure.database.models.user_model import UserModel


class UserRepository(IUserRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: UserModel) -> User:
        return User(
            id=model.id,
            email=model.email,
            username=model.username,
            hashed_password=model.hashed_password,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_active=model.is_active,
        )

    def _to_model(self, entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            email=entity.email,
            username=entity.username,
            hashed_password=entity.hashed_password,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_active=entity.is_active,
        )

    async def create(self, user: User) -> User:
        model = self._to_model(user)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def update(self, user: User) -> User:
        user.update()
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user.id)
        )
        model = result.scalar_one()
        model.email = user.email
        model.username = user.username
        model.hashed_password = user.hashed_password
        model.updated_at = user.updated_at
        model.is_active = user.is_active
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.commit()
            return True
        return False
