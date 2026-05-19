from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteDeviceCommand:
    device_id: str


class DeleteDeviceUseCase(ABC):
    @abstractmethod
    def delete_device(self, command: DeleteDeviceCommand) -> None: ...
        """Elimina il dispositivo specificato.

        Raises:
            DeleteDeviceFailure: se il dispositivo non può essere eliminato (non trovato o errore interno).
        """
        ...