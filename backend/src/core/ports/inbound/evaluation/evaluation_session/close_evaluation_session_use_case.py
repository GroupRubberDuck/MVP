from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class CloseEvaluationSessionCommand:
    session_id: str



class CloseEvaluationSessionUseCase(ABC):

    @abstractmethod
    def close_evaluation_session(self, command: CloseEvaluationSessionCommand) -> None: ...