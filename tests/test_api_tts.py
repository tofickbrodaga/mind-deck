import pytest
from domain.entities.user import User
from domain.entities.deck import Deck
from domain.entities.card import Card
from infrastructure.repositories.user_repository import UserRepository
from infrastructure.repositories.deck_repository import DeckRepository
from infrastructure.repositories.card_repository import CardRepository
from infrastructure.security import create_access_token
from infrastructure.services.tts_service import TTSService


@pytest.mark.asyncio
async def test_generate_audio_and_get_languages(client, db_session, monkeypatch):
    # create user, deck and card
    user = User.create(email="t1@example.com", username="t1", hashed_password="h")
    user_repo = UserRepository(db_session)
    created_user = await user_repo.create(user)
    deck = Deck.create(created_user.id, "TTS Deck")
    deck_repo = DeckRepository(db_session)
    created_deck = await deck_repo.create(deck)

    card = Card.create(created_deck.id, "Hello", "World")
    card_repo = CardRepository(db_session)
    created_card = await card_repo.create(card)

    token = create_access_token({"sub": str(created_user.id), "email": created_user.email})
    headers = {"Authorization": f"Bearer {token}"}

    # mock TTSService.generate_audio and get_supported_languages
    async def fake_generate(self, text, language, card_id):
        return f"https://audio.example/{card_id}.mp3"

    def fake_languages(self):
        return ["ru", "en"]

    monkeypatch.setattr(TTSService, "generate_audio", fake_generate)
    monkeypatch.setattr(TTSService, "get_supported_languages", fake_languages)

    # call generate endpoint
    resp = await client.post(f"/api/v1/tts/card/{created_card.id}/generate", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["audio_url"].startswith("https://audio.example/")

    # get languages
    resp2 = await client.get("/api/v1/tts/languages")
    assert resp2.status_code == 200
    langs = resp2.json()
    assert "ru" in langs["languages"]
