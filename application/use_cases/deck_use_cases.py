from typing import List, Optional
from uuid import UUID

from domain.entities.deck import Deck
from domain.repositories.deck_repository import IDeckRepository
from domain.repositories.user_repository import IUserRepository


class CreateDeckUseCase:
    def __init__(self, deck_repository: IDeckRepository, user_repository: IUserRepository):
        self._deck_repository = deck_repository
        self._user_repository = user_repository

    async def execute(self, user_id: UUID, title: str, description: Optional[str] = None) -> Deck:
        # Проверяем существование пользователя
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            raise ValueError(f"User with id {user_id} not found")
        
        deck = Deck.create(user_id, title, description)
        return await self._deck_repository.create(deck)


class GetDeckUseCase:
    def __init__(self, deck_repository: IDeckRepository):
        self._deck_repository = deck_repository

    async def execute(self, deck_id: UUID) -> Optional[Deck]:
        return await self._deck_repository.get_by_id(deck_id)


class GetUserDecksUseCase:
    def __init__(self, deck_repository: IDeckRepository):
        self._deck_repository = deck_repository

    async def execute(self, user_id: UUID) -> List[Deck]:
        return await self._deck_repository.get_by_user_id(user_id)


class UpdateDeckUseCase:
    def __init__(self, deck_repository: IDeckRepository):
        self._deck_repository = deck_repository

    async def execute(
        self, deck_id: UUID, title: Optional[str] = None, description: Optional[str] = None
    ) -> Deck:
        deck = await self._deck_repository.get_by_id(deck_id)
        if not deck:
            raise ValueError(f"Deck with id {deck_id} not found")
        
        deck.update(title=title, description=description)
        return await self._deck_repository.update(deck)


class DeleteDeckUseCase:
    def __init__(self, deck_repository: IDeckRepository):
        self._deck_repository = deck_repository

    async def execute(self, deck_id: UUID) -> bool:
        return await self._deck_repository.delete(deck_id)
