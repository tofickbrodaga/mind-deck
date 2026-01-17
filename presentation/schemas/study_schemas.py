from pydantic import BaseModel
from typing import List, Optional, Tuple
from uuid import UUID
from datetime import datetime
from domain.entities.study_session import StudyMode

from presentation.schemas.card_schemas import CardResponse


class StudySessionCreate(BaseModel):
    deck_id: UUID
    mode: StudyMode


class StudySessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    deck_id: UUID
    mode: str
    started_at: datetime
    finished_at: Optional[datetime]
    cards_studied: int
    cards_correct: int
    cards_incorrect: int

    class Config:
        from_attributes = True


class StudyFlashcardsResponse(BaseModel):
    cards: List[CardResponse]


class StudyMultipleChoiceResponse(BaseModel):
    card: CardResponse
    options: List[str]
    correct_index: int


class StudyWriteRequest(BaseModel):
    card_id: UUID
    answer: str


class StudyWriteResponse(BaseModel):
    is_correct: bool
    quality: int
    correct_answer: str


class StudyMatchResponse(BaseModel):
    terms: List[str]
    definitions: List[str]
    pairs: List[Tuple[str, str]]
