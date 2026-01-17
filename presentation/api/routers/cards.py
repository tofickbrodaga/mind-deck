from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.database import get_db
from infrastructure.repositories.card_repository import CardRepository
from infrastructure.repositories.deck_repository import DeckRepository
from presentation.schemas.card_schemas import CardCreate, CardUpdate, CardResponse, ReviewCardRequest, FSRSStateResponse
from presentation.api.routers.users import get_current_user_dependency
from domain.entities.user import User
from application.use_cases.card_use_cases import (
    CreateCardUseCase,
    GetCardUseCase,
    GetDeckCardsUseCase,
    UpdateCardUseCase,
    DeleteCardUseCase,
    GetDueCardsUseCase,
    ReviewCardUseCase,
)
from application.services.fsrs_service import FSRSService

router = APIRouter()


@router.post("/deck/{deck_id}", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def create_card(
    deck_id: UUID,
    card_data: CardCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Создать новую карточку"""
    deck_repo = DeckRepository(db)
    deck = await deck_repo.get_by_id(deck_id)
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
    
    card_repo = CardRepository(db)
    use_case = CreateCardUseCase(card_repo, deck_repo)
    
    card = await use_case.execute(
        deck_id=deck_id,
        front=card_data.front,
        back=card_data.back,
    )
    
    return _card_to_response(card)


@router.get("/deck/{deck_id}", response_model=List[CardResponse])
async def get_deck_cards(
    deck_id: UUID,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Получить все карточки набора"""
    deck_repo = DeckRepository(db)
    deck = await deck_repo.get_by_id(deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    if deck.user_id != current_user.id and not deck.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    card_repo = CardRepository(db)
    use_case = GetDeckCardsUseCase(card_repo)
    
    cards = await use_case.execute(deck_id)
    
    return [_card_to_response(card) for card in cards]


@router.get("/deck/{deck_id}/due", response_model=List[CardResponse])
async def get_due_cards(
    deck_id: UUID,
    limit: Optional[int] = None,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Получить карточки для повторения"""
    deck_repo = DeckRepository(db)
    deck = await deck_repo.get_by_id(deck_id)
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
    
    card_repo = CardRepository(db)
    use_case = GetDueCardsUseCase(card_repo)
    
    cards = await use_case.execute(deck_id, limit)
    
    return [_card_to_response(card) for card in cards]


@router.get("/{card_id}", response_model=CardResponse)
async def get_card(
    card_id: UUID,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Получить карточку по ID"""
    card_repo = CardRepository(db)
    use_case = GetCardUseCase(card_repo)
    
    card = await use_case.execute(card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Проверяем права доступа через набор
    deck_repo = DeckRepository(db)
    deck = await deck_repo.get_by_id(card.deck_id)
    if not deck:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Deck not found"
        )
    
    if deck.user_id != current_user.id and not deck.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return _card_to_response(card)


@router.put("/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: UUID,
    card_data: CardUpdate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Обновить карточку"""
    card_repo = CardRepository(db)
    use_case = GetCardUseCase(card_repo)
    
    card = await use_case.execute(card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Проверяем права доступа
    deck_repo = DeckRepository(db)
    deck = await deck_repo.get_by_id(card.deck_id)
    if deck.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    update_use_case = UpdateCardUseCase(card_repo)
    updated_card = await update_use_case.execute(
        card_id=card_id,
        front=card_data.front,
        back=card_data.back,
    )
    
    return _card_to_response(updated_card)


@router.delete("/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: UUID,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Удалить карточку"""
    card_repo = CardRepository(db)
    use_case = GetCardUseCase(card_repo)
    
    card = await use_case.execute(card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    # Проверяем права доступа
    deck_repo = DeckRepository(db)
    deck = await deck_repo.get_by_id(card.deck_id)
    if deck.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    delete_use_case = DeleteCardUseCase(card_repo)
    await delete_use_case.execute(card_id)


@router.post("/{card_id}/review", response_model=CardResponse)
async def review_card(
    card_id: UUID,
    review_data: ReviewCardRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Отметить карточку как просмотренную"""
    card_repo = CardRepository(db)
    
    # Проверяем права доступа
    card = await card_repo.get_by_id(card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )
    
    deck_repo = DeckRepository(db)
    deck = await deck_repo.get_by_id(card.deck_id)
    if deck.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    fsrs_service = FSRSService()
    use_case = ReviewCardUseCase(card_repo, fsrs_service)
    
    reviewed_card = await use_case.execute(card_id, review_data.quality)
    
    return _card_to_response(reviewed_card)


def _card_to_response(card) -> CardResponse:
    """Преобразовать карточку в response схему"""
    return CardResponse(
        id=card.id,
        deck_id=card.deck_id,
        front=card.front,
        back=card.back,
        audio_url=card.audio_url,
        fsrs_state=FSRSStateResponse(
            stability=card.fsrs_state.stability,
            difficulty=card.fsrs_state.difficulty,
            ease_factor=card.fsrs_state.ease_factor,
            interval=card.fsrs_state.interval,
            review_count=card.fsrs_state.review_count,
            last_review=card.fsrs_state.last_review,
            due_date=card.fsrs_state.due_date,
        ),
        created_at=card.created_at,
        updated_at=card.updated_at,
    )
