from abc import ABC, abstractmethod
from pydantic import BaseModel
from core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension
from typing import IO
from dataclasses import dataclass
class ExportDeviceCommand(BaseModel):
    device_id: str
    extension: AllowedDeviceFileExtension
@dataclass(frozen=True)
class ExportedFile:
    content: IO[bytes]
    filename: str
    media_type: str

class ExportDeviceUseCase(ABC):
    @abstractmethod
    def export_device(self, export_command: ExportDeviceCommand) -> ExportedFile: ...