from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.deck import Deck
from domain.repositories.deck_repository import IDeckRepository
from infrastructure.database.models.deck_model import DeckModel


class DeckRepository(IDeckRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: DeckModel) -> Deck:
        return Deck(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            description=model.description,
            created_at=model.created_at,
            updated_at=model.updated_at,
            is_public=model.is_public,
        )

    def _to_model(self, entity: Deck) -> DeckModel:
        return DeckModel(
            id=entity.id,
            user_id=entity.user_id,
            title=entity.title,
            description=entity.description,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            is_public=entity.is_public,
        )

    async def create(self, deck: Deck) -> Deck:
        model = self._to_model(deck)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, deck_id: UUID) -> Optional[Deck]:
        result = await self._session.execute(
            select(DeckModel).where(DeckModel.id == deck_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID) -> List[Deck]:
        result = await self._session.execute(
            select(DeckModel).where(DeckModel.user_id == user_id)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, deck: Deck) -> Deck:
        deck.update()
        result = await self._session.execute(
            select(DeckModel).where(DeckModel.id == deck.id)
        )
        model = result.scalar_one()
        model.title = deck.title
        model.description = deck.description
        model.updated_at = deck.updated_at
        model.is_public = deck.is_public
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, deck_id: UUID) -> bool:
        result = await self._session.execute(
            select(DeckModel).where(DeckModel.id == deck_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.commit()
            return True
        return False

    async def get_public_decks(self, limit: int = 20, offset: int = 0) -> List[Deck]:
        result = await self._session.execute(
            select(DeckModel)
            .where(DeckModel.is_public == True)
            .limit(limit)
            .offset(offset)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]
