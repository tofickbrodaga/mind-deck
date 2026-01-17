from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.deck import Deck


class IDeckRepository(ABC):
    @abstractmethod
    async def create(self, deck: Deck) -> Deck:
        pass

    @abstractmethod
    async def get_by_id(self, deck_id: UUID) -> Optional[Deck]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID) -> List[Deck]:
        pass

    @abstractmethod
    async def update(self, deck: Deck) -> Deck:
        pass

    @abstractmethod
    async def delete(self, deck_id: UUID) -> bool:
        pass

    @abstractmethod
    async def get_public_decks(self, limit: int = 20, offset: int = 0) -> List[Deck]:
        pass
