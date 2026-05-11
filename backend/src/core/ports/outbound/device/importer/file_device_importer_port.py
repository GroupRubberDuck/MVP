from abc import ABC, abstractmethod
from typing import IO

from core.domain.evaluation_object.device import Device


class FileDeviceImporterPort(ABC):
    @abstractmethod
    def parse_device_file(self, device_file_content: IO[bytes]) -> Device: ...