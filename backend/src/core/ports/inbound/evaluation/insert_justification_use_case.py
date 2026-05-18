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
        """Inserisce la giustificazione per un asset specifico e uno specifico requisito nella sessione di valutazione."""
        ...
