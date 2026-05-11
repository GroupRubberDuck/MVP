from abc import ABC, abstractmethod

class CloseEvaluationSessionPort(ABC):

    @abstractmethod
    def close_evaluation_session(self, session_id: str) -> None: ...