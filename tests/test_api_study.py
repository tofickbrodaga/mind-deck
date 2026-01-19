import pytest
from domain.entities.user import User
from domain.entities.deck import Deck
from domain.entities.card import Card
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.deck_repository import DeckRepository
from infrastructure.repositories.card_repository import CardRepository
from infrastructure.security import create_access_token
from domain.entities.study_session import StudyMode


@pytest.mark.asyncio
async def test_start_and_finish_study_session(client, db_session):
    # prepare user and deck
    user = User.create(email="s1@example.com", username="s1", hashed_password="h")
    user_repo = UserRepository(db_session)
    created_user = await user_repo.create(user)

    deck = Deck.create(created_user.id, "Study Deck")
    deck_repo = DeckRepository(db_session)
    created_deck = await deck_repo.create(deck)

    # add one card
    card = Card.create(created_deck.id, "Q", "A")
    card_repo = CardRepository(db_session)
    await card_repo.create(card)

    token = create_access_token({"sub": str(created_user.id), "email": created_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # Start session
    resp = await client.post("/api/v1/study/session", json={"deck_id": str(created_deck.id), "mode": StudyMode.FLASHCARDS.value}, headers=headers)
    assert resp.status_code == 201
    body = resp.json()
    session_id = body["id"]
    assert body["deck_id"] == str(created_deck.id)

    # Finish session
    resp2 = await client.post(f"/api/v1/study/session/{session_id}/finish", headers=headers)
    assert resp2.status_code == 200
    finished = resp2.json()
    assert finished["finished_at"] is not None
