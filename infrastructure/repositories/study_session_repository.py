from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from domain.entities.study_session import StudySession, StudyMode
from domain.repositories.study_session_repository import IStudySessionRepository
from infrastructure.database.models.study_session_model import StudySessionModel


class StudySessionRepository(IStudySessionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    def _to_entity(self, model: StudySessionModel) -> StudySession:
        return StudySession(
            id=model.id,
            user_id=model.user_id,
            deck_id=model.deck_id,
            mode=StudyMode(model.mode),
            started_at=model.started_at,
            finished_at=model.finished_at,
            cards_studied=model.cards_studied,
            cards_correct=model.cards_correct,
            cards_incorrect=model.cards_incorrect,
        )

    def _to_model(self, entity: StudySession) -> StudySessionModel:
        return StudySessionModel(
            id=entity.id,
            user_id=entity.user_id,
            deck_id=entity.deck_id,
            mode=entity.mode.value,
            started_at=entity.started_at,
            finished_at=entity.finished_at,
            cards_studied=entity.cards_studied,
            cards_correct=entity.cards_correct,
            cards_incorrect=entity.cards_incorrect,
        )

    async def create(self, session: StudySession) -> StudySession:
        model = self._to_model(session)
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)

    async def get_by_id(self, session_id: UUID) -> Optional[StudySession]:
        result = await self._session.execute(
            select(StudySessionModel).where(StudySessionModel.id == session_id)
        )
        model = result.scalar_one_or_none()
        return self._to_entity(model) if model else None

    async def get_by_user_id(self, user_id: UUID, limit: int = 20) -> List[StudySession]:
        result = await self._session.execute(
            select(StudySessionModel)
            .where(StudySessionModel.user_id == user_id)
            .order_by(desc(StudySessionModel.started_at))
            .limit(limit)
        )
        models = result.scalars().all()
        return [self._to_entity(model) for model in models]

    async def update(self, session: StudySession) -> StudySession:
        result = await self._session.execute(
            select(StudySessionModel).where(StudySessionModel.id == session.id)
        )
        model = result.scalar_one()
        model.finished_at = session.finished_at
        model.cards_studied = session.cards_studied
        model.cards_correct = session.cards_correct
        model.cards_incorrect = session.cards_incorrect
        await self._session.commit()
        await self._session.refresh(model)
        return self._to_entity(model)
