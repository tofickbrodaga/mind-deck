import pytest

from domain.entities.user import User
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.deck_repository import DeckRepository
from infrastructure.security import create_access_token


@pytest.mark.asyncio
async def test_create_and_list_deck_via_api(client, db_session):
    user = User.create(
        email="apiuser@example.com",
        username="apiuser",
        hashed_password="hashed",
    )
    user_repo = UserRepository(db_session)
    created_user = await user_repo.create(user)

    token = create_access_token({"sub": str(created_user.id), "email": created_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    resp = await client.post(
        "/api/v1/decks",
        json={"title": "API Deck", "description": "Desc"},
        headers=headers,
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "API Deck"
    assert body["user_id"] == str(created_user.id)

    resp2 = await client.get("/api/v1/decks", headers=headers)
    assert resp2.status_code == 200
    data = resp2.json()
    assert any(d["title"] == "API Deck" for d in data)
