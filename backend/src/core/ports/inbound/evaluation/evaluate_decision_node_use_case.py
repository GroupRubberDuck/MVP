from pydantic import BaseModel
from abc import ABC, abstractmethod


class EvaluateDecisionNodeCommand(BaseModel):
    session_id: str
    device_id: str
    asset_id: str
    requirement_id: str
    node_id: str
    answer: bool


class EvaluateDecisionNodeUseCase(ABC):
    @abstractmethod
    def evaluate_node(self, command: EvaluateDecisionNodeCommand) -> None:
        """Registra la risposta a un nodo decisionale e persiste la sessione aggiornata.

        Raises:
            EvaluateNodeFailure: se la valutazione di un nodo decisionale fallisce per regole di business (la sessione o l'asset non esistono,
                la risposta non è valida, o il salvataggio fallisce).
        """
