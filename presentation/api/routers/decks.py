from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.database import get_db
from infrastructure.repositories.deck_repository import DeckRepository
from infrastructure.repositories.user_repository import UserRepository
from presentation.schemas.deck_schemas import DeckCreate, DeckUpdate, DeckResponse
from presentation.api.routers.users import get_current_user_dependency
from domain.entities.user import User
from application.use_cases.deck_use_cases import (
    CreateDeckUseCase,
    GetDeckUseCase,
    GetUserDecksUseCase,
    UpdateDeckUseCase,
    DeleteDeckUseCase,
)

router = APIRouter()


@router.post("", response_model=DeckResponse, status_code=status.HTTP_201_CREATED)
async def create_deck(
    deck_data: DeckCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Создать новый набор карточек"""
    deck_repo = DeckRepository(db)
    user_repo = UserRepository(db)
    use_case = CreateDeckUseCase(deck_repo, user_repo)
    
    deck = await use_case.execute(
        user_id=current_user.id,
        title=deck_data.title,
        description=deck_data.description,
    )
    
    return DeckResponse(
        id=deck.id,
        user_id=deck.user_id,
        title=deck.title,
        description=deck.description,
        is_public=deck.is_public,
        created_at=deck.created_at,
        updated_at=deck.updated_at,
    )


@router.get("", response_model=List[DeckResponse])
async def get_user_decks(
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Получить все наборы карточек пользователя"""
    deck_repo = DeckRepository(db)
    use_case = GetUserDecksUseCase(deck_repo)
    
    decks = await use_case.execute(current_user.id)
    
    return [
        DeckResponse(
            id=deck.id,
            user_id=deck.user_id,
            title=deck.title,
            description=deck.description,
            is_public=deck.is_public,
            created_at=deck.created_at,
            updated_at=deck.updated_at,
        )
        for deck in decks
    ]


@router.get("/{deck_id}", response_model=DeckResponse)
async def get_deck(
    deck_id: UUID,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Получить набор карточек по ID"""
    deck_repo = DeckRepository(db)
    use_case = GetDeckUseCase(deck_repo)
    
    deck = await use_case.execute(deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    # Проверяем права доступа
    if deck.user_id != current_user.id and not deck.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return DeckResponse(
        id=deck.id,
        user_id=deck.user_id,
        title=deck.title,
        description=deck.description,
        is_public=deck.is_public,
        created_at=deck.created_at,
        updated_at=deck.updated_at,
    )


@router.put("/{deck_id}", response_model=DeckResponse)
async def update_deck(
    deck_id: UUID,
    deck_data: DeckUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Обновить набор карточек"""
    deck_repo = DeckRepository(db)
    use_case = GetDeckUseCase(deck_repo)
    
    deck = await use_case.execute(deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    if deck.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    update_use_case = UpdateDeckUseCase(deck_repo)
    updated_deck = await update_use_case.execute(
        deck_id=deck_id,
        title=deck_data.title,
        description=deck_data.description,
    )
    
    return DeckResponse(
        id=updated_deck.id,
        user_id=updated_deck.user_id,
        title=updated_deck.title,
        description=updated_deck.description,
        is_public=updated_deck.is_public,
        created_at=updated_deck.created_at,
        updated_at=updated_deck.updated_at,
    )


@router.delete("/{deck_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_deck(
    deck_id: UUID,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Удалить набор карточек"""
    deck_repo = DeckRepository(db)
    use_case = GetDeckUseCase(deck_repo)
    
    deck = await use_case.execute(deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    if deck.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    delete_use_case = DeleteDeckUseCase(deck_repo)
    await delete_use_case.execute(deck_id)
