from abc import ABC, abstractmethod
from ....domain.session.evaluation_session import EvaluationSession

class SaveEvaluationSessionPort(ABC):

    @abstractmethod
    def save_evaluation_session(self, session: EvaluationSession) -> None: ...