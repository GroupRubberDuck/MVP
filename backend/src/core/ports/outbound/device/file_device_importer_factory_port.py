from abc import ABC, abstractmethod

from core.ports.inbound.device.import_device_use_case import AllowedDeviceFileExtension
from core.ports.outbound.device.file_device_importer_port import FileDeviceImporterPort


class FileDeviceImporterFactoryPort(ABC):
    @abstractmethod
    def get_file_device_importer(
        self, extension: AllowedDeviceFileExtension
    ) -> FileDeviceImporterPort: ...