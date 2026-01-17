from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class DeckCreate(BaseModel):
    title: str
    description: Optional[str] = None


class DeckUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class DeckResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    is_public: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
