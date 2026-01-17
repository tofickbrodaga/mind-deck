import pytest
from uuid import uuid4
from domain.entities.user import User
from domain.entities.deck import Deck
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.deck_repository import DeckRepository
from application.use_cases.deck_use_cases import CreateDeckUseCase, GetDeckUseCase


@pytest.mark.asyncio
async def test_create_deck(db_session):
    """Тест создания набора карточек"""
    # Создаем пользователя
    user = User.create(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
    )
    user_repo = UserRepository(db_session)
    created_user = await user_repo.create(user)
    
    # Создаем набор
    deck_repo = DeckRepository(db_session)
    use_case = CreateDeckUseCase(deck_repo, user_repo)
    
    deck = await use_case.execute(
        user_id=created_user.id,
        title="Test Deck",
        description="Test Description",
    )
    
    assert deck.id is not None
    assert deck.title == "Test Deck"
    assert deck.description == "Test Description"
    assert deck.user_id == created_user.id


@pytest.mark.asyncio
async def test_get_deck(db_session):
    """Тест получения набора карточек"""
    # Создаем пользователя
    user = User.create(
        email="test@example.com",
        username="testuser",
        hashed_password="hashed_password",
    )
    user_repo = UserRepository(db_session)
    created_user = await user_repo.create(user)
    
    # Создаем набор
    deck = Deck.create(created_user.id, "Test Deck")
    deck_repo = DeckRepository(db_session)
    created_deck = await deck_repo.create(deck)
    
    # Получаем набор
    use_case = GetDeckUseCase(deck_repo)
    retrieved_deck = await use_case.execute(created_deck.id)
    
    assert retrieved_deck is not None
    assert retrieved_deck.id == created_deck.id
    assert retrieved_deck.title == "Test Deck"
