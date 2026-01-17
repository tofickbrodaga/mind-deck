import random
from typing import List, Tuple
from uuid import UUID

from domain.entities.card import Card
from domain.entities.study_session import StudySession, StudyMode
from domain.repositories.card_repository import ICardRepository
from domain.repositories.deck_repository import IDeckRepository
from domain.repositories.study_session_repository import IStudySessionRepository
from application.use_cases.card_use_cases import ReviewCardUseCase


class StartStudySessionUseCase:
    def __init__(self, session_repository: IStudySessionRepository):
        self._session_repository = session_repository

    async def execute(self, user_id: UUID, deck_id: UUID, mode: StudyMode) -> StudySession:
        session = StudySession.create(user_id, deck_id, mode)
        return await self._session_repository.create(session)


class FinishStudySessionUseCase:
    def __init__(self, session_repository: IStudySessionRepository):
        self._session_repository = session_repository

    async def execute(self, session_id: UUID) -> StudySession:
        session = await self._session_repository.get_by_id(session_id)
        if not session:
            raise ValueError(f"Session with id {session_id} not found")
        
        session.finish()
        return await self._session_repository.update(session)


class StudyFlashcardsUseCase:
    def __init__(
        self,
        card_repository: ICardRepository,
        deck_repository: IDeckRepository,
        review_card_use_case: ReviewCardUseCase,
    ):
        self._card_repository = card_repository
        self._deck_repository = deck_repository
        self._review_card_use_case = review_card_use_case

    async def execute(self, deck_id: UUID, limit: int = 20) -> List[Card]:
        # Проверяем существование набора
        deck = await self._deck_repository.get_by_id(deck_id)
        if not deck:
            raise ValueError(f"Deck with id {deck_id} not found")
        
        # Получаем карточки для повторения
        cards = await self._card_repository.get_due_cards(deck_id, limit)
        if not cards:
            # Если нет карточек для повторения, возвращаем все карточки
            cards = await self._card_repository.get_by_deck_id(deck_id)
        
        return cards[:limit]


class StudyMultipleChoiceUseCase:
    def __init__(
        self,
        card_repository: ICardRepository,
        deck_repository: IDeckRepository,
        review_card_use_case: ReviewCardUseCase,
    ):
        self._card_repository = card_repository
        self._deck_repository = deck_repository
        self._review_card_use_case = review_card_use_case

    async def execute(self, deck_id: UUID, card_id: UUID) -> Tuple[Card, List[str]]:
        """
        Получить карточку и 4 варианта ответов для режима множественного выбора
        
        Returns:
            Tuple[Card, List[str]]: Карточка и список вариантов ответов
        """
        # Получаем текущую карточку
        card = await self._card_repository.get_by_id(card_id)
        if not card:
            raise ValueError(f"Card with id {card_id} not found")
        
        # Получаем все карточки из набора
        all_cards = await self._card_repository.get_by_deck_id(deck_id)
        
        # Формируем варианты ответов (правильный + 3 случайных)
        other_cards = [c for c in all_cards if c.id != card_id]
        random.shuffle(other_cards)
        
        options = [card.back]  # Правильный ответ
        options.extend([c.back for c in other_cards[:3]])  # 3 случайных ответа
        
        random.shuffle(options)  # Перемешиваем варианты
        
        return card, options


class StudyWriteUseCase:
    def __init__(
        self,
        card_repository: ICardRepository,
        review_card_use_case: ReviewCardUseCase,
    ):
        self._card_repository = card_repository
        self._review_card_use_case = review_card_use_case

    async def check_answer(self, card_id: UUID, user_answer: str) -> Tuple[bool, int]:
        """
        Проверить ответ пользователя в режиме письма
        
        Returns:
            Tuple[bool, int]: (правильность ответа, оценка качества 0-5)
        """
        card = await self._card_repository.get_by_id(card_id)
        if not card:
            raise ValueError(f"Card with id {card_id} not found")
        
        # Простая проверка (можно улучшить с помощью fuzzy matching)
        user_answer_lower = user_answer.strip().lower()
        correct_answer_lower = card.back.strip().lower()
        
        is_correct = user_answer_lower == correct_answer_lower
        
        # Оцениваем качество ответа
        if is_correct:
            quality = 4  # Отлично
        else:
            # Проверяем частичное совпадение
            if correct_answer_lower in user_answer_lower or user_answer_lower in correct_answer_lower:
                quality = 2  # Частично правильно
            else:
                quality = 0  # Неправильно
        
        return is_correct, quality


class StudyMatchUseCase:
    def __init__(
        self,
        card_repository: ICardRepository,
        deck_repository: IDeckRepository,
    ):
        self._card_repository = card_repository
        self._deck_repository = deck_repository

    async def execute(self, deck_id: UUID, limit: int = 10) -> List[Tuple[str, str]]:
        """
        Получить пары термин-определение для режима подбора
        
        Returns:
            List[Tuple[str, str]]: Список пар (термин, определение)
        """
        deck = await self._deck_repository.get_by_id(deck_id)
        if not deck:
            raise ValueError(f"Deck with id {deck_id} not found")
        
        cards = await self._card_repository.get_by_deck_id(deck_id)
        random.shuffle(cards)
        
        pairs = [(card.front, card.back) for card in cards[:limit]]
        return pairs
