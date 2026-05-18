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
    def import_device(self, command: ImportDeviceCommand) -> None: ...
