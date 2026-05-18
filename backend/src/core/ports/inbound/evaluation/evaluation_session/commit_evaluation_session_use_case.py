from pydantic import BaseModel
from abc import ABC, abstractmethod


class CommitEvaluationSessionCommand(BaseModel):
    session_id: str


class CommitEvaluationSessionUseCase(ABC):
    @abstractmethod
    def commit(self, command: CommitEvaluationSessionCommand) -> None:
        pass
