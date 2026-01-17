from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.card import Card, FSRSState
from domain.repositories.card_repository import ICardRepository
from infrastructure.database.models.card_model import CardModel


class CardRepository(ICardRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: CardModel) -> Card:
        return Card(
            id=model.id,
            deck_id=model.deck_id,
            front=model.front,
            back=model.back,
            created_at=model.created_at,
            updated_at=model.updated_at,
            fsrs_state=FSRSState(
                stability=model.stability,
                difficulty=model.difficulty,
                ease_factor=model.ease_factor,
                interval=model.interval,
                review_count=model.review_count,
                last_review=model.last_review,
                due_date=model.due_date,
            ),
            audio_url=model.audio_url,
        )

    def _to_model(self, entity: Card) -> CardModel:
        return CardModel(
            id=entity.id,
            deck_id=entity.deck_id,
            front=entity.front,
            back=entity.back,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            stability=entity.fsrs_state.stability,
            difficulty=entity.fsrs_state.difficulty,
            ease_factor=entity.fsrs_state.ease_factor,
            interval=entity.fsrs_state.interval,
            review_count=entity.fsrs_state.review_count,
            last_review=entity.fsrs_state.last_review,
            due_date=entity.fsrs_state.due_date,
            audio_url=entity.audio_url,
        )

    async def create(self, card: Card) -> Card:
        model = self._to_model(card)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, card_id: UUID) -> Optional[Card]:
        result = await self._session.execute(
            select(CardModel).where(CardModel.id == card_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_deck_id(self, deck_id: UUID) -> List[Card]:
        result = await self._session.execute(
            select(CardModel).where(CardModel.deck_id == deck_id)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def get_due_cards(self, deck_id: UUID, limit: Optional[int] = None) -> List[Card]:
        now = datetime.utcnow()
        query = select(CardModel).where(
            CardModel.deck_id == deck_id,
            or_(
                CardModel.due_date.is_(None),
                CardModel.due_date <= now,
            ),
        ).order_by(CardModel.due_date.asc().nullsfirst())
        
        if limit:
            query = query.limit(limit)
            
        result = await self._session.execute(query)
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, card: Card) -> Card:
        card.update()
        result = await self._session.execute(
            select(CardModel).where(CardModel.id == card.id)
        )
        model = result.scalar_one()
        model.front = card.front
        model.back = card.back
        model.updated_at = card.updated_at
        model.stability = card.fsrs_state.stability
        model.difficulty = card.fsrs_state.difficulty
        model.ease_factor = card.fsrs_state.ease_factor
        model.interval = card.fsrs_state.interval
        model.review_count = card.fsrs_state.review_count
        model.last_review = card.fsrs_state.last_review
        model.due_date = card.fsrs_state.due_date
        model.audio_url = card.audio_url
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def delete(self, card_id: UUID) -> bool:
        result = await self._session.execute(
            select(CardModel).where(CardModel.id == card_id)
        )
        model = result.scalar_one_or_none()
        if model:
            await self._session.delete(model)
            await self._session.commit()
            return True
        return False

    async def bulk_create(self, cards: List[Card]) -> List[Card]:
        models = [self._to_model(card) for card in cards]
        self._session.add_all(models)
        await self._session.commit()
        for model in models:
            await self._session.refresh(model)
        return [self._to_entity(model) for model in models]
