from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class Deck:
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    is_public: bool = False

    @classmethod
    def create(cls, user_id: UUID, title: str, description: Optional[str] = None) -> "Deck":
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            user_id=user_id,
            title=title,
            description=description,
            created_at=now,
            updated_at=now,
            is_public=False,
        )

    def update(self, title: Optional[str] = None, description: Optional[str] = None) -> None:
        if title is not None:
            self.title = title
        if description is not None:
            self.description = description
        self.updated_at = datetime.utcnow()
