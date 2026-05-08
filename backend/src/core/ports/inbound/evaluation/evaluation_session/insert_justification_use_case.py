from abc import ABC, abstractmethod

class InsertJustificationCommand:
    def __init__(self, 
                 session_id: str, 
                 asset_id: str, 
                 requirement_id: str, 
                 justification: str
                 ):
        self.session_id = session_id
        self.asset_id = asset_id
        self.requirement_id= requirement_id
        self.justification = justification


class InsertJustificationUseCase(ABC):
    @abstractmethod
    def insert_justification(self, command: InsertJustificationCommand) -> None:
        """Inserisce la giustificazione per un asset specifico e uno specifico requisito nella sessione di valutazione."""
        pass