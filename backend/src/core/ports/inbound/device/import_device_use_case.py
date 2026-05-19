from abc import ABC, abstractmethod
from dataclasses import dataclass
from core.services.device.allowed_device_extensions import AllowedDeviceFileExtension
from typing import IO


@dataclass(frozen=True)
class ImportDeviceCommand:
    device_file_content: IO[bytes]
    extension: AllowedDeviceFileExtension


class ImportDeviceUseCase(ABC):
    @abstractmethod
    def import_device(self, command: ImportDeviceCommand) -> None:
        """Importa un dispositivo da file.

        Raises:
            ImportDeviceFailure: se il file non può essere interpretato.
            DeviceRegistrationFailure: se si verifica un errore durante la registrazione di un device.
        """
        ...
