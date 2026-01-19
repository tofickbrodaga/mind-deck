import pytest
from domain.entities.user import User
from domain.entities.deck import Deck
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.deck_repository import DeckRepository
from infrastructure.security import create_access_token
from infrastructure.services.import_service import ImportService


@pytest.mark.asyncio
async def test_import_word_and_excel_and_image(client, db_session, monkeypatch):
    # create user and deck
    user = User.create(email="i1@example.com", username="i1", hashed_password="h")
    user_repo = UserRepository(db_session)
    created_user = await user_repo.create(user)
    deck = Deck.create(created_user.id, "Import Deck")
    deck_repo = DeckRepository(db_session)
    created_deck = await deck_repo.create(deck)

    token = create_access_token({"sub": str(created_user.id), "email": created_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # patch import service methods to return sample data
    async def fake_word(self, file):
        return [("W1", "A1"), ("W2", "A2")]

    async def fake_excel(self, file):
        return [("E1", "B1")]

    async def fake_image(self, file):
        return [("ImgQ", "ImgA")]

    monkeypatch.setattr(ImportService, "import_from_word", fake_word)
    monkeypatch.setattr(ImportService, "import_from_excel", fake_excel)
    monkeypatch.setattr(ImportService, "import_from_image", fake_image)

    # word upload
    files = {"file": ("test.docx", b"dummy", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
    resp = await client.post(f"/api/v1/import/word/{created_deck.id}", files=files, headers=headers)
    assert resp.status_code == 201
    assert resp.json()["imported"] == 2

    # excel upload
    files2 = {"file": ("test.xlsx", b"dummy", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    resp2 = await client.post(f"/api/v1/import/excel/{created_deck.id}", files=files2, headers=headers)
    assert resp2.status_code == 201

    # image upload
    files3 = {"file": ("img.png", b"dummy", "image/png")}
    resp3 = await client.post(f"/api/v1/import/image/{created_deck.id}", files=files3, headers=headers)
    assert resp3.status_code == 201
