from abc import ABC, abstractmethod
from core.domain.evaluation_object.device import Device
from typing import IO

class FileDeviceExporterPort(ABC):

    @abstractmethod
    def generate_device_file(self, device: Device) -> IO[bytes]: ...