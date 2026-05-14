from abc import ABC, abstractmethod

class EvaluationSessionExistPort(ABC):

    @abstractmethod
    def has_active_session(self) -> bool: ...