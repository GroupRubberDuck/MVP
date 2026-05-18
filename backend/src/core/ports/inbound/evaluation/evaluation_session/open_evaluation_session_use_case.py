from abc import ABC, abstractmethod
from pydantic import BaseModel


class OpenEvaluationSessionCommand(BaseModel):
    device_id: str


class OpenEvaluationSessionUseCase(ABC):
    @abstractmethod
    def open_evaluation_session(self, command: OpenEvaluationSessionCommand) -> str:
        """
        Opens a new evaluation session and returns the session ID.

        Returns:
                str: The ID of the newly opened evaluation session.
        """
        pass
