from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4


@dataclass
class User:
    id: UUID
    email: str
    username: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime
    is_active: bool = True

    @classmethod
    def create(cls, email: str, username: str, hashed_password: str) -> "User":
        now = datetime.utcnow()
        return cls(
            id=uuid4(),
            email=email,
            username=username,
            hashed_password=hashed_password,
            created_at=now,
            updated_at=now,
            is_active=True,
        )

    def update(self) -> None:
        self.updated_at = datetime.utcnow()
