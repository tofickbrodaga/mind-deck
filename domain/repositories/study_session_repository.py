from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from domain.entities.study_session import StudySession


class IStudySessionRepository(ABC):
    @abstractmethod
    async def create(self, session: StudySession) -> StudySession:
        pass

    @abstractmethod
    async def get_by_id(self, session_id: UUID) -> Optional[StudySession]:
        pass

    @abstractmethod
    async def get_by_user_id(self, user_id: UUID, limit: int = 20) -> List[StudySession]:
        pass

    @abstractmethod
    async def update(self, session: StudySession) -> StudySession:
        pass
