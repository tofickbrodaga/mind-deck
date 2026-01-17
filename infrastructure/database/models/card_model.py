from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Column, String, DateTime, ForeignKey, Float, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import relationship

from infrastructure.database.base import Base


class CardModel(Base):
    __tablename__ = "cards"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    deck_id = Column(PG_UUID(as_uuid=True), ForeignKey("decks.id"), nullable=False, index=True)
    front = Column(Text, nullable=False)  # Термин
    back = Column(Text, nullable=False)   # Определение
    audio_url = Column(String(500), nullable=True)
    
    # FSRS algorithm fields
    stability = Column(Float, default=0.0, nullable=False)
    difficulty = Column(Float, default=0.0, nullable=False)
    ease_factor = Column(Float, default=2.5, nullable=False)
    interval = Column(Integer, default=0, nullable=False)  # дни
    review_count = Column(Integer, default=0, nullable=False)
    last_review = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    deck = relationship("DeckModel", back_populates="cards")
