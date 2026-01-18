from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.database.database import get_db
from infrastructure.repositories.card_repository import CardRepository
from infrastructure.repositories.deck_repository import DeckRepository
from infrastructure.repositories.study_session_repository import StudySessionRepository
from presentation.schemas.study_schemas import (
    StudySessionCreate,
    StudySessionResponse,
    StudyFlashcardsResponse,
    StudyMultipleChoiceResponse,
    StudyWriteRequest,
    StudyWriteResponse,
    StudyMatchResponse,
)
from presentation.schemas.card_schemas import CardResponse, FSRSStateResponse
from presentation.api.routers.users import get_current_user_dependency
from domain.entities.user import User
from domain.entities.study_session import StudyMode
from application.use_cases.study_use_cases import (
    StartStudySessionUseCase,
    FinishStudySessionUseCase,
    StudyFlashcardsUseCase,
    StudyMultipleChoiceUseCase,
    StudyWriteUseCase,
    StudyMatchUseCase,
)
from application.use_cases.card_use_cases import ReviewCardUseCase
from application.services.fsrs_service import FSRSService

router = APIRouter()


@router.post("/session", response_model=StudySessionResponse, status_code=status.HTTP_201_CREATED)
async def start_study_session(
    session_data: StudySessionCreate,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Начать сессию обучения"""
    session_repo = StudySessionRepository(db)
    use_case = StartStudySessionUseCase(session_repo)
    
    session = await use_case.execute(
        user_id=current_user.id,
        deck_id=session_data.deck_id,
        mode=session_data.mode,
    )
    
    return StudySessionResponse(
        id=session.id,
        user_id=session.user_id,
        deck_id=session.deck_id,
        mode=session.mode.value,
        started_at=session.started_at,
        finished_at=session.finished_at,
        cards_studied=session.cards_studied,
        cards_correct=session.cards_correct,
        cards_incorrect=session.cards_incorrect,
    )


@router.post("/session/{session_id}/finish", response_model=StudySessionResponse)
async def finish_study_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Завершить сессию обучения"""
    session_repo = StudySessionRepository(db)
    use_case = FinishStudySessionUseCase(session_repo)
    
    session = await use_case.execute(session_id)
    
    return StudySessionResponse(
        id=session.id,
        user_id=session.user_id,
        deck_id=session.deck_id,
        mode=session.mode.value,
        started_at=session.started_at,
        finished_at=session.finished_at,
        cards_studied=session.cards_studied,
        cards_correct=session.cards_correct,
        cards_incorrect=session.cards_incorrect,
    )


@router.get("/flashcards/{deck_id}", response_model=StudyFlashcardsResponse)
async def study_flashcards(
    deck_id: UUID,
    limit: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Получить карточки для режима флэшкарт"""
    deck_repo = DeckRepository(db)
    card_repo = CardRepository(db)
    
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
    
    review_card_use_case = ReviewCardUseCase(card_repo, FSRSService())
    use_case = StudyFlashcardsUseCase(card_repo, deck_repo, review_card_use_case)
    
    cards = await use_case.execute(deck_id, limit)
    
    return StudyFlashcardsResponse(
        cards=[
            CardResponse(
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
            for card in cards
        ]
    )


@router.get("/multiple-choice/{deck_id}/{card_id}", response_model=StudyMultipleChoiceResponse)
async def study_multiple_choice(
    deck_id: UUID,
    card_id: UUID,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Получить варианты ответов для режима множественного выбора"""
    deck_repo = DeckRepository(db)
    card_repo = CardRepository(db)
    
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
    
    review_card_use_case = ReviewCardUseCase(card_repo, FSRSService())
    use_case = StudyMultipleChoiceUseCase(card_repo, deck_repo, review_card_use_case)
    
    card, options = await use_case.execute(deck_id, card_id)

    correct_index = options.index(card.back)
    
    return StudyMultipleChoiceResponse(
        card=CardResponse(
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
        ),
        options=options,
        correct_index=correct_index,
    )


@router.post("/write/check", response_model=StudyWriteResponse)
async def study_write_check(
    write_data: StudyWriteRequest,
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Проверить ответ в режиме письма"""
    card_repo = CardRepository(db)
    
    card = await card_repo.get_by_id(write_data.card_id)
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
    
    review_card_use_case = ReviewCardUseCase(card_repo, FSRSService())
    use_case = StudyWriteUseCase(card_repo, review_card_use_case)
    
    is_correct, quality = await use_case.check_answer(write_data.card_id, write_data.answer)

    await review_card_use_case.execute(write_data.card_id, quality)
    
    return StudyWriteResponse(
        is_correct=is_correct,
        quality=quality,
        correct_answer=card.back,
    )


@router.get("/match/{deck_id}", response_model=StudyMatchResponse)
async def study_match(
    deck_id: UUID,
    limit: int = Query(default=10, ge=1, le=20),
    current_user: User = Depends(get_current_user_dependency),
    db: AsyncSession = Depends(get_db),
):
    """Получить пары для режима подбора"""
    deck_repo = DeckRepository(db)
    card_repo = CardRepository(db)
    
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
    
    use_case = StudyMatchUseCase(card_repo, deck_repo)
    pairs = await use_case.execute(deck_id, limit)
    
    terms = [pair[0] for pair in pairs]
    definitions = [pair[1] for pair in pairs]

    import random
    random.shuffle(terms)
    random.shuffle(definitions)
    
    return StudyMatchResponse(
        terms=terms,
        definitions=definitions,
        pairs=pairs,
    )
