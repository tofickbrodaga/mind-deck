from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.card import Card


class ICardRepository(ABC):
    @abstractmethod
    async def create(self, card: Card) -> Card:
        pass

    @abstractmethod
    async def get_by_id(self, card_id: UUID) -> Optional[Card]:
        pass

    @abstractmethod
    async def get_by_deck_id(self, deck_id: UUID) -> List[Card]:
        pass

    @abstractmethod
    async def get_due_cards(self, deck_id: UUID, limit: Optional[int] = None) -> List[Card]:
        pass

    @abstractmethod
    async def update(self, card: Card) -> Card:
        pass

    @abstractmethod
    async def delete(self, card_id: UUID) -> bool:
        pass

    @abstractmethod
    async def bulk_create(self, cards: List[Card]) -> List[Card]:
        pass
