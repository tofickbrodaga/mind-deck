from typing import List, Optional
from uuid import UUID

from domain.entities.card import Card
from domain.repositories.card_repository import ICardRepository
from domain.repositories.deck_repository import IDeckRepository
from application.services.fsrs_service import FSRSService


class CreateCardUseCase:
    def __init__(self, card_repository: ICardRepository, deck_repository: IDeckRepository):
        self._card_repository = card_repository
        self._deck_repository = deck_repository

    async def execute(self, deck_id: UUID, front: str, back: str) -> Card:
        # Проверяем существование набора
        deck = await self._deck_repository.get_by_id(deck_id)
        if not deck:
            raise ValueError(f"Deck with id {deck_id} not found")
        
        card = Card.create(deck_id, front, back)
        return await self._card_repository.create(card)


class GetCardUseCase:
    def __init__(self, card_repository: ICardRepository):
        self._card_repository = card_repository

    async def execute(self, card_id: UUID) -> Optional[Card]:
        return await self._card_repository.get_by_id(card_id)


class GetDeckCardsUseCase:
    def __init__(self, card_repository: ICardRepository):
        self._card_repository = card_repository

    async def execute(self, deck_id: UUID) -> List[Card]:
        return await self._card_repository.get_by_deck_id(deck_id)


class UpdateCardUseCase:
    def __init__(self, card_repository: ICardRepository):
        self._card_repository = card_repository

    async def execute(
        self, card_id: UUID, front: Optional[str] = None, back: Optional[str] = None
    ) -> Card:
        card = await self._card_repository.get_by_id(card_id)
        if not card:
            raise ValueError(f"Card with id {card_id} not found")
        
        card.update(front=front, back=back)
        return await self._card_repository.update(card)


class DeleteCardUseCase:
    def __init__(self, card_repository: ICardRepository):
        self._card_repository = card_repository

    async def execute(self, card_id: UUID) -> bool:
        return await self._card_repository.delete(card_id)


class GetDueCardsUseCase:
    def __init__(self, card_repository: ICardRepository):
        self._card_repository = card_repository

    async def execute(self, deck_id: UUID, limit: Optional[int] = None) -> List[Card]:
        return await self._card_repository.get_due_cards(deck_id, limit)


class ReviewCardUseCase:
    def __init__(self, card_repository: ICardRepository, fsrs_service: FSRSService):
        self._card_repository = card_repository
        self._fsrs_service = fsrs_service

    async def execute(self, card_id: UUID, quality: int) -> Card:
        """
        Отметить карточку как просмотренную
        
        Args:
            card_id: ID карточки
            quality: Оценка качества ответа (0-5)
                0: Забыл
                1: Плохо (с подсказкой)
                2: Хорошо (с усилием)
                3: Отлично (легко)
                4: Очень легко
                5: Слишком легко
        """
        if quality < 0 or quality > 5:
            raise ValueError("Quality must be between 0 and 5")
        
        card = await self._card_repository.get_by_id(card_id)
        if not card:
            raise ValueError(f"Card with id {card_id} not found")
        
        # Обновляем состояние FSRS
        card.fsrs_state = self._fsrs_service.review_card(card.fsrs_state, quality)
        card.update()
        
        return await self._card_repository.update(card)
