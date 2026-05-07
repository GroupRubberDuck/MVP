from abc import ABC, abstractmethod
from ....domain.evaluation_object.device import Device
from typing import IO

class FileDeviceExporterPort(ABC):

    @abstractmethod
    def generate_device_file(self, device_dto) -> IO[bytes]: ...