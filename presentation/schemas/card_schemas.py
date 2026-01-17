from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class CardCreate(BaseModel):
    front: str
    back: str


class CardUpdate(BaseModel):
    front: Optional[str] = None
    back: Optional[str] = None


class FSRSStateResponse(BaseModel):
    stability: float
    difficulty: float
    ease_factor: float
    interval: int
    review_count: int
    last_review: Optional[datetime]
    due_date: Optional[datetime]


class CardResponse(BaseModel):
    id: UUID
    deck_id: UUID
    front: str
    back: str
    audio_url: Optional[str]
    fsrs_state: FSRSStateResponse
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReviewCardRequest(BaseModel):
    quality: int  # 0-5
