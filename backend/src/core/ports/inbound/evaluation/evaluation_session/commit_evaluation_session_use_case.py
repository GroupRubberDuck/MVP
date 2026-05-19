from pydantic import BaseModel
from abc import ABC, abstractmethod


class CommitEvaluationSessionCommand(BaseModel):
    session_id: str


class CommitEvaluationSessionUseCase(ABC):
    @abstractmethod
    def commit(self, command: CommitEvaluationSessionCommand) -> None:
        """Persiste il dispositivo aggiornato al termine della sessione di valutazione.

        Raises:
            CommitSessionFailure: se il commit della sessione fallisce per logica di business o problemi infrastrutturali (la sessione non esiste o il salvataggio del dispositivo fallisce).
        """
        ...

