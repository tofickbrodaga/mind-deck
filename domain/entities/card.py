from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class FSRSState:
    """FSRS алгоритм состояния карточки"""
    stability: float = 0.0
    difficulty: float = 0.0
    last_review: Optional[datetime] = None
    review_count: int = 0
    ease_factor: float = 2.5
    interval: int = 0  # дни до следующего повторения
    due_date: Optional[datetime] = None


@dataclass
class Card:
    id: UUID
    deck_id: UUID
    front: str  # Термин
    back: str   # Определение
    created_at: datetime
    updated_at: datetime
    fsrs_state: FSRSState = field(default_factory=FSRSState)
    audio_url: Optional[str] = None

    @classmethod
    def create(cls, deck_id: UUID, front: str, back: str) -> "Card":
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            deck_id=deck_id,
            front=front,
            back=back,
            created_at=now,
            updated_at=now,
            fsrs_state=FSRSState(),
        )

    def update(self, front: Optional[str] = None, back: Optional[str] = None) -> None:
        if front is not None:
            self.front = front
        if back is not None:
            self.back = back
        self.updated_at = datetime.utcnow()

    def mark_reviewed(self, quality: int) -> None:
        """Отметить карточку как просмотренную с оценкой качества (0-5)
        
        Note: Этот метод должен вызываться через use case, который использует FSRSService
        """
        self.updated_at = datetime.utcnow()

    def is_due(self) -> bool:
        """Проверить, нужно ли повторять карточку"""
        if self.fsrs_state.due_date is None:
            return True
        return datetime.utcnow() >= self.fsrs_state.due_date
