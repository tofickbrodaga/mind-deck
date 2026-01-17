from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List, Optional
from uuid import UUID, uuid4


class StudyMode(str, Enum):
    FLASHCARDS = "flashcards"  # Карточки
    MULTIPLE_CHOICE = "multiple_choice"  # Заучивание (выбор из 4)
    WRITE = "write"  # Письмо
    MATCH = "match"  # Подбор


@dataclass
class StudySession:
    id: UUID
    user_id: UUID
    deck_id: UUID
    mode: StudyMode
    started_at: datetime
    finished_at: Optional[datetime]
    cards_studied: int
    cards_correct: int
    cards_incorrect: int

    @classmethod
    def create(cls, user_id: UUID, deck_id: UUID, mode: StudyMode) -> "StudySession":
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            user_id=user_id,
            deck_id=deck_id,
            mode=mode,
            started_at=now,
            finished_at=None,
            cards_studied=0,
            cards_correct=0,
            cards_incorrect=0,
        )

    def finish(self) -> None:
        self.finished_at = datetime.utcnow()

    def record_answer(self, is_correct: bool) -> None:
        self.cards_studied += 1
        if is_correct:
            self.cards_correct += 1
        else:
            self.cards_incorrect += 1
