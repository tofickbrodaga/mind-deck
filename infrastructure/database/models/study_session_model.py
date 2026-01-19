from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, ForeignKey, Integer
from infrastructure.database.types import GUID

from infrastructure.database.base import Base


class StudySessionModel(Base):
    __tablename__ = "study_sessions"

    id = Column(GUID(), primary_key=True, default=uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    deck_id = Column(GUID(), ForeignKey("decks.id"), nullable=False, index=True)
    mode = Column(String(50), nullable=False)  # StudyMode enum as string
    started_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    finished_at = Column(DateTime, nullable=True)
    cards_studied = Column(Integer, default=0, nullable=False)
    cards_correct = Column(Integer, default=0, nullable=False)
    cards_incorrect = Column(Integer, default=0, nullable=False)
