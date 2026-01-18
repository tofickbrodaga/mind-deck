from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.database import get_db
from infrastructure.repositories.card_repository import CardRepository
from presentation.api.routers.users import get_current_user_dependency
from domain.entities.user import User
from infrastructure.services.tts_service import TTSService

router = APIRouter()


@router.post("/card/{card_id}/generate")
async def generate_card_audio(
    card_id: UUID,
    language: str = Query(default="ru", description="Language code (e.g., 'ru', 'en', 'es')"),
    side: str = Query(default="front", description="Which side to generate audio for: 'front' or 'back'"),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Сгенерировать аудио для карточки с помощью Text-to-Speech"""
    card_repo = CardRepository(db)
    card = await card_repo.get_by_id(card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Card not found"
        )

    from infrastructure.repositories.deck_repository import DeckRepository
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

    text = card.front if side == "front" else card.back
    
    tts_service = TTSService()
    audio_url = await tts_service.generate_audio(text, language, card_id)

    if side == "front":
        card.audio_url = audio_url
    else:
        card.audio_url = audio_url
    
    updated_card = await card_repo.update(card)
    
    return {
        "card_id": str(card_id),
        "audio_url": audio_url,
        "language": language,
        "side": side,
    }


@router.get("/languages")
async def get_supported_languages():
    """Получить список поддерживаемых языков для TTS"""
    tts_service = TTSService()
    languages = tts_service.get_supported_languages()
    
    return {
        "languages": languages,
        "total": len(languages),
    }
