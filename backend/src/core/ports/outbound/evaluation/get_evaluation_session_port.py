from abc import ABC, abstractmethod
from ....domain.session.evaluation_session import EvaluationSession

class GetEvaluationSessionPort(ABC):

    @abstractmethod
    def get_evaluation_session(self, session_id: str) -> EvaluationSession: ...