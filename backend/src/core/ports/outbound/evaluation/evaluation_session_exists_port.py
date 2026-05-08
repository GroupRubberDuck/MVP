from abc import ABC, abstractmethod

class EvaluationSessionExistsPort(ABC):

    @abstractmethod
    def has_active_session(self) -> bool: ...