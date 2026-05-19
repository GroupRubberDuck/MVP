from abc import ABC, abstractmethod
from pydantic import BaseModel


class OpenEvaluationSessionCommand(BaseModel):
    device_id: str


class OpenEvaluationSessionUseCase(ABC):
    @abstractmethod
    def open_evaluation_session(self, command: OpenEvaluationSessionCommand) -> str:
        """Apre una nuova sessione di valutazione e restituisce il suo ID.

        Raises:
            OpenEvaluationSessionFailure: se l'apertura di una sessione di valutazione fallisce per logica di business o problemi infrastrutturali (esiste già una sessione attiva, il dispositivo
                o lo standard non esistono, o la creazione della sessione fallisce).
        """
        ...
