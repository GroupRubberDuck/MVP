from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class ActiveSessionInfo:
    session_id: str
    device_id: str


class GetActiveSessionUseCase(ABC):
    @abstractmethod
    def get_active_session(self) -> ActiveSessionInfo | None:
        """Restituisce i dati identificativi della sessione attiva, o None se assente."""
        ...
