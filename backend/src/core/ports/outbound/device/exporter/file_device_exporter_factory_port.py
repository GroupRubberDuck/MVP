from abc import ABC, abstractmethod
from core.domain.evaluation_object.allowed_device_file_extension import (
    AllowedDeviceFileExtension,
)
from core.ports.outbound.device.exporter.file_device_exporter_port import (
    FileDeviceExporterPort,
)


class FileDeviceExporterFactoryPort(ABC):
    @abstractmethod
    def get_file_device_exporter(
        self, extension: AllowedDeviceFileExtension
    ) -> FileDeviceExporterPort: ...
