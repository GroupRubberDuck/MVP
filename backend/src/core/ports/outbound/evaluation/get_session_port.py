from abc import ABC, abstractmethod

from core.domain.session.evaluation_session import EvaluationSession


class GetSessionPort(ABC):
    @abstractmethod
    def get_session(self, session_id: str) -> EvaluationSession: ...