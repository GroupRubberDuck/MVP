from abc import ABC, abstractmethod
from core.domain.session.evaluation_session import EvaluationSession


class GetActiveSessionPort(ABC):
    @abstractmethod
    def get_active_session(self) -> EvaluationSession | None:
        pass
