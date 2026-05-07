from abc import ABC, abstractmethod
from ....domain.evaluation_object.device import Device


class FileDeviceExporterPort(ABC):

    @abstractmethod
    def generate_device_file(self, device_dto) -> bytes: ...