from abc import ABC, abstractmethod

from core.domain.session.evaluation_session import EvaluationSession


class SaveSessionPort(ABC):
    @abstractmethod
    def save_session(self, session: EvaluationSession) -> None: ...