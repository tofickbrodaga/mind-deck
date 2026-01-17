from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.database import get_db
from infrastructure.repositories.deck_repository import DeckRepository
from infrastructure.repositories.card_repository import CardRepository
from infrastructure.repositories.user_repository import UserRepository
from presentation.api.routers.users import get_current_user_dependency
from domain.entities.user import User
from domain.entities.card import Card
from infrastructure.services.import_service import ImportService

router = APIRouter()


@router.post("/word/{deck_id}", status_code=status.HTTP_201_CREATED)
async def import_from_word(
    deck_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Импортировать карточки из Word документа"""
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
    
    if not file.filename.endswith(('.doc', '.docx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .doc and .docx files are supported"
        )
    
    import_service = ImportService()
    cards_data = await import_service.import_from_word(file)
    
    card_repo = CardRepository(db)
    cards = [Card.create(deck_id, front, back) for front, back in cards_data]
    created_cards = await card_repo.bulk_create(cards)
    
    return {
        "imported": len(created_cards),
        "cards": [
            {
                "id": str(card.id),
                "front": card.front,
                "back": card.back,
            }
            for card in created_cards
        ]
    }


@router.post("/excel/{deck_id}", status_code=status.HTTP_201_CREATED)
async def import_from_excel(
    deck_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Импортировать карточки из Excel файла"""
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
    
    if not file.filename.endswith(('.xls', '.xlsx')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .xls and .xlsx files are supported"
        )
    
    import_service = ImportService()
    cards_data = await import_service.import_from_excel(file)
    
    card_repo = CardRepository(db)
    cards = [Card.create(deck_id, front, back) for front, back in cards_data]
    created_cards = await card_repo.bulk_create(cards)
    
    return {
        "imported": len(created_cards),
        "cards": [
            {
                "id": str(card.id),
                "front": card.front,
                "back": card.back,
            }
            for card in created_cards
        ]
    }


@router.post("/image/{deck_id}", status_code=status.HTTP_201_CREATED)
async def import_from_image(
    deck_id: UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Импортировать карточки из изображения с текстом (OCR)"""
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
    
    if not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are supported"
        )
    
    import_service = ImportService()
    cards_data = await import_service.import_from_image(file)
    
    if not cards_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract cards from image"
        )
    
    card_repo = CardRepository(db)
    cards = [Card.create(deck_id, front, back) for front, back in cards_data]
    created_cards = await card_repo.bulk_create(cards)
    
    return {
        "imported": len(created_cards),
        "cards": [
            {
                "id": str(card.id),
                "front": card.front,
                "back": card.back,
            }
            for card in created_cards
        ]
    }
