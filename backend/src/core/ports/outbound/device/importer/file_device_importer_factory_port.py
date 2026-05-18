from abc import ABC, abstractmethod

from core.services.device.allowed_device_extensions import AllowedDeviceFileExtension
from core.ports.outbound.device.importer.file_device_importer_port import (
    FileDeviceImporterPort,
)


class FileDeviceImporterFactoryPort(ABC):
    @abstractmethod
    def get_file_device_importer(
        self, extension: AllowedDeviceFileExtension
    ) -> FileDeviceImporterPort: ...
