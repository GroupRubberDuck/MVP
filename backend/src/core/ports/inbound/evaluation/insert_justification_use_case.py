from abc import ABC, abstractmethod
from pydantic import BaseModel


class InsertJustificationCommand(BaseModel):
    session_id: str
    asset_id: str
    requirement_id: str
    justification: str


class InsertJustificationUseCase(ABC):
    @abstractmethod
    def insert_justification(self, command: InsertJustificationCommand) -> None:
        """Inserisce la giustificazione per un requisito di un asset nella sessione di valutazione.

        Raises:
            InsertJustificationFailure: se la giustificazione non può essere impostata (la sessione o l'asset non esistono, o il salvataggio fallisce).
        """
        ...
