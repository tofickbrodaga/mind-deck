import pytest
from domain.entities.user import User
from domain.entities.deck import Deck
from domain.entities.card import Card
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.deck_repository import DeckRepository
from infrastructure.repositories.card_repository import CardRepository
from application.use_cases.card_use_cases import CreateCardUseCase, GetCardUseCase


@pytest.mark.asyncio
async def test_create_card(db_session):
    """Тест создания карточки"""
    # Создаем пользователя и набор
    user = User.create(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
    )
    user_repo = UserRepository(db_session)
    created_user = await user_repo.create(user)
    
    deck = Deck.create(created_user.id, "Test Deck")
    deck_repo = DeckRepository(db_session)
    created_deck = await deck_repo.create(deck)
    
    # Создаем карточку
    card_repo = CardRepository(db_session)
    use_case = CreateCardUseCase(card_repo, deck_repo)
    
    card = await use_case.execute(
        deck_id=created_deck.id,
        front="Term",
        back="Definition",
    )
    
    assert card.id is not None
    assert card.front == "Term"
    assert card.back == "Definition"
    assert card.deck_id == created_deck.id
    assert card.fsrs_state.review_count == 0


@pytest.mark.asyncio
async def test_get_card(db_session):
    """Тест получения карточки"""
    # Создаем пользователя и набор
    user = User.create(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
    )
    user_repo = UserRepository(db_session)
    created_user = await user_repo.create(user)
    
    deck = Deck.create(created_user.id, "Test Deck")
    deck_repo = DeckRepository(db_session)
    created_deck = await deck_repo.create(deck)
    
    # Создаем карточку
    card = Card.create(created_deck.id, "Term", "Definition")
    card_repo = CardRepository(db_session)
    created_card = await card_repo.create(card)
    
    # Получаем карточку
    use_case = GetCardUseCase(card_repo)
    retrieved_card = await use_case.execute(created_card.id)
    
    assert retrieved_card is not None
    assert retrieved_card.id == created_card.id
    assert retrieved_card.front == "Term"
    assert retrieved_card.back == "Definition"
