from abc import ABC, abstractmethod
 
from core.services.evaluation.insert_justification_command import InsertJustificationCommand
 
 
class InsertJustificationUseCase(ABC):
 
    @abstractmethod
    def insert_justification(self, command: InsertJustificationCommand) -> None:
        raise NotImplementedError
 