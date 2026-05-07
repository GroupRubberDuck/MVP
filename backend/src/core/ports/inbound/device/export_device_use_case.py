from abc import ABC, abstractmethod
from pydantic import BaseModel
from core.domain.evaluation_object.allowed_device_file_extension import AllowedDeviceFileExtension


class ExportDeviceCommand(BaseModel):
    device_id: str
    extension: AllowedDeviceFileExtension

class ExportDeviceUseCase(ABC):
    @abstractmethod
    def export_device(self, export_command: ExportDeviceCommand) -> bytes: ...