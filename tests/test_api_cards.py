import pytest

from domain.entities.user import User
from domain.entities.deck import Deck
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.deck_repository import DeckRepository
from infrastructure.repositories.card_repository import CardRepository
from infrastructure.security import create_access_token


@pytest.mark.asyncio
async def test_create_and_get_card_via_api(client, db_session):
    user = User.create(
        email="carduser@example.com",
        username="carduser",
        hashed_password="hashed",
    )
    user_repo = UserRepository(db_session)
    created_user = await user_repo.create(user)

    deck = Deck.create(created_user.id, "Deck for Cards")
    deck_repo = DeckRepository(db_session)
    created_deck = await deck_repo.create(deck)

    token = create_access_token({"sub": str(created_user.id), "email": created_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        f"/api/v1/cards/deck/{created_deck.id}",
        json={"front": "Term API", "back": "Definition API"},
        headers=headers,
    )
    assert resp.status_code == 201
    card_body = resp.json()
    assert card_body["front"] == "Term API"
    assert card_body["deck_id"] == str(created_deck.id)

    resp2 = await client.get(f"/api/v1/cards/deck/{created_deck.id}", headers=headers)
    assert resp2.status_code == 200
    cards = resp2.json()
    assert any(c["front"] == "Term API" for c in cards)
