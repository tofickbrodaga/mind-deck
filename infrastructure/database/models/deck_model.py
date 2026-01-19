from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from infrastructure.database.types import GUID
from sqlalchemy.orm import relationship

from infrastructure.database.base import Base


class DeckModel(Base):
    __tablename__ = "decks"

    id = Column(GUID(), primary_key=True, default=uuid4)
    user_id = Column(GUID(), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    cards = relationship("CardModel", back_populates="deck", cascade="all, delete-orphan")
